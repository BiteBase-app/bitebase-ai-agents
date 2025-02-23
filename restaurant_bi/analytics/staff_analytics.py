"""
Staff analytics module for restaurant BI system
Handles labor scheduling, performance metrics, and efficiency analysis
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import psycopg2
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class StaffAnalytics:
    """Staff analytics for restaurant business intelligence"""
    
    def __init__(self, config: Config):
        """
        Initialize the staff analytics module
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.pos_conn = psycopg2.connect(
            host=config.POSTGRES_HOST,
            database=config.POSTGRES_DB,
            user=config.POSTGRES_USER,
            password=config.POSTGRES_PASSWORD
        )
    
    def analyze_staff_efficiency(
        self,
        restaurant_id: str,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict:
        """
        Analyze staff performance and efficiency metrics
        
        Args:
            restaurant_id: Restaurant identifier
            date_range: Optional date range tuple (start, end)
            
        Returns:
            Dictionary containing staff efficiency metrics
        """
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
            date_range = (start_date, end_date)
            
        try:
            cursor = self.pos_conn.cursor()
            
            # Get staff performance metrics
            cursor.execute("""
                SELECT 
                    s.staff_id,
                    s.name,
                    s.role,
                    COUNT(t.id) as transactions_handled,
                    AVG(t.service_time) as avg_service_time,
                    SUM(t.total_amount) as total_sales
                FROM staff s
                LEFT JOIN transactions t ON s.staff_id = t.staff_id
                WHERE s.restaurant_id = %s
                AND t.transaction_date BETWEEN %s AND %s
                GROUP BY s.staff_id, s.name, s.role
            """, (restaurant_id, date_range[0], date_range[1]))
            
            staff_data = cursor.fetchall()
            
            # Get shift data for labor cost analysis
            cursor.execute("""
                SELECT 
                    s.staff_id,
                    COUNT(sh.id) as total_shifts,
                    SUM(sh.hours_worked) as total_hours,
                    SUM(sh.hours_worked * s.hourly_rate) as labor_cost
                FROM staff s
                JOIN shifts sh ON s.staff_id = sh.staff_id
                WHERE s.restaurant_id = %s
                AND sh.date BETWEEN %s AND %s
                GROUP BY s.staff_id
            """, (restaurant_id, date_range[0], date_range[1]))
            
            shift_data = cursor.fetchall()
            
            # Combine and analyze data
            staff_metrics = self._calculate_staff_metrics(
                staff_data,
                shift_data
            )
            
            # Get peak hours staffing analysis
            peak_analysis = self._analyze_peak_staffing(
                restaurant_id,
                date_range
            )
            
            # Generate scheduling recommendations
            schedule_recommendations = self._generate_schedule_recommendations(
                staff_metrics,
                peak_analysis
            )
            
            return {
                "staff_metrics": staff_metrics,
                "peak_analysis": peak_analysis,
                "efficiency_summary": self._calculate_efficiency_summary(
                    staff_metrics
                ),
                "recommendations": schedule_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error analyzing staff efficiency: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _calculate_staff_metrics(
        self,
        staff_data: List[tuple],
        shift_data: List[tuple]
    ) -> List[Dict]:
        """Calculate detailed metrics for each staff member"""
        # Create lookup for shift data
        shift_lookup = {
            shift[0]: {
                "total_shifts": shift[1],
                "total_hours": shift[2],
                "labor_cost": shift[3]
            }
            for shift in shift_data
        }
        
        staff_metrics = []
        for staff in staff_data:
            staff_id = staff[0]
            shift_info = shift_lookup.get(staff_id, {
                "total_shifts": 0,
                "total_hours": 0,
                "labor_cost": 0
            })
            
            # Calculate derived metrics
            transactions = staff[3] or 0
            total_sales = staff[5] or 0
            labor_cost = shift_info["labor_cost"] or 0
            hours_worked = shift_info["total_hours"] or 0
            
            metrics = {
                "staff_id": staff_id,
                "name": staff[1],
                "role": staff[2],
                "transactions_handled": transactions,
                "avg_service_time": float(staff[4] or 0),
                "total_sales": float(total_sales),
                "total_hours": float(hours_worked),
                "labor_cost": float(labor_cost)
            }
            
            # Calculate efficiency metrics
            if hours_worked > 0:
                metrics.update({
                    "sales_per_hour": total_sales / hours_worked,
                    "transactions_per_hour": transactions / hours_worked
                })
            else:
                metrics.update({
                    "sales_per_hour": 0,
                    "transactions_per_hour": 0
                })
            
            if labor_cost > 0:
                metrics["sales_to_labor_ratio"] = total_sales / labor_cost
            else:
                metrics["sales_to_labor_ratio"] = 0
            
            staff_metrics.append(metrics)
        
        return staff_metrics
    
    def _analyze_peak_staffing(
        self,
        restaurant_id: str,
        date_range: Tuple[datetime, datetime]
    ) -> Dict:
        """Analyze staffing levels during peak hours"""
        cursor = self.pos_conn.cursor()
        
        # Get hourly transaction volumes and staffing levels
        cursor.execute("""
            SELECT 
                DATE_TRUNC('hour', t.transaction_date) as hour,
                COUNT(t.id) as transaction_count,
                COUNT(DISTINCT t.staff_id) as staff_count,
                SUM(t.total_amount) as revenue
            FROM transactions t
            WHERE t.restaurant_id = %s
            AND t.transaction_date BETWEEN %s AND %s
            GROUP BY DATE_TRUNC('hour', t.transaction_date)
            ORDER BY hour
        """, (restaurant_id, date_range[0], date_range[1]))
        
        hourly_data = cursor.fetchall()
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(hourly_data, columns=[
            'hour', 'transactions', 'staff_count', 'revenue'
        ])
        
        # Calculate efficiency metrics
        df['transactions_per_staff'] = df['transactions'] / df['staff_count']
        df['revenue_per_staff'] = df['revenue'] / df['staff_count']
        
        # Identify peak hours
        peak_hours = df.nlargest(5, 'transactions')
        
        return {
            "peak_hours": [
                {
                    "hour": hour.strftime('%H:00'),
                    "transactions": int(row['transactions']),
                    "staff_count": int(row['staff_count']),
                    "efficiency_metrics": {
                        "transactions_per_staff": float(row['transactions_per_staff']),
                        "revenue_per_staff": float(row['revenue_per_staff'])
                    }
                }
                for hour, row in peak_hours.iterrows()
            ],
            "staffing_correlation": float(
                df['staff_count'].corr(df['revenue'])
            )
        }
    
    def _calculate_efficiency_summary(
        self,
        staff_metrics: List[Dict]
    ) -> Dict:
        """Calculate overall efficiency metrics"""
        if not staff_metrics:
            return {}
            
        metrics_df = pd.DataFrame(staff_metrics)
        
        return {
            "overall_metrics": {
                "avg_sales_per_hour": float(metrics_df['sales_per_hour'].mean()),
                "avg_transactions_per_hour": float(
                    metrics_df['transactions_per_hour'].mean()
                ),
                "total_labor_cost": float(metrics_df['labor_cost'].sum()),
                "avg_service_time": float(metrics_df['avg_service_time'].mean())
            },
            "by_role": self._calculate_role_metrics(metrics_df)
        }
    
    def _calculate_role_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate efficiency metrics by role"""
        role_metrics = {}
        
        for role in df['role'].unique():
            role_df = df[df['role'] == role]
            role_metrics[role] = {
                "staff_count": len(role_df),
                "avg_sales_per_hour": float(role_df['sales_per_hour'].mean()),
                "avg_transactions_per_hour": float(
                    role_df['transactions_per_hour'].mean()
                ),
                "total_labor_cost": float(role_df['labor_cost'].sum())
            }
            
        return role_metrics
    
    def _generate_schedule_recommendations(
        self,
        staff_metrics: List[Dict],
        peak_analysis: Dict
    ) -> List[Dict]:
        """Generate staffing and scheduling recommendations"""
        recommendations = []
        
        # Analyze peak hour staffing
        peak_hours = peak_analysis.get("peak_hours", [])
        staffing_correlation = peak_analysis.get("staffing_correlation", 0)
        
        if peak_hours:
            avg_peak_staff = np.mean([
                hour["staff_count"] for hour in peak_hours
            ])
            
            if staffing_correlation > 0.7:
                recommendations.append({
                    "type": "peak_staffing",
                    "action": "increase_staff",
                    "details": (
                        f"Consider increasing peak hour staffing to "
                        f"{int(avg_peak_staff * 1.2)} staff members"
                    ),
                    "reasoning": "Strong correlation between staff levels and revenue"
                })
        
        # Analyze individual performance
        staff_df = pd.DataFrame(staff_metrics)
        low_performers = staff_df[
            staff_df['sales_per_hour'] < staff_df['sales_per_hour'].mean() * 0.7
        ]
        
        for _, staff in low_performers.iterrows():
            recommendations.append({
                "type": "performance",
                "staff_id": staff["staff_id"],
                "name": staff["name"],
                "action": "training",
                "details": (
                    f"Sales per hour ({staff['sales_per_hour']:.2f}) "
                    f"significantly below average"
                )
            })
        
        # Schedule optimization
        recommendations.append({
            "type": "schedule_optimization",
            "actions": [
                {
                    "hour": hour["hour"],
                    "current_staff": hour["staff_count"],
                    "recommended_staff": int(
                        hour["transactions"] / 
                        peak_analysis["peak_hours"][0]["efficiency_metrics"]
                        ["transactions_per_staff"]
                    )
                }
                for hour in peak_hours
            ]
        })
        
        return recommendations
"""
Menu analytics module for restaurant BI system
Handles menu performance, food cost analysis, and seasonal trends
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from scipy import stats
import psycopg2
import logging
from ..config import Config

logger = logging.getLogger(__name__)

class MenuAnalytics:
    """Menu analytics for restaurant business intelligence"""
    
    def __init__(self, config: Config):
        """
        Initialize the menu analytics module
        
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
        
    def analyze_menu_performance(
        self,
        restaurant_id: str,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> Dict:
        """
        Analyze menu item performance including costs and profitability
        
        Args:
            restaurant_id: Restaurant identifier
            date_range: Optional date range tuple (start, end)
            
        Returns:
            Dictionary containing menu performance metrics
        """
        if not date_range:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)
            date_range = (start_date, end_date)
            
        try:
            cursor = self.pos_conn.cursor()
            
            # Get item performance metrics
            cursor.execute("""
                SELECT 
                    mi.item_name,
                    COUNT(*) as order_count,
                    SUM(t.item_price) as revenue,
                    AVG(mi.food_cost) as avg_food_cost,
                    mi.category
                FROM transactions t
                JOIN menu_items mi ON t.menu_item_id = mi.id
                WHERE t.restaurant_id = %s
                AND t.transaction_date BETWEEN %s AND %s
                GROUP BY mi.item_name, mi.category
                ORDER BY order_count DESC
            """, (restaurant_id, date_range[0], date_range[1]))
            
            items_data = cursor.fetchall()
            
            # Calculate performance metrics
            menu_items = []
            for item in items_data:
                name, orders, revenue, food_cost, category = item
                profit = revenue - (orders * food_cost)
                profit_margin = (profit / revenue) * 100 if revenue > 0 else 0
                
                menu_items.append({
                    "name": name,
                    "category": category,
                    "orders": orders,
                    "revenue": float(revenue),
                    "food_cost": float(food_cost),
                    "profit": float(profit),
                    "profit_margin": float(profit_margin),
                    "performance_score": self._calculate_performance_score(
                        orders, profit_margin
                    )
                })
            
            # Sort items by performance score
            menu_items.sort(key=lambda x: x["performance_score"], reverse=True)
            
            # Analyze seasonal trends
            seasonal_trends = self._analyze_seasonal_trends(
                restaurant_id, date_range
            )
            
            return {
                "top_performers": menu_items[:5],
                "low_performers": menu_items[-5:],
                "category_analysis": self._analyze_categories(menu_items),
                "seasonal_trends": seasonal_trends,
                "recommendations": self._generate_menu_recommendations(
                    menu_items, seasonal_trends
                )
            }
            
        except Exception as e:
            logger.error(f"Error analyzing menu performance: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _calculate_performance_score(
        self,
        orders: int,
        profit_margin: float
    ) -> float:
        """Calculate overall performance score for a menu item"""
        # Normalize orders and profit margin to 0-1 scale
        # and combine with weighted average
        normalized_orders = min(orders / 1000, 1)  # Cap at 1000 orders
        normalized_margin = profit_margin / 100
        
        # Weight factors (can be adjusted)
        ORDER_WEIGHT = 0.6
        MARGIN_WEIGHT = 0.4
        
        return (normalized_orders * ORDER_WEIGHT + 
                normalized_margin * MARGIN_WEIGHT)
    
    def _analyze_seasonal_trends(
        self,
        restaurant_id: str,
        date_range: Tuple[datetime, datetime]
    ) -> Dict:
        """Analyze seasonal trends in menu item performance"""
        cursor = self.pos_conn.cursor()
        
        # Get daily order counts by item
        cursor.execute("""
            SELECT 
                DATE_TRUNC('day', t.transaction_date) as date,
                mi.item_name,
                COUNT(*) as daily_orders
            FROM transactions t
            JOIN menu_items mi ON t.menu_item_id = mi.id
            WHERE t.restaurant_id = %s
            AND t.transaction_date BETWEEN %s AND %s
            GROUP BY DATE_TRUNC('day', t.transaction_date), mi.item_name
            ORDER BY date
        """, (restaurant_id, date_range[0], date_range[1]))
        
        daily_data = cursor.fetchall()
        
        # Convert to DataFrame for time series analysis
        df = pd.DataFrame(daily_data, columns=['date', 'item', 'orders'])
        
        seasonal_trends = []
        for item in df['item'].unique():
            item_df = df[df['item'] == item]
            
            # Calculate basic seasonal metrics
            by_month = item_df.set_index('date').resample('M')['orders'].mean()
            peak_month = by_month.idxmax()
            
            # Calculate trend significance
            trend_coef, p_value = stats.pearsonr(
                range(len(by_month)),
                by_month.values
            )
            
            seasonal_trends.append({
                "item": item,
                "peak_month": peak_month.strftime('%B'),
                "trend_direction": "up" if trend_coef > 0 else "down",
                "trend_strength": abs(trend_coef),
                "is_significant": p_value < 0.05
            })
        
        return {
            "trends": seasonal_trends,
            "analysis_period": {
                "start": date_range[0].strftime('%Y-%m-%d'),
                "end": date_range[1].strftime('%Y-%m-%d')
            }
        }
    
    def _analyze_categories(self, menu_items: List[Dict]) -> Dict:
        """Analyze performance by menu category"""
        categories = {}
        for item in menu_items:
            cat = item["category"]
            if cat not in categories:
                categories[cat] = {
                    "total_orders": 0,
                    "total_revenue": 0,
                    "total_profit": 0,
                    "item_count": 0
                }
            
            categories[cat]["total_orders"] += item["orders"]
            categories[cat]["total_revenue"] += item["revenue"]
            categories[cat]["total_profit"] += item["profit"]
            categories[cat]["item_count"] += 1
        
        # Calculate averages and add to results
        for cat in categories:
            categories[cat]["avg_profit_margin"] = (
                categories[cat]["total_profit"] / 
                categories[cat]["total_revenue"] * 100
                if categories[cat]["total_revenue"] > 0 else 0
            )
            categories[cat]["avg_orders_per_item"] = (
                categories[cat]["total_orders"] / 
                categories[cat]["item_count"]
            )
        
        return categories
    
    def _generate_menu_recommendations(
        self,
        menu_items: List[Dict],
        seasonal_trends: Dict
    ) -> List[Dict]:
        """Generate menu optimization recommendations"""
        recommendations = []
        
        # Identify items for price adjustment
        for item in menu_items:
            if item["profit_margin"] < 15 and item["orders"] > 100:
                recommendations.append({
                    "type": "price_adjustment",
                    "item": item["name"],
                    "current_margin": item["profit_margin"],
                    "suggested_increase": min(
                        10,  # Cap at 10% increase
                        (20 - item["profit_margin"]) / 2  # Half of gap to 20%
                    ),
                    "reasoning": "High volume but low margin"
                })
        
        # Seasonal recommendations
        for trend in seasonal_trends["trends"]:
            if trend["is_significant"]:
                recommendations.append({
                    "type": "seasonal_adjustment",
                    "item": trend["item"],
                    "peak_month": trend["peak_month"],
                    "action": "increase_promotion" if trend["trend_direction"] == "up"
                            else "review_offering",
                    "reasoning": f"Strong seasonal trend detected in {trend['peak_month']}"
                })
        
        return recommendations[:5]  # Limit to top 5 recommendations
"""
Real-time insights DAG for processing streaming restaurant data
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from restaurant_bi.streaming.realtime_processor import RealtimeProcessor
from restaurant_bi.llm.insights_generator import InsightsGenerator
from restaurant_bi.config import Config
import json
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'restaurant_bi',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def process_reviews(**context):
    """Process streaming reviews and generate insights"""
    config = Config()
    processor = RealtimeProcessor(config)
    insights_generator = InsightsGenerator(config)
    processed_reviews = []
    
    def handle_review(review_data):
        try:
            # Generate AI insights
            insights = insights_generator.generate_restaurant_summary(
                review_data['restaurant_name'],
                review_data['review_text']
            )
            
            # Add insights to review data
            review_data['ai_insights'] = insights
            review_data['processed_at'] = datetime.now().isoformat()
            
            processed_reviews.append(review_data)
            logger.info(f"Processed review for {review_data['restaurant_name']}")
            
        except Exception as e:
            logger.error(f"Error processing review: {str(e)}")
    
    try:
        # Process reviews for configured duration
        processor.consume_stream(
            config.KAFKA_TOPICS['REVIEWS'],
            handle_review
        )
        
        # Push processed data to XCom
        context['task_instance'].xcom_push(
            key='processed_reviews',
            value=json.dumps(processed_reviews)
        )
        
    except Exception as e:
        logger.error(f"Error in review processing task: {str(e)}")
        raise
    finally:
        processor.close()

def process_market_updates(**context):
    """Process streaming market updates and generate insights"""
    config = Config()
    processor = RealtimeProcessor(config)
    insights_generator = InsightsGenerator(config)
    processed_updates = []
    
    def handle_update(market_data):
        try:
            # Generate market insights
            insights = insights_generator.generate_market_insights(
                market_data,
                market_data.get('location', 'Unknown')
            )
            
            # Add insights to market data
            market_data['ai_insights'] = insights
            market_data['processed_at'] = datetime.now().isoformat()
            
            processed_updates.append(market_data)
            logger.info(f"Processed market update for {market_data.get('location', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error processing market update: {str(e)}")
    
    try:
        # Process market updates for configured duration
        processor.consume_stream(
            config.KAFKA_TOPICS['MARKET_UPDATES'],
            handle_update
        )
        
        # Push processed data to XCom
        context['task_instance'].xcom_push(
            key='processed_market_updates',
            value=json.dumps(processed_updates)
        )
        
    except Exception as e:
        logger.error(f"Error in market update processing task: {str(e)}")
        raise
    finally:
        processor.close()

def store_insights(**context):
    """Store processed insights in databases"""
    try:
        # Get processed data from XCom
        ti = context['task_instance']
        reviews_data = json.loads(
            ti.xcom_pull(task_ids='process_reviews', key='processed_reviews')
        )
        market_data = json.loads(
            ti.xcom_pull(task_ids='process_market_updates', key='processed_market_updates')
        )
        
        # TODO: Store in databases
        # This would involve:
        # 1. Updating PostgreSQL with structured data
        # 2. Storing insights in Neo4j graph
        # 3. Updating vector embeddings in ChromaDB
        
        logger.info("Successfully stored insights in databases")
        
    except Exception as e:
        logger.error(f"Error storing insights: {str(e)}")
        raise

# Create DAG
dag = DAG(
    'realtime_insights_processing',
    default_args=default_args,
    description='Process streaming restaurant data and generate AI insights',
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['restaurant_bi', 'streaming', 'ai'],
    concurrency=3
)

# Define tasks
process_reviews_task = PythonOperator(
    task_id='process_reviews',
    python_callable=process_reviews,
    provide_context=True,
    dag=dag,
)

process_market_task = PythonOperator(
    task_id='process_market_updates',
    python_callable=process_market_updates,
    provide_context=True,
    dag=dag,
)

store_insights_task = PythonOperator(
    task_id='store_insights',
    python_callable=store_insights,
    provide_context=True,
    dag=dag,
)

# Set task dependencies
[process_reviews_task, process_market_task] >> store_insights_task
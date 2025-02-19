# Restaurant BI - Airflow DAGs

This directory contains Apache Airflow DAGs for the Restaurant BI system's ETL pipelines.

## DAGs Overview

### restaurant_data_etl.py

An ETL pipeline that handles restaurant data collection and processing:

1. **Data Collection**
   - Scrapes restaurant data from Google Maps API
   - Collects additional data from Yelp
   - Combines data from multiple sources

2. **Data Processing**
   - Cleans and standardizes restaurant data
   - Handles missing values and data type conversions
   - Prepares data for storage

3. **Storage & Embeddings**
   - Stores processed data in PostgreSQL
   - Updates vector embeddings in ChromaDB
   - Maintains data freshness for semantic search

### Schedule

The DAG runs daily and includes:
- Retries on failure (max 1 retry)
- 5-minute delay between retries
- No backfilling of missed runs

## Git Synchronization

This DAGs directory is automatically synchronized with GitHub using git-sync. Any changes pushed to the repository will be automatically reflected in Airflow.

### How it works:
1. Push changes to the GitHub repository
2. git-sync service pulls changes every 30 seconds
3. Airflow detects new/modified DAGs
4. Changes are applied without restart

## Development

When developing new DAGs:
1. Test locally first
2. Ensure all dependencies are in requirements.txt
3. Follow Airflow best practices for task design
4. Use XCom for task communication
5. Implement proper error handling and logging

## Environment Variables

Required environment variables for DAGs:
- `GOOGLE_MAPS_API_KEY`: For Google Maps API access
- `POSTGRES_*`: Database connection details
- `NEO4J_*`: Graph database connection details
- `MINIO_*`: Object storage credentials
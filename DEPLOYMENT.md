# Manual AWS Deployment Guide for Restaurant BI System

This guide covers the manual deployment of the Restaurant BI system on AWS, including all components for geospatial analysis, real-time chatbot integration, and dynamic pricing.

## Infrastructure Overview

The system requires the following AWS services:
- EC2 instances for API and services
- RDS (PostgreSQL) for structured data
- Neo4j for graph relationships
- S3 for data storage
- Application Load Balancer (ALB)
- ElastiCache Redis for real-time features
- Amazon MSK (Kafka) for streaming

## Step-by-Step Deployment

### 1. Initial AWS Setup

```bash
# Configure AWS CLI
aws configure
# Enter your AWS credentials and region
```

### 2. Create Security Groups

```bash
# Create main security group
aws ec2 create-security-group \
    --group-name restaurant-bi-sg \
    --description "Security group for Restaurant BI"

# Allow required ports
aws ec2 authorize-security-group-ingress \
    --group-name restaurant-bi-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

# Add additional ports for services
aws ec2 authorize-security-group-ingress \
    --group-name restaurant-bi-sg \
    --protocol tcp \
    --port 8080 \
    --cidr 0.0.0.0/0
```

### 3. Launch EC2 Instance

```bash
# Create key pair
aws ec2 create-key-pair \
    --key-name restaurant-bi-key \
    --query 'KeyMaterial' \
    --output text > restaurant-bi-key.pem

chmod 400 restaurant-bi-key.pem

# Launch EC2 instance
aws ec2 run-instances \
    --image-id ami-0f9575d3d509bae0c \
    --count 1 \
    --instance-type t3.xlarge \
    --key-name restaurant-bi-key \
    --security-groups restaurant-bi-sg
```

### 4. Set Up RDS Database

```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier restaurant-bi-db \
    --db-instance-class db.t3.medium \
    --engine postgres \
    --master-username database_admin \
    --master-user-password Data1234!* \
    --allocated-storage 100
```

### 5. Create S3 Bucket

```bash
# Create bucket for data storage
aws s3 mb s3://restaurant-bi-data

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket restaurant-bi-data \
    --versioning-configuration Status=Enabled
```

### 6. Configure EC2 Instance

SSH into your EC2 instance:
```bash
ssh -i restaurant-bi-key.pem ubuntu@your-ec2-ip
```

Install system dependencies:
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Docker and Docker Compose
sudo apt-get install -y docker.io docker-compose

# Install Python requirements
sudo apt-get install -y python3-pip python3-dev build-essential
```

### 7. Deploy Services Using Docker Compose

Create docker-compose.yml:
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - POSTGRES_HOST=restaurant-bi-db.xxxxx.region.rds.amazonaws.com
      - POSTGRES_DB=restaurant_bi
      - POSTGRES_USER=admin
      - POSTGRES_PASSWORD=your_secure_password
      - NEO4J_URI=bolt://neo4j:7687
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - OPENAI_API_KEY=your_openai_key
      - TWILIO_ACCOUNT_SID=your_twilio_sid
      - TWILIO_AUTH_TOKEN=your_twilio_token
      - AWS_ACCESS_KEY_ID=your_aws_key
      - AWS_SECRET_ACCESS_KEY=your_aws_secret

  neo4j:
    image: neo4j:latest
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=neo4j/password

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    ports:
      - "2181:2181"

  chromadb:
    image: chromadb/chroma:latest
    ports:
      - "8000:8000"

  airflow:
    image: apache/airflow:latest
    ports:
      - "8081:8080"
    environment:
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://admin:password@restaurant-bi-db/airflow
```

### 8. Deploy Application

```bash
# Clone repository
git clone <repository-url>
cd restaurant-bi

# Build and start services
docker-compose up -d
```

### 9. Set Up Application Load Balancer

```bash
# Create target group
aws elbv2 create-target-group \
    --name restaurant-bi-tg \
    --protocol HTTP \
    --port 8080 \
    --vpc-id your_vpc_id

# Create load balancer
aws elbv2 create-load-balancer \
    --name restaurant-bi-alb \
    --subnets subnet-xxxx subnet-yyyy \
    --security-groups sg-zzzz

# Create listener
aws elbv2 create-listener \
    --load-balancer-arn $ALB_ARN \
    --protocol HTTP \
    --port 80 \
    --default-actions Type=forward,TargetGroupArn=$TG_ARN
```

## Configuration

### Environment Variables

Create a `.env` file with the following configurations:
```env
# AWS Configuration
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=your_region

# Database Configuration
POSTGRES_HOST=your_rds_endpoint
POSTGRES_DB=restaurant_bi
POSTGRES_USER=admin
POSTGRES_PASSWORD=your_secure_password

# API Keys
GOOGLE_MAPS_API_KEY=your_google_maps_key
OPENAI_API_KEY=your_openai_key

# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_WHATSAPP_NUMBER=your_whatsapp_number

# Service Endpoints
NEO4J_URI=bolt://your_neo4j_endpoint:7687
KAFKA_BOOTSTRAP_SERVERS=your_kafka_endpoint:9092
CHROMADB_HOST=your_chromadb_endpoint
```

## Verification

### Test API Endpoints

1. Test health check:
```bash
curl http://your-alb-dns/
```

2. Test geospatial analysis:
```bash
curl -X POST http://your-alb-dns/geospatial/clusters/analyze \
    -H "Content-Type: application/json" \
    -d '{"locations": [{"lat": 40.7128, "lng": -74.0060}]}'
```

3. Test real-time chatbot:
```bash
curl -X POST http://your-alb-dns/bot/message \
    -H "Content-Type: application/json" \
    -d '{"customer_id": "123", "message": "Find restaurants near me"}'
```

## Monitoring

1. Set up CloudWatch logs:
```bash
# Install CloudWatch agent
sudo apt-get install -y amazon-cloudwatch-agent

# Configure CloudWatch
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

2. Monitor logs:
```bash
# View API logs
aws logs get-log-events \
    --log-group-name /restaurant-bi/api \
    --log-stream-name main
```

## Backup and Maintenance

1. Database backup:
```bash
# Create RDS snapshot
aws rds create-db-snapshot \
    --db-instance-identifier restaurant-bi-db \
    --db-snapshot-identifier manual-backup-1
```

2. S3 data backup:
```bash
# Sync data to backup bucket
aws s3 sync s3://restaurant-bi-data s3://restaurant-bi-backup
```

## Troubleshooting

Common issues and solutions:

1. Database Connection Issues:
```bash
# Test database connection
psql -h your-rds-endpoint -U admin -d restaurant_bi
```

2. Service Health Check:
```bash
# Check running containers
docker ps
docker logs [container_id]
```

3. Load Balancer Issues:
```bash
# Check target health
aws elbv2 describe-target-health \
    --target-group-arn your_target_group_arn
```

## Security Considerations

1. Rotate credentials regularly:
- Database passwords
- API keys
- AWS access keys

2. Update security group rules to limit access:
```bash
# Update security group
aws ec2 update-security-group-rule-descriptions-ingress \
    --group-id your_security_group_id \
    --ip-permissions "..."
```

## Performance Optimization

1. Configure instance auto-scaling:
```bash
# Create auto-scaling group
aws autoscaling create-auto-scaling-group \
    --auto-scaling-group-name restaurant-bi-asg \
    --launch-template LaunchTemplateName=restaurant-bi-template \
    --min-size 2 \
    --max-size 5
```

2. Set up ElastiCache for caching:
```bash
# Create cache cluster
aws elasticache create-cache-cluster \
    --cache-cluster-id restaurant-bi-cache \
    --engine redis \
    --cache-node-type cache.t3.micro \
    --num-cache-nodes 1
# 🚀 Uptime Monitor — DevOps Hands-On Project

A **FastAPI Python application** that monitors URLs, stores results in SQLite, and exposes:
- `/` — HTML status page
- `/targets` — REST API for managing monitored URLs
- `/metrics` — Prometheus metrics
- `/healthz` — Health check

Built as a **full DevOps project**:
- Multi-stage Dockerfile
- docker-compose for local development
- Terraform for AWS (ECR + EC2 + IAM + Security Group)
- GitHub Actions CI/CD for building & pushing to ECR

---

## 📂 Project Structure

uptime-monitor/

├── app/

│ ├── init.py

│ ├── main.py

│ ├── db.py

│ ├── monitor.py

│ ├── models.py

│ └── templates/

│   ├── status.html    

├── requirements.txt

├── Dockerfile

├── docker-compose.yml

├── Makefile

├── terraform/

│ ├── provider.tf

│ ├── variables.tf

│ ├── outputs.tf

│ ├── main.tf

│ └── user_data.sh

└── .github/

│ └── workflows/

│ ├── ci-cd.yml


---

## 🖥 1. Local Development

### 1.1. Clone the repository
# Uptime Monitor

Uptime Monitor is a lightweight service for monitoring website availability and performance. It records uptime metrics, exposes health checks, and provides Prometheus-compatible metrics for monitoring dashboards.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
  - [Without Docker](#without-docker)
  - [With Docker Compose](#with-docker-compose)
- [AWS Deployment with Terraform](#aws-deployment-with-terraform)
  - [Initialize Terraform](#initialize-terraform)
  - [Create Infrastructure](#create-infrastructure)
- [Build and Push Docker Image to ECR](#build-and-push-docker-image-to-ecr)
  - [Authenticate to ECR](#authenticate-to-ecr)
  - [Build and Push](#build-and-push)
- [CI/CD with GitHub Actions](#cicd-with-github-actions)
- [Updating the Application](#updating-the-application)
- [Destroying Infrastructure](#destroying-infrastructure)
- [Recommended Extensions](#recommended-extensions)

---

## Features

- Monitor multiple URLs with configurable intervals  
- Store check results in SQLite (or replace with RDS)  
- Expose metrics for Prometheus  
- Health check endpoint (`/healthz`)  
- Simple web-based status page  

---

## Prerequisites

- Python 3.11+  
- Docker & Docker Compose  
- AWS CLI configured with access to ECR and EC2  
- Terraform 1.5+  

---

## Local Setup

### Without Docker

git clone https://github.com/yourname/uptime-monitor.git
cd uptime-monitor

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Access the application at:

http://localhost:8000

With Docker Compose

make up

Access the services:

    Status page: http://localhost:8000

    Health check: http://localhost:8000/healthz

    Metrics: http://localhost:8000/metrics

Add a monitored URL:

curl -X POST http://localhost:8000/targets \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","interval_seconds":15,"enabled":true}'

AWS Deployment with Terraform
Initialize Terraform

cd terraform
terraform init

Create Infrastructure

terraform apply -var "key_name=YOUR_EC2_KEYPAIR_NAME"

Terraform outputs:

    ecr_repository_url

    app_url (EC2 public URL)

    ec2_public_ip

Build and Push Docker Image to ECR
Authenticate to ECR

aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr_repository_url>

Build and Push

docker build -t <ecr_repository_url>:latest .
docker push <ecr_repository_url>:latest

The EC2 instance automatically pulls the latest image and runs the application on port 80.
CI/CD with GitHub Actions

    Push the project to GitHub.

    Add repository secrets:

    AWS_REGION

    AWS_ROLE_TO_ASSUME (or AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY)

    ECR_REPOSITORY (e.g., 123456789012.dkr.ecr.eu-central-1.amazonaws.com/uptime-monitor)

Every push to the main branch will:

    Build the Docker image

    Push the image to ECR

Updating the Application

Push the new Docker image and restart the service on the EC2 instance:

sudo systemctl restart uptime-monitor.service

Destroying Infrastructure

cd terraform
terraform destroy

Recommended Extensions

    Deploy with ECS/Fargate using ALB and Route53

    Integrate Grafana + Prometheus via Docker Compose

    Enable Slack/Webhook notifications for downtime alerts

    Use RDS (PostgreSQL/MySQL) instead of SQLite for production persistence

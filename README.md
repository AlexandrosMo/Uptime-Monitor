# Uptime Monitor — Technical Documentation

## Overview

Uptime Monitor is a Python-based application built with FastAPI for monitoring the availability and response times of specified URLs. The application stores monitoring results in an SQLite database and exposes key functionalities through a REST API, Prometheus-compatible metrics, and a web-based status page.

## Features

* Monitor multiple URLs at configurable intervals.
* Store monitoring results in SQLite (can be adapted to RDS for production).
* Serve Prometheus metrics via `/metrics` endpoint.
* Provide a health check endpoint at `/healthz`.
* Display results through an HTML status page.

## Endpoints

* `/` — HTML status page.
* `/targets` — Manage monitored URLs (CRUD operations).
* `/metrics` — Prometheus metrics.
* `/healthz` — Health check endpoint.

## Prerequisites

* Python 3.11 or higher.
* Docker and Docker Compose.
* AWS CLI configured for ECR and EC2.
* Terraform version 1.5 or higher.

## Installation and Usage

### Local Installation (without Docker)

1. Clone the repository:

```bash
git clone https://github.com/yourname/uptime-monitor.git
cd uptime-monitor
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # For Linux/Mac
.venv\Scripts\activate     # For Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Start the application:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

5. Access the application at [http://localhost:8000](http://localhost:8000).

### Using Docker Compose

1. Build and run containers:

```bash
docker compose up -d --build
```

2. Access services:

   * Status page: [http://localhost:8000](http://localhost:8000)
   * Health check: [http://localhost:8000/healthz](http://localhost:8000/healthz)
   * Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

## AWS Deployment (with Terraform)

1. Initialize Terraform:

```bash
cd terraform
terraform init
```

2. Apply configuration:

```bash
terraform apply -var "key_name=YOUR_EC2_KEYPAIR_NAME"
```

3. Terraform will output:

   * ECR repository URL
   * Application public URL
   * EC2 public IP

## Docker Image Management

Authenticate with ECR:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr_repository_url>
```

Build and push image:

```bash
docker build -t <ecr_repository_url>:latest .
docker push <ecr_repository_url>:latest
```

## CI/CD

A GitHub Actions workflow (`.github/workflows/ci-cd.yml`) builds and pushes the Docker image to ECR on each push to the `main` branch.

## Infrastructure Teardown

To remove all AWS resources:

```bash
cd terraform
terraform destroy
```

## Potential Enhancements

* ECS/Fargate deployment with load balancing.
* Grafana and Prometheus integration.
* Slack or webhook notifications for downtime.
* Migration from SQLite to RDS for production use.

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
└── .github/workflows/ci-cd.yml


---

## 🖥 1. Local Development

### 1.1. Clone the repository
```bash
git clone https://github.com/yourname/uptime-monitor.git
cd uptime-monitor

1.2. Run without Docker

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Open http://localhost:8000
🐳 2. Local with Docker Compose

make up

Then:

    Status page: http://localhost:8000

    Health check: http://localhost:8000/healthz

    Metrics: http://localhost:8000/metrics

Add a monitored URL:

curl -X POST http://localhost:8000/targets \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","interval_seconds":15,"enabled":true}'

☁️ 3. AWS Deployment with Terraform
3.1. Initialize Terraform

cd terraform
terraform init

3.2. Create infrastructure

terraform apply -var "key_name=YOUR_EC2_KEYPAIR_NAME"

Terraform outputs will provide:

    ecr_repository_url

    app_url (EC2 public URL)

    ec2_public_ip

📦 4. Build & Push Docker Image to ECR
4.1. Authenticate to ECR

aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <ecr_repository_url>

4.2. Build & push

docker build -t <ecr_repository_url>:latest .
docker push <ecr_repository_url>:latest

The EC2 instance will automatically pull the latest image and run it on port 80.
🔄 5. CI/CD with GitHub Actions

    Push the project to GitHub.

    In Settings → Secrets, add:

        AWS_REGION

        AWS_ROLE_TO_ASSUME (or AWS_ACCESS_KEY_ID + AWS_SECRET_ACCESS_KEY)

        ECR_REPOSITORY (e.g., 123456789012.dkr.ecr.eu-central-1.amazonaws.com/uptime-monitor)

    Every push to main will:

        Build the Docker image

        Push it to ECR

🛠 6. Updating the Application

Push a new latest image and on the EC2 instance run:

sudo systemctl restart uptime-monitor.service

🗑 7. Destroy Infrastructure

cd terraform
terraform destroy

🔮 Possible Extensions

    ECS/Fargate + ALB + Route53

    Grafana + Prometheus stack in docker-compose

    Slack/Webhook alerts

    RDS (PostgreSQL/MySQL) instead of SQLite
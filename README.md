# 🚀 Uptime Monitor — DevOps Hands‑On Project

A **FastAPI** application that monitors URLs, stores results in **SQLite**, and exposes:

* `/` — HTML status page
* `/targets` — REST API for managing monitored URLs
* `/metrics` — Prometheus metrics
* `/healthz` — Health check

Built as a **full DevOps project**:

* Multi‑stage Dockerfile
* `docker-compose` for local development
* Terraform for AWS (ECR + EC2 + IAM + Security Group)
* GitHub Actions CI/CD for building & pushing to ECR

---

## 📦 Features

* Monitor multiple URLs with configurable intervals
* Store check results in SQLite (swap to RDS for production if you prefer)
* Prometheus‑compatible metrics (`/metrics`)
* Health check endpoint (`/healthz`)
* Simple web‑based status page (`/`)

---

## 🧭 Endpoints

| Method | Path            | Description             |
| -----: | --------------- | ----------------------- |
|    GET | `/`             | HTML status page        |
|    GET | `/healthz`      | Health check            |
|    GET | `/metrics`      | Prometheus metrics      |
|    GET | `/targets`      | List monitored targets  |
|   POST | `/targets`      | Add/enable a target     |
|    PUT | `/targets/{id}` | Update a target         |
| DELETE | `/targets/{id}` | Disable/remove a target |

> Exact request/response shapes live in the FastAPI docs at `/docs` when the app is running.

---

## 📂 Project Structure

```text
uptime-monitor/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── db.py
│   ├── monitor.py
│   ├── models.py
│   └── templates/
│       └── status.html
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── terraform/
│   ├── provider.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── main.tf
│   └── user_data.sh
└── .github/
    └── workflows/
        └── ci-cd.yml
```

---

## ✅ Prerequisites

* Python **3.11+**
* Docker & Docker Compose
* AWS CLI configured with permissions for ECR and EC2
* Terraform **1.5+**

---

## 🖥 Local Development

### 1) Without Docker

```bash
# Clone
git clone https://github.com/AlexandrosMo/uptime-monitor.git
cd uptime-monitor

# Create and activate venv (Linux/Mac)
python -m venv .venv
source .venv/bin/activate

# Install deps
pip install -r requirements.txt

# Run dev server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Windows (Git Bash one‑liner):**

```bash
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Access the app: [http://localhost:8000](http://localhost:8000)

### 2) With Docker Compose

Using `make` (recommended):

```bash
make up      # build & start in background
make logs    # tail logs
make down    # stop
```

Or directly with Docker Compose:

```bash
docker compose up -d --build
```

Access the services:

* Status page: [http://localhost:8000](http://localhost:8000)
* Health check: [http://localhost:8000/healthz](http://localhost:8000/healthz)
* Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

Add a monitored URL:

```bash
curl -X POST http://localhost:8000/targets \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com","interval_seconds":15,"enabled":true}'
```

---

## ☁️ AWS Deployment with Terraform

### Initialize Terraform

```bash
cd terraform
terraform init
```

### Create Infrastructure

```bash
terraform apply -var "key_name=YOUR_EC2_KEYPAIR_NAME" -auto-approve
```

**Terraform outputs** (examples):

* `ecr_repository_url`
* `app_url` (EC2 public URL)
* `ec2_public_ip`

> `user_data.sh` installs Docker on EC2, logs in to ECR, pulls the image, and starts the app via systemd service `uptime-monitor.service` listening on port **80**.

---

## 📦 Build & Push Docker Image to ECR

Authenticate to ECR:

```bash
aws ecr get-login-password --region <region> | \
  docker login --username AWS --password-stdin <ecr_repository_url>
```

Build & push:

```bash
docker build -t <ecr_repository_url>:latest .
docker push <ecr_repository_url>:latest
```

The EC2 instance started by Terraform will pull the latest `:latest` image and run the application on port **80**.

> Tip: also tag with a git SHA for traceability, e.g. `:abc123`.

---

## 🤖 CI/CD with GitHub Actions

1. Push this project to GitHub.
2. Add repository **secrets** (Settings → Secrets and variables → Actions):

   * `AWS_REGION`
   * `AWS_ROLE_TO_ASSUME` *(preferred, via OIDC)* **or** `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`
   * `ECR_REPOSITORY` (e.g., `123456789012.dkr.ecr.eu-central-1.amazonaws.com/uptime-monitor`)
3. The workflow `.github/workflows/ci-cd.yml` builds the image and pushes to ECR on every push to `main`.

---

## 🔄 Updating the Application

Push a new Docker image to ECR. The EC2 instance can be restarted to pull latest:

```bash
ssh ec2-user@<ec2_public_ip>
sudo systemctl restart uptime-monitor.service
```

> Alternatively, use an Instance Profile + EventBridge or a simple pull‑on‑schedule if you prefer hands‑off.

---

## 🧹 Destroying Infrastructure

```bash
cd terraform
terraform destroy -auto-approve
```

---

## 🧪 Makefile Targets (optional)

Common targets used by this repo:

```Makefile
up:           ## build & start docker compose
	docker compose up -d --build

down:         ## stop containers
	docker compose down

logs:         ## tail app logs
	docker compose logs -f --tail=100

fmt:          ## format Python code (if black is in requirements)
	black app

lint:         ## lint (if ruff/flake8 in requirements)
	ruff check app || true
```



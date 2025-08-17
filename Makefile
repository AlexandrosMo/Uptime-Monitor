.PHONY: run build up down logs tf-init tf-apply tf-destroy

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

build:
	docker build -t uptime-monitor:local .

up:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

tf-init:
	cd terraform && terraform init

tf-apply:
	cd terraform && terraform apply -auto-approve

tf-destroy:
	cd terraform && terraform destroy -auto-approve

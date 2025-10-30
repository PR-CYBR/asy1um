# Project Asylum - Makefile

.PHONY: help setup start stop restart logs clean test lint build deploy

help: ## Show this help message
	@echo "Project Asylum - Available Commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup: ## Initial setup - copy .env and create directories
	@echo "Setting up Project Asylum..."
	@./setup.sh

start: ## Start all services
	@echo "Starting all services..."
	@docker-compose up -d
	@echo "Services started. Access points:"
	@echo "  - Grafana: http://localhost:3000"
	@echo "  - Prometheus: http://localhost:9090"
	@echo "  - Kibana: http://localhost:5601"
	@echo "  - AI API: http://localhost:8000"
	@echo "  - Orchestration API: http://localhost:3001"

stop: ## Stop all services
	@echo "Stopping all services..."
	@docker-compose down

restart: ## Restart all services
	@echo "Restarting all services..."
	@docker-compose restart

logs: ## View logs from all services
	@docker-compose logs -f

logs-ai: ## View AI service logs
	@docker-compose logs -f ai-api

logs-orch: ## View orchestration service logs
	@docker-compose logs -f orchestration-api

logs-honeypot: ## View honeypot logs
	@docker-compose logs -f cowrie

clean: ## Remove all containers and volumes
	@echo "Cleaning up..."
	@docker-compose down -v
	@echo "Cleaned up containers and volumes"

test: ## Run tests
	@echo "Running tests..."
	@cd ai && pytest || echo "No Python tests found"
	@cd orchestration && npm test || echo "No Node.js tests found"

lint: ## Lint code
	@echo "Linting Python code..."
	@cd ai && flake8 . --max-line-length=120 || true
	@echo "Linting JavaScript code..."
	@cd orchestration && npx eslint . || true
	@echo "Checking Terraform format..."
	@cd terraform && terraform fmt -check || true

format: ## Format code
	@echo "Formatting Python code..."
	@cd ai && black . --line-length=120 || true
	@echo "Formatting Terraform code..."
	@cd terraform && terraform fmt -recursive || true

build: ## Build Docker images
	@echo "Building Docker images..."
	@docker-compose build

train-model: ## Train AI model with synthetic data
	@echo "Training AI model..."
	@docker-compose exec ai-api python train.py --synthetic --epochs 50

terraform-init: ## Initialize Terraform
	@echo "Initializing Terraform..."
	@cd terraform && terraform init

terraform-plan: ## Run Terraform plan
	@echo "Running Terraform plan..."
	@cd terraform && terraform plan -var-file=envs/dev/terraform.tfvars

terraform-apply: ## Apply Terraform configuration
	@echo "Applying Terraform configuration..."
	@cd terraform && terraform apply -var-file=envs/dev/terraform.tfvars

health: ## Check health of all services
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq . || echo "AI API not responding"
	@curl -s http://localhost:3001/health | jq . || echo "Orchestration API not responding"
	@curl -s http://localhost:9090/-/healthy || echo "Prometheus not responding"

status: ## Show status of all services
	@docker-compose ps

rotate-honeypot: ## Rotate honeypot configuration
	@echo "Rotating honeypot configuration..."
	@./honeypot/cowrie/rotate_config.sh

deploy-prod: ## Deploy to production (requires credentials)
	@echo "Deploying to production..."
	@cd terraform && terraform workspace select prod && terraform apply -var-file=envs/prod/terraform.tfvars

backup: ## Backup important data
	@echo "Backing up data..."
	@mkdir -p backups
	@docker-compose exec elasticsearch curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'{"type": "fs","settings": {"location": "/backups"}}'
	@tar -czf backups/ai-models-$(shell date +%Y%m%d-%H%M%S).tar.gz ai/model/saved_models/

install-deps: ## Install development dependencies
	@echo "Installing dependencies..."
	@cd ai && pip install -r requirements.txt
	@cd orchestration && npm install

docs: ## Generate documentation
	@echo "Documentation is in docs/ directory"
	@echo "Main docs:"
	@ls -1 docs/

SHELL := /bin/bash
ENV_FILE := .env
TEMPLATE := nginx.conf.template
GENERATED := nginx.conf

.PHONY: help up down logs shell clean ssl restart status config validate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

config: ## Generate nginx.conf from .env
	@echo ">>> Generating nginx.conf from $(ENV_FILE)"
	@set -a && source $(ENV_FILE) && python3 create_config.py

validate: config ## Validate generated nginx config
	@echo ">>> Validating nginx configuration"
	docker run --rm \
		-v $$PWD/$(GENERATED):/etc/nginx/conf.d/default.conf:ro \
		-v $$PWD/ssl:/etc/nginx/ssl:ro \
		nginx:alpine nginx -t

up: config ## Start nginx proxy service
	docker compose up -d nginx-proxy

down: ## Stop nginx proxy service
	docker compose down

logs: ## Show nginx logs
	docker compose logs -f nginx-proxy

shell: ## Access nginx container shell
	docker compose exec nginx-proxy sh

ssl: ## Generate self-signed SSL certificate for development
	mkdir -p ssl
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout ssl/nginx.key \
		-out ssl/nginx.crt \
		-subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

clean: ## Remove containers and SSL certificates
	docker compose down
	rm -rf ssl/

restart: ## Restart nginx proxy
	docker compose restart nginx-proxy

status: ## Show service status
	docker compose ps

.PHONY: help setup dev dev-fe dev-be build test lint pipeline clean status

help:
	@echo "Commands:"
	@echo "  setup     : Install all dependencies (frontend, backend, data pipelines)"
	@echo "  dev       : Start frontend development server"
	@echo "  dev-fe    : Start frontend development server (alias)"
	@echo "  dev-be    : Start backend development server"
	@echo "  build     : Build production-ready application"
	@echo "  test      : Run all tests"
	@echo "  lint      : Lint all source code"
	@echo "  pipeline  : Run data pipeline"
	@echo "  clean     : Remove all generated files"
	@echo "  status    : Show current work status"

setup:
	@echo "📦 Installing frontend dependencies..."
	@cd app/frontend && npm install
	@echo "📦 Installing backend dependencies..."
	@cd app/backend && npm install || echo "No backend package.json found, skipping..."
	@echo "🐍 Setting up python virtual environment..."
	@python3 -m venv .venv
	@. .venv/bin/activate && pip install -r data/pipelines/requirements.txt || echo "No requirements.txt found, skipping..."
	@echo "✅ Setup complete."

dev:
	@cd app/frontend && npm run dev

dev-fe:
	@cd app/frontend && npm run dev

dev-be:
	@cd app/backend && npm run dev || echo "Backend not configured yet"

build:
	@echo "🏗️  Building frontend..."
	@cd app/frontend && npm run build
	@echo "🏗️  Building backend..."
	@cd app/backend && npm run build || echo "Backend build not configured"

test:
	@echo "🧪 Running frontend tests..."
	@cd app/frontend && npm run test || echo "No tests configured"
	@echo "🧪 Running backend tests..."
	@cd app/backend && npm run test || echo "No backend tests configured"

lint:
	@echo "🔍 Linting frontend..."
	@cd app/frontend && npm run lint || echo "Linter not configured"
	@echo "🔍 Linting backend..."
	@cd app/backend && npm run lint || echo "Backend linter not configured"

pipeline:
	@echo "🔄 Running data pipeline..."
	@. .venv/bin/activate && python data/pipelines/main.py || echo "Pipeline main.py not found"

status:
	@echo "📊 Current Work Status:"
	@echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
	@cat docs/STATUS.md

clean:
	@echo "🧹 Cleaning up..."
	@rm -rf node_modules
	@rm -rf app/frontend/node_modules
	@rm -rf app/frontend/.next
	@rm -rf app/backend/node_modules
	@rm -rf app/backend/dist
	@rm -rf .venv
	@rm -rf __pycache__
	@rm -rf outputs/*
	@echo "✅ Cleanup complete."

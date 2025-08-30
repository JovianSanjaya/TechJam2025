# TikTok Compliance Analyzer - Complete Setup and Run
# Usage: make setup && make run

.PHONY: help setup install-deps build-extension build-docker run-docker run-extension run-all clean stop logs health

# Default target
help:
	@echo "🚀 TikTok Compliance Analyzer - Setup & Run"
	@echo "============================================="
	@echo ""
	@echo "Quick Start:"
	@echo "  make all          - Complete setup and run everything"
	@echo ""
	@echo "Individual Commands:"
	@echo "  make setup        - Install all dependencies and build everything"
	@echo "  make run          - Run Docker services (backend + frontend)"
	@echo "  make run-extension - Build and package VS Code extension"
	@echo "  make run-all      - Run Docker services + build extension"
	@echo ""
	@echo "Utilities:"
	@echo "  make health       - Check if services are running"
	@echo "  make logs         - Show Docker logs"
	@echo "  make stop         - Stop all Docker services"
	@echo "  make clean        - Clean up containers and build artifacts"
	@echo ""
	@echo "Development:"
	@echo "  make install-deps - Install dependencies only"
	@echo "  make build-docker - Build Docker images only"
	@echo "  make build-extension - Build VS Code extension only"

# Complete setup and run everything
all: setup run-all
	@echo "🎉 Everything is set up and running!"
	@echo "📱 Frontend: http://localhost:5173"
	@echo "🔧 Backend API: http://localhost:8000"
	@echo "📊 Health Check: http://localhost:8000/health"
	@echo "🔌 VS Code Extension: Check Extension Host/dist/"

# Setup everything
setup: install-deps build-extension build-docker
	@echo "✅ Setup complete!"

# Install all dependencies
install-deps:
	@echo "📦 Installing dependencies..."
	@echo "Installing Extension Host dependencies..."
	@cd "Extension Host" && npm install
	@echo "Installing Frontend dependencies..."
	@cd FE && npm install
	@echo "Installing additional dependencies..."
	@cd FE && npm install framer-motion papaparse
	@echo "Installing shadcn/ui dropzone component..."
	@cd FE && npx shadcn@latest add https://www.shadcn.io/registry/dropzone.json --yes
	@echo "✅ Dependencies installed!"

# Build VS Code Extension
build-extension:
	@echo "🔌 Building VS Code Extension..."
	@cd "Extension Host" && npm run package
	@echo "✅ Extension built! Check Extension Host/dist/"

# Build Docker images
build-docker:
	@echo "🐳 Building Docker images..."
	@docker-compose build
	@echo "✅ Docker images built!"

# Run Docker services (backend + frontend) - alias for run-docker
run: run-docker

# Run Docker services (backend + frontend)
run-docker:
	@echo "🚀 Starting Docker services..."
	@docker-compose up -d
	@echo "⏳ Waiting for services to start..."
	@sleep 10
	@make health

# Run VS Code Extension (build and package)
run-extension:
	@echo "🔌 Building VS Code Extension..."
	@cd "Extension Host" && npm run package
	@echo "✅ Extension ready! Install the .vsix file from Extension Host/dist/"

# Run everything (Docker + Extension)
run-all: run-docker run-extension
	@echo "🎉 All services running!"

# Check service health
health:
	@echo "🔍 Checking service health..."
	@echo "Backend Health:"
	@curl -s http://localhost:8000/health | head -20 || echo "❌ Backend not responding"
	@echo ""
	@echo "Frontend:"
	@curl -s http://localhost:5173 > /dev/null && echo "✅ Frontend is running" || echo "❌ Frontend not responding"
	@echo ""
	@echo "Docker Status:"
	@docker-compose ps

# Show Docker logs
logs:
	@echo "📋 Docker service logs:"
	@docker-compose logs -f

# Stop all services
stop:
	@echo "🛑 Stopping Docker services..."
	@docker-compose down
	@echo "✅ Services stopped!"

# Clean up everything
clean: stop
	@echo "🧹 Cleaning up..."
	@docker-compose down -v --remove-orphans
	@docker system prune -f
	@cd "Extension Host" && rm -rf dist/ node_modules/
	@cd FE && rm -rf node_modules/
	@echo "✅ Cleanup complete!"

# Development helpers
dev-backend:
	@echo "🔧 Starting backend in development mode..."
	@cd BE && python3 app.py

dev-frontend:
	@echo "📱 Starting frontend in development mode..."
	@cd FE && npm run dev

dev-extension:
	@echo "🔌 Starting extension in development mode..."
	@cd "Extension Host" && npm run dev

# Quick test
test:
	@echo "🧪 Testing API endpoint..."
	@curl -X POST http://localhost:8000/analyze \
		-H "Content-Type: application/json" \
		-d '{"featureName": "Test Feature", "description": "Test description"}' \
		| head -20

# Environment setup
env-setup:
	@echo "📝 Setting up environment files..."
	@echo "BACKEND_PORT=8000" > .env
	@echo "FRONTEND_PORT=5173" >> .env
	@echo "VITE_API_URL=http://localhost:8000" > FE/.env
	@echo "VITE_APP_NAME=TikTok Compliance Analyzer" >> FE/.env
	@echo "VITE_APP_VERSION=1.0.0" >> FE/.env
	@echo "✅ Environment files created!"

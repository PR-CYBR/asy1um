#!/bin/bash
# Setup script for Project Asylum

set -e

echo "🏗️  Setting up Project Asylum..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "❌ Docker is required but not installed. Aborting." >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose is required but not installed. Aborting." >&2; exit 1; }
command -v terraform >/dev/null 2>&1 || echo "⚠️  Terraform not found. Install it for infrastructure provisioning."

echo "✅ Prerequisites check passed"

# Copy environment file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file. Please edit it with your configuration."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p ai/model/saved_models ai/data
mkdir -p monitoring/prometheus/rules
mkdir -p logs

# Set permissions
echo "🔒 Setting permissions..."
chmod +x honeypot/cowrie/rotate_config.sh

# Initialize Terraform (optional)
if command -v terraform >/dev/null 2>&1; then
    echo "🏗️  Initializing Terraform..."
    cd terraform
    terraform init -backend=false || echo "⚠️  Terraform init failed, continuing..."
    cd ..
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Edit .env file with your configuration"
echo "   2. Run: docker-compose up -d"
echo "   3. Access services:"
echo "      - Grafana: http://localhost:3000 (admin/asylum_admin_2024)"
echo "      - Prometheus: http://localhost:9090"
echo "      - Kibana: http://localhost:5601"
echo "      - AI API: http://localhost:8000"
echo "      - Orchestration API: http://localhost:3001"
echo ""
echo "📚 Documentation: See README.md and docs/"
echo ""

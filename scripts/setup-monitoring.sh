#!/bin/bash

# Index Platform Monitoring Setup Script

set -e

echo "🔍 Setting up monitoring for Index Platform..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Create monitoring directories
echo "📁 Creating monitoring directories..."
mkdir -p monitoring/prometheus/rules
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/alertmanager

# Set up Prometheus
echo "📊 Setting up Prometheus..."
if [ ! -f "monitoring/prometheus/prometheus.yml" ]; then
    echo "❌ Prometheus configuration not found. Please ensure monitoring files are in place."
    exit 1
fi

# Set up Grafana
echo "📈 Setting up Grafana..."
if [ ! -f "monitoring/grafana/provisioning/datasources/prometheus.yml" ]; then
    echo "❌ Grafana datasource configuration not found. Please ensure monitoring files are in place."
    exit 1
fi

# Start monitoring services
echo "🚀 Starting monitoring services..."
docker-compose up -d prometheus grafana alertmanager node-exporter cadvisor postgres-exporter redis-exporter

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check Prometheus
if curl -f http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo "✅ Prometheus is healthy"
else
    echo "❌ Prometheus is not responding"
fi

# Check Grafana
if curl -f http://localhost:3001/api/health > /dev/null 2>&1; then
    echo "✅ Grafana is healthy"
else
    echo "❌ Grafana is not responding"
fi

# Check Alertmanager
if curl -f http://localhost:9093/-/healthy > /dev/null 2>&1; then
    echo "✅ Alertmanager is healthy"
else
    echo "❌ Alertmanager is not responding"
fi

echo ""
echo "🎉 Monitoring setup completed!"
echo ""
echo "📋 Access Information:"
echo "   Prometheus: http://localhost:9090"
echo "   Grafana: http://localhost:3001 (admin/admin)"
echo "   Alertmanager: http://localhost:9093"
echo ""
echo "📊 Available Dashboards:"
echo "   - Backend API Metrics"
echo "   - Infrastructure Metrics"
echo "   - Business Metrics"
echo ""
echo "🔔 Alerting:"
echo "   - Critical alerts: admin@indexplatform.com"
echo "   - Warning alerts: devops@indexplatform.com"
echo ""
echo "🔍 Check service status with: docker-compose ps"
echo "📊 View logs with: docker-compose logs -f prometheus"

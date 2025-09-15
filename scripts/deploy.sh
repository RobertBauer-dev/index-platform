#!/bin/bash

# Index Platform Deployment Script

set -e

echo "🚀 Starting Index Platform deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl is not installed. Please install kubectl and try again."
    exit 1
fi

# Build Docker images
echo "📦 Building Docker images..."
docker build -t index-platform-backend:latest ./backend
docker build -t index-platform-frontend:latest ./frontend

# Apply Kubernetes manifests
echo "🔧 Applying Kubernetes manifests..."

# Create namespace
kubectl apply -f k8s/namespace.yaml

# Apply database
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n index-platform --timeout=300s

# Apply backend
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n index-platform --timeout=300s
kubectl wait --for=condition=ready pod -l app=frontend -n index-platform --timeout=300s

# Apply ingress
kubectl apply -f k8s/ingress.yaml

echo "✅ Deployment completed successfully!"
echo ""
echo "📋 Access Information:"
echo "   Frontend: http://index-platform.local"
echo "   Backend API: http://api.index-platform.local"
echo "   GraphQL Playground: http://api.index-platform.local/graphql"
echo ""
echo "🔍 Check status with: kubectl get pods -n index-platform"
echo "📊 View logs with: kubectl logs -f deployment/backend -n index-platform"

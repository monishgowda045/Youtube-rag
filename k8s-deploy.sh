#!/bin/bash

# Kubernetes Deployment Script for YouTube RAG
# Usage: ./k8s-deploy.sh [deploy|update|delete|status]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

NAMESPACE=${K8S_NAMESPACE:-default}

echo -e "${GREEN}🚀 YouTube RAG Kubernetes Deployment${NC}"

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo -e "${RED}❌ kubectl not found. Please install kubectl first.${NC}"
    exit 1
fi

# Function to deploy
deploy() {
    echo -e "${YELLOW}📦 Deploying to Kubernetes...${NC}"

    # Check if secret exists, if not create it
    if ! kubectl get secret youtube-rag-secrets -n $NAMESPACE &> /dev/null; then
        echo -e "${RED}❌ Secret 'youtube-rag-secrets' not found!${NC}"
        echo "Please create the secret first:"
        echo "kubectl create secret generic youtube-rag-secrets --from-literal=openai-api-key=YOUR_API_KEY"
        exit 1
    fi

    kubectl apply -f k8s-all.yml -n $NAMESPACE
    kubectl rollout status deployment/youtube-rag -n $NAMESPACE
    echo -e "${GREEN}✅ Deployment complete!${NC}"
    echo ""
    echo "🌐 Access your app:"
    echo "kubectl port-forward svc/youtube-rag-service 8501:8501 -n $NAMESPACE"
    echo "Then visit: http://localhost:8501"
}

# Function to update deployment
update() {
    echo -e "${YELLOW}🔄 Updating deployment...${NC}"
    kubectl apply -f k8s-all.yml -n $NAMESPACE
    kubectl rollout restart deployment/youtube-rag -n $NAMESPACE
    kubectl rollout status deployment/youtube-rag -n $NAMESPACE
    echo -e "${GREEN}✅ Update complete!${NC}"
}

# Function to delete deployment
delete() {
    echo -e "${YELLOW}🗑️  Deleting deployment...${NC}"
    kubectl delete -f k8s-all.yml -n $NAMESPACE --ignore-not-found=true
    echo -e "${GREEN}✅ Deletion complete!${NC}"
}

# Function to check status
status() {
    echo -e "${YELLOW}📊 Deployment Status:${NC}"
    kubectl get pods -l app=youtube-rag -n $NAMESPACE
    echo ""
    kubectl get svc youtube-rag-service -n $NAMESPACE
    echo ""
    kubectl get deployment youtube-rag -n $NAMESPACE
}

# Main logic
case "${1:-status}" in
    deploy)
        deploy
        ;;
    update)
        update
        ;;
    delete)
        delete
        ;;
    status)
        status
        ;;
    *)
        echo -e "${RED}Usage: $0 [deploy|update|delete|status]${NC}"
        echo "  deploy - Deploy application to Kubernetes"
        echo "  update - Update existing deployment"
        echo "  delete - Remove deployment from Kubernetes"
        echo "  status - Show deployment status (default)"
        exit 1
        ;;
esac
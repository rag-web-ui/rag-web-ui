#!/bin/bash

# Docker build script for RAG Web UI with video processing support
# This script rebuilds the Docker images with the latest changes

set -e

echo "🚀 Building RAG Web UI Docker Images with Video Processing Support"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Parse command line arguments
ENVIRONMENT="production"
FORCE_REBUILD=false
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --dev|--development)
            ENVIRONMENT="development"
            shift
            ;;
        --force)
            FORCE_REBUILD=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dev, --development    Build for development environment"
            echo "  --force                 Force rebuild all images"
            echo "  --no-cache             Build without using cache"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                     # Build for production"
            echo "  $0 --dev               # Build for development"
            echo "  $0 --force --no-cache  # Force rebuild without cache"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use --help for usage information."
            exit 1
            ;;
    esac
done

print_status "Building for environment: $ENVIRONMENT"

# Set compose file based on environment
if [ "$ENVIRONMENT" = "development" ]; then
    COMPOSE_FILE="docker-compose.dev.yml"
else
    COMPOSE_FILE="docker-compose.yml"
fi

# Build options
BUILD_ARGS=""
if [ "$NO_CACHE" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --no-cache"
fi

if [ "$FORCE_REBUILD" = true ]; then
    BUILD_ARGS="$BUILD_ARGS --force-recreate"
fi

print_status "Using compose file: $COMPOSE_FILE"

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f $COMPOSE_FILE down

# Build images
print_status "Building Docker images..."
if [ "$NO_CACHE" = true ]; then
    print_warning "Building without cache (this may take longer)..."
    docker-compose -f $COMPOSE_FILE build --no-cache
else
    docker-compose -f $COMPOSE_FILE build
fi

print_success "Docker images built successfully!"

# Optional: Start the services
read -p "Do you want to start the services now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting services..."
    docker-compose -f $COMPOSE_FILE up -d
    
    print_success "Services started successfully!"
    print_status "You can access the application at:"
    print_status "  - Frontend: http://localhost"
    print_status "  - Backend API: http://localhost/api"
    print_status "  - MinIO Console: http://localhost:9001"
    
    if [ "$ENVIRONMENT" = "development" ]; then
        print_status "  - Backend Direct: http://localhost:8000"
        print_status "  - Frontend Direct: http://localhost:3000"
    fi
    
    print_status ""
    print_status "To view logs: docker-compose -f $COMPOSE_FILE logs -f"
    print_status "To stop services: docker-compose -f $COMPOSE_FILE down"
else
    print_status "Images built but not started."
    print_status "To start services later: docker-compose -f $COMPOSE_FILE up -d"
fi

print_success "Build process completed!"

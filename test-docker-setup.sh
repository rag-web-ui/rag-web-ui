#!/bin/bash

# Test script for Docker setup with video processing support
# This script verifies that all components are working correctly

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[FAIL]${NC} $1"
}

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Testing: $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        print_success "$test_name"
        ((TESTS_PASSED++))
        return 0
    else
        print_error "$test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

# Function to run a test with output
run_test_with_output() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Testing: $test_name"
    
    if output=$(eval "$test_command" 2>&1); then
        print_success "$test_name"
        echo "  Output: $output"
        ((TESTS_PASSED++))
        return 0
    else
        print_error "$test_name"
        echo "  Error: $output"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "🧪 Testing Docker Setup for Video Processing"
echo "============================================="

# Check if Docker is running
print_status "Checking Docker availability..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi
print_success "Docker is running"

# Check if containers are running
print_status "Checking container status..."
COMPOSE_FILE="docker-compose.yml"
if [ -f "docker-compose.dev.yml" ] && docker-compose -f docker-compose.dev.yml ps | grep -q "Up"; then
    COMPOSE_FILE="docker-compose.dev.yml"
fi

# Test 1: Container Status
run_test "Backend container is running" \
    "docker-compose -f $COMPOSE_FILE ps backend | grep -q 'Up'"

run_test "Database container is running" \
    "docker-compose -f $COMPOSE_FILE ps db | grep -q 'Up'"

run_test "MinIO container is running" \
    "docker-compose -f $COMPOSE_FILE ps minio | grep -q 'Up'"

# Test 2: FFmpeg Installation
run_test_with_output "FFmpeg is installed" \
    "docker-compose -f $COMPOSE_FILE exec -T backend ffmpeg -version | head -1"

# Test 3: Python Dependencies
run_test "Whisper library is available" \
    "docker-compose -f $COMPOSE_FILE exec -T backend python -c 'import whisper; print(\"OK\")'"

run_test "Requests library is available" \
    "docker-compose -f $COMPOSE_FILE exec -T backend python -c 'import requests; print(\"OK\")'"

run_test "Video processor imports work" \
    "docker-compose -f $COMPOSE_FILE exec -T backend python -c 'from app.services.video_processor import get_filename_from_url; print(\"OK\")'"

# Test 4: Environment Variables
run_test_with_output "Whisper model configuration" \
    "docker-compose -f $COMPOSE_FILE exec -T backend python -c 'import os; print(os.getenv(\"WHISPER_MODEL\", \"base\"))'"

run_test_with_output "Video timeout configuration" \
    "docker-compose -f $COMPOSE_FILE exec -T backend python -c 'import os; print(os.getenv(\"VIDEO_DOWNLOAD_TIMEOUT\", \"300\"))'"

# Test 5: Volume Mounts
run_test "Video temp directory exists" \
    "docker-compose -f $COMPOSE_FILE exec -T backend test -d /tmp/video_processing"

run_test "Uploads directory exists" \
    "docker-compose -f $COMPOSE_FILE exec -T backend test -d /app/uploads"

# Test 6: Network Connectivity
run_test "Backend can reach database" \
    "docker-compose -f $COMPOSE_FILE exec -T backend nc -z db 3306"

run_test "Backend can reach MinIO" \
    "docker-compose -f $COMPOSE_FILE exec -T backend nc -z minio 9000"

# Test 7: API Endpoints
if run_test "Backend API is responding" \
    "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/health | grep -q '200\|404'"; then
    
    # Test video upload endpoints exist (will return 401/422 but endpoint exists)
    run_test "Video upload endpoint exists" \
        "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/knowledge-base/1/videos/upload | grep -q '401\|422'"
    
    run_test "Video file upload endpoint exists" \
        "curl -s -o /dev/null -w '%{http_code}' http://localhost/api/knowledge-base/1/videos/upload-files | grep -q '401\|422'"
fi

# Test 8: Whisper Model Download (optional - can be slow)
read -p "Do you want to test Whisper model download? This may take a few minutes (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    run_test_with_output "Whisper model can be loaded" \
        "docker-compose -f $COMPOSE_FILE exec -T backend python -c 'import whisper; model = whisper.load_model(\"tiny\"); print(\"Model loaded successfully\")'"
fi

# Summary
echo ""
echo "============================================="
echo "Test Summary:"
echo "  Passed: $TESTS_PASSED"
echo "  Failed: $TESTS_FAILED"
echo "============================================="

if [ $TESTS_FAILED -eq 0 ]; then
    print_success "All tests passed! Your Docker setup is ready for video processing."
    echo ""
    echo "Next steps:"
    echo "  1. Access the application at http://localhost"
    echo "  2. Create a knowledge base"
    echo "  3. Try uploading a video file or URL"
    echo "  4. Monitor the transcription process"
    exit 0
else
    print_error "Some tests failed. Please check the errors above and refer to the troubleshooting guide."
    echo ""
    echo "Common solutions:"
    echo "  - Rebuild Docker images: docker-compose build --no-cache"
    echo "  - Check logs: docker-compose logs backend"
    echo "  - Verify .env configuration"
    exit 1
fi

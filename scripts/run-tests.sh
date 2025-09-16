#!/bin/bash

# Index Platform Test Runner Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false
PARALLEL=false
SKIP_SLOW=false

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

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE        Test type: unit, integration, performance, system, e2e, all (default: all)"
    echo "  -c, --coverage         Generate coverage report"
    echo "  -v, --verbose          Verbose output"
    echo "  -p, --parallel         Run tests in parallel"
    echo "  -s, --skip-slow        Skip slow tests"
    echo "  -h, --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --type unit --coverage"
    echo "  $0 --type integration --verbose"
    echo "  $0 --type e2e --parallel"
    echo "  $0 --coverage --skip-slow"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            TEST_TYPE="$2"
            shift 2
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -s|--skip-slow)
            SKIP_SLOW=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate test type
case $TEST_TYPE in
    unit|integration|performance|system|e2e|all)
        ;;
    *)
        print_error "Invalid test type: $TEST_TYPE"
        show_usage
        exit 1
        ;;
esac

print_status "Starting Index Platform Test Suite"
print_status "Test Type: $TEST_TYPE"
print_status "Coverage: $COVERAGE"
print_status "Verbose: $VERBOSE"
print_status "Parallel: $PARALLEL"
print_status "Skip Slow: $SKIP_SLOW"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_warning "Docker is not running. Some tests may fail."
fi

# Function to run backend tests
run_backend_tests() {
    local test_type=$1
    local test_path=""
    local pytest_args=""
    
    case $test_type in
        unit)
            test_path="tests/unit/"
            ;;
        integration)
            test_path="tests/integration/"
            ;;
        performance)
            test_path="tests/performance/"
            ;;
        system)
            test_path="tests/system/"
            ;;
        all)
            test_path="tests/"
            ;;
    esac
    
    # Build pytest arguments
    if [ "$COVERAGE" = true ]; then
        pytest_args="$pytest_args --cov=app --cov-report=html --cov-report=term-missing"
    fi
    
    if [ "$VERBOSE" = true ]; then
        pytest_args="$pytest_args -v"
    fi
    
    if [ "$PARALLEL" = true ]; then
        pytest_args="$pytest_args -n auto"
    fi
    
    if [ "$SKIP_SLOW" = true ]; then
        pytest_args="$pytest_args -m 'not slow'"
    fi
    
    print_status "Running backend $test_type tests..."
    
    cd backend
    
    # Set up test environment
    export DATABASE_URL="sqlite:///./test.db"
    export REDIS_URL="redis://localhost:6379/0"
    export SECRET_KEY="test-secret-key"
    
    # Run tests
    if pytest $test_path $pytest_args; then
        print_success "Backend $test_type tests passed"
    else
        print_error "Backend $test_type tests failed"
        return 1
    fi
    
    cd ..
}

# Function to run frontend tests
run_frontend_tests() {
    local test_type=$1
    
    print_status "Running frontend $test_type tests..."
    
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    case $test_type in
        unit)
            if npm run test:unit; then
                print_success "Frontend unit tests passed"
            else
                print_error "Frontend unit tests failed"
                return 1
            fi
            ;;
        e2e)
            # Install Playwright if needed
            if ! npx playwright --version > /dev/null 2>&1; then
                print_status "Installing Playwright..."
                npx playwright install --with-deps
            fi
            
            if npm run test:e2e; then
                print_success "Frontend E2E tests passed"
            else
                print_error "Frontend E2E tests failed"
                return 1
            fi
            ;;
        all)
            # Run unit tests
            if npm run test:unit; then
                print_success "Frontend unit tests passed"
            else
                print_error "Frontend unit tests failed"
                return 1
            fi
            
            # Run E2E tests
            if ! npx playwright --version > /dev/null 2>&1; then
                print_status "Installing Playwright..."
                npx playwright install --with-deps
            fi
            
            if npm run test:e2e; then
                print_success "Frontend E2E tests passed"
            else
                print_error "Frontend E2E tests failed"
                return 1
            fi
            ;;
    esac
    
    cd ..
}

# Function to run security tests
run_security_tests() {
    print_status "Running security tests..."
    
    cd backend
    
    # Install security tools if needed
    if ! command -v bandit &> /dev/null; then
        print_status "Installing security tools..."
        pip install bandit safety
    fi
    
    # Run bandit security scan
    if bandit -r app/ -f json -o security-report.json; then
        print_success "Security scan passed"
    else
        print_warning "Security scan found issues (check security-report.json)"
    fi
    
    # Run safety check
    if safety check --json --output safety-report.json; then
        print_success "Dependency safety check passed"
    else
        print_warning "Dependency safety check found issues (check safety-report.json)"
    fi
    
    cd ..
}

# Function to run load tests
run_load_tests() {
    print_status "Running load tests..."
    
    cd backend
    
    # Install locust if needed
    if ! command -v locust &> /dev/null; then
        print_status "Installing Locust..."
        pip install locust
    fi
    
    # Start the application in background
    print_status "Starting application for load testing..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    APP_PID=$!
    
    # Wait for application to start
    sleep 10
    
    # Run load tests
    if locust -f tests/performance/locustfile.py --headless -u 50 -r 5 -t 30s --html load-test-report.html; then
        print_success "Load tests completed"
    else
        print_error "Load tests failed"
    fi
    
    # Stop the application
    kill $APP_PID
    
    cd ..
}

# Main test execution
case $TEST_TYPE in
    unit)
        run_backend_tests "unit"
        run_frontend_tests "unit"
        ;;
    integration)
        run_backend_tests "integration"
        ;;
    performance)
        run_backend_tests "performance"
        run_load_tests
        ;;
    system)
        run_backend_tests "system"
        ;;
    e2e)
        run_frontend_tests "e2e"
        ;;
    all)
        print_status "Running all test suites..."
        
        # Backend tests
        run_backend_tests "unit"
        run_backend_tests "integration"
        run_backend_tests "performance"
        run_backend_tests "system"
        
        # Frontend tests
        run_frontend_tests "unit"
        run_frontend_tests "e2e"
        
        # Security tests
        run_security_tests
        
        # Load tests
        run_load_tests
        
        print_success "All test suites completed"
        ;;
esac

# Generate test summary
print_status "Generating test summary..."

if [ "$COVERAGE" = true ]; then
    print_status "Coverage reports generated:"
    if [ -d "backend/htmlcov" ]; then
        print_status "  Backend: backend/htmlcov/index.html"
    fi
    if [ -d "frontend/coverage" ]; then
        print_status "  Frontend: frontend/coverage/index.html"
    fi
fi

if [ -f "backend/security-report.json" ]; then
    print_status "Security report: backend/security-report.json"
fi

if [ -f "backend/load-test-report.html" ]; then
    print_status "Load test report: backend/load-test-report.html"
fi

print_success "Test execution completed!"

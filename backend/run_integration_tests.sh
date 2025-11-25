#!/bin/bash
# Integration Test Runner Script

echo "Running CMMS Integration Tests..."
echo "=================================="

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "virtualenv" ]; then
    source virtualenv/bin/activate
fi

# Install test dependencies if needed
pip install -q pytest pytest-django pytest-cov factory-boy

# Run integration tests
echo ""
echo "1. Testing Work Order Lifecycle..."
python -m pytest tests/integration/test_work_order_lifecycle.py -v

echo ""
echo "2. Testing Maintenance Plan Execution..."
python -m pytest tests/integration/test_maintenance_plan_execution.py -v

echo ""
echo "3. Testing ML Prediction Flow..."
python -m pytest tests/integration/test_ml_prediction_flow.py -v

echo ""
echo "4. Testing Notification Delivery..."
python -m pytest tests/integration/test_notification_delivery.py -v

echo ""
echo "=================================="
echo "Integration Tests Complete!"
echo ""
echo "To run all tests with coverage:"
echo "python -m pytest tests/integration/ --cov=apps --cov-report=html"

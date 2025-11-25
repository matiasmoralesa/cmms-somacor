# PowerShell Integration Test Runner Script

Write-Host "Running CMMS Integration Tests..." -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path "virtualenv\Scripts\Activate.ps1") {
    & "virtualenv\Scripts\Activate.ps1"
}

# Install test dependencies if needed
Write-Host "`nInstalling test dependencies..." -ForegroundColor Yellow
pip install -q pytest pytest-django pytest-cov factory-boy

# Run integration tests
Write-Host "`n1. Testing Work Order Lifecycle..." -ForegroundColor Green
python -m pytest tests/integration/test_work_order_lifecycle.py -v

Write-Host "`n2. Testing Maintenance Plan Execution..." -ForegroundColor Green
python -m pytest tests/integration/test_maintenance_plan_execution.py -v

Write-Host "`n3. Testing ML Prediction Flow..." -ForegroundColor Green
python -m pytest tests/integration/test_ml_prediction_flow.py -v

Write-Host "`n4. Testing Notification Delivery..." -ForegroundColor Green
python -m pytest tests/integration/test_notification_delivery.py -v

Write-Host "`n==================================" -ForegroundColor Cyan
Write-Host "Integration Tests Complete!" -ForegroundColor Cyan
Write-Host "`nTo run all tests with coverage:" -ForegroundColor Yellow
Write-Host "python -m pytest tests/integration/ --cov=apps --cov-report=html" -ForegroundColor Yellow

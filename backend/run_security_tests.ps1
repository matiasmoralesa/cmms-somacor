# PowerShell Security Test Runner Script

Write-Host "Running CMMS Security Tests..." -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Activate virtual environment if it exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
} elseif (Test-Path "virtualenv\Scripts\Activate.ps1") {
    & "virtualenv\Scripts\Activate.ps1"
}

Write-Host "`n1. Running Authentication Security Tests..." -ForegroundColor Yellow
python -m pytest tests/security/test_authentication_security.py -v

Write-Host "`n2. Checking Python Dependencies for Vulnerabilities..." -ForegroundColor Yellow
pip install -q safety
safety check --json
if ($LASTEXITCODE -ne 0) {
    Write-Host "Vulnerabilities found!" -ForegroundColor Red
}

Write-Host "`n3. Running Bandit Security Linter..." -ForegroundColor Yellow
pip install -q bandit
bandit -r apps/ -f json -o bandit-report.json
if ($LASTEXITCODE -ne 0) {
    Write-Host "Security issues found - check bandit-report.json" -ForegroundColor Yellow
}

Write-Host "`n4. Checking for Hardcoded Secrets..." -ForegroundColor Yellow
pip install -q detect-secrets
detect-secrets scan --baseline .secrets.baseline
if ($LASTEXITCODE -ne 0) {
    Write-Host "Potential secrets detected" -ForegroundColor Yellow
}

Write-Host "`n5. Checking Django Security Settings..." -ForegroundColor Yellow
python manage.py check --deploy

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "Security Tests Complete!" -ForegroundColor Green
Write-Host "`nReports generated:" -ForegroundColor Cyan
Write-Host "  - bandit-report.json (Security linting)"
Write-Host "  - .secrets.baseline (Secret detection)"
Write-Host "`nReview the security audit checklist:" -ForegroundColor Cyan
Write-Host "  tests/security/SECURITY_AUDIT_CHECKLIST.md"

#!/bin/bash
# Security Test Runner Script

echo "Running CMMS Security Tests..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "virtualenv" ]; then
    source virtualenv/bin/activate
fi

echo ""
echo "${YELLOW}1. Running Authentication Security Tests...${NC}"
python -m pytest tests/security/test_authentication_security.py -v

echo ""
echo "${YELLOW}2. Checking Python Dependencies for Vulnerabilities...${NC}"
pip install -q safety
safety check --json || echo "${RED}Vulnerabilities found!${NC}"

echo ""
echo "${YELLOW}3. Running Bandit Security Linter...${NC}"
pip install -q bandit
bandit -r apps/ -f json -o bandit-report.json || echo "${YELLOW}Security issues found - check bandit-report.json${NC}"

echo ""
echo "${YELLOW}4. Checking for Hardcoded Secrets...${NC}"
pip install -q detect-secrets
detect-secrets scan --baseline .secrets.baseline || echo "${YELLOW}Potential secrets detected${NC}"

echo ""
echo "${YELLOW}5. Checking Django Security Settings...${NC}"
python manage.py check --deploy

echo ""
echo "================================"
echo "${GREEN}Security Tests Complete!${NC}"
echo ""
echo "Reports generated:"
echo "  - bandit-report.json (Security linting)"
echo "  - .secrets.baseline (Secret detection)"
echo ""
echo "Review the security audit checklist:"
echo "  tests/security/SECURITY_AUDIT_CHECKLIST.md"

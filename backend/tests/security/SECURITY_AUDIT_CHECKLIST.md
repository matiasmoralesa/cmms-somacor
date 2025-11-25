# Security Audit Checklist
## CMMS Sistema Avanzado

### Overview
This document provides a comprehensive security audit checklist based on OWASP Top 10 and industry best practices for cloud-native applications.

---

## 1. Authentication Security

### JWT Token Security
- [ ] Access tokens expire within 15 minutes
- [ ] Refresh tokens expire within 7 days
- [ ] Tokens use strong signing algorithm (HS256 or RS256)
- [ ] Token secrets are stored securely (Secret Manager)
- [ ] Token rotation implemented on refresh
- [ ] Tokens stored in httpOnly cookies (not localStorage)
- [ ] CSRF protection enabled for token endpoints

### Password Security
- [ ] Minimum password length: 8 characters
- [ ] Password complexity requirements enforced
- [ ] Passwords hashed using Django's PBKDF2
- [ ] Password reset tokens expire within 1 hour
- [ ] Password reset requires email verification
- [ ] Account lockout after 5 failed login attempts
- [ ] Password history prevents reuse of last 3 passwords

### Session Management
- [ ] Sessions expire after 30 minutes of inactivity
- [ ] Concurrent session limit enforced
- [ ] Session invalidation on logout
- [ ] Session fixation protection enabled
- [ ] Secure session cookies (Secure, HttpOnly, SameSite)

**Test Commands:**
```bash
# Test token expiration
python manage.py test tests.security.test_authentication

# Test password policies
python manage.py test tests.security.test_password_security
```

---

## 2. Authorization and Access Control

### Role-Based Access Control (RBAC)
- [ ] Three roles properly defined (ADMIN, SUPERVISOR, OPERADOR)
- [ ] Role permissions enforced at API level
- [ ] Role permissions enforced at UI level
- [ ] Operators can only view assigned work orders
- [ ] Supervisors can view all work orders
- [ ] Only admins can access admin panel
- [ ] Only admins can manage users
- [ ] Prediction alerts restricted to ADMIN and SUPERVISOR

### API Endpoint Protection
- [ ] All endpoints require authentication (except login/register)
- [ ] Permission classes applied to all viewsets
- [ ] Object-level permissions enforced
- [ ] Unauthorized access returns 403 Forbidden
- [ ] Missing authentication returns 401 Unauthorized

### Data Access Control
- [ ] Users can only access their own data
- [ ] Supervisors can access team data
- [ ] Admins can access all data
- [ ] Soft deletes prevent data loss
- [ ] Audit trail for sensitive operations

**Test Commands:**
```bash
# Test RBAC enforcement
python manage.py test tests.security.test_authorization

# Test endpoint permissions
python manage.py test tests.security.test_api_permissions
```

---

## 3. Input Validation and Sanitization

### API Input Validation
- [ ] All input fields validated using serializers
- [ ] Maximum field lengths enforced
- [ ] Data types validated
- [ ] Required fields enforced
- [ ] Email format validated
- [ ] Phone number format validated
- [ ] RUT (Chilean ID) format validated
- [ ] Date ranges validated
- [ ] Numeric ranges validated

### SQL Injection Prevention
- [ ] Django ORM used for all database queries
- [ ] No raw SQL queries without parameterization
- [ ] User input never concatenated into SQL
- [ ] Database query logging enabled

### XSS Prevention
- [ ] React automatic escaping enabled
- [ ] User-generated content sanitized
- [ ] Content Security Policy (CSP) headers configured
- [ ] X-XSS-Protection header enabled
- [ ] No inline JavaScript in HTML

### File Upload Security
- [ ] File type validation (whitelist approach)
- [ ] File size limits enforced (max 10MB)
- [ ] File content validation (not just extension)
- [ ] Uploaded files scanned for malware (if applicable)
- [ ] Files stored in Cloud Storage (not local filesystem)
- [ ] File URLs use signed URLs with expiration

**Test Commands:**
```bash
# Test input validation
python manage.py test tests.security.test_input_validation

# Test XSS prevention
python manage.py test tests.security.test_xss_prevention

# Test file upload security
python manage.py test tests.security.test_file_upload
```

---

## 4. Data Protection

### Data Encryption
- [ ] Data in transit encrypted with TLS 1.3
- [ ] HTTPS enforced for all connections
- [ ] HTTP Strict Transport Security (HSTS) enabled
- [ ] Data at rest encrypted (Cloud SQL automatic encryption)
- [ ] Sensitive fields encrypted at application level
- [ ] Encryption keys rotated regularly

### Sensitive Data Handling
- [ ] Passwords never logged
- [ ] Tokens never logged
- [ ] PII (Personally Identifiable Information) minimized
- [ ] Credit card data not stored (if applicable)
- [ ] Sensitive data masked in logs
- [ ] Database backups encrypted

### Data Privacy
- [ ] GDPR compliance considerations
- [ ] User consent for data collection
- [ ] Right to data deletion implemented
- [ ] Data retention policies defined
- [ ] Privacy policy accessible

**Test Commands:**
```bash
# Test encryption
python manage.py test tests.security.test_encryption

# Test sensitive data handling
python manage.py test tests.security.test_data_protection
```

---

## 5. API Security

### Rate Limiting
- [ ] Rate limiting enabled (100 requests/minute per user)
- [ ] Anonymous rate limiting (20 requests/minute)
- [ ] Rate limit headers included in responses
- [ ] Rate limit bypass for internal services
- [ ] DDoS protection configured (Cloud Armor)

### CORS Configuration
- [ ] CORS enabled for frontend domain only
- [ ] Wildcard (*) not used in production
- [ ] Credentials allowed only for trusted origins
- [ ] Preflight requests handled correctly

### API Versioning
- [ ] API versioned (/api/v1/)
- [ ] Backward compatibility maintained
- [ ] Deprecated endpoints documented
- [ ] Version sunset policy defined

### API Documentation Security
- [ ] Swagger UI requires authentication in production
- [ ] Sensitive endpoints not exposed in docs
- [ ] Example data doesn't contain real credentials
- [ ] API keys not hardcoded in documentation

**Test Commands:**
```bash
# Test rate limiting
python manage.py test tests.security.test_rate_limiting

# Test CORS
python manage.py test tests.security.test_cors
```

---

## 6. Cloud Security (GCP)

### IAM and Permissions
- [ ] Principle of least privilege applied
- [ ] Service accounts have minimal permissions
- [ ] No overly permissive roles (e.g., Owner, Editor)
- [ ] Service account keys rotated regularly
- [ ] Unused service accounts disabled
- [ ] IAM audit logs enabled

### Network Security
- [ ] Cloud SQL uses private IP only
- [ ] VPC configured properly
- [ ] Firewall rules restrict access
- [ ] Cloud Run ingress control configured
- [ ] VPC Service Controls enabled (if applicable)

### Secrets Management
- [ ] Secrets stored in Secret Manager (not environment variables)
- [ ] Database passwords in Secret Manager
- [ ] API keys in Secret Manager
- [ ] JWT secrets in Secret Manager
- [ ] Secrets access logged
- [ ] Secrets rotated regularly

### Cloud Storage Security
- [ ] Buckets not publicly accessible
- [ ] IAM permissions properly configured
- [ ] Signed URLs used for temporary access
- [ ] Lifecycle policies configured
- [ ] Versioning enabled for critical data

**Audit Commands:**
```bash
# Check IAM permissions
gcloud projects get-iam-policy $PROJECT_ID

# Check Cloud SQL configuration
gcloud sql instances describe cmms-db

# Check Cloud Storage bucket permissions
gsutil iam get gs://$BUCKET_NAME
```

---

## 7. Logging and Monitoring

### Security Logging
- [ ] All authentication attempts logged
- [ ] Failed login attempts logged
- [ ] Authorization failures logged
- [ ] Sensitive operations logged (user management, config changes)
- [ ] Logs include user context (user ID, IP address)
- [ ] Logs sent to Cloud Logging
- [ ] Log retention policy defined (90 days for security logs)

### Audit Trail
- [ ] User actions audited
- [ ] Data modifications tracked
- [ ] Admin actions logged
- [ ] Audit logs immutable
- [ ] Audit logs regularly reviewed

### Security Monitoring
- [ ] Failed login alerts configured
- [ ] Unusual activity alerts configured
- [ ] Error rate alerts configured
- [ ] Cloud Monitoring dashboards created
- [ ] Security incidents response plan defined

**Test Commands:**
```bash
# Test logging
python manage.py test tests.security.test_logging

# View security logs
gcloud logging read "severity>=WARNING" --limit 50
```

---

## 8. Dependency Security

### Python Dependencies
- [ ] All dependencies up to date
- [ ] Known vulnerabilities patched
- [ ] Dependency scanning enabled (pip-audit or safety)
- [ ] Unused dependencies removed
- [ ] Dependencies pinned to specific versions

### Frontend Dependencies
- [ ] npm audit run regularly
- [ ] Known vulnerabilities patched
- [ ] Unused dependencies removed
- [ ] Dependencies pinned to specific versions
- [ ] Automated dependency updates configured (Dependabot)

**Audit Commands:**
```bash
# Check Python dependencies
cd backend
pip install pip-audit
pip-audit

# Check npm dependencies
cd frontend
npm audit
npm audit fix
```

---

## 9. Error Handling and Information Disclosure

### Error Messages
- [ ] Detailed error messages not exposed to users
- [ ] Stack traces not shown in production
- [ ] Generic error messages for authentication failures
- [ ] Error codes used instead of detailed messages
- [ ] Debug mode disabled in production

### Information Disclosure
- [ ] Server version not exposed in headers
- [ ] Technology stack not disclosed
- [ ] Internal paths not exposed
- [ ] Database errors sanitized
- [ ] API responses don't leak sensitive data

**Test Commands:**
```bash
# Test error handling
python manage.py test tests.security.test_error_handling
```

---

## 10. Telegram Bot Security

### Bot Authentication
- [ ] Users authenticated via Telegram ID
- [ ] Telegram ID linked to system user
- [ ] Unauthorized users cannot use bot
- [ ] Bot commands require authentication

### Bot Authorization
- [ ] Role-based command access enforced
- [ ] Operators cannot access admin commands
- [ ] Sensitive data not exposed via bot
- [ ] Bot responses sanitized

### Bot Communication
- [ ] Webhook uses HTTPS
- [ ] Webhook secret token validated
- [ ] Bot token stored securely
- [ ] Rate limiting applied to bot commands

**Test Commands:**
```bash
# Test bot security
python manage.py test tests.security.test_telegram_bot
```

---

## Security Testing Tools

### Automated Security Scanning
```bash
# OWASP ZAP (Zed Attack Proxy)
docker run -t owasp/zap2docker-stable zap-baseline.py -t http://localhost:8000

# Bandit (Python security linter)
pip install bandit
bandit -r backend/apps/

# Safety (Python dependency checker)
pip install safety
safety check

# npm audit (Frontend dependencies)
cd frontend
npm audit

# Trivy (Container scanning)
trivy image gcr.io/$PROJECT_ID/cmms-backend:latest
```

### Manual Security Testing
- [ ] Penetration testing performed
- [ ] SQL injection attempts tested
- [ ] XSS attempts tested
- [ ] CSRF attempts tested
- [ ] Authentication bypass attempts tested
- [ ] Authorization bypass attempts tested
- [ ] File upload vulnerabilities tested
- [ ] API fuzzing performed

---

## Compliance Checklist

### OWASP Top 10 (2021)
- [ ] A01:2021 – Broken Access Control
- [ ] A02:2021 – Cryptographic Failures
- [ ] A03:2021 – Injection
- [ ] A04:2021 – Insecure Design
- [ ] A05:2021 – Security Misconfiguration
- [ ] A06:2021 – Vulnerable and Outdated Components
- [ ] A07:2021 – Identification and Authentication Failures
- [ ] A08:2021 – Software and Data Integrity Failures
- [ ] A09:2021 – Security Logging and Monitoring Failures
- [ ] A10:2021 – Server-Side Request Forgery (SSRF)

### Industry Standards
- [ ] PCI DSS (if handling payment data)
- [ ] GDPR (if handling EU citizen data)
- [ ] ISO 27001 considerations
- [ ] SOC 2 considerations

---

## Security Incident Response Plan

### Incident Detection
1. Monitor security alerts in Cloud Monitoring
2. Review security logs daily
3. Investigate anomalies immediately

### Incident Response
1. Identify and contain the incident
2. Assess the impact
3. Notify stakeholders
4. Remediate the vulnerability
5. Document the incident
6. Conduct post-mortem

### Contact Information
- Security Lead: [Name] - [Email] - [Phone]
- Technical Lead: [Name] - [Email] - [Phone]
- GCP Support: [Support Plan Details]

---

## Sign-Off

| Role | Name | Signature | Date | Status |
|------|------|-----------|------|--------|
| Security Lead | | | | |
| Technical Lead | | | | |
| DevOps Lead | | | | |
| Compliance Officer | | | | |

---

## Audit History

| Date | Auditor | Findings | Status |
|------|---------|----------|--------|
| 2024-11-13 | Initial Audit | Checklist created | In Progress |
| | | | |

---

**Document Version:** 1.0  
**Last Updated:** 2024-11-13  
**Next Audit:** Quarterly

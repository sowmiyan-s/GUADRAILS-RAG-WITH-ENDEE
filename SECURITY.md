# Security Policy

## Supported Versions

We maintain security support for the latest major and minor versions. Always upgrade to the latest version for security patches.

| Version | Supported | Status |
|---------|-----------|---------|
| 1.1.x   | ✅ Yes | Current |
| 1.0.x   | ⚠️ Limited | Outdated |
| < 1.0.0 | ❌ No | Deprecated |

**Recommendation**: Always use the latest version (`v1.1.4+`).

## Security Principles

**GUADRAILS-RAG-WITH-ENDEE** is built with security at its core:

- 🔒 **Privacy by Default**: 100% local execution, no data transmission
- 🛡️ **Zero-Trust Architecture**: All inputs validated, all outputs sanitized
- 🔐 **Encryption Support**: HTTPS/TLS for all network communication
- 📋 **Audit Logging**: Comprehensive logging for compliance
- 🚨 **PII Protection**: Automatic detection and masking of sensitive data
- 🔑 **API Security**: Rate limiting, authentication, CORS controls

---

## Reporting a Vulnerability

We take security very seriously. If you discover a security vulnerability in **GUADRAILS-RAG-WITH-ENDEE**, please report it responsibly and **DO NOT** open a public GitHub issue.

### Responsible Disclosure Process

1. **DO NOT** disclose the vulnerability publicly
2. **Email**: Contact the security team at **sowmiyan.s-dev@example.com**
3. **Include**:
   - Clear description of the vulnerability
   - Affected component(s)
   - Proof of concept (PoC) or reproduction steps
   - Potential impact/severity
   - Any suggested mitigation

### Response Timeline
- **24 hours**: Initial acknowledgment
- **72 hours**: Initial investigation and assessment
- **7 days**: Security update or mitigation plan
- **30 days**: Public disclosure (with reporter credit if desired)

---

## Security Features & Best Practices

### 1. Local-First Architecture
```python
# ✅ All processing stays on your machine
- Document Loading → Local
- Embedding Generation → Local (or your API key)
- Vector Storage → Endee (Local)
- LLM Inference → Ollama (Local) or Your API Key
- Results → Returned locally
```

### 2. Data Protection

#### Input Validation
- File size limits enforced
- File type whitelisting
- Malware scanning for uploads (optional)
- Rate limiting on API endpoints

#### Output Sanitization
- PII detection and masking
- Automatic redaction of sensitive patterns:
  - Email addresses
  - Phone numbers
  - Credit card numbers
  - SSN/Tax IDs
  - API keys
  - Database credentials

### 3. API Security
```bash
# Enable authentication
ENABLE_AUTH=true
API_KEY=$(openssl rand -hex 32)

# Configure rate limiting
ENABLE_RATE_LIMIT=true
RATE_LIMIT=100_requests_per_minute

# Enable HTTPS
ENABLE_HTTPS=true
SSL_CERT=/path/to/server.crt
SSL_KEY=/path/to/server.key

# Restrict access
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8
```

### 4. Audit & Compliance
```python
# Enable comprehensive logging
LOG_QUERIES=true
LOG_LEVEL=INFO
LOG_FILE=/var/log/guadrails/audit.log

# Compliance classifications
SAFETY_LEVEL=restricted  # public|internal|confidential|restricted
```

---

## Security Checklist for Deployment

### Before Production
- [ ] Disable debug mode: `DEBUG=false`
- [ ] Enable authentication: `ENABLE_AUTH=true`
- [ ] Set strong API key: `API_KEY=<strong_random_key>`
- [ ] Configure HTTPS: `ENABLE_HTTPS=true`
- [ ] Enable rate limiting: `ENABLE_RATE_LIMIT=true`
- [ ] Set safety level: `SAFETY_LEVEL=confidential` (at minimum)
- [ ] Enable audit logging: `LOG_QUERIES=true`
- [ ] Restrict IP access: `ALLOWED_IPS=...`
- [ ] Update to latest version
- [ ] Review dependencies: `pip audit`

### Network Security
- [ ] Use firewall to restrict access
- [ ] Enable SSL/TLS encryption
- [ ] Use VPN for remote access
- [ ] Monitor network traffic
- [ ] Regular security audits

### Data Security
- [ ] Encrypt data at rest (filesystem encryption)
- [ ] Encrypt vectors in Endee
- [ ] Regular backups with encryption
- [ ] Access control lists (ACLs)
- [ ] Data retention policies

### Operational Security
- [ ] Regular security updates
- [ ] Monitor logs for anomalies
- [ ] Incident response plan
- [ ] Security training for team
- [ ] Regular penetration testing

---

## Known Security Considerations

### LLM Provider Security

**Using Cloud LLMs (OpenAI, Anthropic, Google)?**

- Queries are sent to provider's servers
- Review provider's privacy policies
- Use dedicated API keys with minimal permissions
- Monitor API usage and costs
- Consider data residency requirements

**Using Local Ollama (Recommended for Privacy)?**

- ✅ All data stays on your machine
- ✅ No external API calls needed
- ⚠️ Requires sufficient local compute resources
- ⚠️ Model quality depends on chosen model

### Endee Vector Database

- ✅ Local storage by default
- ✅ No external connectivity required
- ✅ Direct filesystem access only
- ⚠️ Protect database files with filesystem permissions
- ⚠️ Regular backups recommended

### Dependencies

We regularly audit dependencies for vulnerabilities:
```bash
# Check for vulnerable packages
pip audit

# Update all packages
pip install --upgrade -r requirements.txt
```

---

## Security Resources

- 📖 [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- 🔒 [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- 🛡️ [Python Security Best Practices](https://python.readthedocs.io/en/latest/library/security_warnings.html)
- 🔑 [API Security](https://owasp.org/www-project-api-security/)

---

## Questions?

- 🔐 **Security Issues**: Email sowmiyan.s-dev@example.com (private)
- 📖 **Security Docs**: See [README](./README.md#-solution-how-endee-solves-traditional-rag-issues)
- 💬 **General Questions**: [GitHub Discussions](https://github.com/sowmiyan-s/GUADRAILS-RAG-WITH-ENDEE/discussions)

---

**Last Updated**: April 2026  
**Version**: 1.1.4

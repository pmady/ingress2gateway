# Security Policy

## Reporting a Vulnerability

The ingress2gateway team takes security seriously. We appreciate your efforts to responsibly disclose your findings.

### How to Report

If you discover a security vulnerability, please report it by:

1. **DO NOT** create a public GitHub issue
2. Email the maintainers directly or use GitHub's private vulnerability reporting feature
3. Provide detailed information about the vulnerability

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity, typically within 30 days

### Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Security Best Practices

When deploying ingress2gateway:

1. **Network Security**: Run behind a reverse proxy in production
2. **Input Validation**: The application validates YAML input, but always sanitize user input
3. **Updates**: Keep dependencies updated for security patches
4. **Access Control**: Restrict access to the application as needed

## Acknowledgments

We thank all security researchers who help keep ingress2gateway secure.

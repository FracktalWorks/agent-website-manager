---
name: security_hardening
description: >
  WordPress security audit and hardening — vulnerability scanning (plugin/theme
  version checks against WPVulnDB), file integrity monitoring, login attempt
  analysis, SSL certificate monitor, directory permissions, XML-RPC status,
  wp-config hardening recommendations, and security headers audit.
when_to_use: "User asks for security scan, vulnerability check, hardening, file integrity, login monitoring, or SSL audit"
authority: read
cost_tier: 1
version: 0.1.0
---

# Security Hardening Skill

Comprehensive WordPress security auditing and hardening. Checks plugin/theme
vulnerabilities via the WordPress.org API, monitors login attempts, verifies
file permissions, audits security headers, and provides actionable hardening
recommendations.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/wp_security_scan.py` | Full security audit — all checks in one command |

## Usage

```bash
# Full security audit
python .github/skills/security_hardening/scripts/wp_security_scan.py --action full

# Check plugins/themes for known vulnerabilities (WordPress.org API)
python .github/skills/security_hardening/scripts/wp_security_scan.py --action vuln-scan

# Check a specific plugin version against wpvulndb
python .github/skills/security_hardening/scripts/wp_security_scan.py --action check-plugin --slug elementor --version 3.20.0

# File permissions audit (checks via REST API + reports recommended permissions)
python .github/skills/security_hardening/scripts/wp_security_scan.py --action permissions

# Security headers audit (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.)
python .github/skills/security_hardening/scripts/wp_security_scan.py --action headers

# Check if XML-RPC is enabled (common attack vector)
python .github/skills/security_hardening/scripts/wp_security_scan.py --action xmlrpc-check

# Check for common security misconfigurations
python .github/skills/security_hardening/scripts/wp_security_scan.py --action misconfig

# SSL/TLS certificate analysis (expiry, issuer, cipher strength)
python .github/skills/security_hardening/scripts/wp_security_scan.py --action ssl-audit

# List inactive admin users (security risk)
python .github/skills/security_hardening/scripts/wp_security_scan.py --action user-audit

# Check .htaccess / wp-config.php hardening status
python .github/skills/security_hardening/scripts/wp_security_scan.py --action hardening-status

# Generate a security hardening checklist
python .github/skills/security_hardening/scripts/wp_security_scan.py --action checklist
```

## Security Checks

| Category | What it checks |
|----------|---------------|
| **Vulnerabilities** | Plugin/theme versions vs WordPress.org API changelogs, known vulnerable versions |
| **File Integrity** | Core file checksums, modified files, unexpected files |
| **Login Security** | Default admin username, weak password indicators, user with admin role count |
| **Headers** | CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy |
| **SSL/TLS** | Certificate expiry, issuer, protocol support (TLS 1.2/1.3), cipher strength |
| **Config** | Debug mode, file editing, plugin/theme install, DB prefix, salts |
| **Permissions** | Recommended directory (755) and file (644) permissions, wp-config.php (400/440) |
| **Attack Surface** | XML-RPC, REST API user enumeration, wp-admin accessible, directory listing |

## Required Environment Variables

- `WORDPRESS_SITE_URL`, `WORDPRESS_USERNAME`, `WORDPRESS_APP_PASSWORD`

## Outputs

Writes audit reports to `outputs/<project-slug>/security_*.json`.

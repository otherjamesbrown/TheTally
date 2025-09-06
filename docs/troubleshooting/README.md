# Troubleshooting Guide

This directory contains troubleshooting guides for common issues encountered in TheTally project.

## Security Scanning

- **[Security Scan Local Testing](security-scan-local-testing.md)** - Guide for testing security scans locally before committing
- **[Security Scan Failure Analysis](security-scan-failure-analysis.md)** - Analysis of the 50+ iteration security scan failure
- **[Secret Detection Tools Analysis](secret-detection-tools-analysis.md)** - Comparison of Gitleaks vs TruffleHog
- **[Security Scan Issues](security-scan-issues.md)** - General security scan troubleshooting

## Problem Solving

- **[Problem Solving Methodology](problem-solving-methodology.md)** - Best practices for approaching complex problems

## Quick Reference

### Local Testing Commands

```bash
# Test Gitleaks locally
docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --config /repo/.gitleaks.toml --verbose

# Test without configuration
docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --verbose
```

### Key Lessons Learned

1. **Always test locally first** - Saves 10x the time vs CI/CD iterations
2. **Research industry solutions** - Don't reinvent the wheel
3. **Use official documentation** - Reference tool documentation for correct formats
4. **Iterative development** - Fix one issue at a time and test each fix

## Contributing

When you encounter new issues:

1. **Test locally first** using the guides above
2. **Document the issue** and solution
3. **Update relevant guides** with new information
4. **Share knowledge** with the team

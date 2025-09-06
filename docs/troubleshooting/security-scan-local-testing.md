# Security Scan Local Testing Guide

## Overview

This guide provides step-by-step instructions for testing security scanning tools locally before committing changes to CI/CD pipelines. This prevents the 50+ iteration failures we experienced with security scans.

## Prerequisites

- Docker installed and running
- Access to the repository
- Understanding of the security scanning tools used

## Gitleaks Local Testing

### 1. Test Current Configuration

```bash
# Test Gitleaks with current configuration
docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --config /repo/.gitleaks.toml --verbose
```

### 2. Test Without Configuration (Default Rules)

```bash
# Test with default Gitleaks rules
docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --verbose
```

### 3. Test Specific File Patterns

```bash
# Test specific files only
docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --config /repo/.gitleaks.toml --path docs/ --verbose
```

## Configuration Validation

### 1. Validate TOML Syntax

```bash
# Check TOML syntax (if you have toml-tools installed)
python -c "import toml; toml.load('.gitleaks.toml')"
```

### 2. Test Configuration Loading

```bash
# Test if Gitleaks can load the configuration
docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --config /repo/.gitleaks.toml --help
```

## Common Issues and Solutions

### Issue: TOML Parsing Errors

**Error**: `Failed to load config error="expected type 'string', got unconvertible type 'map[string]interface {}'"`

**Solution**: 
1. Use correct TOML format: `[allowlist]` not `[[AllowList]]`
2. Use arrays for `paths` and `regexes`: `paths = ["pattern1", "pattern2"]`
3. Reference [official Gitleaks configuration](https://github.com/gitleaks/gitleaks)

### Issue: False Positives

**Problem**: Legitimate environment variables flagged as secrets

**Solution**:
1. Add patterns to `regexes` array in `[allowlist]` section
2. Add file patterns to `paths` array to exclude documentation
3. Test locally to verify exclusions work

### Issue: Configuration Not Working

**Problem**: Changes don't take effect

**Solution**:
1. Verify TOML syntax is correct
2. Test locally with Docker
3. Check file paths are relative to repository root
4. Ensure regex patterns are properly escaped

## Best Practices

### 1. Always Test Locally First

- **Before committing** any security scan changes
- **Use Docker** to match CI/CD environment
- **Test with actual repository data**

### 2. Iterative Development

- **Make small changes** and test each one
- **Fix one issue at a time**
- **Verify each fix works** before moving to next

### 3. Documentation

- **Document working commands** for future reference
- **Keep configuration examples** in troubleshooting docs
- **Update this guide** when new issues are discovered

## Time Savings

- **Local testing**: 5 minutes per iteration
- **CI/CD testing**: 5-10 minutes per iteration + wait time
- **Total saved**: 50+ iterations × 5 minutes = 4+ hours

## Example Workflow

1. **Make configuration change**
2. **Test locally**: `docker run --rm -v $(pwd):/repo zricethezav/gitleaks:latest detect --source /repo --config /repo/.gitleaks.toml --verbose`
3. **Verify results**: Check for leaks and false positives
4. **Fix issues**: Adjust configuration as needed
5. **Repeat until working**: Only commit when local test passes
6. **Commit and push**: Changes are ready for CI/CD

## References

- [Gitleaks GitHub Repository](https://github.com/gitleaks/gitleaks)
- [Gitleaks Configuration Documentation](https://github.com/gitleaks/gitleaks/blob/master/config/gitleaks.toml)
- [Problem Solving Methodology](../troubleshooting/problem-solving-methodology.md)

# Pull Request Workflow with Google Code Assist

## Overview

TheTally uses Google Code Assist (Gemini Code Assist) for AI-powered code reviews to ensure code quality, security, and adherence to project standards. This provides native GitHub integration without requiring external API keys.

## Workflow Components

### 1. Branch Protection Rules

The `main` branch is protected with the following requirements:
- ✅ **Pull Request Required**: All changes must go through a PR
- ✅ **AI Review**: Every PR is automatically reviewed by an AI agent
- ✅ **Status Checks**: All tests must pass before merging
- ✅ **Approval Required**: At least 1 approval needed
- ✅ **Up-to-date Branches**: Branch must be up-to-date with main

### 2. Google Code Assist Integration

Google Code Assist automatically reviews every PR using Gemini AI, configured specifically for TheTally's standards:

#### Security Checks
- JWT authentication implementation
- Input validation and sanitization
- SQL injection prevention
- Multi-tenant security (tenant_id usage)
- 2FA implementation compliance

#### Code Quality Checks
- Type hints and TypeScript compliance
- Error handling patterns
- Naming conventions
- Function size and complexity
- Documentation completeness

#### Architecture Checks
- Service layer separation
- Modular design principles
- Database model structure
- API endpoint organization
- Logging implementation

#### Testing Requirements
- Unit test coverage
- Integration test implementation
- Test file organization
- Mock usage patterns

## Configuration Files

### `config.yaml`
Main configuration file that customizes Google Code Assist behavior for TheTally:
- Severity thresholds and comment limits
- Project-specific context and rules
- Security and architecture focus areas
- File patterns to ignore during review

### `.github/CODEOWNERS`
Defines code ownership rules for different parts of the codebase.

### `.github/workflows/setup-branch-protection.yml`
Workflow to automatically configure branch protection rules.

### `.github/workflows/test-gemini-setup.yml`
Test workflow to verify Google Code Assist configuration.

## Setup Instructions

### 1. Prerequisites

- GitHub repository
- Google account (for Code Assist access)
- Repository admin permissions

### 2. Install Google Code Assist

1. Go to [Gemini Code Assist for GitHub](https://github.com/apps/gemini-code-assist)
2. Sign in to your GitHub account
3. Click **Install**
4. Select your organization and repository
5. Complete setup in the Admin Console

### 3. Automated Setup

Run the setup script:
```bash
./scripts/setup-google-code-assist.sh
```

### 4. Manual Configuration

1. **Branch Protection**:
   - Go to `Settings > Branches`
   - Add rule for `main` branch
   - Enable "Require a pull request before merging"

2. **Customize Review Behavior**:
   - Edit `config.yaml` to adjust review settings
   - Modify severity thresholds and focus areas
   - Add project-specific rules

## Google Code Assist Review Process

### 1. Automatic Trigger
- Reviews every new PR automatically
- No manual configuration required
- Works on all branches targeting `main`

### 2. Analysis
- Uses Gemini AI to analyze code changes
- Applies TheTally-specific rules from `config.yaml`
- Focuses on security, architecture, and code quality

### 3. Review Criteria
Google Code Assist checks against TheTally's specific rules:

```yaml
# From config.yaml
security_requirements:
  - "All API endpoints protected by default"
  - "Input validation and sanitization required"
  - "SQL injection prevention via ORM"
  - "Multi-tenant data isolation"
  - "JWT authentication with refresh tokens"
  - "2FA implementation using TOTP"
```

### 4. Interactive Commands
Use these commands in PR comments:
- `/gemini summary` - Get PR summary
- `/gemini review` - Detailed code review
- `/gemini help` - Show available commands
- `/gemini` - Ask specific questions

### 5. Output
- Automatic review comments with severity levels
- Code suggestions that can be committed directly
- References to project style guide
- Interactive Q&A capability

## Example Google Code Assist Review

Google Code Assist will automatically post comments like:

```markdown
## 🔍 Code Review by gemini-code-assist[bot]

### Summary
The changes implement user authentication with JWT handling. Overall good structure, but some security concerns need attention.

### 🚨 High Severity Issues
- **Line 45**: Missing tenant_id validation in user creation
- **Line 67**: No input sanitization for email field

### ⚠️ Medium Severity Issues  
- **Line 23**: Missing type hints for function parameters
- **Line 89**: Consider adding error handling for database operations

### 💡 Suggestions
- Add structured logging for audit trail
- Implement unit tests for authentication service
- Use dependency injection for database session

### 🔧 Code Suggestion
```python
# Suggested improvement for line 45
def create_user(user_data: UserCreateSchema, tenant_id: str) -> User:
    # Add tenant_id validation
    if not tenant_id:
        raise ValueError("tenant_id is required")
    # ... rest of implementation
```

---
*Review generated by Google Code Assist*
```

## Best Practices

### For Developers

1. **Small, Focused PRs**: Keep changes small and focused on single features
2. **Clear Descriptions**: Provide detailed PR descriptions
3. **Test Coverage**: Include tests for new functionality
4. **Follow Standards**: Adhere to TheTally's coding standards
5. **Address Feedback**: Respond to AI review feedback promptly

### For AI Review

1. **Specific Feedback**: AI provides line-specific suggestions when possible
2. **Actionable Items**: All feedback includes clear next steps
3. **Context Aware**: Reviews consider TheTally's specific architecture
4. **Security Focus**: Prioritizes security and compliance issues

## Troubleshooting

### Common Issues

1. **AI Review Not Running**:
   - Check if `OPENAI_API_KEY` secret is set
   - Verify workflow file syntax
   - Check Actions tab for error logs

2. **Branch Protection Not Working**:
   - Run the setup workflow manually
   - Check repository permissions
   - Verify branch protection settings

3. **Review Quality Issues**:
   - Update `ai-rules.md` with more specific guidelines
   - Adjust AI prompt in `ai_reviewer.py`
   - Provide more context in PR descriptions

### Debug Mode

Enable debug logging by adding to workflow:
```yaml
env:
  DEBUG: true
```

## Future Enhancements

- [ ] Custom review templates for different file types
- [ ] Integration with code coverage reports
- [ ] Automated fix suggestions
- [ ] Integration with security scanning tools
- [ ] Custom AI models trained on TheTally codebase

## Support

For issues with the PR workflow:
1. Check the Actions tab for workflow logs
2. Review the AI review output for specific feedback
3. Update the AI rules if needed
4. Contact the development team for assistance

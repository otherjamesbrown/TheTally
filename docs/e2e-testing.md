# End-to-End Testing Guide

This document provides comprehensive information about the E2E testing setup for TheTally application.

## Overview

TheTally uses Playwright for end-to-end testing, providing comprehensive coverage of the authentication flow and user interactions.

## Test Structure

### Test Files
- `e2e/auth.spec.ts` - Authentication flow tests (login, logout, navigation)
- `e2e/registration.spec.ts` - User registration flow tests
- `e2e/dashboard.spec.ts` - Dashboard and protected route tests
- `e2e/helpers/test-data.ts` - Test data and mock responses

### Test Coverage

#### Authentication Flow (`auth.spec.ts`)
- ✅ Home page navigation and button visibility
- ✅ Login page navigation and form validation
- ✅ Register page navigation and form validation
- ✅ Form validation errors (empty fields, password mismatch)
- ✅ Navigation between login and register pages
- ✅ Invalid credentials handling
- ✅ Network error handling
- ✅ Protected route redirection
- ✅ Loading states during form submission

#### Registration Flow (`registration.spec.ts`)
- ✅ Successful user registration
- ✅ Duplicate email/username error handling
- ✅ Password validation (length, confirmation)
- ✅ Email format validation
- ✅ Server error handling
- ✅ Form clearing after successful registration
- ✅ Loading states during registration

#### Dashboard and Auth State (`dashboard.spec.ts`)
- ✅ Redirect to login when accessing protected routes
- ✅ User information display after login
- ✅ Token expiration handling
- ✅ Logout functionality and token clearing
- ✅ Network error handling
- ✅ Navigation from dashboard
- ✅ Loading states while fetching user data

## Running Tests

### Prerequisites
- Node.js 18+
- Playwright browsers installed (`npx playwright install`)

### Commands

```bash
# Run all E2E tests
npm run test:e2e

# Run tests with UI mode (interactive)
npm run test:e2e:ui

# Run tests in headed mode (visible browser)
npm run test:e2e:headed

# Run tests in debug mode
npm run test:e2e:debug

# Run specific test file
npx playwright test auth.spec.ts

# Run tests in specific browser
npx playwright test --project=chromium
```

### Environment Variables

```bash
# Frontend URL (default: http://localhost:3000)
FRONTEND_URL=http://localhost:3000

# Backend URL (default: http://localhost:8000)
BACKEND_URL=http://localhost:8000

# CI mode (disables parallel execution)
CI=true
```

## Test Configuration

### Playwright Config (`playwright.config.ts`)
- **Test Directory**: `./e2e`
- **Parallel Execution**: Enabled (disabled in CI)
- **Retries**: 2 on CI, 0 locally
- **Reporters**: HTML report
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome, Mobile Safari
- **Auto-start**: Development server starts automatically

### Test Features
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry
- **Auto-cleanup**: localStorage cleared before each test

## Mock Data and API Responses

### Test Data (`e2e/helpers/test-data.ts`)
- Valid user credentials
- Invalid test data
- Mock JWT tokens
- API response templates

### API Mocking
Tests use Playwright's `page.route()` to mock API responses:
- Successful authentication
- Error responses (400, 401, 500)
- Network failures
- Slow responses for loading state testing

## Test Scenarios

### 1. User Registration Flow
1. Navigate to home page
2. Click "Sign Up" button
3. Fill registration form with valid data
4. Submit form
5. Verify redirect to dashboard
6. Verify tokens stored in localStorage

### 2. User Login Flow
1. Navigate to login page
2. Enter valid credentials
3. Submit form
4. Verify redirect to dashboard
5. Verify user data displayed

### 3. Authentication State Management
1. Access protected route without auth
2. Verify redirect to login
3. Login successfully
4. Access protected route
5. Verify access granted
6. Logout
7. Verify redirect to login
8. Verify tokens cleared

### 4. Error Handling
1. Invalid credentials
2. Network errors
3. Server errors
4. Token expiration
5. Form validation errors

## Best Practices

### Test Organization
- Each test file focuses on a specific feature
- Tests are independent and can run in any order
- Setup and teardown handled in `beforeEach` hooks

### Data Management
- Use test data helpers for consistent test data
- Mock API responses for predictable test behavior
- Clear state between tests (localStorage, cookies)

### Assertions
- Use semantic selectors (`data-testid` attributes)
- Test both positive and negative scenarios
- Verify loading states and error messages
- Check URL changes and redirects

### Performance
- Use `page.waitForURL()` for navigation assertions
- Use `page.waitForSelector()` for element visibility
- Avoid hard-coded timeouts when possible

## Debugging Tests

### Debug Mode
```bash
npm run test:e2e:debug
```
- Opens browser in debug mode
- Allows step-by-step execution
- Shows browser console and network logs

### UI Mode
```bash
npm run test:e2e:ui
```
- Interactive test runner
- Visual test execution
- Easy test selection and debugging

### Trace Viewer
```bash
npx playwright show-trace trace.zip
```
- Detailed execution trace
- Network requests and responses
- Screenshots and videos

## CI/CD Integration

### GitHub Actions
```yaml
- name: Run E2E tests
  run: |
    cd frontend
    npm run test:e2e
  env:
    CI: true
```

### Docker Integration
```bash
# Run tests in Docker container
docker run --rm -v $(pwd):/app -w /app/frontend node:18 npm run test:e2e
```

## Troubleshooting

### Common Issues

1. **Tests timing out**
   - Increase timeout in config
   - Check if dev server is running
   - Verify API endpoints are accessible

2. **Element not found**
   - Check if element has `data-testid` attribute
   - Verify element is visible and not hidden
   - Use `page.waitForSelector()` for dynamic content

3. **API mocking not working**
   - Verify route pattern matches API calls
   - Check if route is registered before navigation
   - Use `page.route()` before `page.goto()`

4. **Flaky tests**
   - Add proper waits for async operations
   - Use deterministic test data
   - Avoid hard-coded delays

### Debug Commands
```bash
# Run single test with debug info
npx playwright test auth.spec.ts --debug

# Run with verbose output
npx playwright test --reporter=list

# Generate test report
npx playwright show-report
```

## Maintenance

### Regular Tasks
- Update test data when API changes
- Review and update selectors when UI changes
- Add new test cases for new features
- Remove obsolete tests

### Test Data Updates
- Update mock responses when API schema changes
- Add new test users for different scenarios
- Update error messages to match backend responses

### Performance Monitoring
- Monitor test execution time
- Optimize slow tests
- Remove redundant assertions
- Use parallel execution effectively

## Future Enhancements

### Planned Improvements
- [ ] Add 2FA flow testing
- [ ] Add password reset flow testing
- [ ] Add accessibility testing
- [ ] Add visual regression testing
- [ ] Add performance testing
- [ ] Add cross-browser compatibility testing

### Integration with CI/CD
- [ ] Automated test execution on PRs
- [ ] Test result reporting
- [ ] Screenshot comparison
- [ ] Performance regression detection

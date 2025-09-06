# Frontend Troubleshooting Guide

## Common Frontend Issues and Solutions

This guide helps diagnose and fix common frontend rendering and functionality issues in TheTally.

## Blank White Screen Issues

### Symptoms
- Browser shows blank white screen
- No JavaScript errors in console
- Network requests appear to succeed
- HTML structure is present but no React content renders

### Root Causes and Solutions

#### 1. React Version Incompatibility
**Problem**: Using pre-release or incompatible React versions
**Solution**:
```bash
# Check current React version
npm list react react-dom

# Downgrade to stable LTS version
npm install react@^18.2.0 react-dom@^18.2.0

# Clean install
rm -rf node_modules package-lock.json
npm install
```

#### 2. Material-UI Version Conflicts
**Problem**: Using incompatible Material-UI versions with React
**Solution**:
```bash
# Use stable Material-UI v5 with React 18
npm install @mui/material@^5.15.20 @mui/icons-material@^5.15.20

# Check for peer dependency warnings
npm ls --depth=0
```

#### 3. ESLint Configuration Issues
**Problem**: ESLint v9+ incompatibility with other packages
**Solution**:
```bash
# Use stable ESLint v8
npm install eslint@^8.57.0

# Use traditional .eslintrc.cjs instead of flat config
# Remove eslint.config.js and create .eslintrc.cjs
```

#### 4. JavaScript Runtime Errors
**Problem**: Silent JavaScript errors preventing React from rendering
**Diagnosis**:
1. Open browser DevTools (F12)
2. Check Console tab for errors
3. Check Network tab for failed requests
4. Look for import/export errors

**Solution**:
```bash
# Check for missing imports
grep -r "import.*from" src/ | grep -v "node_modules"

# Verify all imports are correct
# Fix any missing or incorrect import statements
```

## API Integration Issues

### Symptoms
- Frontend loads but API calls fail
- 404 errors for API endpoints
- CORS errors
- Network errors in console

### Solutions

#### 1. API Proxy Configuration
**Problem**: Frontend trying to call APIs on wrong port
**Solution**: Configure Vite proxy in `vite.config.ts`:
```typescript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://backend:8000',  // Docker service name
        changeOrigin: true,
        secure: false,
      },
    },
  },
})
```

#### 2. CORS Configuration
**Problem**: Backend not allowing frontend requests
**Solution**: Update backend CORS settings:
```python
# In backend/app/core/config.py
CORS_ORIGINS = ["http://localhost:3000", "http://localhost:5173"]
```

#### 3. Missing Backend Endpoints
**Problem**: Frontend calling non-existent API endpoints
**Solution**: Check backend logs and verify endpoint exists:
```bash
# Check backend logs
docker-compose logs backend

# Test API endpoint directly
curl http://localhost:8000/api/v1/health
```

## Component Rendering Issues

### Symptoms
- Components don't render
- Missing UI elements
- Styling issues
- Console errors about missing components

### Solutions

#### 1. Missing Imports
**Problem**: Components not imported correctly
**Solution**:
```typescript
// Check all imports are correct
import React from 'react';
import { Button, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
```

#### 2. Icon Import Issues
**Problem**: Material-UI icons not found
**Solution**:
```typescript
// Use correct icon names
import { HealthAndSafety, SystemUpdate } from '@mui/icons-material';
// NOT: import { HealthCheck } from '@mui/icons-material';
```

#### 3. Router Configuration
**Problem**: React Router not working correctly
**Solution**:
```typescript
// Ensure proper router setup
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

// Add future flags for React Router v6
<Router future={{ v7_startTransition: true }}>
```

## Testing Issues

### Symptoms
- E2E tests fail
- Tests pass but don't verify complete functionality
- Tests timeout or hang

### Solutions

#### 1. Test Element Selection
**Problem**: Tests can't find elements
**Solution**:
```typescript
// Use proper selectors for Material-UI components
await page.locator('input[name="email"]').fill('test@example.com');
// NOT: await page.getByTestId('email-input').fill('test@example.com');
```

#### 2. Test Timeout Issues
**Problem**: Tests timeout waiting for elements
**Solution**:
```typescript
// Add proper timeouts and wait conditions
await expect(page.getByText('Welcome, Test User!')).toBeVisible({ timeout: 10000 });
```

#### 3. Complete Flow Testing
**Problem**: Tests only verify partial functionality
**Solution**: Always verify complete user experience:
```typescript
// Verify complete flow, not just redirects
await expect(page).toHaveURL('/dashboard');
await expect(page.getByText('Welcome, Test User!')).toBeVisible();
await expect(page.getByText('Email: test@example.com')).toBeVisible();
```

## Performance Issues

### Symptoms
- Slow page loads
- High memory usage
- Bundle size too large

### Solutions

#### 1. Bundle Analysis
```bash
# Analyze bundle size
npm run build
npx webpack-bundle-analyzer dist/static/js/*.js
```

#### 2. Code Splitting
```typescript
// Use lazy loading for routes
const Dashboard = lazy(() => import('./pages/DashboardPage'));
```

#### 3. Dependency Optimization
```bash
# Check for unused dependencies
npx depcheck

# Remove unused packages
npm uninstall unused-package
```

## Debugging Tools

### Browser DevTools
1. **Console Tab**: Check for JavaScript errors
2. **Network Tab**: Verify API calls and responses
3. **Elements Tab**: Inspect DOM structure
4. **Sources Tab**: Debug JavaScript execution

### React DevTools
1. Install React DevTools browser extension
2. Check component tree and props
3. Verify state changes
4. Profile component performance

### Vite DevTools
1. Check Vite dev server logs
2. Verify hot module replacement
3. Check build output for errors

## Prevention Strategies

### 1. Dependency Management
- Always use stable, LTS versions
- Test updates incrementally
- Lock major versions in package.json
- Regular security audits

### 2. Code Quality
- Use TypeScript for type safety
- Implement proper error boundaries
- Add comprehensive logging
- Write thorough tests

### 3. Monitoring
- Set up error tracking (Sentry)
- Monitor performance metrics
- Track user experience issues
- Regular health checks

## Emergency Recovery

### Quick Fix for Blank Screen
```bash
# 1. Check browser console for errors
# 2. Clear browser cache completely
# 3. Restart development server
docker-compose restart frontend

# 4. If still broken, reset to known good state
git checkout main
rm -rf node_modules package-lock.json
npm install
docker-compose up --build
```

### Rollback Strategy
```bash
# 1. Identify last working commit
git log --oneline

# 2. Rollback to working state
git checkout <working-commit-hash>

# 3. Rebuild and test
docker-compose up --build
npm run test:e2e
```

---

*This troubleshooting guide should be updated as new issues are discovered and resolved.*

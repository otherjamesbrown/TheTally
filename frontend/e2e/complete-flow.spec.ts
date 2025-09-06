import { test, expect } from '@playwright/test';

test.describe('Complete User Flow Test', () => {
  test('should complete full registration and login flow', async ({ page }) => {
    // Clear localStorage
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());

    // Generate unique email for this test run
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    const username = `testuser${timestamp}`;

    // === REGISTRATION FLOW ===
    console.log('🔄 Testing registration flow...');
    
    await page.goto('/register');
    
    // Fill out registration form
    await page.locator('input[name="firstName"]').fill('Test');
    await page.locator('input[name="lastName"]').fill('User');
    await page.locator('input[name="username"]').fill(username);
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.locator('input[name="confirmPassword"]').fill('TestPassword123!');
    
    // Submit registration
    await page.getByTestId('register-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify dashboard displays user data correctly
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
    await expect(page.getByText(`Email: ${email}`)).toBeVisible();
    await expect(page.getByText(`Username: ${username}`)).toBeVisible();
    await expect(page.getByText('Status: Active')).toBeVisible();
    await expect(page.getByText('Verified: No')).toBeVisible();
    await expect(page.getByText('2FA Enabled: No')).toBeVisible();
    
    console.log('✅ Registration flow completed successfully');

    // === LOGOUT FLOW ===
    console.log('🔄 Testing logout flow...');
    
    // Test logout
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL('/login');
    
    // Verify tokens are cleared
    const accessTokenAfterLogout = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshTokenAfterLogout = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessTokenAfterLogout).toBeNull();
    expect(refreshTokenAfterLogout).toBeNull();
    
    console.log('✅ Logout flow completed successfully');

    // === LOGIN FLOW ===
    console.log('🔄 Testing login flow...');
    
    // Test login
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.getByTestId('login-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify dashboard displays user data correctly after login
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
    await expect(page.getByText(`Email: ${email}`)).toBeVisible();
    await expect(page.getByText(`Username: ${username}`)).toBeVisible();
    await expect(page.getByText('Status: Active')).toBeVisible();
    await expect(page.getByText('Verified: No')).toBeVisible();
    await expect(page.getByText('2FA Enabled: No')).toBeVisible();
    
    // Verify tokens are stored after login
    const accessTokenAfterLogin = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshTokenAfterLogin = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessTokenAfterLogin).toBeTruthy();
    expect(refreshTokenAfterLogin).toBeTruthy();
    
    console.log('✅ Login flow completed successfully');

    // === NAVIGATION TEST ===
    console.log('🔄 Testing navigation...');
    
    // Test navigation to health page
    await page.getByTestId('health-button').click();
    await expect(page).toHaveURL('/health');
    await expect(page.getByText('System Health')).toBeVisible();
    await expect(page.getByText('Backend API Status')).toBeVisible();
    await expect(page.getByText('Status: HEALTHY')).toBeVisible({ timeout: 10000 });
    
    // Navigate back to dashboard
    await page.goto('/dashboard');
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
    
    console.log('✅ Navigation flow completed successfully');

    console.log('🎉 Complete user flow test passed!');
  });

  test('should handle invalid login credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill in invalid credentials
    await page.locator('input[name="email"]').fill('invalid@example.com');
    await page.locator('input[name="password"]').fill('wrongpassword');
    
    // Submit form
    await page.getByTestId('login-button').click();
    
    // Should show error message
    await expect(page.getByText(/Authentication failed|Login failed|Invalid/)).toBeVisible();
    
    // Should stay on login page
    await expect(page).toHaveURL('/login');
    
    console.log('✅ Invalid login handling test passed');
  });

  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Clear any existing tokens
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    
    // Try to access dashboard without authentication
    await page.goto('/dashboard');
    
    // Should be redirected to login
    await expect(page).toHaveURL('/login');
    
    console.log('✅ Protected route redirect test passed');
  });
});

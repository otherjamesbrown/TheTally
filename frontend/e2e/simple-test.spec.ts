import { test, expect } from '@playwright/test';

test.describe('Simple Full Stack Test', () => {
  test('should register and login successfully', async ({ page }) => {
    // Clear localStorage
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());

    // Generate unique email for this test run
    const timestamp = Date.now();
    const email = `test${timestamp}@example.com`;
    const username = `testuser${timestamp}`;

    // Test registration
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
    
    // Verify user data is displayed
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
    await expect(page.getByText(`Email: ${email}`)).toBeVisible();
    
    // Test logout
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL('/login');
    
    // Test login
    await page.locator('input[name="email"]').fill(email);
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.getByTestId('login-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
  });

  test('should test health endpoint', async ({ page }) => {
    await page.goto('/health');
    
    // Should show health status
    await expect(page.getByText('System Health')).toBeVisible();
    await expect(page.getByText('Backend API Status')).toBeVisible();
    
    // Wait for health data to load
    await expect(page.getByText('Status: HEALTHY')).toBeVisible({ timeout: 10000 });
  });
});

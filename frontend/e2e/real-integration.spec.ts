import { test, expect } from '@playwright/test';

test.describe('Real Integration Tests - Full Stack', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should successfully register and login with real backend', async ({ page }) => {
    // Test registration with real backend
    await page.goto('/register');
    
    // Fill out registration form with valid data
    await page.locator('input[name="firstName"]').fill('Test');
    await page.locator('input[name="lastName"]').fill('User');
    await page.locator('input[name="username"]').fill('testuser');
    await page.locator('input[name="email"]').fill('test@example.com');
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.locator('input[name="confirmPassword"]').fill('TestPassword123!');
    
    // Submit registration form
    await page.getByTestId('register-button').click();
    
    // Should redirect to dashboard after successful registration
    await expect(page).toHaveURL('/dashboard');
    
    // Check that tokens are stored
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessToken).toBeTruthy();
    expect(refreshToken).toBeTruthy();
    
    // Verify user data is displayed on dashboard
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
    await expect(page.getByText('Email: test@example.com')).toBeVisible();
    await expect(page.getByText('Username: testuser')).toBeVisible();
  });

  test('should handle login with existing user', async ({ page }) => {
    // First, create a user via API (since we can't register the same user twice)
    await page.goto('/register');
    
    // Fill out registration form
    await page.locator('input[name="firstName"]').fill('Login');
    await page.locator('input[name="lastName"]').fill('Test');
    await page.locator('input[name="username"]').fill('logintest');
    await page.locator('input[name="email"]').fill('login@example.com');
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.locator('input[name="confirmPassword"]').fill('TestPassword123!');
    
    // Submit registration
    await page.getByTestId('register-button').click();
    await expect(page).toHaveURL('/dashboard');
    
    // Logout
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL('/login');
    
    // Now test login
    await page.locator('input[name="email"]').fill('login@example.com');
    await page.locator('input[name="password"]').fill('TestPassword123!');
    
    // Submit login form
    await page.getByTestId('login-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Verify user data is displayed
    await expect(page.getByText('Welcome, Login Test!')).toBeVisible();
    await expect(page.getByText('Email: login@example.com')).toBeVisible();
    await expect(page.getByText('Username: logintest')).toBeVisible();
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
  });

  test('should handle duplicate email registration', async ({ page }) => {
    // First registration
    await page.goto('/register');
    await page.locator('input[name="firstName"]').fill('First');
    await page.locator('input[name="lastName"]').fill('User');
    await page.locator('input[name="username"]').fill('firstuser');
    await page.locator('input[name="email"]').fill('duplicate@example.com');
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.locator('input[name="confirmPassword"]').fill('TestPassword123!');
    await page.getByTestId('register-button').click();
    await expect(page).toHaveURL('/dashboard');
    
    // Logout
    await page.getByTestId('logout-button').click();
    
    // Try to register with same email
    await page.goto('/register');
    await page.locator('input[name="firstName"]').fill('Second');
    await page.locator('input[name="lastName"]').fill('User');
    await page.locator('input[name="username"]').fill('seconduser');
    await page.locator('input[name="email"]').fill('duplicate@example.com');
    await page.locator('input[name="password"]').fill('TestPassword123!');
    await page.locator('input[name="confirmPassword"]').fill('TestPassword123!');
    await page.getByTestId('register-button').click();
    
    // Should show error message
    await expect(page.getByText(/already registered|already exists|duplicate/)).toBeVisible();
    
    // Should stay on register page
    await expect(page).toHaveURL('/register');
  });

  test('should test health endpoint integration', async ({ page }) => {
    await page.goto('/health');
    
    // Should show health status
    await expect(page.getByText('System Health')).toBeVisible();
    await expect(page.getByText('Backend API Status')).toBeVisible();
    
    // Should show healthy status
    await expect(page.getByText('Status: HEALTHY')).toBeVisible();
    
    // Should show version and environment info
    await expect(page.getByText('1.0.0')).toBeVisible();
    await expect(page.getByText('development')).toBeVisible();
  });

  test('should test navigation between pages', async ({ page }) => {
    // Test home page
    await page.goto('/');
    await expect(page.getByText('Welcome to TheTally')).toBeVisible();
    
    // Navigate to login
    await page.getByTestId('login-button').click();
    await expect(page).toHaveURL('/login');
    
    // Navigate to register
    await page.getByTestId('register-link').click();
    await expect(page).toHaveURL('/register');
    
    // Navigate to health
    await page.goto('/health');
    await expect(page.getByText('System Health')).toBeVisible();
    
    // Navigate back to home
    await page.getByTestId('home-button').click();
    await expect(page).toHaveURL('/');
  });
});

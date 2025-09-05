import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should display login and register buttons on home page', async ({ page }) => {
    await page.goto('/');
    
    // Check that login and register buttons are visible
    await expect(page.getByTestId('login-button')).toBeVisible();
    await expect(page.getByTestId('register-button')).toBeVisible();
  });

  test('should navigate to login page when login button is clicked', async ({ page }) => {
    await page.goto('/');
    
    // Click login button
    await page.getByTestId('login-button').click();
    
    // Check that we're on the login page
    await expect(page).toHaveURL('/login');
    await expect(page.getByTestId('email-input')).toBeVisible();
    await expect(page.getByTestId('password-input')).toBeVisible();
    await expect(page.getByTestId('login-button')).toBeVisible();
  });

  test('should navigate to register page when register button is clicked', async ({ page }) => {
    await page.goto('/');
    
    // Click register button
    await page.getByTestId('register-button').click();
    
    // Check that we're on the register page
    await expect(page).toHaveURL('/register');
    await expect(page.getByTestId('email-input')).toBeVisible();
    await expect(page.getByTestId('password-input')).toBeVisible();
    await expect(page.getByTestId('register-button')).toBeVisible();
  });

  test('should show validation errors for empty login form', async ({ page }) => {
    await page.goto('/login');
    
    // Try to submit empty form
    await page.getByTestId('login-button').click();
    
    // Check that form validation prevents submission
    await expect(page.getByTestId('email-input')).toHaveAttribute('required');
    await expect(page.getByTestId('password-input')).toHaveAttribute('required');
  });

  test('should show validation errors for empty register form', async ({ page }) => {
    await page.goto('/register');
    
    // Try to submit empty form
    await page.getByTestId('register-button').click();
    
    // Check that form validation prevents submission
    await expect(page.getByTestId('email-input')).toHaveAttribute('required');
    await expect(page.getByTestId('password-input')).toHaveAttribute('required');
    await expect(page.getByTestId('first-name-input')).toHaveAttribute('required');
    await expect(page.getByTestId('last-name-input')).toHaveAttribute('required');
    await expect(page.getByTestId('username-input')).toHaveAttribute('required');
  });

  test('should show password mismatch error for register form', async ({ page }) => {
    await page.goto('/register');
    
    // Fill out form with mismatched passwords
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('differentpassword');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Check for password mismatch error
    await expect(page.getByText('Passwords do not match')).toBeVisible();
  });

  test('should navigate between login and register pages', async ({ page }) => {
    // Start at login page
    await page.goto('/login');
    
    // Click register link
    await page.getByTestId('register-link').click();
    await expect(page).toHaveURL('/register');
    
    // Click login link
    await page.getByTestId('login-link').click();
    await expect(page).toHaveURL('/login');
  });

  test('should handle login with invalid credentials', async ({ page }) => {
    await page.goto('/login');
    
    // Fill in invalid credentials
    await page.getByTestId('email-input').fill('invalid@example.com');
    await page.getByTestId('password-input').fill('wrongpassword');
    
    // Submit form
    await page.getByTestId('login-button').click();
    
    // Wait for error message
    await expect(page.getByText(/Invalid|Login failed|Unauthorized/)).toBeVisible();
  });

  test('should handle registration with invalid email', async ({ page }) => {
    await page.goto('/register');
    
    // Fill out form with invalid email
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('invalid-email');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Check that email validation prevents submission
    await expect(page.getByTestId('email-input')).toHaveAttribute('type', 'email');
  });

  test('should handle network error gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/api/v1/auth/login', route => route.abort());
    
    await page.goto('/login');
    
    // Fill in credentials
    await page.getByTestId('email-input').fill('test@example.com');
    await page.getByTestId('password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('login-button').click();
    
    // Check for network error message
    await expect(page.getByText('Network error. Please try again.')).toBeVisible();
  });

  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Try to access dashboard without authentication
    await page.goto('/dashboard');
    
    // Should be redirected to login
    await expect(page).toHaveURL('/login');
  });

  test('should show loading state during form submission', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/v1/auth/login', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Invalid credentials' })
      });
    });
    
    await page.goto('/login');
    
    // Fill in credentials
    await page.getByTestId('email-input').fill('test@example.com');
    await page.getByTestId('password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('login-button').click();
    
    // Check that loading state is shown
    await expect(page.getByRole('progressbar')).toBeVisible();
    
    // Wait for error message
    await expect(page.getByText('Invalid credentials')).toBeVisible();
  });
});

import { test, expect } from '@playwright/test';

test.describe('User Registration Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should successfully register a new user', async ({ page }) => {
    // Mock successful registration
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          expires_in: 1800,
          refresh_expires_in: 604800
        })
      });
    });

    await page.goto('/register');
    
    // Fill out registration form
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Check that tokens are stored
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessToken).toBe('mock-access-token');
    expect(refreshToken).toBe('mock-refresh-token');
  });

  test('should show error for duplicate email registration', async ({ page }) => {
    // Mock duplicate email error
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Email already registered'
        })
      });
    });

    await page.goto('/register');
    
    // Fill out registration form
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('existing@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Should show error message
    await expect(page.getByText('Email already registered')).toBeVisible();
    
    // Should stay on register page
    await expect(page).toHaveURL('/register');
  });

  test('should show error for duplicate username registration', async ({ page }) => {
    // Mock duplicate username error
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Username already taken'
        })
      });
    });

    await page.goto('/register');
    
    // Fill out registration form
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('existinguser');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Should show error message
    await expect(page.getByText('Username already taken')).toBeVisible();
  });

  test('should validate password length', async ({ page }) => {
    await page.goto('/register');
    
    // Fill out form with short password
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('short');
    await page.getByTestId('confirm-password-input').fill('short');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Should show password length error
    await expect(page.getByText('Password must be at least 8 characters long')).toBeVisible();
  });

  test('should validate email format', async ({ page }) => {
    await page.goto('/register');
    
    // Fill out form with invalid email
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('invalid-email');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Try to submit form
    await page.getByTestId('register-button').click();
    
    // Email validation should prevent submission
    await expect(page.getByTestId('email-input')).toHaveAttribute('type', 'email');
  });

  test('should handle server error during registration', async ({ page }) => {
    // Mock server error
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 500,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Internal server error'
        })
      });
    });

    await page.goto('/register');
    
    // Fill out registration form
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Should show error message
    await expect(page.getByText('Internal server error')).toBeVisible();
  });

  test('should clear form data after successful registration', async ({ page }) => {
    // Mock successful registration
    await page.route('**/api/v1/auth/register', async route => {
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          expires_in: 1800,
          refresh_expires_in: 604800
        })
      });
    });

    await page.goto('/register');
    
    // Fill out registration form
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Navigate back to register page
    await page.goto('/register');
    
    // Form should be cleared
    await expect(page.getByTestId('first-name-input')).toHaveValue('');
    await expect(page.getByTestId('last-name-input')).toHaveValue('');
    await expect(page.getByTestId('username-input')).toHaveValue('');
    await expect(page.getByTestId('email-input')).toHaveValue('');
    await expect(page.getByTestId('password-input')).toHaveValue('');
    await expect(page.getByTestId('confirm-password-input')).toHaveValue('');
  });

  test('should show loading state during registration', async ({ page }) => {
    // Mock slow API response
    await page.route('**/api/v1/auth/register', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          expires_in: 1800,
          refresh_expires_in: 604800
        })
      });
    });

    await page.goto('/register');
    
    // Fill out registration form
    await page.getByTestId('first-name-input').fill('John');
    await page.getByTestId('last-name-input').fill('Doe');
    await page.getByTestId('username-input').fill('johndoe');
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    await page.getByTestId('confirm-password-input').fill('password123');
    
    // Submit form
    await page.getByTestId('register-button').click();
    
    // Check that loading state is shown
    await expect(page.getByRole('progressbar')).toBeVisible();
    
    // Wait for redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
  });
});

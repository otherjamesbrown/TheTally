import { test, expect } from '@playwright/test';

test.describe('Dashboard and Authentication State', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('should redirect to login when accessing dashboard without authentication', async ({ page }) => {
    await page.goto('/dashboard');
    
    // Should be redirected to login page
    await expect(page).toHaveURL('/login');
  });

  test('should display user information after successful login', async ({ page }) => {
    // Mock successful login
    await page.route('**/api/v1/auth/login', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          expires_in: 1800,
          refresh_expires_in: 604800
        })
      });
    });

    // Mock user data endpoint
    await page.route('**/api/v1/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-123',
          email: 'john@example.com',
          username: 'johndoe',
          first_name: 'John',
          last_name: 'Doe',
          full_name: 'John Doe',
          is_active: true,
          is_verified: true,
          totp_enabled: false,
          timezone: 'UTC',
          language: 'en',
          last_login: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    await page.goto('/login');
    
    // Fill in login credentials
    await page.getByTestId('email-input').fill('john@example.com');
    await page.getByTestId('password-input').fill('password123');
    
    // Submit login form
    await page.getByTestId('login-button').click();
    
    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    
    // Check that user information is displayed
    await expect(page.getByText('Welcome, John Doe!')).toBeVisible();
    await expect(page.getByText('Email: john@example.com')).toBeVisible();
    await expect(page.getByText('Username: johndoe')).toBeVisible();
    await expect(page.getByText('Status: Active')).toBeVisible();
    await expect(page.getByText('Verified: Yes')).toBeVisible();
    await expect(page.getByText('2FA Enabled: No')).toBeVisible();
  });

  test('should handle token expiration and redirect to login', async ({ page }) => {
    // Set expired token in localStorage
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'expired-token');
    });

    // Mock token expiration response
    await page.route('**/api/v1/auth/me', async route => {
      await route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Token expired'
        })
      });
    });

    await page.goto('/dashboard');
    
    // Should redirect to login page
    await expect(page).toHaveURL('/login');
    
    // Tokens should be cleared
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessToken).toBeNull();
    expect(refreshToken).toBeNull();
  });

  test('should logout successfully and clear tokens', async ({ page }) => {
    // Set tokens in localStorage
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-access-token');
      localStorage.setItem('refresh_token', 'mock-refresh-token');
    });

    // Mock user data endpoint
    await page.route('**/api/v1/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-123',
          email: 'john@example.com',
          username: 'johndoe',
          first_name: 'John',
          last_name: 'Doe',
          full_name: 'John Doe',
          is_active: true,
          is_verified: true,
          totp_enabled: false,
          timezone: 'UTC',
          language: 'en',
          last_login: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    await page.goto('/dashboard');
    
    // Wait for dashboard to load
    await expect(page.getByText('Welcome, John Doe!')).toBeVisible();
    
    // Click logout button
    await page.getByTestId('logout-button').click();
    
    // Should redirect to login page
    await expect(page).toHaveURL('/login');
    
    // Tokens should be cleared
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessToken).toBeNull();
    expect(refreshToken).toBeNull();
  });

  test('should handle network error when loading user data', async ({ page }) => {
    // Set valid token in localStorage
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-access-token');
    });

    // Mock network error
    await page.route('**/api/v1/auth/me', route => route.abort());

    await page.goto('/dashboard');
    
    // Should show error message
    await expect(page.getByText('Network error. Please try again.')).toBeVisible();
    
    // Should show back to login button
    await expect(page.getByText('Back to Login')).toBeVisible();
  });

  test('should navigate to other pages from dashboard', async ({ page }) => {
    // Set tokens in localStorage
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-access-token');
    });

    // Mock user data endpoint
    await page.route('**/api/v1/auth/me', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-123',
          email: 'john@example.com',
          username: 'johndoe',
          first_name: 'John',
          last_name: 'Doe',
          full_name: 'John Doe',
          is_active: true,
          is_verified: true,
          totp_enabled: false,
          timezone: 'UTC',
          language: 'en',
          last_login: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    await page.goto('/dashboard');
    
    // Wait for dashboard to load
    await expect(page.getByText('Welcome, John Doe!')).toBeVisible();
    
    // Click home button
    await page.getByTestId('home-button').click();
    await expect(page).toHaveURL('/');
    
    // Navigate back to dashboard
    await page.goto('/dashboard');
    
    // Click health button
    await page.getByTestId('health-button').click();
    await expect(page).toHaveURL('/health');
  });

  test('should show loading state while fetching user data', async ({ page }) => {
    // Set valid token in localStorage
    await page.evaluate(() => {
      localStorage.setItem('access_token', 'mock-access-token');
    });

    // Mock slow API response
    await page.route('**/api/v1/auth/me', async route => {
      await new Promise(resolve => setTimeout(resolve, 1000));
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          id: 'user-123',
          email: 'john@example.com',
          username: 'johndoe',
          first_name: 'John',
          last_name: 'Doe',
          full_name: 'John Doe',
          is_active: true,
          is_verified: true,
          totp_enabled: false,
          timezone: 'UTC',
          language: 'en',
          last_login: '2024-01-01T00:00:00Z',
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        })
      });
    });

    await page.goto('/dashboard');
    
    // Should show loading spinner
    await expect(page.getByRole('progressbar')).toBeVisible();
    
    // Wait for dashboard to load
    await expect(page.getByText('Welcome, John Doe!')).toBeVisible();
  });
});

import { test, expect } from '@playwright/test';

test.describe('Registration Test', () => {
  test('should register successfully and redirect to dashboard', async ({ page }) => {
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
    
    // Check that tokens are stored
    const accessToken = await page.evaluate(() => localStorage.getItem('access_token'));
    const refreshToken = await page.evaluate(() => localStorage.getItem('refresh_token'));
    expect(accessToken).toBeTruthy();
    expect(refreshToken).toBeTruthy();
    
    // Verify dashboard displays user data correctly
    await expect(page.getByText('Welcome, Test User!')).toBeVisible();
    await expect(page.getByText(`Email: ${email}`)).toBeVisible();
    await expect(page.getByText(`Username: ${username}`)).toBeVisible();
    await expect(page.getByText('Status: Active')).toBeVisible();
    await expect(page.getByText('Verified: No')).toBeVisible();
    await expect(page.getByText('2FA Enabled: No')).toBeVisible();
    
    console.log(`✅ Registration successful for user: ${email}`);
    console.log(`✅ Access token stored: ${accessToken ? 'Yes' : 'No'}`);
    console.log(`✅ Refresh token stored: ${refreshToken ? 'Yes' : 'No'}`);
    console.log(`✅ Dashboard displays user data correctly`);
  });
});

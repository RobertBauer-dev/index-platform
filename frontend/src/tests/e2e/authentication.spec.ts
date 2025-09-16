/**
 * E2E tests for Authentication functionality
 */
import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test('should display login form', async ({ page }) => {
    // Check if login form elements are visible
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
    await expect(page.locator('[data-testid="username-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
  });

  test('should allow successful login', async ({ page }) => {
    // Fill login form
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Should navigate to dashboard
    await page.waitForURL('**/dashboard');
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  });

  test('should handle invalid credentials', async ({ page }) => {
    // Fill login form with invalid credentials
    await page.fill('[data-testid="username-input"]', 'invaliduser');
    await page.fill('[data-testid="password-input"]', 'wrongpassword');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-error"]')).toContainText('Invalid credentials');
    
    // Should remain on login page
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should handle empty form submission', async ({ page }) => {
    // Try to submit empty form
    await page.click('[data-testid="login-button"]');
    
    // Should show validation errors
    await expect(page.locator('[data-testid="username-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-error"]')).toBeVisible();
  });

  test('should handle network errors gracefully', async ({ page }) => {
    // Mock network failure
    await page.route('**/api/v1/auth/token', route => route.abort());
    
    // Fill login form
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Should show network error
    await expect(page.locator('[data-testid="network-error"]')).toBeVisible();
  });

  test('should persist login state', async ({ page }) => {
    // Login successfully
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForURL('**/dashboard');
    
    // Refresh page
    await page.reload();
    
    // Should remain logged in
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  });

  test('should allow logout', async ({ page }) => {
    // Login first
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForURL('**/dashboard');
    
    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('[data-testid="logout-button"]');
    
    // Should navigate back to login page
    await page.waitForURL('**/login');
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should redirect to login when accessing protected routes', async ({ page }) => {
    // Try to access protected route without login
    await page.goto('http://localhost:3000/dashboard');
    
    // Should redirect to login page
    await page.waitForURL('**/login');
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should show loading state during login', async ({ page }) => {
    // Fill login form
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    
    // Submit form
    await page.click('[data-testid="login-button"]');
    
    // Should show loading state
    await expect(page.locator('[data-testid="login-loading"]')).toBeVisible();
    
    // Wait for navigation
    await page.waitForURL('**/dashboard');
    
    // Loading state should be hidden
    await expect(page.locator('[data-testid="login-loading"]')).not.toBeVisible();
  });

  test('should handle token expiration', async ({ page }) => {
    // Login successfully
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForURL('**/dashboard');
    
    // Mock token expiration by intercepting API calls
    await page.route('**/api/v1/**', route => {
      route.fulfill({
        status: 401,
        contentType: 'application/json',
        body: JSON.stringify({ detail: 'Token expired' })
      });
    });
    
    // Try to make an API call
    await page.reload();
    
    // Should redirect to login page
    await page.waitForURL('**/login');
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
  });

  test('should be accessible with keyboard navigation', async ({ page }) => {
    // Navigate to username field with Tab
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="username-input"]')).toBeFocused();
    
    // Type username
    await page.keyboard.type('admin');
    
    // Navigate to password field
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="password-input"]')).toBeFocused();
    
    // Type password
    await page.keyboard.type('admin123');
    
    // Navigate to login button
    await page.keyboard.press('Tab');
    await expect(page.locator('[data-testid="login-button"]')).toBeFocused();
    
    // Submit with Enter
    await page.keyboard.press('Enter');
    
    // Should navigate to dashboard
    await page.waitForURL('**/dashboard');
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if login form is visible and properly sized
    await expect(page.locator('[data-testid="login-form"]')).toBeVisible();
    await expect(page.locator('[data-testid="username-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="password-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="login-button"]')).toBeVisible();
    
    // Test login on mobile
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    await page.waitForURL('**/dashboard');
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  });

  test('should handle multiple login attempts', async ({ page }) => {
    // First attempt with wrong credentials
    await page.fill('[data-testid="username-input"]', 'wronguser');
    await page.fill('[data-testid="password-input"]', 'wrongpass');
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    
    // Second attempt with correct credentials
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    // Should succeed
    await page.waitForURL('**/dashboard');
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
  });

  test('should clear form after failed login', async ({ page }) => {
    // Fill form with wrong credentials
    await page.fill('[data-testid="username-input"]', 'wronguser');
    await page.fill('[data-testid="password-input"]', 'wrongpass');
    await page.click('[data-testid="login-button"]');
    
    await expect(page.locator('[data-testid="login-error"]')).toBeVisible();
    
    // Password should be cleared for security
    await expect(page.locator('[data-testid="password-input"]')).toHaveValue('');
    
    // Username might be cleared or kept (depending on UX design)
    // This test assumes username is kept for convenience
    await expect(page.locator('[data-testid="username-input"]')).toHaveValue('wronguser');
  });
});

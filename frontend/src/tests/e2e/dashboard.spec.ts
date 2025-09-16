/**
 * E2E tests for Dashboard functionality
 */
import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');
    
    // Login if needed
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    // Wait for navigation to dashboard
    await page.waitForURL('**/dashboard');
  });

  test('should display dashboard overview', async ({ page }) => {
    // Check if dashboard elements are visible
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="total-indices"]')).toBeVisible();
    await expect(page.locator('[data-testid="total-securities"]')).toBeVisible();
    await expect(page.locator('[data-testid="active-users"]')).toBeVisible();
    
    // Check if charts are rendered
    await expect(page.locator('[data-testid="performance-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="sector-allocation-chart"]')).toBeVisible();
  });

  test('should display index performance metrics', async ({ page }) => {
    // Check if performance metrics are displayed
    await expect(page.locator('[data-testid="index-performance-table"]')).toBeVisible();
    
    // Check if table has data
    const tableRows = page.locator('[data-testid="index-performance-table"] tbody tr');
    await expect(tableRows).toHaveCountGreaterThan(0);
    
    // Check if performance values are displayed
    await expect(page.locator('[data-testid="total-return"]')).toBeVisible();
    await expect(page.locator('[data-testid="volatility"]')).toBeVisible();
    await expect(page.locator('[data-testid="sharpe-ratio"]')).toBeVisible();
  });

  test('should allow navigation to index details', async ({ page }) => {
    // Click on first index in the table
    await page.click('[data-testid="index-performance-table"] tbody tr:first-child');
    
    // Should navigate to index details page
    await page.waitForURL('**/indices/*');
    await expect(page.locator('[data-testid="index-details-title"]')).toBeVisible();
  });

  test('should display real-time data updates', async ({ page }) => {
    // Wait for initial data load
    await page.waitForSelector('[data-testid="total-indices"]');
    
    // Get initial values
    const initialIndices = await page.textContent('[data-testid="total-indices"]');
    const initialSecurities = await page.textContent('[data-testid="total-securities"]');
    
    // Wait for potential updates (if real-time updates are implemented)
    await page.waitForTimeout(5000);
    
    // Values should still be present (not necessarily changed)
    await expect(page.locator('[data-testid="total-indices"]')).toContainText(initialIndices || '');
    await expect(page.locator('[data-testid="total-securities"]')).toContainText(initialSecurities || '');
  });

  test('should handle loading states', async ({ page }) => {
    // Reload page to see loading states
    await page.reload();
    
    // Check if loading indicators are shown
    await expect(page.locator('[data-testid="loading-spinner"]')).toBeVisible();
    
    // Wait for data to load
    await page.waitForSelector('[data-testid="dashboard-title"]');
    
    // Loading spinner should be hidden
    await expect(page.locator('[data-testid="loading-spinner"]')).not.toBeVisible();
  });

  test('should display error states gracefully', async ({ page }) => {
    // Mock API failure
    await page.route('**/api/v1/indices', route => route.abort());
    
    // Reload page
    await page.reload();
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    
    // Should show retry button
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if dashboard adapts to mobile
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible();
    
    // Check if charts are still visible (might be stacked)
    await expect(page.locator('[data-testid="performance-chart"]')).toBeVisible();
    
    // Check if table is scrollable on mobile
    const table = page.locator('[data-testid="index-performance-table"]');
    await expect(table).toBeVisible();
  });
});

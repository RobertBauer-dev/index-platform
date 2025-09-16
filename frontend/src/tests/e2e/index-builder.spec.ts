/**
 * E2E tests for Index Builder functionality
 */
import { test, expect } from '@playwright/test';

test.describe('Index Builder', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application and login
    await page.goto('http://localhost:3000');
    await page.fill('[data-testid="username-input"]', 'admin');
    await page.fill('[data-testid="password-input"]', 'admin123');
    await page.click('[data-testid="login-button"]');
    
    // Navigate to Index Builder
    await page.click('[data-testid="index-builder-nav"]');
    await page.waitForURL('**/builder');
  });

  test('should display index builder form', async ({ page }) => {
    // Check if form elements are visible
    await expect(page.locator('[data-testid="index-builder-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="index-name-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="index-description-input"]')).toBeVisible();
    await expect(page.locator('[data-testid="weighting-method-select"]')).toBeVisible();
    await expect(page.locator('[data-testid="rebalance-frequency-select"]')).toBeVisible();
  });

  test('should allow basic index configuration', async ({ page }) => {
    // Fill basic information
    await page.fill('[data-testid="index-name-input"]', 'Test Index');
    await page.fill('[data-testid="index-description-input"]', 'A test index for E2E testing');
    
    // Select weighting method
    await page.selectOption('[data-testid="weighting-method-select"]', 'equal_weight');
    
    // Select rebalance frequency
    await page.selectOption('[data-testid="rebalance-frequency-select"]', 'monthly');
    
    // Verify values are set
    await expect(page.locator('[data-testid="index-name-input"]')).toHaveValue('Test Index');
    await expect(page.locator('[data-testid="weighting-method-select"]')).toHaveValue('equal_weight');
  });

  test('should allow sector and country selection', async ({ page }) => {
    // Navigate to filters step
    await page.click('[data-testid="next-step-button"]');
    
    // Check if filter options are visible
    await expect(page.locator('[data-testid="sector-filters"]')).toBeVisible();
    await expect(page.locator('[data-testid="country-filters"]')).toBeVisible();
    
    // Select sectors
    await page.check('[data-testid="sector-technology"]');
    await page.check('[data-testid="sector-healthcare"]');
    
    // Select countries
    await page.check('[data-testid="country-usa"]');
    await page.check('[data-testid="country-germany"]');
    
    // Verify selections
    await expect(page.locator('[data-testid="sector-technology"]')).toBeChecked();
    await expect(page.locator('[data-testid="country-usa"]')).toBeChecked();
  });

  test('should allow market cap range configuration', async ({ page }) => {
    // Navigate to filters step
    await page.click('[data-testid="next-step-button"]');
    
    // Set market cap range
    await page.fill('[data-testid="min-market-cap-input"]', '1000000000');
    await page.fill('[data-testid="max-market-cap-input"]', '1000000000000');
    
    // Set max constituents
    await page.fill('[data-testid="max-constituents-input"]', '50');
    
    // Verify values
    await expect(page.locator('[data-testid="min-market-cap-input"]')).toHaveValue('1000000000');
    await expect(page.locator('[data-testid="max-constituents-input"]')).toHaveValue('50');
  });

  test('should allow ESG criteria configuration', async ({ page }) => {
    // Navigate to filters step
    await page.click('[data-testid="next-step-button"]');
    
    // Enable ESG filtering
    await page.check('[data-testid="enable-esg-filter"]');
    
    // Set minimum ESG score
    await page.fill('[data-testid="min-esg-score-input"]', '7.0');
    
    // Verify ESG filter is enabled
    await expect(page.locator('[data-testid="enable-esg-filter"]')).toBeChecked();
    await expect(page.locator('[data-testid="min-esg-score-input"]')).toHaveValue('7.0');
  });

  test('should allow time range selection for backtesting', async ({ page }) => {
    // Navigate to time range step
    await page.click('[data-testid="next-step-button"]');
    await page.click('[data-testid="next-step-button"]');
    
    // Set backtest time range
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-12-31');
    
    // Verify dates
    await expect(page.locator('[data-testid="start-date-input"]')).toHaveValue('2024-01-01');
    await expect(page.locator('[data-testid="end-date-input"]')).toHaveValue('2024-12-31');
  });

  test('should run backtest and display results', async ({ page }) => {
    // Complete index configuration
    await page.fill('[data-testid="index-name-input"]', 'Backtest Index');
    await page.selectOption('[data-testid="weighting-method-select"]', 'market_cap_weight');
    
    // Navigate through steps
    await page.click('[data-testid="next-step-button"]');
    await page.check('[data-testid="sector-technology"]');
    await page.click('[data-testid="next-step-button"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-01-31');
    
    // Run backtest
    await page.click('[data-testid="run-backtest-button"]');
    
    // Wait for backtest to complete
    await page.waitForSelector('[data-testid="backtest-results"]', { timeout: 30000 });
    
    // Check if results are displayed
    await expect(page.locator('[data-testid="backtest-results"]')).toBeVisible();
    await expect(page.locator('[data-testid="performance-chart"]')).toBeVisible();
    await expect(page.locator('[data-testid="performance-metrics"]')).toBeVisible();
  });

  test('should display performance metrics', async ({ page }) => {
    // Complete configuration and run backtest
    await page.fill('[data-testid="index-name-input"]', 'Metrics Test Index');
    await page.selectOption('[data-testid="weighting-method-select"]', 'equal_weight');
    
    await page.click('[data-testid="next-step-button"]');
    await page.check('[data-testid="sector-technology"]');
    await page.click('[data-testid="next-step-button"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-01-31');
    
    await page.click('[data-testid="run-backtest-button"]');
    await page.waitForSelector('[data-testid="backtest-results"]', { timeout: 30000 });
    
    // Check performance metrics
    await expect(page.locator('[data-testid="total-return"]')).toBeVisible();
    await expect(page.locator('[data-testid="volatility"]')).toBeVisible();
    await expect(page.locator('[data-testid="sharpe-ratio"]')).toBeVisible();
    await expect(page.locator('[data-testid="max-drawdown"]')).toBeVisible();
  });

  test('should allow saving custom index', async ({ page }) => {
    // Complete index configuration
    await page.fill('[data-testid="index-name-input"]', 'Custom Test Index');
    await page.fill('[data-testid="index-description-input"]', 'A custom index for testing');
    await page.selectOption('[data-testid="weighting-method-select"]', 'equal_weight');
    
    await page.click('[data-testid="next-step-button"]');
    await page.check('[data-testid="sector-technology"]');
    await page.click('[data-testid="next-step-button"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-01-31');
    
    await page.click('[data-testid="run-backtest-button"]');
    await page.waitForSelector('[data-testid="backtest-results"]', { timeout: 30000 });
    
    // Save the index
    await page.click('[data-testid="save-index-button"]');
    
    // Should show success message
    await expect(page.locator('[data-testid="save-success-message"]')).toBeVisible();
    
    // Should navigate to saved index or show confirmation
    await expect(page.locator('[data-testid="index-saved-confirmation"]')).toBeVisible();
  });

  test('should allow exporting results', async ({ page }) => {
    // Complete configuration and run backtest
    await page.fill('[data-testid="index-name-input"]', 'Export Test Index');
    await page.selectOption('[data-testid="weighting-method-select"]', 'market_cap_weight');
    
    await page.click('[data-testid="next-step-button"]');
    await page.check('[data-testid="sector-technology"]');
    await page.click('[data-testid="next-step-button"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-01-31');
    
    await page.click('[data-testid="run-backtest-button"]');
    await page.waitForSelector('[data-testid="backtest-results"]', { timeout: 30000 });
    
    // Test CSV export
    const [download] = await Promise.all([
      page.waitForEvent('download'),
      page.click('[data-testid="export-csv-button"]')
    ]);
    
    expect(download.suggestedFilename()).toContain('.csv');
    
    // Test Excel export
    const [excelDownload] = await Promise.all([
      page.waitForEvent('download'),
      page.click('[data-testid="export-excel-button"]')
    ]);
    
    expect(excelDownload.suggestedFilename()).toContain('.xlsx');
  });

  test('should handle validation errors', async ({ page }) => {
    // Try to proceed without filling required fields
    await page.click('[data-testid="next-step-button"]');
    
    // Should show validation errors
    await expect(page.locator('[data-testid="validation-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="index-name-error"]')).toBeVisible();
  });

  test('should allow step navigation', async ({ page }) => {
    // Fill basic information
    await page.fill('[data-testid="index-name-input"]', 'Navigation Test Index');
    await page.selectOption('[data-testid="weighting-method-select"]', 'equal_weight');
    
    // Go to next step
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="filters-step"]')).toBeVisible();
    
    // Go back to previous step
    await page.click('[data-testid="previous-step-button"]');
    await expect(page.locator('[data-testid="basic-info-step"]')).toBeVisible();
    
    // Go forward again
    await page.click('[data-testid="next-step-button"]');
    await expect(page.locator('[data-testid="filters-step"]')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page }) => {
    // Mock API failure for backtest
    await page.route('**/api/v1/indices/*/backtest', route => route.abort());
    
    // Complete configuration
    await page.fill('[data-testid="index-name-input"]', 'Error Test Index');
    await page.selectOption('[data-testid="weighting-method-select"]', 'equal_weight');
    
    await page.click('[data-testid="next-step-button"]');
    await page.check('[data-testid="sector-technology"]');
    await page.click('[data-testid="next-step-button"]');
    await page.fill('[data-testid="start-date-input"]', '2024-01-01');
    await page.fill('[data-testid="end-date-input"]', '2024-01-31');
    
    // Try to run backtest
    await page.click('[data-testid="run-backtest-button"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="backtest-error"]')).toBeVisible();
    await expect(page.locator('[data-testid="retry-button"]')).toBeVisible();
  });

  test('should be responsive on mobile devices', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check if form adapts to mobile
    await expect(page.locator('[data-testid="index-builder-title"]')).toBeVisible();
    await expect(page.locator('[data-testid="index-name-input"]')).toBeVisible();
    
    // Check if step navigation works on mobile
    await page.fill('[data-testid="index-name-input"]', 'Mobile Test Index');
    await page.click('[data-testid="next-step-button"]');
    
    await expect(page.locator('[data-testid="filters-step"]')).toBeVisible();
  });
});

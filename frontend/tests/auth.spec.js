const { test, expect } = require('@playwright/test');

test.describe('Authentication Flow', () => {
  
  test('should display login page', async ({ page }) => {
    await page.goto('/login');
    await expect(page.locator('h1')).toContainText('CIROP Login');
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'wrong@test.com');
    await page.fill('input[type="password"]', 'wrongpass');
    await page.click('button[type="submit"]');
    await expect(page.locator('text=Invalid credentials')).toBeVisible({ timeout: 5000 });
  });

  test('should login successfully', async ({ page }) => {
    await page.goto('/login');
    await page.fill('input[type="email"]', 'test@cirop.com');
    await page.fill('input[type="password"]', 'Test@123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/dashboard/);
  });
});
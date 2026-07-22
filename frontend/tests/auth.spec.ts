import { test, expect } from '@playwright/test';

test.describe('MDRP End-to-End Tests', () => {
  test('should display login page if unauthenticated', async ({ page }) => {
    // Navigate to a protected route
    await page.goto('/dashboard');
    
    // Clerk usually redirects to its login/sign-in component
    // If not configured with full SSR redirect, the page should show some sign-in elements
    // The exact behavior depends on the clerk config. Let's just check the URL or a known text.
    // If we're redirected to Clerk's hosted UI or a custom sign in page:
    await expect(page).toHaveURL(/.*sign-in|.*login/i);
  });

  test('should load the home page successfully', async ({ page }) => {
    await page.goto('/');
    
    // Check if the title is present
    await expect(page).toHaveTitle(/MDRP|Multi Disease/i);
    
    // There should be a link to login or dashboard
    const actionButton = page.locator('a', { hasText: /Dashboard|Sign In|Get Started/i }).first();
    await expect(actionButton).toBeVisible();
  });
});

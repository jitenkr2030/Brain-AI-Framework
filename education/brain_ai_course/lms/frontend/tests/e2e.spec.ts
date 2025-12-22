import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/LMS|Learning/);
  });

  test('should display hero section', async ({ page }) => {
    await expect(page.locator('h1')).toBeVisible();
  });

  test('should navigate to courses catalog', async ({ page }) => {
    await page.click('text=Browse Courses');
    await expect(page).toHaveURL(/.*courses/);
  });

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=Sign In');
    await expect(page).toHaveURL(/.*auth\/login/);
  });
});

test.describe('Authentication', () => {
  test('should display login form', async ({ page }) => {
    await page.goto('/auth/login');
    await expect(page.locator('text=Welcome Back')).toBeVisible();
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
  });

  test('should display register form', async ({ page }) => {
    await page.goto('/auth/register');
    await expect(page.locator('text=Create Account')).toBeVisible();
  });

  test('should navigate to register from login', async ({ page }) => {
    await page.goto('/auth/login');
    await page.click('text=Sign up');
    await expect(page).toHaveURL(/.*auth\/register/);
  });
});

test.describe('Dashboard', () => {
  test('should require authentication', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL(/.*auth\/login/);
  });
});

test.describe('Course Catalog', () => {
  test('should display course cards', async ({ page }) => {
    await page.goto('/courses/catalog');
    await expect(page.locator('text=Course Catalog')).toBeVisible();
  });
});

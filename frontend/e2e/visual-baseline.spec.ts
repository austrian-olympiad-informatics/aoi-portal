import { test, expect, Page } from "@playwright/test";

// Wait for Vue app to be mounted and any initial loading to finish
async function waitForApp(page: Page) {
  await page.waitForLoadState("networkidle");
  // Give Vue a moment to render
  await page.waitForTimeout(500);
}

test.describe("Visual Baseline — Public Pages", () => {
  test("home page", async ({ page }) => {
    await page.goto("/");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("home.png", { fullPage: true });
  });

  test("login page", async ({ page }) => {
    await page.goto("/auth/login");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("login.png", { fullPage: true });
  });

  test("register page", async ({ page }) => {
    await page.goto("/auth/register");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("register.png", { fullPage: true });
  });

  test("password reset page", async ({ page }) => {
    await page.goto("/auth/password-reset");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("password-reset.png", {
      fullPage: true,
    });
  });

  test("newsletter signup page", async ({ page }) => {
    await page.goto("/newsletter/sign-up");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("newsletter-signup.png", {
      fullPage: true,
    });
  });
});

test.describe("Visual Baseline — Authenticated Pages", () => {
  test.beforeEach(async ({ page }) => {
    // Log in
    await page.goto("/auth/login");
    await waitForApp(page);
    await page.fill('input[type="email"]', "t.rainer@example.org");
    await page.fill('input[type="password"]', "password1");
    await page.click('button[type="submit"]');
    await page.waitForURL((url) => !url.pathname.includes("/auth/login"));
    await waitForApp(page);
  });

  test("profile page", async ({ page }) => {
    await page.goto("/profile");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("profile.png", { fullPage: true });
  });

  test("admin dashboard", async ({ page }) => {
    await page.goto("/admin");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("admin-dashboard.png", {
      fullPage: true,
    });
  });

  test("admin users list", async ({ page }) => {
    await page.goto("/admin/users");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("admin-users.png", {
      fullPage: true,
    });
  });

  test("admin contests list", async ({ page }) => {
    await page.goto("/admin/contests");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("admin-contests.png", {
      fullPage: true,
    });
  });

  test("admin groups list", async ({ page }) => {
    await page.goto("/admin/groups");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("admin-groups.png", {
      fullPage: true,
    });
  });

  test("admin user mail", async ({ page }) => {
    await page.goto("/admin/user-mail");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("admin-user-mail.png", {
      fullPage: true,
    });
  });

  test("admin newsletter", async ({ page }) => {
    await page.goto("/admin/newsletter");
    await waitForApp(page);
    await expect(page).toHaveScreenshot("admin-newsletter.png", {
      fullPage: true,
    });
  });
});

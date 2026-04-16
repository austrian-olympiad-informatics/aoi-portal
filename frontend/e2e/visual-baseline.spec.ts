import { test, expect, Page, APIRequestContext } from "@playwright/test";

const CONTEST_UUID = "ffe0fcce-3b1e-44a5-870b-4e10dff2bbff";
const CONTEST_CMS_NAME = "dev";
const TASK_NAME = "HELLO";

const EMAIL = "t.rainer@example.org";
const PASSWORD = "password1";

const HELLO_WORLD_CPP = [
  "#include <iostream>",
  "int main() {",
  '    std::cout << "Hello, world." << std::endl;',
  "    return 0;",
  "}",
].join("\n");

// Wait for Vue app to be mounted and any initial loading to finish
async function waitForApp(page: Page) {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
}

async function getAuthToken(request: APIRequestContext): Promise<string> {
  const resp = await request.post("/api/auth/login", {
    data: { email: EMAIL, password: PASSWORD },
  });
  const body = await resp.json();
  return body.token;
}

async function login(page: Page) {
  await page.goto("/auth/login");
  await waitForApp(page);
  await page.fill('input[type="email"]', EMAIL);
  await page.fill('input[type="password"]', PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL((url) => !url.pathname.includes("/auth/login"));
  await waitForApp(page);
}

// Ensure the user has joined the dev contest (via API, idempotent)
async function ensureJoined(request: APIRequestContext, token: string) {
  const resp = await request.get(`/api/contests/${CONTEST_UUID}`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  const contest = await resp.json();
  if (!contest.joined) {
    await request.post(`/api/contests/${CONTEST_UUID}/join`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  }
}

// Clear any previously saved code from localStorage for the task
async function clearTaskLocalStorage(page: Page) {
  await page.evaluate((taskName) => {
    for (const key of Object.keys(localStorage)) {
      if (key.includes(taskName)) {
        localStorage.removeItem(key);
      }
    }
  }, TASK_NAME);
}

// Paste code into the CodeMirror editor (avoids auto-bracket-close issues)
async function pasteIntoCodeMirror(page: Page, code: string) {
  const cmEditor = page.locator(".cm-editor .cm-content");
  await expect(cmEditor).toBeVisible();
  await cmEditor.click();
  await page.keyboard.press("Control+a");
  await page.evaluate(
    (text) => navigator.clipboard.writeText(text),
    code,
  );
  await page.keyboard.press("Control+v");
  await page.waitForTimeout(300);
}

// ─── Visual Baselines (static pages) ────────────────────────────

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
    await login(page);
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

// ─── Contest Flow: Join → View Task → Submit → Score ────────────
// These tests verify functionality, not pixel-perfect visuals.
// Screenshots use maxDiffPixelRatio because scores/timestamps/submission
// counts depend on prior DB state which may be reset at any time.

const DYNAMIC_SCREENSHOT_OPTS = { maxDiffPixelRatio: 0.05 };

test.describe("Contest Flow", () => {
  test.describe.configure({ mode: "serial" });

  test("join the development contest", async ({ page }) => {
    await login(page);
    await page.goto(`/contests/${CONTEST_UUID}`);
    await waitForApp(page);

    // Check if already joined
    const alreadyJoined = await page
      .locator('a:has-text("Zum Bewerb")')
      .isVisible();

    if (!alreadyJoined) {
      // Should see the join button
      const joinButton = page.locator('button[type="submit"]');
      await expect(joinButton).toBeVisible();

      // Click join and wait for API
      const joinResponsePromise = page.waitForResponse(
        (resp) => resp.url().includes("/join"),
        { timeout: 15000 },
      );
      await joinButton.click();
      await joinResponsePromise;
      await waitForApp(page);
    }

    // Should now see "Zum Bewerb" link
    const goToContestButton = page.locator('a:has-text("Zum Bewerb")');
    await expect(goToContestButton).toBeVisible({ timeout: 10000 });
    await expect(page).toHaveScreenshot("contest-joined.png", {
      fullPage: true,
    });
  });

  test("view CMS contest overview with tasks", async ({ page }) => {
    await login(page);
    await page.goto(`/cms/contest/${CONTEST_CMS_NAME}`);
    await waitForApp(page);

    // Verify key UI elements are present
    await expect(page.locator("text=Development Contest")).toBeVisible();
    await expect(page.locator("text=HELLO")).toBeVisible();
    await expect(page.locator("text=COMM")).toBeVisible();
    await expect(page.locator("text=Deine Punktzahl")).toBeVisible();
    await expect(page.locator("text=Aufgaben")).toBeVisible();
    await expect(page).toHaveScreenshot(
      "cms-contest-overview.png",
      { fullPage: true, ...DYNAMIC_SCREENSHOT_OPTS },
    );
  });

  test("view the Hello World task", async ({ page }) => {
    await login(page);
    await clearTaskLocalStorage(page);
    await page.goto(
      `/cms/contest/${CONTEST_CMS_NAME}/task/${TASK_NAME}`,
    );
    await waitForApp(page);

    // Verify the task page structure
    await expect(page.locator("h1:has-text('HELLO')")).toBeVisible();
    await expect(page.locator("text=Hello, world")).toBeVisible();
    await expect(page.locator(".cm-editor")).toBeVisible();
    await expect(
      page.locator('button:has-text("Abschicken")'),
    ).toBeVisible();
    await expect(page.locator("text=Deine Punktzahl")).toBeVisible();
    await expect(page.locator("text=Deine Einsendungen")).toBeVisible();
    await expect(page.locator("text=Zeitlimit")).toBeVisible();

    await expect(page).toHaveScreenshot(
      "task-hello-world.png",
      DYNAMIC_SCREENSHOT_OPTS,
    );
  });

  test("submit a correct C++ solution and receive 100/100", async ({
    page,
  }) => {
    await login(page);
    await clearTaskLocalStorage(page);
    await page.goto(
      `/cms/contest/${CONTEST_CMS_NAME}/task/${TASK_NAME}`,
    );
    await waitForApp(page);

    // Count existing submission rows before submitting
    const rowsBefore = await page.locator("table tbody tr").count();

    // Paste the hello world solution into CodeMirror
    await pasteIntoCodeMirror(page, HELLO_WORLD_CPP);

    // Verify the code is in the editor
    await expect(page.locator(".cm-editor")).toContainText("#include");
    await expect(page.locator(".cm-editor")).toContainText("Hello, world.");

    // Click Submit ("Abschicken") and wait for the API response
    const submitPromise = page.waitForResponse(
      (resp) => resp.url().includes("/submit") && resp.status() === 200,
      { timeout: 15000 },
    );
    await page.locator('button:has-text("Abschicken")').click();
    await submitPromise;

    // Wait for our new submission to appear in the list
    await expect(page.locator("table tbody tr")).toHaveCount(rowsBefore + 1, {
      timeout: 15000,
    });

    // Wait for the newest submission (first row) to finish evaluating.
    // Only check this row — old stuck submissions from past runs are ignored.
    const newestRow = page.locator("table tbody tr").first();
    await expect(newestRow.locator(".sub-loading")).toHaveCount(0, {
      timeout: 90000,
    });

    // Verify the overall task score is 100 / 100
    const overallScore = page.locator(".progress-value").first();
    await expect(overallScore).toHaveText("100 / 100", { timeout: 10000 });

    // A success modal with confetti may appear — close it
    const modalBg = page.locator(".modal-background");
    if (
      await modalBg.first().isVisible().catch(() => false)
    ) {
      await modalBg.first().click();
      await page.waitForTimeout(500);
    }

    await expect(page).toHaveScreenshot(
      "task-scored-100.png",
      DYNAMIC_SCREENSHOT_OPTS,
    );
  });
});

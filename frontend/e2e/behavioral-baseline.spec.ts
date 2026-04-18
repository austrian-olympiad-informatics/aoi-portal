/**
 * Behavioral Baseline Tests — Phase 0
 *
 * These tests are written BEFORE the Class → Composition API migration and
 * capture the expected behavior of the most migration-sensitive patterns:
 *
 *   Group 1: @VModel round-trip binding (RegisterInput, LoginInput, NumberInput)
 *   Group 2: @Watch watcher reactivity (CodeMirror lang switch, RichTextEditor typing)
 *   Group 3: Timer lifecycle — no JS errors on unmount (CheckNotifications, ContestStartStop)
 *   Group 4: ContestStartStop renders non-empty contest status text
 *
 * Run with --update-snapshots once to capture baseline screenshots, then run
 * normally on every subsequent change.
 */

import { test, expect, Page } from "@playwright/test";

const CONTEST_CMS_NAME = "dev";
const TASK_NAME = "HELLO";

const EMAIL = "t.rainer@example.org";
const PASSWORD = "password1";

async function waitForApp(page: Page) {
  await page.waitForLoadState("networkidle");
  await page.waitForTimeout(500);
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

// ─── Group 1: @VModel Round-Trip Binding ────────────────────────────────────

test.describe("Behavioral Baseline — @VModel Round-Trip Binding", () => {
  test("register form: typed values are retained across all fields", async ({
    page,
  }) => {
    await page.goto("/auth/register");
    await waitForApp(page);

    const firstNameInput = page.locator('input[placeholder="Dein Vorname"]');
    const lastNameInput = page.locator('input[placeholder="Dein Nachname"]');
    const emailInput = page.locator(
      'input[placeholder="Deine E-Mail-Adresse"]',
    );
    const passwordInput = page.locator('input[type="password"]');

    await firstNameInput.fill("Alice");
    await lastNameInput.fill("Smith");
    await emailInput.fill("alice@example.com");
    await passwordInput.fill("securepassword1");

    // Press Tab to trigger any onBlur/reactive updates
    await passwordInput.press("Tab");
    await page.waitForTimeout(200);

    // All values must still be set — verifies @VModel binding is live
    await expect(firstNameInput).toHaveValue("Alice");
    await expect(lastNameInput).toHaveValue("Smith");
    await expect(emailInput).toHaveValue("alice@example.com");
    await expect(passwordInput).toHaveValue("securepassword1");

    await expect(page).toHaveScreenshot("vmodel-register.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });

  test("login form: clearing and retyping email retains the new value", async ({
    page,
  }) => {
    await page.goto("/auth/login");
    await waitForApp(page);

    const emailInput = page.locator('input[type="email"]');
    const passwordInput = page.locator('input[type="password"]');

    await emailInput.fill("first@example.com");
    await passwordInput.fill("somepassword");

    // Clear and retype — tests that the reactive binding is two-way
    await emailInput.clear();
    await emailInput.fill("updated@example.com");
    await passwordInput.press("Tab");
    await page.waitForTimeout(200);

    await expect(emailInput).toHaveValue("updated@example.com");
    await expect(passwordInput).toHaveValue("somepassword");

    await expect(page).toHaveScreenshot("vmodel-login.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });

  test("NumberInput: typing updates the value and re-typing changes it", async ({
    page,
  }) => {
    await login(page);

    // UserCreateView renders UserForm which contains NumberInput for CMS ID
    await page.goto("/admin/users/create");
    await waitForApp(page);

    // NumberInput renders a b-input with inputmode="numeric" — this attribute
    // is unique to NumberInput, so we can use it directly as the selector.
    const cmsIdInput = page.locator('input[inputmode="numeric"]');
    await expect(cmsIdInput).toBeVisible();

    // Type a number and verify it's reflected in the input value
    await cmsIdInput.fill("42");
    await cmsIdInput.press("Tab");
    await page.waitForTimeout(200);
    await expect(cmsIdInput).toHaveValue("42");

    // Change to a different number — verifies watch(modelValue) fires on re-render
    await cmsIdInput.fill("99");
    await cmsIdInput.press("Tab");
    await page.waitForTimeout(200);
    await expect(cmsIdInput).toHaveValue("99");

    await expect(page).toHaveScreenshot("vmodel-numberinput.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });
});

// ─── Group 2: @Watch Watcher Reactivity ─────────────────────────────────────

test.describe("Behavioral Baseline — @Watch Watcher Reactivity", () => {
  test("CodeMirror: switching language keeps the editor visible and non-empty", async ({
    page,
  }) => {
    await login(page);

    await page.goto(`/cms/contest/${CONTEST_CMS_NAME}/task/${TASK_NAME}`);
    await waitForApp(page);

    await expect(page.locator(".cm-editor")).toBeVisible({ timeout: 10000 });

    const langSelect = page.locator(".code-bar-lang select");
    await expect(langSelect).toBeVisible();

    const options = await langSelect.locator("option").all();
    if (options.length > 1) {
      // Switch to the second available language
      const secondValue = await options[1].getAttribute("value");
      await langSelect.selectOption(secondValue!);
      await page.waitForTimeout(500);

      // The @Watch("lang") watchLang() calls resetState() — the editor must
      // survive the state reset and still be visible with a cm-content element
      await expect(page.locator(".cm-editor")).toBeVisible();
      await expect(page.locator(".cm-editor .cm-content")).toBeVisible();
    }

    await expect(page).toHaveScreenshot("watch-codemirror-lang.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });

  test("RichTextEditor: typed text appears in the editor", async ({ page }) => {
    await login(page);

    await page.goto("/admin/user-mail");
    await waitForApp(page);

    // TipTap renders a contenteditable .ProseMirror div
    const editor = page.locator(".ProseMirror").first();
    await expect(editor).toBeVisible({ timeout: 10000 });

    await editor.click();
    await page.keyboard.type("Hello migration test");
    await page.waitForTimeout(300);

    // Typed text must appear — verifies @Watch("modelValue") and TipTap binding
    await expect(editor).toContainText("Hello migration test");

    await expect(page).toHaveScreenshot("watch-richtexteditor.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });
});

// ─── Group 3: Timer Lifecycle ────────────────────────────────────────────────

test.describe("Behavioral Baseline — Timer Lifecycle", () => {
  test("no JS errors after navigating away from CMS contest page", async ({
    page,
  }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });

    await login(page);

    // Set up the response waiter BEFORE navigating — the notification check fires
    // immediately on mount (in mounted()), so waitForResponse must be registered
    // before goto() or the response will have already passed.
    const firstNotificationResponse = page.waitForResponse(
      (resp) => resp.url().includes("check-notifications"),
      { timeout: 10000 },
    );

    // Navigate to CMS contest — mounts CheckNotifications (setInterval, 15s)
    // and ContestStartStop (setInterval, 1s)
    await page.goto(`/cms/contest/${CONTEST_CMS_NAME}`);
    await waitForApp(page);
    await firstNotificationResponse;

    // Navigate away — triggers unmounted() cleanup for both interval-using components
    await page.goto("/");
    await waitForApp(page);

    // Wait for any stale timers to fire (they would throw if cleanup was dropped)
    await page.waitForTimeout(2000);

    // Must be zero — any errors here mean an unmounted() hook was lost in migration
    expect(errors, "JS errors after navigation away from CMS page").toEqual([]);
  });

  test("CheckNotifications: at least one polling request fires on mount", async ({
    page,
  }) => {
    await login(page);

    const checkNotifUrls: string[] = [];
    page.on("request", (req) => {
      if (req.url().includes("check-notifications")) {
        checkNotifUrls.push(req.url());
      }
    });

    await page.goto(`/cms/contest/${CONTEST_CMS_NAME}`);
    await waitForApp(page);

    // The mounted() hook calls checkNotifications immediately — we must see it
    await expect
      .poll(() => checkNotifUrls.length, {
        timeout: 10000,
        message: "Expected at least one check-notifications request on mount",
      })
      .toBeGreaterThanOrEqual(1);

    await expect(page).toHaveScreenshot("timer-cms-contest.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });
});

// ─── Group 4: ContestStartStop Renders Status Text ──────────────────────────

test.describe("Behavioral Baseline — ContestStartStop", () => {
  test("contest status text is rendered and non-empty", async ({ page }) => {
    await login(page);

    await page.goto(`/cms/contest/${CONTEST_CMS_NAME}`);
    await waitForApp(page);

    // ContestStartStop renders inside the first .block inside .section.
    // It always renders at least one <template> branch with text about the
    // contest timing. Accept any text mentioning German contest time keywords.
    const statusBlock = page
      .locator(".section .block")
      .first();
    await expect(statusBlock).toBeVisible({ timeout: 10000 });

    const statusText = await statusBlock.innerText();
    expect(statusText.trim().length, "ContestStartStop rendered empty block").toBeGreaterThan(0);

    await expect(page).toHaveScreenshot("conteststartstop-status.png", {
      fullPage: true,
      maxDiffPixelRatio: 0.05,
    });
  });
});

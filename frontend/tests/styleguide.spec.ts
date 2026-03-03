import { test, expect } from '@playwright/test';

// E2E tests validating Styleguide rendering and theme toggle (guidelines-compliant)

test.describe('Styleguide - Design Tokens', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/styleguide');
  });

  test('shows key sections', async ({ page }) => {
    await test.step('Verify headings present with correct text', async () => {
      await expect(page.getByRole('heading', { name: 'Design Tokens' })).toHaveText('Design Tokens');
      await expect(page.getByRole('heading', { name: 'Color Palette' })).toHaveText('Color Palette');
      await expect(page.getByRole('heading', { name: 'Typography' })).toHaveText('Typography');
      await expect(page.getByRole('heading', { name: 'Border Radius' })).toHaveText('Border Radius');
      await expect(page.getByRole('heading', { name: 'Shadows' })).toHaveText('Shadows');
      await expect(page.getByRole('heading', { name: 'Component Examples' })).toHaveText('Component Examples');
    });
  });

  test('renders base color blocks from CSS variables', async ({ page }) => {
    await test.step('Check representative base colors render', async () => {
      const vars = ['--background', '--foreground', '--primary', '--secondary'];
      for (const v of vars) {
        const block = page.locator(`div[style*="var(${v})"]`).first();
        await expect(block).toHaveCount(1);
        const styleAttr = await block.getAttribute('style');
        expect(styleAttr).toContain(`var(${v})`);
      }
    });
  });

  test('renders semantic colors with foreground pairing', async ({ page }) => {
    await test.step('Check semantic background + foreground pairs exist', async () => {
      const pairs = [
        { bg: '--success', fg: '--success-foreground' },
        { bg: '--warning', fg: '--warning-foreground' },
        { bg: '--info', fg: '--info-foreground' },
      ];
      for (const { bg, fg } of pairs) {
        const block = page.locator(`div[style*="var(${bg})"][style*="var(${fg})"]`).first();
        await expect(block).toHaveCount(1);
      }
    });
  });

  test('renders chart colors', async ({ page }) => {
    await test.step('Check five chart color blocks', async () => {
      for (let i = 1; i <= 5; i++) {
        const v = `--chart-${i}`;
        const block = page.locator(`div[style*="var(${v})"]`).first();
        await expect(block).toHaveCount(1);
      }
    });
  });

  test('dark mode toggle updates html class', async ({ page }) => {
    await test.step('Toggle and assert html.dark class presence changes', async () => {
      const hasDarkBefore = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      await page.getByTestId('styleguide-theme-toggle').click();
      const hasDarkAfter = await page.evaluate(() => document.documentElement.classList.contains('dark'));
      expect(hasDarkAfter).toBe(!hasDarkBefore);
    });
  });
});

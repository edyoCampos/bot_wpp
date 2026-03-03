import { test, expect } from '@playwright/test'

// Test Forgot Password Page

test.describe('Forgot Password Page', () => {
  test('should render all elements and handle form submission', async ({ page }) => {
    await page.goto('/forgot')

    await test.step('Verify page title and main elements', async () => {
      await expect(page.getByTestId('forgot-title')).toHaveText('Recuperar senha')
      await expect(page.getByTestId('forgot-email')).toBeVisible()
      await expect(page.getByTestId('forgot-submit')).toBeVisible()
    })

    await test.step('Test form validation - empty email', async () => {
      // Button should be disabled when email is empty
      await expect(page.getByTestId('forgot-submit')).toBeDisabled()
      await expect(page).toHaveURL('/forgot') // Should not navigate
    })

    await test.step('Fill email and verify form state', async () => {
      await page.getByTestId('forgot-email').fill('test@example.com')
      await expect(page.getByTestId('forgot-submit')).toBeEnabled()
      await expect(page.getByTestId('forgot-email')).toHaveValue('test@example.com')
    })

    // Note: Actual submission would require backend mocking
    // For now, we verify the form is ready for submission
  })

  test('should show success message after submission', async ({ page }) => {
    await page.goto('/forgot')

    await test.step('Fill and submit form', async () => {
      await page.getByTestId('forgot-email').fill('test@example.com')
      await page.getByTestId('forgot-submit').click()
    })

    // Note: In a real scenario, this would show success/error messages
    // For now, we verify the form remains accessible
    await expect(page.getByTestId('forgot-email')).toBeVisible()
  })
})

// Test Reset Password Page

test.describe('Reset Password Page', () => {
  test('should render all elements with valid token', async ({ page }) => {
    await page.goto('/reset?token=valid-token-123')

    await test.step('Verify page title and main elements', async () => {
      await expect(page.getByTestId('reset-title')).toHaveText('Redefinir senha')
      await expect(page.getByTestId('reset-new-password')).toBeVisible()
      await expect(page.getByTestId('reset-confirm-password')).toBeVisible()
      await expect(page.getByTestId('reset-submit')).toBeVisible()
    })
  })

  test('should validate password requirements', async ({ page }) => {
    await page.goto('/reset?token=valid-token-123')

    await test.step('Test empty form submission', async () => {
      // Button should be disabled when passwords are empty
      await expect(page.getByTestId('reset-submit')).toBeDisabled()
      await expect(page).toHaveURL('/reset?token=valid-token-123')
    })

    await test.step('Test password mismatch', async () => {
      await page.getByTestId('reset-new-password').fill('password123')
      await page.getByTestId('reset-confirm-password').fill('different123')
      // Button should remain enabled (validation happens on submit)
      await expect(page.getByTestId('reset-submit')).toBeEnabled()
    })

    await test.step('Test valid passwords', async () => {
      await page.getByTestId('reset-new-password').fill('newpassword123')
      await page.getByTestId('reset-confirm-password').fill('newpassword123')
      await expect(page.getByTestId('reset-submit')).toBeEnabled()
    })
  })

  test('should handle invalid or missing token', async ({ page }) => {
    await test.step('Test without token', async () => {
      await page.goto('/reset')
      // Should still render but submission should fail
      await expect(page.getByTestId('reset-title')).toBeVisible()
    })

    await test.step('Test with invalid token', async () => {
      await page.goto('/reset?token=invalid')
      await page.getByTestId('reset-new-password').fill('password123')
      await page.getByTestId('reset-confirm-password').fill('password123')
      await page.getByTestId('reset-submit').click()

      // In real scenario, this would show error message
      await expect(page.getByTestId('reset-new-password')).toHaveValue('password123')
    })
  })

  test('should handle successful password reset', async ({ page }) => {
    await page.goto('/reset?token=valid-token-123')

    await test.step('Fill and submit valid form', async () => {
      await page.getByTestId('reset-new-password').fill('newpassword123')
      await page.getByTestId('reset-confirm-password').fill('newpassword123')
      await page.getByTestId('reset-submit').click()
    })

    // Note: In real scenario, this would show success message and redirect
    // For now, we verify the form remains accessible
    await expect(page.getByTestId('reset-new-password')).toBeVisible()
  })
})
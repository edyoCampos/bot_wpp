# Component Token Usage: Buttons, Cards, Inputs

## Buttons
- **Primary**: Uses `action-primary`, `action-primary-hover`, `action-primary-active`, `text-on-brand`, `radius-md`, `shadow-button-primary`
- **Secondary**: Uses `action-secondary`, `text-primary`, `radius-md`, `shadow-sm`
- **Strong**: Uses `action-strong`, `action-strong-hover`, `text-on-brand`, `radius-md`, `shadow-md`
- **States**:
  - Default: `action-primary`, `text-on-brand`
  - Hover: `action-primary-hover`
  - Active: `action-primary-active`
  - Focus: `border-focus`, `shadow-button-primary`
  - Disabled: `text-muted`, `surface-subtle`

## Cards
- **Surface**: `surface-card`, `surface-elevated`, `border-default`, `radius-lg`, `shadow-card`
- **States**:
  - Default: `surface-card`, `border-default`
  - Hover: `shadow-card-hover`
  - Focus: `border-focus`
  - Disabled: `surface-subtle`, `text-muted`

## Inputs
- **Surface**: `surface-section`, `border-default`, `radius-md`, `shadow-sm`
- **States**:
  - Default: `surface-section`, `border-default`, `text-primary`
  - Hover: `border-focus`
  - Active: `border-focus`, `shadow-md`
  - Focus: `border-focus`, `shadow-md`
  - Disabled: `surface-subtle`, `text-muted`

---

All visual properties reference semantic tokens only. No raw values are used. For any missing token, update globals.css and documentation before using a new value.

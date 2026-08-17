# 0002 Default Hotkeys

## Status

Accepted for MVP planning.

## Decision

Use configurable hotkeys with these defaults:

- `Ctrl+Shift+Space`: toggle voice input.
- `Ctrl+Shift+Enter`: voice input translated to English.
- `Ctrl+Shift+T`: translate selected text to Chinese.

## Rationale

`Alt+Space` conflicts with the Windows system menu. `Shift+Space` commonly conflicts with Chinese IME full-width and half-width toggling. `Ctrl+Shift+Space` has a lower conflict probability while remaining easy to press.

## Consequences

Hotkeys must be stored in user-editable configuration rather than hard-coded.

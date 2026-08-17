# 0007 Global Hotkey and Auto-Paste Flow

## Status

Proposed. Waiting for product confirmation before implementation.

## Goal

Allow the user to press one global shortcut in any Windows text input, speak, press the shortcut again, and have the recognized text inserted at the original cursor position.

## Proposed Architecture

Keep the Electron shell, but move it into a background-first desktop role:

- Electron main process owns the global shortcut, tray icon, foreground-window tracking, clipboard, and paste trigger.
- Python API continues to own audio capture, ASR, and text structuring.
- React renderer remains as a small settings and diagnostics window. It is not part of the hot path and does not need to stay visible.

The hot path is:

```text
global shortcut
-> remember the current foreground window
-> start Python recording
-> same shortcut
-> stop recording
-> transcribe
-> structure
-> put result in clipboard
-> activate the original foreground window
-> send Ctrl+V
-> restore the previous clipboard contents
```

## Shortcut

Use `Shift+Space` initially because it is easy to press with one hand, but make it configurable.

On Chinese Windows IMEs, `Shift+Space` may already toggle full-width and half-width input. This must be tested with the user's active IME before calling the shortcut stable. If it conflicts, use a configurable alternative such as `Ctrl+Shift+Space`.

## Why Keep the Frontend

Removing the renderer does not remove the need for a desktop process. We still need a resident process for global shortcuts and auto-paste. Keeping a small renderer provides:

- microphone selection;
- ASR provider and model status;
- shortcut configuration;
- test recording;
- logs and troubleshooting;
- manual fallback when a target application blocks simulated paste.

The main window can remain hidden until opened from the tray.

## Auto-Paste Risks

Auto-paste is not equally reliable in every target application. The implementation should:

- save the current clipboard text and supported formats;
- write the recognized result to the clipboard;
- activate the remembered foreground window;
- send `Ctrl+V`;
- restore the clipboard after a short delay;
- report a failure without losing the recognized text.

Some elevated applications, secure input fields, terminals, and remote-desktop sessions may reject simulated keyboard input. This is an environment limitation, not an ASR failure.

# 0001 Initial MVP Architecture

## Status

Accepted for MVP.

## Context

The project targets Windows first and needs global hotkeys, tray behavior, clipboard access, floating UI, local speech recognition, and local LLM processing.

## Decision

Use:

- Electron + React + TypeScript for the desktop shell.
- Python FastAPI for local AI capabilities.
- Ollama as the default local text inference backend.
- `qwen3:8b` as the default model.

## Rationale

Electron has mature Windows support for global shortcuts, clipboard access, tray integration, and floating windows. The main product risk is stable system-level interaction, not installer size.

Python is the better boundary for AI capabilities because speech recognition and audio processing libraries are stronger there. Keeping AI behind a local HTTP API also makes the desktop shell independent from model provider details.

Ollama gives a practical local inference interface and can later be swapped for any OpenAI-compatible backend without changing desktop UI flows.

## Alternatives Considered

- Tauri: smaller and more resource efficient, but higher integration risk for this Windows-first MVP.
- Single-process Node application: simpler process model, weaker speech recognition ecosystem.
- Native Windows UI: strong platform integration, slower UI iteration and narrower future portability.

## Consequences

The app will run multiple local processes during development. This is acceptable for the MVP because process boundaries make AI capabilities easier to test and replace.

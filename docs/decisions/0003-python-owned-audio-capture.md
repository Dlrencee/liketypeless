# 0003 Python-Owned Audio Capture

## Status

Accepted for MVP.

## Context

The application needs push-to-toggle voice input on Windows. Audio capture can be owned by Electron or by the Python local API.

## Decision

Use Python-owned audio capture for the MVP.

The desktop shell calls local API endpoints to start and stop recording. The Python service captures microphone audio and writes WAV files under `apps/local-api/data/recordings`.

## Rationale

The first technical goal is validating the local AI pipeline: microphone audio to speech recognition to text cleanup. Keeping capture, WAV formatting, and future Whisper integration in Python reduces format conversion work and keeps Electron focused on system interaction.

## Alternatives Considered

- Electron MediaRecorder: good for UI and browser-native permissions, but commonly emits webm/opus, which adds conversion work before Whisper.
- Native Windows audio APIs: strongest platform control, but higher implementation cost for the MVP.

## Consequences

The Python service now owns microphone device access. Electron must keep recording state synchronized through local API calls. If later waveform UI, browser-level permission behavior, or lower-latency capture becomes more important, the capture layer can move to Electron while preserving the Python transcription and LLM endpoints.

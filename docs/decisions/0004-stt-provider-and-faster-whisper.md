# 0004 STT Provider and faster-whisper

## Status

Accepted for MVP.

## Context

The application needs speech-to-text for local voice input. STT may run locally or through a cloud API in the future.

## Decision

Use a provider-shaped STT boundary and implement `local-faster-whisper` first.

Default configuration:

- Provider: `local-faster-whisper`
- Model: `base` for speed-first mode
- Language: `zh`
- Device: `cpu`
- Compute type: `int8`
- Hugging Face endpoint: `https://hf-mirror.com`

## Rationale

Local faster-whisper gives a practical balance of latency, quality, privacy, and Python integration. The `base` model is the MVP default because local tests show it is still sub-second for short utterances on CPU while being materially more accurate than `tiny`.

The provider boundary is intentionally small: audio file in, transcript out. This same contract can support cloud transcription APIs later without changing the desktop shell.

## Alternatives Considered

- `tiny`: fastest, but weaker for Chinese dictation.
- `small`: better recognition quality, but too slow for the current speed-first default.
- `medium`: better recognition quality, but heavier for a default setting.
- `large-v3`: best quality, too slow and heavy for the MVP default.
- Cloud STT: useful fallback for low-end machines, but introduces network, cost, API key, and privacy considerations.

## Consequences

First use may download a Whisper model. The app sets `HF_ENDPOINT` to a mirror by default and also supports `LIKETYPELESS_STT_MODEL_PATH` for a local model directory.

CPU int8 is the default because CUDA probing can fail at the native library level when cuDNN is not available, preventing a Python-level fallback. CUDA should be enabled only after an explicit runtime check.

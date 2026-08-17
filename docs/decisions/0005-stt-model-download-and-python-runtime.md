# 0005 STT Model Download and Python Runtime

## Status

Accepted for MVP.

## Context

Local faster-whisper requires model files before transcription can run. If the files are not already cached or configured through `LIKETYPELESS_STT_MODEL_PATH`, the first transcription call may attempt to download the model.

This is a poor first-use experience because model downloads can be slow or fail behind regional network restrictions.

## Decision

Prefer explicit model pre-download before first transcription.

For development on this machine:

- Proxy: `http://127.0.0.1:7897`
- Recommended source through proxy: `https://huggingface.co`
- Disable Hugging Face xet downloads: `HF_HUB_DISABLE_XET=1`
- Default local model directory: `D:\Models\faster-whisper-base`

Use:

```powershell
$env:HTTP_PROXY="http://127.0.0.1:7897"
$env:HTTPS_PROXY="http://127.0.0.1:7897"
$env:ALL_PROXY="http://127.0.0.1:7897"
$env:HF_ENDPOINT="https://huggingface.co"
$env:HF_HUB_DISABLE_XET="1"
python apps/local-api/scripts/download_stt_model.py --model base --endpoint https://huggingface.co --output-dir D:\Models\faster-whisper-base
$env:LIKETYPELESS_STT_MODEL_PATH="D:\Models\faster-whisper-base"
```

Use a project-local `.venv` rather than the global Anaconda environment.

Pin:

- `ctranslate2==4.6.0`
- `setuptools<81`

## Rationale

Testing showed that model downloads through the local proxy work with Hugging Face. `tiny`, `base`, and `small` were downloaded successfully.

Testing also showed that `ctranslate2==4.8.1` crashed during `WhisperModel(...)` loading on this machine without a Python exception. Downgrading to `ctranslate2==4.6.0` and keeping `setuptools<81` fixed model loading.

`onnxruntime` failed to initialize on this machine, which breaks faster-whisper VAD. The STT provider therefore retries transcription with `vad_filter=False` when VAD/onnxruntime fails.

## Consequences

The product should not silently rely on first-use model downloads. The app should eventually provide a setup/check screen that verifies:

- STT model availability.
- LLM model availability.
- Python runtime health.
- Proxy or offline model path configuration.

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import sys
from pathlib import Path
from time import perf_counter


MODEL_NAME = "iic/SenseVoiceSmall"
TAG_PATTERN = re.compile(r"<\|[^|]+?\|>")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Transcribe audio with FunASR SenseVoice.")
    parser.add_argument("audio_file", nargs="?", help="Absolute path to the WAV file.")
    parser.add_argument("--server", action="store_true", help="Run as a JSON-lines worker process.")
    return parser.parse_args()


def clean_text(text: str) -> str:
    return TAG_PATTERN.sub("", text).strip()


def create_model():
    with contextlib.redirect_stdout(sys.stderr):
        from funasr import AutoModel

        return AutoModel(model=MODEL_NAME, trust_remote_code=True, device="cpu", disable_update=True)


def transcribe(model, audio_file: Path) -> dict[str, object]:
    if not audio_file.exists():
        return {"error": f"Audio file does not exist: {audio_file}"}

    started_at = perf_counter()
    try:
        with contextlib.redirect_stdout(sys.stderr):
            result = model.generate(input=str(audio_file), language="zh", use_itn=True, batch_size_s=60)
    except Exception as exc:
        return {"error": f"SenseVoice transcription failed: {exc}"}

    text = ""
    if result and isinstance(result, list):
        first = result[0]
        if isinstance(first, dict):
            text = clean_text(str(first.get("text", "")))

    return {
        "provider": "local-sensevoice",
        "model": MODEL_NAME,
        "text": text,
        "language": "zh",
        "elapsedMs": round((perf_counter() - started_at) * 1000),
    }


def run_server() -> int:
    model = create_model()
    print(json.dumps({"status": "ready", "model": MODEL_NAME}), flush=True)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            audio_file = Path(str(request["audioFile"]))
            payload = transcribe(model, audio_file)
        except Exception as exc:
            payload = {"error": f"SenseVoice worker request failed: {exc}"}
        print(json.dumps(payload), flush=True)

    return 0


def main() -> int:
    args = parse_args()
    if args.server:
        return run_server()

    if not args.audio_file:
        print(json.dumps({"error": "audio_file is required unless --server is set"}))
        return 2

    model = create_model()
    payload = transcribe(model, Path(args.audio_file))
    print(json.dumps(payload))
    return 1 if "error" in payload else 0


if __name__ == "__main__":
    raise SystemExit(main())

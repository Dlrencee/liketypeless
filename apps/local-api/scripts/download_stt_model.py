from __future__ import annotations

import argparse
import os
from pathlib import Path


MODEL_REPOSITORIES = {
    "tiny": "Systran/faster-whisper-tiny",
    "base": "Systran/faster-whisper-base",
    "small": "Systran/faster-whisper-small",
    "medium": "Systran/faster-whisper-medium",
    "large-v3": "Systran/faster-whisper-large-v3",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download a faster-whisper model for local STT.")
    parser.add_argument("--model", default="small", help="Model alias or Hugging Face repository id.")
    parser.add_argument("--endpoint", default="https://hf-mirror.com", help="Hugging Face endpoint or mirror.")
    parser.add_argument("--cache-dir", default=None, help="Optional Hugging Face cache directory.")
    parser.add_argument("--output-dir", default=None, help="Optional local model directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    os.environ.setdefault("HF_ENDPOINT", args.endpoint)
    os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

    from huggingface_hub import snapshot_download

    repository = MODEL_REPOSITORIES.get(args.model, args.model)
    output_dir = Path(args.output_dir).resolve() if args.output_dir else None

    path = snapshot_download(
        repo_id=repository,
        cache_dir=args.cache_dir,
        local_dir=str(output_dir) if output_dir else None,
        local_dir_use_symlinks=False,
    )

    print(path)


if __name__ == "__main__":
    main()

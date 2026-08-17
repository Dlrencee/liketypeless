from __future__ import annotations

import os
from pathlib import Path

import uvicorn


def add_optional_nvidia_dll_paths(project_root: Path) -> None:
    site_packages = project_root / ".venv" / "Lib" / "site-packages"
    dll_dirs = [
        site_packages / "nvidia" / "cudnn" / "bin",
        site_packages / "nvidia" / "cublas" / "bin",
        site_packages / "nvidia" / "cuda_nvrtc" / "bin",
    ]
    existing_dirs = [str(path) for path in dll_dirs if path.exists()]
    if not existing_dirs:
        return

    os.environ["PATH"] = ";".join([*existing_dirs, os.environ.get("PATH", "")])


if __name__ == "__main__":
    api_root = Path(__file__).resolve().parents[1]
    project_root = api_root.parents[1]
    add_optional_nvidia_dll_paths(project_root)
    os.chdir(api_root)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8716, reload=True, app_dir=str(api_root))

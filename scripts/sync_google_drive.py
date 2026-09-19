"""Download the public Google Drive knowledge-base folder into the staging directory."""

from __future__ import annotations

import shutil

import gdown

from app.core.config import load_settings


def main() -> None:
    settings = load_settings()
    target = settings.documents_path
    target.mkdir(parents=True, exist_ok=True)

    for item in target.iterdir():
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    downloaded = gdown.download_folder(
        settings.google_drive_folder_url,
        output=str(target),
        quiet=False,
        use_cookies=False,
        remaining_ok=True,
    )
    if not downloaded:
        raise RuntimeError("Google Drive folder could not be downloaded")
    print(f"Synced Google Drive knowledge base to {target}")


if __name__ == "__main__":
    main()
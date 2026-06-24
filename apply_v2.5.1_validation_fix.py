from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent


def replace_exact(path: str, old: str, new: str) -> None:
    file_path = ROOT / path
    text = file_path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


def patch_check_release_readiness() -> None:
    replace_exact(
        "scripts/check_release_readiness.py",
        'EXPECTED_VERSION = "2.5.0"',
        'EXPECTED_VERSION = "2.5.1"',
    )


def patch_web_version() -> None:
    path = ROOT / "xau_lfx" / "web.py"
    text = path.read_text(encoding="utf-8")

    if "from xau_lfx import __version__" not in text:
        anchor = "from fastapi.responses import HTMLResponse\n\n"
        if anchor not in text:
            raise SystemExit("Could not locate web.py import anchor.")
        text = text.replace(anchor, anchor + "from xau_lfx import __version__\n", 1)

    text, n = re.subn(
        r'app = FastAPI\(title="XAU-LFX External Data Foundation", version="[^"]+"\)',
        'app = FastAPI(title="XAU-LFX External Data Foundation", version=__version__)',
        text,
        count=1,
    )
    if n != 1:
        raise SystemExit("Could not patch FastAPI app version in xau_lfx/web.py.")

    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_check_release_readiness()
    patch_web_version()
    print("Applied v2.5.1 validation metadata fix.")


if __name__ == "__main__":
    main()

"""Refresh this repo from the monorepo the site is deployed from.

    python scripts/sync_from_monorepo.py [path/to/mise-erp]

The live site is built and served from the mise-erp monorepo (frontend/dev,
frontend/app/dev, frontend/app/award, backend/app/api/dev_site.py). This repo
is its public, runnable mirror. The script copies the site's code across,
cuts the site's CSS out of the monorepo's globals.css, and rewrites the one
line that differs here (the page reads its files from this app's own
/api/dev-site route instead of the FastAPI backend).

It never copies: the editor password hash, the music files (they stay in
S3, see CLAUDE.md), tokens or anything under docs/secrets.
Content (photos, résumé, manifests) is refreshed separately with
scripts/pull_content.sh, because it lives in S3, not in git.
"""

from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
MONO = Path(sys.argv[1] if len(sys.argv) > 1 else HERE.parent / "try1").resolve()
FE = MONO / "frontend"


def copy(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def copytree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def main() -> None:
    if not (FE / "dev" / "DevProfile.tsx").exists():
        sys.exit(f"Not the monorepo: {MONO}")

    # The site's components, the two pages, its static files and fonts.
    copytree(FE / "dev", HERE / "dev")
    copytree(FE / "public" / "dev", HERE / "public" / "dev")
    for font in ("geist.woff2", "geist-mono.woff2", "fraunces.woff2", "fraunces-italic.woff2", "cinzel.woff2"):
        copy(FE / "app" / "fonts" / font, HERE / "app" / "fonts" / font)
    # (And the rest of the award page's folder: its own error page.)
    for f in (FE / "app" / "award").iterdir():
        if f.is_file():
            copy(f, HERE / "app" / "award" / f.name)
    # What stands in when a page fails: the profile's (at the root here), and
    # the last resort for every page.
    copy(FE / "app" / "dev" / "error.tsx", HERE / "app" / "error.tsx")
    copy(FE / "app" / "global-error.tsx", HERE / "app" / "global-error.tsx")

    # The profile page lives at / here (the monorepo serves it at /dev and
    # rewrites pandi-dev.dineai.cloud/ onto it). Its files come from this
    # app's own read-only route rather than the FastAPI backend.
    page = (FE / "app" / "dev" / "page.tsx").read_text(encoding="utf8")
    page, n = re.subn(
        r'const BACKEND = process\.env\.INTERNAL_API_URL \?\? "http://backend:8000";',
        "// Standalone mirror: the files come from app/api/dev-site (content/).\n"
        'const BACKEND = process.env.INTERNAL_API_URL ?? `http://127.0.0.1:${process.env.PORT ?? "3000"}`;',
        page,
    )
    if n != 1:
        sys.exit("app/dev/page.tsx changed shape: update the BACKEND rewrite in this script")
    (HERE / "app" / "page.tsx").write_text(page, encoding="utf8")

    # The site's CSS: the two pandi-dev blocks of the monorepo's globals.css.
    css = (FE / "app" / "globals.css").read_text(encoding="utf8").splitlines()
    start1 = next(i for i, l in enumerate(css) if l.startswith("/* ── pandi-dev.dineai.cloud"))
    end1 = next(i for i in range(start1, len(css)) if css[i].startswith("/* The chat header"))
    start2 = next(i for i, l in enumerate(css) if l.startswith("/* pandi-dev: a wrong password"))
    blocks = css[start1:end1] + [""] + css[start2:]
    head = (HERE / "scripts" / "globals.head.css").read_text(encoding="utf8")
    (HERE / "app" / "globals.css").write_text(head + "\n" + "\n".join(blocks).rstrip() + "\n", encoding="utf8")

    # Every keyframe the components name must exist in the CSS we kept.
    used: set[str] = set()
    for f in list((HERE / "dev").glob("*.ts*")) + list((HERE / "app").rglob("*.tsx")):
        used |= set(re.findall(r"\b(dev[A-Z][A-Za-z]+)\b", f.read_text(encoding="utf8")))
    defined = set(re.findall(r"@keyframes (dev[A-Za-z]+)", (HERE / "app" / "globals.css").read_text(encoding="utf8")))
    named_in_styles = {u for u in used if u not in defined and re.search(rf"animation[^;\n]*\b{u}\b", "".join(
        f.read_text(encoding="utf8") for f in (HERE / "dev").glob("*.tsx")))}
    if named_in_styles:
        sys.exit(f"Animations used but not defined: {sorted(named_in_styles)}")

    # The backend half, for reference (it runs inside the monorepo's API).
    copy(MONO / "backend" / "app" / "api" / "dev_site.py", HERE / "backend" / "dev_site.py")
    copy(MONO / "backend" / "tests" / "test_dev_site.py", HERE / "backend" / "test_dev_site.py")

    # The build and publish scripts, with the bucket left to the environment.
    for script in (MONO / "dev" / "scripts").iterdir():
        text = script.read_text(encoding="utf8")
        text = re.sub(r"s3://mise-uploads-\d+/", "s3://${DEV_SITE_BUCKET}/", text)
        text = re.sub(
            r'^BUCKET = "s3://\$\{DEV_SITE_BUCKET\}/([^"]*)"',
            lambda m: f"BUCKET = f\"s3://{{os.environ['DEV_SITE_BUCKET']}}/{m.group(1)}\"",
            text,
            flags=re.M,
        )
        if script.suffix == ".py" and "os.environ[" in text and not re.search(r"^import os\b", text, re.M):
            text = re.sub(r"^(import [a-z]+\n)", r"import os\n\1", text, count=1, flags=re.M)
        (HERE / "ops" / script.name).parent.mkdir(parents=True, exist_ok=True)
        (HERE / "ops" / script.name).write_text(text, encoding="utf8")

    # The résumé generator and its final output.
    copy(MONO / "resume" / "build_resume.py", HERE / "resume" / "build_resume.py")
    for f in (MONO / "resume" / "final").iterdir():
        copy(f, HERE / "resume" / f.name)

    # Nothing secret may leave: fail loudly rather than publish it.
    bad = re.compile(rb"(ghp_|github_pat_)[A-Za-z0-9_]{20,}|AKIA[0-9A-Z]{16}|mise-uploads-\d{6,}|\$2[aby]\$\d\d\$")
    for f in HERE.rglob("*"):
        if f.is_file() and ".git" not in f.parts and "node_modules" not in f.parts and ".next" not in f.parts:
            if f.suffix in {".webp", ".png", ".jpg", ".pdf", ".docx", ".woff2", ".glb", ".mp3", ".svg"}:
                continue
            if bad.search(f.read_bytes()):
                sys.exit(f"Refusing: something secret-looking in {f.relative_to(HERE)}")
    print(f"synced from {MONO}")


if __name__ == "__main__":
    main()

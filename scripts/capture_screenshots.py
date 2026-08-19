"""Launch the local app and capture reproducible documentation screenshots.

The command uses an existing Chrome or Edge installation through Playwright. It does
not download a browser or deploy the application. Generated images are documentation
artifacts and should be refreshed when the default overview changes materially.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Sequence
from pathlib import Path

from playwright.sync_api import sync_playwright

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = PROJECT_ROOT / "docs" / "images" / "overview.png"
BROWSER_CANDIDATES = (
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
)


def find_browser(explicit_path: Path | None = None) -> Path:
    """Return a usable local Chromium browser executable or raise a clear error."""
    candidates = (explicit_path,) if explicit_path is not None else BROWSER_CANDIDATES
    for candidate in candidates:
        if candidate is not None and candidate.is_file():
            return candidate
    raise FileNotFoundError(
        "Chrome or Edge was not found. Pass --browser-executable with its full path."
    )


def wait_for_server(url: str, *, timeout: float = 45) -> None:
    """Wait until Streamlit accepts HTTP requests or fail within a fixed timeout."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
                if response.status == 200:
                    return
        except (urllib.error.URLError, TimeoutError):
            time.sleep(0.25)
    raise TimeoutError(f"Streamlit did not become ready within {timeout:.0f} seconds.")


def capture(output: Path, browser_executable: Path, *, port: int) -> None:
    """Run Streamlit temporarily and capture the fully rendered overview page."""
    url = f"http://127.0.0.1:{port}"
    command = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "src/babynames/app.py",
        "--server.headless=true",
        f"--server.port={port}",
        "--browser.gatherUsageStats=false",
    ]
    server = subprocess.Popen(  # noqa: S603
        command,
        cwd=PROJECT_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        wait_for_server(url)
        output.parent.mkdir(parents=True, exist_ok=True)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                executable_path=str(browser_executable),
                headless=True,
            )
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            page.goto(url, wait_until="networkidle")
            # The sidebar repeats the product heading as navigation branding;
            # the last matching heading is the rendered overview content.
            page.get_by_role("heading", name="Baby Names", exact=True).last.wait_for()
            # Streamlit paints placeholders before Arrow tables and Vega charts.
            # Waiting for both known latest-year leaders makes the capture stable.
            # Streamlit's canvas-backed tables keep accessibility cells visually
            # hidden, so attached state is the correct data-readiness signal.
            page.get_by_text("Olivia", exact=True).first.wait_for(state="attached", timeout=45_000)
            page.get_by_text("Liam", exact=True).first.wait_for(state="attached", timeout=45_000)
            page.locator('[data-testid="stVegaLiteChart"]').first.wait_for(timeout=45_000)
            page.wait_for_timeout(1_000)
            page.screenshot(path=str(output), full_page=True)
            browser.close()
    finally:
        server.terminate()
        try:
            server.wait(timeout=10)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)


def main(argv: Sequence[str] | None = None) -> int:
    """Parse command arguments and capture the application overview."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--browser-executable", type=Path)
    parser.add_argument("--port", type=int, default=8511)
    arguments = parser.parse_args(argv)
    if not 1 <= arguments.port <= 65535:
        parser.error("Port must be between 1 and 65535.")
    browser = find_browser(arguments.browser_executable)
    capture(arguments.output.resolve(), browser, port=arguments.port)
    print(f"Captured {arguments.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

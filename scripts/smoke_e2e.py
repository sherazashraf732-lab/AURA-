"""Browser smoke test: sign up, verify, sign in, open every live page, chat once, report errors.

Needs the API on :8000 (dev database) and the built web app on :5173 (vite preview).
Run:  backend\\.venv\\Scripts\\python.exe -I scripts\\smoke_e2e.py
"""

import os
import re
import sys
import time
import uuid

import psycopg
from playwright.sync_api import sync_playwright

BASE = os.environ.get("AURA_BASE", "http://localhost:5173")
DB = "postgresql://aura:aura@127.0.0.1:5433/aura"
PAGES = ["/app", "/app/chat", "/app/projects", "/app/memory", "/app/knowledge", "/app/research",
         "/app/fact-check", "/app/agents", "/app/documents", "/app/data", "/app/coding",
         "/app/workflows", "/app/usage", "/app/security", "/app/arena", "/app/evaluation",
         "/app/integrations", "/app/graph", "/app/ocr", "/app/vision", "/app/audio",
         "/app/settings", "/app/modules"]  # fmt: skip


def main() -> int:
    email = f"smoke-{uuid.uuid4().hex[:8]}@example.com"
    password = "smoke-test-pass-1"
    failures: list[str] = []
    with sync_playwright() as p:
        exe = os.environ.get("AURA_CHROMIUM")  # reuse an already-installed Chromium if given
        browser = (p.chromium.launch(executable_path=exe) if exe
                   else p.chromium.launch(channel=os.environ.get("AURA_BROWSER_CHANNEL") or None))
        page = browser.new_page()
        errors: list[str] = []
        page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: errors.append(f"{e} @ {(e.stack or '')[:300]}"))

        page.goto(f"{BASE}/signup")
        page.get_by_label("Email").fill(email)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Create account").click()
        page.get_by_text("Check your inbox").wait_for()

        with psycopg.connect(DB) as conn:
            body = conn.execute("SELECT body FROM outbox_emails WHERE to_email=%s ORDER BY created_at DESC",
                                (email,)).fetchone()[0]  # fmt: skip
        token = re.search(r"token=([\w\-]+)", body).group(1)  # type: ignore[union-attr]
        page.goto(f"{BASE}/verify-email?token={token}")
        page.get_by_text("Your email is verified").wait_for()

        page.goto(f"{BASE}/login")
        page.get_by_label("Email").fill(email)
        page.get_by_label("Password").fill(password)
        page.get_by_role("button", name="Sign in").click()
        page.wait_for_url(f"{BASE}/app")

        for path in PAGES:
            errors.clear()
            page.goto(f"{BASE}{path}")
            try:
                page.locator("main h1").first.wait_for(timeout=8000)
                page.wait_for_load_state("networkidle")
            except Exception as e:  # noqa: BLE001
                failures.append(f"{path}: no heading ({type(e).__name__})")
            real = [e for e in errors if "favicon" not in e]
            if real:
                failures.append(f"{path}: console errors {real[:2]}")
            print(f"ok {path}" if not real else f"ERR {path}")

        errors.clear()
        page.goto(f"{BASE}/app/chat")
        try:
            page.get_by_label("Message").fill("aap kaise hain", timeout=15000)
        except Exception:  # noqa: BLE001
            print("CHAT PAGE ERRORS", errors[:3])
            raise
        page.get_by_role("button", name="Send").click()
        try:
            page.get_by_text("Demo jawab").wait_for(timeout=15000)
            print("ok chat round trip (Roman Urdu reply)")
        except Exception:  # noqa: BLE001
            text = page.url + " :: " + " | ".join(page.inner_text("body").splitlines())[-400:] + " :: " + str(errors[-3:])
            failures.append("chat: no reply; page says: " + text)
        time.sleep(0.5)
        browser.close()
    for f in failures:
        print("FAIL", f)
    print(f"{len(PAGES) - len(failures)}/{len(PAGES)} pages clean")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

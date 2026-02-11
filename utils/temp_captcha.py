import requests
import re
import base64
from bs4 import BeautifulSoup
from pathlib import Path


BASE = "https://vtopcc.vit.ac.in/vtop"


def extract_csrf(html: str) -> str:
    """
    Extracts CSRF value from a hidden input
    """
    m = re.search(
        r'<input[^>]+name="_csrf"[^>]+value="([^"]+)"',
        html
    )
    if not m:
        raise RuntimeError("CSRF token not found in page")
    return m.group(1)


def login_and_get_csrf_auth(username: str, password: str) -> str:

    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0",
        "X-Requested-With": "XMLHttpRequest"
    }

    # ------------------------------------------------------------
    # 1. /open/page   (GET)  → csrf_unauth
    # ------------------------------------------------------------

    r1 = session.get(
        f"{BASE}/open/page",
        headers=headers,
        timeout=30,
        verify=False
    )

    r1.raise_for_status()
    csrf_unauth = extract_csrf(r1.text)

    print("csrf_unauth:", csrf_unauth)

    # ------------------------------------------------------------
    # 2. /prelogin/setup  (POST)
    # ------------------------------------------------------------

    r2 = session.post(
        f"{BASE}/prelogin/setup",
        data={
            "_csrf": csrf_unauth,
            "flag": "VTOP"
        },
        headers=headers,
        timeout=30,
        verify=False
    )

    r2.raise_for_status()

    # ------------------------------------------------------------
    # 3. /login   (GET) → captcha page
    # ------------------------------------------------------------

    r3 = session.get(
        f"{BASE}/login",
        headers=headers,
        timeout=30,
        verify=False
    )

    r3.raise_for_status()

    soup = BeautifulSoup(r3.text, "html.parser")

    captcha_block = soup.find("div", id="captchaBlock")

    captcha_file = None

    if captcha_block:
        img = captcha_block.find("img")

        if img and img.get("src"):

            src = img["src"]

            # ----------------------------------------------------
            # data:image/...;base64,...
            # ----------------------------------------------------
            if src.startswith("data:image"):
                header, encoded = src.split(",", 1)
                data = base64.b64decode(encoded)

                captcha_file = Path("captcha.jpg")
                captcha_file.write_bytes(data)

            # ----------------------------------------------------
            # normal image url
            # ----------------------------------------------------
            else:
                if src.startswith("/"):
                    src = "https://vtopcc.vit.ac.in" + src

                img_resp = session.get(
                    src,
                    headers=headers,
                    timeout=30,
                    verify=False
                )

                img_resp.raise_for_status()

                captcha_file = Path("captcha.jpg")
                captcha_file.write_bytes(img_resp.content)

    if captcha_file:
        print("Captcha saved as:", captcha_file.resolve())
    else:
        print("No captcha image found (probably no-captcha flow)")

    # ------------------------------------------------------------
    # User enters captcha
    # ------------------------------------------------------------

    captcha_value = input("Enter captcha: ").strip()

    # ------------------------------------------------------------
    # 4. /login   (POST)
    # ------------------------------------------------------------

    r4 = session.post(
        f"{BASE}/login",
        data={
            "_csrf": csrf_unauth,
            "username": username,
            "password": password,
            "captchaStr": captcha_value
        },
        headers=headers,
        timeout=30,
        verify=False,
        allow_redirects=True
    )

    r4.raise_for_status()

    # ------------------------------------------------------------
    # 5. /content  (GET)
    # ------------------------------------------------------------

    r5 = session.get(
        f"{BASE}/content",
        headers=headers,
        timeout=30,
        verify=False
    )

    r5.raise_for_status()

    # ------------------------------------------------------------
    # 6. extract csrf_auth
    # ------------------------------------------------------------

    csrf_auth = extract_csrf(r5.text)

    print("csrf_auth:", csrf_auth)

    return csrf_auth

if __name__ == "__main__":
    login_and_get_csrf_auth("23BPS1136", "Vampire69?!")
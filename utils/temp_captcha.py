import os
import base64
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dotenv import load_dotenv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

LOGIN_URL = "https://vtopcc.vit.ac.in/vtop/login"

JSESSIONID = os.getenv("VTOP_JSESSIONID")
SERVERID = os.getenv("VTOP_SERVERID", "vt1")


def fetch_captcha_image():

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://vtopcc.vit.ac.in/vtop/content",
    }

    cookies = {
        "JSESSIONID": JSESSIONID,
        "SERVERID": SERVERID
    }

    resp = requests.get(
        LOGIN_URL,
        headers=headers,
        cookies=cookies,
        verify=False,
        timeout=30
    )

    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    captcha_block = soup.find("div", id="captchaBlock")

    if not captcha_block:
        print("captchaBlock not found (maybe no captcha on this session)")
        return

    img = captcha_block.find("img")

    if not img or not img.get("src"):
        print("No captcha image found inside captchaBlock")
        return

    img_src = img["src"]

    print("Captcha image URL:", img_src[:80], "...")

    # -----------------------------
    # CASE 1 : inline base64 image
    # -----------------------------
    if img_src.startswith("data:image"):
        print("Detected base64 embedded captcha")

        header, encoded = img_src.split(",", 1)

        image_bytes = base64.b64decode(encoded)

        with open("captcha.png", "wb") as f:
            f.write(image_bytes)

        print("captcha.png saved (from base64)")
        return

    # -----------------------------
    # CASE 2 : normal URL image
    # -----------------------------
    img_url = urljoin(LOGIN_URL, img_src)

    print("Resolved captcha URL:", img_url)

    img_resp = requests.get(
        img_url,
        headers=headers,
        cookies=cookies,
        verify=certifi.where(),
        timeout=20
    )

    img_resp.raise_for_status()

    with open("captcha.png", "wb") as f:
        f.write(img_resp.content)

    print("captcha.png saved (from URL)")


if __name__ == "__main__":
    fetch_captcha_image()

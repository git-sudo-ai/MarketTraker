import os
import sys
import re
import io
import json
import time
import threading
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urljoin
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

if sys.platform == "darwin":
    try:
        import ctypes
        import ctypes.util
    except Exception:
        pass

__version__ = "1.2"
__license__ = "GPL-2.0"
__author__ = "git-sudo-ai"

CHECK_INTERVAL_SEC = 240
DB_FILE_NAME = "goods_search_db"

DRAWER_TARGET_HEIGHT = 148
DRAWER_ANIM_STEP = 15
DRAWER_ANIM_DELAY_MS = 10

COLOR_GREEN = "#5bb974"
COLOR_GREEN_HOVER = "#48a060"
COLOR_ACCENT = "#2563eb"
COLOR_WARNING = "#b33a3a"
COLOR_WB = "#6b21a8"
COLOR_OZON = "#005bff"
COLOR_BG = "#f8fafc"
COLOR_CARD_BORDER = "#cbd5e1"
COLOR_SUCCESS_BG = "#f0fdf4"
COLOR_SUCCESS_BORDER = "#22c55e"

DEFAULT_WINDOW_SIZE = "780x680"
ADD_WINDOW_SIZE = "660x580"

TG_ICON_DATA = "iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAADL0lEQVR4nK1UzWtcVRT/nXPvm4/MJOlMsTWC2iaNECIuShUx4MavinFRhGzEipWAbt1L/wO3XfgFgpsuxIXSFNtNsEixiKBVSMg0/ZgQQ81o+l5m5r17z5F7p5Ngcel5m/vOOb/f+bjnHsJQzp83WFjw4Tj5+dprnJjT4v0cRB6JduYNNuaKFP6L1jtT3z6IoahQZRDJ5LmfpqnW+AjAPFkLzftQiX4gNqBSGepc+P1Gs84HrfePrw6xHFmJ5Oi5X5+hWuMql6vzWvRUupmoOB0mHM5RV/Q0+FC9cTVgAjZwMK5f1+kvb05yrbYEpoZLOw7EBCIGaJDxICdiJrbGUH6v40SpETABGzii49FPf79g682TLt12RGzxgJj7dLtO0XWCw7UEFuKy0rhF1llqvTvzKh35ZOVlU0ouatGXQRbD+IGA4ESRFYJQ40yzjFNTY3jyYBkf/rCF22kulXKVXT9/xTLrItkEWvRjP5jCDRB6XpAVHmMlxouP1fHWzAG88GgNosClWynWd3LULCuMBXN/0arq81L0AjpwxOh9r5g+UMb8ZB1vHBuPmQRZ+ytHs2Lw/cZu9BlNwK7oIXBYYnMI3oOIKPeKZydG8N5TTcxNjKCW7FWKlU4fhSjqpQSXb6fR5hUUsWwO7XvqoCd/7DrcywVVu2/azBzupAVmD1ZwYT1F6+8cFcOxb0NhFb8FY6BQDbdzc6fA4qU2XvrqBpbbGf7sevxyt4cTh6sR8PXaTuxhjAzViBW/xUS0zEkl6EMfUTGEhyoWv2338fbFNpbvpHj64SrGSiZm9uPmLkYSGjgrJGAjhwh9rK7Yey7BHi6biPDcRBU/3+3hzHft2NxrW120M4fyflkUsIHjPwcyKENjp8ZL2Nx1sdxTx8ZC+bh8K8NoycCLd7betC7dXroRBhJnz/L0E2eOiJdr4YlIv7tHlovCEiExhDSXOB9lSxAvjitVC9EOGz6xuvLZOmN2llbffLwlWXYyGGy9YaESPikxaQCH6R6xpGWDoFY72ogkAROwgeN/WyODB3p/FbQWjq8CeD0sNmJ/WonmQBwXmxJtkPgr6uXfi40oRvoHtInEN4izdlgAAAAASUVORK5CYII="
GH_ICON_DATA = "iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAACv0lEQVR4nI1US2sUQRCu6u6Z1fg6icJKZJNJWNaYZM1BBCEnb0nIZQ4iiIg3f4B4CgH/guLNg6LIXgRB8GYgHnII0TyWPHY3Go2GiChIjDszXSXV2dnEPMCCXYqq7/u6uqqmAfYaAoQaDrRQcrgP6R9TAEDitBUKrQr8i0DUvpVRVYJoolYur+zG7hIaUQCjdLZQOO2xPwrIV5XSx7ABYWAgsr+A8VmM0cjHcnkt5ewUcuq5zq5uo81L43utSRwDEUcALDmBklLoG8+DJIpXEpsMLi/OTqdc+XPAXFfXKaXNKwbIRvX6U2L6po32EdHIT3yJSU4wghVOWoiCMJSqSFt9z/NMlplmq/PT1zDmC8TJkLK2B5Ok1/kJFiUnGMEKx/UpDNFdraOjJ8uaF5XWh62185j8LlYqlfp+MwuCIMOmZUprnSdrN9Fi59LS+1V3LTJ8GbVukUYw4iMR6evr8yB0o966fhhqiUlOMIIVjnDTJgMy5BQiMzMg23GJTU62EZRKtjFi57uYw9txwQpHuE0hdlpuggysjrul61/fs3TgYqEGUicEzg2upExjRz6AnKAUEvEwQOk1vIF0hbZtbEwqZFDnh1x3WQqC5aYQxjROSAkD/0TEG0G+d6aC7x5uHbhtQRD44LXcBMBbRMQMEGFs30LaxGp17hMzv1CovgPRdaXxfue54o9cvnugKZLvHkD/6ByifsDMqLWWop4LVzQMlEpyKnIEt+EQ1kDhlXoUFTKeP6QTNdHYfiaj1zRDOxHVldYZa+1XTequy5dKbv1lElirTa8TJf2IOOwZcydO4tU/fiQ9caYZNpiIjDYZIP7MTIMLC1NfGge5T0SMZBrV+ZnJzRiKgHDS87zHR6zOpn2S6wDCBpF9wrG9JNjGk9J8AXZaKgzyChQKBX9HozNBcP7MftiDTP3Hw7ZH5C+myVc9YUeWwgAAAABJRU5ErkJggg=="
QR_CODE_DATA = "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"

def get_db_path():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, DB_FILE_NAME)

def load_db():
    path = get_db_path()
    if not os.path.exists(path):
        save_db([])
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []

def save_db(items):
    path = get_db_path()
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except OSError:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

def send_notification(title, message):
    if sys.platform == "darwin":
        clean_msg = message.replace('"', '\\"').replace("'", "")
        clean_title = title.replace('"', '\\"').replace("'", "")
        cmd = f'display notification "{clean_msg}" with title "{clean_title}" sound name "Glass"'
        try:
            subprocess.run(["osascript", "-e", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass

def is_product_ready(item):
    cp = item.get("current_price")
    tp = item.get("target_price")
    return bool(cp is not None and tp is not None and cp <= tp)

def get_basket_number(nm: int) -> int:
    vol = nm // 100000
    if 0 <= vol <= 143: return 1
    elif 144 <= vol <= 287: return 2
    elif 288 <= vol <= 431: return 3
    elif 432 <= vol <= 719: return 4
    elif 720 <= vol <= 1007: return 5
    elif 1008 <= vol <= 1061: return 6
    elif 1062 <= vol <= 1115: return 7
    elif 1116 <= vol <= 1169: return 8
    elif 1170 <= vol <= 1313: return 9
    elif 1314 <= vol <= 1601: return 10
    elif 1602 <= vol <= 1655: return 11
    elif 1656 <= vol <= 1919: return 12
    elif 1920 <= vol <= 2045: return 13
    elif 2046 <= vol <= 2189: return 14
    elif 2190 <= vol <= 2405: return 15
    elif 2406 <= vol <= 2621: return 16
    elif 2622 <= vol <= 2837: return 17
    elif 2838 <= vol <= 3053: return 18
    elif 3054 <= vol <= 3269: return 19
    elif 3270 <= vol <= 3485: return 20
    elif 3486 <= vol <= 3701: return 21
    elif 3702 <= vol <= 3917: return 22
    elif 3918 <= vol <= 4133: return 23
    elif 4134 <= vol <= 4349: return 24
    elif 4350 <= vol <= 4565: return 25
    elif 4566 <= vol <= 4781: return 26
    elif 4782 <= vol <= 4997: return 27
    elif 4998 <= vol <= 5213: return 28
    else: return 29

def parse_target_url(raw_url: str):
    clean = raw_url.strip()
    if re.fullmatch(r'\d{5,12}', clean):
        return "Wildberries", clean, None
    if not clean.startswith(("http://", "https://")):
        clean = "https://" + clean

    if "wildberries" in clean or "wb.ru" in clean or "linkwb" in clean or "wb.click" in clean:
        wb_match = re.search(r'/catalog/(\d+)', clean) or re.search(r'[?&]card=(\d+)', clean) or re.search(r'(\d{5,12})', clean)
        nm_str = wb_match.group(1) if wb_match else ""
        parsed = urlparse(clean)
        qs = parse_qs(parsed.query)
        size_param = qs.get("size", [None])[0]
        return "Wildberries", nm_str, size_param

    if "ozon." in clean or "ozon" in clean:
        ozon_match = re.search(r'/product/(?:([^/]+)-)?(\d+)', clean) or re.search(r'/context/detail/id/(\d+)', clean)
        slug = ""
        prod_id = ""
        if ozon_match:
            slug = ozon_match.group(1) if (ozon_match.lastindex and ozon_match.lastindex >= 2) else ""
            prod_id = ozon_match.group(2) if (ozon_match.lastindex and ozon_match.lastindex >= 2) else ozon_match.group(1)
        parsed = urlparse(clean)
        qs = parse_qs(parsed.query)
        sku_param = qs.get("sku", [None])[0]
        return "Ozon", prod_id or sku_param or "", sku_param or slug

    return "Unknown", None, None

def unshorten_url(url: str, max_hops: int = 5) -> str:
    current = url.strip()
    if not current.startswith(("http://", "https://")):
        if re.fullmatch(r'\d{5,12}', current):
            return f"https://www.wildberries.ru/catalog/{current}/detail.aspx"
        current = "https://" + current

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
    }

    for _ in range(max_hops):
        wb_m = re.search(r'/catalog/(\d+)', current) or re.search(r'[?&]card=(\d+)', current)
        oz_m = re.search(r'/product/(?:([^/]+)-)?(\d+)', current) or re.search(r'/context/detail/id/(\d+)', current)
        if (wb_m and ("wildberries" in current or "wb.ru" in current)) or oz_m:
            return current

        next_url = None

        try:
            cmd = ["curl", "-s", "-D", "-", "-o", "/dev/null", "-m", "4", "-A", headers["User-Agent"], current]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            for line in res.stdout.splitlines():
                if line.lower().startswith("location:"):
                    loc = line.split(":", 1)[1].strip()
                    if loc:
                        next_url = urljoin(current, loc)
                        break
        except Exception:
            pass

        if not next_url:
            class NoRedirect(urllib.request.HTTPRedirectHandler):
                def redirect_request(self, req, fp, code, msg, hds, newurl):
                    return None

            try:
                opener = urllib.request.build_opener(NoRedirect)
                req = urllib.request.Request(current, headers=headers)
                resp = opener.open(req, timeout=4)
                dest = resp.geturl()
                if dest and dest != current:
                    next_url = dest
            except urllib.error.HTTPError as e:
                loc = e.headers.get("Location") or e.headers.get("location")
                if loc:
                    next_url = urljoin(current, loc)
            except Exception:
                pass

        if not next_url:
            try:
                cmd = ["curl", "-s", "-L", "-m", "5", "-o", "/dev/null", "-w", "%{url_effective}", "-A", headers["User-Agent"], current]
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=6)
                eff = res.stdout.strip()
                if eff and eff.startswith("http") and eff != current:
                    next_url = eff
            except Exception:
                pass

        if not next_url or next_url == current:
            break
        current = next_url

    return current

def get_wb_image_candidates(nm, b=None):
    if b is None:
        b = get_basket_number(nm)
    vol = nm // 100000
    part = nm // 1000
    base = f"https://basket-{b:02d}.wbbasket.ru/vol{vol}/part{part}/{nm}/images"
    return [
        f"{base}/c246x328/1.webp",
        f"{base}/c516x688/1.webp",
        f"{base}/big/1.webp",
        f"{base}/big/1.jpg",
        f"{base}/c246x328/1.jpg"
    ]

def extract_safari_tab_source(target_url, prod_id, original_url=""):
    if sys.platform != "darwin":
        return None
    try:
        id_chk = str(prod_id).replace("\\", "\\\\").replace("\"", "\\\"") if prod_id else ""
        url_chk = str(target_url).replace("\\", "\\\\").replace("\"", "\\\"") if target_url else ""
        orig_chk = str(original_url).replace("\\", "\\\\").replace("\"", "\\\"") if original_url else ""

        load_url = ""
        if target_url and target_url.startswith(("http://", "https://")):
            load_url = target_url
        elif original_url and original_url.startswith(("http://", "https://")):
            load_url = original_url
        elif prod_id:
            if "wildberries" in str(target_url):
                load_url = f"https://www.wildberries.ru/catalog/{prod_id}/detail.aspx"
            else:
                load_url = f"https://www.ozon.ru/product/{prod_id}/"
        load_url = load_url.replace("\\", "\\\\").replace("\"", "\\\"")

        script = f'''
        tell application "System Events"
            set isRunning to (name of processes) contains "Safari"
        end tell
        if isRunning then
            tell application "Safari"
                repeat with w in windows
                    repeat with t in tabs of w
                        set u to URL of t
                        if ("{id_chk}" is not "" and u contains "{id_chk}") or ("{url_chk}" is not "" and u contains "{url_chk}") or ("{orig_chk}" is not "" and u contains "{orig_chk}") then
                            return source of t
                        end if
                    end repeat
                end repeat
            end tell
        end if

        if "{load_url}" is not "" then
            tell application "System Events"
                set isRunning to (name of processes) contains "Safari"
            end tell
            if not isRunning then
                tell application "Safari" to launch
                delay 0.8
            end if
            tell application "Safari"
                if (count of windows) = 0 then
                    set newDoc to (make new document with properties {{URL:"{load_url}"}})
                    repeat 15 times
                        delay 0.25
                        set src to source of newDoc
                        if src contains "webPrice" or src contains "state-webPrice" then
                            exit repeat
                        end if
                    end repeat
                    set finalSrc to source of newDoc
                    close newDoc
                    return finalSrc
                else
                    set newTab to (make new tab at end of tabs of window 1 with properties {{URL:"{load_url}"}})
                    repeat 15 times
                        delay 0.25
                        set src to source of newTab
                        if src contains "webPrice" or src contains "state-webPrice" then
                            exit repeat
                        end if
                    end repeat
                    set finalSrc to source of newTab
                    close newTab
                    return finalSrc
                end if
            end tell
        end if
        return ""
        '''
        res = subprocess.run(["osascript", "-e", script], capture_output=True, text=True, timeout=8)
        html = res.stdout
        return html if html and len(html) > 500 else None
    except Exception:
        return None

def fetch_wb_card_data(nm: int):
    vol = nm // 100000
    part = nm // 1000
    primary_b = get_basket_number(nm)
    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}

    candidate_baskets = [primary_b]
    for delta in (-1, 1, -2, 2):
        cand = primary_b + delta
        if 1 <= cand <= 30 and cand not in candidate_baskets:
            candidate_baskets.append(cand)

    for b in candidate_baskets:
        card_url = f"https://basket-{b:02d}.wbbasket.ru/vol{vol}/part{part}/{nm}/info/ru/card.json"
        try:
            req = urllib.request.Request(card_url, headers=headers)
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode())
                    return data, b
        except Exception:
            pass
    return {}, primary_b

def fetch_wb_details(nm_str: str):
    try:
        nm = int(nm_str)
    except ValueError:
        return None

    card_data, b = fetch_wb_card_data(nm)

    title = card_data.get("imt_name") or f"Товар Wildberries #{nm}"
    colors = card_data.get("colors") or []
    tech_size = card_data.get("data", {}).get("tech_size")
    default_img_cands = get_wb_image_candidates(nm, b)
    default_img = default_img_cands[0]

    detected_price = None
    detected_stock = ""

    safari_html = extract_safari_tab_source(f"wildberries.ru/catalog/{nm}", str(nm))
    if safari_html:
        p_matches = re.findall(r'(\d[\d\s]{1,8})\s*₽', safari_html)
        for pm in p_matches:
            digits = int(re.sub(r'\s+', '', pm))
            if 50 <= digits <= 2000000:
                detected_price = digits
                break
        sn_wb = re.search(r'"stockNumber":\s*\{\s*"text":\s*"([^"]+)"', safari_html)
        if sn_wb:
            detected_stock = f"Остаток: {sn_wb.group(1).strip()} шт."
        else:
            m_wb = re.search(r'(\d+)\s*(?:шт|единиц\w*|штук\w*)\s*осталось', safari_html, re.IGNORECASE)
            if m_wb:
                detected_stock = f"Остаток: {m_wb.group(1)} шт."
            elif "нет в наличии" in safari_html.lower() or "товар закончился" in safari_html.lower():
                detected_stock = "Нет в наличии"

    if not detected_stock and card_data:
        detected_stock = "В наличии"

    categories = {}

    if len(colors) > 1:
        color_variants = []
        for c in colors:
            cb = get_basket_number(c)
            c_cands = get_wb_image_candidates(c, cb)
            cimg = c_cands[0]
            is_cur = (c == nm)
            label = f"Арт. {c}" + (" (текущий)" if is_cur else "")
            color_variants.append({
                "label": label,
                "variant_name": f"Цвет / Арт: {c}",
                "nm": str(c),
                "url": f"https://www.wildberries.ru/catalog/{c}/detail.aspx",
                "image_url": cimg,
                "image_candidates": c_cands,
                "price": detected_price if is_cur else None,
                "stock": detected_stock if is_cur else "В наличии",
                "is_default": is_cur
            })
        categories["Цвет / Модель"] = color_variants

    if tech_size and tech_size != "0":
        categories["Размер"] = [{
            "label": str(tech_size),
            "variant_name": f"Размер: {tech_size}",
            "nm": str(nm),
            "url": f"https://www.wildberries.ru/catalog/{nm}/detail.aspx",
            "image_url": default_img,
            "image_candidates": default_img_cands,
            "price": detected_price,
            "stock": detected_stock,
            "is_default": True
        }]

    if not categories:
        categories["Вариант"] = [{
            "label": "Основной (по умолчанию)",
            "variant_name": "Основной",
            "nm": str(nm),
            "url": f"https://www.wildberries.ru/catalog/{nm}/detail.aspx",
            "image_url": default_img,
            "image_candidates": default_img_cands,
            "price": detected_price,
            "stock": detected_stock,
            "is_default": True
        }]

    return {
        "marketplace": "Wildberries",
        "title": title,
        "default_image": default_img,
        "image_candidates": default_img_cands,
        "detected_price": detected_price,
        "detected_stock": detected_stock,
        "categories": categories
    }

def clean_slug_title(slug_str: str):
    if not slug_str:
        return ""
    clean = re.sub(r'-\d+$', '', slug_str)
    words = clean.replace('-', ' ').split()
    return ' '.join(w.capitalize() for w in words)

def parse_ozon_html(html: str, prod_id: str, original_url: str):
    title = None
    detected_price = None
    detected_stock = ""
    default_img = ""
    gallery_imgs = []
    categories = {}

    state_map = {}
    for st, _q, content in re.findall(r'<div id="state-([^"]+)" data-state=([\'"])(.*?)\2>', html):
        state_map[st] = content

    sn_m = re.search(r'"stockNumber":\s*\{\s*"text":\s*"([^"]+)"', html)
    if sn_m:
        detected_stock = f"Остаток: {sn_m.group(1).strip()} шт."
    else:
        m_ost = re.search(r'(\d+)\s*(?:шт|единиц\w*|штук\w*)\s*осталось', html, re.IGNORECASE)
        if m_ost:
            detected_stock = f"Остаток: {m_ost.group(1)} шт."
        elif 'data-widget="webOutOfStock"' in html or '"isOutOfStock":true' in html:
            detected_stock = "Нет в наличии"
        elif 'schema.org/InStock' in html or '"availability":"http://schema.org/InStock"' in html:
            detected_stock = "В наличии"

    for k, v in state_map.items():
        if "webProductHeading" in k:
            try:
                hd = json.loads(v)
                if hd.get("title"):
                    title = hd["title"]
                    break
            except Exception:
                pass

    for k, v in state_map.items():
        if "webPrice" in k:
            try:
                wp = json.loads(v)
                raw = wp.get("cardPrice") or wp.get("price")
                if raw:
                    digits = re.sub(r'[^\d]', '', str(raw))
                    if digits:
                        detected_price = int(digits)
                        break
            except Exception:
                pass

    for k, v in state_map.items():
        if "webGallery" in k:
            try:
                wg = json.loads(v)
                cov = wg.get("coverImage")
                if cov:
                    default_img = cov
                for im in wg.get("images", []):
                    src = im.get("src") if isinstance(im, dict) else im
                    if src:
                        gallery_imgs.append(src)
            except Exception:
                pass

    for k, v in state_map.items():
        if "webAspects" in k:
            try:
                wa = json.loads(v)
                for asp in wa.get("aspects", []):
                    cat_name = asp.get("aspectName") or "Вариант"
                    var_list = []
                    for v_item in asp.get("variants", []):
                        sku = str(v_item.get("sku") or "")
                        v_link = v_item.get("link") or ""
                        if v_link.startswith("/"):
                            v_url = f"https://www.ozon.ru{v_link}"
                        else:
                            v_url = v_link or original_url
                        v_data = v_item.get("data", {})
                        opt_label = v_data.get("searchableText") or v_data.get("title") or sku
                        v_price = v_item.get("price")
                        if not v_price and v_data.get("price"):
                            d_p = re.sub(r'[^\d]', '', str(v_data.get("price")))
                            if d_p:
                                v_price = int(d_p)
                        v_cover = v_data.get("coverImage") or ""
                        v_cands = []
                        if v_cover:
                            v_cands.append(v_cover.replace("/wc140/", "/c600/"))
                            v_cands.append(v_cover.replace("/wc140/", "/wc1000/"))
                            v_cands.append(v_cover)
                        is_cur = (sku == str(prod_id))
                        lbl_txt = str(opt_label) + (" (текущий)" if is_cur else "")
                        v_avail = v_item.get("availability")
                        if v_avail == "outOfStock":
                            v_stock = "Нет в наличии"
                        elif is_cur and detected_stock:
                            v_stock = detected_stock
                        elif v_avail == "inStock":
                            v_stock = "В наличии"
                        else:
                            v_stock = detected_stock
                        var_list.append({
                            "label": lbl_txt,
                            "variant_name": f"{cat_name}: {opt_label}",
                            "nm": sku,
                            "url": v_url,
                            "image_url": v_cands[0] if v_cands else (default_img or ""),
                            "image_candidates": v_cands or ([default_img] if default_img else []),
                            "price": v_price or detected_price,
                            "stock": v_stock,
                            "is_default": is_cur
                        })
                    if var_list:
                        categories[cat_name] = var_list
            except Exception:
                pass

    if not title:
        og_t = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\'](.*?)["\']', html)
        if og_t:
            title = og_t.group(1).strip()

    if not default_img:
        og_i = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\'](.*?)["\']', html)
        if og_i and "logo" not in og_i.group(1).lower():
            default_img = og_i.group(1).strip()

    if not default_img and gallery_imgs:
        default_img = gallery_imgs[0]

    if detected_price is None:
        p_matches = re.findall(r'(\d[\d\s]{1,8})\s*₽', html)
        for pm in p_matches:
            digits = int(re.sub(r'\s+', '', pm))
            if 50 <= digits <= 2000000:
                detected_price = digits
                break

    if not categories:
        categories["Вариант"] = [{
            "label": "Основной вариант",
            "variant_name": "Основной",
            "nm": str(prod_id),
            "url": original_url,
            "image_url": default_img,
            "image_candidates": [default_img] if default_img else [],
            "price": detected_price,
            "stock": detected_stock,
            "is_default": True
        }]

    return {
        "marketplace": "Ozon",
        "title": title or f"Товар Ozon #{prod_id}",
        "default_image": default_img,
        "image_candidates": [default_img] if default_img else [],
        "detected_price": detected_price,
        "detected_stock": detected_stock,
        "categories": categories
    }

def fetch_ozon_details(clean_url: str):
    resolved_url = unshorten_url(clean_url)
    ozon_match = re.search(r'/product/(?:([^/]+)?-)?(\d+)', resolved_url)
    if ozon_match:
        slug = ozon_match.group(1) or ""
        prod_id = ozon_match.group(2) or ""
    else:
        ctx_match = re.search(r'/context/detail/id/(\d+)', resolved_url)
        slug = ""
        prod_id = ctx_match.group(1) if ctx_match else ""

    if not prod_id:
        parsed = urlparse(resolved_url)
        qs = parse_qs(parsed.query)
        prod_id = qs.get("sku", [None])[0] or ""

    html = extract_safari_tab_source(resolved_url, prod_id, original_url=clean_url)
    if html:
        return parse_ozon_html(html, prod_id, resolved_url)

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    try:
        req = urllib.request.Request(resolved_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode(errors="ignore")
            if html:
                return parse_ozon_html(html, prod_id, resolved_url)
    except Exception:
        pass

    fallback_title = clean_slug_title(slug) if slug else f"Товар Ozon #{prod_id}"
    return {
        "marketplace": "Ozon",
        "title": fallback_title,
        "default_image": "",
        "image_candidates": [],
        "detected_price": None,
        "detected_stock": "",
        "categories": {
            "Вариант": [{
                "label": "Основной вариант",
                "variant_name": "Основной",
                "nm": str(prod_id),
                "url": resolved_url,
                "image_url": "",
                "image_candidates": [],
                "price": None,
                "stock": "",
                "is_default": True
            }]
        }
    }

def inspect_product(url: str):
    resolved = unshorten_url(url)
    mp, art, _ = parse_target_url(resolved)
    if mp == "Wildberries":
        if not art:
            _, art_orig, _ = parse_target_url(url)
            art = art_orig
        if art:
            return fetch_wb_details(art)
    elif mp == "Ozon":
        return fetch_ozon_details(resolved)
    return None

def download_image_pil(image_urls, max_w: int = 100, max_h: int = 120):
    if not image_urls or not HAS_PIL:
        return None
    raw_urls = [image_urls] if isinstance(image_urls, str) else list(image_urls)
    urls = []
    for u in raw_urls:
        if not u or not isinstance(u, str):
            continue
        if "/wc140/" in u:
            urls.append(u.replace("/wc140/", "/c600/"))
            urls.append(u.replace("/wc140/", "/wc1000/"))
        if "/c246x328/" in u:
            urls.append(u.replace("/c246x328/", "/c516x688/"))
            urls.append(u.replace("/c246x328/", "/big/"))
        urls.append(u)

    headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    for u in urls:
        if not u.startswith("http"):
            continue
        try:
            req = urllib.request.Request(u, headers=headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = resp.read()
                im = Image.open(io.BytesIO(data))
                im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                return im
        except Exception:
            pass
    return None

CACHED_IMAGES = {}

def get_qr_image(master):
    local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "my_QR.png")
    if os.path.exists(local_path):
        try:
            full = tk.PhotoImage(master=master, file=local_path)
            sub = full.subsample(5, 5)
            CACHED_IMAGES["qr_full"] = full
            CACHED_IMAGES["qr_sub"] = sub
            return sub
        except Exception:
            pass
    img = tk.PhotoImage(master=master, data=QR_CODE_DATA)
    CACHED_IMAGES["qr_img"] = img
    return img

def get_tg_image(master):
    img = tk.PhotoImage(master=master, data=TG_ICON_DATA)
    CACHED_IMAGES["tg_img"] = img
    return img

def get_gh_image(master):
    img = tk.PhotoImage(master=master, data=GH_ICON_DATA)
    CACHED_IMAGES["gh_img"] = img
    return img

class AddWindow:
    def __init__(self, parent, on_added_cb):
        self.win = tk.Toplevel(parent)
        self.win.title("Добавить товар в отслеживание")
        self.win.geometry(ADD_WINDOW_SIZE)
        self.win.minsize(580, 500)
        self.win.transient(parent)
        self.on_added_cb = on_added_cb

        self.inspected_data = None
        self.selected_variant = None
        self.current_preview_tk = None
        self.variant_buttons = {}
        self.last_clipboard = ""

        self.setup()

    def setup(self):
        container = tk.Frame(self.win, padx=16, pady=12)
        container.pack(fill="both", expand=True)

        url_box = tk.Frame(container)
        url_box.pack(fill="x", pady=(0, 8))

        tk.Label(url_box, text="Ссылка на товар (Wildberries или Ozon):", font=("TkDefaultFont", 9, "bold"), anchor="w").pack(fill="x", pady=(0, 2))
        url_row = tk.Frame(url_box)
        url_row.pack(fill="x")

        self.url_var = tk.StringVar()
        self.url_entry = tk.Entry(url_row, textvariable=self.url_var)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.url_entry.bind("<Return>", lambda _e: self.trigger_inspect())

        self.check_btn = tk.Button(url_row, text="Проверить", width=10, command=self.trigger_inspect)
        self.check_btn.pack(side="left", padx=(0, 4))

        paste_btn = tk.Button(url_row, text="Вставить", width=8, command=self.paste_clipboard)
        paste_btn.pack(side="right")

        self.status_lbl = tk.Label(container, text="Вставьте ссылку и нажмите «Проверить»", font=("TkDefaultFont", 9), fg="#64748b", anchor="w")
        self.status_lbl.pack(fill="x", pady=(0, 6))

        self.result_frame = tk.Frame(container, bg="#ffffff", padx=12, pady=10, relief="solid", bd=1)

        top_info = tk.Frame(self.result_frame, bg="#ffffff")
        top_info.pack(fill="x", pady=(0, 10))

        self.preview_frame = tk.Frame(top_info, width=100, height=130, bg="#f1f5f9", relief="solid", bd=1)
        self.preview_frame.pack_propagate(False)
        self.preview_frame.pack(side="left", padx=(0, 12))

        self.preview_lbl = tk.Label(self.preview_frame, text="Превью", bg="#f1f5f9", fg="#94a3b8")
        self.preview_lbl.pack(fill="both", expand=True)

        right_meta = tk.Frame(top_info, bg="#ffffff")
        right_meta.pack(side="left", fill="both", expand=True)

        self.prod_title_lbl = tk.Label(right_meta, text="", font=("TkDefaultFont", 10, "bold"), bg="#ffffff", fg="#0f172a", justify="left", wraplength=440, anchor="w")
        self.prod_title_lbl.pack(fill="x", pady=(0, 6))

        prices_box = tk.Frame(right_meta, bg="#ffffff")
        prices_box.pack(fill="x", pady=(2, 0))

        p_row1 = tk.Frame(prices_box, bg="#ffffff")
        p_row1.pack(fill="x", pady=2)
        tk.Label(p_row1, text="Текущая цена (₽):", font=("TkDefaultFont", 9, "bold"), bg="#ffffff", fg="#334155", width=22, anchor="w").pack(side="left")
        self.cur_price_var = tk.StringVar()
        self.cur_price_entry = tk.Entry(p_row1, textvariable=self.cur_price_var, width=12, font=("TkDefaultFont", 10, "bold"))
        self.cur_price_entry.pack(side="left")
        self.cur_price_hint = tk.Label(p_row1, text="рублей", font=("TkDefaultFont", 8), bg="#ffffff", fg="#64748b")
        self.cur_price_hint.pack(side="left", padx=(6, 0))

        p_row2 = tk.Frame(prices_box, bg="#ffffff")
        p_row2.pack(fill="x", pady=2)
        tk.Label(p_row2, text="Желаемая цена покупки (₽):", font=("TkDefaultFont", 9, "bold"), bg="#ffffff", fg="#15803d", width=22, anchor="w").pack(side="left")
        self.tgt_price_var = tk.StringVar()
        self.tgt_price_entry = tk.Entry(p_row2, textvariable=self.tgt_price_var, width=12, font=("TkDefaultFont", 10, "bold"))
        self.tgt_price_entry.pack(side="left")
        tk.Label(p_row2, text="(не выше которой готовы купить)", font=("TkDefaultFont", 8), bg="#ffffff", fg="#16a34a").pack(side="left", padx=(6, 0))

        def _on_cur_price(*_args):
            digits = re.sub(r'[^\d]', '', self.cur_price_var.get())
            if digits:
                try:
                    self.tgt_price_var.set(str(int(int(digits) * 0.95)))
                except ValueError:
                    pass
        self.cur_price_var.trace_add("write", _on_cur_price)

        self.variants_outer = tk.Frame(self.result_frame, bg="#ffffff")
        self.variants_outer.pack(fill="both", expand=True, pady=(6, 0))

        tk.Label(self.variants_outer, text="Доступные варианты товара (нажмите для выбора):", font=("TkDefaultFont", 9, "bold"), bg="#ffffff", fg="#0f172a", anchor="w").pack(fill="x", pady=(0, 4))

        self.variants_canvas = tk.Canvas(self.variants_outer, bg="#ffffff", highlightthickness=0, height=140)
        self.variants_scroll = ttk.Scrollbar(self.variants_outer, orient="vertical", command=self.variants_canvas.yview)
        self.variants_inner = tk.Frame(self.variants_canvas, bg="#ffffff")

        self.variants_inner.bind("<Configure>", lambda e: self.variants_canvas.configure(scrollregion=self.variants_canvas.bbox("all")))
        self.v_canvas_win = self.variants_canvas.create_window((0, 0), window=self.variants_inner, anchor="nw")
        self.variants_canvas.configure(yscrollcommand=self.variants_scroll.set)
        self.variants_canvas.bind("<Configure>", lambda e: self.variants_canvas.itemconfig(self.v_canvas_win, width=e.width))

        self.variants_scroll.pack(side="right", fill="y")
        self.variants_canvas.pack(side="left", fill="both", expand=True)

        bottom_row = tk.Frame(container)
        bottom_row.pack(fill="x", side="bottom", pady=(10, 0))

        cancel_btn = tk.Button(bottom_row, text="Отмена", width=10, command=self.win.destroy)
        cancel_btn.pack(side="right", padx=(6, 0))

        self.add_btn = tk.Label(
            bottom_row, text="Добавить в отслеживание",
            bg=COLOR_GREEN, fg="white",
            relief="flat", cursor="hand2",
            font=("TkDefaultFont", 9, "bold"),
            padx=14, pady=6
        )
        self.add_btn.pack(side="right")
        self.add_btn.bind("<Button-1>", lambda _e: self.submit())
        self.add_btn.bind("<Enter>", lambda _e: self.add_btn.config(bg=COLOR_GREEN_HOVER))
        self.add_btn.bind("<Leave>", lambda _e: self.add_btn.config(bg=COLOR_GREEN))

        self.check_clipboard()
        self.start_clipboard_monitor()

    def start_clipboard_monitor(self):
        self.win.bind("<FocusIn>", lambda _e: self.check_clipboard())
        self.poll_clipboard_tick()

    def poll_clipboard_tick(self):
        if not self.win.winfo_exists():
            return
        self.check_clipboard()
        if self.win.winfo_exists():
            self.win.after(500, self.poll_clipboard_tick)

    def check_clipboard(self):
        try:
            cb = self.win.clipboard_get().strip()
        except Exception:
            return
        if not cb or cb == self.last_clipboard:
            return
        self.last_clipboard = cb
        is_mp = (cb.startswith("http") or any(cb.startswith(p) for p in ("ozon.", "wb.", "wildberries.", "linkwb."))) and any(k in cb for k in ("wildberries", "ozon", "wb.ru", "linkwb", "wb.click"))
        is_wb_digits = bool(re.fullmatch(r'\d{5,12}', cb))
        if is_mp or is_wb_digits:
            if cb != self.url_var.get().strip():
                self.url_var.set(cb)
                self.trigger_inspect()

    def paste_clipboard(self):
        try:
            cb = self.win.clipboard_get().strip()
            self.last_clipboard = cb
            self.url_var.set(cb)
            self.trigger_inspect()
        except Exception:
            pass

    def trigger_inspect(self):
        url = self.url_var.get().strip()
        if not url:
            self.status_lbl.config(text="Укажите ссылку на товар.", fg=COLOR_WARNING)
            return

        mp, art, _ = parse_target_url(url)
        if mp == "Unknown":
            self.status_lbl.config(text="Поддерживаются только ссылки на Wildberries или Ozon.", fg=COLOR_WARNING)
            return

        hint_name = f"{mp} #{art}" if art else mp
        self.status_lbl.config(text=f"Проверка {hint_name}... Поиск доступных вариантов и цен", fg=COLOR_ACCENT)
        self.check_btn.config(state="disabled")

        def worker():
            resolved = unshorten_url(url)
            data = inspect_product(resolved)
            def done():
                self.check_btn.config(state="normal")
                if not data:
                    self.status_lbl.config(text="Не удалось получить данные о товаре. Проверьте ссылку.", fg=COLOR_WARNING)
                    return
                if resolved and resolved != url and resolved.startswith("http"):
                    self.url_var.set(resolved)
                self.inspected_data = data
                self.render_inspected_data()
            self.win.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def render_inspected_data(self):
        self.result_frame.pack(fill="both", expand=True, pady=(4, 0))
        d = self.inspected_data
        mp = d.get("marketplace", "")
        self.status_lbl.config(text=f"Товар {mp} успешно проверен. Выберите нужный вариант ниже:", fg="#15803d")
        self.prod_title_lbl.config(text=d.get("title", ""))

        det_p = d.get("detected_price")
        if det_p is not None:
            self.cur_price_var.set(str(det_p))
            if not self.tgt_price_var.get().strip():
                self.tgt_price_var.set(str(int(det_p * 0.95)))
        else:
            self.cur_price_var.set("")

        for w in self.variants_inner.winfo_children():
            w.destroy()
        self.variant_buttons.clear()

        categories = d.get("categories", {})
        default_var = None

        for cat_name, items in categories.items():
            cat_box = tk.Frame(self.variants_inner, bg="#ffffff", pady=4)
            cat_box.pack(fill="x", anchor="w")

            tk.Label(cat_box, text=f"{cat_name}:", font=("TkDefaultFont", 8, "bold"), bg="#ffffff", fg="#475569").pack(anchor="w", pady=(0, 2))

            btns_col = tk.Frame(cat_box, bg="#ffffff")
            btns_col.pack(fill="x", anchor="w")

            for item in items:
                v_btn = tk.Label(
                    btns_col,
                    text=item["label"],
                    font=("TkDefaultFont", 8),
                    bg="#f1f5f9",
                    fg="#1e293b",
                    relief="solid",
                    bd=1,
                    padx=10,
                    pady=4,
                    cursor="hand2"
                )
                v_btn.pack(anchor="w", pady=2)
                v_btn.bind("<Button-1>", lambda _e, it=item, cat=cat_name: self.select_variant(it, cat))

                if cat_name not in self.variant_buttons:
                    self.variant_buttons[cat_name] = []
                self.variant_buttons[cat_name].append((v_btn, item))

                if item.get("is_default") and default_var is None:
                    default_var = (item, cat_name)

        if default_var:
            self.select_variant(default_var[0], default_var[1])
        elif categories:
            first_cat = list(categories.keys())[0]
            if categories[first_cat]:
                self.select_variant(categories[first_cat][0], first_cat)

    def select_variant(self, item, cat_name):
        self.selected_variant = item
        if cat_name in self.variant_buttons:
            for btn, it in self.variant_buttons[cat_name]:
                if it == item:
                    btn.config(bg=COLOR_ACCENT, fg="#ffffff", font=("TkDefaultFont", 8, "bold"))
                else:
                    btn.config(bg="#f1f5f9", fg="#1e293b", font=("TkDefaultFont", 8))

        var_price = item.get("price")
        if var_price is not None:
            self.cur_price_var.set(str(var_price))
            if not self.tgt_price_var.get().strip():
                self.tgt_price_var.set(str(int(var_price * 0.95)))

        var_stock = item.get("stock") or self.inspected_data.get("detected_stock", "")
        if var_stock:
            self.status_lbl.config(text=f"Выбран вариант: {item.get('label')}. {var_stock}", fg="#1e293b")

        img_url = item.get("image_candidates") or item.get("image_url") or self.inspected_data.get("default_image", "")
        self.load_preview_async(img_url)

    def load_preview_async(self, img_url):
        self.preview_lbl.config(image="", text="Загрузка...")
        def worker():
            pil_im = download_image_pil(img_url, 98, 128)
            def done():
                if pil_im and HAS_PIL and self.preview_lbl.winfo_exists():
                    tk_img = ImageTk.PhotoImage(pil_im)
                    self.current_preview_tk = tk_img
                    self.preview_lbl.config(image=tk_img, text="")
                elif self.preview_lbl.winfo_exists():
                    self.preview_lbl.config(image="", text="Нет фото")
            self.win.after(0, done)
        threading.Thread(target=worker, daemon=True).start()

    def submit(self):
        if not self.inspected_data or not self.selected_variant:
            self.status_lbl.config(text="Сначала укажите ссылку и выберите вариант товара.", fg=COLOR_WARNING)
            return

        cur_raw = self.cur_price_var.get().strip()
        tgt_raw = self.tgt_price_var.get().strip()

        cur_digits = re.sub(r'[^\d]', '', cur_raw)
        tgt_digits = re.sub(r'[^\d]', '', tgt_raw)

        if not tgt_digits:
            self.status_lbl.config(text="Укажите желаемую цену покупки (не выше которой готовы купить).", fg=COLOR_WARNING)
            self.tgt_price_entry.focus_set()
            return

        target_price = int(tgt_digits)
        current_price = int(cur_digits) if cur_digits else target_price

        v_item = self.selected_variant
        d = self.inspected_data
        mp = d.get("marketplace", "")
        url = v_item.get("url") or self.url_var.get().strip()
        variant_name = v_item.get("variant_name") or v_item.get("label", "")
        art = v_item.get("nm") or parse_target_url(url)[1] or "0"

        chosen_img = v_item.get("image_url") or d.get("default_image", "")
        chosen_cands = v_item.get("image_candidates") or ([chosen_img] if chosen_img else [])
        stock_val = v_item.get("stock") or d.get("detected_stock", "")

        item = {
            "id": f"{mp.lower()}_{art}_{int(time.time())}",
            "marketplace": mp,
            "url": url,
            "title": d.get("title", ""),
            "variant": variant_name,
            "image_url": chosen_img,
            "image_candidates": chosen_cands,
            "target_price": target_price,
            "current_price": current_price,
            "stock": stock_val,
            "status": "Готово к покупке" if current_price <= target_price else "Отслеживается",
            "last_checked": datetime.now().strftime("%H:%M:%S"),
            "notified": bool(current_price <= target_price)
        }

        self.on_added_cb(item)
        self.win.destroy()

class MacStatusBar:
    def __init__(self):
        self.status_item = None
        self.sb = None
        self.img_normal = None
        self.img_gold = None
        self.set_img_fn = None
        self.set_tip_fn = None
        self.tip_fn = None
        self.NSString = None
        self.objc = None
        self.appkit = None
        self.sel_set_image = None
        self.sel_set_tip = None
        self.sel_utf8 = None
        self.setup()

    def make_icon(self, is_gold):
        im = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if is_gold:
            d.ellipse([2, 2, 15, 15], fill=(235, 198, 86, 240), outline=(202, 160, 48, 255), width=2)
        else:
            d.ellipse([2, 2, 15, 15], outline=(0, 0, 0, 255), width=2)
        buf = io.BytesIO()
        im.save(buf, format="PNG")
        raw = buf.getvalue()

        data_sel = self.objc.sel_registerName(b"dataWithBytes:length:")
        data_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p, ctypes.c_size_t))
        nsdata = data_fn(self.NSData, data_sel, raw, len(raw))

        alloc_sel = self.objc.sel_registerName(b"alloc")
        alloc_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
        alloc_img = alloc_fn(self.NSImage, alloc_sel)

        init_sel = self.objc.sel_registerName(b"initWithData:")
        init_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
        nsimg = init_fn(alloc_img, init_sel, nsdata)

        tmpl_sel = self.objc.sel_registerName(b"setTemplate:")
        tmpl_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_bool))
        tmpl_fn(nsimg, tmpl_sel, not is_gold)

        ret_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
        ret_fn(nsimg, self.objc.sel_registerName(b"retain"))
        return nsimg

    def setup(self):
        if sys.platform != "darwin" or not HAS_PIL:
            return
        try:
            self.objc = ctypes.cdll.LoadLibrary(ctypes.util.find_library("objc"))
            self.appkit = ctypes.cdll.LoadLibrary(ctypes.util.find_library("AppKit"))
            self.objc.objc_getClass.restype = ctypes.c_void_p
            self.objc.objc_getClass.argtypes = [ctypes.c_char_p]
            self.objc.sel_registerName.restype = ctypes.c_void_p
            self.objc.sel_registerName.argtypes = [ctypes.c_char_p]

            self.NSData = self.objc.objc_getClass(b"NSData")
            self.NSImage = self.objc.objc_getClass(b"NSImage")
            self.NSString = self.objc.objc_getClass(b"NSString")
            NSStatusBar = self.objc.objc_getClass(b"NSStatusBar")

            self.img_normal = self.make_icon(is_gold=False)
            self.img_gold = self.make_icon(is_gold=True)

            sb_sel = self.objc.sel_registerName(b"systemStatusBar")
            send_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
            self.sb = send_fn(NSStatusBar, sb_sel)

            item_sel = self.objc.sel_registerName(b"statusItemWithLength:")
            item_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_double))
            self.status_item = item_fn(self.sb, item_sel, ctypes.c_double(-1.0))
            send_fn(self.status_item, self.objc.sel_registerName(b"retain"))

            self.sel_set_image = self.objc.sel_registerName(b"setImage:")
            self.sel_set_tip = self.objc.sel_registerName(b"setToolTip:")
            self.sel_utf8 = self.objc.sel_registerName(b"stringWithUTF8String:")

            self.set_img_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
            self.set_tip_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
            self.tip_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_char_p))

            NSApp = send_fn(self.objc.objc_getClass(b"NSApplication"), self.objc.sel_registerName(b"sharedApplication"))
            act_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
            act_fn(self.status_item, self.objc.sel_registerName(b"setTarget:"), NSApp)
            act_fn(self.status_item, self.objc.sel_registerName(b"setAction:"), self.objc.sel_registerName(b"unhide:"))

            self.update_status(0)
        except Exception:
            self.status_item = None

    def update_status(self, ready_count):
        if not self.status_item or not self.sb:
            return
        try:
            img = self.img_gold if ready_count > 0 else self.img_normal
            self.set_img_fn(self.status_item, self.sel_set_image, img)
            tip_text = f"Маркетплейс Трекер: {ready_count} товаров со скидкой!" if ready_count > 0 else "Маркетплейс Трекер"
            tip_obj = self.tip_fn(self.NSString, self.sel_utf8, tip_text.encode("utf-8"))
            self.set_tip_fn(self.status_item, self.sel_set_tip, tip_obj)
        except Exception:
            pass

    def cleanup(self):
        if self.sb and self.status_item:
            try:
                rem_sel = self.objc.sel_registerName(b"removeStatusItem:")
                rem_fn = ctypes.cast(self.objc.objc_msgSend, ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p))
                rem_fn(self.sb, rem_sel, self.status_item)
            except Exception:
                pass
            self.status_item = None

class App:
    def __init__(self, root):
        self.root = root
        self.items = []
        self.seconds_left = CHECK_INTERVAL_SEC
        self.is_checking = False
        self.card_thumbnails = {}
        self.drawer_expanded = False
        self.drawer_animating = False
        self.drawer_current_h = 0
        self.status_bar_mgr = MacStatusBar()

        self.root.title("Маркетплейс Трекер Цен (WB / Ozon)")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(680, 560)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup()
        self.load_items()
        self.start_timer()

        if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
            self.open_add_dialog(initial_url=sys.argv[1])

    def on_close(self):
        if self.status_bar_mgr:
            self.status_bar_mgr.cleanup()
        self.root.destroy()

    def setup(self):
        top_bar = tk.Frame(self.root, bg="#ffffff", padx=14, pady=10, relief="solid", bd=1)
        top_bar.pack(fill="x", side="top")

        actions_frame = tk.Frame(top_bar, bg="#ffffff")
        actions_frame.pack(side="right")

        self.add_btn = tk.Label(
            actions_frame, text="+ Добавить товар",
            bg=COLOR_GREEN, fg="white",
            relief="flat", cursor="hand2",
            font=("TkDefaultFont", 9, "bold"),
            width=17, pady=5, anchor="center"
        )
        self.add_btn.pack(side="left")
        self.add_btn.bind("<Button-1>", lambda _e: self.open_add_dialog())
        self.add_btn.bind("<Enter>", lambda _e: self.add_btn.config(bg=COLOR_GREEN_HOVER))
        self.add_btn.bind("<Leave>", lambda _e: self.add_btn.config(bg=COLOR_GREEN))

        self.refresh_btn = tk.Button(actions_frame, text="Проверить сейчас", width=16, command=self.manual_check)
        self.refresh_btn.pack(side="left", padx=(6, 0))

        title_lbl = tk.Label(top_bar, text="Мониторинг цен (WB & Ozon)", font=("TkDefaultFont", 12, "bold"), bg="#ffffff", fg="#0f172a")
        title_lbl.pack(side="left")

        status_bar = tk.Frame(self.root, bg="#f1f5f9", padx=14, pady=6)
        status_bar.pack(fill="x", side="top")

        self.count_lbl = tk.Label(status_bar, text="Отслеживается: 0 товаров", font=("TkDefaultFont", 9), bg="#f1f5f9", fg="#334155")
        self.count_lbl.pack(side="left")

        self.status_indicator = tk.Label(status_bar, text="", font=("TkDefaultFont", 9, "bold"), bg="#f1f5f9", fg=COLOR_GREEN)
        self.status_indicator.pack(side="right")

        ver_bar = tk.Frame(self.root, bg="#f1f5f9", padx=14, pady=3)
        ver_bar.pack(side="bottom", fill="x")
        tk.Label(ver_bar, text=f"Маркетплейс Трекер v{__version__} ({__license__})", font=("TkDefaultFont", 8), fg="#94a3b8", bg="#f1f5f9").pack(side="left")
        tk.Label(ver_bar, text=f"by {__author__}", font=("TkDefaultFont", 8), fg="#94a3b8", bg="#f1f5f9").pack(side="right")

        self.drawer_frame = tk.Frame(self.root, bg=COLOR_BG)
        self.drawer_frame.pack(side="bottom", fill="x")

        self.toggle_row = tk.Frame(self.drawer_frame, bg=COLOR_BG)
        self.toggle_row.pack(fill="x", pady=(2, 2))

        self.toggle_btn = tk.Label(
            self.toggle_row,
            text="▲  Поблагодарить",
            font=("TkDefaultFont", 9, "bold"),
            bg="#f1f5f9", fg="#334155",
            relief="solid", bd=1,
            cursor="hand2",
            padx=14, pady=3
        )
        self.toggle_btn.pack(anchor="center")
        self.toggle_btn.bind("<Button-1>", lambda _e: self.toggle_drawer())
        self.toggle_btn.bind("<Enter>", lambda _e: self.toggle_btn.config(bg="#e2e8f0"))
        self.toggle_btn.bind("<Leave>", lambda _e: self.toggle_btn.config(bg="#f1f5f9" if not self.drawer_expanded else "#e2e8f0"))

        self.anim_box = tk.Frame(self.drawer_frame, height=0, bg="#f8fafc")
        self.anim_box.pack_propagate(False)

        support_frame = tk.Frame(
            self.anim_box, bg="#f8fafc", padx=10, pady=8,
            highlightbackground="#cbd5e1", highlightcolor="#cbd5e1", highlightthickness=1
        )
        support_frame.pack(fill="both", expand=True, padx=10, pady=(0, 4))

        tk.Label(support_frame, text="Буду благодарен любой поддержке! <3", font=("TkDefaultFont", 10, "bold"), fg="#0f172a", bg="#f8fafc").pack(anchor="w", pady=(0, 2))

        support_row = tk.Frame(support_frame, bg="#f8fafc")
        support_row.pack(fill="x")

        support_left = tk.Frame(support_row, bg="#f8fafc")
        support_left.pack(side="left", fill="both", expand=True)

        tk.Label(
            support_left,
            text="Если программа вам полезна, вы можете поддержать проект или задать вопрос автору:",
            font=("TkDefaultFont", 9),
            fg="#475569",
            bg="#f8fafc",
            justify="left"
        ).pack(anchor="w")

        contacts_box = tk.Frame(support_left, bg="#f8fafc")
        contacts_box.pack(anchor="w", pady=(3, 3))

        tg_row = tk.Frame(contacts_box, bg="#f8fafc")
        tg_row.pack(anchor="w", pady=(0, 2))
        self.tg_img = get_tg_image(self.root)
        CACHED_IMAGES["tg"] = self.tg_img
        tg_lbl = tk.Label(tg_row, image=self.tg_img, bg="#f8fafc")
        tg_lbl.image = self.tg_img
        tg_lbl.pack(side="left", padx=(0, 5))
        tk.Label(tg_row, text="Связь с автором в Telegram:", font=("TkDefaultFont", 9), fg="#334155", bg="#f8fafc").pack(side="left", padx=(0, 4))
        tg_link = tk.Label(tg_row, text="@sudo_ai", font=("TkDefaultFont", 9, "bold"), fg="#2563eb", bg="#f8fafc", cursor="hand2")
        tg_link.pack(side="left")
        tg_link.bind("<Button-1>", lambda _e: webbrowser.open_new_tab("https://t.me/sudo_ai"))

        gh_row = tk.Frame(contacts_box, bg="#f8fafc")
        gh_row.pack(anchor="w", pady=(2, 0))
        self.gh_img = get_gh_image(self.root)
        CACHED_IMAGES["gh"] = self.gh_img
        gh_lbl = tk.Label(gh_row, image=self.gh_img, bg="#f8fafc")
        gh_lbl.image = self.gh_img
        gh_lbl.pack(side="left", padx=(0, 5))
        tk.Label(gh_row, text="Профиль на GitHub:", font=("TkDefaultFont", 9), fg="#334155", bg="#f8fafc").pack(side="left", padx=(0, 4))
        gh_link = tk.Label(gh_row, text="git-sudo-ai", font=("TkDefaultFont", 9, "bold"), fg="#2563eb", bg="#f8fafc", cursor="hand2")
        gh_link.pack(side="left")
        gh_link.bind("<Button-1>", lambda _e: webbrowser.open_new_tab("https://github.com/git-sudo-ai"))

        tk.Label(
            support_left,
            text="Перевод через СБП по QR-коду справа ➔",
            font=("TkDefaultFont", 8),
            fg="#64748b",
            bg="#f8fafc"
        ).pack(anchor="w", pady=(2, 0))

        self.qr_img = get_qr_image(self.root)
        CACHED_IMAGES["qr"] = self.qr_img
        qr_frame = tk.Frame(support_row, bg="#ffffff", padx=2, pady=2, highlightbackground="#cbd5e1", highlightcolor="#cbd5e1", highlightthickness=1)
        qr_frame.pack(side="right", padx=(8, 0))
        qr_lbl = tk.Label(qr_frame, image=self.qr_img, bg="#ffffff")
        qr_lbl.image = self.qr_img
        qr_lbl.pack()
        tk.Label(qr_frame, text="СБП", font=("TkDefaultFont", 7, "bold"), fg="#64748b", bg="#ffffff").pack()

        cards_container = tk.Frame(self.root, bg=COLOR_BG)
        cards_container.pack(fill="both", expand=True, padx=10, pady=6)

        self.canvas = tk.Canvas(cards_container, bg=COLOR_BG, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(cards_container, orient="vertical", command=self.canvas.yview)
        self.cards_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.cards_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

    def load_items(self):
        self.items = load_db()
        self.render_cards()

    def render_cards(self):
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        self.items.sort(key=lambda it: not is_product_ready(it))

        total = len(self.items)
        ready_count = 0

        if total == 0:
            if self.status_bar_mgr:
                self.status_bar_mgr.update_status(0)
            self.count_lbl.config(text="Отслеживается: 0 товаров")
            empty_box = tk.Frame(self.cards_frame, bg="#ffffff", padx=24, pady=32, relief="solid", bd=1)
            empty_box.pack(fill="x", padx=16, pady=32)
            tk.Label(empty_box, text="Список отслеживаемых товаров пуст", font=("TkDefaultFont", 11, "bold"), bg="#ffffff", fg="#334155").pack(pady=(0, 6))
            empty_lbl = tk.Label(
                empty_box,
                text="Нажмите «+ Добавить товар», вставьте ссылку на Wildberries или Ozon,\nвыберите вариант и задайте желаемую цену.",
                bg="#ffffff", fg="#64748b", justify="center", wraplength=480
            )
            empty_lbl.pack()
            empty_box.bind("<Configure>", lambda e: empty_lbl.config(wraplength=max(200, e.width - 48)))
            return

        for item in self.items:
            cur_p = item.get("current_price")
            target_p = item.get("target_price")
            is_ready = is_product_ready(item)
            if is_ready:
                ready_count += 1

            card_bg = COLOR_SUCCESS_BG if is_ready else "#ffffff"
            border_color = COLOR_SUCCESS_BORDER if is_ready else COLOR_CARD_BORDER

            card = tk.Frame(self.cards_frame, bg=card_bg, padx=12, pady=10, relief="solid", bd=1, highlightbackground=border_color, highlightthickness=1)
            card.pack(fill="x", padx=8, pady=6)

            card_inner = tk.Frame(card, bg=card_bg)
            card_inner.pack(fill="x")

            thumb_box = tk.Frame(card_inner, width=64, height=84, bg="#f1f5f9", relief="solid", bd=1)
            thumb_box.pack_propagate(False)
            thumb_box.pack(side="left", padx=(0, 12))

            thumb_lbl = tk.Label(thumb_box, text="Фото", bg="#f1f5f9", fg="#94a3b8")
            thumb_lbl.pack(fill="both", expand=True)

            img_cands = item.get("image_candidates") or item.get("image_url")
            if img_cands:
                self.load_card_thumbnail_async(item.get("id"), img_cands, thumb_lbl)

            info_box = tk.Frame(card_inner, bg=card_bg)
            info_box.pack(side="left", fill="both", expand=True)

            header_row = tk.Frame(info_box, bg=card_bg)
            header_row.pack(fill="x", pady=(0, 4))

            mp = item.get("marketplace", "")
            mp_color = COLOR_WB if mp == "Wildberries" else (COLOR_OZON if mp == "Ozon" else "#475569")
            mp_badge = tk.Label(header_row, text=f"[{mp}]", font=("TkDefaultFont", 9, "bold"), fg=mp_color, bg=card_bg)
            mp_badge.pack(side="left", padx=(0, 6))

            title_text = item.get("title", "Без названия")
            title_lbl = tk.Label(header_row, text=title_text, font=("TkDefaultFont", 10, "bold"), fg="#0f172a", bg=card_bg, anchor="w", justify="left")
            title_lbl.pack(side="left", fill="x", expand=True)

            var_val = item.get("variant", "")
            if var_val:
                var_badge = tk.Label(header_row, text=var_val, font=("TkDefaultFont", 8, "bold"), bg="#e2e8f0", fg="#1e293b", padx=6, pady=2)
                var_badge.pack(side="right")

            price_row = tk.Frame(info_box, bg=card_bg)
            price_row.pack(fill="x", pady=(2, 6))

            cur_txt = f"{cur_p:,} ₽".replace(",", " ") if cur_p is not None else "-"
            cur_color = "#15803d" if is_ready else "#1e293b"
            tk.Label(price_row, text=f"Текущая: {cur_txt}", font=("TkDefaultFont", 11, "bold"), fg=cur_color, bg=card_bg).pack(side="left", padx=(0, 16))

            tgt_txt = f"{target_p:,} ₽".replace(",", " ") if target_p is not None else "-"
            tk.Label(price_row, text=f"Цель: не выше {tgt_txt}", font=("TkDefaultFont", 9), fg="#475569", bg=card_bg).pack(side="left", padx=(0, 16))

            stock_val = item.get("stock", "")
            if stock_val:
                stock_color = "#dc2626" if "нет" in stock_val.lower() else "#475569"
                tk.Label(price_row, text=stock_val, font=("TkDefaultFont", 9), fg=stock_color, bg=card_bg).pack(side="left", padx=(0, 16))

            if is_ready:
                tk.Label(price_row, text="★ ЦЕЛЬ ДОСТИГНУТА! Пора покупать", font=("TkDefaultFont", 9, "bold"), fg="#166534", bg=card_bg).pack(side="left")

            actions_row = tk.Frame(info_box, bg=card_bg)
            actions_row.pack(fill="x", pady=(4, 0))

            if is_ready:
                site_btn = tk.Label(
                    actions_row, text="Перейти на сайт",
                    bg=COLOR_GREEN, fg="white",
                    relief="flat", cursor="hand2",
                    font=("TkDefaultFont", 9, "bold"),
                    padx=14, pady=5
                )
                site_btn.bind("<Enter>", lambda _e, b=site_btn: b.config(bg=COLOR_GREEN_HOVER))
                site_btn.bind("<Leave>", lambda _e, b=site_btn: b.config(bg=COLOR_GREEN))
            else:
                site_btn = tk.Label(
                    actions_row, text="Перейти на сайт",
                    bg="#f1f5f9", fg="#334155",
                    relief="solid", bd=1, cursor="hand2",
                    font=("TkDefaultFont", 9),
                    padx=14, pady=5
                )
                site_btn.bind("<Enter>", lambda _e, b=site_btn: b.config(bg="#e2e8f0"))
                site_btn.bind("<Leave>", lambda _e, b=site_btn: b.config(bg="#f1f5f9"))

            site_btn.pack(side="left", padx=(0, 8))
            site_btn.bind("<Button-1>", lambda _e, it=item: self.open_site(it))

            del_btn = tk.Label(
                actions_row, text="✕ Удалить",
                bg="#fee2e2", fg="#b91c1c",
                relief="solid", bd=1, cursor="hand2",
                font=("TkDefaultFont", 9),
                padx=10, pady=4
            )
            del_btn.pack(side="right")
            del_btn.bind("<Enter>", lambda _e, b=del_btn: b.config(bg="#fecaca"))
            del_btn.bind("<Leave>", lambda _e, b=del_btn: b.config(bg="#fee2e2"))
            del_btn.bind("<Button-1>", lambda _e, it=item: self.delete_item(it))

        status_text = f"Отслеживается: {total} позиций"
        if ready_count > 0:
            status_text += f" | Готовы к покупке: {ready_count}!"
            self.root.title(f"Маркетплейс Трекер ({ready_count} товаров готовы к покупке!)")
        else:
            self.root.title("Маркетплейс Трекер Цен (WB / Ozon)")
        self.count_lbl.config(text=status_text)
        if self.status_bar_mgr:
            self.status_bar_mgr.update_status(ready_count)

    def load_card_thumbnail_async(self, item_id, image_url, target_label):
        if item_id in self.card_thumbnails:
            target_label.config(image=self.card_thumbnails[item_id], text="")
            return

        def worker():
            pil_im = download_image_pil(image_url, 62, 82)
            def done():
                if pil_im and HAS_PIL and target_label.winfo_exists():
                    tk_img = ImageTk.PhotoImage(pil_im)
                    self.card_thumbnails[item_id] = tk_img
                    target_label.config(image=tk_img, text="")
            self.root.after(0, done)
        threading.Thread(target=worker, daemon=True).start()

    def toggle_drawer(self):
        if self.drawer_animating:
            return
        if self.drawer_expanded:
            self.collapse_drawer()
        else:
            self.expand_drawer()

    def expand_drawer(self):
        self.drawer_animating = True
        self.anim_box.pack(side="bottom", fill="x")
        self.toggle_btn.config(text="▼  Поблагодарить", bg="#e2e8f0")
        self.drawer_current_h = 0

        def _anim():
            self.drawer_current_h += DRAWER_ANIM_STEP
            if self.drawer_current_h >= DRAWER_TARGET_HEIGHT:
                self.anim_box.config(height=DRAWER_TARGET_HEIGHT)
                self.drawer_expanded = True
                self.drawer_animating = False
            else:
                self.anim_box.config(height=self.drawer_current_h)
                self.root.after(DRAWER_ANIM_DELAY_MS, _anim)

        self.root.after(DRAWER_ANIM_DELAY_MS, _anim)

    def collapse_drawer(self):
        self.drawer_animating = True
        self.toggle_btn.config(text="▲  Поблагодарить", bg="#f1f5f9")
        self.drawer_current_h = DRAWER_TARGET_HEIGHT

        def _anim():
            self.drawer_current_h -= DRAWER_ANIM_STEP
            if self.drawer_current_h <= 0:
                self.anim_box.config(height=0)
                self.anim_box.pack_forget()
                self.drawer_expanded = False
                self.drawer_animating = False
            else:
                self.anim_box.config(height=self.drawer_current_h)
                self.root.after(DRAWER_ANIM_DELAY_MS, _anim)

        self.root.after(DRAWER_ANIM_DELAY_MS, _anim)

    def open_site(self, item):
        url = item.get("url")
        if url:
            webbrowser.open_new_tab(url)

    def delete_item(self, item):
        item_id = item.get("id")
        self.items = [x for x in self.items if x.get("id") != item_id]
        save_db(self.items)
        self.render_cards()

    def add_item_callback(self, item):
        self.items.append(item)
        save_db(self.items)
        self.render_cards()

    def open_add_dialog(self, initial_url=""):
        dlg = AddWindow(self.root, self.add_item_callback)
        if initial_url:
            dlg.url_var.set(initial_url)
            dlg.trigger_inspect()

    def start_timer(self):
        def tick():
            if not self.is_checking:
                self.seconds_left -= 1
                if self.seconds_left <= 0:
                    self.seconds_left = CHECK_INTERVAL_SEC
                    self.run_background_check()
            self.root.after(1000, tick)
        self.root.after(1000, tick)

    def manual_check(self):
        if self.is_checking:
            return
        self.seconds_left = CHECK_INTERVAL_SEC
        self.run_background_check()

    def run_background_check(self):
        if self.is_checking or len(self.items) == 0:
            return
        self.is_checking = True
        self.refresh_btn.config(state="disabled")
        self.status_indicator.config(text="Идет проверка цен...", fg=COLOR_GREEN)

        def worker():
            notified_items = []
            for item in self.items:
                res = inspect_product(item["url"])
                if res:
                    item["last_checked"] = datetime.now().strftime("%H:%M:%S")
                    if res.get("title") and "Товар" not in res.get("title"):
                        item["title"] = res["title"]

                    var_p = None
                    var_stock = None
                    var_tgt = item.get("variant")
                    sku = item["id"].split("_")[1] if "_" in item.get("id", "") else ""
                    for vlist in res.get("categories", {}).values():
                        for v in vlist:
                            m_name = bool(var_tgt and (v.get("variant_name") == var_tgt or v.get("label") == var_tgt))
                            m_sku = bool(sku and str(v.get("nm")) == sku)
                            if m_name or m_sku:
                                if v.get("price") is not None:
                                    var_p = v["price"]
                                if v.get("stock"):
                                    var_stock = v["stock"]
                                break
                        if var_p is not None and var_stock:
                            break

                    new_p = var_p if var_p is not None else res.get("detected_price")
                    new_stock = var_stock if var_stock else res.get("detected_stock")

                    if new_stock:
                        item["stock"] = new_stock

                    if new_p is not None:
                        item["current_price"] = new_p
                        tgt = item.get("target_price")
                        if tgt is not None and new_p <= tgt:
                            item["status"] = "Готово к покупке"
                            if not item.get("notified", False):
                                item["notified"] = True
                                notified_items.append(item)
                        else:
                            item["status"] = "Отслеживается"
                            item["notified"] = False

            self.items.sort(key=lambda it: not is_product_ready(it))
            save_db(self.items)

            def update_ui():
                self.is_checking = False
                self.refresh_btn.config(state="normal")
                self.status_indicator.config(text="")
                self.render_cards()

                for n_item in notified_items:
                    t = n_item.get("title", "")
                    p = n_item.get("current_price", "")
                    tp = n_item.get("target_price", "")
                    msg = f"Цена на '{t[:35]}' снизилась до {p} ₽ (цель: {tp} ₽)!"
                    send_notification("Маркетплейс Трекер", msg)
                    try:
                        self.root.bell()
                    except Exception:
                        pass

            self.root.after(0, update_ui)

        threading.Thread(target=worker, daemon=True).start()

def main():
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    main()

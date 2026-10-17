import os
import sys
import re
import io
import json
import time
import socket
import base64
import threading
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urljoin, quote
import urllib.request
import urllib.error
import tkinter as tk
from tkinter import ttk
import platform
import shutil
import tempfile
import html as html_lib

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

__version__ = "2.2"
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
QR_CODE_DATA = "iVBORw0KGgoAAAANSUhEUgAAAFAAAABQCAAAAACreq1xAAAQJklEQVR42rVZeZxU1ZX+zr33varqvZulu4FGdpqlWQwIY1Ro0YlJ0BATl6j5kZgY/WUcjWaMiRoVRNGoySQ6SZwAipE4cVwAIzpBIooa4wayI9ACAXvf6Kruqvfevd/8UVXdrfHPmftH1bu3zjn3vHO/e7YSghafGEoBiPIzLZZKfZJGKVoYAM59klULhPi/HYbSsM0MXglPneFU8HyfgBTqC4re+HDq3K5NVAMUc6aeeKVose/Uzve9wazRmeOIkKs+tcctDNjRPzvIL+MK7v0Exd3cAN3JgLd8inUVQwPETWxE/s1FmpMFAPT8dlEdHeJiGpP2Dz1y1KDGo4CANPX2HE1OGKYBFJiiSuZZ+XEmDiDkE5iYCtKZTCaTyaTDhbibIV2Q6Y3uFQ/xI0xlfuvHITuCdBAEmXQwBwl/cSbtGPJuLAzznEFqIp5gaABAYrpfawEgEA9WazoAiGkVAEjkzaUQhc7Pk5r+A1ACAAYAGKlv7NdO3LDnCgmLd64pe7bcuUvO2r8UDndsOnvHwct4if7x1zbd4lk5ZJy8Oc9p+9B8CzL11VZFZWufjNgvECI7DgBAiRUA6PogFomHmppKgHhv+9SZ8RA7cERad+a06XobQCsAiH37JACkRTAgEChUygmLcouqKLKr94pr1lrhX+tnByUPMhbVI+5ri2smrH912nes5+qgAEhRUqhcYR6HuW/n4IQ54NOxVK9+GwBSwJe+BFTfmEVgAOC68c1/GXNdv8HhnHDgzuQFiohIlgAAgmfK5o4+vLt8npfA3/7uKVosKKY5ZbEX4eWdvGD0s7F6Az/PChH5lMCAFkSQ0xCppfjzuQ9dN34jHO56AQCwrwI46ywAsz64b8OmL8fb/CjPStg8a7/A6jbtxFXm9xHjTjSmKotPYGhsdLVnhdLR5JAosa2obi6yunpYY2FJFnMjjaKy1YMFCt2zTgCqhMuJtLwOVx16tzb+3uj7V4oQXHTQS39t7bHT0i/O8FT9/o4zOzeebSEu8XqW1XEAhxJDcT88c4eEHrAokcwQufPrOAn0gt1hogTw/ehkKgKglMqzxvoFmqb6gbu8xwCCwseH3/KmR+fFHVa8dOENDd/CfaMe3BiLrIn6wt89eeayvpinALN70cBdbjJZgX1R99bBLiMJwFtU7IVJicIwwrY3RkjydayZWBoGpgIs8/a9Ll55GwMko+bmwax9gFGYe5unxTJ/HpmzobVKFlw5fwHG3ulX2Kvnzofnozc4v0bd0eX0Q6OGLOPtWOZq8UUvluOiaCI8DQr8jLEZXvMnV3YDH5F8Jst9P19DAT97GErjjuLT1LsnFQEQyo4fX7Gg1GMEpRm59/okHDWtsB7vHhpXkzYFs7Vh+i9vmfL2UtENBzwHASiuZA4ArYCQa1GT4cQBQ9w+eMOwEsA3GZGT8Rs+ifEk+QMAwzoZ8KcDXFPzGgJGFQDVrdpBXA9LxXShhCknLp6Ikpm4KkUF6BhT6VQS7I2HXmGZdAIAfGUiKdbJUDm/G3CFftZjTwrY+nFjY2Pr7lL9TPNPh389aq8dOmLIbdHfKqti+G1jmw2jcApKq8vU2GQURh2Nf9AjOmyGy+Hrku0t52kPXlXViOH/nfPYAIbmIGNHDkdLoy5s7gT6tG6GwogqQAEK3d1AqhBAOaptskgZAJFLjS9W1iJsAtCd99ihXH/Yz5x+e8Gf7KMr5mw8/pWoTzz+qaF8U/i95uWrrQJwDMae8aOuC60l3OgNvZf33TELZsaK9JXJf/7++lWTfkkbzYFGyCcwmawFcA4tWYflfCtv6dHkmEExHN9mKvt4Hgm8wuU4ja4MW7kW8wcOBar7AZPSXlgEF+HqBndfcFN6TerCCc7VBGmlF9eGCsDaDuD9BzI3y7pmiY7dH97EN9/lDeOCnqKeNe9v1VHg1rZ9dapDyDW5vAQX0JLkPVhAjsS27I4j8FL2YQIAoIKcmXUF5ALcSTLnuKaQlVjD0AgqZ/siO1MiYGafDc0RL/O37jQ6oxN/NyacMeLwW1ZRMLniSKtGWTJe559o1FKyuTQwLuw60heK4fCa6nfCQhMD8lfvVHhYzBN+fx6FDbwHAI7x69mVvfwuPJzSR/KmrJNTuJVbssTX8T1A43GGBrCBABaeNplMaY8QYsNc5PaVn0qbBNLKk9404joEkFIuZiwgNgjDKK6cWOtocxFJWWycUldb+yFu2Ldk0kWv7t+9Z/eBx7KuR3Pqnre+Pbl+362csGf3v02uO3iv9oDLJw3fu2P//r0H5mDN5If379lz4GxoAam1AIZoOwpAY/SYQ8fS430AqMm/eOFYNB6rOmUsCsah9Vh8VIXtBo4fLxkHAEigs63qFABFWeUyCACjcc5/td5oiUfePOLHeorv3XXxV1JGibgowoFLow618qn9+OgyafPFzXui1INRq1+Z+WMH5WDoOUdt4SJnzP1D5kODJFu8XEQuIKfjVr4KAC/xlwNxGgDwK5J0nAtgASPLevg4kzbihbiZu4GmHLAj1w4IPz87sN5vzBdO93/XfZWAO05sU5pwEKEtv0gYzISlKCgVC0sAB0CUOEdx2P5Y11XGBlpnYXPcg4dHSFrgPS7DWSS5aFCSjrp+B+k4AwpfoiUXQWVv3BIAYwY8dufHJwggGXU0dZSmPihoMvHIUSfM0GE9R2R8/NhJkdROgaspBwBODjubgLABSVRWVO8lvZOoGjY54tG+0aVEyMdhAIMH+Qw0AKVRT2t5AX7INxA/xIugARGDRxiRZMibcT6bysTDLdwiGmJwPQMGk/szWGY/BhcdTgCVdYMKyoGAAG6gFHCOuUytfym7EPIJEwO0GTnt8l0vF2H1vmtwDrsXTv/DrmPhX03hofDIrl271ots2H/tlLq6urq66TMrTdnMKTHjmcrZ46Tw5T2LTPXUJWFvrVnH0ADpKAIsTpwYP71WY07tWADhqyydDhRHUZk5BUAVMWVial+/Ml1dAIDmZkAvMH7U2CjGdEcZwGic8XDnsujmCX98be/VPb24bcxfYaP4Y8kp7uWnyx7hst7vnrZ1XRLS6zw178pQZfNMQuBI/8AD6aUFpy/Z8nT79+VWfUYO2JkYjvOGAQOem0XAnRhHDsOj/AUA2clr8L1/iOsHIcAWPgoAH+dgc/jNdotHx3uXnXhDLOpHbd/d/HTkovqauRfXRunyrjgSnskInVP7nowEOpo1ufG1wi94W5uUt1eJds+3bVFDz9WMRAMhV2fV+gU3QQPvcFl2voEk2TcKj/MhANjHb+ffYDnXw+vhvMH3csZATPG1DhCzLkpCj8LRIZnRHmxz6CFUNDIWJSgd5Vs0FsTHpFsFGOF5x/rGDjlS6pny0ojuY6tRUjLS5iqfkI9Di3jyIJ/FiOa+c+J3p3vSzVWyyYXOOZfujVyY6u3tPTX26/Qa8ZRsTd8UW9J3ZHgiLj/JnEy3Vokv16aTpMtHPZAI4QCokng67WJGJyIqMQAQA2AMgCDjxeIMgYKYywTx4p4+wPN9RBED6FgsV2QYQKHmSWOjMVBoO0N+cO/IkM57IVq9TDmh9/iIO1/2IwDHvPsfnfm2dfLzI0ve2fVPJS8kIr1l3pyH/c0B1WvzpqwKlx656wsWIZ9Abdae66GAPXlAnJU1dhO/OGD580hyClZwQ9ZN3YPp2dD7AMaQpfhPhhKadVdM3On9suHrC5+7UAMX1zgNMOLQhHOi2W6LfcnWpdrWfrHj/rASC+c2bJRm51iSqLmEgkh2/EU6UcHF01y2Xs5wElbyaehBONiSVTSB5wcDuSGbypJpALhr4IdjQLL/UACUm0Q2nT99mBVK+EZfMjy0d+jpwWVNDc+NntnzOs4ootCT4vSGsbUTLZIXp99t2fdC6Jmz4u83iW2/QG0sOLWGeQ3n4FdcD62wPbthNV7gfZhNkt/At7gd2E+SPK4B3JNFyLlZd97IRQAmkFVYM5AfAt2dHQBwdESkKCctOjr7tNfK0At1HLEqdrU65VRbdcaPTIse4lqkF4bCwhYztNLPnGLDsbYEQMh1anKGp6qioUVKKVVcUV5eXlYiKKxIKK+ivLQ8gauY7mifW15RWl46tbGjuePHpZfaxpoyXymllC4vfaqrrb3b2q62TC7q9QK9LpkEAPTkNU6lANcBQAPwytHaCQAlVQBcd6eKdyZzhJ2IlwIASgHAaJy7qRjRmpMq68MFiL3/Iwlg7NeuCbzgO82eMGq4GiuqH3zRY+cCLa5+84eLwlAe+FwGYnqvbI341H/4Dl54yzn2Mwufbdk7tIwkxwNYygaghdfnlX+I2wDBX7PUo/AsV2Z/+A0D49QHT3+qNFsw7Cfhr3tFbzaBjrr1V6fblS0+lo98A9MvaltlYTee3K3F8aTdtmXCFT2Es772nPpe8XxohPzdp/pNPyHJyoH5U3w4/3gFWwdF/5f4Q0xh90i8yIehB4CdMIWzB5W37YVo2Z0KZNoQKggYFoXVZ3ohtPnwWBD11kcf9Khsu0NY9/m5JPFe2X4pnqH+p3RaFfNVQP9YhOV8EQD+/A+mvRaXMyLn5vPXrSTJVBUAYCY5Co/lA33GS+VaBMply/RCa1064ycASYfidAEiEwGwSYmVBGlTYNNIpkJF3UMoxrxCFw7rSuQLH1EX7tJOXOXrxQQgruT1ikL+/o55G2jNDc/FM5NeFRJw9sQ56VWzlv+2fm3T2T3f8qkAtkFFly8H9YvBEPS3whqbASDK9ztlZBmQaj4MAG0tQDEQgw9PxxswsnooSqrLk7Zt4OCGjgBQObjN4otyQn+gT1C48u3PrS+DWBjxA1/wLyf2mG0Xx5/Tv+reY95a4q1NLNt5yTcypu/6LuKpA9aDhDcusHlvMwsKgqpuLsRy/hkVfTwPP8qexTfhYwo5KtdiZU0+2T0f/06ShQOK/pqB6W/8Kkh/n1WFPy9v8RHYWLSud282LRvSUj8twpC0d/1RpT563l9ZdFC9hNC478jGjwyHX0YVnpYrHidmOBkAUNLFhVjOTVmxN5JkHIDCFHIifj+AoFcHpd8BL0IMcwYVjwA5K66duGGaAFA2U2sw8rZbHS7oOtwuADEzlojaPyqYrvZ1jarqgj/VhLqppWhCbOuQJjixIQRachV9NLB3Pe5mbvoAFMxHvBgeppCk5ZMY3cc5+BmfR1WSjiuxkKmhAASzBmvIjJfreVETgIuUkbSORDvtqD0TMhBSfGMSQNyIDYE+P/Sc0WFf3LdWKxPCSL5V9fGsQW1nE+HtpeWbhl27rUfDeFp+tuKPtx+vgw5WXHru3lgM68JV09K6c75W9tIDH0wreGb49zcvvW3fNP/FGqeQzWAPDvY2veg6jBB7PgSApMNIKY+SHwJoRnEpgNE4eQCwhwGkxh09iDHDEcXHtB9EGgDE/UPrfvbMxpfjixOvHFdOqL9SaOXQmx4g0ekTHKBgZcduY6GgwhkzWjbHvpx4raHucx0v6fOL+P/x5wI+4+8PWhhY9ncscx1bpQY6wJ8iVYoWWgD8L5Mvhqo523R9AAAAAElFTkSuQmCC"

def get_db_path():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, DB_FILE_NAME)

SETTINGS_FILE_NAME = "goods_search_db_settings.json"

def get_settings_path():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(app_dir, SETTINGS_FILE_NAME)

def load_settings():
    path = get_settings_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}

def save_settings(data):
    path = get_settings_path()
    tmp_path = path + ".tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except OSError:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

def get_skipped_version():
    path = get_db_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for it in data:
                        if it.get("id") == "__app_meta__":
                            return it.get("skipped_version")
        except Exception:
            pass
    settings = load_settings()
    return settings.get("skipped_version")

def set_skipped_version(version_str):
    path = get_db_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                meta_found = False
                for it in data:
                    if it.get("id") == "__app_meta__":
                        it["skipped_version"] = version_str
                        meta_found = True
                        break
                if not meta_found:
                    data.insert(0, {"id": "__app_meta__", "skipped_version": version_str})
                tmp_path = path + ".tmp"
                with open(tmp_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp_path, path)
        except Exception:
            pass
    settings = load_settings()
    settings["skipped_version"] = version_str
    save_settings(settings)

def load_db():
    path = get_db_path()
    if not os.path.exists(path):
        save_db([])
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return [it for it in data if it.get("id") != "__app_meta__"]
            return []
    except (json.JSONDecodeError, OSError):
        return []

def save_db(items):
    path = get_db_path()
    tmp_path = path + ".tmp"
    try:
        skipped = get_skipped_version()
        out_list = [x for x in items if x.get("id") != "__app_meta__"]
        if skipped:
            out_list.insert(0, {"id": "__app_meta__", "skipped_version": skipped})
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(out_list, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, path)
    except OSError:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass

def parse_version_tuple(v_str):
    if not v_str:
        return (0,)
    clean = re.sub(r"[^0-9.]", "", str(v_str))
    parts = [int(p) for p in clean.split(".") if p.isdigit()]
    return tuple(parts) if parts else (0,)

def fetch_remote_version():
    urls = [
        "https://raw.githubusercontent.com/git-sudo-ai/MarketTraker/main/MarketTracker.py",
        "https://raw.githubusercontent.com/git-sudo-ai/MarketTraker/main/MarketTrackerV2.py",
        "https://api.github.com/repos/git-sudo-ai/MarketTraker/releases/latest"
    ]
    for u in urls:
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "MarketTracker-App"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    txt = resp.read().decode("utf-8", errors="ignore")
                    if "tag_name" in txt:
                        try:
                            d = json.loads(txt)
                            tag = d.get("tag_name")
                            if tag:
                                return re.sub(r"[^0-9.]", "", tag)
                        except Exception:
                            pass
                    m = re.search(r"__version__\s*=\s*['\"]([^'\"]+)['\"]", txt)
                    if m:
                        return m.group(1).strip()
        except Exception:
            continue
    return None

def send_notification(title, message):
    if sys.platform == "darwin":
        clean_msg = message.replace('"', '\\"').replace("'", "")
        clean_title = title.replace('"', '\\"').replace("'", "")
        cmd = f'display notification "{clean_msg}" with title "{clean_title}" sound name "Glass"'
        try:
            subprocess.run(["osascript", "-e", cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError:
            pass
    elif sys.platform.startswith("linux"):
        cmd = shutil.which("notify-send")
        if cmd:
            try:
                subprocess.run([cmd, title, message], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

def run_hidden_subprocess(cmd, timeout=10):
    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=timeout,
        startupinfo=startupinfo,
        creationflags=creationflags
    )

def unshorten_url(url: str, max_hops: int = 5) -> str:
    current = url.strip()
    if not current.startswith(("http://", "https://")):
        if re.fullmatch(r'\d{5,12}', current):
            return f"https://www.wildberries.ru/catalog/{current}/detail.aspx"
        current = "https://" + current

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }
    null_target = "NUL" if sys.platform == "win32" else "/dev/null"

    for _ in range(max_hops):
        wb_m = re.search(r'/catalog/(\d+)', current) or re.search(r'[?&]card=(\d+)', current)
        oz_m = re.search(r'/product/(?:([^/]+)-)?(\d+)', current) or re.search(r'/context/detail/id/(\d+)', current)
        if (wb_m and ("wildberries" in current or "wb.ru" in current)) or oz_m:
            return current

        next_url = None

        try:
            from curl_cffi import requests as cffi_requests
            r = cffi_requests.get(current, impersonate="chrome120", timeout=5, allow_redirects=True)
            if r.url and r.url != current and r.url.startswith("http"):
                next_url = r.url
        except Exception:
            pass

        if not next_url:
            try:
                cmd = ["curl", "-s", "-D", "-", "-o", null_target, "-m", "4", "-A", headers["User-Agent"], current]
                res = run_hidden_subprocess(cmd, timeout=5)
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
                cmd = ["curl", "-s", "-L", "-m", "5", "-o", null_target, "-w", "%{url_effective}", "-A", headers["User-Agent"], current]
                res = run_hidden_subprocess(cmd, timeout=6)
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

def parse_binary_cookies(file_path):
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, "rb") as f:
            data = f.read()
        if data[:4] != b"cook":
            return []
        import struct
        num_pages = struct.unpack(">I", data[4:8])[0]
        page_sizes = [struct.unpack(">I", data[8+i*4:12+i*4])[0] for i in range(num_pages)]
        offset = 8 + num_pages * 4
        cookies = []
        for p_size in page_sizes:
            p_data = data[offset:offset+p_size]
            offset += p_size
            if p_data[:4] != bytes([0, 0, 1, 0]):
                continue
            num_cookies = struct.unpack("<I", p_data[4:8])[0]
            cookie_offsets = [struct.unpack("<I", p_data[8+i*4:12+i*4])[0] for i in range(num_cookies)]
            for c_off in cookie_offsets:
                c_size = struct.unpack("<I", p_data[c_off:c_off+4])[0]
                c_data = p_data[c_off:c_off+c_size]
                url_off = struct.unpack("<I", c_data[16:20])[0]
                name_off = struct.unpack("<I", c_data[20:24])[0]
                path_off = struct.unpack("<I", c_data[24:28])[0]
                val_off = struct.unpack("<I", c_data[28:32])[0]
                domain = c_data[url_off:].split(bytes([0]), 1)[0].decode("utf-8", errors="ignore")
                name = c_data[name_off:].split(bytes([0]), 1)[0].decode("utf-8", errors="ignore")
                path = c_data[path_off:].split(bytes([0]), 1)[0].decode("utf-8", errors="ignore")
                val = c_data[val_off:].split(bytes([0]), 1)[0].decode("utf-8", errors="ignore")
                if "ozon" in domain:
                    import Foundation
                    cookies.append({
                        Foundation.NSHTTPCookieName: name,
                        Foundation.NSHTTPCookieValue: val,
                        Foundation.NSHTTPCookieDomain: domain,
                        Foundation.NSHTTPCookiePath: path or "/",
                        Foundation.NSHTTPCookieSecure: "TRUE",
                    })
        return cookies
    except Exception:
        return []

if sys.platform == "darwin":
    try:
        import CoreFoundation
        import Foundation
        import AppKit
        import WebKit

        class OzonNavDelegate(Foundation.NSObject):
            def webView_didFinishNavigation_(self, wv, nav):
                self.wv = wv
                self.poll = 0
                self.check()

            def check(self):
                self.poll += 1
                self.wv.evaluateJavaScript_completionHandler_(
                    "document.documentElement.outerHTML",
                    self.handle_html
                )

            def handle_html(self, html, err):
                if html:
                    is_ready = False
                    tgt = getattr(self, "target_url", "")
                    if "wildberries" in tgt or "wb.ru" in tgt:
                        if "price-block__wallet-price" in html or "price-block__final-price" in html or "red-price" in html:
                            is_ready = True
                    else:
                        if "webPrice" in html or "state-webPrice" in html or "cardPrice" in html:
                            is_ready = True
                    if is_ready:
                        self.result["html"] = html
                        CoreFoundation.CFRunLoopStop(CoreFoundation.CFRunLoopGetMain())
                        return
                if self.poll < 35:
                    Foundation.NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
                        0.3, False, lambda t: self.check()
                    )
                else:
                    self.result["html"] = html
                    CoreFoundation.CFRunLoopStop(CoreFoundation.CFRunLoopGetMain())
    except Exception:
        pass

def fetch_ozon_headless_worker(url, prod_id):
    if sys.platform != "darwin":
        return None
    try:
        cookie_path = os.path.expanduser("~/Library/Containers/com.apple.Safari/Data/Library/Cookies/Cookies.binarycookies")
        cookie_props = parse_binary_cookies(cookie_path)
        store = WebKit.WKWebsiteDataStore.defaultDataStore().httpCookieStore()
        if cookie_props:
            for p in cookie_props:
                c = Foundation.NSHTTPCookie.cookieWithProperties_(p)
                store.setCookie_completionHandler_(c, None)

        result = {"html": None}
        delegate = OzonNavDelegate.alloc().init()
        delegate.result = result
        delegate.target_url = url

        config = WebKit.WKWebViewConfiguration.alloc().init()
        config.setWebsiteDataStore_(WebKit.WKWebsiteDataStore.defaultDataStore())
        wv = WebKit.WKWebView.alloc().initWithFrame_configuration_(
            AppKit.NSMakeRect(0, 0, 800, 600), config
        )
        wv.setNavigationDelegate_(delegate)
        wv.setCustomUserAgent_("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15")

        ns_url = Foundation.NSURL.URLWithString_(url)
        req = Foundation.NSURLRequest.requestWithURL_(ns_url)
        wv.loadRequest_(req)

        timer = Foundation.NSTimer.scheduledTimerWithTimeInterval_repeats_block_(
            12.0, False, lambda t: CoreFoundation.CFRunLoopStop(CoreFoundation.CFRunLoopGetMain())
        )
        CoreFoundation.CFRunLoopRun()
        timer.invalidate()
        return result["html"]
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

def parse_wb_html(html: str):
    if not html:
        return None
    m_wallet = re.search(r'class=[\'"][^\'"]*price-block__wallet-price[^\'"]*[\'"][^>]*>([^<]+)<', html) or \
               re.search(r'class=[\'"][^\'"]*red-price[^\'"]*[\'"][^>]*>([^<]+)<', html)
    if m_wallet:
        digs = re.sub(r'[^\d]', '', m_wallet.group(1))
        if digs and 10 <= int(digs) <= 10000000:
            return int(digs)

    m_final = re.search(r'class=[\'"][^\'"]*price-block__final-price[^\'"]*[\'"][^>]*>([^<]+)<', html) or \
              re.search(r'itemprop=[\'"]price[\'"][^>]*content=[\'"](\d+)[\'"]', html) or \
              re.search(r'content=[\'"](\d+)[\'"][^>]*itemprop=[\'"]price[\'"]', html)
    if m_final:
        digs = re.sub(r'[^\d]', '', m_final.group(1))
        if digs and 10 <= int(digs) <= 10000000:
            return int(digs)

    m_blk = re.search(r'class=[\'"][^\'"]*price-block[^\'"]*[\'"][^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
    if m_blk:
        m_r = re.search(r'(\d[\d\s\xa0]{0,8})\s*(?:₽|&nbsp;₽)', m_blk.group(1))
        if m_r:
            digs = re.sub(r'[^\d]', '', m_r.group(1))
            if digs and 10 <= int(digs) <= 10000000:
                return int(digs)

    m_any = re.search(r'(\d[\d\s\xa0]{1,8})\s*(?:₽|&nbsp;₽)', html)
    if m_any:
        digs = re.sub(r'[^\d]', '', m_any.group(1))
        if digs and 10 <= int(digs) <= 10000000:
            return int(digs)
    return None

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

    wb_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Origin": "https://www.wildberries.ru",
        "Referer": f"https://www.wildberries.ru/catalog/{nm}/detail.aspx"
    }

    if detected_price is None:
        vol = nm // 100000
        part = nm // 1000
        cand_bs = [b] if b else []
        for delta in (0, -1, 1, -2, 2):
            cb = (b or get_basket_number(nm)) + delta
            if 1 <= cb <= 30 and cb not in cand_bs:
                cand_bs.append(cb)
        for cur_b in cand_bs:
            ph_url = f"https://basket-{cur_b:02d}.wbbasket.ru/vol{vol}/part{part}/{nm}/info/price-history.json"
            try:
                req = urllib.request.Request(ph_url, headers=wb_headers)
                with urllib.request.urlopen(req, timeout=2.5) as resp:
                    if resp.status == 200:
                        ph_data = json.loads(resp.read().decode())
                        if isinstance(ph_data, list) and ph_data:
                            last_p = ph_data[-1].get("price", {}).get("RUB")
                            if last_p:
                                p_int = int(last_p)
                                detected_price = p_int // 100 if p_int > 500 else p_int
                                break
            except Exception:
                pass
            if detected_price is not None:
                break

    if detected_price is None:
        wb_api_urls = [
            f"https://card.wb.ru/cards/v2/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={nm}",
            f"https://card.wb.ru/cards/v1/detail?appType=1&curr=rub&dest=-1257786&spp=30&nm={nm}",
            f"https://card.wb.ru/cards/detail?appType=1&curr=rub&dest=-1255987&spp=30&nm={nm}"
        ]

        for api_u in wb_api_urls:
            raw_wb_text = None
            try:
                from curl_cffi import requests as cffi_requests
                wb_resp = cffi_requests.get(api_u, headers=wb_headers, impersonate="chrome120", timeout=6)
                if wb_resp.status_code == 200 and wb_resp.text:
                    raw_wb_text = wb_resp.text
            except Exception:
                pass
            if not raw_wb_text:
                try:
                    wb_req = urllib.request.Request(api_u, headers=wb_headers)
                    with urllib.request.urlopen(wb_req, timeout=5) as resp:
                        if resp.status == 200:
                            raw_wb_text = resp.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass
            if not raw_wb_text:
                try:
                    cmd = ["curl", "-s", "-m", "5", "-A", wb_headers["User-Agent"], "-H", "Origin: https://www.wildberries.ru", "-H", f"Referer: https://www.wildberries.ru/catalog/{nm}/detail.aspx", "-H", "Accept: */*", api_u]
                    res = run_hidden_subprocess(cmd, timeout=6)
                    if res.stdout and "products" in res.stdout:
                        raw_wb_text = res.stdout
                except Exception:
                    pass
            if raw_wb_text:
                try:
                    wb_json = json.loads(raw_wb_text)
                    wb_prods = wb_json.get("data", {}).get("products", [])
                    if wb_prods:
                        p_obj = wb_prods[0]
                        cand_p = p_obj.get("salePriceU") or p_obj.get("priceU")
                        if not cand_p:
                            for s_item in p_obj.get("sizes", []):
                                p_val = s_item.get("price")
                                if isinstance(p_val, dict):
                                    cand_p = p_val.get("total") or p_val.get("product") or p_val.get("basic")
                                elif isinstance(p_val, (int, float)):
                                    cand_p = p_val
                                if not cand_p:
                                    cand_p = s_item.get("salePriceU") or s_item.get("sum")
                                if cand_p:
                                    break
                        if cand_p:
                            p_int = int(cand_p)
                            detected_price = p_int // 100 if p_int > 500 else p_int
                            break
                except Exception:
                    pass

    wb_page_url = f"https://www.wildberries.ru/catalog/{nm}/detail.aspx"
    if detected_price is None:
        try:
            page_html = None
            try:
                from curl_cffi import requests as cffi_requests
                p_resp = cffi_requests.get(wb_page_url, headers=wb_headers, impersonate="chrome120", timeout=6)
                if p_resp.status_code == 200 and p_resp.text:
                    page_html = p_resp.text
            except Exception:
                pass
            if not page_html:
                try:
                    req = urllib.request.Request(wb_page_url, headers=wb_headers)
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        page_html = resp.read().decode("utf-8", errors="ignore")
                except Exception:
                    pass
            if not page_html:
                try:
                    cmd = ["curl", "-s", "-L", "-m", "6", "-A", wb_headers["User-Agent"], wb_page_url]
                    res = run_hidden_subprocess(cmd, timeout=8)
                    if res.stdout and len(res.stdout) > 500:
                        page_html = res.stdout
                except Exception:
                    pass
            if page_html:
                p_from_html = parse_wb_html(page_html)
                if p_from_html is not None:
                    detected_price = p_from_html
        except Exception:
            pass

    if detected_price is None:
        if sys.platform == "win32":
            wb_path = find_windows_browser()
            if wb_path:
                cdp_html = fetch_ozon_cdp(wb_path, wb_page_url)
                if not cdp_html:
                    cdp_html = fetch_ozon_headless_windows(wb_path, wb_page_url)
                if cdp_html:
                    p_from_cdp = parse_wb_html(cdp_html)
                    if p_from_cdp is not None:
                        detected_price = p_from_cdp
        elif sys.platform.startswith("linux"):
            lb_path = find_linux_browser()
            if lb_path:
                cdp_html = fetch_ozon_cdp(lb_path, wb_page_url)
                if not cdp_html:
                    cdp_html = fetch_ozon_headless_linux(lb_path, wb_page_url)
                if cdp_html:
                    p_from_cdp = parse_wb_html(cdp_html)
                    if p_from_cdp is not None:
                        detected_price = p_from_cdp
        elif sys.platform == "darwin":
            try:
                cur_script = os.path.abspath(__file__)
                res = subprocess.run(
                    [sys.executable, cur_script, "--fetch-wb-headless", wb_page_url, str(nm)],
                    capture_output=True,
                    text=True,
                    timeout=18
                )
                out = res.stdout
                if "__WB_JSON_START__" in out and "__WB_JSON_END__" in out:
                    raw_json = out.split("__WB_JSON_START__")[1].split("__WB_JSON_END__")[0].strip()
                    if raw_json and raw_json != "{}":
                        parsed_dict = json.loads(raw_json)
                        if parsed_dict and parsed_dict.get("detected_price"):
                            detected_price = parsed_dict["detected_price"]
            except Exception:
                pass

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
            var_p = detected_price if is_cur else None
            if not is_cur:
                try:
                    c_vol = c // 100000
                    c_part = c // 1000
                    c_ph = f"https://basket-{cb:02d}.wbbasket.ru/vol{c_vol}/part{c_part}/{c}/info/price-history.json"
                    c_req = urllib.request.Request(c_ph, headers=wb_headers)
                    with urllib.request.urlopen(c_req, timeout=1.5) as c_resp:
                        if c_resp.status == 200:
                            c_data = json.loads(c_resp.read().decode())
                            if isinstance(c_data, list) and c_data:
                                cp = c_data[-1].get("price", {}).get("RUB")
                                if cp:
                                    c_int = int(cp)
                                    var_p = c_int // 100 if c_int > 500 else c_int
                except Exception:
                    pass
            label = f"Арт. {c}" + (" (текущий)" if is_cur else "")
            color_variants.append({
                "label": label,
                "variant_name": f"Цвет / Арт: {c}",
                "nm": str(c),
                "url": f"https://www.wildberries.ru/catalog/{c}/detail.aspx",
                "image_url": cimg,
                "image_candidates": c_cands,
                "price": var_p,
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
    schema_price = None
    detected_stock = ""
    default_img = ""
    gallery_imgs = []
    categories = {}

    for s in re.findall(r'<script[^>]+type=[\'"]application/ld\+json[\'"][^>]*>(.*?)</script>', html, re.DOTALL):
        try:
            raw_s = html_lib.unescape(s.strip())
            d = json.loads(raw_s)
            items = d if isinstance(d, list) else [d]
            for it in items:
                if isinstance(it, dict) and it.get("@type") == "Product":
                    if not title and it.get("name"):
                        title = str(it["name"]).strip()
                    if not default_img and it.get("image"):
                        im = it["image"]
                        if isinstance(im, list) and im:
                            default_img = str(im[0])
                            gallery_imgs.extend([str(x) for x in im])
                        elif isinstance(im, str):
                            default_img = im
                    offers = it.get("offers")
                    if offers:
                        off_list = offers if isinstance(offers, list) else [offers]
                        for off in off_list:
                            if isinstance(off, dict):
                                p_val = off.get("price")
                                if p_val is not None and schema_price is None:
                                    try:
                                        p_clean = int(float(str(p_val).replace(",", ".").replace(" ", "")))
                                        if 10 <= p_clean <= 10000000:
                                            schema_price = p_clean
                                    except Exception:
                                        pass
                                avail = str(off.get("availability") or "")
                                if "InStock" in avail:
                                    detected_stock = "В наличии"
                                elif "OutOfStock" in avail:
                                    detected_stock = "Нет в наличии"
        except Exception:
            pass

    state_map = {}
    for m in re.finditer(r'data-widget="([^"]+)"[^>]*data-state=([\'"])(.*?)\2', html, re.DOTALL):
        state_map[m.group(1)] = html_lib.unescape(m.group(3))
    for m in re.finditer(r'data-state=([\'"])(.*?)\1[^>]*data-widget="([^"]+)"', html, re.DOTALL):
        state_map[m.group(3)] = html_lib.unescape(m.group(2))
    for m in re.finditer(r'id="state-([^"]+)"[^>]*data-state=([\'"])(.*?)\2', html, re.DOTALL):
        state_map[m.group(1)] = html_lib.unescape(m.group(3))

    fr_val = None
    fr_matches = re.findall(r'"sku":\s*"' + re.escape(str(prod_id)) + r'"[^}]*"freeRest":\s*(\d+)', html)
    if not fr_matches:
        fr_matches = re.findall(r'"freeRest":\s*(\d+)[^}]*"sku":\s*"' + re.escape(str(prod_id)) + r'"', html)
    if not fr_matches:
        fr_matches = re.findall(r'"freeRest":\s*(\d+)', html)
    if fr_matches:
        try:
            fr_val = int(fr_matches[0])
        except Exception:
            pass

    sn_m = re.search(r'"stockNumber":\s*\{\s*"text":\s*"([^"]+)"', html)
    sn_val = int(sn_m.group(1).strip()) if sn_m and sn_m.group(1).strip().isdigit() else None

    exact_count = fr_val if fr_val is not None else sn_val

    if exact_count is not None:
        if exact_count > 0:
            detected_stock = f"Остаток: {exact_count} шт."
        else:
            detected_stock = "Нет в наличии"
    elif not detected_stock:
        m_ost = re.search(r'(\d+)\s*(?:шт|единиц\w*|штук\w*)\s*осталось', html, re.IGNORECASE)
        if m_ost:
            detected_stock = f"Остаток: {m_ost.group(1)} шт."
        elif 'data-widget="webOutOfStock"' in html or '"isOutOfStock":true' in html:
            detected_stock = "Нет в наличии"
        elif 'schema.org/InStock' in html or '"availability":"http://schema.org/InStock"' in html:
            detected_stock = "В наличии"

    for k, v in state_map.items():
        if "webProductHeading" in k and not title:
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
                raw_card = wp.get("cardPrice") or wp.get("cardPriceDecimal") or wp.get("priceWithCard") or wp.get("priceWithOzonCard")
                raw_reg = wp.get("price") or wp.get("priceDecimal") or wp.get("finalPrice")
                if raw_card:
                    c_dig = re.sub(r'[^\d]', '', str(raw_card))
                    if c_dig and 10 <= int(c_dig) <= 10000000:
                        detected_price = int(c_dig)
                        break
                elif raw_reg and detected_price is None:
                    r_dig = re.sub(r'[^\d]', '', str(raw_reg))
                    if r_dig and 10 <= int(r_dig) <= 10000000:
                        detected_price = int(r_dig)
            except Exception:
                pass

    if detected_price is None:
        m_card = re.search(r'"(?:cardPrice|cardPriceDecimal|priceWithCard|priceWithOzonCard)":\s*"?(\d[\d\s]{1,8}(?:\.\d+)?)"?', html)
        if m_card:
            try:
                digits = int(float(re.sub(r'[^\d.]', '', m_card.group(1))))
                if 10 <= digits <= 10000000:
                    detected_price = digits
            except Exception:
                pass

    if detected_price is None and schema_price is not None:
        detected_price = schema_price

    for k, v in state_map.items():
        if "webGallery" in k:
            try:
                wg = json.loads(v)
                cov = wg.get("coverImage")
                if cov and not default_img:
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
        og_t = re.search(r'<meta[^>]+property=[\'"]og:title[\'"][^>]+content=[\'"](.*?)[\'"]', html) or \
               re.search(r'<meta[^>]+content=[\'"](.*?)[\'"][^>]+property=[\'"]og:title[\'"]', html) or \
               re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
        if og_t:
            raw_t = html_lib.unescape(og_t.group(1).strip())
            raw_t = re.sub(r'\s*[-|]\s*купить\s.*$', '', raw_t, flags=re.IGNORECASE)
            raw_t = re.sub(r'\s*[-|]\s*OZON.*$', '', raw_t, flags=re.IGNORECASE).strip()
            if raw_t and "похоже, нет соединения" not in raw_t.lower() and "доступ ограничен" not in raw_t.lower():
                title = raw_t

    if not default_img:
        og_i = re.search(r'<meta[^>]+property=[\'"]og:image[\'"][^>]+content=[\'"](.*?)[\'"]', html) or \
               re.search(r'<meta[^>]+content=[\'"](.*?)[\'"][^>]+property=[\'"]og:image[\'"]', html) or \
               re.search(r'<meta[^>]+name=[\'"]twitter:image[\'"][^>]+content=[\'"](.*?)[\'"]', html) or \
               re.search(r'<link[^>]+rel=[\'"]image_src[\'"][^>]+href=[\'"](.*?)[\'"]', html)
        if og_i:
            cand = html_lib.unescape(og_i.group(1).strip())
            if "logo" not in cand.lower():
                default_img = cand

    if not default_img and gallery_imgs:
        default_img = gallery_imgs[0]

    if not default_img:
        ozon_imgs = re.findall(r'https://(?:[a-z0-9-]+\.)?ozone\.ru/s3/multimedia-[^"\'\s>]+\.(?:jpg|jpeg|png|webp)', html)
        for im in ozon_imgs:
            if "logo" not in im.lower() and "warn" not in im.lower():
                default_img = im
                break

    if detected_price is None:
        p_matches = re.findall(r'(\d[\d\s]{1,8})\s*₽', html)
        for pm in p_matches:
            digits = int(re.sub(r'\s+', '', pm))
            if 50 <= digits <= 2000000:
                detected_price = digits
                break

    if detected_price is None:
        p_json = re.search(r'"(?:cardPrice|price|finalPrice|priceWithCard|priceWithOzonCard)":\s*"?(\d[\d\s]{1,8}(?:\.\d+)?)"?', html)
        if p_json:
            try:
                digits = int(float(re.sub(r'[^\d.]', '', p_json.group(1))))
                if 50 <= digits <= 2000000:
                    detected_price = digits
            except Exception:
                pass

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

OZON_CFFI_SESSION = None

def get_ozon_cffi_session():
    global OZON_CFFI_SESSION
    if OZON_CFFI_SESSION is None:
        try:
            from curl_cffi import requests as cffi_requests
            OZON_CFFI_SESSION = cffi_requests.Session()
        except Exception:
            return None
    return OZON_CFFI_SESSION

def fetch_ozon_curl_cffi(url):
    sess = get_ozon_cffi_session()
    if not sess:
        return None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1"
    }
    try:
        resp = sess.get(url, headers=headers, impersonate="chrome120", timeout=14)
        if resp.status_code == 200 and resp.text and len(resp.text) > 1000:
            if "Похоже, нет соединения" not in resp.text and "Antibot Challenge" not in resp.text:
                return resp.text
    except Exception:
        pass
    return None

def fetch_ozon_composer_api(url, prod_id):
    sess = get_ozon_cffi_session()
    if not sess:
        return None
    try:
        parsed = urlparse(url)
        rel_path = parsed.path
        if not rel_path.startswith("/product/"):
            rel_path = f"/product/{prod_id}/" if prod_id else rel_path
        api_url = f"https://www.ozon.ru/api/composer-api.bx/page/json/v2?url={quote(rel_path)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.ozon.ru/"
        }
        resp = sess.get(api_url, headers=headers, impersonate="chrome120", timeout=10)
        if resp.status_code == 200 and resp.text:
            data = json.loads(resp.text)
            ws = data.get("widgetStates", {})
            if ws:
                fake_html = ""
                for k, v in ws.items():
                    v_str = v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)
                    escaped_v = html_lib.escape(v_str, quote=True)
                    fake_html += f'<div data-widget="{k}" data-state="{escaped_v}"></div>\n'
                parsed = parse_ozon_html(fake_html, prod_id, url)
                if parsed and (parsed.get("detected_price") is not None or parsed.get("default_image")):
                    return parsed
    except Exception:
        pass
    return None

def find_windows_browser():
    if sys.platform != "win32":
        return None
    try:
        import winreg
        for exe in ("msedge.exe", "chrome.exe", "browser.exe"):
            for hive in (winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER):
                try:
                    with winreg.OpenKey(hive, rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{exe}") as k:
                        val, _ = winreg.QueryValueEx(k, "")
                        if val and os.path.exists(val):
                            return val
                except Exception:
                    pass
    except Exception:
        pass

    candidates = [
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMW6432", r"C:\Program Files"), r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Microsoft\Edge\Application\msedge.exe"),
        os.path.join(os.environ.get("PROGRAMFILES", r"C:\Program Files"), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("PROGRAMFILES(X86)", r"C:\Program Files (x86)"), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("PROGRAMW6432", r"C:\Program Files"), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Google\Chrome\Application\chrome.exe"),
        os.path.join(os.environ.get("LOCALAPPDATA", ""), r"Yandex\YandexBrowser\Application\browser.exe"),
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    for name in ("msedge", "chrome", "google-chrome", "browser"):
        f = shutil.which(name)
        if f:
            return f
    return None

def ws_handshake(sock, host, path):
    key = base64.b64encode(os.urandom(16)).decode()
    req = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"Origin: http://{host}\r\n\r\n"
    )
    sock.sendall(req.encode())
    resp = b""
    while b"\r\n\r\n" not in resp:
        chunk = sock.recv(1024)
        if not chunk:
            break
        resp += chunk
    return b"101 Switching Protocols" in resp

def ws_send(sock, msg_str):
    data = msg_str.encode("utf-8")
    l = len(data)
    mask = os.urandom(4)
    if l <= 125:
        header = bytes([0x81, 0x80 | l]) + mask
    elif l <= 65535:
        header = bytes([0x81, 0x80 | 126]) + l.to_bytes(2, "big") + mask
    else:
        header = bytes([0x81, 0x80 | 127]) + l.to_bytes(8, "big") + mask
    masked = bytes([data[i] ^ mask[i % 4] for i in range(l)])
    sock.sendall(header + masked)

def recv_exact(sock, n):
    buf = bytearray()
    while len(buf) < n:
        chunk = sock.recv(min(32768, n - len(buf)))
        if not chunk:
            break
        buf.extend(chunk)
    return bytes(buf)

def ws_recv_message(sock):
    msg_bytes = bytearray()
    while True:
        head = recv_exact(sock, 2)
        if len(head) < 2:
            return None
        b1, b2 = head[0], head[1]
        is_fin = bool(b1 & 0x80)
        is_masked = bool(b2 & 0x80)
        l = b2 & 0x7F
        if l == 126:
            len_b = recv_exact(sock, 2)
            if len(len_b) < 2:
                return None
            l = int.from_bytes(len_b, "big")
        elif l == 127:
            len_b = recv_exact(sock, 8)
            if len(len_b) < 8:
                return None
            l = int.from_bytes(len_b, "big")
        mask = recv_exact(sock, 4) if is_masked else b""
        payload = recv_exact(sock, l)
        if is_masked and mask:
            payload = bytes([payload[i] ^ mask[i % 4] for i in range(len(payload))])
        msg_bytes.extend(payload)
        if is_fin:
            break
    return msg_bytes.decode("utf-8", errors="ignore")

def cdp_call(sock, method, params=None, msg_id=1, timeout=5.0):
    cmd = {"id": msg_id, "method": method, "params": params or {}}
    ws_send(sock, json.dumps(cmd))
    start_t = time.time()
    while time.time() - start_t < timeout:
        raw = ws_recv_message(sock)
        if not raw:
            break
        try:
            d = json.loads(raw)
            if d.get("id") == msg_id:
                return d
        except Exception:
            pass
    return None

def fetch_ozon_cdp(browser_path, url):
    profile_dir = tempfile.mkdtemp(prefix="mt_br_")
    cmd = [
        browser_path,
        "--remote-debugging-port=0",
        f"--user-data-dir={profile_dir}",
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        "--window-size=1920,1080",
        "--lang=ru-RU,ru",
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "about:blank"
    ]

    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE
        creationflags = subprocess.CREATE_NO_WINDOW

    proc = None
    sock = None
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            startupinfo=startupinfo,
            creationflags=creationflags
        )

        port_file = os.path.join(profile_dir, "DevToolsActivePort")
        port = None
        for _ in range(35):
            time.sleep(0.15)
            if os.path.exists(port_file):
                try:
                    with open(port_file, "r", encoding="utf-8") as pf:
                        lines = [ln.strip() for ln in pf.readlines() if ln.strip()]
                        if len(lines) >= 1 and lines[0].isdigit():
                            port = int(lines[0])
                            break
                except Exception:
                    pass

        if not port:
            try:
                proc.terminate()
                proc.wait(1)
            except Exception:
                pass
            cmd_classic = list(cmd)
            cmd_classic[cmd_classic.index("--headless=new")] = "--headless"
            proc = subprocess.Popen(
                cmd_classic,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            for _ in range(35):
                time.sleep(0.15)
                if os.path.exists(port_file):
                    try:
                        with open(port_file, "r", encoding="utf-8") as pf:
                            lines = [ln.strip() for ln in pf.readlines() if ln.strip()]
                            if len(lines) >= 1 and lines[0].isdigit():
                                port = int(lines[0])
                                break
                    except Exception:
                        pass

        if not port:
            return None

        ws_url = None
        for _ in range(30):
            time.sleep(0.15)
            try:
                req = urllib.request.Request(f"http://127.0.0.1:{port}/json/list")
                with urllib.request.urlopen(req, timeout=1.5) as resp:
                    tabs = json.loads(resp.read().decode())
                    for t in tabs:
                        if t.get("type") == "page" and t.get("webSocketDebuggerUrl"):
                            ws_url = t["webSocketDebuggerUrl"]
                            break
                    if ws_url:
                        break
            except Exception:
                pass

        if not ws_url:
            try:
                req_new = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT")
                with urllib.request.urlopen(req_new, timeout=2.0) as resp:
                    t = json.loads(resp.read().decode())
                    ws_url = t.get("webSocketDebuggerUrl")
            except Exception:
                pass

        if not ws_url:
            return None

        parsed_ws = urlparse(ws_url)
        ws_host = parsed_ws.hostname or "127.0.0.1"
        ws_port = parsed_ws.port or port
        ws_path = parsed_ws.path + ("?" + parsed_ws.query if parsed_ws.query else "")

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(6.0)
        sock.connect((ws_host, ws_port))

        if not ws_handshake(sock, f"{ws_host}:{ws_port}", ws_path):
            return None

        cdp_call(sock, "Page.enable", msg_id=1, timeout=2.0)
        cdp_call(sock, "Runtime.enable", msg_id=2, timeout=2.0)
        cdp_call(sock, "Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined}); window.chrome = { runtime: {} }; Object.defineProperty(navigator, 'languages', {get: () => ['ru-RU', 'ru', 'en-US', 'en']}); Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});"
        }, msg_id=3, timeout=2.0)
        cdp_call(sock, "Page.navigate", {"url": url}, msg_id=4, timeout=3.0)

        is_wb = ("wildberries" in url or "wb.ru" in url)
        msg_id = 10
        for i in range(35):
            time.sleep(0.4)
            msg_id += 1
            res = cdp_call(sock, "Runtime.evaluate", {
                "expression": "document.documentElement.outerHTML"
            }, msg_id=msg_id, timeout=3.0)
            if res:
                val = res.get("result", {}).get("result", {}).get("value")
                if val:
                    if is_wb:
                        if ("price-block__wallet-price" in val or "price-block__final-price" in val or ("price-block" in val and "₽" in val)):
                            if "__wbaas" not in val or i > 12:
                                return val
                    else:
                        if ("webPrice" in val or "cardPrice" in val or "state-webPrice" in val or "schema.org/Product" in val or "webProductHeading" in val or "webGallery" in val):
                            if "Похоже, нет соединения" not in val and "Antibot Challenge" not in val and "Проверка безопасности" not in val:
                                return val
                    if i >= 20 and len(val) > 4000:
                        if "Похоже, нет соединения" not in val and "Antibot Challenge" not in val and "__wbaas" not in val:
                            return val
        return None
    except Exception:
        return None
    finally:
        if sock:
            try:
                sock.close()
            except Exception:
                pass
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        if profile_dir:
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass

def fetch_ozon_headless_windows(browser_path, url):
    profile_dir = tempfile.mkdtemp(prefix="mt_br_hw_")
    try:
        base_args = [
            browser_path,
            f"--user-data-dir={profile_dir}",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            "--lang=ru-RU,ru"
        ]
        try:
            cmd1 = base_args + ["--headless=new", "--timeout=8000", "--dump-dom", url]
            res1 = run_hidden_subprocess(cmd1, timeout=18)
            out1 = res1.stdout or ""
            if out1 and ("webPrice" in out1 or "cardPrice" in out1 or "schema.org/Product" in out1 or "ir.ozone.ru" in out1):
                return out1
        except Exception:
            pass
        try:
            cmd2 = base_args + ["--headless", "--virtual-time-budget=7000", "--dump-dom", url]
            res2 = run_hidden_subprocess(cmd2, timeout=18)
            out2 = res2.stdout or ""
            if out2 and ("webPrice" in out2 or "cardPrice" in out2 or "schema.org/Product" in out2 or "ir.ozone.ru" in out2):
                return out2
            if out2 and len(out2) > 1000 and "Похоже, нет соединения" not in out2 and "Antibot Challenge" not in out2:
                return out2
        except Exception:
            pass
        return None
    finally:
        if profile_dir:
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass

def find_linux_browser():
    if not sys.platform.startswith("linux"):
        return None
    candidates = [
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        "/snap/bin/google-chrome",
        "/var/lib/flatpak/exports/bin/org.chromium.Chromium",
        "/var/lib/flatpak/exports/bin/com.google.Chrome",
        "/usr/bin/microsoft-edge",
        "/usr/bin/microsoft-edge-stable",
        "/usr/bin/brave-browser",
        "/usr/bin/opera",
        "/usr/bin/vivaldi"
    ]
    for p in candidates:
        if p and os.path.exists(p):
            return p
    for name in (
        "google-chrome",
        "google-chrome-stable",
        "chromium",
        "chromium-browser",
        "microsoft-edge",
        "microsoft-edge-stable",
        "brave-browser",
        "opera",
        "vivaldi"
    ):
        f = shutil.which(name)
        if f:
            return f
    return None

def fetch_ozon_headless_linux(browser_path, url):
    profile_dir = tempfile.mkdtemp(prefix="mt_br_hl_")
    try:
        base_args = [
            browser_path,
            f"--user-data-dir={profile_dir}",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1920,1080",
            "--lang=ru-RU,ru"
        ]
        try:
            cmd1 = base_args + ["--headless=new", "--timeout=8000", "--dump-dom", url]
            res1 = run_hidden_subprocess(cmd1, timeout=18)
            out1 = res1.stdout or ""
            if out1 and ("webPrice" in out1 or "cardPrice" in out1 or "schema.org/Product" in out1 or "ir.ozone.ru" in out1):
                return out1
        except Exception:
            pass
        try:
            cmd2 = base_args + ["--headless", "--virtual-time-budget=7000", "--dump-dom", url]
            res2 = run_hidden_subprocess(cmd2, timeout=18)
            out2 = res2.stdout or ""
            if out2 and ("webPrice" in out2 or "cardPrice" in out2 or "schema.org/Product" in out2 or "ir.ozone.ru" in out2):
                return out2
            if out2 and len(out2) > 1000 and "Похоже, нет соединения" not in out2 and "Antibot Challenge" not in out2:
                return out2
        except Exception:
            pass
        return None
    finally:
        if profile_dir:
            try:
                shutil.rmtree(profile_dir, ignore_errors=True)
            except Exception:
                pass

def parse_ozon_from_ui_texts(texts, tab_title, prod_id, original_url):
    title = None
    detected_price = None
    detected_stock = ""
    default_img = ""
    gallery_imgs = []

    if tab_title:
        clean_t = tab_title
        for cut in ("Google Chrome", "Microsoft Edge", "Яндекс Браузер", "Mozilla Firefox", "Brave", "Opera"):
            clean_t = clean_t.replace(cut, "").strip()
        m_cut = re.search(r'(.*?)(?:\s+[\W_]+\s+(?:купить|интернет-магазине|OZON|Озон)|\s+(?:OZON|Озон))', clean_t, flags=re.IGNORECASE)
        if m_cut and len(m_cut.group(1).strip()) > 3:
            clean_t = m_cut.group(1).strip()
        clean_t = clean_t.rstrip("-| :").strip()
        clean_t = re.sub(r'\(\d+\)$', '', clean_t).strip()
        if clean_t and len(clean_t) > 3:
            title = clean_t

    card_price = None
    reg_price = None

    for i, t in enumerate(texts):
        if not t:
            continue
        if not title and len(t) > 10 and not any(ch in t for ch in ("₽", "руб", "Ozon", "Корзин", "Доставк", "Отзыв")):
            title = t
        if "ozone.ru" in t or "ozon.ru" in t:
            m_img = re.search(r'https://[^\s"]+(?:ozone|ozon)\.ru[^\s"]+', t)
            if m_img:
                img_u = m_img.group(0)
                if not default_img:
                    default_img = img_u
                gallery_imgs.append(img_u)

        target_str = t
        if t.strip() in ("₽", "руб", "руб.") and i > 0 and texts[i - 1]:
            target_str = texts[i - 1] + " " + t
        elif i + 1 < len(texts) and texts[i + 1].strip() in ("₽", "руб", "руб."):
            target_str = t + " " + texts[i + 1]

        if "₽" in target_str or "руб" in target_str:
            m_p = re.search(r'(\d[\d\s]*)\s*(?:₽|руб)', target_str)
            if m_p:
                p_digits = int(re.sub(r'\s+', '', m_p.group(1)))
                if 10 <= p_digits <= 10000000:
                    context_window = " ".join(texts[max(0, i - 2):min(len(texts), i + 3)]).lower()
                    if "c ozon" in context_window or "с ozon" in context_window or "ozon карт" in context_window or "озон карт" in context_window:
                        if card_price is None:
                            card_price = p_digits
                    elif reg_price is None:
                        reg_price = p_digits

        if not detected_stock:
            t_low = t.lower()
            if "в наличии" in t_low:
                detected_stock = "В наличии"
            elif "нет в наличии" in t_low or "закончился" in t_low or "распродано" in t_low:
                detected_stock = "Нет в наличии"
            elif "осталось" in t_low:
                m_ost = re.search(r'(\d+)\s*(?:шт|единиц|штук)', t_low)
                if m_ost:
                    detected_stock = f"Остаток: {m_ost.group(1)} шт."

    detected_price = card_price if card_price is not None else reg_price

    if not title:
        title = f"Товар Ozon #{prod_id}"

    categories = {
        "Вариант": [{
            "label": "Основной вариант",
            "variant_name": "Основной",
            "nm": str(prod_id),
            "url": original_url,
            "image_url": default_img,
            "image_candidates": gallery_imgs,
            "price": detected_price,
            "stock": detected_stock,
            "is_default": True
        }]
    }

    return {
        "marketplace": "Ozon",
        "title": title,
        "default_image": default_img,
        "image_candidates": gallery_imgs,
        "detected_price": detected_price,
        "detected_stock": detected_stock,
        "categories": categories
    }

def fetch_ozon_windows_tabs(resolved_url, prod_id, slug, allow_open_tab=True):
    for port in (9222, 9223, 9224, 9225):
        try:
            req = urllib.request.Request(f"http://127.0.0.1:{port}/json")
            with urllib.request.urlopen(req, timeout=0.8) as resp:
                tabs = json.loads(resp.read().decode())
                for t in tabs:
                    if t.get("type") == "page":
                        u = t.get("url") or ""
                        if (prod_id and str(prod_id) in u) or (resolved_url and resolved_url in u) or ("ozon.ru/product" in u and str(prod_id) in u):
                            ws_url = t.get("webSocketDebuggerUrl")
                            if ws_url:
                                parsed_host = urlparse(ws_url)
                                host = parsed_host.netloc or f"127.0.0.1:{port}"
                                path = parsed_host.path
                                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                sock.settimeout(3.0)
                                sock.connect((parsed_host.hostname or "127.0.0.1", parsed_host.port or port))
                                if ws_handshake(sock, host, path):
                                    cdp_call(sock, "Page.enable", msg_id=1, timeout=1.5)
                                    cdp_call(sock, "Runtime.enable", msg_id=2, timeout=1.5)
                                    eval_res = cdp_call(sock, "Runtime.evaluate", {
                                        "expression": "document.documentElement.outerHTML",
                                        "returnByValue": True
                                    }, msg_id=3, timeout=3.0)
                                    sock.close()
                                    if eval_res and "result" in eval_res and "value" in eval_res["result"]:
                                        h = eval_res["result"]["value"]
                                        if h:
                                            parsed = parse_ozon_html(h, prod_id, resolved_url)
                                            if parsed and (parsed.get("detected_price") is not None or parsed.get("default_image")):
                                                return parsed
        except Exception:
            pass

    def scan_uia():
        try:
            import uiautomation as auto
            root = auto.GetRootControl()
            b_wins = []
            for w in root.GetChildren():
                c = w.ClassName
                nm = (w.Name or "").lower()
                if c in ("Chrome_WidgetWin_1", "MozillaWindowClass", "ApplicationFrameWindow") or "ozon" in nm or "озон" in nm:
                    b_wins.append(w)

            for w in b_wins:
                w_title = w.Name or ""
                target_found = False
                matched_tab = None

                w_title_lower = w_title.lower()
                is_ozon_window = "ozon" in w_title_lower or "озон" in w_title_lower
                if is_ozon_window and (str(prod_id) in w_title or (slug and len(slug) >= 4 and slug[:15].lower() in w_title_lower)):
                    target_found = True

                for ctrl in w.GetChildren():
                    if ctrl.ControlType == auto.ControlType.TabControl:
                        for ti in ctrl.GetChildren():
                            if ti.ControlType == auto.ControlType.TabItemControl:
                                tn = ti.Name or ""
                                tn_lower = tn.lower()
                                if ("ozon" in tn_lower or "озон" in tn_lower) and (str(prod_id) in tn or (slug and len(slug) >= 4 and slug[:15].lower() in tn_lower)):
                                    target_found = True
                                    w_title = tn
                                    matched_tab = ti
                                    break
                    if target_found:
                        break

                edit = w.EditControl(searchDepth=8)
                if edit.Exists(0, 0):
                    ev = ""
                    try:
                        if hasattr(edit, "GetValuePattern"):
                            ev = edit.GetValuePattern().Value or ""
                    except Exception:
                        pass
                    if not ev:
                        try:
                            if hasattr(edit, "GetLegacyIAccessiblePattern"):
                                ev = edit.GetLegacyIAccessiblePattern().Value or ""
                        except Exception:
                            pass
                    if not ev:
                        ev = edit.Name or ""
                    if ev and (str(prod_id) in ev or (slug and len(slug) >= 4 and slug in ev) or (resolved_url and resolved_url in ev)):
                        target_found = True

                if not target_found and is_ozon_window:
                    target_found = True

                if target_found:
                    if matched_tab and hasattr(matched_tab, "Select"):
                        try:
                            matched_tab.Select()
                            time.sleep(0.1)
                        except Exception:
                            pass

                    doc_ctrl = w.DocumentControl(searchDepth=10)
                    scope = doc_ctrl if doc_ctrl.Exists(0, 0) else w
                    collected = []

                    def walk_controls(elem, depth=0):
                        if depth > 16 or len(collected) > 600:
                            return
                        nm = elem.Name
                        if nm:
                            collected.append(nm.strip())
                        if hasattr(elem, "ControlType") and elem.ControlType == auto.ControlType.ImageControl:
                            val = getattr(elem, "Value", "") or getattr(elem, "HelpText", "") or ""
                            if "ozone.ru" in val or "ozon.ru" in val or "cdn" in val:
                                collected.append(val.strip())
                        for child in elem.GetChildren():
                            walk_controls(child, depth + 1)

                    walk_controls(scope)
                    parsed_ui = parse_ozon_from_ui_texts(collected, w_title, prod_id, resolved_url)
                    if parsed_ui and (parsed_ui.get("detected_price") is not None or parsed_ui.get("title")):
                        return parsed_ui
        except Exception:
            pass
        return None

    def scan_enum_windows():
        try:
            import ctypes
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            enum_titles = []
            def enum_handler(hwnd, _l):
                if user32.IsWindowVisible(hwnd):
                    length = user32.GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buf = ctypes.create_unicode_buffer(length + 1)
                        user32.GetWindowTextW(hwnd, buf, length + 1)
                        cls_buf = ctypes.create_unicode_buffer(256)
                        user32.GetClassNameW(hwnd, cls_buf, 256)
                        cls_name = cls_buf.value
                        t_val = buf.value
                        t_low = t_val.lower()
                        if "ozon" in t_low or "озон" in t_low:
                            enum_titles.append(t_val)
                return True
            WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(WNDENUMPROC(enum_handler), 0)
            if enum_titles:
                for t in enum_titles:
                    if str(prod_id) in t or (slug and slug[:15].lower() in t.lower()):
                        parsed_enum = parse_ozon_from_ui_texts([], t, prod_id, resolved_url)
                        if parsed_enum and parsed_enum.get("title"):
                            return parsed_enum
                parsed_enum = parse_ozon_from_ui_texts([], enum_titles[0], prod_id, resolved_url)
                if parsed_enum and parsed_enum.get("title"):
                    return parsed_enum
        except Exception:
            pass
        return None

    res = scan_uia()
    if res and (res.get("detected_price") is not None or res.get("title")):
        return res

    res = scan_enum_windows()
    if res and (res.get("detected_price") is not None or res.get("title")):
        return res

    if allow_open_tab:
        try:
            webbrowser.open_new_tab(resolved_url)
            for _ in range(8):
                time.sleep(0.5)
                res = scan_uia()
                if res and (res.get("detected_price") is not None or res.get("title")):
                    return res
                res = scan_enum_windows()
                if res and (res.get("detected_price") is not None or res.get("title")):
                    return res
        except Exception:
            pass

    return None

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

    cffi_html = fetch_ozon_curl_cffi(resolved_url)
    if cffi_html:
        parsed_cffi = parse_ozon_html(cffi_html, prod_id, resolved_url)
        if parsed_cffi and (parsed_cffi.get("detected_price") is not None or parsed_cffi.get("default_image")):
            return parsed_cffi

    api_parsed = fetch_ozon_composer_api(resolved_url, prod_id)
    if api_parsed and (api_parsed.get("detected_price") is not None or api_parsed.get("default_image")):
        return api_parsed

    if sys.platform == "darwin":
        try:
            cur_script = os.path.abspath(__file__)
            res = subprocess.run(
                [sys.executable, cur_script, "--fetch-ozon-headless", resolved_url, prod_id],
                capture_output=True,
                text=True,
                timeout=18
            )
            out = res.stdout
            if "__OZON_JSON_START__" in out and "__OZON_JSON_END__" in out:
                raw_json = out.split("__OZON_JSON_START__")[1].split("__OZON_JSON_END__")[0].strip()
                if raw_json and raw_json != "{}":
                    parsed_dict = json.loads(raw_json)
                    if parsed_dict and (parsed_dict.get("detected_price") is not None or parsed_dict.get("default_image")):
                        return parsed_dict
        except Exception:
            pass
    elif sys.platform == "win32":
        tab_parsed = fetch_ozon_windows_tabs(resolved_url, prod_id, slug, allow_open_tab=True)
        if tab_parsed and (tab_parsed.get("detected_price") is not None or tab_parsed.get("title") or tab_parsed.get("default_image")):
            return tab_parsed
    elif sys.platform.startswith("linux"):
        lb_path = find_linux_browser()
        if lb_path:
            linux_html = fetch_ozon_cdp(lb_path, resolved_url)
            if not linux_html:
                linux_html = fetch_ozon_headless_linux(lb_path, resolved_url)
            if linux_html:
                parsed_linux = parse_ozon_html(linux_html, prod_id, resolved_url)
                if parsed_linux and (parsed_linux.get("detected_price") is not None or parsed_linux.get("default_image")):
                    return parsed_linux

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }

    try:
        req = urllib.request.Request(resolved_url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            html = resp.read().decode(errors="ignore")
            if html:
                parsed_u = parse_ozon_html(html, prod_id, resolved_url)
                if parsed_u and (parsed_u.get("detected_price") is not None or parsed_u.get("default_image")):
                    return parsed_u
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

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
        "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8"
    }
    for u in urls:
        if not u.startswith("http"):
            continue
        cur_headers = dict(headers)
        if "ozone.ru" in u or "ozon" in u:
            cur_headers["Referer"] = "https://www.ozon.ru/"
            cur_headers["Origin"] = "https://www.ozon.ru"
        elif "wbbasket" in u or "wildberries" in u:
            cur_headers["Referer"] = "https://www.wildberries.ru/"
            cur_headers["Origin"] = "https://www.wildberries.ru"
        try:
            req = urllib.request.Request(u, headers=cur_headers)
            with urllib.request.urlopen(req, timeout=4) as resp:
                data = resp.read()
                im = Image.open(io.BytesIO(data))
                im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                return im
        except Exception:
            pass
        try:
            from curl_cffi import requests as cffi_requests
            r = cffi_requests.get(u, headers=cur_headers, impersonate="chrome120", timeout=5)
            if r.status_code == 200 and r.content:
                im = Image.open(io.BytesIO(r.content))
                im.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                return im
        except Exception:
            pass
        try:
            startupinfo = None
            creationflags = 0
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            cmd = ["curl", "-s", "-L", "-m", "5", "-A", cur_headers["User-Agent"]]
            if "Referer" in cur_headers:
                cmd.extend(["-H", f"Referer: {cur_headers['Referer']}"])
            cmd.append(u)
            res = subprocess.run(cmd, capture_output=True, timeout=6, startupinfo=startupinfo, creationflags=creationflags)
            if res.stdout:
                im = Image.open(io.BytesIO(res.stdout))
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
    def __init__(self, parent, on_added_cb, item_to_edit=None):
        self.win = tk.Toplevel(parent)
        self.item_to_edit = item_to_edit
        self.win.title("Редактировать товар" if item_to_edit else "Добавить товар в отслеживание")
        self.win.geometry(ADD_WINDOW_SIZE)
        self.win.minsize(580, 500)
        self.win.transient(parent)
        self.on_added_cb = on_added_cb

        self.inspected_data = None
        self.selected_variant = None
        self.current_preview_tk = None
        self.variant_buttons = {}
        self.last_clipboard = ""
        self.target_price_locked = bool(item_to_edit)

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
        tk.Label(p_row2, text="рублей", font=("TkDefaultFont", 8), bg="#ffffff", fg="#64748b").pack(side="left", padx=(6, 0))

        def _on_cur_price(*_args):
            if getattr(self, "target_price_locked", False):
                return
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

        self.variants_canvas = tk.Canvas(self.variants_outer, bg="#ffffff", highlightthickness=0, height=140, yscrollincrement=1)
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

        btn_txt = "Сохранить изменения" if self.item_to_edit else "Добавить в отслеживание"
        self.add_btn = tk.Label(
            bottom_row, text=btn_txt,
            bg=COLOR_GREEN, fg="white",
            relief="flat", cursor="hand2",
            font=("TkDefaultFont", 9, "bold"),
            padx=14, pady=6
        )
        self.add_btn.pack(side="right")
        self.add_btn.bind("<Button-1>", lambda _e: self.submit())
        self.add_btn.bind("<Enter>", lambda _e: self.add_btn.config(bg=COLOR_GREEN_HOVER))
        self.add_btn.bind("<Leave>", lambda _e: self.add_btn.config(bg=COLOR_GREEN))

        try:
            self.win.bind("<TouchpadScroll>", self.on_touchpad_scroll, add="+")
        except Exception:
            pass
        self.win.bind("<MouseWheel>", self.on_mousewheel, add="+")
        self.win.bind("<Button-4>", self.on_mousewheel_up, add="+")
        self.win.bind("<Button-5>", self.on_mousewheel_down, add="+")

        if not self.item_to_edit:
            self.check_clipboard()
            self.start_clipboard_monitor()
        else:
            self.url_var.set(self.item_to_edit.get("url", ""))
            self.tgt_price_var.set(str(self.item_to_edit.get("target_price", "")))
            self.target_price_locked = True
            self.trigger_inspect()

    def _is_in_variants_area(self, event):
        if not hasattr(self, "variants_canvas") or not self.variants_canvas.winfo_exists():
            return False
        widget = getattr(event, "widget", None)
        if widget:
            try:
                if widget.winfo_toplevel() != self.win:
                    return False
            except Exception:
                pass
            if hasattr(self, "variants_scroll") and widget == self.variants_scroll:
                return False
            curr = widget
            while curr:
                if curr in (self.variants_inner, self.variants_canvas):
                    return True
                curr = getattr(curr, "master", None)
        try:
            vx = self.variants_canvas.winfo_rootx()
            vy = self.variants_canvas.winfo_rooty()
            vw = self.variants_canvas.winfo_width()
            vh = self.variants_canvas.winfo_height()
            return (vx <= event.x_root <= vx + vw) and (vy <= event.y_root <= vy + vh)
        except Exception:
            return False

    def on_touchpad_scroll(self, event):
        if not self._is_in_variants_area(event):
            return
        try:
            yv = self.variants_canvas.yview()
            if yv[0] <= 0.0 and yv[1] >= 1.0:
                return
            delta = getattr(event, "delta", 0)
            if not delta:
                return
            low = delta & 0xffff
            delta_y = low if low < 0x8000 else low - 0x10000
            if delta_y != 0:
                step = -delta_y if sys.platform == "darwin" else delta_y
                self.variants_canvas.yview_scroll(step, "units")
        except Exception:
            pass

    def on_mousewheel(self, event):
        if not self._is_in_variants_area(event):
            return
        try:
            yv = self.variants_canvas.yview()
            if yv[0] <= 0.0 and yv[1] >= 1.0:
                return
            delta = getattr(event, "delta", 0)
            if not delta:
                return
            if abs(delta) >= 120:
                step = -1 * int(delta / 120) * 30
            else:
                step = -1 * int(delta) * 30
                if step == 0:
                    step = -30 if delta > 0 else 30
            if sys.platform == "darwin":
                step = -step
            self.variants_canvas.yview_scroll(step, "units")
        except Exception:
            pass

    def on_mousewheel_up(self, event):
        if not self._is_in_variants_area(event):
            return
        try:
            self.variants_canvas.yview_scroll(-30, "units")
        except Exception:
            pass

    def on_mousewheel_down(self, event):
        if not self._is_in_variants_area(event):
            return
        try:
            self.variants_canvas.yview_scroll(30, "units")
        except Exception:
            pass

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
                if not self.win.winfo_exists():
                    return
                self.check_btn.config(state="normal")
                if not data and self.item_to_edit:
                    it = self.item_to_edit
                    fallback_data = {
                        "marketplace": it.get("marketplace", "WB"),
                        "title": it.get("title", ""),
                        "default_image": it.get("image_url", ""),
                        "image_candidates": it.get("image_candidates", []),
                        "detected_price": it.get("current_price"),
                        "detected_stock": it.get("stock", ""),
                        "categories": {
                            "Текущий выбор": [{
                                "label": it.get("variant") or "Выбранный вариант",
                                "variant_name": it.get("variant") or "Основной",
                                "nm": parse_target_url(it.get("url", ""))[1] or "",
                                "url": it.get("url", ""),
                                "image_url": it.get("image_url", ""),
                                "image_candidates": it.get("image_candidates", []),
                                "price": it.get("current_price"),
                                "stock": it.get("stock", ""),
                                "is_default": True
                            }]
                        }
                    }
                    data_to_use = fallback_data
                else:
                    data_to_use = data
                if not data_to_use:
                    self.status_lbl.config(text="Не удалось получить данные о товаре. Проверьте ссылку.", fg=COLOR_WARNING)
                    return
                if resolved and resolved != url and resolved.startswith("http"):
                    self.url_var.set(resolved)
                self.inspected_data = data_to_use
                self.render_inspected_data()
            self.win.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def render_inspected_data(self):
        if not self.win.winfo_exists():
            return
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
        matched_var = None

        if self.item_to_edit:
            cur_vname = str(self.item_to_edit.get("variant", "")).strip().lower()
            cur_url = str(self.item_to_edit.get("url", "")).strip()
            _, cur_art, _ = parse_target_url(cur_url)
            for cat_name, items in categories.items():
                for it in items:
                    it_vname = str(it.get("variant_name") or it.get("label", "")).strip().lower()
                    it_nm = str(it.get("nm", "")).strip()
                    it_url = str(it.get("url", "")).strip()
                    if cur_vname and (it_vname == cur_vname or cur_vname in it_vname or it_vname in cur_vname):
                        matched_var = (it, cat_name)
                        break
                    if cur_art and it_nm and cur_art == it_nm:
                        matched_var = (it, cat_name)
                        break
                    if cur_url and it_url and cur_url == it_url:
                        matched_var = (it, cat_name)
                        break
                if matched_var:
                    break

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

        if matched_var:
            self.select_variant(matched_var[0], matched_var[1])
        elif default_var:
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
            self.status_lbl.config(text="Укажите желаемую цену покупки.", fg=COLOR_WARNING)
            self.tgt_price_entry.focus_set()
            return

        target_price = int(tgt_digits)
        current_price = int(cur_digits) if cur_digits else None
        is_ready = bool(current_price is not None and current_price <= target_price)

        v_item = self.selected_variant
        d = self.inspected_data
        mp = d.get("marketplace", "")
        url = v_item.get("url") or self.url_var.get().strip()
        variant_name = v_item.get("variant_name") or v_item.get("label", "")
        art = v_item.get("nm") or parse_target_url(url)[1] or "0"

        chosen_img = v_item.get("image_url") or d.get("default_image", "")
        chosen_cands = v_item.get("image_candidates") or ([chosen_img] if chosen_img else [])
        stock_val = v_item.get("stock") or d.get("detected_stock", "")

        if self.item_to_edit:
            self.item_to_edit["url"] = url
            if d.get("title"):
                self.item_to_edit["title"] = d.get("title")
            self.item_to_edit["variant"] = variant_name
            self.item_to_edit["image_url"] = chosen_img
            self.item_to_edit["image_candidates"] = chosen_cands
            self.item_to_edit["target_price"] = target_price
            self.item_to_edit["current_price"] = current_price
            self.item_to_edit["stock"] = stock_val
            self.item_to_edit["status"] = "Готово к покупке" if is_ready else "Отслеживается"
            self.item_to_edit["last_checked"] = datetime.now().strftime("%H:%M:%S")
            self.item_to_edit["notified"] = is_ready
            self.on_added_cb(self.item_to_edit)
            self.win.destroy()
            return

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
            "status": "Готово к покупке" if is_ready else "Отслеживается",
            "last_checked": datetime.now().strftime("%H:%M:%S"),
            "notified": is_ready
        }

        self.on_added_cb(item)
        self.win.destroy()

class MacStatusBar:
    def __init__(self, root=None):
        self.root = root
        self.status_item = None
        self.sb = None
        self.img_normal = None
        self.img_gold = None
        self.img_blank = None
        self.set_img_fn = None
        self.set_tip_fn = None
        self.tip_fn = None
        self.NSString = None
        self.objc = None
        self.appkit = None
        self.sel_set_image = None
        self.sel_set_tip = None
        self.sel_utf8 = None
        self.blink_timer_id = None
        self.is_blinking = False
        self.blink_visible = True
        self.ready_count = 0
        self.setup()

    def make_icon(self, mode):
        im = Image.new("RGBA", (18, 18), (0, 0, 0, 0))
        d = ImageDraw.Draw(im)
        if mode == "gold":
            d.ellipse([2, 2, 15, 15], fill=(235, 198, 86, 240), outline=(202, 160, 48, 255), width=2)
        elif mode == "normal":
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
        tmpl_fn(nsimg, tmpl_sel, mode == "normal")

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

            self.img_normal = self.make_icon("normal")
            self.img_gold = self.make_icon("gold")
            self.img_blank = self.make_icon("blank")

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
        self.ready_count = ready_count
        try:
            tip_text = f"Маркетплейс Трекер: {ready_count} товаров со скидкой!" if ready_count > 0 else "Маркетплейс Трекер"
            tip_obj = self.tip_fn(self.NSString, self.sel_utf8, tip_text.encode("utf-8"))
            self.set_tip_fn(self.status_item, self.sel_set_tip, tip_obj)

            if ready_count > 0:
                if not self.is_blinking:
                    self.is_blinking = True
                    self.blink_visible = True
                    self.set_img_fn(self.status_item, self.sel_set_image, self.img_gold)
                    self.schedule_blink()
            else:
                self.stop_blinking()
                self.set_img_fn(self.status_item, self.sel_set_image, self.img_normal)
        except Exception:
            pass

    def schedule_blink(self):
        if self.blink_timer_id and self.root:
            try:
                self.root.after_cancel(self.blink_timer_id)
            except Exception:
                pass
            self.blink_timer_id = None
        if self.is_blinking and self.root:
            try:
                self.blink_timer_id = self.root.after(1000, self._blink_tick)
            except Exception:
                pass

    def _blink_tick(self):
        self.blink_timer_id = None
        if not self.is_blinking or not self.status_item or not self.sb:
            return
        try:
            self.blink_visible = not self.blink_visible
            img = self.img_gold if self.blink_visible else self.img_blank
            self.set_img_fn(self.status_item, self.sel_set_image, img)
        except Exception:
            pass
        self.schedule_blink()

    def stop_blinking(self):
        self.is_blinking = False
        self.blink_visible = True
        if self.blink_timer_id and self.root:
            try:
                self.root.after_cancel(self.blink_timer_id)
            except Exception:
                pass
            self.blink_timer_id = None

    def cleanup(self):
        self.stop_blinking()
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
        settings = load_settings()
        init_min = str(settings.get("interval_min", 4))
        self.interval_var = tk.StringVar(value=init_min)
        self.seconds_left = int(init_min) * 60 if init_min.isdigit() and int(init_min) > 0 else CHECK_INTERVAL_SEC
        self.is_checking = False
        self.card_thumbnails = {}
        self.drawer_expanded = False
        self.drawer_animating = False
        self.drawer_current_h = 0
        self.status_bar_mgr = MacStatusBar(self.root)

        self.root.title("Маркетплейс Трекер Цен (WB / Ozon)")
        self.root.geometry(DEFAULT_WINDOW_SIZE)
        self.root.minsize(700, 560)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.setup()
        self.load_items()
        self.start_timer()
        self.check_github_updates_async()

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

        interval_box = tk.Frame(actions_frame, bg="#ffffff")
        interval_box.pack(side="left", padx=(12, 0))

        tk.Label(interval_box, text="Проверка каждые", font=("TkDefaultFont", 9), bg="#ffffff", fg="#475569").pack(side="left", padx=(0, 4))
        self.interval_entry = tk.Entry(interval_box, textvariable=self.interval_var, width=3, justify="center", font=("TkDefaultFont", 9))
        self.interval_entry.pack(side="left")
        tk.Label(interval_box, text="мин.", font=("TkDefaultFont", 9), bg="#ffffff", fg="#475569").pack(side="left", padx=(4, 0))

        def _validate_interval(P):
            return len(P) <= 4 and (P == "" or P.isdigit())
        vcmd = (self.root.register(_validate_interval), "%P")
        self.interval_entry.config(validate="key", validatecommand=vcmd)

        def _on_interval_change(*_args):
            sec = self.get_check_interval_seconds()
            if self.seconds_left > sec:
                self.seconds_left = sec
            val_str = self.interval_var.get().strip()
            if val_str.isdigit() and int(val_str) > 0:
                save_settings({"interval_min": int(val_str)})
        self.interval_var.trace_add("write", _on_interval_change)

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
        self.cards_container = cards_container

        self.canvas = tk.Canvas(cards_container, bg=COLOR_BG, highlightthickness=0, yscrollincrement=1)
        self.scrollbar = ttk.Scrollbar(cards_container, orient="vertical", command=self.canvas.yview)
        self.cards_frame = tk.Frame(self.canvas, bg=COLOR_BG)

        self.cards_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.cards_frame, anchor="nw")
        self.canvas.configure(xscrollcommand=None, yscrollcommand=self.scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        try:
            self.root.bind_all("<TouchpadScroll>", self.on_touchpad_scroll, add="+")
        except Exception:
            pass
        self.root.bind_all("<MouseWheel>", self.on_mousewheel, add="+")
        self.root.bind_all("<Button-4>", self.on_mousewheel_up, add="+")
        self.root.bind_all("<Button-5>", self.on_mousewheel_down, add="+")

    def _is_in_cards_area(self, event):
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists():
            return False
        widget = getattr(event, "widget", None)
        if widget:
            try:
                if widget.winfo_toplevel() != self.root:
                    return False
            except Exception:
                pass
            if hasattr(self, "scrollbar") and widget == self.scrollbar:
                return False
            curr = widget
            while curr:
                if curr in (self.cards_frame, self.canvas):
                    return True
                curr = getattr(curr, "master", None)
        try:
            cx = self.canvas.winfo_rootx()
            cy = self.canvas.winfo_rooty()
            cw = self.canvas.winfo_width()
            ch = self.canvas.winfo_height()
            return (cx <= event.x_root <= cx + cw) and (cy <= event.y_root <= cy + ch)
        except Exception:
            return False

    def on_touchpad_scroll(self, event):
        if not self._is_in_cards_area(event):
            return
        try:
            yv = self.canvas.yview()
            if yv[0] <= 0.0 and yv[1] >= 1.0:
                return
            delta = getattr(event, "delta", 0)
            if not delta:
                return
            low = delta & 0xffff
            delta_y = low if low < 0x8000 else low - 0x10000
            if delta_y != 0:
                step = -delta_y if sys.platform == "darwin" else delta_y
                self.canvas.yview_scroll(step, "units")
        except Exception:
            pass

    def on_mousewheel(self, event):
        if not self._is_in_cards_area(event):
            return
        try:
            yv = self.canvas.yview()
            if yv[0] <= 0.0 and yv[1] >= 1.0:
                return
            delta = getattr(event, "delta", 0)
            if not delta:
                return
            if abs(delta) >= 120:
                step = -1 * int(delta / 120) * 40
            else:
                step = -1 * int(delta) * 40
                if step == 0:
                    step = -40 if delta > 0 else 40
            if sys.platform == "darwin":
                step = -step
            self.canvas.yview_scroll(step, "units")
        except Exception:
            pass

    def on_mousewheel_up(self, event):
        if not self._is_in_cards_area(event):
            return
        try:
            self.canvas.yview_scroll(-40, "units")
        except Exception:
            pass

    def on_mousewheel_down(self, event):
        if not self._is_in_cards_area(event):
            return
        try:
            self.canvas.yview_scroll(40, "units")
        except Exception:
            pass

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

            edit_btn = tk.Label(
                actions_row, text="Редактировать",
                bg="#f1f5f9", fg="#334155",
                relief="solid", bd=1, cursor="hand2",
                font=("TkDefaultFont", 9),
                padx=14, pady=5
            )
            edit_btn.pack(side="left", padx=(0, 8))
            edit_btn.bind("<Enter>", lambda _e, b=edit_btn: b.config(bg="#e2e8f0"))
            edit_btn.bind("<Leave>", lambda _e, b=edit_btn: b.config(bg="#f1f5f9"))
            edit_btn.bind("<Button-1>", lambda _e, it=item: self.open_edit_dialog(it))

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
            try:
                self.root.after(0, done)
            except Exception:
                pass
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

    def edit_item_callback(self, item):
        item_id = item.get("id")
        if item_id in self.card_thumbnails:
            del self.card_thumbnails[item_id]
        save_db(self.items)
        self.render_cards()

    def open_edit_dialog(self, item):
        AddWindow(self.root, self.edit_item_callback, item_to_edit=item)

    def open_add_dialog(self, initial_url=""):
        dlg = AddWindow(self.root, self.add_item_callback)
        if initial_url:
            dlg.url_var.set(initial_url)
            dlg.trigger_inspect()

    def get_check_interval_seconds(self):
        try:
            val_str = self.interval_var.get().strip()
            if val_str.isdigit():
                val = int(val_str)
                if val > 0:
                    return val * 60
        except Exception:
            pass
        return CHECK_INTERVAL_SEC

    def start_timer(self):
        def tick():
            if not self.is_checking:
                self.seconds_left -= 1
                if self.seconds_left <= 0:
                    self.seconds_left = self.get_check_interval_seconds()
                    self.run_background_check()
            self.root.after(1000, tick)
        self.root.after(1000, tick)

    def run_background_check(self):
        if self.is_checking or len(self.items) == 0:
            return
        self.is_checking = True
        try:
            self.status_indicator.config(text="Проверяю цены...")
        except Exception:
            pass

        def worker():
            notified_items = []
            try:
                for idx, item in enumerate(self.items):
                    if idx > 0:
                        time.sleep(1.2)
                    res = inspect_product(item["url"])
                    if res:
                        item["last_checked"] = datetime.now().strftime("%H:%M:%S")
                        if res.get("title") and "Товар" not in res.get("title"):
                            item["title"] = res["title"]

                        if not item.get("image_url") and res.get("default_image"):
                            item["image_url"] = res["default_image"]
                        if not item.get("image_candidates") and res.get("image_candidates"):
                            item["image_candidates"] = res["image_candidates"]

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

                        if res.get("detected_stock") and "остаток" in res.get("detected_stock").lower():
                            new_stock = res.get("detected_stock")
                        elif var_stock and "остаток" in var_stock.lower():
                            new_stock = var_stock
                        else:
                            new_stock = res.get("detected_stock") or var_stock

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
            except Exception:
                pass
            finally:
                def update_ui():
                    self.is_checking = False
                    try:
                        self.status_indicator.config(text="")
                    except Exception:
                        pass
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

    def check_github_updates_async(self):
        def worker():
            try:
                remote_v = fetch_remote_version()
                if not remote_v:
                    return
                if parse_version_tuple(remote_v) <= parse_version_tuple(__version__):
                    return
                skipped = get_skipped_version()
                if skipped and parse_version_tuple(remote_v) <= parse_version_tuple(skipped):
                    return
                self.root.after(0, lambda: self.show_update_dialog(remote_v))
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

    def show_update_dialog(self, remote_ver):
        win = tk.Toplevel(self.root)
        win.title("Обновление приложения")
        win.configure(bg="#ffffff")
        win.resizable(False, False)
        win.transient(self.root)

        w, h = 460, 200
        try:
            rx = self.root.winfo_rootx()
            ry = self.root.winfo_rooty()
            rw = self.root.winfo_width()
            rh = self.root.winfo_height()
            x = rx + max(0, (rw - w) // 2)
            y = ry + max(0, (rh - h) // 2)
            win.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            win.geometry(f"{w}x{h}")

        card = tk.Frame(win, bg="#ffffff", padx=20, pady=16)
        card.pack(fill="both", expand=True)

        tk.Label(
            card,
            text=f"Доступно обновление: v{remote_ver}",
            font=("TkDefaultFont", 12, "bold"),
            fg="#0f172a", bg="#ffffff"
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            card,
            text=f"Текущая версия программы: v{__version__}. Рекомендуется обновить приложение для стабильной работы и новых функций.",
            font=("TkDefaultFont", 9),
            fg="#475569", bg="#ffffff",
            wraplength=410, justify="left"
        ).pack(anchor="w", pady=(0, 18))

        btn_bar = tk.Frame(card, bg="#ffffff")
        btn_bar.pack(fill="x", side="bottom")

        def on_yes():
            win.destroy()
            webbrowser.open_new_tab("https://github.com/git-sudo-ai/MarketTraker")

        def on_skip():
            set_skipped_version(remote_ver)
            win.destroy()

        btn_download = tk.Label(
            btn_bar,
            text="Скачать",
            font=("TkDefaultFont", 9, "bold"),
            bg="#16a34a", fg="#ffffff",
            padx=18, pady=6,
            cursor="hand2", relief="flat"
        )
        btn_download.pack(side="right", padx=(8, 0))
        btn_download.bind("<Button-1>", lambda _e: on_yes())
        btn_download.bind("<Enter>", lambda _e: btn_download.config(bg="#15803d"))
        btn_download.bind("<Leave>", lambda _e: btn_download.config(bg="#16a34a"))

        btn_skip = tk.Label(
            btn_bar,
            text="Пропустить версию",
            font=("TkDefaultFont", 9),
            bg="#f1f5f9", fg="#475569",
            padx=14, pady=5,
            cursor="hand2", relief="solid", bd=1
        )
        btn_skip.pack(side="right")
        btn_skip.bind("<Button-1>", lambda _e: on_skip())
        btn_skip.bind("<Enter>", lambda _e: btn_skip.config(bg="#e2e8f0"))
        btn_skip.bind("<Leave>", lambda _e: btn_skip.config(bg="#f1f5f9"))

def get_missing_dependencies():
    missing = []
    try:
        import PIL
    except ImportError:
        missing.append({
            "name": "Pillow",
            "package": "pillow",
            "desc": "Отображение фотографий товаров, галереи и иконок приложения"
        })
    if sys.platform == "darwin":
        has_webkit = False
        try:
            import WebKit
            import Foundation
            import AppKit
            import CoreFoundation
            has_webkit = True
        except ImportError:
            pass
        if not has_webkit:
            missing.append({
                "name": "WebKit для macOS",
                "package": "pyobjc-framework-WebKit",
                "desc": "Фоновая проверка цен Ozon без открытия реального окна браузера"
            })
    elif sys.platform == "win32":
        has_uiauto = False
        try:
            import uiautomation
            has_uiauto = True
        except ImportError:
            pass
        if not has_uiauto:
            missing.append({
                "name": "UIAutomation (для вкладок браузера)",
                "package": "uiautomation",
                "desc": "Необязательный компонент для проверки цен Ozon через открытые вкладки в браузере (Chrome, Edge, Яндекс Браузер)",
                "optional": True
            })
        has_curl_cffi = False
        try:
            import curl_cffi
            has_curl_cffi = True
        except ImportError:
            pass
        if not has_curl_cffi:
            missing.append({
                "name": "curl_cffi",
                "package": "curl_cffi",
                "desc": "Необязательный модуль для быстрого скачивания картинок и проверки цен товаров",
                "optional": True
            })
    elif sys.platform.startswith("linux"):
        has_curl_cffi = False
        try:
            import curl_cffi
            has_curl_cffi = True
        except ImportError:
            pass
        if not has_curl_cffi:
            missing.append({
                "name": "curl_cffi",
                "package": "curl_cffi",
                "desc": "Модуль для фоновой проверки цен и фото товаров Ozon и Wildberries на Linux"
            })
    return missing

def show_dependency_dialog(missing_deps):
    root = tk.Tk()
    root.title("Установка компонентов")
    root.configure(bg="#f8fafc")
    root.resizable(False, False)

    w, h = 540, 480
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws - w) // 2
    y = (hs - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    card = tk.Frame(root, bg="#ffffff", highlightbackground="#e2e8f0", highlightthickness=1)
    card.pack(fill="both", expand=True, padx=16, pady=16)

    all_optional = all(item.get("optional", False) for item in missing_deps)

    top_frame = tk.Frame(card, bg="#ffffff")
    top_frame.pack(fill="x", padx=20, pady=(18, 10))

    title_text = "Дополнительные компоненты (необязательно)" if all_optional else "Необходима разовая настройка"
    title_lbl = tk.Label(
        top_frame,
        text=title_text,
        font=("SF Pro Display", 16, "bold"),
        bg="#ffffff",
        fg="#0f172a"
    )
    title_lbl.pack(anchor="w")

    subtitle_text = "Для расширенной работы с вкладками браузера доступны компоненты. Вы можете установить их автоматически или пропустить." if all_optional else "Для полноценной работы программы требуются дополнительные компоненты. Программа может установить их автоматически."
    subtitle_lbl = tk.Label(
        top_frame,
        text=subtitle_text,
        font=("SF Pro Text", 11),
        bg="#ffffff",
        fg="#475569",
        wraplength=460,
        justify="left"
    )
    subtitle_lbl.pack(anchor="w", pady=(6, 0))

    sys_name = "macOS" if sys.platform == "darwin" else platform.system()
    sys_info = f"Система: {sys_name} ({platform.machine()}) • Python {platform.python_version()}"
    badge = tk.Label(
        card,
        text=sys_info,
        font=("SF Pro Text", 9),
        bg="#f1f5f9",
        fg="#64748b",
        padx=8,
        pady=3
    )
    badge.pack(anchor="w", padx=20, pady=(0, 12))

    items_box = tk.Frame(card, bg="#f8fafc", highlightbackground="#cbd5e1", highlightthickness=1)
    items_box.pack(fill="both", expand=True, padx=20, pady=(0, 14))

    for item in missing_deps:
        row = tk.Frame(items_box, bg="#f8fafc")
        row.pack(fill="x", padx=14, pady=10)

        icon_lbl = tk.Label(row, text="📦", font=("SF Pro Text", 14), bg="#f8fafc")
        icon_lbl.pack(side="left", anchor="n", padx=(0, 10))

        text_col = tk.Frame(row, bg="#f8fafc")
        text_col.pack(side="left", fill="x", expand=True)

        p_title = tk.Label(
            text_col,
            text=f"{item['name']}  ({item['package']})",
            font=("SF Pro Text", 11, "bold"),
            bg="#f8fafc",
            fg="#1e293b"
        )
        p_title.pack(anchor="w")

        p_desc = tk.Label(
            text_col,
            text=item["desc"],
            font=("SF Pro Text", 10),
            bg="#f8fafc",
            fg="#64748b",
            wraplength=380,
            justify="left"
        )
        p_desc.pack(anchor="w", pady=(2, 0))

    status_lbl = tk.Label(
        card,
        text="",
        font=("SF Pro Text", 10),
        bg="#ffffff",
        fg="#0284c7"
    )
    status_lbl.pack(fill="x", padx=20, pady=(0, 8))

    btn_bar = tk.Frame(card, bg="#ffffff")
    btn_bar.pack(fill="x", padx=20, pady=(0, 18))

    installed_ok = [False]

    def on_install():
        btn_install.pack_forget()
        btn_cancel.pack_forget()
        status_lbl.config(text="Устанавливаю компоненты через pip... Пожалуйста, подождите...", fg="#0284c7")
        root.update()

        def worker():
            pkgs = [item["package"] for item in missing_deps]
            cmd = [sys.executable, "-m", "pip", "install", *pkgs]
            proc = subprocess.run(cmd, capture_output=True, text=True)
            if proc.returncode == 0:
                def fin_ok():
                    status_lbl.config(text="Все компоненты успешно установлены! Запускаю...", fg="#16a34a")
                    installed_ok[0] = True
                    root.after(1000, root.destroy)
                root.after(0, fin_ok)
            else:
                def fin_err():
                    err_txt = f"Не удалось установить автоматически. Выполните:\npip install {' '.join(pkgs)}"
                    status_lbl.config(text=err_txt, fg="#b91c1c")
                    close_lbl_text = "Продолжить без них" if all_optional else "Закрыть"
                    close_btn = tk.Label(
                        btn_bar, text=close_lbl_text, font=("SF Pro Text", 11),
                        bg="#f1f5f9", fg="#475569", padx=16, pady=7, cursor="hand2", relief="solid", bd=1
                    )
                    close_btn.pack(side="right")
                    close_btn.bind("<Button-1>", lambda _e: (root.destroy(), None if all_optional else sys.exit(1)))
                root.after(0, fin_err)

        threading.Thread(target=worker, daemon=True).start()

    def on_cancel():
        root.destroy()
        if not all_optional:
            sys.exit(0)

    btn_install = tk.Label(
        btn_bar,
        text="Да, установи",
        font=("SF Pro Text", 11, "bold"),
        bg="#16a34a",
        fg="#ffffff",
        padx=18,
        pady=8,
        cursor="hand2",
        relief="flat"
    )
    btn_install.pack(side="right", padx=(10, 0))
    btn_install.bind("<Button-1>", lambda _e: on_install())
    btn_install.bind("<Enter>", lambda _e: btn_install.config(bg="#15803d"))
    btn_install.bind("<Leave>", lambda _e: btn_install.config(bg="#16a34a"))

    cancel_lbl_text = "Пропустить" if all_optional else "Нет, я сам(а)"
    btn_cancel = tk.Label(
        btn_bar,
        text=cancel_lbl_text,
        font=("SF Pro Text", 11),
        bg="#f8fafc",
        fg="#475569",
        padx=16,
        pady=7,
        cursor="hand2",
        relief="solid",
        bd=1
    )
    btn_cancel.pack(side="right")
    btn_cancel.bind("<Button-1>", lambda _e: on_cancel())
    btn_cancel.bind("<Enter>", lambda _e: btn_cancel.config(bg="#e2e8f0"))
    btn_cancel.bind("<Leave>", lambda _e: btn_cancel.config(bg="#f8fafc"))

    root.mainloop()
    return installed_ok[0]

def main():
    missing = get_missing_dependencies()
    if missing:
        ok = show_dependency_dialog(missing)
        if not ok and not all(item.get("optional", False) for item in missing):
            return
        global HAS_PIL
        try:
            from PIL import Image, ImageTk, ImageDraw
            HAS_PIL = True
        except ImportError:
            pass
    root = tk.Tk()
    App(root)
    root.mainloop()

if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] in ("--fetch-ozon-headless", "--fetch-wb-headless"):
        try:
            os.nice(10)
        except Exception:
            pass
        mode = sys.argv[1]
        u = sys.argv[2]
        pid = sys.argv[3]
        h = fetch_ozon_headless_worker(u, pid)
        if h:
            if mode == "--fetch-wb-headless":
                wb_p = parse_wb_html(h)
                sys.stdout.write("__WB_JSON_START__\n" + json.dumps({"detected_price": wb_p}, ensure_ascii=False) + "\n__WB_JSON_END__\n")
            else:
                p = parse_ozon_html(h, pid, u)
                sys.stdout.write("__OZON_JSON_START__\n" + json.dumps(p, ensure_ascii=False) + "\n__OZON_JSON_END__\n")
        else:
            if mode == "--fetch-wb-headless":
                sys.stdout.write("__WB_JSON_START__\n{}\n__WB_JSON_END__\n")
            else:
                sys.stdout.write("__OZON_JSON_START__\n{}\n__OZON_JSON_END__\n")
        sys.exit(0)
    main()

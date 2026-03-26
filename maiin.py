# pip install requests
import time
import re
import requests

BASE = "https://www.ivasms.com"
RECEIVED_PAGE = f"{BASE}/portal/sms/received"
GETSMS_URL = f"{BASE}/portal/sms/received/getsms"
NUMBER_URL = f"{BASE}/portal/sms/received/getsms/number"

# 1) بعد ما تسجّل دخول يدويًا بالمتصفح (بسبب Turnstile)، انسخ الكوكيز والصقها هنا:
COOKIES = {
 # أمثلة أسماء شائعة (استبدل القيم من المتصفح):
 # "cf_clearance": "PASTE_VALUE_HERE",
 # "laravel_session": "PASTE_VALUE_HERE",
 # "XSRF-TOKEN": "PASTE_VALUE_HERE",
}

def extract_token(html: str):
 m = re.search(r'name="_token"\s+value="([^"]+)"', html)
 return m.group(1) if m else None

def make_session():
 s = requests.Session()
 s.headers.update({
 "User-Agent": "Mozilla/5.0",
 "X-Requested-With": "XMLHttpRequest",
 "Referer": RECEIVED_PAGE,
 "Origin": BASE,
 })
 for k, v in COOKIES.items():
 s.cookies.set(k, v, domain="www.ivasms.com")
 return s

def get_csrf_token(session: requests.Session):
 r = session.get(RECEIVED_PAGE, timeout=20)
 r.raise_for_status()
 token = extract_token(r.text)
 if not token:
 raise RuntimeError("لم يتم العثور على _token. غالبًا الكوكيز منتهية أو غير كاملة.")
 return token

def post_json(session: requests.Session, url: str, data: dict):
 r = session.post(url, data=data, timeout=20)
 r.raise_for_status()
 try:
 return r.json()
 except Exception:
 return r.text

def fetch_ivasms_messages_last_hour(range_id: str):
 s = make_session()
 token = get_csrf_token(s)

 # ملاحظة: الموقع عندك يرسل start/end فارغة. لو يدعم، ضع توقيتاتك بدل "".
 payload_common = {"_token": token, "start": "", "end": "", "range": range_id}

 sms_list = post_json(s, GETSMS_URL, payload_common)
 numbers = post_json(s, NUMBER_URL, payload_common)

 return {"sms_list": sms_list, "numbers": numbers}

if __name__ == "__main__":
 RANGE_ID = "PASTE_RANGE_ID_HERE" # نفس id اللي عندك في Network
 while True:
 data = fetch_ivasms_messages_last_hour(RANGE_ID)
 print(data)
 time.sleep(3)

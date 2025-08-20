import requests
import time

URL = "https://instagramcopybot.onrender.com/ping"  # Render 서버 주소
INTERVAL = 5 * 60  # 5분 = 300초

while True:
    try:
        response = requests.get(URL)
        print(f"Ping sent! Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending ping: {e}")
    
    time.sleep(INTERVAL)

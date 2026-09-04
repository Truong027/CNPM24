"""
Script test gửi request HTTP đến Flask app
"""
import requests
import time

url = "http://127.0.0.1:5000/video_feed_webcam"
print(f"🌐 Đang gửi request đến {url}...")

try:
    response = requests.get(url, timeout=5, stream=True)
    print(f"✅ Response status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    
    # Đọc vài bytes đầu
    count = 0
    for chunk in response.iter_content(chunk_size=1024):
        print(f"📦 Nhận chunk {count}: {len(chunk)} bytes")
        count += 1
        if count > 5:  # Chỉ đọc 5 chunks
            break
    
    print("✅ Request thành công!")
except Exception as e:
    print(f"❌ Lỗi: {e}")

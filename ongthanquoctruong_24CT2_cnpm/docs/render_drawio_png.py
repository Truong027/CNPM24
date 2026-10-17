import os
import sys
import subprocess
import base64
import time
import urllib.parse
import zlib
from PIL import Image, ImageChops

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = r"d:\CNPM24CT2_OngThanQuocTruong\ongthanquoctruong_24CT2_cnpm"
DOCS_DIR = os.path.join(ROOT_DIR, "docs")
TUAN_TU_DIR = os.path.join(DOCS_DIR, "Tuần Tự")
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
VIEWER_JS = os.path.join(DOCS_DIR, "viewer-static.min.js")

def update_png_drawio_xml(png_path, xml_str):
    if not os.path.exists(png_path):
        return
    try:
        with open(png_path, "rb") as f:
            data = f.read()

        encoded_xml = urllib.parse.quote(xml_str).encode("latin1")
        text_payload = b"mxfile\x00" + encoded_xml
        crc = zlib.crc32(b"tEXt" + text_payload) & 0xffffffff
        new_text_chunk = len(text_payload).to_bytes(4, "big") + b"tEXt" + text_payload + crc.to_bytes(4, "big")

        new_data = bytearray(data[:8])
        pos = 8
        text_inserted = False
        while pos < len(data):
            length = int.from_bytes(data[pos:pos+4], "big")
            chunk_type = data[pos+4:pos+8]
            chunk_full_len = 12 + length
            chunk_bytes = data[pos:pos+chunk_full_len]

            if chunk_type == b"tEXt" and data[pos+8:pos+14] == b"mxfile":
                new_data.extend(new_text_chunk)
                text_inserted = True
            elif chunk_type == b"IDAT" and not text_inserted:
                new_data.extend(new_text_chunk)
                text_inserted = True
                new_data.extend(chunk_bytes)
            else:
                new_data.extend(chunk_bytes)
            pos += chunk_full_len

        with open(png_path, "wb") as f:
            f.write(new_data)
        print(f"Updated embedded Draw.io XML in {png_path}")
    except Exception as e:
        print(f"Lỗi update_png_drawio_xml: {e}")

def render_diagram(base_name):
    drawio_file = os.path.join(TUAN_TU_DIR, f"{base_name}.drawio")
    png_file = os.path.join(TUAN_TU_DIR, f"{base_name}.drawio.png")
    
    with open(drawio_file, "r", encoding="utf-8") as f:
        xml_content = f.read()

    b64_xml = base64.b64encode(xml_content.encode("utf-8")).decode("ascii")

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
body {{ margin: 0; padding: 25px; background: white; }}
#container {{ display: block; width: 1550px; height: 1150px; }}
</style>
</head>
<body>
<div id="container"></div>
<script src="viewer-static.min.js"></script>
<script>
  try {{
    var rawXml = decodeURIComponent(escape(atob("{b64_xml}")));
    var doc = mxUtils.parseXml(rawXml);
    var container = document.getElementById("container");
    var viewer = new GraphViewer(container, doc.documentElement, {{
      highlight: '#0000ff',
      nav: false,
      resize: true,
      checkVisibleState: false
    }});
  }} catch (err) {{
    document.body.innerText = "Lỗi render: " + err.message;
    console.error(err);
  }}
</script>
</body>
</html>"""

    html_file = os.path.join(DOCS_DIR, f"temp_{int(time.time()*1000)}.html")
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    temp_screenshot = os.path.join(DOCS_DIR, f"shot_{int(time.time()*1000)}.png")
    user_data_dir = os.path.join(os.environ.get("TEMP", "C:/Temp"), f"chrome_drawio_{int(time.time()*1000)}")

    cmd = [
        CHROME_PATH,
        "--headless=new",
        f"--user-data-dir={user_data_dir}",
        "--virtual-time-budget=3000",
        "--run-all-compositor-stages-before-draw",
        f"--screenshot={temp_screenshot}",
        "--window-size=1650,1250",
        f"file:///{html_file.replace(os.sep, '/')}"
    ]

    print(f"Rendering {base_name} via headless Chrome...")
    subprocess.run(cmd, check=True)

    if os.path.exists(temp_screenshot):
        img = Image.open(temp_screenshot)
        bg = Image.new("RGB", img.size, (255, 255, 255))
        diff = ImageChops.difference(img.convert("RGB"), bg)
        bbox = diff.getbbox()
        print(f"Content bbox for {base_name}: {bbox}")
        if bbox:
            pad = 20
            bbox = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(img.width, bbox[2] + pad),
                min(img.height, bbox[3] + pad)
            )
            cropped = img.crop(bbox)
            cropped.save(png_file, "PNG")
        else:
            img.save(png_file, "PNG")

        try:
            os.remove(temp_screenshot)
            os.remove(html_file)
        except Exception:
            pass

        update_png_drawio_xml(png_file, xml_content)
        print(f"Done rendering {png_file}!\n")

if __name__ == "__main__":
    for name in [
        "chức năng phê duyệt đơn chuyển nhượng Admin",
        "chức năng quản lý và phân quyền người dùng Admin"
    ]:
        render_diagram(name)

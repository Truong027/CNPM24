import os
import sys
import torch
from flask import Flask, render_template, request, jsonify

# Khởi tạo Flask App với đường dẫn templates tương ứng
app = Flask(__name__, template_folder="templates")

# Thông điệp chính theo yêu cầu
DEFAULT_MESSAGE = "Chào bạn khóa 24CT đến với học phần CNPM - DAU"

def process_text_with_pytorch(text: str):
    """
    Sử dụng PyTorch Framework để xử lý chuỗi văn bản:
    1. Chuyển đổi chuỗi thành Tensor (Byte / Unicode ASCII tensor)
    2. Thực hiện các phép biến đổi ma trận và tính toán Tensor
    3. Trích xuất thông tin tensor và trạng thái phần cứng (CUDA / CPU)
    """
    byte_values = [ord(c) for c in text]
    
    # 2. Tạo PyTorch Tensor
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    text_tensor = torch.tensor(byte_values, dtype=torch.float32, device=device)
    
    # 3. Thực hiện phép toán tensor
    tensor_len = text_tensor.numel()
    tensor_mean = float(torch.mean(text_tensor).item()) if tensor_len > 0 else 0.0
    tensor_std = float(torch.std(text_tensor).item()) if tensor_len > 1 else 0.0
    tensor_min = float(torch.min(text_tensor).item()) if tensor_len > 0 else 0.0
    tensor_max = float(torch.max(text_tensor).item()) if tensor_len > 0 else 0.0
    
    # Tạo tensor 2D giả lập vector embedding
    embedding_dim = 8
    weight_matrix = torch.randn((tensor_len, embedding_dim), device=device)
    projected = torch.matmul(text_tensor.unsqueeze(0), weight_matrix) # Shape: [1, 8]
    
    # 4. Thu thập thông tin PyTorch System
    system_info = {
        "pytorch_version": torch.__version__,
        "cuda_available": torch.cuda.is_available(),
        "cuda_version": torch.version.cuda if torch.cuda.is_available() else "N/A",
        "device_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU Mode",
        "device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0,
        "tensor_device": str(text_tensor.device),
        "tensor_shape": list(text_tensor.shape),
        "tensor_dtype": str(text_tensor.dtype),
        "tensor_bytes": byte_values,
        "tensor_sample_values": [int(x) for x in byte_values[:20]],
        "tensor_stats": {
            "length": tensor_len,
            "mean": round(tensor_mean, 2),
            "std": round(tensor_std, 2),
            "min": int(tensor_min),
            "max": int(tensor_max)
        },
        "projected_vector": [round(float(x), 4) for x in projected.squeeze(0).tolist()]
    }
    return system_info

@app.route("/")
def index():
    pytorch_data = process_text_with_pytorch(DEFAULT_MESSAGE)
    return render_template(
        "index.html",
        message=DEFAULT_MESSAGE,
        pytorch_data=pytorch_data
    )

@app.route("/api/process", methods=["POST"])
def api_process():
    data = request.get_json(force=True)
    text = data.get("text", DEFAULT_MESSAGE)
    if not text.strip():
        text = DEFAULT_MESSAGE
    result = process_text_with_pytorch(text)
    return jsonify(result)

if __name__ == "__main__":
    print("=" * 60)
    print("  ỨNG DỤNG WEB PYTORCH - CNPM DAU (KHOÁ 24CT)")
    print(f"  Sinh viên: Ông Thân Quốc Trường (24CT2)")
    print(f"  PyTorch Version: {torch.__version__}")
    print(f"  CUDA Available: {torch.cuda.is_available()}")
    print("  Server đang chạy tại: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(host="127.0.0.1", port=5000, debug=True)

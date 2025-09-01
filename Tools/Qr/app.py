from flask import Flask, request, jsonify, render_template_string, send_file
import qrcode
import io
import base64
from PIL import Image

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''
    <html>
<head>
    <title>QR Code Generator</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
        
        body {
            font-family: 'Montserrat', sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            color: #fff;
            overflow: hidden;
            perspective: 1000px;
        }

        .container {
            background-color: rgba(255, 255, 255, 0.95);
            color: #333;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
            text-align: center;
            max-width: 400px;
            width: 100%;
            transition: transform 0.3s ease, background-color 0.3s ease;
            position: relative;
            z-index: 10;
            transform-style: preserve-3d;
        }

        .container:hover {
            transform: translateY(-5px) rotateY(5deg);
            background-color: rgba(255, 255, 255, 1);
        }

        h1 {
            margin-bottom: 20px;
            font-size: 2em;
            color: #333;
        }

        input[type="text"] {
            width: calc(100% - 24px);
            padding: 12px;
            margin-bottom: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            font-size: 1.1em;
            outline: none;
            transition: border-color 0.3s ease, box-shadow 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: #007bff;
            box-shadow: 0 0 10px rgba(0, 123, 255, 0.2);
        }

        button {
            padding: 12px 25px;
            background-color: #007bff;
            color: #fff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1.1em;
            transition: background-color 0.3s ease, box-shadow 0.3s ease;
        }

        button:hover {
            background-color: #0056b3;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.1);
        }

        button:active {
            background-color: #003f7f;
        }

        #qrCode {
            margin-top: 20px;
        }

        #qrCode img {
            max-width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        #qrCode img:hover {
            transform: scale(1.05) rotate(3deg);
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        }

        .footer {
            margin-top: 20px;
            font-size: 0.8em;
            color: #888;
        }

        .footer a {
            color: #007bff;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .footer a:hover {
            color: #0056b3;
        }

        .background {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 25%, transparent 25%), 
            linear-gradient(225deg, rgba(255, 255, 255, 0.1) 25%, transparent 25%), 
            linear-gradient(45deg, rgba(255, 255, 255, 0.1) 25%, transparent 25%),
            linear-gradient(315deg, rgba(255, 255, 255, 0.1) 25%, transparent 25%);
            background-size: 50px 50px;
            animation: moveBackground 5s linear infinite;
            z-index: 1;
        }

        @keyframes moveBackground {
            0% {
                background-position: 0 0, 0 0, 0 0, 0 0;
            }
            100% {
                background-position: 50px 50px, 50px 50px, 50px 50px, 50px 50px;
            }
        }

        #downloadSection {
            margin-top: 15px;
        }

        select {
            padding: 8px;
            border-radius: 5px;
            margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="background"></div>
    <div class="container">
        <h1>QR Code Generator</h1>
        <input type="text" id="urlInput" placeholder="Enter URL">
        <button id="generateBtn">Generate QR Code</button>
        <div id="qrCode"></div>
        <div id="downloadSection" style="display:none;">
            <select id="formatSelect">
                <option value="PNG">PNG</option>
                <option value="JPG">JPG</option>
                <option value="SVG">SVG</option>
                <option value="PDF">PDF</option>
            </select>
            <button id="downloadBtn">Download</button>
        </div>
        <div class="footer">Made with ❤️ using <a href="https://flask.palletsprojects.com/" target="_blank">Flask</a> and 
                                  <a href="https://web.dev/learn/javascript" target="_blank">JavaScript</a></div>
    </div>
    <script>
        let lastUrl = "";

        document.getElementById('generateBtn').addEventListener('click', function() {
            const url = document.getElementById('urlInput').value;
            if (url.trim() !== '') {
                fetch('http://127.0.0.1:5000/generate_qr', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ url: url })
                })
                .then(response => response.json())
                .then(data => {
                    lastUrl = url;
                    const qrCodeDiv = document.getElementById('qrCode');
                    qrCodeDiv.innerHTML = `<img src="${data.qr_url}" alt="QR Code">`;
                    document.getElementById('downloadSection').style.display = "block";
                })
                .catch(error => {
                    console.error('Error generating QR code:', error);
                });
            }
        });

        document.getElementById('downloadBtn').addEventListener('click', function() {
            const format = document.getElementById('formatSelect').value;
            window.location.href = `/download_qr?url=${encodeURIComponent(lastUrl)}&format=${format}`;
        });
    </script>
</body>
</html>
    ''')

def create_trendy_qr(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="white", back_color="black").convert("RGBA")
    return img

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400
    img = create_trendy_qr(url)
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    img_base64 = base64.b64encode(img_byte_arr.read()).decode('utf-8')
    return jsonify({'qr_url': 'data:image/png;base64,' + img_base64})

@app.route('/download_qr')
def download_qr():
    url = request.args.get("url")
    fmt = request.args.get("format", "PNG").upper()
    img = create_trendy_qr(url)
    buf = io.BytesIO()
    if fmt == "PNG":
        img.save(buf, format="PNG")
        mimetype = "image/png"
        ext = "png"
    elif fmt == "JPG":
        img.convert("RGB").save(buf, format="JPEG")
        mimetype = "image/jpeg"
        ext = "jpg"
    elif fmt == "SVG":
        img.save(buf, format="PNG")
        mimetype = "image/png"
        ext = "png"
    elif fmt == "PDF":
        img.save(buf, format="PDF")
        mimetype = "application/pdf"
        ext = "pdf"
    else:
        return "Unsupported format", 400
    buf.seek(0)
    return send_file(buf, mimetype=mimetype, as_attachment=True, download_name=f"qr_code.{ext}")

if __name__ == '__main__':
    app.run(debug=True)

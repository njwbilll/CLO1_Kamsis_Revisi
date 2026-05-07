import http.server
import socketserver
import cgi
import struct

def xor_cipher_byte(b, key_str, index):
    k_bytes = key_str.encode()
    if not k_bytes: return b
    return b ^ k_bytes[index % len(k_bytes)]

def vigenere_byte(b, key_str, index, encrypt=True):
    k_bytes = key_str.encode()
    if not k_bytes: return b
    k = k_bytes[index % len(k_bytes)]
    return (b + k) % 256 if encrypt else (b - k) % 256

def caesar_byte(b, key_str, encrypt=True):
    k_bytes = key_str.encode()
    shift = sum(k_bytes) % 256 if k_bytes else 0
    if not encrypt: shift = -shift
    return (b + shift) % 256

def transposition(data):
    res = bytearray(data)
    for i in range(0, len(res) - 1, 2):
        res[i], res[i+1] = res[i+1], res[i]
    return res

def run_cbc_custom(data, k_vig, k_csr, k_xor, encrypt=True, iv=0xAA):
    res = bytearray()
    prev_block = iv
    
    for i, b in enumerate(data):
        if encrypt:
            step1 = b ^ prev_block
            step2 = xor_cipher_byte(step1, k_xor, i)
            step3 = caesar_byte(step2, k_csr, True)
            cipher_byte = vigenere_byte(step3, k_vig, i, True)
            res.append(cipher_byte)
            prev_block = cipher_byte 
        else:
            step1 = vigenere_byte(b, k_vig, i, False)
            step2 = caesar_byte(step1, k_csr, False)
            step3 = xor_cipher_byte(step2, k_xor, i)
            plain_byte = step3 ^ prev_block
            res.append(plain_byte)
            prev_block = b 
            
    return res

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>~* CRYPTOGRAPHY ENGINE *~</title>
    <style>
        body { background: #000; color: #0f0; font-family: "Comic Sans MS", sans-serif; padding: 20px; }
        .grid-container { display: grid; grid-template-columns: 1fr 1.5fr 1fr; gap: 20px; }
        .retro-window { background: #c0c0c0; border: 3px double #fff; box-shadow: 6px 6px 0px #333; color: #000; padding: 2px; }
        .title-bar { background: #800000; color: white; padding: 5px; font-weight: bold; font-size: 13px; text-transform: uppercase; }
        .content { padding: 15px; border: 1px inset #eee; }
        marquee { background: #ffff00; color: #ff0000; font-weight: bold; padding: 8px; border: 3px solid black; margin-bottom: 25px; }
        fieldset { border: 2px dashed #0000ff; margin-bottom: 12px; background: #e0e0e0; }
        .key-container { position: relative; width: 95%; }
        input[type="text"], input[type="password"] { 
            width: 100%; background: #222; color: #0f0; border: 2px solid #f0f; padding: 8px; font-family: monospace; box-sizing: border-box;
        }
        .btn-show {
            position: absolute; right: 5px; top: 50%; transform: translateY(-50%);
            background: #808080; border: 2px outset #fff; cursor: pointer; font-size: 10px; font-weight: bold; padding: 2px 5px;
        }
        .btn-show:active { border: 2px inset #fff; }
        .btn-chaos {
            background: linear-gradient(to bottom, #ff00ff, #800080);
            color: white; padding: 12px; border: 4px outset #ff00ff;
            cursor: pointer; font-size: 16px; width: 100%; text-shadow: 2px 2px black; font-weight: bold;
        }
        .sidebar-box { border: 2px solid #0ff; padding: 10px; margin-bottom: 15px; background: rgba(0,255,255,0.1); color: #0ff; font-size: 12px; }
        .blink { animation: blinker 0.8s linear infinite; color: #ff00ff; font-weight: bold; }
        @keyframes blinker { 50% { opacity: 0; } }
    </style>
</head>
<body>

<center>
    <h1><font color="cyan" size="7">== _#CRYPTOGRAPHY#_ ==</font></h1>
    <marquee scrollamount="12">*** ENCRYPTION AND DECRYPTION SYSTEM *** $NAJWA BILQIS AL KHALIDAH$ *** NIM 101032300186 *** TK-47-01 CLASS ***</marquee>
</center>

<div class="grid-container">
    <div style="grid-column: 1">
        <div class="sidebar-box">
            <p>STATUS: <span class="blink">SITE_ACCESSED</span></p>
            <p>PORT: 9999</p>
        </div>
    </div>

    <div style="grid-column: 2">
        <div class="retro-window">
            <div class="title-bar">Main.exe</div>
            <div class="content">
                <form method="POST" enctype="multipart/form-data">
                    <fieldset>
                        <legend>SECRET_PHRASE</legend>
                        <p>ENTER KEY:</p>
                        <div class="key-container">
                            <input type="password" name="user_key" id="user_key" placeholder="Type key..." required>
                            <button type="button" class="btn-show" onclick="toggleKey()">SHOW</button>
                        </div>
                    </fieldset>

                    <fieldset>
                        <legend>MODE</legend>
                        <input type="radio" name="op" value="enc" checked> ENCRYPT | 
                        <input type="radio" name="op" value="dec"> DECRYPT
                    </fieldset>

                    <fieldset>
                        <legend>PROTOCOL</legend>
                        <input type="radio" name="mode" value="ECB" checked onclick="toggleMode('ECB')"> ECB | 
                        <input type="radio" name="mode" value="CBC" onclick="toggleMode('CBC')"> CBC
                    </fieldset>

                    <fieldset>
                        <legend>INPUT_TYPE</legend>
                        <input type="radio" name="in_type" value="text" id="in_text" checked onclick="updateUI()"> TEXT | 
                        <span id="f_opt"><input type="radio" name="in_type" value="file" id="in_file" onclick="updateUI()"> IMAGE (.bmp)</span>
                    </fieldset>

                    <div id="t_box">
                        <p>INPUT DATA:</p>
                        <input type="text" name="val" autocomplete="off">
                    </div>

                    <div id="f_box" style="display:none;">
                        <p>UPLOAD BITMAP:</p>
                        <input type="file" name="f_val" accept=".bmp">
                    </div>

                    <p><button type="submit" class="btn-chaos">EXECUTE_NOW</button></p>
                </form>
            </div>
        </div>
    </div>

    <div style="grid-column: 3">
        <div class="sidebar-box" style="text-align:center;">
            <p class="blink">V.1.0_CLO1</p>
        </div>
    </div>
</div>

<script>
    function toggleKey() {
        const keyInput = document.getElementById('user_key');
        const btn = document.querySelector('.btn-show');
        if (keyInput.type === "password") {
            keyInput.type = "text";
            btn.innerText = "HIDE";
        } else {
            keyInput.type = "password";
            btn.innerText = "SHOW";
        }
    }

    function toggleMode(m) {
        const opt = document.getElementById('f_opt');
        if (m === 'CBC') {
            opt.style.display = 'none';
            document.getElementById('in_text').checked = true;
        } else {
            opt.style.display = 'inline';
        }
        updateUI();
    }

    function updateUI() {
        const isT = document.getElementById('in_text').checked;
        document.getElementById('t_box').style.display = isT ? 'block' : 'none';
        document.getElementById('f_box').style.display = isT ? 'none' : 'block';
    }
</script>

</body>
</html>
"""

def ecb_encrypt_bytes(d_bytes, key_vigenere, key_xor_alg):
    s1 = bytearray()
    for i, b in enumerate(d_bytes):
        s1.append(vigenere_byte(b, key_vigenere, i, True))
    s2 = transposition(s1)
    res = bytearray()
    for i, b in enumerate(s2):
        res.append(xor_cipher_byte(b, key_xor_alg, i))
    return res

def ecb_decrypt_bytes(d_bytes, key_vigenere, key_xor_alg):
    s1 = bytearray()
    for i, b in enumerate(d_bytes):
        s1.append(xor_cipher_byte(b, key_xor_alg, i))
    s2 = transposition(s1)
    res = bytearray()
    for i, b in enumerate(s2):
        res.append(vigenere_byte(b, key_vigenere, i, False))
    return res

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode())

    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST', 'CONTENT_TYPE': self.headers['Content-Type']}
        )

        master_key = form.getfirst("user_key", "DEFAULT").strip()
        if not master_key:
            master_key = "SAFE"

        key_vigenere = master_key
        key_caesar   = master_key[::-1]
        key_xor_alg  = master_key[1:] + master_key[0] if len(master_key) > 1 else master_key

        op      = form.getfirst("op",      "enc")
        mode    = form.getfirst("mode",    "ECB")
        in_type = form.getfirst("in_type", "text")

        if mode == "ECB" and in_type == "file":
            try:
                file_item = form["f_val"]
                bmp_data  = bytearray(file_item.file.read())

                if len(bmp_data) < 54:
                    raise ValueError("File BMP terlalu kecil / bukan BMP valid.")

                pixel_offset = struct.unpack_from("<I", bmp_data, 10)[0]

                header      = bmp_data[:pixel_offset]
                pixel_data  = bmp_data[pixel_offset:]

                if op == "enc":
                    processed_pixels = ecb_encrypt_bytes(bytes(pixel_data), key_vigenere, key_xor_alg)
                    out_filename     = "encrypted_output.bmp"
                    action_label     = "ENKRIPSI"
                else:
                    processed_pixels = ecb_decrypt_bytes(bytes(pixel_data), key_vigenere, key_xor_alg)
                    out_filename     = "decrypted_output.bmp"
                    action_label     = "DEKRIPSI"

                output_bmp = bytes(header) + bytes(processed_pixels)

                self.send_response(200)
                self.send_header("Content-Type",        "image/bmp")
                self.send_header("Content-Disposition", f'attachment; filename="{out_filename}"')
                self.send_header("Content-Length",      str(len(output_bmp)))
                self.end_headers()
                self.wfile.write(output_bmp)

            except Exception as e:
                self._send_error(str(e))
            return

        val = form.getfirst("val", "").strip()
        try:
            if op == "enc":
                d_bytes = val.encode()
                if mode == "ECB":
                    res = ecb_encrypt_bytes(d_bytes, key_vigenere, key_xor_alg)
                else:
                    res = run_cbc_custom(d_bytes, key_vigenere, key_caesar, key_xor_alg, True)
                display = res.hex()
            else:
                d_bytes = bytes.fromhex(val)
                if mode == "ECB":
                    res = ecb_decrypt_bytes(d_bytes, key_vigenere, key_xor_alg)
                else:
                    res = run_cbc_custom(d_bytes, key_vigenere, key_caesar, key_xor_alg, False)
                display = "".join(chr(b) for b in res if 31 < b < 127)
        except Exception as e:
            display = f"FATAL_ERROR: {str(e)}"

        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

        response_html = f"""
        <html>
        <body style="background:#000; color:#0f0; font-family:monospace; padding:20px;">
            <h2>PROCESS COMPLETED</h2>
            <p>RESULT:</p>
            <textarea style="width:100%; height:100px; background:#222; color:#0f0; border:1px solid #0f0;">{display}</textarea>
            <br><br>
            <a href="/" style="color:cyan;">[ BACK TO CONSOLE ]</a>
        </body>
        </html>
        """
        self.wfile.write(response_html.encode())

    def _send_error(self, msg):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(f"""
        <html>
        <body style="background:#000; color:#f00; font-family:monospace; padding:20px;">
            <h2>FATAL_ERROR</h2><p>{msg}</p>
            <a href="/" style="color:cyan;">[ BACK TO CONSOLE ]</a>
        </body>
        </html>
        """.encode())

if __name__ == "__main__":
    print("Server jalan di http://localhost:9999")
    socketserver.TCPServer(("", 9999), Handler).serve_forever()

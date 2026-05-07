import http.server
import socketserver
import cgi

def xor(data, key):
    k_bytes = key.encode()
    if not k_bytes: return data
    return bytearray([data[i] ^ k_bytes[i % len(k_bytes)] for i in range(len(data))])

def vigenere(data, key, encrypt=True):
    k_bytes = key.encode()
    if not k_bytes: return data
    res = bytearray()
    for i in range(len(data)):
        k = k_bytes[i % len(k_bytes)]
        val = (data[i] + k) % 256 if encrypt else (data[i] - k) % 256
        res.append(val)
    return res

def caesar(val_byte, key_str, encrypt=True):
    k_bytes = key_str.encode()
    shift = sum(k_bytes) % 256 if k_bytes else 0
    if not encrypt: shift = -shift
    return (val_byte + shift) % 256

def transposition(data):
    res = bytearray(data)
    for i in range(0, len(res) - 1, 2):
        res[i], res[i+1] = res[i+1], res[i]
    return res

def run_ecb(data, key, encrypt=True):
    if encrypt:
        temp = bytearray(data)
        if len(temp) % 2 != 0: temp.append(0)
        s1 = vigenere(temp, key, True)
        s2 = transposition(s1)
        return xor(s2, key)
    else:
        s1 = xor(data, key)
        s2 = transposition(s1)
        return vigenere(s2, key, False)

def run_cbc_custom(data, k_vig, k_csr, encrypt=True, iv=0xAA):
    res = bytearray()
    prev_block = iv
    if encrypt:
        for b in data:
            xored_input = b ^ prev_block
            # Tahap Caesar pakai k_csr, Tahap Vigenere pakai k_vig
            k1 = caesar(xored_input, k_csr, True)
            cipher_byte = vigenere(bytes([k1]), k_vig, True)[0]
            res.append(cipher_byte)
            prev_block = cipher_byte
    else:
        for b in data:
            k1 = vigenere(bytes([b]), k_vig, False)[0]
            decrypted_block = caesar(k1, k_csr, False)
            plain_byte = decrypted_block ^ prev_block
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
                        <input type="file" name="f_val">
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

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200); self.send_header("Content-type", "text/html"); self.end_headers()
        self.wfile.write(HTML_TEMPLATE.encode())

    # --- BAGIAN DO_POST YANG DIUBAH ---

    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type']})
        
        # 1. Ambil Master Key dari user
        master_key = form.getfirst("user_key", "DEFAULT").strip()
        if not master_key: master_key = "SAFE"

        # 2. Key Derivation (Memecah kunci agar tiap metode punya kunci unik)
        # Anak Kunci 1: Untuk Vigenere (Gunakan kunci asli)
        key_vigenere = master_key
        
        # Anak Kunci 2: Untuk Caesar (Gunakan kunci yang dibalik)
        key_caesar = master_key[::-1]
        
        # Anak Kunci 3: Untuk XOR (Gunakan rotasi sederhana)
        key_xor = master_key[1:] + master_key[0] if len(master_key) > 1 else master_key

        op = form.getfirst("op", "enc")
        mode = form.getfirst("mode", "ECB")
        in_type = form.getfirst("in_type", "text")

        # --- LOGIKA EKSEKUSI DENGAN ANAK KUNCI ---
        # Note: Kita harus sedikit menyesuaikan fungsi run agar menerima anak kunci ini
        # Namun agar tidak mengubah banyak kode, kita modifikasi cara panggilnya saja
        
        val = form.getfirst("val", "").strip()
        try:
            if op == "enc":
                d_bytes = val.encode()
                if mode == "ECB":
                    # Manual Pipeline ECB dengan kunci berbeda tiap tahap
                    s1 = vigenere(d_bytes, key_vigenere, True)
                    s2 = transposition(s1)
                    res = xor(s2, key_xor)
                else:
                    # Manual Pipeline CBC dengan kunci berbeda
                    res = run_cbc_custom(d_bytes, key_vigenere, key_caesar, True)
                display = res.hex()
            else:
                d_bytes = bytes.fromhex(val)
                if mode == "ECB":
                    # Manual Pipeline ECB Balik
                    s1 = xor(d_bytes, key_xor)
                    s2 = transposition(s1)
                    res = vigenere(s2, key_vigenere, False)
                else:
                    res = run_cbc_custom(d_bytes, key_vigenere, key_caesar, False)
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
        
if __name__ == "__main__":
    print("Server jalan di http://localhost:9999")
    socketserver.TCPServer(("", 9999), Handler).serve_forever()
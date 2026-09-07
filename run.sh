#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
#   TRIO MERAK - ZERO-INTERACTION RUNNER FOR TERMUX (ANDROID)
#   Otomatis setup dependensi, izin, dan langsung menjalankan bridge.
#   Tekan Ctrl + C untuk berhenti kapan saja.
# ==============================================================================

echo "============================================================"
echo "    🚀 MEMULAI TRIO MERAK SHIZUKU BRIDGE"
echo "============================================================"

# 1. Pastikan Python terinstall otomatis tanpa konfirmasi
if ! command -v python &> /dev/null; then
    echo "[*] Menginstall Python..."
    pkg update -y && pkg install -y python
fi

# 2. Pastikan izin storage aktif
if [ ! -d "$HOME/storage" ]; then
    echo "[*] Mengatur izin penyimpanan Termux..."
    termux-setup-storage
fi

# 3. Setup binary rish otomatis jika belum ada
if ! command -v rish &> /dev/null && [ ! -f "$PREFIX/bin/rish" ]; then
    SHIZUKU_RISH="/sdcard/Android/data/moe.shizuku.privileged.api/files/rish"
    if [ -f "$SHIZUKU_RISH" ]; then
        cp "$SHIZUKU_RISH" "$PREFIX/bin/rish"
        chmod +x "$PREFIX/bin/rish"
        echo "✅ Binary rish berhasil disalin!"
    fi
fi

# 4. Kunci CPU Termux agar tidak tidur saat layar mati
command -v termux-wake-lock &> /dev/null && termux-wake-lock 2>/dev/null

# 5. Langsung jalankan bridge.py (Non-Interaktif)
echo "[*] Menjalankan bridge..."
echo ""
python bridge.py "$@"

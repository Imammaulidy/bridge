#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
#   TRIO MERAK - SHIZUKU BRIDGE INSTALLER & RUNNER FOR TERMUX (ANDROID)
# ==============================================================================

echo "============================================================"
echo "    🚀 SETUP & JALANKAN SHIZUKU BRIDGE FOR TERMUX"
echo "============================================================"

# 1. Update pkg & Install python
if ! command -v python &> /dev/null; then
    echo "[*] Menginstall Python..."
    pkg update -y && pkg install -y python
fi

# 2. Setup Storage Permission
if [ ! -d "$HOME/storage" ]; then
    echo "[*] Mengatur izin penyimpanan Termux..."
    termux-setup-storage
fi

# 3. Setup rish binary
if ! command -v rish &> /dev/null && [ ! -f "$PREFIX/bin/rish" ]; then
    echo "[*] Mencari binary rish dari Shizuku..."
    SHIZUKU_RISH="/sdcard/Android/data/moe.shizuku.privileged.api/files/rish"
    if [ -f "$SHIZUKU_RISH" ]; then
        cp "$SHIZUKU_RISH" "$PREFIX/bin/rish"
        chmod +x "$PREFIX/bin/rish"
        echo "✅ Binary rish berhasil disalin ke $PREFIX/bin/rish!"
    else
        echo "⚠️ Binary rish belum ditemukan di $SHIZUKU_RISH"
        echo "   Buka aplikasi Shizuku -> Use Shizuku in terminal apps -> Export rish files."
    fi
fi

# 4. Jalankan bridge.py
echo ""
echo "[*] Menjalankan bridge.py..."
python bridge.py "$@"

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

# Jika ada argumen CLI yang diteruskan, jalankan langsung
if [ $# -gt 0 ]; then
    python bridge.py "$@"
    exit 0
fi

echo ""
echo "Pilih Mode Menjalankan:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "[1] 🎮 Jalankan Menu Interaktif (Foreground)"
echo "[2] 🚀 Jalankan Background 24/7 via PM2 (Auto-Bridge Standby)"
echo "[3] 📦 Install Node.js & PM2 di Termux"
echo "[4] 📊 Cek Status & Log PM2"
echo "[0] Keluar"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
read -p "Pilihan Anda [1/2/3/4/0]: " PIL

case "$PIL" in
    1)
        python bridge.py
        ;;
    2)
        if ! command -v pm2 &> /dev/null; then
            echo "[*] PM2 belum terinstall. Menginstall Node.js & PM2..."
            pkg update -y && pkg install -y nodejs
            npm install -g pm2
        fi
        termux-wake-lock
        pm2 start ecosystem.config.js
        pm2 save
        echo "✅ Bridge berhasil berjalan di background via PM2!"
        echo "   Gunakan 'pm2 status' atau 'pm2 logs bridge' untuk memantau."
        ;;
    3)
        echo "[*] Menginstall Node.js & PM2..."
        pkg update -y && pkg install -y nodejs
        npm install -g pm2
        echo "✅ Node.js & PM2 berhasil dipasang!"
        ;;
    4)
        if command -v pm2 &> /dev/null; then
            pm2 status
            echo ""
            read -p "Tampilkan log realtime? (y/n): " JWB
            if [ "$JWB" = "y" ] || [ "$JWB" = "Y" ]; then
                pm2 logs bridge
            fi
        else
            echo "PM2 belum terinstall."
        fi
        ;;
    *)
        echo "Keluar."
        ;;
esac

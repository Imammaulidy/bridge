#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
#   TRIO MERAK - ALL-IN-ONE SHIZUKU BRIDGE RUNNER (TERMUX ANDROID)
#   Otomatis setup dependensi, izin Shizuku, dan menjalankan 24/7 via PM2.
# ==============================================================================

# Tangani argumen kontrol cepat jika ada
if [ "$1" = "--stop" ] || [ "$1" = "stop" ]; then
    command -v pm2 &> /dev/null && pm2 stop bridge
    echo "⏹️ Bridge berhasil dihentikan."
    exit 0
fi

if [ "$1" = "--restart" ] || [ "$1" = "restart" ]; then
    command -v pm2 &> /dev/null && pm2 restart bridge
    echo "🔄 Bridge berhasil direstart."
    exit 0
fi

if [ "$1" = "--status" ] || [ "$1" = "status" ]; then
    command -v pm2 &> /dev/null && pm2 status
    exit 0
fi

if [ "$1" = "--logs" ] || [ "$1" = "logs" ]; then
    command -v pm2 &> /dev/null && pm2 logs bridge
    exit 0
fi

echo "============================================================"
echo "    🚀 MEMULAI TRIO MERAK SHIZUKU BRIDGE (PM2 24/7)"
echo "============================================================"

# 1. Pastikan Python terinstall
if ! command -v python &> /dev/null; then
    echo "[*] Menginstall Python..."
    pkg update -y && pkg install -y python
fi

# 2. Pastikan Node.js & PM2 terinstall
if ! command -v node &> /dev/null; then
    echo "[*] Menginstall Node.js..."
    pkg update -y && pkg install -y nodejs
fi

if ! command -v pm2 &> /dev/null; then
    echo "[*] Menginstall PM2 Process Manager..."
    npm install -g pm2
fi

# 3. Setup izin storage Termux
if [ ! -d "$HOME/storage" ]; then
    echo "[*] Mengatur izin penyimpanan Termux..."
    termux-setup-storage
fi

# 4. Setup binary rish otomatis dari Shizuku jika belum ada
if ! command -v rish &> /dev/null && [ ! -f "$PREFIX/bin/rish" ]; then
    SHIZUKU_RISH="/sdcard/Android/data/moe.shizuku.privileged.api/files/rish"
    if [ -f "$SHIZUKU_RISH" ]; then
        cp "$SHIZUKU_RISH" "$PREFIX/bin/rish"
        chmod +x "$PREFIX/bin/rish"
        echo "✅ Binary rish berhasil disalin ke $PREFIX/bin/rish!"
    fi
fi

# 5. Kunci CPU Termux agar tidak tidur saat layar mati (Wake Lock)
command -v termux-wake-lock &> /dev/null && termux-wake-lock 2>/dev/null

# 6. Jalankan / Restart via PM2 Process Manager secara otomatis
echo "[*] Menjalankan bridge di latar belakang via PM2..."
pm2 delete bridge 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save

echo ""
echo "============================================================"
echo "✅ TRIO MERAK SHIZUKU BRIDGE AKTIF 24/7 DI BACKGROUND (PM2)!"
echo "============================================================"
echo "👉 Tekan Tombol Fisik [VOLUME ATAS / BAWAH] di HP untuk ekstrak (Timer 3s)."
echo "👉 Atau klik tombol [Ambil Phrase] di Web POS Kasir (Instan)."
echo "👉 HP bebas dimatikan layarnya atau minimize Termux."
echo "👉 Menampilkan log realtime di bawah (Tekan Ctrl + C untuk keluar log):"
echo "============================================================"
echo ""

# Tampilkan log realtime langsung di layar. Menekan Ctrl+C hanya keluar dari log viewer,
# proses PM2 di background tetap berjalan 24/7!
pm2 logs bridge

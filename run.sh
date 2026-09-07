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

if [ "$1" = "--trigger" ] || [ "$1" = "--extract" ]; then
    touch "$HOME/.bridge_trigger"
    echo "⚡ Perintah ekstraksi berhasil dikirim ke bridge background!"
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

# 3. Setup izin storage Termux jika belum ada
if [ ! -d "$HOME/storage" ]; then
    echo "[*] Mengatur izin penyimpanan Termux..."
    termux-setup-storage
fi

# 4. Setup binary rish otomatis dari Shizuku (rish & rish_shizuku.dex)
for dir in "/sdcard/Android/data/moe.shizuku.privileged.api/files" "/sdcard/Download" "$HOME/storage/shared/Android/data/moe.shizuku.privileged.api/files" "$HOME/storage/downloads"; do
    if [ -f "$dir/rish" ]; then
        cp "$dir/rish"* "$PREFIX/bin/" 2>/dev/null || cp "$dir/rish" "$PREFIX/bin/rish" 2>/dev/null
        [ -f "$dir/rish_shizuku.dex" ] && cp "$dir/rish_shizuku.dex" "$PREFIX/bin/" 2>/dev/null
        chmod +x "$PREFIX/bin/rish" 2>/dev/null
        echo "✅ Binary rish & dex berhasil disalin dari $dir!"
        break
    fi
done

# Pastikan binary rish dapat dieksekusi
[ -f "$PREFIX/bin/rish" ] && chmod +x "$PREFIX/bin/rish" 2>/dev/null

# Pastikan environment RISH_APPLICATION_ID terdaftar
export RISH_APPLICATION_ID="com.termux"
grep -q "RISH_APPLICATION_ID" ~/.bashrc 2>/dev/null || echo 'export RISH_APPLICATION_ID="com.termux"' >> ~/.bashrc

# Verifikasi koneksi Shizuku
echo "[*] Memeriksa status Shizuku di HP..."
RISH_UID=$(rish -c id 2>/dev/null || /data/data/com.termux/files/usr/bin/rish -c id 2>/dev/null)
if echo "$RISH_UID" | grep -q "uid="; then
    echo "✅ Akses Shizuku (rish) TERVERIFIKASI AKTIF! ($RISH_UID)"
else
    echo "⚠️ PERINGATAN: Akses Shizuku (rish) belum aktif!"
    echo "👉 Buka aplikasi Shizuku di HP -> Pastikan 'Shizuku is running'"
    echo "👉 Buka menu 'Authorized applications' (Aplikasi yang diizinkan) -> Centang 'Termux'"
    echo "👉 Salin file rish: cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/ && chmod +x $PREFIX/bin/rish"
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
echo "👉 Atau tekan tombol [ENTER] di terminal ini untuk ekstrak (Timer 3s)."
echo "👉 Atau klik tombol [Ambil Phrase] di Web POS Kasir (Instan)."
echo "👉 HP bebas dimatikan layarnya atau minimize Termux."
echo "👉 Tekan Ctrl + C untuk keluar dari monitor (PM2 tetap jalan 24/7)."
echo "============================================================"
echo ""

# Stream logs di background subshell
pm2 logs bridge --lines 15 &
LOGS_PID=$!

cleanup() {
    kill $LOGS_PID 2>/dev/null
    echo ""
    echo "[*] Keluar dari monitor log. Bridge tetap aktif 24/7 di background (PM2)!"
    exit 0
}
trap cleanup INT TERM

# Main thread mendengarkan penekanan tombol ENTER di Termux
while true; do
    read -r
    touch "$HOME/.bridge_trigger"
    echo "⚡ [ENTER DITEKAN] Mengirim sinyal trigger ke bridge..."
done

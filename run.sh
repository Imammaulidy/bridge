#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
#   TRIO MERAK - SHIZUKU BRIDGE INTERACTIVE MENU (TERMUX ANDROID)
# ==============================================================================

CONFIG_FILE="$HOME/.merak_bridge_config.json"

show_menu() {
    clear
    echo "============================================================"
    echo "    🚀 TRIO MERAK - SHIZUKU BRIDGE CONTROL MENU"
    echo "============================================================"
    echo ""
    echo "  [1] 🎯 ALL-IN-ONE: Auto Setup & Jalankan Bridge (PM2 24/7)"
    echo "  [2] 📡 Ubah Target Server Gateway"
    echo "  [3] 📊 Status & Monitor PM2"
    echo "  [4] 📜 Lihat Log Realtime"
    echo "  [5] 🔄 Restart Bridge"
    echo "  [6] ⏹️  Stop Bridge"
    echo "  [7] ⚡ Trigger Manual Extract (ENTER)"
    echo "  [8] 🔍 Test Koneksi Shizuku"
    echo "  [0] 🚪 Keluar"
    echo ""
    echo "============================================================"
    
    # Show current server
    if [ -f "$CONFIG_FILE" ]; then
        SERVER=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['server_url'])" 2>/dev/null || echo "https://triomerak.web.id")
        echo "🌐 Target Server: $SERVER"
        echo "============================================================"
    fi
    echo ""
}

all_in_one_setup() {
    echo "============================================================"
    echo "    🚀 ALL-IN-ONE SETUP & LAUNCH"
    echo "============================================================"
    
    # 1. Install Python
    if ! command -v python &> /dev/null; then
        echo "[1/8] Menginstall Python..."
        pkg update -y && pkg install -y python
    else
        echo "[1/8] ✅ Python sudah terinstall"
    fi
    
    # 2. Install Node.js
    if ! command -v node &> /dev/null; then
        echo "[2/8] Menginstall Node.js..."
        pkg update -y && pkg install -y nodejs
    else
        echo "[2/8] ✅ Node.js sudah terinstall"
    fi
    
    # 3. Install PM2
    if ! command -v pm2 &> /dev/null; then
        echo "[3/8] Menginstall PM2..."
        npm install -g pm2
    else
        echo "[3/8] ✅ PM2 sudah terinstall"
    fi
    
    # 4. Setup storage
    if [ ! -d "$HOME/storage" ]; then
        echo "[4/8] Setup storage Termux..."
        termux-setup-storage
    else
        echo "[4/8] ✅ Storage sudah dikonfigurasi"
    fi
    
    # 5. Copy binary rish dari Shizuku
    echo "[5/8] Mencari binary rish dari Shizuku..."
    RISH_FOUND=0
    for dir in "/sdcard/Android/data/moe.shizuku.privileged.api/files" "/sdcard/Download" "$HOME/storage/shared/Android/data/moe.shizuku.privileged.api/files" "$HOME/storage/downloads"; do
        if [ -f "$dir/rish" ]; then
            cp "$dir/rish"* "$PREFIX/bin/" 2>/dev/null || cp "$dir/rish" "$PREFIX/bin/rish" 2>/dev/null
            [ -f "$dir/rish_shizuku.dex" ] && cp "$dir/rish_shizuku.dex" "$PREFIX/bin/" 2>/dev/null
            chmod +x "$PREFIX/bin/rish" 2>/dev/null
            echo "     ✅ Binary rish disalin dari $dir"
            RISH_FOUND=1
            break
        fi
    done
    
    if [ $RISH_FOUND -eq 0 ]; then
        echo "     ⚠️ Binary rish tidak ditemukan. Jalankan manual:"
        echo "     cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* \$PREFIX/bin/"
    fi
    
    [ -f "$PREFIX/bin/rish" ] && chmod +x "$PREFIX/bin/rish" 2>/dev/null
    
    # 6. Setup environment
    echo "[6/8] Setup environment variable..."
    export RISH_APPLICATION_ID="com.termux"
    grep -q "RISH_APPLICATION_ID" ~/.bashrc 2>/dev/null || echo 'export RISH_APPLICATION_ID="com.termux"' >> ~/.bashrc
    
    # 7. Test Shizuku
    echo "[7/8] Testing koneksi Shizuku..."
    RISH_UID=$(rish -c id 2>/dev/null || /data/data/com.termux/files/usr/bin/rish -c id 2>/dev/null)
    if echo "$RISH_UID" | grep -q "uid="; then
        echo "     ✅ Shizuku AKTIF! ($RISH_UID)"
    else
        echo "     ⚠️ Shizuku belum aktif. Pastikan:"
        echo "        1. Aplikasi Shizuku berjalan"
        echo "        2. Termux sudah diizinkan di Shizuku"
        echo ""
        read -p "     Lanjutkan? (y/n): " confirm
        if [ "$confirm" != "y" ]; then
            return
        fi
    fi
    
    # 8. Launch PM2
    echo "[8/8] Menjalankan bridge via PM2..."
    command -v termux-wake-lock &> /dev/null && termux-wake-lock 2>/dev/null
    
    pm2 delete bridge 2>/dev/null || true
    pm2 start ecosystem.config.js
    pm2 save
    
    echo ""
    echo "============================================================"
    echo "✅ BRIDGE AKTIF 24/7 DI BACKGROUND!"
    echo "============================================================"
    echo "Tekan tombol fisik Volume atau ENTER untuk extract"
    echo "Atau klik 'Ambil Phrase' di Web POS"
    echo "============================================================"
    echo ""
    read -p "Tekan ENTER untuk kembali ke menu..."
}

change_server() {
    echo "============================================================"
    echo "    📡 UBAH TARGET SERVER GATEWAY"
    echo "============================================================"
    
    if [ -f "$CONFIG_FILE" ]; then
        CURRENT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['server_url'])" 2>/dev/null || echo "https://triomerak.web.id")
        echo "Server saat ini: $CURRENT"
    else
        echo "Server saat ini: https://triomerak.web.id (default)"
    fi
    
    echo ""
    echo "Contoh:"
    echo "  - https://triomerak.web.id"
    echo "  - http://192.168.1.100:5000"
    echo "  - https://your-domain.com"
    echo ""
    read -p "Masukkan URL server baru: " NEW_SERVER
    
    if [ -z "$NEW_SERVER" ]; then
        echo "❌ URL tidak boleh kosong!"
        read -p "Tekan ENTER untuk kembali..."
        return
    fi
    
    # Add https if not present
    if [[ ! "$NEW_SERVER" =~ ^https?:// ]]; then
        NEW_SERVER="https://$NEW_SERVER"
    fi
    
    # Save to config
    echo "{\"server_url\": \"$NEW_SERVER\"}" > "$CONFIG_FILE"
    
    echo ""
    echo "✅ Target server berhasil diubah ke: $NEW_SERVER"
    echo ""
    echo "Restart bridge agar perubahan diterapkan?"
    read -p "(y/n): " restart_choice
    
    if [ "$restart_choice" = "y" ]; then
        pm2 restart bridge 2>/dev/null && echo "✅ Bridge direstart!"
    fi
    
    read -p "Tekan ENTER untuk kembali..."
}

show_status() {
    echo "============================================================"
    echo "    📊 STATUS PM2"
    echo "============================================================"
    if command -v pm2 &> /dev/null; then
        pm2 status
    else
        echo "❌ PM2 belum terinstall!"
    fi
    echo ""
    read -p "Tekan ENTER untuk kembali..."
}

show_logs() {
    echo "============================================================"
    echo "    📜 LOG REALTIME (Ctrl+C untuk keluar)"
    echo "============================================================"
    if command -v pm2 &> /dev/null; then
        pm2 logs bridge --lines 50
    else
        echo "❌ PM2 belum terinstall!"
        read -p "Tekan ENTER untuk kembali..."
    fi
}

restart_bridge() {
    echo "============================================================"
    echo "    🔄 RESTART BRIDGE"
    echo "============================================================"
    if command -v pm2 &> /dev/null; then
        pm2 restart bridge
        echo "✅ Bridge berhasil direstart!"
    else
        echo "❌ PM2 belum terinstall!"
    fi
    echo ""
    read -p "Tekan ENTER untuk kembali..."
}

stop_bridge() {
    echo "============================================================"
    echo "    ⏹️  STOP BRIDGE"
    echo "============================================================"
    if command -v pm2 &> /dev/null; then
        pm2 stop bridge
        echo "✅ Bridge berhasil dihentikan!"
    else
        echo "❌ PM2 belum terinstall!"
    fi
    echo ""
    read -p "Tekan ENTER untuk kembali..."
}

trigger_extract() {
    echo "============================================================"
    echo "    ⚡ TRIGGER MANUAL EXTRACT"
    echo "============================================================"
    touch "$HOME/.bridge_trigger"
    echo "✅ Sinyal ekstraksi berhasil dikirim ke bridge!"
    echo "Pastikan layar HP menampilkan 12 kata Bitget Wallet"
    echo ""
    read -p "Tekan ENTER untuk kembali..."
}

test_shizuku() {
    echo "============================================================"
    echo "    🔍 TEST KONEKSI SHIZUKU"
    echo "============================================================"
    
    export RISH_APPLICATION_ID="com.termux"
    
    echo "[*] Testing binary rish..."
    if [ -f "$PREFIX/bin/rish" ]; then
        echo "✅ File rish ditemukan di $PREFIX/bin/rish"
    else
        echo "❌ File rish tidak ditemukan!"
        echo "Jalankan: cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* \$PREFIX/bin/"
        read -p "Tekan ENTER untuk kembali..."
        return
    fi
    
    echo ""
    echo "[*] Testing eksekusi perintah via Shizuku..."
    RISH_UID=$(rish -c id 2>&1)
    
    if echo "$RISH_UID" | grep -q "uid="; then
        echo "✅ Shizuku BERHASIL TERHUBUNG!"
        echo "   $RISH_UID"
        echo ""
        echo "[*] Testing uiautomator dump..."
        rish -c "uiautomator dump /data/local/tmp/test_dump.xml" 2>&1
        TEST_RESULT=$(rish -c "cat /data/local/tmp/test_dump.xml 2>/dev/null | head -c 50")
        if echo "$TEST_RESULT" | grep -q "hierarchy"; then
            echo "✅ UIAutomator dump BERHASIL!"
        else
            echo "⚠️ UIAutomator dump gagal atau tidak ada data"
        fi
    else
        echo "❌ Shizuku TIDAK TERHUBUNG!"
        echo "   Error: $RISH_UID"
        echo ""
        echo "Checklist:"
        echo "  1. ✓ Aplikasi Shizuku berjalan di HP?"
        echo "  2. ✓ Termux sudah diizinkan di Shizuku?"
        echo "  3. ✓ File rish sudah disalin ke \$PREFIX/bin/?"
    fi
    
    echo ""
    read -p "Tekan ENTER untuk kembali..."
}

# Handle quick arguments
case "$1" in
    --stop|stop)
        pm2 stop bridge 2>/dev/null && echo "⏹️ Bridge dihentikan"
        exit 0
        ;;
    --restart|restart)
        pm2 restart bridge 2>/dev/null && echo "🔄 Bridge direstart"
        exit 0
        ;;
    --status|status)
        pm2 status
        exit 0
        ;;
    --logs|logs)
        pm2 logs bridge
        exit 0
        ;;
    --trigger|--extract)
        touch "$HOME/.bridge_trigger"
        echo "⚡ Trigger extract dikirim"
        exit 0
        ;;
esac

# Main menu loop
while true; do
    show_menu
    read -p "Pilih menu [0-8]: " choice
    
    case $choice in
        1) all_in_one_setup ;;
        2) change_server ;;
        3) show_status ;;
        4) show_logs ;;
        5) restart_bridge ;;
        6) stop_bridge ;;
        7) trigger_extract ;;
        8) test_shizuku ;;
        0) 
            echo "👋 Terima kasih! Bridge tetap berjalan di background (PM2)."
            exit 0
            ;;
        *)
            echo "❌ Pilihan tidak valid!"
            sleep 1
            ;;
    esac
done

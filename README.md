# 🌉 Trio Merak - Shizuku Bridge for Android (Termux)

Jembatan otomatisasi **Shizuku (`rish`)** di HP Android untuk mengekstrak **12/24 Kata Seed Phrase** dan mendeteksi **Alamat Barcode Penerima (`0x...`)** Bitget Wallet, lalu mengirimkannya secara instan dan aman ke Web Server Gateway lewat **Internet Seluler (Data Mobile)**.

Mendukung eksekusi latar belakang **24/7 non-stop menggunakan PM2**, sehingga Termux dapat di-minimize atau layar HP dimatikan tanpa menghentikan automasi.

---

## 🌟 Keunggulan Utama
- 🚫 **Tanpa Kabel USB**: Tidak perlu colok ke laptop / PC.
- 🚫 **Tanpa WiFi**: Berjalan 100% menggunakan koneksi data kartu seluler.
- ✈️ **Kebal Mode Pesawat**: Izin Shizuku tidak akan pernah putus atau revoked saat HP di-refresh dengan Mode Pesawat.
- ⚡ **Tanpa Dependensi Berat**: Murni menggunakan pustaka bawaan Python (`urllib`, `xml`, `subprocess`). **Tanpa perlu `pip install`**.
- 🔄 **Auto-Retry Cerdas**: Otomatis menunggu dan mengirim ulang data saat internet menyala kembali setelah Mode Pesawat.
- 🚀 **Aktif 24/7 di Background via PM2**: Termux bebas di-minimize atau layar dimatikan.

---

## ⚡ Quick Start (1 Baris Perintah Langsung Jalan)

Salin dan tempel perintah ini di terminal **Termux** Anda:

```bash
pkg update -y && pkg install -y git python && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash setup.sh
```

---

## 📱 Panduan Lengkap Dari Awal Sampai Running

### Langkah 1: Persiapan Aplikasi di HP Android
1. **Install Termux Resmi**:
   * Unduh Termux dari **[F-Droid](https://f-droid.org/en/packages/com.termux/)** atau **[GitHub Releases Termux](https://github.com/termux/termux-app/releases)**.
   * *(⚠️ Jangan gunakan Termux dari Google Play Store karena sudah usang/deprecated).*
2. **Install & Aktifkan Shizuku**:
   * Unduh **Shizuku** dari Play Store atau GitHub.
   * Aktifkan Shizuku via **Wireless Debugging** (menu Developer Options di Android).
   * Pastikan status Shizuku di dalam aplikasi menampilkan: **"Shizuku is running"**.

---

### Langkah 2: Berikan Izin Shizuku (`rish`) ke Termux

Buka aplikasi **Termux**, lalu jalankan perintah berikut untuk mengizinkan penyimpanan:

```bash
termux-setup-storage
```
*(Izinkan akses storage saat muncul popup di layar HP).*

Lalu salin file `rish` dari Shizuku ke direktori Termux:

```bash
cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish $PREFIX/bin/rish && chmod +x $PREFIX/bin/rish
```

> [!TIP]
> **Cara Alternatif jika file belum ada di sdcard**:
> Buka aplikasi **Shizuku** → tap menu **"Use Shizuku in terminal apps"** → tap **"Export files"**, lalu simpan ke folder Downloads. Kemudian di Termux ketik:
> ```bash
> cp ~/storage/downloads/rish $PREFIX/bin/rish && chmod +x $PREFIX/bin/rish
> ```

Uji apakah Shizuku sudah aktif di Termux:
```bash
rish -c id
```
*(Jika muncul `uid=2000(shell)` atau `uid=0(root)`, berarti akses Shizuku di Termux sudah 100% Berhasil).*

---

### Langkah 3: Download Repositori Bridge

Jalankan perintah berikut di Termux:

```bash
git clone https://github.com/Imammaulidy/bridge.git
cd bridge
```

---

## 🚀 Panduan Menjalankan Background 24/7 dengan PM2

Dengan PM2, script bridge akan berjalan di latar belakang secara terus menerus (*daemon*). Anda bebas minimize Termux atau mematikan layar HP; script tetap standby menerima perintah dari Web POS Kasir.

### 1️⃣ Install Node.js & PM2 di Termux (Hanya Sekali):
```bash
pkg update -y && pkg install -y nodejs && npm install -g pm2
```

### 2️⃣ Aktifkan Wake Lock (Mencegah Android Menidurkan Termux):
```bash
termux-wake-lock
```

### 3️⃣ Jalankan Auto-Bridge di Background via PM2:
Gunakan file konfigurasi bawaan `ecosystem.config.js`:
```bash
pm2 start ecosystem.config.js
```
*(Atau gunakan perintah manual: `pm2 start bridge.py --name "bridge" --interpreter python -- 3`)*

### 4️⃣ Simpan Konfigurasi PM2 agar Otomatis Pulih:
```bash
pm2 save
```

---

### 📊 Perintah Monitoring & Manajemen PM2

#### 📋 Cek Status Proses:
```bash
pm2 status
```

#### 📜 Pantau Log Realtime:
```bash
pm2 logs bridge
```

#### 🔄 Restart Bridge:
```bash
pm2 restart bridge
```

#### ⏹️ Hentikan Bridge:
```bash
pm2 stop bridge
```

#### ❌ Hapus dari PM2:
```bash
pm2 delete bridge
```

---

## 🎮 Mode Manual Interaktif & Menu Terminal

Jika Anda ingin menjalankan secara langsung di layar terminal (tanpa PM2):

```bash
python bridge.py
```

Menu interaktif akan muncul:

```text
============================================================
   TRIO MERAK - SHIZUKU BRIDGE CLIENT FOR TERMUX
============================================================
✅ Akses Shizuku / Root Aktif : rish
🌐 Server Target Web Gateway : https://triomerak.web.id
============================================================
[1] ⚡ Ambil Seed Phrase (12/24 Kata) & Kirim ke Web Server
[2] 📱 Ambil Address Penerima (Barcode Receive) & Kirim
[3] 🔄 Jalankan Mode Auto-Bridge (Standby menunggu klik Web)
[4] ⚙️ Ubah Alamat Server Web POS
[0] Keluar
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Pilih menu [1/2/3/4/0]: 
```

### 1️⃣ Menu `[1]` — Ambil Seed Phrase (12 Kata):
1. Di HP, buka aplikasi **Bitget Wallet** pada dompet yang ingin digarap → buka halaman **Tampilkan 12 Kata Seed Phrase**.
2. Di Termux, pilih menu **`1`** (atau jalankan `python bridge.py 1`).
3. Script otomatis membaca layar, mem-parse 12 kata, dan mengirimkannya ke Web Server.
4. Pada Beranda Web POS Kasir, dompet langsung otomatis terhubung dan saldo muncul seketika!

### 2️⃣ Menu `[2]` — Ambil Address Penerima (Barcode Receive):
1. Di HP, buka aplikasi **Bitget Wallet** akun baru → buka menu **Receive / Barcode Terima Token** (USDC/USDT).
2. Di Termux, pilih menu **`2`** (atau jalankan `python bridge.py 2`).
3. Script membaca alamat `0x...` dari barcode layar dan mengirimkannya ke Web POS.
4. Kolom **Address Penerima** di Web POS otomatis terisi.

### 3️⃣ Menu `[3]` — Mode Auto-Bridge (Otomatis Penuh):
* Saat mode `[3]` berjalan (baik di foreground maupun di background via PM2):
* Setiap kali Anda menekan tombol **`⚡ Ambil Phrase dari HP (Shizuku)`** atau tombol **`📱 Dari HP`** di halaman Web POS Kasir, HP Anda akan otomatis memindai layar dan mengirim hasilnya ke web tanpa perlu menyentuh Termux lagi!

---

## ⚙️ Shortcut Command Line (Cepat & Praktis)

Anda bisa langsung mengeksekusi fungsi tanpa masuk ke menu interaktif:

#### ⚡ Ambil Phrase Langsung:
```bash
python bridge.py 1
```

#### 📱 Ambil Address Barcode Langsung:
```bash
python bridge.py 2
```

#### 🔄 Jalankan Mode Auto-Bridge Foreground Langsung:
```bash
python bridge.py 3
```

#### 🌐 Mengatur Alamat Server Web Khusus:
```bash
python bridge.py --server https://triomerak.web.id
```
*(Atau jika menggunakan IP lokal: `python bridge.py --server http://192.168.1.100:5000`)*

---

## ✈️ Alur Garap dengan Mode Pesawat (Anti-Putus)

Saat garap multi-akun menggunakan jaringan seluler:
1. Jalankan **Mode Pesawat ON** → Tunggu 3 detik → **Mode Pesawat OFF** (IP HP berganti).
2. Buka Bitget Wallet → buka halaman 12 kata phrase.
3. Jalankan `python bridge.py 1` di Termux (atau jika Auto-Bridge via PM2 aktif, cukup klik tombol di Web POS Kasir).
4. Jika saat itu koneksi seluler masih dalam proses *reconnecting*, bridge akan **otomatis retry** hingga sinyal internet aktif kembali dan data terkirim sukses!
5. Buka Web POS Kasir → klik **`⚡ MAX SWEEP`** → Saldo lunas terpindah!
6. Ulangi untuk akun Bitget berikutnya.

---

## 🔒 Keamanan & Privasi
- Script ini **hanya membaca UI layar saat diperintahkan** via Shizuku.
- Tidak ada data yang dikirim ke pihak ketiga; seluruh komunikasi hanya terarah langsung ke server Web POS milik Anda sendiri.

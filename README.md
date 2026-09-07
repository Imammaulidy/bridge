# 🌉 Trio Merak - Shizuku Bridge for Android (Termux)

Jembatan otomatisasi **Shizuku (`rish`)** di HP Android untuk mengekstrak **12/24 Kata Seed Phrase** dan mendeteksi **Alamat Barcode Penerima (`0x...`)** Bitget Wallet, lalu mengirimkannya secara instan dan aman ke Web Server Gateway lewat **Internet Seluler (Data Mobile)**.

---

## ⚡ 1 Perintah Langsung Jadi (Non-Interaktif)

Cukup ketik perintah ini di **Termux**:

```bash
pkg update -y && pkg install -y git python && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

> [!TIP]
> **Otomatis Tanpa Pilihan Menu**: Perintah di atas langsung menginstall semua dependensi, menyalin akses Shizuku, dan langsung menjalankan bridge.  
> Untuk menghentikan program kapan saja, cukup tekan **Ctrl + C**.

---

## 🎮 Cara Penggunaan & Shortcut Ekstraksi

Setelah `bash run.sh` berjalan, terminal akan berada dalam status **Standby & Siap Ekstrak**. Anda memiliki 3 pilihan cara mengeksekusi:

### 1️⃣ Tekan [ENTER] di Termux (Timer 3 Detik):
* Tekan tombol **Enter** di keyboard Termux.
* Script akan menghitung mundur **3... 2... 1...** memberikan jeda waktu bagi Anda untuk membuka/berpindah ke tampilan 12 kata di aplikasi Bitget.
* Hasil langsung terbaca dan dikirim ke server.

### 2️⃣ Tekan Tombol [VOLUME ATAS] atau [VOLUME BAWAH] di HP (Timer 3 Detik):
* Anda **tidak perlu menyentuh terminal Termux sama sekali**!
* Cukup buka aplikasi **Bitget Wallet** pada layar 12 kata, lalu tekan salah satu tombol fisik: **Volume Up** atau **Volume Down** di samping bodi HP Anda.
* Script mendeteksi penekanan tombol fisik di latar belakang, menghitung mundur **3 detik**, lalu otomatis memotret dan mengekstrak kata phrase seketika!

### 3️⃣ Klik Tombol di Web POS Kasir (Tanpa Timer / Instan 0 Detik):
* Jika Anda menekan tombol **`⚡ Ambil Phrase dari HP (Shizuku)`** atau **`📱 Dari HP`** di browser Web POS Kasir, server akan memanggil HP Anda dan mengekstrak layar **seketika tanpa delay**.

---

## 📱 Panduan Persiapan Awal (Hanya Sekali)

### 1. Salin Binary Shizuku (`rish`) ke Termux:
Buka aplikasi **Termux**, lalu jalankan:

```bash
termux-setup-storage
cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish $PREFIX/bin/rish && chmod +x $PREFIX/bin/rish
```

*(Uji status Shizuku dengan mengetik `rish -c id`. Jika muncul `uid=2000`, Shizuku sudah aktif 100%).*

---

## 🚀 Menjalankan di Background 24/7 via PM2 (Opsional)

Jika Anda ingin menjalankan bridge di background 24 jam tanpa jendela terminal terbuka:

### 1. Install Node.js & PM2 di Termux:
```bash
pkg update -y && pkg install -y nodejs && npm install -g pm2
```

### 2. Kunci CPU Termux (Wake Lock):
```bash
termux-wake-lock
```

### 3. Jalankan Background via PM2:
```bash
pm2 start ecosystem.config.js
pm2 save
```

### 4. Perintah Monitoring PM2:
* **Cek Status**:
  ```bash
  pm2 status
  ```
* **Lihat Log Realtime**:
  ```bash
  pm2 logs bridge
  ```
* **Stop Bridge**:
  ```bash
  pm2 stop bridge
  ```

---

## 🌐 Mengatur Alamat Web Server Khusus

Jika Anda menggunakan alamat server sendiri atau IP lokal, jalankan dengan flag `--server`:

```bash
python bridge.py --server https://triomerak.web.id
```
*(Alamat akan tersimpan otomatis untuk eksekusi selanjutnya).*

---

## ✈️ Alur Garap Mode Pesawat (Anti-Putus)

1. Nyalakan **Mode Pesawat** $ightarrow$ Tunggu 3 detik $ightarrow$ Matikan **Mode Pesawat** (IP seluler berganti).
2. Buka aplikasi Bitget Wallet pada halaman 12 kata.
3. Tekan tombol **Volume Atas / Bawah** di HP (atau tekan Enter di Termux).
4. Timer 3 detik berjalan $ightarrow$ Bridge membaca layar dan otomatis retry saat sinyal data pulih $ightarrow$ Data sukses terkirim ke Web POS!
5. Klik **`⚡ MAX SWEEP`** di Web POS $ightarrow$ Saldo lunas berpindah!
6. Siap untuk akun berikutnya!

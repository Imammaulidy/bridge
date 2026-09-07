# 🌉 Trio Merak - Shizuku Bridge for Android (Termux)

Jembatan otomatisasi **Shizuku (`rish`)** di HP Android untuk mengekstrak **12/24 Kata Seed Phrase** dan mendeteksi **Alamat Barcode Penerima (`0x...`)** Bitget Wallet, lalu mengirimkannya secara instan dan aman ke Web Server Gateway lewat **Internet Seluler (Data Mobile)**.

Secara default **berjalan otomatis 24/7 di latar belakang menggunakan PM2 Process Manager**, sehingga Termux dapat di-minimize atau layar HP dimatikan tanpa menghentikan automasi. Terhubung langsung ke website gateway resmi **`https://triomerak.web.id`**.

---

## ⚡ 1 Perintah Langsung Jadi (All-in-One via PM2)

Cukup salin dan tempel perintah ini di terminal **Termux** Anda:

```bash
pkg update -y && pkg install -y git python && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

> [!TIP]
> **Otomatis Penuh**: Perintah `bash run.sh` di atas secara otomatis memeriksa dan memasang Python, Node.js, PM2, menyalin akses Shizuku (`rish`), mengaktifkan `termux-wake-lock`, serta menjalankan bridge di latar belakang via PM2.  
> Anda bebas menutup Termux atau mematikan layar HP; bridge tetap aktif 24 jam non-stop terhubung ke **`https://triomerak.web.id`**!

---

## 🔄 Reset & Update Bersih (Jika Git Pull Nyangkut / Error)

Jika update mengalami kendala, file bentrok (*merge conflict*), atau perintah `git pull origin main` nyangkut di Termux, **gunakan 1 baris perintah ini untuk menghentikan proses, menghapus direktori `bridge` lama secara tuntas, dan clone ulang**:

```bash
pm2 delete bridge 2>/dev/null; cd ~ && rm -rf bridge && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

> [!NOTE]
> Perintah di atas akan membersihkan seluruh file lama tanpa sisa, mengunduh versi terbaru yang 100% segar dari GitHub, dan langsung mengaktifkan kembali bridge di background PM2 24/7.

---

## 🎮 Cara Penggunaan & Shortcut Ekstraksi

Setelah menjalankan `bash run.sh`, sistem sudah aktif di background. Anda memiliki 3 cara praktis untuk mengekstrak:

### 1️⃣ Tekan Tombol Fisik [VOLUME ATAS] atau [VOLUME BAWAH] di HP:
* **Tidak perlu menyentuh terminal Termux sama sekali!**
* Cukup buka aplikasi **Bitget Wallet** pada layar 12 kata phrase.
* Tekan salah satu tombol fisik: **Volume Up** atau **Volume Down** di bodi samping HP Anda.
* Bridge otomatis mendeteksi tombol fisik, menghitung mundur **3 detik** (memberikan jeda agar layar phrase tampil penuh), lalu memindai dan mengirimkan kata phrase ke Web Server!

### 2️⃣ Tekan [ENTER] di Termux:
* Buka Termux, tekan **Enter**.
* Countdown **3 detik** akan berjalan, lalu mengekstrak layar HP seketika.

### 3️⃣ Klik Tombol di Web POS Kasir (Instan 0 Detik):
* Jika Anda menekan tombol **`⚡ Ambil Phrase dari HP (Shizuku)`** atau **`📱 Dari HP`** di halaman Web POS Kasir, server akan memanggil HP Anda dan mengekstrak layar **langsung tanpa jeda/timer**.

---

## 📱 Persiapan Awal (Hanya Sekali)

### Berikan Izin Shizuku (`rish`) ke Termux:
Buka aplikasi **Termux**, lalu jalankan:

```bash
termux-setup-storage
cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish $PREFIX/bin/rish && chmod +x $PREFIX/bin/rish
```

*(Uji status Shizuku dengan mengetik `rish -c id`. Jika muncul `uid=2000`, Shizuku sudah aktif 100%).*

---

## 📊 Manajemen & Kontrol PM2 via `run.sh`

Seluruh perintah pengelolaan sudah dicover dalam `run.sh`:

#### 📋 Cek Status Running:
```bash
bash run.sh --status
```
*(Atau langsung `pm2 status`)*

#### 📜 Pantau Log Realtime:
```bash
bash run.sh --logs
```
*(Atau langsung `pm2 logs bridge`. Tekan Ctrl + C untuk keluar dari log tanpa mematikan proses)*

#### 🔄 Restart Bridge:
```bash
bash run.sh --restart
```

#### ⏹️ Hentikan Bridge:
```bash
bash run.sh --stop
```

---

## 🌐 Alamat Web Server Kasir (Default: triomerak.web.id)

Sistem bridge **sudah diatur secara default terhubung langsung ke server resmi `https://triomerak.web.id`**, sehingga Anda **tidak perlu mengonfigurasi URL server lagi** untuk pemakaian normal.

Jika Anda ingin mengubah target server ke alamat domain sendiri atau IP lokal, Anda cukup menjalankannya sekali dengan opsi `--server`:

```bash
python bridge.py --server https://triomerak.web.id
```
*(Alamat server yang Anda tentukan akan otomatis tersimpan permanen di HP).*

---

## ✈️ Alur Garap Mode Pesawat (Anti-Putus)

1. Nyalakan **Mode Pesawat** → Tunggu 3 detik → Matikan **Mode Pesawat** (IP seluler berganti).
2. Buka aplikasi Bitget Wallet pada halaman 12 kata.
3. Tekan tombol **Volume Atas / Bawah** di HP Anda.
4. Timer 3 detik berjalan → Bridge membaca layar dan otomatis retry saat data seluler pulih → Phrase sukses terkirim ke Web POS!
5. Klik **`⚡ MAX SWEEP`** di Web POS → Saldo lunas berpindah ke akun baru!
6. Siap untuk akun berikutnya!

---

## 📁 Struktur Repositori Bersih (Pure Engine)

```text
bridge/
├── bridge.py            # 🐍 Script Bridge Client Shizuku
├── ecosystem.config.js  # ⚙️ Konfigurasi PM2 Process Manager
├── run.sh               # 🚀 All-in-One Runner (Auto-Install, Wake-Lock & PM2 24/7)
├── README.md            # 📖 Dokumentasi Lengkap
└── .gitignore           # 🔒 Proteksi File Konfigurasi Lokal
```

# 🌉 Trio Merak - Shizuku Bridge for Android (Termux 24/7)

Jembatan otomatisasi Shizuku (Non-Root) di HP Android untuk menghubungkan perangkat seluler ke Server Gateway (`https://triomerak.web.id`).

---

## 🚀 Fungsi & Fitur Utama

1. **⚡ Ekstraksi Seed Phrase & Barcode Address**:
   - Membaca 12/24 kata Seed Phrase Bitget Wallet dari layar HP tanpa kabel USB & tanpa Wi-Fi lokal.
   - Deteksi otomatis alamat deposit EVM (`0x...`) dari layar HP penerima.
2. **🔄 Reset Multi App & Jaringan (ADB Atomic Engine)**:
   - Force stop `com.waxmoon.ma.gp`, bersihkan cache, toggle Mode Pesawat ON/OFF (reset IP seluler 4G/5G), dan relaunch otomatis.
3. **🌐 Komunikasi Dua Arah**:
   - Terhubung secara aman ke `https://triomerak.web.id` via polling & socket HTTP. Kebal terhadap pergantian IP dinamis / Mode Pesawat.
4. **🎛️ Terintegrasi Langsung dengan POS Grid Card**:
   - Dikuasai langsung dari Web POS Kasir (`triomerak.web.id/pos`) via tombol **Ambil Phrase dari HP (Shizuku)** dan **Ambil Address dari Layar HP Penerima** pada **Wallet Auto & Sweeper Slot Card**.

---

## ⚡ Mode Ekspres (1 Baris Perintah Install / Reset Termux):

Jalankan perintah berikut di aplikasi **Termux**:

```bash
pm2 delete bridge 2>/dev/null; cd ~ && rm -rf bridge && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

> [!TIP]
> Perintah di atas akan otomatis mengunduh dependensi, menyalin binary Shizuku `rish`, mengaktifkan wake-lock, dan menjalankan bridge 24/7 di latar belakang via PM2.

---

## 📋 Prasyarat di HP Android

1. **Termux**: Unduh versi resmi dari **[F-Droid](https://f-droid.org/en/packages/com.termux/)** atau GitHub Releases (jangan gunakan versi Play Store).
2. **Shizuku**:
   - Buka aplikasi Shizuku di HP → Pastikan **Shizuku is running**.
   - Buka menu **Authorized applications** (Aplikasi yang diizinkan) → Centang **Termux**.
3. **Setup rish di Termux**:
   ```bash
   cp /sdcard/Android/data/moe.shizuku.privileged.api/files/rish* $PREFIX/bin/ && chmod +x $PREFIX/bin/rish
   rish -c id  # Verifikasi (wajib muncul uid=2000(shell))
   ```

---

## 🎯 Fitur & Kemampuan ADB

| Perintah | Deskripsi Aksi di HP |
|---|---|
| **RESET MULTI APP** | Force-stop `com.waxmoon.ma.gp`, bersihkan cache, toggle mode pesawat ON-OFF (reset IP), dan buka kembali Multi App |
| **TOGGLE AIRPLANE** | Toggle Mode Pesawat ON (2 detik) → OFF untuk mendapatkan IP baru data seluler |
| **EXTRACT PHRASE** | Dump UI uiautomator dan ambil 12 kata Seed Phrase Bitget Wallet |
| **DETECT ADDRESS** | Ambil alamat barcode deposit/penerimaan `0x...` dari layar Bitget |

---

## ⚡ Metode Trigger Cepat:

1. **Tombol Web POS Kasir**: Klik **[Ambil Phrase dari HP]** atau **[Ambil Address]** di slot card Web POS (`triomerak.web.id/pos`).
2. **Tombol Fisik HP**: Tekan **[VOLUME ATAS]** atau **[VOLUME BAWAH]** di HP (Countdown 3 detik).
3. **Tombol Enter di Termux**: Tekan **[ENTER]** di terminal Termux (Countdown 4 detik).
4. **Bot Telegram**: Jalankan menu `/reset_adb` di Bot Telegram.

---

## 🔧 Manajemen Layanan PM2 di Termux

```bash
pm2 status          # Cek status bridge
pm2 logs bridge     # Monitor log aktivitas realtime
pm2 restart bridge  # Restart bridge
pm2 stop bridge     # Hentikan bridge
```

## 📌 Troubleshooting: Mengatasi Error `couldn't find librish.so`

Jika saat tes `rish -c id` di Termux muncul error `java.lang.UnsatisfiedLinkError: couldn't find "librish.so"`, hal itu disebabkan karena file C++ JNI `librish.so` belum disalin ke direktori library Termux (`$PREFIX/lib/`).

**Solusi 1 (Jalankan Ulang Skrip Otomatis)**:
Skrip `run.sh` terbaru sudah secara otomatis meng-unzip `librish.so` dari APK Shizuku. Cukup jalankan:
```bash
pm2 delete bridge 2>/dev/null; cd ~ && rm -rf bridge && git clone https://github.com/Imammaulidy/bridge.git && cd bridge && bash run.sh
```

**Solusi 2 (Ekspor Manual dari App Shizuku)**:
1. Buka aplikasi **Shizuku** → klik **Export rish** → simpan di folder **Download**.
2. Di Termux jalankan:
   ```bash
   cp /sdcard/Download/rish* $PREFIX/bin/ 2>/dev/null
   cp /sdcard/Download/librish.so $PREFIX/lib/ 2>/dev/null
   cp /sdcard/Download/librish.so $PREFIX/bin/ 2>/dev/null
   chmod +x $PREFIX/bin/rish
   ```

---

**Server Gateway Target:** `https://triomerak.web.id`  
**Versi:** `v3.3 - Shizuku ADB Bridge & Auto-librish Extraction Fix`

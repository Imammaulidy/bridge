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

---

**Server Gateway Target:** `https://triomerak.web.id`  
**Versi:** `v3.2 - Shizuku ADB Bridge & Web POS Slot Card Integration`

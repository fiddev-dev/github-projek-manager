GitHub Project Manager

Aplikasi desktop yang powerful dibuat dengan Python dan CustomTkinter untuk mengelola repository GitHub Anda secara efisien. Tool ini mempermudah proses upload banyak proyek ke GitHub sekaligus dan mengelola repository yang sudah ada dengan antarmuka grafis yang intuitif.
(untuk aplikasi desktop nya ada di folder dist)
✨ Fitur Utama

###  Upload Proyek Massal
- **Pembuatan Repository Otomatis**: Membuat repository GitHub untuk banyak proyek sekaligus secara otomatis
- **Penanganan Duplikat Cerdas**: Otomatis mengganti nama repository jika sudah ada (menambahkan counter)
- **Pelacakan Riwayat Push**: Mengingat proyek yang sudah di-push untuk menghindari duplikasi
- **Monitoring Progress**: Progress bar real-time dan logging detail untuk semua operasi

###  Dukungan Organisasi
- **Mode User & Organisasi**: Upload ke akun personal atau repository organisasi
- **Auto-Discovery Organisasi**: Otomatis memuat dan memilih dari organisasi Anda
- **Switching Organisasi Mudah**: Toggle cepat antara personal dan target organisasi

###  Opsi Konfigurasi Lanjutan
- **Visibilitas Repository**: Pilih antara repository Public (🌐) atau Private (🔒)
- **Sorting Berdasarkan Tahun**: Organisasi proyek berdasarkan folder tahun (otomatis menambah prefix tahun pada nama repo)
- **Penggantian Spasi**: Opsi untuk mengganti spasi dengan tanda minus dalam nama repository
- **Folder Tersimpan**: Simpan folder proyek yang sering digunakan untuk akses cepat

###  Manajemen Repository
- **Hapus Massal**: Hapus banyak repository sekaligus dengan antarmuka checkbox yang rapi
- **Pencarian & Filter**: Cari repository dengan cepat menggunakan pencarian real-time
- **Pilih Semua/Batal Pilih**: Kontrol pemilihan massal yang nyaman
- **Penghapusan Aman**: Dialog konfirmasi mencegah penghapusan tidak sengaja
- **Auto-Refresh**: Memperbarui daftar repository setelah penghapusan

### Antarmuka Pengguna
- **Tema Dark Modern**: Antarmuka CustomTkinter yang bersih dan profesional
- **Layout Dual-Panel**: Halaman khusus untuk upload dan hapus repository
- **Logging Real-Time**: Log aktivitas lengkap dengan indikator emoji
- **Desain Responsif**: Scrolling halus dan komponen yang dapat diubah ukurannya

### Fitur Keamanan
- **Autentikasi Personal Access Token**: Autentikasi GitHub API yang aman
- **Validasi Kredensial**: Validasi otomatis username dan token
- **Perlindungan Privacy**: Token disembunyikan di input field


## Kasus Penggunaan

Sempurna untuk developer yang perlu:
- Upload banyak proyek lama ke GitHub
- Migrasi proyek dari penyimpanan lokal ke GitHub
- Organisir arsip proyek berdasarkan tahun
- Kelola repository dalam jumlah besar secara efisien
- Upload massal tugas kuliah atau proyek portfolio
- Bersihkan repository yang tidak terpakai dengan cepat

 Detail Teknis

- **Bahasa**: Python 3
- **GUI Framework**: CustomTkinter
- **Integrasi API**: GitHub REST API v3
- **Operasi Git**: Eksekusi command Git native
- **Penyimpanan**: History dan pengaturan berbasis file lokal

Cara Memulai

1. Masukkan username GitHub dan Personal Access Token Anda
2. Pilih target (Akun User atau Organisasi)
3. Pilih folder proyek Anda
4. Konfigurasi opsi upload (visibilitas, penamaan, sorting)
5. Klik "Scan and Push Projects" untuk mulai upload


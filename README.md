## FIND WHAT - OSINT TOOL

### Deskripsi
FIND WHAT adalah alat OSINT (Open Source Intelligence) untuk pencarian, pengumpulan, dan penyajian informasi dari web. Mendukung beberapa penyedia pencarian, menyimpan hasil ke file, mode interaktif, serta pengaturan lanjutan seperti timeout, retries, dan fallback otomatis.

### Fitur 🚀
- **Pencarian multi-provider**: Google dan DuckDuckGo (fallback otomatis)
- **Retry + backoff**: Lebih tangguh terhadap gangguan jaringan/limitasi
- **Auto-open**: Otomatis buka hasil di browser
- **Ekstraksi ringkas**: Ambil title dan deskripsi halaman
- **Simpan ke file**: Hasil diserialisasi rapi ke `.txt`
- **Mode interaktif**: Pilih hasil yang ingin dibuka
- **Output kaya warna**: Lebih mudah dibaca di terminal

### Prasyarat
- Python 3.9+ (disarankan Python 3.13 sesuai venv contoh)
- Pustaka Python:
  ```bash
  pip install argparse requests googlesearch-python beautifulsoup4 tqdm colorama
  ```

### Instalasi
```bash
git clone https://github.com/bagaspra16/find-what.git
cd find-what
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r <(printf "requests\ngooglesearch-python\nbeautifulsoup4\ntqdm\ncolorama\nargparse\n")
```

## Penggunaan Dasar
```bash
python find_what.py "kata kunci"
```

## Opsi CLI Lengkap
- **--num <int>**: Jumlah hasil pencarian. Default: 10
- **--auto-open**: Otomatis buka setiap URL yang ditemukan
- **--save**: Simpan hasil ke file `.txt` bernama `<query>_YYYYMMDD_HHMMSS.txt`
- **--interactive**: Mode interaktif untuk memilih hasil yang ingin dibuka
- **--timeout <int>**: Timeout HTTP (detik) saat melakukan pencarian. Default: 15
- **--retries <int>**: Jumlah percobaan ulang saat gagal. Default: 3
- **--provider <auto|google|ddg>**: Pilih penyedia pencarian. Default: `auto`
  - `auto`: coba Google dulu, jika kosong/gagal jatuh ke DuckDuckGo
  - `google`: paksa gunakan Google
  - `ddg`: paksa gunakan DuckDuckGo HTML
- **--insecure**: Nonaktifkan verifikasi SSL pada request pencarian (tidak direkomendasikan; gunakan hanya bila lingkungan jaringan memaksa inspeksi SSL)

## Contoh Penggunaan Lanjutan

### 1) Pencarian cepat dengan batas hasil dan simpan
```bash
python find_what.py "osint framework" --num 20 --save
```

### 2) Auto-open hasil + fallback otomatis
```bash
python find_what.py "latest cybersecurity trends" --num 5 --auto-open --provider auto
```

### 3) Mode interaktif untuk memilih tautan
```bash
python find_what.py "deep web search techniques" --interactive
```

### 4) Atur ketahanan jaringan: timeout dan retries
```bash
python find_what.py "threat intel feeds" --timeout 30 --retries 4
```

### 5) Paksa gunakan DuckDuckGo (mis. jika Google 429/blocked)
```bash
python find_what.py "osint email enumeration" --provider ddg --num 10
```

### 6) Jaringan ketat/SSL inspeksi (hindari bila tidak perlu)
```bash
python find_what.py "bug bounty recon" --provider ddg --insecure --timeout 20 --retries 2
```

## Perilaku Fallback dan Ketahanan
- **Provider auto**: mencoba Google terlebih dahulu. Jika gagal/hasil kosong, otomatis beralih ke DuckDuckGo.
- **Retry + backoff**: kegagalan akan dicoba ulang dengan jeda meningkat secara eksponensial.
- **Timeout**: cegah hang saat jaringan lambat atau server tidak responsif.

## Output dan Penyimpanan Hasil
- Hasil ditampilkan dengan nomor, judul, URL, dan deskripsi ringkas.
- Opsi `--save` akan menyimpan ke berkas: `<query_sanitized>_YYYYMMDD_HHMMSS.txt` pada direktori kerja saat ini.

## Tips Praktik Baik
- **Kurangi frekuensi** pencarian massal untuk menghindari limitasi sementara (mis. 429 dari Google).
- Gunakan **--provider ddg** saat Google menolak permintaan.
- Atur **--timeout** lebih besar di jaringan lambat dan naikkan **--retries** saat koneksi tidak stabil.
- Hindari **--insecure** kecuali benar-benar diperlukan oleh lingkungan jaringan (berisiko keamanan).

## Troubleshooting
- **429 Too Many Requests (Google)**:
  - Jalankan ulang dengan `--provider ddg`
  - Kurangi `--num`, tambah `--timeout`, naikkan `--retries`
- **SSL: CERTIFICATE_VERIFY_FAILED**:
  - Coba `--provider ddg` (endpoint: `https://html.duckduckgo.com/html/`)
  - Jika jaringan melakukan SSL inspection, gunakan `--insecure` (dengan risiko keamanan)
- **Hasil kosong**:
  - Ubah kata kunci (lebih spesifik), atau tambah `--num`
  - Gunakan `--provider ddg` jika Google memfilter/blokir
- **Browser terbuka terlalu banyak tab**:
  - Hilangkan `--auto-open` atau kurangi `--num`

## Catatan
- Bergantung pada perubahan antarmuka mesin pencari, scraping bisa terdampak. Gunakan fallback `--provider ddg` bila perlu.
- Hormati ketentuan layanan situs yang diakses. Hindari beban berlebih.

## Author
Dibuat oleh bagaspra16 — kontak: bagaspratamajunianika72@gmail.com

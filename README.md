# Hough Circle Detection

Implementasi deteksi lingkaran menggunakan Hough Transform dengan OpenCV untuk mendeteksi objek berbentuk lingkaran dalam gambar atau video stream real-time.

## Fitur

- **Deteksi Lingkaran pada Gambar**: Memproses file gambar untuk mendeteksi objek berbentuk lingkaran
- **Real-time Camera Stream**: Deteksi lingkaran secara real-time dari kamera
- **HSV Color Filtering**: Filter warna HSV dengan threshold area untuk mengurangi noise
- **Distance Calculation**: Menghitung jarak dari pusat gambar ke setiap lingkaran yang terdeteksi
- **Parameter Tuning**: Parameter yang dapat disesuaikan untuk optimasi deteksi

## Requirements

```bash
pip install opencv-python matplotlib numpy
```

## Penggunaan

### 1. Deteksi pada Gambar

```bash
python hough.py <nama_file_gambar>
```

Contoh:
```bash
python hough.py image.jpg
python hough.py test_image.png
```

### 2. Real-time Camera Stream

```bash
# Menggunakan kamera default (laptop camera)
python hough.py camera

# Menggunakan kamera eksternal
python hough.py camera 1
python hough.py camera 2
```

## Parameter Deteksi

### HSV Color Range
- **Target Range**: `[0, 70, 6]` hingga `[90, 255, 255]`
- **Optimal untuk**: Objek berwarna orange/kuning
- **Custom HSV**: Gunakan `python get_hsv_value.py` untuk mendapatkan nilai HSV custom

### Circle Detection Parameters
- `param1`: Threshold edge detection (default: 200)
- `param2`: Threshold center detection (default: 14)
- `minDist`: Jarak minimum antar lingkaran (default: 1000)
- `minRadius`: Radius minimum (default: 15)
- `maxRadius`: Radius maximum (default: 100)

### Area Threshold
- `min_area_threshold`: Area minimum untuk filtering noise (default: 200 pixels)

## Tuning Guidelines

### Parameter `param2` (Center Detection)
- **8-15**: Untuk objek kecil
- **12-20**: Untuk objek sedang (recommended)
- **15-25**: Untuk objek besar

### Area Threshold
- **50-200**: Deteksi objek kecil (lebih banyak noise)
- **200-500**: Balance antara deteksi dan noise reduction
- **500+**: Hanya objek besar (noise minimal)

## Output

### Mode Gambar
Menampilkan 4 panel:
1. **Original**: Gambar asli
2. **HSV Mask**: Hasil filtering HSV
3. **Detected Circles**: Lingkaran yang terdeteksi
4. **Distance Lines**: Garis jarak dari pusat ke lingkaran

### Mode Camera
- Real-time detection dengan overlay informasi
- Koordinat dan jarak setiap lingkaran
- Tekan `q` untuk keluar
- Tekan `s` untuk screenshot

## Contoh Output

```
Detected 3 small circles
Image center: (320, 240)
Circle centers (x, y, radius) and distances:
  Circle 1: center=(150, 180), radius=25, distance=185.2 pixels
  Circle 2: center=(400, 200), radius=30, distance=102.5 pixels
  Circle 3: center=(280, 350), radius=20, distance=115.8 pixels
```

## Camera Notes

- Camera 0,1,3,4: Akan di-flip horizontal
- Camera 2: Tidak di-flip
- Resolusi default: 640x480

## HSV Value Tuning

Untuk mendapatkan nilai HSV yang tepat untuk objek target:

```bash
# Dari gambar
python get_hsv_value.py image.jpg

# Dari kamera
python get_hsv_value.py -c 0

# Dari video
python get_hsv_value.py -v video.mp4
```

**Controls:**
- Klik kiri pada objek untuk auto-detect HSV range
- Tekan `r` untuk select ROI (Region of Interest)
- Tekan `s` untuk save HSV values ke file JSON
- Tekan `x` untuk keluar

## Troubleshooting

### Tidak Ada Deteksi
- Turunkan `param2` (coba 8-12)
- Kurangi `min_area_threshold`
- Sesuaikan range HSV untuk warna objek

### Terlalu Banyak False Positive
- Naikkan `param2` (coba 18-25)
- Naikkan `min_area_threshold`
- Sesuaikan `minRadius` dan `maxRadius`

### Objek Terlalu Dekat/Jauh
- Sesuaikan `minDist` parameter
- Ubah `minRadius` dan `maxRadius`

## Struktur Kode

- `create_hsv_mask()`: Filtering warna HSV dengan noise reduction
- `detect_circles()`: Deteksi lingkaran menggunakan HoughCircles
- `hough_transform()`: Pemrosesan gambar statis
- `hough_camera_stream()`: Real-time camera processing

## License

MIT License
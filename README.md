# Auto Visit — Android APK

App Python chạy trực tiếp trên Android, tự động visit nhiều URL theo chu kỳ.

## Tính năng
- Nhập danh sách URL (mỗi dòng 1 URL)
- Tùy chỉnh interval (giây) và thời lượng (giờ)
- Nút BẮT ĐẦU / DỪNG
- Log real-time với thống kê OK / FAIL
- Chạy nền khi tắt màn hình

## Tải APK

### Cách 1: Tự build bằng GitHub Actions (khuyến nghị)

1. Tạo repo GitHub mới, đẩy code lên:
   ```bash
   cd auto-app
   git init
   git add .
   git commit -m "init"
   git branch -M main
   git remote add origin https://github.com/<user>/<repo>.git
   git push -u origin main
   ```

2. Vào tab **Actions** → chọn workflow "Build Android APK" → bấm **Run workflow**

3. Chờ 30-60 phút (lần đầu), tải APK ở mục **Artifacts** cuối trang workflow run

### Cách 2: Build trên máy có Linux/macOS

```bash
sudo apt install -y openjdk-17-jdk
pip install buildozer cython
cd auto-app
buildozer android debug
# APK ở thư mục bin/
```

## Cài lên Android

1. Copy file `.apk` vào điện thoại
2. Bật **"Cài đặt từ nguồn không xác định"** trong Settings
3. Mở file APK, bấm Cài đặt

## Lưu ý

- App cần **Internet** (quyền INTERNET)
- Lần đầu chạy nên thử 1-2 URL trước
- Để chạy nền thật sự khi tắt màn hình, cần bật "Pin app" trong Recent Apps
- Một số anti-bot mạnh có thể chặn cả khi dùng cloudscraper

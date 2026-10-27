# canhreel

Công cụ dòng lệnh nhỏ gọn để **dựng video từ storyboard JSON** bằng FFmpeg: mỗi cảnh là một ảnh (hoặc nền màu) kèm lời thoại, công cụ tự tính thời lượng, xuất phụ đề và ghép thành MP4.

## Giới thiệu
Bạn viết kịch bản dạng danh sách cảnh, `canhreel` lo phần timeline, phụ đề và render. Không cần giao diện, không cần dịch vụ ngoài, chỉ dùng thư viện chuẩn Python + FFmpeg.

## Tính năng
- **Tự tính thời lượng cảnh theo tốc độ đọc** (`wpm`, mặc định 150 từ/phút): cảnh không ghi `duration` sẽ kéo dài đủ để đọc hết lời thoại (tối thiểu 1.5s, cộng 0.6s nghỉ). *Đây là tính năng riêng của canhreel.*
- **`lint` kiểm tra storyboard trước khi render**: báo ảnh/audio bị thiếu, cảnh quá ngắn so với lời thoại, chữ quá dài nên tách cảnh. Trả mã thoát 1 nếu có cảnh báo, tiện dùng trong CI.
- `plan`: in timeline (thời điểm bắt đầu, thời lượng từng cảnh).
- `srt`: xuất phụ đề `.srt` khớp timeline.
- `render`: dựng MP4 (H.264), tự scale/pad ảnh về đúng khung hình, đốt phụ đề vào video (tắt bằng `--no-subs`), ghép nhạc nền tùy chọn.
- Thông báo lỗi rõ ràng (JSON sai dòng nào, thiếu ffmpeg, lỗi FFmpeg).

## Cài đặt
Yêu cầu: Python ≥ 3.9 và FFmpeg (có bộ lọc `subtitles`/libass).
```bash
# Ubuntu/Debian
sudo apt install ffmpeg
# macOS
brew install ffmpeg

git clone <repo> canhreel && cd canhreel
pip install pytest   # chỉ cần để chạy test
```
Không có phụ thuộc Python nào khác.

## Cách dùng
```bash
python3 -m canhreel plan   examples/demo.json
python3 -m canhreel lint   examples/demo.json
python3 -m canhreel srt    examples/demo.json -o demo.srt
python3 -m canhreel render examples/demo.json -o demo.mp4
```

Định dạng storyboard:
```json
{
  "title": "Video của tôi",
  "width": 1280, "height": 720, "fps": 25, "wpm": 150,
  "audio": "nhac-nen.mp3",
  "scenes": [
    {"text": "Lời thoại cảnh 1", "image": "anh1.jpg"},
    {"text": "Cảnh 2 dùng nền màu", "color": "navy", "duration": 3}
  ]
}
```
Đường dẫn ảnh/audio tính tương đối theo thư mục chứa file JSON. Ảnh thiếu sẽ được thay bằng nền màu.

## Cấu trúc thư mục
```
canhreel/
├── canhreel/
│   ├── storyboard.py   # đọc JSON, tự tính thời lượng, lint
│   ├── subtitles.py    # sinh phụ đề SRT
│   ├── render.py       # gọi FFmpeg dựng từng cảnh rồi nối
│   └── cli.py          # lệnh plan / lint / srt / render
├── examples/demo.json
├── tests/test_core.py
└── LICENSE
```

## Kiểm thử
```bash
python3 -m pytest -q
```

## Giới hạn
- Chưa có hiệu ứng chuyển cảnh, chưa có giọng đọc TTS (lời thoại chỉ hiển thị dạng phụ đề).
- Ước lượng thời lượng dựa trên số từ, chỉ mang tính gần đúng.

## Ghi chú
Lấy cảm hứng ý tưởng từ [frameweaver](https://github.com/phucnguyentvp1/frameweaver), không dùng lại mã nguồn. Toàn bộ mã của canhreel được viết mới.

## Giấy phép
MIT © 2026 Viet Phan

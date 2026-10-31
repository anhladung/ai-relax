# Chuyển máy và tái lập

## Phụ thuộc

| Thành phần | Bắt buộc | Cách dùng |
|---|---|---|
| Blender 5.2.3 LTS | Có | bpy, Geometry Nodes, Cycles/Eevee, NumPy 2.3.4 bundled |
| Python 3.11+ trên PATH | Có cho launcher | Chỉ thư viện chuẩn; `python3` trên macOS/Linux |
| FFmpeg + FFprobe | Khi xuất MP4/smoke | Build có libx264 và AAC |
| Git | Để clone | Không cần đăng nhập khi clone repo công khai |
| Codex và skill | Tùy chọn | Hỗ trợ thao tác; không cần để render |
| Blender MCP | Tùy chọn | Đã dùng trong quá trình phát triển, không là phụ thuộc runtime |

Tải từ nguồn chính thức: [Blender](https://www.blender.org/download/), [các bản Blender](https://download.blender.org/release/), [Python](https://www.python.org/downloads/), [FFmpeg](https://ffmpeg.org/download.html). Blender binary/installer, Python, FFmpeg không được chép vào repo; cần bản phù hợp OS/CPU của máy mới.

Blender phát hiện qua `--blender`, `BLENDER_BIN`, PATH, rồi một số vị trí cài thông dụng. FFmpeg/FFprobe qua cờ tương ứng, biến môi trường tương ứng, rồi PATH. Mọi subprocess dùng danh sách đối số, không ghép shell command; đường dẫn có dấu cách được hỗ trợ.

Máy hiện tại từng crash Eevee OpenGL trong driver AMD; Vulkan chạy được. Điều này không chứng minh mọi GPU sẽ như vậy. Cycles CPU là đường chạy dự phòng chính. Pipeline mới không import Blender MCP hoặc yêu cầu mở ứng dụng Blender trước.

## Quy trình đề nghị

1. Clone repo vào thư mục có quyền ghi và đủ dung lượng trống. Tránh thư mục đồng bộ đang tải dở file.
2. Chạy `python run.py doctor`; sửa đường dẫn theo thông báo. Kiểm tra asset: `python scripts/check_assets.py`.
3. Chạy `python run.py reference --samples 8 --scale 50` để xác nhận mở được checkpoint.
4. Chạy `python run.py still` để dựng độc lập từ đầu, so sánh `preview.png` với `assets/approved-v06.png`.
5. Chạy `python run.py smoke --samples 4 --scale 25`: yêu cầu `verification.json` có `passed: true`.
6. Khi cần video, chạy `python run.py video --out outputs/video-01`. Đợi đủ 300 PNG rồi launcher mới ghép tiếng/MP4 và kiểm tra. Không coi 6 khung smoke là video hoàn chỉnh.

`outputs/<tên>/` chứa scene, manifest, sound.wav, log và ảnh/video. Không đẩy thư mục này lên Git. `manifest.json` ghi engine, version, preset hash, motion hashes, số hạt và âm thanh. `run.json` ghi signature cho resume. Nếu input đổi, dùng thư mục mới. Resume chỉ bỏ qua PNG đã có; file hỏng sẽ làm bước ghép/kiểm tra thất bại thay vì báo thành công.

## Chỉnh preset

Sao chép JSON sang preset mới, rồi dùng `--preset presets/my-scene.json`. Thay thời lượng/độ cao/độ nảy/màu/đèn có thể thay phong cách; giữ ràng buộc đĩa chỉ rộng hơn vùng hạt một ít. `reference` chỉ dành cho preset v06 đi kèm; custom preset dùng `still`/`video`.

Giữ fps 30; số khung = duration × 30. Độ phân giải phải chẵn; `--scale` làm tròn xuống số chẵn phù hợp H.264. Không tăng sáng bằng cách nâng toàn ảnh đến mức mất màu hạt. Tách màu nền và đĩa. Xem `PRODUCTION_STANDARDS.md`.

## Skill Codex tùy chọn

Từ repo trên **máy mới**, chạy:

```bash
python scripts/install_skill.py
```

Script chép skill vào `$CODEX_HOME/skills/ai-relax` (mặc định `~/.codex/skills/ai-relax`) và ghi vị trí clone của máy đó vào cấu hình skill cục bộ. Không ghi token hay credential. Nếu skill đã tồn tại, script dừng; dùng `--replace` khi chủ động muốn thay nó. Khởi động lại Codex nếu chưa thấy skill, rồi gọi `$ai-relax`.

Không di chuyển thư mục repo sau khi cài skill; nếu chuyển, chạy lại installer với `--replace`. Có thể chỉ dùng `run.py` mà không cài Codex hay bất kỳ skill nào.

## Lỗi thường gặp

- Thiếu executable: đặt đường dẫn tới file, không phải thư mục. Windows cần `blender.exe`, `ffmpeg.exe`, `ffprobe.exe`.
- Blender khác phiên bản: kiểm tra log cảnh báo; 5.2.3 là phiên bản đã chạy, không khẳng định mọi bản Blender tương thích.
- Driver crash: dùng engine mặc định Cycles CPU, không truyền `--gpu-backend`.
- Không ghi được folder/đầy đĩa: chọn `--out` khác; không xóa output cũ tự động.
- Không có libx264: cài một build FFmpeg hỗ trợ encoder đó.
- Màu khác: dùng cùng engine, color management, preset, Blender version; xem ảnh trong trình xem có quản lý màu. Không thể hứa pixel-identical giữa mọi phần cứng.

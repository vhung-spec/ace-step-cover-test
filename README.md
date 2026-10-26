# ACE-Step cover test

Thử chức năng **cover** của [ACE-Step 1.5](https://github.com/ACE-Step/ACE-Step-1.5) trên máy
của GitHub (không có GPU), rồi tự chấm điểm từng bản cover.

## Bài test làm gì

1. Cài ACE-Step 1.5 ở một commit cố định, rồi tải mô hình (turbo, 8 bước).
2. Tạo bản gốc: *We Wish You a Merry Christmas*, bài hát truyền thống đã hết bản quyền. Bài được
   phối cho piano ngay trong `make_source.py`, rồi phát thành âm thanh bằng FluidSynth.
3. Cover bản gốc theo từng dòng trong `plan.json`: mỗi dòng có một câu mô tả phong cách
   (`caption`) và một mức bám theo bản gốc (`strength`). Thông số giống hệt chức năng cover
   của app: mô hình turbo, 8 bước, shift 3, không dùng mô hình ngôn ngữ, không nén INT8.
4. Chấm điểm từng bản cover so với bản gốc (`score_covers.py`).

## Cách chạy

**Actions → ACE-Step cover test → Run workflow.** Ô *plan* để trống thì dùng `plan.json`.
Muốn thử kế hoạch khác thì dán một danh sách JSON, ví dụ:

```json
[{"name": "lofi-5of8", "strength": 0.625,
  "caption": "instrumental lofi Christmas, soft Rhodes piano, vinyl crackle, mellow drums"}]
```

Kết quả xem ở trang tóm tắt của lần chạy (bảng điểm), và trong mục **Artifacts → ace-cover-test**
(MP3 của bản gốc và các bản cover, ảnh phổ âm thanh, file điểm). Máy chỉ có CPU, nên mỗi lần
chạy mất khoảng một đến vài giờ.

## Ý nghĩa các điểm

| Điểm | Ý nghĩa |
|---|---|
| melody % (chance) | Phần trăm nốt giai điệu của bản gốc còn nghe rõ đúng lúc trong bản cover. Chính bản gốc được khoảng 90 % (mức trần của cách đo); số trong ngoặc là mức đoán bừa (bản cover phát ngược) |
| harmony | Giữ hoà âm và giai điệu: 1 là trùng khớp, 0 là ngang bản gốc phát ngược (đúng nốt, sai thời điểm) |
| key shift | Bản cover lệch tông bao nhiêu nửa cung (0 là cùng tông) |
| rhythm | Giữ nhịp: tương quan của các điểm bắt đầu nốt theo thời gian (1 là trùng khớp) |
| sound change | Âm sắc đổi bao nhiêu so với bản gốc (0 là cùng âm sắc) |
| style src→cover | Độ giống câu mô tả theo mô hình CLAP, của bản gốc so với của bản cover; tăng lên là đổi đúng hướng |
| closest style | Nhãn phong cách gần nhất mà CLAP chọn cho bản cover |
| peak dBFS, clipped %, silent % | Độ to đỉnh, tỉ lệ mẫu bị méo do quá to, tỉ lệ đoạn gần như im lặng |

Các điểm này đo được việc giữ giai điệu, giữ nhịp và đổi âm sắc. Còn hay hay không thì phải nghe.

## Giấy phép

Mã ACE-Step theo giấy phép MIT; xem giấy phép của trọng số mô hình trên
[trang Hugging Face của ACE-Step](https://huggingface.co/ACE-Step/Ace-Step1.5) trước khi dùng
kết quả cho mục đích thương mại. Mô hình CLAP dùng để chấm điểm là `laion/larger_clap_music`.

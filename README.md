# ACE-Step cover test

Thử chức năng **cover** của [ACE-Step 1.5](https://github.com/ACE-Step/ACE-Step-1.5) trên máy
của GitHub (không có GPU), rồi tự chấm điểm từng bản cover.

## Bài test làm gì

1. Cài ACE-Step 1.5 ở một commit cố định, rồi tải mô hình đã chọn: turbo (mô hình app dùng),
   SFT (chậm hơn, kỹ hơn) hoặc base (để thêm bè và phối thêm nhạc cụ).
2. Tạo bản gốc: *We Wish You a Merry Christmas*, bài hát truyền thống đã hết bản quyền. Bài được
   phối cho piano ngay trong `make_source.py`, rồi phát thành âm thanh bằng FluidSynth. Bản
   phối v2 chơi như người thật (mở đầu nhẹ, hợp âm rải, lần hai đầy hơn, có pedal, to nhỏ theo
   câu nhạc); v1 là bản phối đơn giản của các lượt đầu. Tiếng đàn lấy từ bộ âm thanh
   GeneralUser GS (mặc định) hoặc FluidR3.
3. Cover bản gốc theo từng dòng trong `plan.json`: mỗi dòng có một câu mô tả phong cách
   (`caption`) và một mức bám theo bản gốc (`strength`). Mặc định giống chức năng cover của
   app: mô hình turbo, 8 bước, shift 3, không dùng mô hình ngôn ngữ, không nén INT8.
4. Chấm điểm từng bản cover so với bản gốc (`score_covers.py`).

## Cách chạy

**Actions → ACE-Step cover test → Run workflow.** Chọn mô hình (*model*), bản phối (*arrangement*)
và bộ âm thanh (*soundfont*). Ô *plan* để trống thì dùng `plan.json`. Muốn thử kế hoạch khác thì
dán một danh sách JSON, ví dụ:

```json
[{"name": "piano-16", "strength": 1.0, "noise": 0.1, "steps": 16,
  "caption": "instrumental Christmas music, warm grand piano, soft strings, gentle and cozy"}]
```

Mỗi dòng có thể đặt thêm:

| Mục | Ý nghĩa |
|---|---|
| `noise` | Giữ lại bao nhiêu âm thanh của bản gốc làm điểm xuất phát (0 là không giữ) |
| `steps`, `shift`, `guidance` | Số bước (mặc định 8 với turbo, 50 với SFT và base), shift (3 với turbo, 1 với hai mô hình kia), mức bám câu mô tả (chỉ SFT và base, mặc định 7) |
| `reference` | Tên một dòng trước đó; bản của dòng đó làm âm sắc mẫu |
| `task: "text2music"` | Sáng tác một đoạn mới từ câu mô tả (`duration` giây), ví dụ để làm âm sắc mẫu |
| `task: "lego"`, `track` | Chỉ mô hình base: tạo riêng bè của một nhạc cụ (`strings`, `percussion`, `woodwinds`…) chơi cùng bản gốc. Bè mới lưu riêng (`stem_01`) và được trộn với bản gốc thành bản nghe (`take_01`) |
| `task: "complete"`, `tracks` | Chỉ mô hình base: phối thêm cả nhóm nhạc cụ quanh bản gốc |
| `source_from` | Tên một dòng trước đó; bản của dòng đó làm bản gốc, để chồng thêm bè |

Kết quả xem ở trang tóm tắt của lần chạy (bảng điểm), và trong mục **Artifacts → ace-cover-test**
(MP3 của bản gốc và các bản cover, ảnh phổ âm thanh, file điểm). Máy chỉ có CPU, nên mỗi lần
chạy mất khoảng một đến vài giờ.

## Ý nghĩa các điểm

| Điểm | Ý nghĩa |
|---|---|
| how | Mô hình và cách làm: `turbo 6/6` là số bước bám bản gốc trên số bước chạy; `base lego strings` là thêm bè dây. Dòng có chữ *new part only* chấm riêng bè mới |
| melody % (chance) | Phần trăm nốt giai điệu của bản gốc còn nghe rõ đúng lúc trong bản cover. Chính bản gốc được khoảng 90 % (mức trần của cách đo); số trong ngoặc là mức đoán bừa (bản cover phát ngược) |
| harmony | Giữ hoà âm và giai điệu: 1 là trùng khớp, 0 là ngang bản gốc phát ngược (đúng nốt, sai thời điểm) |
| key shift | Bản cover lệch tông bao nhiêu nửa cung (0 là cùng tông) |
| rhythm | Giữ nhịp: tương quan của các điểm bắt đầu nốt theo thời gian (1 là trùng khớp) |
| sound change | Âm sắc đổi bao nhiêu so với bản gốc (0 là cùng âm sắc) |
| style src→cover | Độ giống câu mô tả theo mô hình CLAP, của bản gốc so với của bản cover; tăng lên là đổi đúng hướng |
| closest style | Nhãn phong cách gần nhất mà CLAP chọn cho bản cover |
| quality PQ / enjoy CE | Điểm 1-10 của mô hình Audiobox Aesthetics (Meta): PQ là chất lượng âm thanh (sạch, rõ; thấp là rè, đục, nghe rẻ), CE là mức người nghe thích. Bên trái là bản gốc, bên phải là bản cover |
| peak dBFS, clipped %, silent % | Độ to đỉnh, tỉ lệ mẫu bị méo do quá to, tỉ lệ đoạn gần như im lặng |

Các điểm này đo được việc giữ giai điệu, giữ nhịp và đổi âm sắc. Còn hay hay không thì phải nghe.

**Chấm lại các lần chạy cũ:** Actions → *Judge earlier takes* → Run workflow, nhập mã các lần chạy
(số trong địa chỉ trang của lần chạy), cách nhau bằng dấu cách. Mọi file MP3 của các lần đó được
chấm PQ, CE, CU (độ hữu dụng làm nhạc nền) và PC (độ phức tạp của bản phối).

## Giấy phép

Mã ACE-Step theo giấy phép MIT; xem giấy phép của trọng số mô hình trên
[trang Hugging Face của ACE-Step](https://huggingface.co/ACE-Step/Ace-Step1.5) trước khi dùng
kết quả cho mục đích thương mại. Mô hình CLAP dùng để chấm điểm là `laion/clap-htsat-unfused`;
mô hình Audiobox Aesthetics (`facebook/audiobox-aesthetics`) theo giấy phép CC-BY 4.0.

Bộ âm thanh [GeneralUser GS](https://schristiancollins.com/generaluser.php) v2.0.3 là của
S. Christian Collins, được dùng tự do để làm nhạc, kể cả thương mại. Bài test tải nó từ kho
GitHub của tác giả ở một commit cố định, không chép vào kho này.

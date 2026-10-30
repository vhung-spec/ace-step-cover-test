# Dark piano

Nhạc piano u buồn, tối (dark piano): bản nhạc gốc viết dưới dạng dữ liệu (`pieces/*.json`), được
`compose.py` phối thành MIDI cho từng nhạc cụ, rồi `render_samples.py` (ở thư mục gốc) phát bằng
nhạc cụ thu thật (VCSL, VSCO 2 CE, đều CC0) và trộn với tiếng phòng.

Mỗi lần đẩy lên nhánh `dark-piano`, Actions **Dark piano** tự dựng lại các bản; bản nghe (MP3
320 kbit/s) nằm ở nhánh `dark-renders`.

| Bản | Giọng, nhịp | Âm thanh |
|---|---|---|
| `dem-mua` (Mưa đêm) | Rê thứ, 66 bpm | Piano đứng tiếng nỉ (felt), hợp âm rải, cello, phòng nhỏ gần tai, tiếng rì nhẹ |
| `dem-mua-hall` | như trên | Piano đứng sáng hơn, hội trường 3,2 giây, để so không gian |
| `bong-ma` (Bóng ma) | Mi thứ (Phrygian), 76 bpm | Grand, ostinato móc tám, chuông trầm, drone, dây và violin |
| `loi-tu-biet` (Lời từ biệt) | Đô thứ, 3/4, 63 bpm | Grand, dây, contrabass, cello hát giai điệu, cao trào |
| `suong-mu` (Sương mù) | La Dorian, 52 bpm | Piano đứng thưa nốt, drone, hội trường rất dài 4,5 giây |

Cách viết một bản (`pieces/*.json`) ghi ở đầu `compose.py`. Tất cả giai điệu đều là sáng tác mới.

## Phong cách "Đêm dịu" (`dem-diu`)

Người dùng chọn bản C3 của vòng thứ tư: chậm (72-84 bpm), tay trái nhẹ (`flow`: một nốt trầm giữ, hai nốt
lắc móc đơn, buông sau một phách, pedal thay mỗi hai phách), piano đứng Yamaha gõ mềm (25 ms), màu tiếng
theo phổ trung bình của các bản mẫu (`EQ_DEM_DIU`), phòng 2,8 giây. Một bản nhạc chỉ cần ghi
`"style": "dem-diu"` cùng nhịp độ, hợp âm và giai điệu; mọi thứ khác lấy từ phong cách.

Vòng năm (người dùng: "bớt chói hơn chút"): D1 đánh giai điệu nhẹ tay hơn, không vượt 64 (chỉ dùng lớp
mẫu mềm nhất của đàn); D2 thêm tối hơn chút từ 630 Hz; D3 giai điệu hòa vào tay trái hơn; "Phố vắng" là
bài mới dài 2 phút 20 theo phong cách này (đánh như D1).

Người dùng chọn **D2** ("D2 ổn"): phong cách `dem-diu` giờ là C3 đánh nhẹ tay (giai điệu 38-60, không vượt 64)
và tối hơn chút từ 630 Hz (`EQ_DEM_DIU`; `EQ_C3` là màu tiếng của C3). D1 và D3 giữ màu tiếng C3 như lúc nghe.
App chơi phong cách này y hệt (gói `bokin_music/dark` trên nhánh của app): cùng nốt, cùng màu tiếng.

Người dùng muốn nghe rõ trên loa điện thoại và chọn **H3** ("H3 nghe rõ nhất"): `dem-diu` giờ là D2 với màu tiếng
H3 (bớt 125-400 Hz, thêm lại 1,2-2,5 kHz; trên 3 kHz vẫn tối như D2), piano hẹp hơn (0,7), ít vang hơn (0,65), to
-14 LUFS (mức YouTube). Đo qua loa điện thoại ảo: D2 nhỏ đi 9,1 dB, H3 6,2 dB; gộp hai kênh mất 2,5 so với 1,8 dB.
D1, D2, D3 giữ cách trộn cũ như lúc nghe.

## Đàn mô phỏng (vòng 10)

Người dùng: "tôi muốn dùng tiếng mô phỏng thay vì tiếng thu âm thật". `piano_model.py` tạo cây đàn bằng phép tính, không
dùng bản thu âm nào: mỗi nốt là các họa âm của dây đàn (hơi giãn như dây thật), búa nỉ (càng gõ mạnh càng sáng), tấm nỉ
che dây, thùng đàn đứng (ít phát âm dưới ~180 Hz, mỗi tần số đáp lại một khác), hai-ba dây một phím lệch nhau chút ít,
tiếng tắt hai chặng, tiếng búa và thùng gỗ. Nó ghi thành mẫu FLAC + tệp SFZ ngay khi dựng (Actions, bước "Modelled
pianos"), nên `render_samples.py` chơi nó như mọi nhạc cụ khác; không mẫu nào được lưu vào repo.

Chỉnh cho khớp: búa, nỉ và thùng đàn được dò (bình phương tối thiểu trên họa âm H2-H6 từng nhóm phím) theo tiếng H3
người dùng đã chọn và theo giai điệu của bản mẫu (H2 thấp hơn H1 khoảng 23 dB, H3 khoảng 42 dB); độ tắt theo bản mẫu
(họa âm cơ bản của giai điệu nhỏ đi 3-6 dB sau 250 ms).

| Bản | Đàn | Khác gì |
|---|---|---|
| `m1-mo-phong` | `model` | Sát H3: cùng màu tiếng, cùng cách chơi I3 |
| `m2-mo-mang` | `model-dream` | Mơ màng: dây lệch nhau rõ hơn (lung linh chậm), các dây khác ngân theo, vang dài 3,6 giây |
| `m3-ni-gan` | `model-close` | Nỉ, gần tai: nghe tiếng búa nỉ và thùng gỗ, phòng nhỏ |
| `m4-pho-vang` | `model` | Phố vắng (I4) trên đàn M1 |

Người dùng chọn **M2** ("hãy làm theo M2"): phong cách `dem-diu` giờ là M2: đàn mô phỏng `model-dream`, chơi như người
(I3: `human` 1.0 + `vary`), gõ mềm 45 ms, rộng 0,85, vang 3,6 giây (0,85). Các bản trước dùng `dem-diu` được ghim sang
`dem-diu-h3` (đàn thu âm qua màu tiếng H3), nên vẫn đúng như lúc nghe (đã kiểm tra: 24 bản, MIDI và mix.json không đổi
một byte). App chơi phong cách này y hệt: cùng nốt (Thư cuối của app = M2 từng byte MIDI), cùng mẫu tiếng đàn.

## Bài mới (vòng 11)

Người dùng: "hãy sáng tác thêm các bài hát khác". Năm bài mới theo `dem-diu` (đàn mô phỏng M2, chơi như người), sáng tác
mới hoàn toàn, mỗi bài một giọng chưa có trong app, dài 2:18-2:40, qua kiểm tra của app (không lỗi, không nốt chỏi):

| Bài | Giọng, nhịp | Nét riêng |
|---|---|---|
| `hien-mua-cu` (Hiên mưa cũ) | Si thứ, 74 bpm | Một nốt gõ hai lần như giọt mưa; cao trào lên Đô thăng 6 |
| `ru-suong` (Ru sương) | Mi thứ, nhịp ba, 72 bpm | Lời ru đung đưa; đoạn giữa sáng màu Sol trưởng, hai lượt |
| `do-khuya` (Đò khuya) | Đô thăng thứ, 76 bpm | Hợp âm rải đi lên như mái chèo; cao trào có giai điệu đôi quãng tám |
| `vang-trang-mong` (Vầng trăng mỏng) | Si giáng thứ, 70 bpm | Chậm, thưa, nốt dài; hợp âm Napoli (Đô giáng) trước lần kết cuối |
| `khoi-bep-chieu` (Khói bếp chiều) | Sol thứ, 78 bpm | Hợp âm rải lên Si giáng 5; đoạn giữa ấm (Si giáng trưởng); cao trào đôi quãng tám |

Tiếng rè ở nốt cao: người dùng nghe các bài (file MP3 128 kbit/s) bằng tai nghe và vẫn thấy rè ở cả bốn bài có nốt
cao (Hiên mưa cũ, Ru sương, Đò khuya, Khói bếp chiều). Cùng đoạn cao trào Hiên mưa cũ ở 320 kbit/s, bốn cách (đàn như
bây giờ, đàn thu âm, nốt cao đầy tiếng hơn, nốt cao yên hơn) thì cả bốn đều không rè. Nốt cao của đàn mô phỏng gần như
một âm đơn, hai bên tai hơi lệch pha nhau: MP3 128 kbit/s nén phần đó kém, tai nghe lộ ra. Nên các bài giờ được đăng ở
320 kbit/s (đúng như app lưu), đàn không đổi.

Nhưng file 320 kbit/s vẫn rè. Nguyên nhân thật: sfizz 1.2.3 phát mỗi nốt lệch 1 mẫu cho tới hết khối 1024 mẫu đầu
tiên của nốt rồi nhảy về; cú nhảy là tiếng "tách" 13-23 ms sau đầu nốt, rõ ở nốt cao gần như âm thuần (các đoạn thử dựng
trong phiên, không qua sfizz, thì không có). `render_samples.py` giờ cho sfizz chạy khối 32 mẫu (`BLOCK`): người dùng
nghe lại, "đã hết rè".

## Bài mới (vòng 12)

Người dùng: "hãy sáng tác thêm 5 bài mới nghe lạ hơn, bpm khác biệt hơn". Năm bài mới theo `dem-diu` (đàn mô phỏng
M2, chơi như người), sáng tác mới hoàn toàn, tốc độ trải từ 50 đến 112 bpm, mỗi bài một kiểu tay trái và một màu hòa âm
lạ hơn vòng 11. Qua kiểm tra của app (không lỗi, không nốt chỏi). App hiện chỉ nhận Đêm dịu từ 70 đến 84 bpm: bài nào
được chọn vào app thì phải nới khoảng đó.

| Bài | Nhịp độ, nhịp | Lạ ở đâu |
|---|---|---|
| `chuong-chua-xa` (Chuông chùa xa) | 50 bpm, 4/4 | Rê điệu thức (giai điệu ngũ cung, không có nốt dẫn), tay trái rải rồi giữ như tiếng chuông, tiếng ù trầm ở đầu và cuối |
| `guong-vo` (Gương vỡ) | 63 bpm, 3/4 | Đô thăng thứ trượt sang hợp âm cách một quãng ba (C#m-Am, C#m-Fm), giai điệu cong từ Đô thăng sang Đô |
| `song-khong-ten` (Sông không tên) | 80 bpm, 4/4 | Fa thăng Dorian (F#m-B, nốt Rê thăng), đoạn giữa tối lại về D, đoạn cuối nâng lên một cung (Son thăng Dorian) |
| `buoc-chan-tren-gac` (Bước chân trên gác) | 96 bpm, 4/4 | La thứ trên nốt La giữ dưới Si giáng (Phrygian), giai điệu từng bước và khoảng lặng trên nhịp tim, rồi vòng lặp xoay |
| `den-long-tat` (Đèn lồng tắt) | 112 bpm, 3/4 | Mỗi ô một hợp âm nên trôi chậm; Son thứ với bè trong tụt dần (Gm, Gm(maj7), Gm7, Gm6) |

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

## Tiếng đàn phong phú hơn (vòng 13)

Người dùng: "tôi muốn thay đổi tiếng piano khác để nghe phong phú hơn". Bốn cây đàn mô phỏng mới (`piano_model.py`),
cùng gốc M2, mỗi cây giàu theo một kiểu; cùng chơi Thư cuối như M2 (cùng nốt, cùng cách chơi, cùng phòng). Đo trong
phiên: phần 1,5-4 kHz (độ giàu âm bồi) so với cả tiếng; M2 -41,7 dB, các bản mẫu của người dùng -36 đến -45.

| Bản | Đàn | Khác M2 | 1,5-4 kHz | Loa điện thoại |
|---|---|---|---|---|
| `p1-grand-am` | `model-grand` | Grand ấm: trầm đầy hơn (thùng đàn từ 110 Hz), nhiều âm bồi hơn, ngân dài, rộng hơn | -34,8 | -5,8 dB |
| `p2-trong` | `model-clear` | Trong: búa cứng hơn, đầu nốt sáng rồi dịu trong 45 ms, màu theo lực tay; sáng nhất | -32,3 | -5,8 dB |
| `p3-ngan-vang` | `model-bloom` | Ngân vang: các dây khác ngân theo to hơn, ngân rất dài | -35,9 | -5,6 dB |
| `p4-go-am` | `model-wood` | Gỗ ấm: gần tai, nghe tiếng búa nỉ và gỗ, mỗi nốt một màu riêng | -36,8 | -5,4 dB |

## Mười bài trên ba tiếng đàn (vòng 14)

Người dùng giữ cả ba tiếng đàn P1, P3, P4 ("giữ cả 3 trong app") và nhờ: "tổng hợp lại 10 bài đã sáng tác và phối lại
theo các kiểu tiếng đàn khác nhau, mỗi kiểu bạn hãy tự lựa chọn 1 kiểu tiếng phù hợp", gửi WAV và MP3. Mỗi bài của vòng
11-12 giờ chơi trên một cây (`"piano"` trong bài; nốt, cách chơi, phòng như cũ):

| Tiếng đàn | Bài | Vì sao |
|---|---|---|
| Ngân vang (`model-bloom`) | Hiên mưa cũ, Vầng trăng mỏng, Chuông chùa xa | nốt dài, cần khoảng vang: mưa, trăng, chuông |
| Gỗ ấm (`model-wood`) | Ru sương, Khói bếp chiều, Sông không tên | gần, mộc: lời ru, bếp nhà, dân ca |
| Grand ấm (`model-grand`) | Đò khuya, Gương vỡ, Bước chân trên gác, Đèn lồng tắt | cần trầm đầy và cao trào đôi quãng tám, nhịp tim ở bè trầm |

Workflow giờ đăng thêm bản không nén (FLAC 16-bit) của các bài trong lượt chạy; lượt sau chỉ giữ MP3.

## Phong cách "Mờ ảo" (vòng 15)

Người dùng gửi một bản mẫu mới: "tiếp theo tôi muốn phối nhạc kiểu như này, màu sắc nhạc cụ kiểu như này". Bản mẫu chỉ
được nghe và đo trong máy làm việc (không có ở đây); học âm thanh, không chép giai điệu hay bản phối. Đo được: Mi thứ,
có màu giảm; tiếng dồn ở quãng giữa (quãng tám Đô 4 mạnh nhất), ít trầm; hai bên rất rộng; nốt tắt nhanh hơn (11 dB
một giây, các bài Đêm dịu 8); âm bồi thứ hai yếu, các âm bồi cao xuống chậm, máy nhận ra "piano" và "electric piano";
ở các đoạn dâng lên có một lớp hai nốt rung đổi nhanh (9-14 lần một giây).

Làm ở đây: đàn mô phỏng `felt-glass` (phím kính: piano nỉ có thêm "chuông" của đàn phím điện, âm bồi khớp bản mẫu trong
3 dB), lớp `tremolo` (hai nốt của hợp âm ngay trên giai điệu rung đổi theo nốt móc kép, rất nhẹ), phong cách `mo-ao`
(giai điệu thấp quanh G3-E5, tay trái nhẹ, cắt bớt trầm, rộng hơn, phòng ngắn hơn). Đo bài thử so với bản mẫu (trầm /
ấm / thân / sáng / không khí, dB): -6,0 / -1,8 / -10,6 / -39,3 / -53,3 so với -10,8 / -0,8 / -11,2 / -35,8 / -49,8; loa
điện thoại mất 4,1 dB.

| Bài | Giọng, nhịp | Nét riêng |
|---|---|---|
| `mua-tren-kinh` (Mưa trên kính) | Mi thứ, 104 bpm | Giai điệu nốt trắng nên nghe chậm một nửa; A#dim7, F#m7b5, bè trầm đi xuống E-D-C |
| `den-duong-khuya` (Đèn đường khuya) | Si thứ, 96 bpm | E#dim7, C#m7b5; bè trầm B-A-G |
| `thu-chua-gui` (Thư chưa gửi) | Son thứ, 84 bpm, nhịp ba | Mỗi ô một hợp âm; C#dim7, Am7b5 |

Người dùng: "tôi nghe chưa giống phong cách bài mẫu, hãy phân tích kĩ những nhạc cụ được dùng trong bài mẫu". Phân tích
từng lớp (nhận dạng riêng phần trầm, giữa, cao, hai bên, phần gõ, phần ngân): chỉ có đàn phím (piano pha màu đàn phím
điện); "chuông" ở dải cao và "nhịp tim" ở dải trầm đều là chính cây đàn (các bài piano khác cũng được nhận như vậy; tiếng
trầm luôn đi cùng nốt đàn); không có dây, pad, trống, tiếng mưa hay tiếng xì nền. Chỗ khác là cách đặt nốt: trầm sâu
(80-100 Hz) nhưng khoảng 130-250 Hz thưa, sáng ở 1,3-1,6 kHz, tay trái chơi nhiều hơn giai điệu. `mo-ao` giờ: tay trái
`open` (một nốt trầm sâu giữ, hợp âm rải cách trên nó một quãng tám trở lên), cân bằng tiếng theo bản mẫu (giảm
130-250 Hz, thêm 1,3-2 kHz, bỏ cắt trầm), phòng ngắn hơn (2,2 s, 0,5). Phổ dài hạn lệch bản mẫu 3,1 dB rms (trước 4,5).

## Mờ ảo trên tiếng C5, thêm oboe nền (vòng 16)

Đo độ giống bản mẫu bằng CLAP (máy nghe nhạc mã nguồn mở của LAION): các bài cũ trên đàn Kawai thu âm (C5 0,877) gần bản
mẫu hơn đàn mô phỏng (0,54-0,64). Người dùng nghe thử: "tôi thích bản c5 hơn, và dùng thêm nhạc cụ oboe làm nền".

Làm ở đây: `mo-ao` giờ là tiếng của C5 (đàn Kawai của VCSL, màu tiếng mẫu một nửa, phòng 2,8 s, tay trái `flow` nhẹ, chơi
đều), cộng lớp `oboe`: oboe của VSCO 2 CE (CC0, tải khi thu, không lưu ở đây) ngân mỗi hợp âm một nốt dài, chọn nốt màu
của hợp âm (quãng ba, sáu, bảy; không phải nốt gốc hay quãng năm khi được), gần nốt trước, giữ qua các hợp âm có chung
nốt (tối đa hai ô nhịp và 7 giây: mẫu thu bị cắt khi còn kêu), không bao giờ cách giai điệu một cung hay nửa cung; nằm
dưới giai điệu khi có chỗ (từ Đô 4), không thì ở trên. Oboe vào sau hợp âm của đàn một móc đơn, như lời đáp. Thu nguyên
bản, oboe sáng nhất bản nhạc (thêm 16-17 dB ở 1,2-5 kHz so với chỉ có đàn): giờ được làm tối như tiếng C5 (đường EQ_C3,
mức 0,75), nhỏ hơn lớp nền 3 dB, còn thêm 9 và 3 dB. Ba bài vòng 15 nâng giai điệu một quãng tám (`melody_shift`: 12),
đến chỗ giai điệu C5 nằm, để oboe nằm ấm phía dưới; bỏ lớp `tremolo`. Tiếng cũ giữ tên `mo-ao-glass`.

| Bản thử Mưa trên kính | Độ giống bản mẫu (CLAP) |
|---|---|
| Chỉ đàn C5, giai điệu thấp | 0,738 |
| Thêm oboe như thu (sáng) | 0,648 |
| Oboe tối (EQ_C3 0,6 / 0,9), nhỏ hơn 3 dB | 0,693 / 0,707 |

Oboe làm bài khác bản mẫu hơn (bản mẫu không có oboe): đó là lựa chọn của người dùng, không phải để giống bản mẫu.

## Không đệm đều, oboe mô phỏng (vòng 17)

Người dùng: "tôi muốn không có tiếng piano đệm đều phía dưới, tiếng oboe dùng loại mô phỏng".

- Đàn chỉ chơi giai điệu (`texture` `none`; pedal vẫn giữ từng hợp âm), vẫn tiếng C5.
- Oboe mô phỏng (`dark/oboe_model.py`, không dùng bản thu): mỗi nốt là các âm bồi của một lưỡi gà, mạnh yếu theo số đo
  trên oboe của VSCO (24 âm bồi đầu của từng nốt thu, nốt ở giữa lấy giữa hai nốt gần nhất; cao hơn theo đường bao phổ
  của oboe: mạnh nhất 300 Hz-1,3 kHz, tụt 15 dB ở 1,6 kHz, 30 dB ở 2 kHz). Âm bồi đọc theo tần số đang rung nên rung
  giọng đổi cả màu tiếng như oboe thật; rung 5 lần/giây, ±7 cent, bắt đầu sau khi nốt đã đứng; mỗi âm bồi tự dao động
  nhẹ (±1 dB); hơi thở 42 dB dưới tiếng. Nốt dài tới 15 giây, không phải thổi lại.
- Đo bằng CLAP (máy nghe nhạc mã nguồn mở), bỏ phần dưới 150 Hz (tiếng ù của micro): oboe mô phỏng giống oboe thu
  0,72-0,74 (chỉ theo đường bao phổ 0,64; hai cách thổi của chính oboe thu với nhau 0,89). Thêm hơi thở, rung cao độ
  nhanh, vào nốt chậm hơn hay thêm phòng đều làm kém đi.
- Hai oboe (`oboe_voices`: 2): oboe thứ nhất như vòng 16 (nốt màu của hợp âm, dưới giai điệu); oboe thứ hai thấp hơn nó
  một quãng ba tới quãng sáu, ưu tiên nốt gốc hay nốt trầm của hợp âm (không còn tay trái, nó giữ chân hòa âm), nhỏ hơn
  2 dB, lệch sang trái. Có oboe từ ô nhịp đầu tới hết bài.
- Mức: không còn tay trái, đặt 15 và 17 dB dưới đàn thì oboe chỉ thêm 1 dB vào bản nhạc, gần như không nghe thấy; giờ
  7 và 9 dB dưới đàn (thêm 3-5 dB ở 1,2-2,5 kHz).
- Tiếng vòng 16 giữ tên `mo-ao-c5`.

## Piano, cello, viola (vòng 18)

Người dùng: "hãy thử piano + cello + viola: piano chơi chính, cello đáp câu, viola chỉ giữ nền mỏng". Ba bài vòng 17 giữ
nguyên giai điệu, thêm bản `-day` (dây) theo phong cách `mo-ao-day`:

- Piano: tiếng C5, chỉ chơi giai điệu (không đệm đều).
- Cello (`cello-answer`, bè cello của VSCO 2 CE, CC0; thư viện không có cello đơn): chỗ giai điệu ngân từ ba phách trở
  lên hay nghỉ từ một phách, cello đáp vào khoảng trống đó (từ phách thứ hai của nốt ngân, hay chỗ nghỉ, tới nốt kế của
  giai điệu): nhắc lại tối đa ba nốt cuối của câu, thấp một hay hai quãng tám (quanh Son 3), mỗi nốt một phách, nốt cuối
  ngân sang câu sau một phách; cứ một lần nhắc lại thì lần sau lật ngược (bước đi soi gương, giữ trong giọng của bài).
  Nốt cuối là nốt của hợp âm; không nốt nào cách giai điệu nửa cung. Tối đa một lần đáp mỗi hai ô nhịp. Đoạn không có
  giai điệu (mở đầu, kết) cello giữ nốt trầm của hợp âm. 6 dB dưới đàn khi chơi.
- Viola (`viola-pad`): một bè mỏng, nốt màu của hợp âm, dưới giai điệu, tránh cả giai điệu và cello, 10 dB dưới đàn.
  Mẫu viola nhẹ có tiếng xì (35-42 dB dưới nhạc ở chỗ lặng): lọc bớt trên 2 kHz (`violas-dark`), còn 47-50 dB.

## Tam tấu: đàn Salamander và bài "Hồi âm" (vòng 19)

Người dùng: "tiếng piano chưa phù hợp, hãy chọn tiếng piano phù hợp hơn và sáng tác 1 bài mới phù hợp kiểu phối".

- Chọn đàn: bài mới thu với bốn cây đàn, cùng cello và viola, rồi hỏi CLAP. Cả bốn được nghe là "a sad piano trio with
  cello and viola". Salamander Grand (Yamaha C5 của Alexander Holm, CC-BY 3.0) ít "dull, muffled" nhất (0,363; Steinway
  0,373, Kawai thu nguyên 0,420, Kawai qua màu C5 0,442), ít "synth pad" nhất (0,467; 0,476, 0,532, 0,542), gần "a high
  quality classical recording" nhất so với "a low quality MIDI rendering" (0,187 với 0,201; Steinway 0,199 với 0,211;
  Kawai 0,207 với 0,265 và 0,227 với 0,298). Kawai thu nguyên còn xì (39 dB dưới nhạc). Phong cách mới `tam-tau`:
  Salamander, chơi như người (tempo thở theo câu), cello đáp câu, viola nền mỏng; tiếng thả phím và tiếng pedal của
  đàn bỏ đi. `mo-ao-day` giữ như vòng 18.
- Bài mới `hoi-am` (Hồi âm): Rê thứ, 72 bpm. Mỗi câu hai ô nhịp, kết bằng một nốt ngân ba phách và một phách nghỉ, chỗ
  cho cello đáp (lần đầu: ba nốt thở dài F-E-D nhắc lại thấp hai quãng tám). Đoạn giữa cao hơn một quãng ba trên F và
  C/E, piano chơi quãng ba, quãng sáu ở đỉnh. Mở và kết bằng hợp âm rải của piano, cello giữ nốt trầm.
- Cello không còn lặp một nốt hai lần liền trong câu đáp (vòng 18 có chỗ A3 A3 A3).
- Trong máy làm việc, đàn Salamander được chơi qua một bản SFZ phẳng (mở #define, #include, chỉ nhóm nốt, amp_veltrack
  27 như bản gốc đặt); trên GitHub, sfizz chơi bản gốc.

## Tiếng piano trầm hơn, giống keyboard (vòng 20)

Người dùng: "tôi muốn tiếng piano trầm hơn nghe giống keyboard hơn". "Hồi âm" thu lại với ba cách, cùng cello và viola:

| Cách | CLAP: "a warm, deep, dark piano" | Giống bài mẫu (CLAP) |
|---|---|---|
| Salamander như vòng 19 | 0,578 | 0,746 |
| K1: Rhodes (jRhodes3d, 1977 Rhodes Mark I), cao trên 4 kHz dịu bớt | 0,593 | 0,732 |
| K2: Salamander kiểu đàn keyboard: ấm hơn dưới 400 Hz, tối từ 1,2 kHz (`EQ_KEYS`), hẹp hơn, chút chorus, gõ trong khoảng lực hẹp hơn | 0,610 | 0,769 |
| K3: K2 với Rhodes chơi chồng, 4 dB dưới đàn (`piano_layer`) | 0,637 | 0,815 |

Rhodes riêng được nghe rõ nhất là "a Rhodes electric piano", nhưng với dây thì thành "piano with a synth pad". K3 thành
phong cách `tam-tau-phim`; "Hồi âm" giờ dùng nó. jRhodes3d: dùng tự do trong nhạc; mẫu thu (CC BY-NC 4.0) chỉ tải khi
thu, không lưu ở đây.

## Bốn bài mới cho `tam-tau-phim` (vòng 21)

Người dùng chọn K1 (piano tối kiểu keyboard, Rhodes chơi chồng): "tôi thích bản 1, hãy sáng tác thêm". Bốn bài mới, viết
cho kiểu hỏi-đáp: câu nào cũng kết bằng một nốt ngân (hay ngân rồi nghỉ) để cello đáp; mở và kết bằng hợp âm rải.
Bản thu "Hồi âm" trên GitHub (sfizz thật) và bản thu trong máy làm việc giống nhau 0,999 (CLAP).

| Bài | Giọng, nhịp | Nét riêng | CLAP "a warm, deep, dark piano" |
|---|---|---|---|
| `ngo-nho` (Ngõ nhỏ) | La thứ, 66 bpm | Nốt cảm Son# ngân trên E7 cho cello đáp; đoạn giữa Đô trưởng, piano chơi quãng bốn, quãng ba ở đỉnh; F#m7b5, Dm6 | 0,646 |
| `ben-vang` (Bến vắng) | Fa thứ, nhịp ba, 80 bpm | Câu bốn ô, ô cuối ngân trọn, câu sau vào sau một phách nghỉ: cello đáp qua vạch nhịp; đoạn giữa La giáng trưởng hát hai lần | 0,639 |
| `chuyen-tau-dem` (Chuyến tàu đêm) | Fa thăng thứ, 92 bpm | Giai điệu móc đơn như bánh xe trên ray, dừng mỗi hai ô cho cello; đoạn giữa La trưởng hai lần, lần sau qua E7 | 0,642 |
| `mua-dong-nam-ay` (Mùa đông năm ấy) | Si giáng thứ, 60 bpm | Chậm nhất, giai điệu thấp hơn (Fa 4 tới La giáng 5, Rê giáng 6 ở đỉnh); Ebm6, Gbmaj7 | 0,630 |

## Không gian u tối (nhánh `dark-khac`, vòng k1)

Kiểu nhạc u tối thứ hai, làm song song với piano u buồn: **dark ambient** — âm nền kéo dài, chuyển
động chậm, chuông trầm, gần như không có giai điệu. Người dùng chọn kiểu này ("Không gian u tối").
Mọi tiếng đều tự tạo bằng `ambient.py` (không dùng bản thu, không cần giấy phép), được dựng cùng các
bản nhạc như đàn mô phỏng:

- `amb-pad`: nền synth tối, ba sóng răng cưa mỗi bên lệch nhau vài cent, bộ lọc mở ra đóng vào thật
  chậm (17-29 giây một nhịp thở), giữ được bao lâu cũng được (vòng lặp 30 giây);
- `amb-choir`: dàn hợp xướng xa hát "oo", tám giọng, mỗi giọng rung nhẹ riêng;
- `amb-sub`: nốt trầm rất sâu; `amb-bell`: chuông lớn gõ dùi nỉ, tiếng ngân hai quãng tám dưới;
  `amb-glass`: chuông thủy tinh/bát hát, gần như âm thuần.

Một bản chỉ cần ghi `"style": "khong-gian"` (và `"family": "dark-khac"`): hợp âm, các lớp
(`pad`, `choir`, `sub`, `toll`, `bells`, `glass`, `drone`), `dyn`, `swell` (lớn dần trong đoạn),
`melody` (trên chuông) và `answer` (chuông trầm đáp lại). Phòng 6,5 giây, -16 LUFS.

| Bản | Giọng, nhịp | Âm thanh |
|---|---|---|
| `k1-suong-den` (Sương đen) | Rê thứ, 52 bpm | Nền pad, bass sâu, chuông trầm điểm thưa, vài nốt chuông |
| `k2-ham-mo` (Hầm mộ) | Đô thứ, 46 bpm | Hợp xướng xa "oo", drone, chuông đổ mỗi hợp âm, kiểu gothic |
| `k3-day-sau` (Đáy sâu) | Mi thứ, 50 bpm | Chuông thủy tinh gọi, chuông trầm đáp (hỏi-đáp), nền pad |

Bản nghe ở nhánh `dark-khac-renders` (Actions **Dark khac** chỉ dựng các bản của nhánh này).

## Không gian u tối, thêm sáu bản (vòng X2)

Người dùng: "hãy làm thêm nhiều phiên bản hơn". Thêm hai tiếng tự tạo: `amb-wind` (gió lùa trong hang,
thoảng ra nốt nhạc, từng cơn, không có gì trên 2 kHz nên không rít) và `amb-pulse` (tiếng tim đập trầm);
ba lớp mới: `wind`, `pulse` (nhịp tim, `pulse_beats`), `shimmer` (chuông thủy tinh cao, khẽ, rải ngẫu nhiên
trên hợp âm); bản nhạc chọn được tầm cao của nền (`pad_range`) và hợp xướng (`choir_range`).

| Bản | Giọng, nhịp | Âm thanh |
|---|---|---|
| `k4-gio-hoang` (Gió hoang) | Si thứ, 48 bpm | Gió lùa từng cơn, nền tối, chuông xa |
| `k5-nha-tho-bo-hoang` (Nhà thờ bỏ hoang) | La thứ, 44 bpm | Hợp xướng trầm, dày, chuông lớn đổ |
| `k6-troi-trong-dem` (Trôi trong đêm) | Fa thứ, 54 bpm | Nhiều giai điệu nhất: chuông thủy tinh hát, chuông trầm đáp |
| `k7-nhip-tim` (Nhịp tim) | Son thứ, 56 bpm | Tim đập trầm, nhanh dần ở đoạn căng rồi chậm lại |
| `k8-bang-gia` (Băng giá) | Đô thăng thứ, 50 bpm | Thủy tinh cao lạnh và bass sâu, khoảng giữa bỏ trống |
| `k9-vuc-tham` (Vực thẳm) | Rê thứ, 42 bpm | Tối và trầm nhất, không có gì cao |

## Không gian u tối, thêm tám bản (vòng X3)

Người dùng: "tôi rất thích các phiên bản bạn tạo, hãy tạo thêm cho tôi nhiều phiên bản khác". Thêm hai
tiếng tự tạo: `amb-organ` (đàn ống ở xa trong nhà đá, ống sáo mềm, không có gì trên 3,5 kHz) và
`amb-drop` (giọt nước rơi xuống vũng trong hang); hai lớp mới: `organ`, `drops` (`drops_per_bar`).

| Bản | Giọng, nhịp | Âm thanh |
|---|---|---|
| `k10-hang-nuoc` (Hang nước) | Mi thứ, 50 bpm | Giọt nước rơi, gió trong hang, nền tối |
| `k11-dan-ong-xa` (Đàn ống xa) | Rê thứ, 44 bpm | Đàn ống xa, chuông lớn, hợp xướng vào giữa bài |
| `k12-nghia-trang-suong` (Nghĩa trang sương) | Son thăng thứ, 46 bpm | Hợp xướng, thủy tinh cao, chuông xa, gần như không có trầm |
| `k13-thanh-pho-chet` (Thành phố chết) | La thứ, 52 bpm | Tim đập chậm, gió, chuông hát một giai điệu cô đơn, chuông trầm đáp |
| `k14-giac-mo-toi` (Giấc mơ tối) | Si giáng thứ, 54 bpm | Nhiều giai điệu: thủy tinh hát, hợp xướng, nền |
| `k15-bien-dem` (Biển đêm) | Fa thăng thứ, 48 bpm | Nền và gió dâng lên hạ xuống như sóng dài |
| `k16-den-cuoi-ham` (Đèn cuối hầm) | Đô thứ, 50 bpm | Đàn ống, tim đập, thủy tinh gọi, chuông trầm đáp; kết sáng ở Mi giáng |
| `k17-tuyet-roi` (Tuyết rơi) | La thứ, 52 bpm | Thủy tinh cao khẽ, giọt nước như bông tuyết, không có trầm |

## Không gian u tối, thêm tám bài (vòng X4)

Người dùng: "hãy sáng tác thêm cho tôi". Thêm hai tiếng tự tạo: `amb-box` (hộp nhạc cũ, mỗi phím lệch
tông một chút) và `amb-bowl` (bát hát xoay bằng dùi gỗ, rung chậm); hai lớp: `box` (giai điệu trên hộp
nhạc), `bowl` (`bowl_every`). Sửa thêm: tiếng vang (hall) làm một nốt gần như thuần (drone, bát hát) lệch
hẳn sang một bên tai, tới 7 dB; mix sheet nào ghi `"hall": {"even": true}` thì bên phải của tiếng vang được
làm từ bên trái qua các bộ lọc allpass (cùng độ to ở mọi tần số), hai bên đều nhau. Kiểu `khong-gian` bật
nó; các bản piano không đổi.

| Bản | Giọng, nhịp | Âm thanh |
|---|---|---|
| `k18-hop-nhac-cu` (Hộp nhạc cũ) | Rê thứ, nhịp ba, 60 bpm | Hộp nhạc lệch tông chơi bài ru chậm, nền tối |
| `k19-bat-hat` (Bát hát) | Đô thăng thứ, 46 bpm | Bát hát rung chậm, drone, gió; tĩnh như thiền |
| `k20-phong-tre-bo-hoang` (Phòng trẻ bỏ hoang) | La thứ, nhịp ba, 54 bpm | Hộp nhạc, giọt nước, hợp xướng xa; rợn |
| `k21-loi-nguyen` (Lời nguyện) | Fa thứ, 44 bpm | Hợp xướng, đàn ống trầm, bát hát |
| `k22-rung-dem` (Rừng đêm) | Son thứ, 50 bpm | Gió, tim đập khẽ, thủy tinh lấp lánh, chuông hỏi-đáp |
| `k23-mat-bao` (Mắt bão) | Mi thứ, 56 bpm | Cơn bão dâng, giữa bài lặng hẳn, rồi bão lại |
| `k24-ky-uc-mo` (Ký ức mờ) | Si thứ, 58 bpm | Nhiều giai điệu nhất: hộp nhạc hát, chuông đáp |
| `k25-lang` (Lặng) | La giáng thứ, 40 bpm | Thưa nhất: bass, bát hát, chuông lớn hai lần |

## Không gian u tối, thêm mười bài (vòng X5)

Người dùng: "hãy sáng tác thêm cho tôi nhiều bài nữa". Thêm ba tiếng tự tạo: `amb-bowed` (dàn dây trầm kéo
vĩ, làm từ các họa âm qua cộng hưởng thân đàn, mỗi người chơi một độ rung riêng), `amb-bowsolo` (một cây dây
hát giai điệu) và `amb-thunder` (sấm rền ở xa, chỉ phần rền, rất trầm); ba lớp: `strings`, `solo` (giai điệu
trên cây dây, ngân liền nốt), `thunder` (`thunder_odds`).

| Bản | Giọng, nhịp | Âm thanh |
|---|---|---|
| `k26-sam-xa` (Sấm xa) | Rê thứ, 50 bpm | Sấm rền xa, nền tối, vài nốt chuông |
| `k27-day-tram` (Dây trầm) | Đô thứ, 48 bpm | Dàn dây trầm, một cây dây hát giai điệu buồn, kiểu nhạc phim |
| `k28-hai-dang-tat` (Hải đăng tắt) | La thứ, 46 bpm | Gió biển, chuông trầm như còi sương, thủy tinh xa |
| `k29-gieng-co` (Giếng cổ) | Fa thăng thứ, 44 bpm | Giọt nước vọng sâu, bát hát, nền rất trầm |
| `k30-ru-trong-bong-toi` (Ru trong bóng tối) | Mi thứ, nhịp ba, 58 bpm | Hộp nhạc hát bài ru, dây trầm đưa nhịp ba |
| `k31-tau-ma` (Tàu ma) | Si giáng thứ, 50 bpm | Dây trầm đung đưa, gió, nhịp chậm, chuông từ xa |
| `k32-binh-minh-xam` (Bình minh xám) | Son thứ, 52 bpm | Vẫn tối nhưng mở dần ra, hợp xướng, dây, thủy tinh |
| `k33-thanh-duong-chim` (Thánh đường chìm) | Mi giáng thứ, 44 bpm | Đàn ống như nghe qua nước, giọt nước, chuông |
| `k34-bong-nguoi` (Bóng người) | La thứ, 54 bpm | Dây trầm bò từng nửa cung, tim đập, hỏi-đáp |
| `k35-dem-dai` (Đêm dài) | Rê thứ, 48 bpm | Dài nhất (gần 4 phút), đi qua gần hết các tiếng |

## Nhạc ngủ (vòng X6, kiểu `ngu-ngon`)

Người dùng: "hãy sáng tác thêm cho tôi nhiều bài nữa, phù hợp cho các người nghe có thể nghe để ngủ". Kiểu
mới `ngu-ngon`: cùng các tiếng của `khong-gian`, nhưng không có gì đột ngột (không sấm, không tim đập, không
chuông gõ), phòng vang dài và mềm hơn (7,5 giây), nhỏ hơn (-17 LUFS), mỗi bài dài 5-6 phút, đều từ đầu đến
cuối. Thêm tiếng `amb-waves` (biển đêm ở xa, từng đợt sóng chậm như hơi thở, không có gì trên 1,2 kHz) và lớp
`felt`: piano nỉ "mơ màng" của phiên piano (`model-dream`), chạm thật khẽ, các nốt hợp âm lên xuống chậm
(`felt_beats`), hoặc chơi giai điệu nếu đoạn có `melody`.

| Bản | Tên tiếng Anh | Giọng, nhịp | Âm thanh |
|---|---|---|---|
| `k36-ru-bien-dem` (Ru biển đêm) | Sea Lullaby | La thứ, 50 bpm, 5:48 | Sóng biển xa, nền, piano nỉ khẽ |
| `k37-may-dem` (Mây đêm) | Night Clouds | Rê thứ, 48 bpm, 5:43 | Nền và hợp xướng xa trôi chậm, thủy tinh hiếm |
| `k38-ngu-duoi-sao` (Ngủ dưới sao) | Sleeping Under the Stars | Mi thứ, 52 bpm, 5:18 | Piano nỉ đưa nhẹ như bài ru |
| `k39-vong-tay-dem` (Vòng tay đêm) | Embrace of the Night | Đô thứ, 48 bpm, 5:42 | Dây trầm êm, một lần cây dây hát |
| `k40-hoi-tho-cham` (Hơi thở chậm) | Slow Breathing | Rê thứ, 44 bpm, 5:30 | Sóng theo nhịp thở chậm, bát hát |
| `k41-lua-tan` (Lửa tàn) | Dying Embers | Son thứ, 46 bpm, 5:15 | Đàn ống rất khẽ, piano nỉ, nhỏ dần |
| `k42-troi-ve-giac-mo` (Trôi về giấc mơ) | Drifting into Dreams | Si thứ, nhịp ba, 54 bpm, 4:46 | Hộp nhạc hát ru, dây trầm đưa nhịp ba |
| `k43-giac-ngu-sau` (Giấc ngủ sâu) | Deep Sleep | Rê thứ, 42 bpm, 6:09 | Tĩnh nhất: nền, bass, hợp xướng rất xa |

## Hai hướng mới (vòng X7)

Người dùng: "hãy sáng tác thêm 2 bản nữa theo hướng khác". Hai kiểu mới, cùng bộ máy `ambient.py`:
- `toi-nhip` (darkwave): bass synth đập móc đơn (`amb-synbass`, bộ lọc đóng nhanh sau khi nốt vang), arp synth
  lạnh (`amb-arp`), trống nhẹ đều (`amb-kick`, `amb-snare`, chải hơn là đánh), nền lạnh; phòng nhỏ 2,5 giây.
- `dien-anh` (nhạc phim u tối): dàn dây, cây dây hát, hợp xướng, timpani dùi mềm (`amb-timpani`, các mode của
  nồi trống), dâng qua một hồi trống cuộn tới cao trào với chuông lớn rồi lắng; phòng 4,5 giây.
Trống và timpani chơi hết tiếng dù nốt ngắn (`loop_mode=one_shot`).

| Bản | Tên tiếng Anh | Giọng, nhịp | Âm thanh |
|---|---|---|---|
| `k44-thanh-pho-khong-ngu` (Thành phố không ngủ) | Sleepless City | La thứ, 96 bpm, 2:43 | Darkwave: bass synth, arp lạnh, trống nhẹ |
| `k45-truoc-con-bao` (Trước cơn bão) | Before the Storm | Rê thứ, 60 bpm, 3:12 | Nhạc phim: dây, hợp xướng, timpani, cao trào |

## Bốn hướng tự chọn (vòng X8)

Người dùng: "hãy sáng tác thêm nhiều bài nữa, hướng bạn tự đề xuất". Bốn hướng, mỗi hướng hai bài:
- Tân cổ điển u tối (`dien-anh`): piano nỉ hát, cây dây trầm đáp lại (`answer_on: "solo"`), hoặc piano nỉ
  rải hợp âm dưới cây dây hát.
- Lofi tối (kiểu mới `lofi-toi`, phòng ấm 1,8 giây): nhịp chậm nhẹ, piano nỉ chơi cả hợp âm (`felt_chords`),
  bass mỗi phách (`bass_step: 1`).
- Phương Đông u tối: tiếng mới `amb-pluck`, dây gảy (Karplus-Strong, tối dần khi tắt; nghe gần đàn hạc hơn
  đàn tranh), giai điệu ngũ cung có nốt luyến nhỏ, hoặc rải hợp âm chậm (`pluckarp`); bát hát, drone.
- Darkwave và nhạc phim: mỗi kiểu một bài.
Thêm `tune_on`: đoạn tự chọn nhạc cụ cho giai điệu.

| Bản | Tên tiếng Anh | Hướng | Giọng, nhịp |
|---|---|---|---|
| `k46-thu-khong-gui` (Thư không gửi) | The Unsent Letter | Tân cổ điển | Si thứ, 58 bpm |
| `k47-hanh-lang-trong` (Hành lang trống) | Empty Corridor | Tân cổ điển | Mi thứ, 62 bpm |
| `k48-den-duong-3-gio-sang` (Đèn đường 3 giờ sáng) | 3 AM Streetlight | Lofi tối | La thứ, 72 bpm |
| `k49-quan-khuya` (Quán khuya) | Last Café Open | Lofi tối | Rê thứ, 76 bpm |
| `k50-den-hoang` (Đền hoang) | Forgotten Temple | Phương Đông | La ngũ cung, 54 bpm |
| `k51-suong-nui` (Sương núi) | Mountain Mist | Phương Đông | Mi thứ, 50 bpm |
| `k52-tin-hieu-cuoi` (Tín hiệu cuối) | Last Transmission | Darkwave | Mi thứ, 88 bpm |
| `k53-vuong-quoc-sup-do` (Vương quốc sụp đổ) | Fallen Kingdom | Nhạc phim | Đô thứ, 56 bpm |

## Nhạc ngủ có giai điệu ngẫu hứng (vòng X9)

Người dùng: "tôi muốn những bài âm thanh u tối nhưng dễ nghe để ngủ hơn, có thể thêm những giai điệu ngẫu
hứng". Thêm `improvise()` trong `ambient.py`: một giai điệu tự nghĩ ra khi chơi, như người dạo đàn chậm lúc
đêm: từng câu 2-4 ô, nghỉ 1-3 ô giữa các câu; mỗi nốt 1-3 phách, đi một hai bậc của thang âm (thỉnh thoảng
nhảy quãng ba, quãng bốn), lên ở nửa đầu câu, xuống ở nửa sau; mỗi câu bắt đầu từ giữa tầm cữ; nốt ngân
(từ 2 phách) và nốt cuối câu luôn là nốt của hợp âm, nên không chỏi. Lớp `improv` (nhạc cụ: `felt`, `glass`,
`pluck`, `box`, `bells`, `solo`), `improv_range`, `improv_density`, thang âm của bài (`mode`: aeolian,
dorian, lydian, major, pentatonic), `seed`. Hòa âm êm hơn: hợp âm có quãng chín, bảy trưởng, không còn nửa
cung Phrygian chỏi; kiểu `ngu-ngon`.

| Bản | Tên tiếng Anh | Giọng | Ngẫu hứng trên |
|---|---|---|---|
| `k54-dao-dem` (Dạo đêm) | Night Wandering | La thứ, 54 bpm | piano nỉ |
| `k55-song-va-thuy-tinh` (Sóng và thủy tinh) | Glass and Waves | Rê Dorian, 50 bpm | chuông thủy tinh, sóng xa |
| `k56-day-dan-trong-mo` (Dây đàn trong mơ) | Strings in a Dream | Mi thứ, 50 bpm | cây dây, dây trầm |
| `k57-mua-sao-bang-cham` (Mưa sao băng chậm) | Slow Meteor Shower | Si Dorian, 52 bpm | đàn dây gảy |
| `k58-ngon-nen-cuoi` (Ngọn nến cuối) | The Last Candle | Đô thứ, 48 bpm | piano nỉ, đàn ống xa |
| `k59-thuyen-dem` (Thuyền đêm) | Night Boat | Son Dorian, 52 bpm | piano nỉ, sóng, dây |
| `k60-khu-vuon-toi` (Khu vườn tối) | Dark Garden | Đô thăng thứ, 50 bpm | thủy tinh rồi dây gảy |
| `k61-giac-mo-khong-ten` (Giấc mơ không tên) | Nameless Dream | Rê thứ, 46 bpm | piano nỉ, cây dây, thủy tinh lần lượt |

### Người dùng chấm điểm (sau vòng X8)

- Không gian u tối X1-X37: 28 thích, 8 tạm được, không bài nào không thích. Tạm được: Nhà thờ bỏ hoang, Vực
  thẳm, Biển đêm, Đàn ống xa, Đèn cuối hầm, Nghĩa trang sương, Tàu ma, Thành phố không ngủ (darkwave). Trước
  cơn bão (nhạc phim) được thích.
- Nhạc ngủ S1-S8: 6 thích; tạm được: Giấc ngủ sâu (tĩnh nhất), Vòng tay đêm.
- Vòng X8: không thích hai bài lofi (có trống) và hai bài phương Đông (dây gảy `amb-pluck`); tân cổ điển,
  darkwave, nhạc phim: tạm được.
- Nên: hộp nhạc, bát hát, thủy tinh, gió, giọt nước, dây trầm, piano nỉ, sóng, hợp xướng. Tránh: trống/nhịp
  lofi, dây gảy; đàn ống chỉ "tạm được". Vì vậy vòng X9 đổi ngẫu hứng dây gảy sang hộp nhạc (Mưa sao băng
  chậm, Khu vườn tối), Ngọn nến cuối bỏ đàn ống, dùng dây trầm và nền.

## Bảy album, và vòng X10 (nhạc ngủ ngẫu hứng, tập 3)

56 bài người dùng thích hoặc "tạm được" đã được chia thành 7 album để phát hành (Echoes of the Deep, Hollow
Places, Night Weather, Faded Memory, Before the Storm, Sleep in the Dark Vol. 1 và 2), các file chỉ còn tên
bài. **Từ nay không đổi cách `ambient.py` chơi các bài cũ**: bản phát hành phải dựng lại y như cũ; thêm gì mới
thì thêm tuỳ chọn mới.

Vòng X10, tám bài ngủ ngẫu hứng trên những tiếng người dùng thích nhất (hộp nhạc, thủy tinh, cây dây; sóng,
gió, giọt nước, bát hát, hợp xướng), không trống, không dây gảy, không đàn ống:

| Bản | Tên tiếng Anh | Giọng | Ngẫu hứng trên |
|---|---|---|---|
| `k62-tuyet-dem` (Tuyết đêm) | Snow at Night | La thứ | hộp nhạc |
| `k63-hang-sau-yen-tinh` (Hang sâu yên tĩnh) | Quiet Cavern | Mi Dorian | thủy tinh, giọt nước, bát hát |
| `k64-hai-dang-xa` (Ngọn hải đăng xa) | Far Lighthouse | Rê thứ | cây dây, sóng |
| `k65-gio-qua-dong-co` (Gió qua đồng cỏ) | Wind over the Moor | Si thứ | thủy tinh, gió |
| `k66-phong-nhac-cu` (Phòng nhạc cũ) | The Old Music Room | Fa thăng thứ | hộp nhạc, dây trầm |
| `k67-dem-bat-hat` (Đêm bát hát) | Night of Singing Bowls | Đô thăng Dorian | thủy tinh, bát hát |
| `k68-anh-trang-tren-ho` (Ánh trăng trên hồ) | Moonlight on the Lake | Son thứ | hộp nhạc rồi thủy tinh |
| `k69-giac-mo-hop-xuong` (Giấc mơ hợp xướng) | Choir Dream | Fa thứ | cây dây, hợp xướng |

### Album 8: Sleep in the Dark, Vol. 3

Người dùng thích cả tám bài vòng X10; album 8 gồm đủ tám, theo thứ tự: Snow at Night, Wind over the Moor,
Moonlight on the Lake, Quiet Cavern, The Old Music Room, Far Lighthouse, Night of Singing Bowls, Choir Dream
(39 phút 31 giây, -17 LUFS). Bìa vẽ bằng máy (trăng trên hồ), file chỉ còn tên bài.

## Hướng mới: ambient piano u buồn (vòng X11, kiểu `piano-am`)

Người dùng gửi năm bài mẫu để lấy ý tưởng (chỉ phân tích chất âm và cách phối, không chép gì; bài mẫu không
đưa vào kho). Điểm chung: piano là chính, rải hợp âm nhẹ và đều (khoảng 5 nốt mỗi giây), giai điệu đơn giản
ở giữa bàn phím, nền synth mềm và tiếng ngân "ừm", có bài có bass rất sâu; buồn mà ấm (trưởng đi với thứ
song song), không trống, vang dài; bài ngắn 1,5-2 phút, vào dần 15-20 giây rồi giữ đều; to hơn (-10 đến
-19 LUFS), hẹp hơn. Kiểu mới `piano-am`: piano mô phỏng `model-dream` (không lọc), lớp `pianoarp` (bass rồi
hợp âm lên xuống móc đơn), giai điệu ngẫu hứng một lần rồi lặp lại (`improv: keys`, `motif`), hợp xướng xa,
nền, sub; phòng 5 giây; -14 LUFS.

| Bản | Tên tiếng Anh | Giọng, nhịp |
|---|---|---|
| `k70-thu-gui-mua-dong` (Thư gửi mùa đông) | Letter to Winter | Mi thứ, 72 bpm |
| `k71-cho-anh-sang` (Chờ ánh sáng) | Waiting for the Light | Son trưởng, 70 bpm |
| `k72-day-ho` (Đáy hồ) | Beneath the Lake | Si thứ, 68 bpm, sub rất sâu |
| `k73-sao-roi-cham` (Sao rơi chậm) | Slow Falling Stars | Rê trưởng, 74 bpm |
| `k74-hoi-tho-cuoi-thu` (Hơi thở cuối thu) | Last Breath of Autumn | La thứ, 70 bpm, dây trầm |
| `k75-anh-sang-xa` (Ánh sáng xa) | Distant Light | Fa thăng thứ, 76 bpm |

## Vòng X12: piano "điện tử" (kiểu `piano-dt`)

Người dùng nghe X11: "tiếng piano và độ vang chưa giống lắm, bài mẫu nghe cảm giác điện tử hơn". So bằng
LAION CLAP, bài mẫu nghiêng về piano số / piano điện, chorus, vang plate sáng có lớp ngân cao, synth cao như
không khí, tiếng đảo ngược, tiếng vọng. Kiểu mới `piano-dt` (tất cả là tùy chọn mới, bài cũ không đổi):

- `amb-epiano`: piano điện tự tổng hợp (FM hai bộ dao động như tiếng thanh kim loại của Rhodes, sáng lúc gõ
  rồi dịu đi; không dùng bản thu nào), thêm chorus; piano mô phỏng `model-dream` lót nhẹ bên dưới
  (`keys_layer`) cho ra tiếng "piano số".
- Tiếng vọng qua lại hai tai (delay chấm dôi móc đơn, `keys_echo`, hiệu ứng `echo` mới trong mixer).
- Lớp `air` (synth cao `amb-air`), lớp `swells` (nốt piano điện đảo ngược dâng lên vào mỗi hợp âm).
- Vang plate (`"plate": true`): tiếng cao ngân gần dài bằng tiếng giữa, phòng 4 giây.

Sáu bài X11 làm lại bằng bộ tiếng này, cùng bản nhạc, để so trực tiếp: `k76-thu-gui-mua-dong-dien-tu`,
`k77-cho-anh-sang-dien-tu`, `k78-day-ho-dien-tu`, `k79-sao-roi-cham-dien-tu`, `k80-hoi-tho-cuoi-thu-dien-tu`,
`k81-anh-sang-xa-dien-tu` (tên tiếng Anh thêm "(Electronic)").

## Vòng X13: quay lại ambient piano kiểu X11 (`piano-am`)

Người dùng nghe X12: "tôi vẫn thích kiểu cũ hơn, hãy quay lại sáng tác kiểu cũ". Sáu bài mới theo đúng kiểu
X11 (piano mô phỏng rải hợp âm, giai điệu ngẫu hứng một lần rồi lặp, nền, sub, hợp xướng hoặc dây ở giữa bài,
phòng 5 giây, -14 LUFS), giọng và vòng hợp âm khác:

| Bản | Tên tiếng Anh | Giọng, nhịp |
|---|---|---|
| `k82-mua-tren-mai-hien` (Mưa trên mái hiên) | Rain on the Porch | Rê thứ, 70 bpm |
| `k83-o-cua-sang-den` (Ô cửa sáng đèn) | A Lit Window | Đô trưởng, 72 bpm, chuông lấp lánh |
| `k84-con-duong-ve-nha` (Con đường về nhà) | The Road Home | La trưởng, 74 bpm, dây |
| `k85-gio-dau-dong` (Gió đầu đông) | First Winter Wind | Đô thứ, 68 bpm, sub rất sâu |
| `k86-trang-tren-song` (Trăng trên sông) | Moonlight on the River | Son thứ, 70 bpm, dây và hợp xướng |
| `k87-giac-mo-mua-ha` (Giấc mơ mùa hạ) | Summer Dream | Fa trưởng, 72 bpm, chuông lấp lánh |

## Vòng X14: nhạc ngủ như album 6-8 (`ngu-ngon`)

Người dùng: "tôi thích kiểu giống album 6-7-8" (Sleep in the Dark). Tám bài ngủ mới, chậm (44-52 bpm), khoảng
4,5-5,5 phút, mỗi bài một giai điệu ngẫu hứng trên những tiếng người dùng thích (hộp nhạc, chuông thủy tinh,
cây dây, piano nỉ, bát hát), không trống, không đàn gảy, không organ:

| Bản | Tên tiếng Anh | Giọng, nhịp |
|---|---|---|
| `k88-mua-dem-tren-la` (Mưa đêm trên lá) | Night Rain on Leaves | Mi thứ, 50 bpm, giọt nước, chuông thủy tinh |
| `k89-song-ngan` (Sông Ngân) | The Milky Way | Rê thứ, 48 bpm, lấp lánh, hộp nhạc |
| `k90-gio-bien-dem` (Gió biển đêm) | Night Sea Breeze | Đô thứ, 50 bpm, sóng và gió, cây dây |
| `k91-rung-thong-ngu` (Rừng thông ngủ) | Sleeping Pines | Son thứ, 52 bpm, dàn dây, piano nỉ |
| `k92-may-troi-cham` (Mây trôi chậm) | Slow Drifting Clouds | Fa thứ, 46 bpm, hợp xướng, chuông thủy tinh |
| `k93-bat-hat-duoi-trang` (Bát hát dưới trăng) | Bowls under the Moon | La thứ, 44 bpm, bát hát, hộp nhạc |
| `k94-can-phong-am` (Căn phòng ấm) | The Warm Room | Si thứ, 50 bpm, dàn dây, hộp nhạc |
| `k95-ve-lai-giac-mo` (Về lại giấc mơ) | Back into the Dream | Fa thăng thứ, 48 bpm, sóng, cây dây |
| `k96-dom-dom` (Đom đóm) | Fireflies | Đô thăng thứ, 50 bpm, lấp lánh, chuông thủy tinh rồi hộp nhạc |
| `k97-hoi-am-cuoi-ngay` (Hơi ấm cuối ngày) | Last Warmth of the Day | Son thăng thứ, 48 bpm, dàn dây, hộp nhạc rồi piano nỉ |

Hai bài cuối (`k96`, `k97`) người dùng xin thêm "để đủ album".

### Album 9: Sleep in the Dark, Vol. 4

Người dùng chấm vòng X14: sáu bài thích, bốn bài tạm được, không bài nào không thích; album 9 gồm đủ mười, theo
thứ tự: Night Rain on Leaves, Night Sea Breeze, Slow Drifting Clouds, The Milky Way, The Warm Room, Sleeping
Pines, Fireflies, Back into the Dream, Last Warmth of the Day, Bowls under the Moon (49 phút 48 giây, -17 LUFS).
Bìa vẽ bằng máy (rừng thông và đom đóm), file chỉ còn tên bài.

## Vòng X15: album 10, nhạc ngủ điện tử (kiểu `ngu-dt`)

Người dùng: "hãy sáng tác album thứ 10, hãy thử phong cách âm thanh điện tử hơn, vẫn là nhạc ambient phù hợp
ngủ". Kiểu mới `ngu-dt`: khung nhạc ngủ (chậm, êm, -17 LUFS, không trống) với bộ tiếng điện tử của vòng X12 làm
dịu lại: piano điện tự tạo tối và khẽ (lọc 3,2 kHz) hát giai điệu ngẫu hứng, tiếng vọng qua lại dài (1,5 phách);
chuỗi nốt synth chậm (`arp`, lọc 1,8 kHz, có tiếng vọng); lớp synth cao `air` rất nhỏ; tiếng đảo ngược
`swells`; vang plate 6,5 giây. Tùy chọn mới `tones` (giọng riêng cho từng lớp, có `echo_beats`). Bản đầu đo thấy
sáng hơn các album ngủ trước, nên lớp `air` hạ xuống -10 dB, `swells` -3 dB.

| Bản | Tên tiếng Anh | Giọng, nhịp |
|---|---|---|
| `k98-tin-hieu-sao-xa` (Tín hiệu sao xa) | Distant Star Signal | Mi thứ, 50 bpm |
| `k99-thanh-pho-ngu` (Thành phố ngủ) | Sleeping City | La thứ, 52 bpm |
| `k100-quy-dao-cham` (Quỹ đạo chậm) | Slow Orbit | Rê thứ, 48 bpm |
| `k101-neon-duoi-mua` (Đèn neon dưới mưa) | Neon in the Rain | Đô thứ, 50 bpm |
| `k102-tram-vu-tru-ngu` (Trạm vũ trụ ngủ) | Sleeping Space Station | Fa thăng thứ, 46 bpm |
| `k103-song-radio-dem` (Sóng radio đêm) | Night Radio Waves | Si thứ, 50 bpm |
| `k104-bau-troi-so` (Bầu trời số) | Digital Sky | Son thứ, 48 bpm |
| `k105-bien-sao-dien-tu` (Biển sao điện tử) | Electric Sea of Stars | Đô thăng thứ, 50 bpm |
| `k106-giac-mo-tong-hop` (Giấc mơ tổng hợp) | Synthetic Dream | Fa thứ, 50 bpm |
| `k107-tat-den` (Tắt đèn) | Lights Out | Rê thứ, 44 bpm |

### Album 10: Sleep Signals

Người dùng chấm vòng X15: bảy bài thích, một bài tạm được, hai bài chưa chấm (Neon in the Rain, Sleeping Space
Station) bị bỏ như các album trước. Album 10 gồm tám bài: Distant Star Signal, Sleeping City, Digital Sky, Night
Radio Waves, Slow Orbit, Synthetic Dream, Electric Sea of Stars, Lights Out (39 phút 17 giây, -17 LUFS). Bìa vẽ
bằng máy (vòng sáng như tín hiệu lan ra trên đường chân trời tối), file chỉ còn tên bài.

Người dùng sau đó: "hãy thêm D4 D5 vào album". Album 10 thành mười bài: Distant Star Signal, Sleeping City,
Neon in the Rain, Digital Sky, Night Radio Waves, Slow Orbit, Synthetic Dream, Electric Sea of Stars, Sleeping
Space Station, Lights Out (49 phút 18 giây).

## Vòng X16: album 11, nhạc ngủ điện tử tiếp (kiểu `ngu-dt`)

Người dùng: "hãy sáng tác album 11", sau khi giữ trọn album 10. Mười bài mới cùng kiểu `ngu-dt` (đã làm êm như
bản cuối của album 10: `air` -10 dB, `swells` -3 dB, `arp` -6 dB), pha thêm dàn dây, sóng, hộp nhạc:

| Bản | Tên tiếng Anh | Giọng, nhịp |
|---|---|---|
| `k108-cuc-quang` (Cực quang) | Aurora Drift | Rê thứ, 48 bpm |
| `k109-ve-tinh-ngu-quen` (Vệ tinh ngủ quên) | The Dozing Satellite | Son thứ, 50 bpm |
| `k110-chuyen-tau-nua-dem` (Chuyến tàu nửa đêm) | Midnight Train | Mi thứ, 52 bpm, dây |
| `k111-tinh-van` (Tinh vân) | Nebula | Fa thăng thứ, 46 bpm |
| `k112-thuy-trieu-dem` (Thủy triều đêm) | Night Tide | La thứ, 50 bpm, sóng |
| `k113-bang-cu` (Băng cassette cũ) | Old Cassette Dreams | Đô thứ, 50 bpm, dây, hộp nhạc |
| `k114-den-khuya` (Đèn khuya) | Late Night Lamp | Si thứ, 52 bpm |
| `k115-mat-trang-xanh` (Mặt trăng xanh) | Blue Moon Hum | Đô thăng thứ, 48 bpm |
| `k116-toa-do-cuoi` (Tọa độ cuối) | Last Coordinates | Fa thứ, 50 bpm |
| `k117-ngu-sau-trong-may` (Ngủ sâu trong mây) | Deep in the Clouds | Son thăng thứ, 44 bpm |

## Bản thay thế Night Clouds (album 6)

Người dùng: "bài 2 night cloud trong album bị dính content id nhạc khoảng 10s". `k37-may-dem` chỉ có nền synth
trên vòng Rê thứ 9 / Si giáng trưởng 7 rất phổ biến, không giai điệu, nên dễ bị khớp nhầm. Bản thay
`k118-may-dem-moi` (cùng tên Mây đêm / Night Clouds): Fa thăng thứ, vòng hợp âm khác, chuông thủy tinh ngẫu
hứng, hộp nhạc ở giữa, 46 bpm. `k37` giữ nguyên.

## Bản thay thế Before the Storm (album 5) và The Last Candle (album 7)

Người dùng: "2 bài số 6 trong 2 album này bị dính content id youtube". Cả hai dùng vòng i-VI-iv-V cung thứ rất
phổ biến; `k45` còn có giai điệu viết sẵn kiểu nhạc phim quen thuộc. Bản thay (cùng tên):
`k119-truoc-con-bao-moi` (Mi thứ màu Dorian/Lydian, vòng Em9 - Cmaj7/G - Am9 - D6 ..., cây dây ngẫu hứng thay
giai điệu viết sẵn, dây, hợp xướng, timpani, 58 bpm) và `k120-ngon-nen-cuoi-moi` (Si thứ, vòng Bmadd9 -
Dmaj7/A - Em9 - Gmaj7 ..., hộp nhạc rồi cây dây ngẫu hứng, 46 bpm). Thêm hợp âm `6` và `maj7#11` vào
compose.py. `k45`, `k58` giữ nguyên.

### Album 11 làm lại an toàn hơn

Người dùng: "ok làm lại album 11 an toàn hơn" (sau ba bài bị Content ID khớp, đều trên vòng i-VI-iv-V phổ
biến). Mười bài `k108`-`k117` giữ chủ đề, tiếng và giai điệu ngẫu hứng, nhưng đổi sang bốn khung hợp âm ít gặp
(không còn i-VI-iv-V thuần): hợp âm iv6 trên bass chủ, VI maj7#11, II giáng maj7#11 (màu Phrygian), V 7sus4;
hai bài (`k111`, `k115`) theo Dorian (IV trưởng, ii, vi m7b5). Năm bài sau bắt đầu vòng giữa từ nửa sau.

## Quy tắc xuất album (từ 13/11/2026, theo yêu cầu người dùng)

Mỗi lần xuất album, xuất đúng cách này để nhập thẳng vào Kho nhạc của công ty:

1. Thư mục `<Tên chủ đề>\<Tên album>\`. Tên chủ đề viết GIỐNG HỆT tên chủ đề trong Dashboard YouTube (ví dụ
   `Jazz`, `NHẠC DARK`). Mỗi album một thư mục, không lồng thư mục MP3/WAV bên trong.
2. Chỉ WAV: 44,1 hoặc 48 kHz, 16 hoặc 24 bit, stereo, khoảng -16 LUFS. Tên file `01 - Tên bài tiếng Anh.wav`
   (hai chữ số, cách " - "). Không xuất MP3. Tag trong file chỉ có tên bài.
3. `cover.jpg` vuông (ví dụ 1400x1400) trong thư mục album.
4. `Tracklist.txt` (UTF-8) trong thư mục album:
   - Dòng 1: `<Tên album tiếng Anh> / <Tên album tiếng Việt>`
   - Dòng 2: `<Thể loại>, <N> tracks / <N> bài`
   - Một dòng trống, có thể vài dòng mô tả, nhạc cụ, giấy phép.
   - Bảng, các cột cách nhau ít nhất hai khoảng trắng, dòng đầu là tiêu đề:
     `No. English title  Tên tiếng Việt  Key  BPM  Length`. English title trùng tên trong tên file (không số
     đầu). Key dạng `<nốt> major` / `<nốt> minor` (C, C#, Db, D, Eb, E, F, F#, G, Ab, A, Bb, B), có thể thêm
     `, 3/4`; không ghi "Dorian", "to C major". BPM là số; Length dạng m:ss.
5. Không kèm Excel "Kho bài hát.xlsx", không đặt danh-sach.csv hay bokin-music.csv trong thư mục.
6. Nhạc có dùng sample hay nhạc cụ ảo cần ghi công (CC-BY...) thì ghi trong phần mô tả của Tracklist.txt.
   (Nhạc của phiên này: mọi tiếng tự tổng hợp, không sample nào cần ghi công.)

Ví dụ: `NHẠC DARK\The Year I Waited\01 - July Rain.wav`, `...\cover.jpg`, `...\Tracklist.txt`.

Người dùng chọn: mọi album của phiên này xuất vào thư mục chủ đề `Nhạc Dark Ambient`; cách xuất mới áp dụng từ
album 11 (album 1-10 giữ như đã gửi); nhạc ngủ giữ khoảng -17 LUFS.

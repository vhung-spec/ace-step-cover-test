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

## Bốn bài nữa, mỗi bài một cách mở đầu (vòng 22)

Người dùng: "hãy sáng tác thêm vài bài kiểu này nhưng hơi khác đi chút, đoạn mở đầu khác nhau". Vẫn `tam-tau-phim`.
Mới: `melody_on: cello` cho một đoạn, cello hát giai điệu của đoạn đó (viết ở giọng cello), piano để trống hay chỉ
chơi kết cấu của đoạn. Cello hát dùng `cellos-dark` (cắt từ 3 kHz: mẫu nhẹ có tiếng xì, 38-39 dB dưới nhạc ở chỗ lặng,
giờ 43-45). 69 bài cũ soạn ra y hệt như trước.

| Bài | Giọng, nhịp | Mở đầu | Khác thêm |
|---|---|---|---|
| `gio-lanh` (Gió lạnh) | Đô thứ, 70 bpm | Cello hát chủ đề một mình, viola nền, chưa có piano (4 ô) | Piano nhắc lại chủ đề cao hơn hơn một quãng tám; đoạn giữa Mi giáng trưởng lên tới Mi giáng 6 |
| `dong-ho-cu` (Đồng hồ cũ) | Son thứ, 76 bpm | Piano một mình gõ "tích tắc" (Rê, Si giáng đổi nhau từng móc đơn) như đồng hồ cũ (2 ô) | Kết bài gõ lại tiếng đồng hồ, cello đáp |
| `mat-ho-dem` (Mặt hồ đêm) | Mi giáng thứ, nhịp ba, 69 bpm | Chỉ dàn dây: cello giữ nốt trầm, viola một bè chậm (4 ô), piano vào sau | Đoạn giữa Son giáng trưởng hát hai lần |
| `ngay-xa` (Ngày xa) | Mi thứ, 84 bpm | Không có đoạn mở: hai nốt dạo của piano rồi vào thẳng giai điệu | Đoạn giữa đổi vai: cello hát, piano rải hợp âm; rồi piano hát lại cao hơn, cello đáp |

## Hai bài nữa, đủ mười bài cho `tam-tau-phim` (vòng 23)

Người dùng: "hãy sáng tác thêm 2 bài nữa cho đủ 10 bài" (bốn bài vòng 21, bốn bài vòng 22, hai bài này). Mới:
`melody_on: viola` (viola hát một đoạn, trên `violas-dark`: cắt ở 3 kHz thì tiếng xì của viola lộ ra ở đoạn mở đầu, 41 dB
dưới nhạc; cắt ở 2 kHz còn 47) và lớp `cello-pizz` (cello gảy dây: nốt trầm của hợp âm ở phách một, quãng tám nửa phách
sau phách hai, quãng năm ở phách cuối, như giọt nước). 73 bài cũ soạn ra y hệt.

| Bài | Giọng, nhịp | Mở đầu | Khác thêm |
|---|---|---|---|
| `trang-khuyet` (Trăng khuyết) | Si thứ, 66 bpm | Viola hát chủ đề một mình, cello đáp từng câu (4 ô) | Piano nhận chủ đề ở đúng cao độ đó, trầm và ấm, rồi lên một quãng tám; kết bài viola hát lại câu cuối một mình |
| `giot-dem` (Giọt đêm) | Đô thăng thứ, 74 bpm | Cello gảy dây một mình như giọt nước rơi (2 ô) | Giai điệu kiểu mới: một nốt gõ hai lần rồi đi xuống (Mi-Mi-Rê#-Đô#); kết bài tiếng gảy trở lại |

## Kiểu phối mới 1: piano + viola, `song-tau` (vòng 24)

Người dùng: "hãy chuyển sang sáng tác các bài theo kiểu phối mới: 1. Piano + viola: Piano chơi giai điệu thưa; viola kéo
những nốt trung trầm, chỉ xuất hiện cuối câu".

- Piano: tiếng đàn người dùng chọn (Salamander làm tối kiểu keyboard, Rhodes chơi chồng), giai điệu thưa (hai, ba nốt
  một ô, ô thứ tư mỗi câu ngân dài), dưới nó chỉ một nốt trầm nhẹ mỗi hợp âm (`texture` `deep`, giữ nguyên khi hợp âm
  lặp lại).
- Viola (`viola-end`): chỉ vào ở cuối câu (ô cuối của mỗi bốn ô, và ô cuối mỗi đoạn), từ phách hai: một nốt dài giọng
  trung trầm (Rê 3 tới Mi 4), nốt của hợp âm (ưu tiên nốt gốc, quãng ba), gần nốt trước nhưng không lặp nốt vào lần
  trước, không cách giai điệu nửa cung; ngân sang phách đầu câu sau rồi chuyển sang nốt gần nhất của hợp âm mới hai
  phách và dừng. 8 dB dưới đàn.
- Màu viola: làm tối ở 2 kHz và vào chậm (0,3 s) thì CLAP nghe là "piano with a synth pad" (85-95 %); để màu thu nguyên
  (lọc 6 kHz như dàn dây khác, vào 80 ms) thì "a piano and viola duet" đứng đầu ở ba bài, tiếng xì vẫn 47-56 dB dưới nhạc.
  Cả bốn bài: "a sparse, slow piano melody with long silences" 100 %, "a warm, deep, dark piano" 0,64-0,65.

| Bài | Giọng, nhịp | Độ dài |
|---|---|---|
| `o-cua-so` (Ô cửa sổ) | La thứ, 60 bpm | 2:29 |
| `phong-trong` (Phòng trống) | Son thứ, nhịp ba, 60 bpm | 2:17 |
| `canh-cua-khep` (Cánh cửa khép) | Mi thứ, 56 bpm, thưa nhất | 2:39 |
| `dem-khong-ngu` (Đêm không ngủ) | Fa thứ, 64 bpm | 2:20 |

## Kiểu phối Claude đề xuất: "Kể chuyện", `ke-chuyen` (vòng 25)

Người dùng: "bạn hãy tự sáng tác những bản khác hay hơn, phối theo kiểu bạn đề xuất". Đề xuất: mỗi bài là một câu chuyện
có cung bậc, nhạc cụ vào dần rồi rút dần: piano kể một mình (một nốt trầm nhẹ mỗi hợp âm); cello vào (một bè thứ hai chậm,
`cello-counter`: nốt màu của hợp âm, mỗi hợp âm một nốt dài, A2-C4; hay lời đáp từ xa, `cello-answer`); cao trào có dàn dây
giữ hợp âm (`strings`) và piano rải hợp âm (`blocks`, chỉ ở cao trào); rồi lắng về piano một mình, viola chỉ ở cuối câu.
Hợp âm cuối gõ nhẹ (`ending_velocity` 38, mặc định 52: ở 52 nó to hơn đoạn lắng trước nó 5 dB, giờ 1-2 dB).

Giai điệu viết kỹ hơn: mỗi bài một mô-típ riêng, được phát triển (nhắc lại cao hơn một bậc, biến thành đường leo ở cao
trào) và một đỉnh rõ ràng.

| Bài | Giọng, nhịp | Mô-típ | Cung bậc (dB theo đoạn) |
|---|---|---|---|
| `nguoi-o-lai` (Người ở lại) | La thứ, 63 bpm, bè trầm "lament" A-G-F-E | Tiếng thở dài đi xuống E-D-C-B về A, câu đáp đi lên tới F; cao trào leo tới Rê 6, Esus4 về E | -25, -22, -17, -24, -22 |
| `khuc-ru-muon` (Khúc ru muộn) | Mi thứ, nhịp ba, 66 bpm | Leo theo hợp âm B-E-G rồi tựa xuống một bậc (F#-E; G-F# trên B7) | -26, -23, -18, -17, -25, -24 |
| `tieng-goi-xa` (Tiếng gọi xa) | Son thăng thứ, 68 bpm | Tiếng gọi: một nốt gõ hai lần rồi nhảy lên quãng sáu (D#-D#-B), cello đáp từ xa | -25, -23, -17, -25, -24 |

CLAP: cả ba "a piano with cello and strings", "sad, emotional, cinematic piano music", "a warm, deep, dark piano".

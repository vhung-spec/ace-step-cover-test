# ACE-Step cover test

Thử chức năng **cover** của [ACE-Step 1.5](https://github.com/ACE-Step/ACE-Step-1.5) trên máy
của GitHub (không có GPU), rồi tự chấm điểm từng bản cover.

## Bài test làm gì

1. Cài ACE-Step 1.5 ở một commit cố định, rồi tải mô hình đã chọn: turbo (mô hình app dùng),
   SFT (chậm hơn, kỹ hơn) hoặc base (để thêm bè và phối thêm nhạc cụ).
2. Tạo bản gốc: *We Wish You a Merry Christmas*, bài hát truyền thống đã hết bản quyền. Bài được
   phối cho piano ngay trong `make_source.py`, rồi phát thành âm thanh bằng FluidSynth. Bản
   phối v2 chơi như người thật (mở đầu nhẹ, hợp âm rải, lần hai đầy hơn, có pedal, to nhỏ theo
   câu nhạc); v3 giống v2 nhưng bỏ pedal và các nốt chồng quãng tám phía dưới cho đỡ đục;
   v1 là bản phối đơn giản của các lượt đầu. Tiếng đàn lấy từ bộ âm thanh GeneralUser GS
   (mặc định) hoặc FluidR3. Chọn *song* `silent-night` thì bản gốc là *Silent Night* (Franz
   Gruber, 1818, đã hết bản quyền), một lượt, chỉ có bản phối đơn giản v1.
3. Cover bản gốc theo từng dòng trong `plan.json`: mỗi dòng có một câu mô tả phong cách
   (`caption`) và một mức bám theo bản gốc (`strength`). Mặc định giống chức năng cover của
   app: mô hình turbo, 8 bước, shift 3, không dùng mô hình ngôn ngữ, không nén INT8.
4. Chấm điểm từng bản cover so với bản gốc (`score_covers.py`).

## Cách chạy

**Actions → ACE-Step cover test → Run workflow.** Chọn mô hình (*model*), bản phối (*arrangement*),
bộ âm thanh (*soundfont*) và bài (*song*). Muốn dùng một bản của lần chạy trước làm bản gốc (ví dụ
thêm bè dây cho một bản cover), điền mã lần chạy đó vào *source_run* và tên bản vào *source_take*. Ô *plan* để trống thì dùng `plan.json`. Muốn thử kế hoạch khác thì
dán một danh sách JSON, ví dụ:

```json
[{"name": "piano-16", "strength": 1.0, "noise": 0.1, "steps": 16,
  "caption": "instrumental Christmas music, warm grand piano, soft strings, gentle and cozy"}]
```

Mỗi dòng có thể đặt thêm:

| Mục | Ý nghĩa |
|---|---|
| `noise` | Giữ lại bao nhiêu âm thanh của bản gốc làm điểm xuất phát (0 là không giữ) |
| `steps`, `shift`, `guidance` | Số bước (turbo luôn chạy tối đa 8 bước; SFT và base mặc định 50), shift (3 với turbo, 1 với hai mô hình kia), mức bám câu mô tả (chỉ SFT và base, mặc định 7) |
| `bpm`, `keyscale`, `timesignature` | Nhịp độ, giọng (ví dụ `C major`) và số phách mỗi ô nhịp (ví dụ `3` cho nhịp 3/4) của bài; không đặt thì ACE-Step coi là chưa biết |
| `seed` | Hạt giống ngẫu nhiên (mặc định 1); đổi hạt giống để có bản khác với cùng cài đặt |
| `reference` | Tên một dòng trước đó; bản của dòng đó làm âm sắc mẫu |
| `task: "text2music"` | Sáng tác một đoạn mới từ câu mô tả (`duration` giây), ví dụ để làm âm sắc mẫu |
| `task: "lego"`, `track` | Chỉ mô hình base: tạo riêng bè của một nhạc cụ (`strings`, `percussion`, `woodwinds`…) chơi cùng bản gốc. Bè mới lưu riêng (`stem_01`) và được trộn với bản gốc thành bản nghe (`take_01`), to bằng `level` (mặc định 0,7) lần bản gốc |
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
Chọn thêm *remix* thì mỗi bè mới (lego) được trộn với bản gốc ở các mức to 0 / 0,4 / 0,7 / 1,0 / 1,4
(`remix.py`; mức 0 là bản gốc một mình, để so), và mỗi bản trộn được đo giữ giai điệu, hoà âm,
phong cách và chấm điểm như trên. Nhờ vậy chọn được mức to vừa đủ đổi phong cách mà chưa lấn giai điệu.
Ô *stack* thì trộn lần lượt nhiều bè mới vào một bản, đúng như app làm khi thêm bè thứ hai (`stack.py`),
và chấm từng bước, ví dụ `runs/<mã> runs/<mã>/covers/lego-strings/stem_01.mp3:1.0
runs/<mã khác>/covers/lego-woodwinds/stem_01.mp3:0.7` (nhiều lượt cách nhau bằng dấu `;`). Mỗi bước
được lưu thành MP3 để nghe, trong artifact **judged** (thư mục `stacked/`).

## Phối bằng tiếng nhạc cụ thật (không dùng AI)

**Actions → Real-sample arrangements → Run workflow.** Không có mô hình AI nào tạo âm thanh ở đây:

1. `arrange.py` phối bảy bài carol đã hết bản quyền thành nhiều bè MIDI, mỗi nhạc cụ một file:
   `wish` (We Wish You a Merry Christmas), `silent-night`, `first-noel`, `joy` (Joy to the World),
   `o-holy-night`, `jingle-bells`, `deck-the-halls`. Bài nhịp 3, nhịp 2, nhịp 4 hay nhịp 12/8 đều được, mỗi
   bài ở giọng riêng. Giai điệu và hợp âm của The First Noel, Joy to the World và O Holy Night lấy từ bản
   nhạc gốc đã hết bản quyền của Mutopia Project (xem `carols.py`). Mỗi bài được phối theo các kiểu:
   - `piano`: giai điệu có to nhỏ theo câu, tay trái rải hợp âm, pedal; đàn Steinway B.
   - Các kiểu piano nhẹ nhàng: cùng tiếng đàn với `piano` nhưng chậm hơn, đánh nhẹ hơn. Giai điệu hơi trễ
     nhịp, nghỉ lấy hơi dài hơn ở cuối câu. Bài ngắn được chơi ba lượt.
     - `chill`: tay trái rải hợp âm thưa; lượt giữa (khi có ba lượt) cao lên một quãng tám.
     - `lullaby`: ru ngủ, chậm nhất. Giai điệu cao một quãng tám như hộp nhạc, tay trái đưa nôi.
     - `flowing`: tay trái rải liên tục từng nốt móc đơn, lên rồi xuống.
     - `hymn`: hợp âm khẽ dưới giai điệu, như đánh thánh ca.
     - `piano-strings`: như `chill`, có nền dây rất khẽ.
     - `felt`: tiếng piano tối và tròn như đàn búa nỉ (lọc bỏ dải cao từ 900 Hz), theo bản ru ngủ mẫu.
       Tay trái rải đều từng nốt móc đơn ngay từ đầu.
     - `felt-noise`: như `felt`, có thêm lớp tiếng rì (pink noise) rất khẽ như nhạc ru ngủ cho em bé.
   - `ballad` và `pulse`: làm theo hai bản mẫu piano Giáng sinh thư giãn của bạn (chỉ đo âm thanh và
     cách chơi, không chép gì của họ). Đây là hai kiểu chạy mặc định. Đo so với hai bản mẫu, bản cũ trên đàn
     Yamaha thiếu khoảng 20 dB tiếng trầm và 25–30 dB độ sáng, tay trái lại thưa. Hai bản mẫu là một cây
     đàn grand đánh vừa tay, có bass trầm và mạnh mỗi lần đổi hợp âm, quãng giữa đi đều từng nốt móc đơn
     (2–3 nốt một lúc) dưới pedal, giai điệu ở trên cao. Hợp âm của họ chính là hợp âm của bài, không thêm
     màu nhiều. Nên giờ:
     - đàn upright Yamaha (bạn nghe so với Steinway grand mở dải cao và chọn Yamaha; muốn so thì điền
       `grand` vào ô *pianos*), giai điệu và bass đánh vừa tay, không đánh quá nhẹ;
     - bass trầm (từ La1 tới Son#2) đánh mỗi lần đổi hợp âm, thỉnh thoảng đi bằng nốt ba của hợp âm cho
       đường bass liền mạch (Đô – Son/Si – La thứ); giai điệu cao một quãng tám; lượt giữa có bè quãng ba
       hoặc quãng sáu dưới các nốt dài, lượt cuối nhân đôi quãng tám; cuối câu có vài nốt rải nhẹ lên trên
       nốt ngân; hợp âm cuối rải từ nốt trầm. Tiếng vang dài hơn.
     - `ballad` (khoảng 72 nhịp/phút): mở đầu bằng câu cuối của bài; bass đi từng phách (gốc, năm, tám,
       năm); quãng giữa mỗi nốt móc đơn hai nốt của hợp âm, thấp cao xen kẽ; một lớp pad synth rất khẽ ở dưới
       như bản mẫu thứ hai (tự tạo bằng bộ dao động của sfizz, `instruments/pad.sfz`, không cần mẫu thu nào).
     - `pulse` (khoảng 88 nhịp/phút): mở đầu tự do bằng hợp âm của mấy ô nhịp cuối, rải từ bass trầm lên
       một nốt cao đi thành giai điệu riêng; sau đó tiếng đệm nảy đều như nhịp tim, mỗi nốt móc đơn một
       quãng năm (thêm quãng tám ở đầu phách), bass trầm ở đầu hợp âm và quãng năm ở giữa ô nhịp. Thêm các
       nhạc cụ nghe được trong bản mẫu thứ nhất: lượt đầu có glockenspiel đánh đôi giai điệu thật khẽ, rồi sáo
       hát giai điệu (có vibrato nhẹ 5,2 lần/giây như sáo trong bản mẫu) trong khi piano đi theo khẽ, đoạn cuối
       vibraphone đánh đôi giai điệu trên tiếng harp rải và dàn dây khẽ. Tiếng lấp lánh ở lượt đầu là chuông
       lắc (sleigh bells) lắc khẽ theo nhịp từng nốt móc đơn, và một nốt glockenspiel cao mỗi hai ô nhịp, như
       bản mẫu (soi kỹ: những tiếng leng keng ngắn ở 5–7,5 kHz cách nhau 0,33–0,66 giây); bản trước dùng
       mark tree (chùm thanh kim loại gạt lướt) nghe không hay nên đã bỏ.
     - Các nhạc cụ này được nhận ra bằng hai mô hình nhận diện âm thanh (PaSST, huấn luyện trên AudioSet) nghe
       từng đoạn 5–10 giây của hai bản mẫu, so với các bản chỉ có piano của mình, cùng với đo bồi âm và độ rung
       (vibrato) của giai điệu.
     - `ballad-clear`, `pulse-clear`: như trên nhưng rõ từng nốt hơn và sáng hơn. Nghe gần, tiếng đệm của
       hai bản mẫu nở ra rồi tắt theo từng phách, còn ở `ballad`/`pulse` pedal giữ cả hợp âm nên tiếng ngân
       liền một mảng. Nên ở đây pedal được thay mỗi phách, bass giữ một phách, tay giữa nhấc lên sau mỗi nốt
       móc đơn, và dải cao của đàn được nâng (+8 dB từ 6 kHz).
   - `bells`: vibraphone cùng chuông tay hát giai điệu, cao hơn bài một quãng tám, nơi chuông ngân hay
     nhất. Glockenspiel lấp lánh ở các nốt dài; nhạc cụ này vang cao hơn phím một quãng tám. Đệm bằng
     harp và nền dây khẽ. Chuông ống ngân nhẹ ở đầu mỗi lượt.
   - `orchestra`: sáo rồi violin hát giai điệu, sáo bè cao ở lượt cuối. Viola và cello giữ hợp âm,
     contrabass gảy rồi kéo vĩ, horn vào từ giữa lượt cuối. Có harp lướt phím ở chỗ chuyển và một hồi
     timpani khẽ ở hợp âm cuối.
   - `salamander`: như `piano` nhưng trên đàn Salamander Grand Piano (không chạy mặc định).

   Các kiểu piano nhẹ nhàng (chill, lullaby, flowing, hymn, piano-strings, felt, felt-noise) chơi trên đàn
   upright Yamaha: tiếng mềm, ấm, gần gũi (đã nghe so với Steinway và upright Knight). Kiểu `piano` chơi
   trên đàn Steinway B grand có cắt dải cao; `ballad` và `pulse` chơi trên cùng cây Steinway nhưng mở dải cao
   (`grand`). Các kiểu cũ vẫn còn trong mã nhưng không chạy mặc định nữa: muốn chạy thì điền tên vào ô
   *styles*. Muốn so đàn, điền ô *pianos* khi chạy (`piano`, `grand`, `knight`, `yamaha`): bản chơi trên đàn
   khác đàn của kiểu đó có đuôi là tên đàn. Vài mẫu thu của đàn Yamaha bị ngược pha giữa hai kênh;
   `fetch_samples.py` tự sửa lại.

   Mọi bè đi theo cùng một hợp âm từng phách nên luôn khớp nhau. Bè ngân giữ nguyên nốt chung giữa hai
   hợp âm, nốt khác đi tới nốt gần nhất, và to nhỏ theo từng câu (CC11). Hai nốt cùng phím không bao giờ
   chồng lên nhau: nếu chồng, lệnh tắt nốt trước sẽ cắt luôn nốt sau thành một tiếng vĩ cụt.
2. `fetch_samples.py` tải đúng các nhạc cụ cần dùng từ hai thư viện mẫu âm thanh CC0 của Versilian
   Studios: VS Chamber Orchestra 2 Community Edition và Versilian Community Sample Library. Mẫu tiếng của
   đàn Steinway có tiếng xì đều ở dải cao (từ 4 kHz): nốt nhẹ chỉ to hơn tiếng xì 16–26 dB, và khi giữ pedal
   cả chục nốt cùng ngân thì thành tiếng "xào". Nên với từng mẫu, ngay khi nốt đã tắt dần xuống tới mức
   tiếng xì thì dải cao được giảm dần đi (tới 50 dB). Tiếng búa gõ và tiếng ngân của nốt giữ nguyên. Dải
   trên cùng của nốt nhẹ chỉ toàn tiếng xì nên bỏ hẳn. Thử với 12 nốt giữ pedal: lúc ngân, tiếng xì trên 6 kHz
   nhỏ đi 22–45 dB.
3. `render_samples.py` phát từng bè bằng [sfizz](https://sfz.tools/sfizz/) (`sfizz_render`). Sau đó:
   - chỉnh âm sắc từng bè: mẫu thu nào cũng có chút tiếng xì nền. Dải cao nơi mẫu chỉ còn tiếng xì được
     cắt hẳn (piano từ 6 kHz, vibraphone từ 2,5 kHz, chuông ống từ 4 kHz, đàn hạc từ 5 kHz…), và lúc nhạc
     lặng thì phần xì còn lại được hạ thêm tới 10 dB. Tiếng giảm âm của piano khi nhả phím được vặn nhỏ;
   - cân độ to của từng bè theo vai trò và xếp vị trí trái/phải. Trước đó, mỗi bè được đưa về chính giữa,
     vì nhiều mẫu thu lệch hẳn sang một bên (có nốt vibraphone lệch 17 dB). Các nhạc cụ có nốt lệch nhiều
     còn được thu hẹp âm trường, để giai điệu không nhảy qua lại giữa hai tai;
   - thêm vang phòng hoà nhạc tự tạo (không cần bản quyền): dải cao tắt nhanh nên đuôi vang ấm, không xì;
   - cân trái/phải: bài nào lệch quá 1 dB về một bên thì được cân lại (`master.py`). Các bước master khác
     (chỉnh âm sắc, tạo độ sáng, độ rộng, làm đều độ to theo hai bản mẫu) đã thử và đang tắt: nghe thử thấy
     bị rè và không hay bằng bản không master;
   - đưa cả bài về -16 LUFS. Bộ hạn chế đỉnh âm hạ âm lượng từ từ, không giật (giật sẽ gây tiếng tách).
     Mỗi đỉnh bị hạ tối đa 3 dB; bài nào cần hạ nhiều hơn thì để nhỏ hơn một chút (tối đa -19 LUFS).
     Nhật ký ghi lại bài bị hạ đỉnh bao nhiêu và độ cân bằng trái/phải.
4. `rate.py` chấm điểm như các phần trên.

Mỗi bài chạy trên một máy riêng, cùng lúc với các bài khác. Kết quả: artifact **sampled-<bài>** cho từng
bài và **sampled** gồm tất cả (MP3 của từng bài và kiểu, các file MIDI, điểm chấm `rated-<bài>.txt`).

## Giấy phép

Mã ACE-Step theo giấy phép MIT; xem giấy phép của trọng số mô hình trên
[trang Hugging Face của ACE-Step](https://huggingface.co/ACE-Step/Ace-Step1.5) trước khi dùng
kết quả cho mục đích thương mại. Mô hình CLAP dùng để chấm điểm là `laion/clap-htsat-unfused`;
mô hình Audiobox Aesthetics (`facebook/audiobox-aesthetics`) theo giấy phép CC-BY 4.0.

Bộ âm thanh [GeneralUser GS](https://schristiancollins.com/generaluser.php) v2.0.3 là của
S. Christian Collins, được dùng tự do để làm nhạc, kể cả thương mại. Bài test tải nó từ kho
GitHub của tác giả ở một commit cố định, không chép vào kho này.

Hai thư viện mẫu âm thanh [VSCO 2 Community Edition](https://github.com/sgossner/VSCO-2-CE) và
[VCSL](https://github.com/sgossner/VCSL) của Versilian Studios theo giấy phép CC0 (dùng tự do, kể cả
thương mại, không cần ghi nguồn); bài test tải chúng ở commit cố định, không chép vào kho này.
[Salamander Grand Piano V3](https://github.com/sfzinstruments/SalamanderGrandPiano) của Alexander Holm
theo giấy phép CC-BY 3.0: dùng được cho thương mại nhưng phải ghi tên tác giả (ví dụ trong mô tả video).
sfizz theo giấy phép BSD 2-Clause.

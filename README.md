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
     - `felt-2k`, `felt-4k`, `felt-open`: `felt` sáng hơn, theo ý bạn. Bộ lọc dải cao nới từ 900 Hz lên
       2 kHz, 4 kHz, hoặc bỏ hẳn.
     - `felt-bright`: sáng hơn nữa: không lọc, và giai điệu đánh mạnh tay hơn một chút để đàn dùng lớp
       tiếng sáng của nó.
   - `ballad` và `pulse`: làm theo hai bản mẫu piano Giáng sinh thư giãn của bạn (chỉ đo âm thanh và
     cách chơi, không chép gì của họ). Đây là hai kiểu chạy mặc định. Đo so với hai bản mẫu, bản cũ trên đàn
     Yamaha thiếu khoảng 20 dB tiếng trầm và 25–30 dB độ sáng, tay trái lại thưa. Hai bản mẫu là một cây
     đàn grand đánh vừa tay, có bass trầm và mạnh mỗi lần đổi hợp âm, quãng giữa đi đều từng nốt móc đơn
     (2–3 nốt một lúc) dưới pedal, giai điệu ở trên cao. Hợp âm của họ chính là hợp âm của bài, không thêm
     màu nhiều. Nên giờ:
     - `pulse` chơi trên đàn upright Yamaha (bạn nghe so với Steinway grand mở dải cao và chọn Yamaha; muốn
       so thì điền `grand` vào ô *pianos*), `ballad` trên đàn piano điện Rhodes (xem dưới); giai điệu và bass
       đánh vừa tay, không đánh quá nhẹ;
     - bass trầm (từ La1 tới Son#2) đánh mỗi lần đổi hợp âm, thỉnh thoảng đi bằng nốt ba của hợp âm cho
       đường bass liền mạch (Đô – Son/Si – La thứ); giai điệu cao một quãng tám; lượt giữa có bè quãng ba
       hoặc quãng sáu dưới các nốt dài, lượt cuối nhân đôi quãng tám; cuối câu có vài nốt rải nhẹ lên trên
       nốt ngân; hợp âm cuối rải từ nốt trầm.
     - tiếng vang của một phòng nhỏ (0,8 giây), ít vang, để nghe gần như hai bản mẫu. Bạn nghe hai bản mẫu
       "rất gần tai", còn bản cũ với tiếng vang dài 2,8 giây "như trong phòng lớn". Đã nghe thử 1,2 giây (lượng
       vang 0,6 lần) và 0,8 giây (0,45 lần); bạn chọn mức gần hơn.
     - `ballad` (khoảng 72 nhịp/phút): mở đầu bằng câu cuối của bài; bass đi từng phách (gốc, năm, tám,
       năm); quãng giữa mỗi nốt móc đơn hai nốt của hợp âm, thấp cao xen kẽ; một lớp pad synth rất khẽ ở dưới
       như bản mẫu thứ hai (tự tạo bằng bộ dao động của sfizz, `instruments/pad.sfz`, không cần mẫu thu nào).
       Hợp âm được tô màu kiểu pop ballad như bản mẫu thứ hai (vòng ii–V–I–vi, khoảng hai phần năm là hợp âm
       thứ; hợp âm gốc của các bài carol gần như toàn trưởng): trong một chuỗi ô nhịp hợp âm chủ, cứ ô thứ
       hai thành hợp âm bậc vi thứ bảy (Đô thành La thứ 7, vẫn chứa đủ nốt của Đô); chuỗi hợp âm bậc IV thì ô
       thứ hai thành ii thứ bảy (Fa thành Rê thứ 7); ô hợp âm át (V) mở đầu bằng ii thứ bảy. Chỉ đổi ở chỗ các
       nốt giai điệu vẫn là nốt của hợp âm mới (Silent Night: 10/24 ô nhịp, từ 0% lên 33% phách là hợp âm thứ).
     - `ballad` chơi trên đàn piano điện Rhodes (bộ mẫu jRhodes3d của Jeff Learman, đàn Rhodes Mark I đời
       1977). Soi từng nốt của bản mẫu thứ hai, cứ khoảng 10 nốt có một nốt mang một bồi âm đứng riêng ở khoảng
       7,2 lần cao độ. Đó là tiếng "chuông" của thanh rung (tine) trong đàn Rhodes; đàn Yamaha không có tiếng
       này. Chơi bằng Rhodes thì mô hình nhận diện nghe tiếng đàn giống bản mẫu (nhãn "Piano" 0,08–0,11; bản
       mẫu 0,05; Yamaha 0,30–0,42), và "tiếng chuông" cũng có ở khoảng 10% số nốt. Bạn nghe thấy "khá gần bản
       mẫu". Đã thử và bỏ: Rhodes trộn nhỏ hơn 6 hoặc 12 dB dưới tiếng Yamaha (gần như không đổi gì). Bản
       Rhodes tối hơn bản mẫu (dải 2–6 kHz thấp hơn khoảng 20 dB). Muốn nghe `ballad` trên Yamaha thì điền
       `yamaha` vào ô *pianos*. Mẫu Rhodes thu thẳng từ đàn nên gần như mono: bớt vang thì tiếng đàn dồn vào
       giữa, còn bản mẫu rộng sang hai bên ngay từ lúc nốt vang lên. Nên tiếng Rhodes có thêm chorus stereo
       (mỗi bên tai nghe một bản trễ 10 hoặc 14 ms, lắc nhẹ 0,5 lần/giây), cách người chơi Rhodes hay dùng:
       rộng mà không thêm tiếng vang phòng. Đo thì đây là bản có không gian gần bản mẫu thứ hai nhất; bạn
       nghe có hay không có chorus đều ổn và giữ cả hai (bản 11 và 10 trên trang nghe): `ballad` có chorus,
       `ballad-plain` không có.
     - `pulse` (khoảng 88 nhịp/phút): vào thẳng giai điệu, không dạo đầu. Bạn muốn bỏ 10 giây piano dạo ở
       đầu: hợp âm của mấy ô nhịp cuối rải tự do từ bass trầm lên một nốt cao (`pulse-clear` vẫn giữ đoạn
       này). Tiếng đệm nảy đều như nhịp tim, mỗi nốt móc đơn một
       quãng năm (thêm quãng tám ở đầu phách), bass trầm ở đầu hợp âm và quãng năm ở giữa ô nhịp. Thêm các
       nhạc cụ nghe được trong bản mẫu thứ nhất: lượt đầu có glockenspiel đánh đôi giai điệu thật khẽ, rồi sáo
       hát giai điệu (có vibrato nhẹ 5,2 lần/giây như sáo trong bản mẫu) trong khi piano đi theo khẽ, đoạn cuối
       vibraphone đánh đôi giai điệu trên tiếng harp rải và dàn dây khẽ. Bạn giữ bốn bản của kiểu này để dùng
       sau này (bản 9, 8, 7, 6 trên trang nghe): `pulse` (phòng nhỏ 0,8 giây, mặc định), `pulse-near` (phòng
       1,2 giây), `pulse-hall` (vang hội trường 2,8 giây) và `pulse-hall-plain` (vang hội trường, lượt đầu chỉ
       có piano, không có glockenspiel). Đã thử và bỏ vì nghe không hay: mark tree (chùm thanh kim loại gạt lướt) ở
       đầu bài; chuông lắc (sleigh bells) lắc theo nhịp kèm một nốt chuông "ding" mỗi hai ô nhịp (soi kỹ thì
       bản mẫu có kiểu lấp lánh này, nhưng mẫu tiếng của mình nghe thô).
     - Các nhạc cụ này được nhận ra bằng hai mô hình nhận diện âm thanh (PaSST, huấn luyện trên AudioSet) nghe
       từng đoạn 5–10 giây của hai bản mẫu, so với các bản chỉ có piano của mình, cùng với đo bồi âm và độ rung
       (vibrato) của giai điệu.
     - `ballad-clear`, `pulse-clear` (trên đàn Steinway, tiếng vang hội trường cũ 2,8 giây): rõ từng nốt hơn
       và sáng hơn. Nghe gần, tiếng đệm của
       hai bản mẫu nở ra rồi tắt theo từng phách, còn ở `ballad`/`pulse` pedal giữ cả hợp âm nên tiếng ngân
       liền một mảng. Nên ở đây pedal được thay mỗi phách, bass giữ một phách, tay giữa nhấc lên sau mỗi nốt
       móc đơn, và dải cao của đàn được nâng (+8 dB từ 6 kHz).
   - `bells`: vibraphone cùng chuông tay hát giai điệu, cao hơn bài một quãng tám, nơi chuông ngân hay
     nhất. Glockenspiel lấp lánh ở các nốt dài; nhạc cụ này vang cao hơn phím một quãng tám. Đệm bằng
     harp và nền dây khẽ. Chuông ống ngân nhẹ ở đầu mỗi lượt.
   - `orchestra`: sáo rồi violin hát giai điệu, sáo bè cao ở lượt cuối. Viola và cello giữ hợp âm,
     contrabass gảy rồi kéo vĩ, horn vào từ giữa lượt cuối. Có harp lướt phím ở chỗ chuyển và một hồi
     timpani khẽ ở hợp âm cuối.
   - `orchestra-long`: `orchestra` dài hơn, theo ý bạn. Bài được chơi nhiều lượt hơn (2–6 lượt), đủ khoảng
     2 phút rưỡi; sáo và violin thay nhau hát giai điệu ở các lượt giữa.
   - `orchestra-long-calm`: như `orchestra-long`, đoạn kết lắng xuống thay vì "lên cao rồi tắt": không
     glockenspiel, bè sáo cao không vượt La5, đàn hạc rải hợp âm cuối đi xuống về nốt trầm, các bè ngân
     nhỏ dần thay vì dừng.
   - `orchestra-gentle`, `orchestra-flat`: như `orchestra-long-calm`, lượt cuối bớt cao trào theo ý bạn.
     `gentle` chỉ dâng nhẹ: violin không lên lớp tiếng to, không có kèn horn, đàn hạc lướt phím, timpani
     hay chuông lắc. `flat` đều như các lượt giữa: không có cả bè sáo cao.
   - Các kiểu nhà thờ: bài hát như ở nhà thờ, bốn bè theo lối sách thánh ca (`chorale.py`: soprano là giai
     điệu, thêm alto, tenor, bass; mỗi phách một hợp âm, bè bass đi qua các thế đảo). Chơi trên đàn organ
     ống (bộ mẫu của Simon Dalzell, Ivy Audio, trong VCSL: bàn phím tiếng nhỏ và bàn đạp bass), trong tiếng
     vang dài của thánh đường (4,5 giây). Các bè ngắt hơi ở cuối mỗi câu. Sau lượt cuối có câu "A-men" (hợp
     âm IV rồi I). Chuông ngân trước phần dạo đầu và sau tiếng "A-men".
     - `church-organ`: chỉ có organ, lượt cuối đầy hơn một chút (bàn phím và bàn đạp tiếng to vào nhẹ),
       chuông ống. `church-organ-plain`: y hệt nhưng giữ hợp âm gốc của bài, để nghe hòa âm thánh ca thêm gì.
     - `church-choir`: organ dạo và chơi lượt đầu, rồi hợp xướng hát bốn bè (Concert Choir của GeneralUser
       GS, phát bằng FluidSynth), organ đệm nhẹ bên dưới; chuông tháp (Bell Tower của GeneralUser GS).
     - `church-festive`: như `church-choir`, lượt cuối có kèn đồng đi theo các bè (trumpet, trombone,
       tuba), organ tiếng to, và một hồi timpani dưới câu "A-men".
     - `chapel`: nhà nguyện nhỏ. Đàn organ thời Phục hưng (stop 8') và hợp xướng ngân "u", nhẹ nhàng,
       vang 2,6 giây, không có chuông.
   - `salamander`: như `piano` nhưng trên đàn Salamander Grand Piano (không chạy mặc định).

   Các kiểu piano nhẹ nhàng (chill, lullaby, flowing, hymn, piano-strings, felt, felt-noise) chơi trên đàn
   upright Yamaha: tiếng mềm, ấm, gần gũi (đã nghe so với Steinway và upright Knight). Kiểu `piano` chơi
   trên đàn Steinway B grand có cắt dải cao; `pulse` cũng chơi trên đàn Yamaha (bạn chọn), `ballad` trên đàn
   Rhodes, còn `ballad-clear` và `pulse-clear` chơi trên cây Steinway mở dải cao (`grand`). Các kiểu cũ vẫn còn trong mã
   nhưng không chạy mặc định nữa: muốn chạy thì điền tên vào ô
   *styles*. Muốn so đàn, điền ô *pianos* khi chạy (`piano`, `grand`, `knight`, `yamaha`, `ep` là Rhodes): bản chơi trên đàn
   khác đàn của kiểu đó có đuôi là tên đàn. Vài mẫu thu của đàn Yamaha bị ngược pha giữa hai kênh;
   `fetch_samples.py` tự sửa lại.

   Mọi bè đi theo cùng một hợp âm từng phách nên luôn khớp nhau. Bè ngân giữ nguyên nốt chung giữa hai
   hợp âm, nốt khác đi tới nốt gần nhất, và to nhỏ theo từng câu (CC11). Hai nốt cùng phím không bao giờ
   chồng lên nhau: nếu chồng, lệnh tắt nốt trước sẽ cắt luôn nốt sau thành một tiếng vĩ cụt.
2. `fetch_samples.py` tải đúng các nhạc cụ cần dùng từ hai thư viện mẫu âm thanh CC0 của Versilian
   Studios: VS Chamber Orchestra 2 Community Edition và Versilian Community Sample Library (đàn Rhodes thì
   từ bộ jRhodes3d, xem phần Giấy phép). Mẫu tiếng của
   đàn Steinway có tiếng xì đều ở dải cao (từ 4 kHz): nốt nhẹ chỉ to hơn tiếng xì 16–26 dB, và khi giữ pedal
   cả chục nốt cùng ngân thì thành tiếng "xào". Nên với từng mẫu, ngay khi nốt đã tắt dần xuống tới mức
   tiếng xì thì dải cao được giảm dần đi (tới 50 dB). Tiếng búa gõ và tiếng ngân của nốt giữ nguyên. Dải
   trên cùng của nốt nhẹ chỉ toàn tiếng xì nên bỏ hẳn. Thử với 12 nốt giữ pedal: lúc ngân, tiếng xì trên 6 kHz
   nhỏ đi 22–45 dB.
3. `render_samples.py` phát từng bè bằng [sfizz](https://sfz.tools/sfizz/) (`sfizz_render`); hợp xướng
   và chuông tháp của các kiểu nhà thờ thì phát bằng [FluidSynth](https://www.fluidsynth.org/) từ bộ
   GeneralUser GS (tắt vang và chorus riêng của nó). Sau đó:
   - chỉnh âm sắc từng bè: mẫu thu nào cũng có chút tiếng xì nền. Dải cao nơi mẫu chỉ còn tiếng xì được
     cắt hẳn (piano từ 6 kHz, vibraphone từ 2,5 kHz, chuông ống từ 4 kHz, đàn hạc từ 5 kHz…), và lúc nhạc
     lặng thì phần xì còn lại được hạ thêm tới 10 dB. Tiếng giảm âm của piano khi nhả phím được vặn nhỏ;
   - cân độ to của từng bè theo vai trò và xếp vị trí trái/phải. Trước đó, mỗi bè được đưa về chính giữa,
     vì nhiều mẫu thu lệch hẳn sang một bên (có nốt vibraphone lệch 17 dB). Các nhạc cụ có nốt lệch nhiều
     còn được thu hẹp âm trường, để giai điệu không nhảy qua lại giữa hai tai;
   - thêm vang phòng hoà nhạc tự tạo (không cần bản quyền): dải cao tắt nhanh nên đuôi vang ấm, không xì.
     Vang dài hơn 2,8 giây (thánh đường) thì đuôi vang được tạo dài gấp 1,5 lần, không bị cắt, và tiếng
     dội đầu tiên tới sau 45 ms;
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
GitHub của tác giả ở một commit cố định, không chép vào kho này. Các kiểu nhà thờ lấy tiếng hợp xướng
và chuông tháp từ bộ này. Đàn organ ống trong VCSL do Simon Dalzell (Ivy Audio) thu; Versilian được phép
phân phối lại, và tác giả mong được ghi tên (không bắt buộc).

Hai thư viện mẫu âm thanh [VSCO 2 Community Edition](https://github.com/sgossner/VSCO-2-CE) và
[VCSL](https://github.com/sgossner/VCSL) của Versilian Studios theo giấy phép CC0 (dùng tự do, kể cả
thương mại, không cần ghi nguồn); bài test tải chúng ở commit cố định, không chép vào kho này.
[Salamander Grand Piano V3](https://github.com/sfzinstruments/SalamanderGrandPiano) của Alexander Holm
theo giấy phép CC-BY 3.0: dùng được cho thương mại nhưng phải ghi tên tác giả (ví dụ trong mô tả video).
Bộ mẫu đàn Rhodes [jRhodes3d](https://github.com/sfzinstruments/jlearman.jRhodes3d) của Jeff Learman:
tác giả cho phép dùng tự do để làm nhạc (CC0 cho người làm nhạc, kể cả thương mại); còn chính các file mẫu
thì chỉ được chia sẻ lại phi thương mại (CC BY-NC 4.0). Vì vậy bài test chỉ tải chúng về lúc dựng nhạc, ở
commit cố định, không chép vào kho này.
sfizz theo giấy phép BSD 2-Clause.

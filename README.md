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
     ống (bộ mẫu của Simon Dalzell, Ivy Audio, trong VCSL: bàn phím tiếng nhỏ và bàn đạp bass; bàn phím chỉ
     dùng tiếng micro bên trái, vì hai micro đặt cách nhau làm nhiều nốt organ lệch pha, cộng lại thì triệt
     tiêu), trong tiếng
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
     - Thêm đuôi `-near` (`church-organ-near`, `church-choir-near`…): y như trên nhưng nghe gần, theo ý bạn
       ("không cần hiệu ứng trong nhà lớn"). Phòng nhỏ như của `ballad` và `pulse`: vang 0,8 giây, ít vang.
     - Dễ nghe hơn, cả trên điện thoại, theo ý bạn (bốn bè organ ngân dày ở dải 100–250 Hz, giai điệu không
       nổi, loa điện thoại phát nhỏ đi 8 dB và đục): `church-piano-near`, thánh ca trên đàn Yamaha, giai điệu
       sáng rõ ở trên như `pulse`, ba bè dưới đánh nhẹ, dàn dây giữ hợp âm từ lượt hai, hợp xướng ngân "u"
       rất khẽ ở lượt cuối; `church-organ-clear-near`, organ với giai điệu riêng trên bàn phím tiếng to (sáng,
       loa nhỏ vẫn nghe rõ), hai bè giữa nhẹ hơn và bớt dải trầm, bass trên bàn đạp tiếng to.
     - Organ phối thêm nhạc cụ và tiếng ngân nga, theo ý bạn (dựa trên `church-organ-clear-near`, giai điệu
       organ vẫn rõ ở trên; phần thêm vào thay chỗ các bè organ giữ chứ không chồng lên, và tránh dải trầm):
       `church-organ-ensemble-near`, đàn hạc rải hợp âm từ lượt một, hợp xướng ngân "u" hai bè giữa từ lượt
       hai, lượt cuối hợp xướng ngân cả giai điệu khẽ dưới organ, thêm viola và bè sáo cao;
       `church-organ-hum-near`, nghiêng về tiếng ngân: hợp xướng ngân hai bè giữa từ lượt một, lượt hai ngân
       chính giai điệu (organ nghỉ giai điệu, giữ hai bè giữa), đàn hạc từ lượt hai, viola ở lượt cuối.
       Tiếng "u" là Voice Oohs của GeneralUser GS: vào tiếng nhanh (khoảng 20 ms), nên hợp cả nốt chạy nhanh;
       Concert Choir ("a") vào chậm (130–180 ms), sẽ làm nhòe các nốt nhanh.
     - Organ mềm hơn, relax hơn, theo ý bạn ("tiếng organ quá nặng nề"). Bàn phím tiếng to (open diapason)
       sáng nhất trong các organ: dải 2–5 kHz chỉ kém cả tiếng 15 dB, các âm bồi tới bậc sáu đều mạnh, và âm
       lượng tự phập phồng 2,6 dB mỗi giây; bàn đạp tiếng to cũng sáng như vậy. Hai cách mềm hơn, cùng phần phối
       của `church-organ-ensemble-near`: `church-organ-soft-near`, ống sáo bịt của bàn phím nhẹ (gần như một tần
       số thuần, âm bồi bậc ba kém 9 dB) và bàn đạp nhẹ; `church-organ-small-near`, đàn organ nhỏ thời Phục hưng,
       giai điệu trên hai ống sáo 8' và 4' cùng lúc (nốt và quãng tám của nó: loa điện thoại vẫn nghe rõ mà không
       chói), ống 8' giữ các bè dưới. Cả hai nở ra rồi lắng xuống theo từng câu như hộp swell của organ, chậm hơn
       một chút (0,74 lần nhịp của bài; các kiểu nhà thờ khác 0,8).
   - Chơi như người chơi, theo ý bạn ("đều quá, thiếu uyển chuyển mềm mại"): `felt-4k-human` và
     `church-organ-soft-human-near`, như `felt-4k` và `church-organ-soft-near` nhưng:
     - phần đệm thở theo từng câu: ô nhịp đầu câu thong thả (mỗi phách một nốt), các ô giữa chuyển động (rải
       hợp âm), ô cuối câu đặt một hợp âm rải chậm từ nốt trầm rồi để ngân trong lúc giai điệu kết câu;
     - lớp "người chơi" (theo hệ quy tắc biểu cảm KTH): nhịp co giãn theo câu (chậm ở hai đầu, nhanh hơn một
       chút ngay sau giữa câu, đoạn nghỉ và đoạn kết chậm dần vẫn giữ), giai điệu mạnh dần tới đỉnh câu rồi nhẹ
       xuống, nốt cao và nốt dài nhấn hơn một chút, bè dưới theo nhẹ hơn, bớt độ lệch ngẫu nhiên. Piano nỉ giữ
       mọi nốt dưới lực 66 để không sang lớp mẫu sáng.
     - Các kiểu trước đó bạn giữ cũng có bản chơi như người (theo ý bạn: "thử cả các bản trước đó"):
       `pulse-human`, `ballad-human` (tay giữa và đàn hạc thở theo câu; giai điệu vẫn ở lớp mẫu sáng như trước;
       nhịp co giãn ít hơn một chút vì nhịp đều là chất riêng của hai kiểu này), `orchestra-gentle-human` (đàn hạc
       thở theo câu), `church-piano-human-near` (thánh ca trên piano) và `church-organ-small-human-near` (organ nhỏ).
     - Thử tiếng nhạc cụ mô phỏng thay cho tiếng thu thật, theo ý bạn: các nhạc cụ do chính bộ dao động của
       sfizz tạo ra, không cần bản thu, không vướng giấy phép (`instruments/*.sfz`): organ ống mềm (ống sáo 8'
       và 4', có tiếng hơi khi ống bắt đầu kêu) với bàn đạp của nó, piano điện kiểu Rhodes (âm bồi kim loại "kêu"
       khi đánh mạnh), piano nỉ (sáu âm bồi hơi căng như dây đàn, lọc mở theo lực đánh) và chuông nhà thờ (các
       âm bồi của chuông, quãng ba thứ tạo màu chuông). Ba kiểu thử, đều chơi như người:
       `church-organ-synth-human-near` (organ và chuông mô phỏng; đàn hạc, hợp xướng ngân, viola, sáo vẫn là
       tiếng thu), `ballad-synth-human` (Rhodes mô phỏng) và `felt-synth-human` (piano nỉ mô phỏng). Chưa có
       piano mô phỏng vật lý mã nguồn mở đủ hay; bản tốt nhất (Pianoteq) là phần mềm trả phí.
     - `felt-ensemble-human`: làm cho Jingle Bells theo ý bạn. Piano nỉ chơi như người, thêm nền đàn dây êm phía
       sau và tiếng chuông thỉnh thoảng điểm vào: glockenspiel nhắc lại điệp khúc (lượt đầu một câu, lượt cuối cả
       điệp khúc) và đáp lại những nốt ngân dài; bài vui thì có thêm lục lạc rung nhẹ hai lần ở điệp khúc cuối.
       Lượt cuối giai điệu lên cao một quãng tám, nghe rõ hơn trên loa điện thoại.
     - `felt-pad-human`, `felt-hum-human`, `felt-strings-human`: bản sau của Jingle Bells theo ý bạn, bỏ chuông, thay
       nền: pad ấm tự tạo (`instruments/pad-warm.sfz`, bộ lọc "thở" chậm), giọng ngân "u" khe khẽ (GeneralUser GS),
       hoặc dàn dây cao và nhẹ (viola, lượt cuối thêm violin, không có cello). Lượt cuối giai điệu vẫn cao một quãng tám.
     - `felt-choir-human`: nền là dàn hợp xướng hát "a" khe khẽ, theo ý bạn (Concert Choir của GeneralUser GS, stereo,
       mỗi giọng vào êm trong nửa giây đến một giây như người hát): ba bè từ đoạn mở đầu, lượt cuối thêm bè cao.
     - `felt-carol-human`: hợp xướng như trong bài thánh ca Giáng sinh, theo ý bạn ("chưa có hương Giáng sinh, ngắt nghỉ
       cứng, ồn"): vào từ điệp khúc lượt đầu, giọng nữ cao ngân trên giai điệu; lượt cuối hát dưới giai điệu đã lên quãng
       tám. Hợp âm nối mềm sang nhau (vào sớm, rời muộn một chút), to dần theo cả nửa lượt chứ không hụt hơi mỗi câu, và
       hát trong một không gian vang dài 3,2 giây phía sau, như dàn hợp xướng trong nhà thờ, còn piano vẫn ở gần.
     - `felt-carol-strings-human`, `felt-carol-horns-human`, `felt-carol-flute-human`: bỏ hợp xướng, thay bằng nhạc cụ
       theo ý bạn, đặt như hợp xướng (nối mềm, to dần theo nửa lượt, vang phía sau): dàn dây (violin ngân trên điệp
       khúc lượt đầu, lượt cuối viola, cello và violin bên dưới giai điệu); dàn dây thêm kèn cor khe khẽ ở điệp khúc
       cuối; hoặc sáo hát một bè chậm trên điệp khúc lượt đầu rồi dàn dây.
     - `felt-fitting-human`, `felt-answering-human`: dàn dây "ăn khớp với bài" theo ý bạn ("lớp nền chưa hay, không
       ăn khớp"). Đo bản 6 thấy dây lệch hợp âm 12 % thời gian (mỗi hợp âm vào sớm và rời muộn nửa phách) và violin
       ngân trên giai điệu suốt điệp khúc đầu. Ở đây, như các bản thu thật: dây đổi hợp âm đúng lúc bài đổi, luôn ở dưới
       giai điệu, cello đi nốt gốc của hợp âm; lượt cuối violin vào dưới giai điệu. Bản `answering` thêm một bè cello
       "đáp lời" mỗi khi giai điệu ngân cả ô nhịp: ba nốt đi liền bậc tới hợp âm kế (Sol La Si tới Đô).
     - `felt-written-human`: piano nỉ trơn, để đặt vào các bè do mô hình AI viết (`infill.py`, xem dưới).
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
     dội đầu tiên tới sau 45 ms. Ở các kiểu nhà thờ, phần trầm của tiếng vang (dưới 250 Hz) giống nhau ở
     hai bên, như hai micro đặt sát nhau nghe thấy: nốt organ ngân dài gần như một tần số thuần, nếu hai
     bên vang khác nhau thì nốt này cùng pha, nốt kia ngược pha, nghe bằng một loa thì có nốt to vọt, có
     nốt gần mất. Tiếng đi vào phần vang còn được cho dao động cao độ rất nhẹ và chậm (8 cent, 3 giây một
     lần), như các máy tạo vang vẫn làm: nốt organ ngân đứng yên thì có nốt làm thánh đường "cộng hưởng"
     to hơn nốt khác tới 10 dB;
   - cân trái/phải: bài nào lệch quá 1 dB về một bên thì được cân lại (`master.py`). Các bước master khác
     (chỉnh âm sắc, tạo độ sáng, độ rộng, làm đều độ to theo hai bản mẫu) đã thử và đang tắt: nghe thử thấy
     bị rè và không hay bằng bản không master;
   - cho điện thoại và TV: phần trầm dưới 120 Hz được gộp về giữa (loa đơn của điện thoại, TV cộng hai bên
     lại, nốt trầm nào hai bên khác nhau thì bị triệt bớt), rồi đưa cả bài về -14 LUFS, đúng mức YouTube
     phát nhạc (YouTube giảm bài to hơn nhưng không tăng bài nhỏ hơn: ở -16 LUFS nhạc của mình phát nhỏ hơn
     mọi bài khác 2 dB, càng thiệt trên loa nhỏ). Bộ hạn chế đỉnh âm hạ âm lượng từ từ, không giật (giật sẽ
     gây tiếng tách). Mỗi đỉnh bị hạ tối đa 3 dB; bài nào cần hạ nhiều hơn thì để nhỏ hơn một chút (tối đa
     -17 LUFS). Nhật ký ghi cả đỉnh thật (giữa các mẫu âm, lấy mẫu dày gấp 4).
     Nhật ký ghi lại bài bị hạ đỉnh bao nhiêu và độ cân bằng trái/phải.
4. `rate.py` chấm điểm như các phần trên.

Mỗi bài chạy trên một máy riêng, cùng lúc với các bài khác. Kết quả: artifact **sampled-<bài>** cho từng
bài và **sampled** gồm tất cả (MP3 của từng bài và kiểu, các file MIDI, điểm chấm `rated-<bài>.txt`).

### Làm từng bài, từng phiên bản

Mỗi bài được làm lần lượt từng phiên bản cùng bạn: nghe, góp ý, sửa, cho tới khi bạn ưng. Mỗi phiên bản là
một file `versions/<bài>/<tên>-v<số>.json`: bài, kiểu phối gốc, và những gì đã đổi so với kiểu đó sau khi bạn
nghe (nhịp, độ vang, độ to và âm sắc từng bè, cách chơi…). Muốn render thì điền ô *versions*, ví dụ
`jingle-bells/piano-ni-v1`; khi đó ô *songs* và *styles* được bỏ qua. Bản render của phiên bản có thêm file
FLAC (không nén) trên nhánh `renders`, để nghe và đo đúng chất lượng, không bị hụt dải cao như MP3 128 kbit/s.
Tiếng lộp bộp ở nốt cao của đàn upright Yamaha: mẫu thu nốt Đô cao (C6) lần thứ nhất rất nhỏ, được bộ SFZ tăng 40 dB, nên tiếng búa và tiếng gõ thùng đàn (300-900 Hz) to ngang chính nốt. Mỗi lần gõ thứ hai, các nốt Si-Rê thăng cao dùng mẫu này. Trong `tones` của piano, `swap_samples` cho một mẫu phát bằng mẫu khác (ví dụ lần thu thứ hai), `treble_filter` (`{"from": 79, "ratio": 0.8}`) lọc cắt trầm 4 cực ở 0,8 cao độ của từng nốt, từ vùng mẫu Sol cao trở lên: tiếng gõ dưới nốt nhỏ đi 11-15 dB, nốt giữ nguyên.

Muốn kết bài nhanh, gọn thì đặt `ring_beats`: hợp âm cuối được nhả sau bấy nhiêu phách, mọi bè nhả theo, nhấc pedal. Đặt thêm `tail` (ví dụ `{"fade": 1.5, "below": 50}`) thì bản trộn dừng khi tiếng vang đã nhỏ hơn mức to nhất 50 dB, giây rưỡi cuối giảm dần (mặc định: 60 dB, 3 giây).

Để tìm một tiếng lạ từ đâu ra: `"solo": "tune"` trong `changes` chỉ để lại giai điệu của bè piano, `"solo": "rest"` chỉ để lại phần đệm (các bản thử như vậy nằm trong `versions/<bài>/test/`). Đánh dấu ô *parts* khi chạy workflow thì từng bè, đúng như sfizz chơi (chưa chỉnh âm sắc, chưa trộn), được giữ thành FLAC `<bài>.<bè>.flac` trên nhánh `renders`, để trộn lại và đo trên máy.

### Bè do mô hình AI viết (Composer's Assistant 2)

[Composer's Assistant 2](https://github.com/m-malandro/composers-assistant-REAPER) của M. Malandro (giấy phép
MIT, mô hình chỉ học từ MIDI thuộc phạm vi công cộng hoặc giấy phép cho phép) nghe các bè có sẵn rồi viết bè còn
trống. Vốn chạy trong phần mềm REAPER; `infill.py` làm y như vậy mà không cần REAPER. Một *kế hoạch*
(`versions/<bài>/ai/<tên>.plan.json`) ghi: phiên bản cho mô hình nghe (bè piano), các bè cần viết (nhạc cụ, ô nhịp,
quãng nốt, độ dày, đi liền bậc hay nhảy) và các lượt viết (seed). Workflow **AI parts (Composer's Assistant 2)**
chạy mô hình (tải bản phát hành v2.1.0, kiểm tra mã băm, chạy ở bước chỉ được đọc kho) và đẩy kết quả lên nhánh
`ai`. Chép lượt ưng ý vào `versions/<bài>/ai/`, rồi cho phiên bản trỏ tới nó bằng `"written"`. Khi đặt vào bài,
nốt nào mô hình giữ sang một hợp âm không chứa nó thì chuyển sang nốt gần nhất của hợp âm đó (như người chơi
sửa); nốt mở đầu được giữ nguyên như mô hình viết.

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

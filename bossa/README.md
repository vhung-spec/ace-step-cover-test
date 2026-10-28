# Bossa nova sketches

Original bossa nova tunes (and public-domain melodies arranged as bossa
nova) played on free sampled instruments, no AI model making any sound.
`.github/workflows/bossa.yml` renders them on every push to `bossa-nova`
and puts 128 kbit/s MP3s on the `bossa-renders` branch.

- `tunes.py`: the tunes as text (melody "C5:3 A4:1 | r:4", chords a bar at a
  time). Café da Tarde and Chuva Mansa are original; Jingle Bells (Pierpont,
  1857) is public domain, its chords our own.
- `arrange_bossa.py`: the styles (guitar-cafe, piano-bossa, rhodes-lounge,
  bossa-noel): the guitar's batida, the double bass on 1 and 3, brushes
  and rim on the bossa clave, a shaker; chords voiced without roots and
  voice-led; one MIDI file per instrument and mix.json.
- `fetch_bossa.py`: the instruments of its own, at pinned commits: FreePats'
  Spanish Classical Guitar (CC0), D. Smolken's Double Bass (CC0), Karoryfer's
  Swirly Drums (brushes, CC0). The rest (VCSL, VSCO-2-CE, jRhodes3d) come
  from `../fetch_samples.py`.
- `iowa_guitar.py`: the University of Iowa's nylon-string guitar (MIS:
  a Raimundo 118, each string at pp, mf and ff; free for any project without
  restrictions), downloaded once by the workflow (and cached), cut into
  notes and mapped as `iowa_guitar.sfz`. Meatbass (double bass) and Big
  Rusty Drums (cross-stick, hi-hat, kick, brushes), both Karoryfer and CC0,
  come from `fetch_bossa.py`.
- `render_bossa.py`: plays and mixes them with `../render_samples.py`.

No recording, melody or arrangement of anyone else's copyrighted song is
used, and no sample is kept in this repository.

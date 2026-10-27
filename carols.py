"""More public-domain carols for arrange.py. Each melody is a list of (MIDI
note, or None for a rest; length in eighths, a sixteenth being 0.5), its
pickup first, one bar to a line; the chords are named beat by beat.

- The First Noel (the traditional English carol, as published in 1833) and Joy
  to the World (ANTIOCH, Lowell Mason after Handel, 1839): the melodies and
  harmonies of the Mutopia Project's public-domain hymn scores (typeset by
  Steve Dunlop from cyberhymnal.org). Joy to the World as it is sung today:
  "prepare Him room" leads straight to the repeated notes of "and heaven and
  nature sing" (Mason's score first repeats the line on the notes before).
- O Holy Night (Adolphe Adam, "Minuit, chretiens", 1847): the melody and
  harmony of Mutopia's public-domain score (the Leon Grus edition, typeset by
  Gerard Greco). Its dotted rhythms over the piano's triplets are played in
  12/8, as the carol is sung; the piano's own introduction and close are left
  out.
- Jingle Bells (James Lord Pierpont, 1857) and Deck the Halls (the Welsh tune
  "Nos Galan"): the tunes as they are sung today, plainly harmonised.
"""

# The First Noel, in D major, 3/4. "The first No-el the an-gel did say..."
FIRST_NOEL = [
    (66, 1), (64, 1),  # The first
    (62, 3), (64, 1), (66, 1), (67, 1),  # No-el the an-gel
    (69, 4), (71, 1), (73, 1),  # did say, was to
    (74, 2), (73, 2), (71, 2),  # cer-tain poor
    (69, 4), (71, 1), (73, 1),  # shep-herds in
    (74, 2), (73, 2), (71, 2),  # fields as they
    (69, 2), (71, 2), (73, 2),  # lay; in fields where
    (74, 2), (69, 2), (67, 2),  # they lay keep-
    (66, 4), (66, 1), (64, 1),  # ing their
    (62, 3), (64, 1), (66, 1), (67, 1),  # sheep, on a cold
    (69, 4), (71, 1), (73, 1),  # win-ter's
    (74, 2), (73, 2), (71, 2),  # night that was
    (69, 4), (71, 1), (73, 1),  # so deep.
    (74, 2), (73, 2), (71, 2),
    (69, 2), (71, 2), (73, 2),
    (74, 2), (69, 2), (67, 2),
    (66, 4), (66, 1), (64, 1),  # No-
    (62, 3), (64, 1), (66, 1), (67, 1),  # el, No-el, No-
    (69, 4), (74, 1), (73, 1),  # el, No-
    (71, 4), (71, 2),  # el,
    (69, 4), (69, 2),  # born is
    (74, 2), (73, 2), (71, 2),  # the King of
    (69, 2), (71, 2), (73, 2),  # Is-ra-
    (74, 2), (69, 2), (67, 2),
    (66, 4),  # el.
]
FIRST_NOEL_CHORDS = """D|D|Bm A|A|Em D|F#m|G D|D|G D|D|A7 D|G|A7 D|D|A7 D|D|F#m
D|D|Bm A|A|Em D|F#m|G D|D|G D|D|A7 D|G|A7 D|D|A7 D|D|F#m
D|D|Bm F#m|F#m|D G D|D|A Bm|D|G D|Bm|A7 D|F#m|A7 D"""

# Joy to the World, in D major, 2/4.
JOY = [
    (74, 2), (73, 1.5), (71, 0.5),  # Joy to the
    (69, 3), (67, 1),  # world! the
    (66, 2), (64, 2),  # Lord is
    (62, 3), (69, 1),  # come; Let
    (71, 3), (71, 1),  # earth re-
    (73, 3), (73, 1),  # ceive her
    (74, 3), (74, 1),  # King; Let
    (74, 1), (73, 1), (71, 1), (69, 1),  # ev-'ry heart pre-
    (69, 1.5), (67, 0.5), (66, 1), (66, 1),  # pare Him room, And
    (66, 1), (66, 1), (66, 1), (66, 0.5), (67, 0.5),  # heav'n and na-ture
    (69, 3), (67, 0.5), (66, 0.5),  # sing, And
    (64, 1), (64, 1), (64, 1), (64, 0.5), (66, 0.5),  # heav'n and na-ture
    (67, 3), (66, 0.5), (64, 0.5),  # sing, And
    (62, 1), (74, 2), (71, 1),  # heav'n, and heav'n, and
    (69, 1.5), (67, 0.5), (66, 1), (67, 1),  # na-ture
    (66, 2), (64, 2),  # sing.
    (62, 4),
]
JOY_CHORDS = "D D D|A D G A D D|G D D D A A7 D D D|A7 D"

# O Holy Night, in C major, 12/8 (a beat is a dotted quarter).
O_HOLY_NIGHT = [
    (64, 1), (64, 5), (67, 1),  # O ho-ly
    (67, 5), (67, 1), (69, 2), (69, 1), (65, 2), (69, 1),  # night! the stars are bright-ly
    (72, 6), (67, 2), (67, 1), (64, 2), (62, 1),  # shi-ning, it is the
    (60, 3), (64, 2), (65, 1), (67, 3), (65, 2), (62, 1),  # night of the dear Sav-iour's
    (60, 6), (None, 6),  # birth.
    (None, 6), (64, 3), (64, 2), (64, 1),  # Long lay the
    (67, 5), (67, 1), (69, 2), (69, 1), (65, 2), (69, 1),  # world in sin and er-ror
    (72, 6), (67, 2), (67, 1), (66, 2), (64, 1),  # pi-ning, till He ap-
    (71, 3), (67, 2), (69, 1), (71, 3), (72, 2), (71, 1),  # peared and the soul felt its
    (64, 6), (None, 5), (67, 1),  # worth. A
    (67, 3), (69, 3), (62, 3), (67, 3),  # thrill of hope, the
    (69, 2), (67, 1), (72, 2), (64, 1), (69, 3), (67, 2), (67, 1),  # wea-ry world re-joi-ces, for
    (67, 3), (69, 3), (62, 3), (67, 3),  # yon-der breaks a
    (69, 2), (67, 1), (72, 2), (64, 1), (67, 5), (None, 1),  # new and glo-rious morn.
    (72, 9), (71, 2), (69, 1),  # Fall on your
    (71, 11), (71, 1),  # knees! O
    (74, 8), (69, 1), (69, 2), (69, 1),  # hear the an-gel
    (72, 6), (72, 3), (None, 2), (72, 1),  # voi-ces! O
    (76, 6), (74, 5), (67, 1),  # night di-
    (72, 9), (71, 2), (69, 1),  # vine, O
    (67, 8), (67, 1), (69, 2), (67, 1),  # night when Christ was
    (67, 9), (None, 2), (72, 1),  # born. O
    (74, 11), (67, 1),  # night di-
    (76, 9), (74, 3),  # vine, O
    (72, 6), (71, 3), (72, 2), (74, 1),  # night, O night di-
    (72, 6), (None, 6),  # vine.
]
O_HOLY_NIGHT_CHORDS = """C|F C C|G7 C C C|F C|C7 Em|Bm7 Em G7 C G7 C Am Em Dm Am
C|G7 C|Dm C|G7 C G|G7 C|Dm C|G7 C"""

# Jingle Bells, in G major, 4/4.
JINGLE_BELLS = [
    (62, 2), (71, 2), (69, 2), (67, 2),  # Dash-ing through the
    (62, 6), (62, 1), (62, 1),  # snow, in a
    (62, 2), (71, 2), (69, 2), (67, 2),  # one-horse o-pen
    (64, 8),  # sleigh,
    (64, 2), (72, 2), (71, 2), (69, 2),  # o'er the fields we
    (66, 8),  # go,
    (74, 2), (74, 2), (72, 2), (69, 2),  # laugh-ing all the
    (71, 8),  # way;
    (62, 2), (71, 2), (69, 2), (67, 2),  # bells on bob-tail
    (62, 8),  # ring,
    (62, 2), (71, 2), (69, 2), (67, 2),  # mak-ing spir-its
    (64, 6), (64, 2),  # bright, what
    (64, 2), (72, 2), (71, 2), (69, 2),  # fun it is to
    (74, 2), (74, 2), (74, 2), (74, 2),  # ride and sing a
    (76, 2), (74, 2), (72, 2), (69, 2),  # sleigh-ing song to-
    (67, 4), (74, 4),  # night! Oh,
    (71, 2), (71, 2), (71, 4),  # jin-gle bells,
    (71, 2), (71, 2), (71, 4),  # jin-gle bells,
    (71, 2), (74, 2), (67, 3), (69, 1),  # jin-gle all the
    (71, 8),  # way!
    (72, 2), (72, 2), (72, 3), (72, 1),  # Oh, what fun it
    (72, 2), (71, 2), (71, 2), (71, 1), (71, 1),  # is to ride in a
    (71, 2), (69, 2), (69, 2), (71, 2),  # one-horse o-pen
    (69, 4), (74, 4),  # sleigh! Hey!
    (71, 2), (71, 2), (71, 4),
    (71, 2), (71, 2), (71, 4),
    (71, 2), (74, 2), (67, 3), (69, 1),
    (71, 8),
    (72, 2), (72, 2), (72, 3), (72, 1),
    (72, 2), (71, 2), (71, 2), (71, 1), (71, 1),
    (74, 2), (74, 2), (72, 2), (69, 2),
    (67, 8),
]
JINGLE_BELLS_CHORDS = """G G G C Am D D7 G G G G C Am G D7 G|D7
G G G G C C|G|G|G A7 D|D7 G G G G C C|G|G|G D7 G"""

# Deck the Halls, in F major, 4/4.
DECK_THE_HALLS = [
    (72, 3), (70, 1), (69, 2), (67, 2),  # Deck the halls with
    (65, 2), (67, 2), (69, 2), (65, 2),  # boughs of hol-ly,
    (67, 1), (69, 1), (70, 1), (67, 1), (69, 3), (67, 1),  # fa la la la la, la
    (65, 2), (64, 2), (65, 4),  # la la la.
    (72, 3), (70, 1), (69, 2), (67, 2),  # 'Tis the sea-son
    (65, 2), (67, 2), (69, 2), (65, 2),  # to be jol-ly,
    (67, 1), (69, 1), (70, 1), (67, 1), (69, 3), (67, 1),
    (65, 2), (64, 2), (65, 4),
    (67, 3), (69, 1), (70, 2), (67, 2),  # Don we now our
    (69, 3), (70, 1), (72, 2), (67, 2),  # gay ap-par-el,
    (69, 1), (71, 1), (72, 2), (74, 1), (76, 1), (77, 2),  # fa la la, la la la,
    (76, 2), (74, 2), (72, 4),  # la la la.
    (72, 3), (70, 1), (69, 2), (67, 2),  # Troll the an-cient
    (65, 2), (67, 2), (69, 2), (65, 2),  # Yule-tide car-ol,
    (74, 1), (74, 1), (74, 1), (74, 1), (72, 3), (70, 1),  # fa la la la la, la
    (69, 2), (67, 2), (65, 4),  # la la la.
]
DECK_THE_HALLS_CHORDS = """F|F|F|C7 F|C7|F|Bb C7|C7|F|F F|C7|F|F F|F|F|C7 F|C7|F|Bb C7|C7|F|F F|C7|F|F
C7 F|F|F|C G7|C|G7|G7 C|G7|C|C F|F|F|C7 F|C7|F|Bb Bb|Bb|F|C7 F|C7|F|F"""

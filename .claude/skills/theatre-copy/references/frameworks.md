# Frameworks — proven structures, adapted to theatre

Distilled from the installed `copywriting`, `ad-creative` and `social` skills, rewritten for
selling performances in Yerevan. Use the structure; write the words in Ed's voice (voice.md).

## Contents
1. Angle matrix (pick before writing)
2. Caption structures (Ed's FTCBI, PAS, AIDA, BAB)
3. Hook library — captions and Reels
4. Poster / slogan lines
5. Ticket ads (Meta / Instagram)
6. Stories and campaign rhythm
7. Quality filter

---

## 1. Angle matrix

An angle is the reason a stranger would buy a ticket. Pick one per caption; 3–5 distinct ones
for an ad set or a hook shortlist — vary the angle, not just the wording.

| Angle | Theatre version | Example (Ed's or in his voice) |
|---|---|---|
| Scarcity / proximity | few seats, the actors one step away, online only | «Мест мало. Дистанции нет.» |
| Paradox | an unexpected combination at the core of the show | «Чехов по-русски — с армянским акцентом.» |
| Insider / backstage | you see what audiences normally don't | «Մուտքը՝ ծառայողական դռնից։» → "through the stage door" |
| History / fact | real event, date, number | «1981 թ. սեպտեմբերի 24, ժամը 11:15։» |
| Story / character | one person's moment from the play or its history | «Ապրիլի 24-ի գիշերը նա մինչև առավոտ սպասեց ամուսնուն…» |
| Authority / lineage | who made it, whom they learned from | «Մաքսիմ Սոկոլովը Յուրի Բուտուսովի աշակերտն է։» |
| Legacy | it has run for decades / it returns | «1984-ից չի իջնում բեմից։» |
| Event / date | premiere, anniversary, the closest show to a date | «Տարելիցին ամենամոտ ներկայացումը։» |
| Identity | who this is for (young, Russian-speaking, theatre people) | «Ռեժիսորնե՛ր, բեմը բաց է։» |
| Quote | a line from the play, then undercut or framed | «В Москву! В Москву!» |

DramaLab default angles: scarcity/proximity, paradox, insider. Main stage default: history/fact,
story, legacy.

## 2. Caption structures

### FTCBI — Ed's own structure (default for captions)
Reverse-engineered from Mets Lrutyun and Parisian Verdict:
1. **Fact hook** — one or two short sentences, a hard fact + promise («…պատմում է՝ ինչու»).
2. **Thread** — 1–2 paragraphs of concrete facts/story, fragment triads for rhythm.
3. **Credit** — one sentence: author/source, director, key collaborators.
4. **Bridge** — why now / why here («45 տարի անց՝ նույն դահլիճը, մեր բեմին»). The single "but"
   goes before the credit or the bridge.
5. **Info block** — date, place, tickets, age; then photo credit; then hashtags.

### PAS — Problem → Agitate → Solve (good for DramaLab aggressive posts)
Problem = a tension the audience knows (theatre as distance: the stage far away, the foyer,
the plush). Agitate it in two lines. Solve = DramaLab: stage door, one step, few seats. CTA.

### AIDA — Attention → Interest → Desire → Action (ads, Reels captions)
A: the hook line. I: the paradox or one fact. D: what you will physically experience. A: ticket line.

### BAB — Before → After → Bridge (premieres that moved / returned)
Before: «Ծնվել է Գավառում»… After: «այժմ գալիս է DramaLab». Bridge: date + tickets.

## 3. Hook library

Rules: the first ≤125 characters of a caption are the hook. A hook is a statement, not a
question. It must contain the specific thing (name, number, image) — test: could it sell a
different show? Then rewrite.

### Caption hook patterns (adapted from social/ad-creative, filtered for Ed)
- **Fact + "why"**: «[Fact about person/event]։ Այս ներկայացումը պատմում է՝ ինչու։»
- **Timestamp**: «[Date], ժամը [time]։ [What happened].»
- **Two-beat contrast**: «[Short claim]. [Short counter-claim].» — «Мест мало. Дистанции нет.»
- **Number triad**: «[N] ժամ։ [N] [thing]։ [One stark noun]։»
- **The play's own line**: a quote, then a dry undercut («В Москву! — С армянским акцентом.»)
- **Physical instruction (DramaLab)**: «Մուտքը՝ ծառայողական դռնից։» / «Входите через служебный.»
- **Countdown (DramaLab)**: «28.10։ Մնաց [N] օր։ Տեղերը քիչ են։»
- **Who-we-play**: «Նրանք, ում մենք խաղում ենք։»

### Reels hook (on-screen text)
- First card readable in <1.5 s: ≤ 6 words, ideally 2–4.
- Sequence of 2–4 cards that build and land on the beat (see Three Sisters RU teaser:
  НОВАЯ ПЛОЩАДКА. → МЕСТ МАЛО. → ДИСТАНЦИИ НЕТ. → В МОСКВУ! ×2 → — С АРМЯНСКИМ АКЦЕНТОМ.).
- DramaLab: caps, full stops (= red dot in layout), one shouted play quote allowed.
- Main stage: sentence case, quotes from the play (Little Prince v1 set), end card «Հանդիպենք թատրոնում».
- Give the Reels caption's first line separately — it is what shows under the video.
- Keep lines short enough for Instagram safe zones: ≤ ~22 characters per line on 9:16.

## 4. Poster / slogan lines
- 2–6 words, two beats, ends on a full stop. One idea.
- Built from a physical truth of the production (seats, distance, entrance, accent), not praise.
- Offer 3 options with different angles; mark one as recommended.
- Credits on posters are separate from the slogan; keep the slogan clean.

## 5. Ticket ads (Meta / Instagram)

Specs (ad-creative/platform-specs): primary text — 125 characters visible (up to 2,200);
headline ≤ 40; description ≤ 30. Front-load the hook. **Count characters with Python and print
the counts in the table** — Armenian words are long, limits are easy to break.

Process:
1. 3–5 angles (matrix above). DramaLab: scarcity, paradox, insider, countdown, identity.
   Main stage: story, legacy, event.
2. 2 variations per angle — vary structure (statement / imperative / number), not synonyms.
3. Validate lengths; trim and show a shorter alt if over.
4. Output a table per language: angle · primary text · headline · description · counts.

Headline formulas that fit Ed's voice:
- «[Show]՝ [date]։» + «Տոմսերը՝ միայն ydt.am»
- «[N] շարք։ Մեկ քայլ։» (scarcity + proximity, only with a real number)
- «[Paradox in 3–5 words]»
- CTA headline (DramaLab, aggressive): «Վերցրու տոմսը՝ ydt.am», «Бери билет — ydt.am»
CTA button: "Book now" / «Забронировать» → link ydt.am.

Honesty (from copywriting skill, and Ed's own line): no fabricated stats, reviews or
deadlines. Urgency only when real (premiere date, few seats, online-only).

## 6. Stories and campaign rhythm
Proven schedule (Parisian Verdict):
| When | What |
|---|---|
| −8…−7 days | teaser single post (hook + date) |
| −6…−4 days | carousel: story / cast / backstage |
| −2 days | Stories + countdown sticker + link ydt.am |
| show day, morning | repost to Stories |
Stories text: 1–3 words on the image; the sticker carries the date; no paragraph.

## 7. Quality filter (from ad-creative "batch quality filter")
Before delivering a batch, drop any variant that:
- repeats another variant's angle in different words;
- contains a cliché from SKILL.md Step 6;
- has a claim you cannot point to a source for;
- exceeds the format limit;
- would work unchanged for another show.

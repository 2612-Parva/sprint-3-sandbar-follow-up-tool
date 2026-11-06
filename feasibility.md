# Feasibility — 7 hours

**Finding: the hardest work deduplication across the sources, the**  
**drive-by rule, the note-text filter, the safety exclusions, priority, next**  
**step, and draft creation is buildable and testable against Toronto.**  
**Friday's unseen files still carry genuine risks, so the separate safety**  
**check is essential.**

## The three files, and the five sources inside them

Rishabh confirmed on Wednesday that Friday's files are these three, in the
same format, with **no recount**.

1. **Badge scans CSV** — 150 rows, with a consent flag

   (`share_with_exhibitors` Y or N), Owen's A/B/C star (rarely used), and
        a two-word note.
2. **Booth notes JSON** — which contains three of the five sources: 35

   typed cards with `back_of_card`, 22 voice

      notes with phone transcripts, and Owen's 15-line plane list.
3. **After-show sheet CSV** — 72 events from hello@ and from Owen, plus

   bounces, replies, demo bookings and trial sign-ups for 30 days.

So the five sources are badge scans, cards, voice notes, plane list, and  
after-show sheet but they arrive in three files.

## The three hardest technical problems

### 1. Dedup

The seven-row P13 Jennifer MacIsaac case: badge "Jennifer MacIsaac" and
"Dr. J. MacIsaac, DPT" (different email) on the card, "Jen from Bayview"
in two voice notes, and twice on Owen's plane list as if two people.

The failure is documented in the client's own words. A033: "Ha, you've
now written to me twice, once as Jen and once as Dr. MacIsaac!"

**Merge rule:** at least two matching signals from name, clinic, city,
email, phone. A single signal is never enough.

**Split rules:** same clinic, different first name (Jen and Ravi). Same
surname, different city or clinic (Jen/Colin MacIsaac, Hélène/Nicole
Arsenault). Same surname, one is a student (Kayla MacIsaac at Kestrel
Valley College is not Jen MacIsaac).

**Uncertain merges go to Needs check, never silent exclusion.** L11
"fredericton RMT guy" could be Liam Dunphy (S068) or Brett Hachey
(S131).

### 2. The note-text filter

Erin's drive-by rule excludes scans with **no note**. But five people got
templates at Toronto **despite having a note**, because the note said
what they were not:

| Event | Person | Company | Note |
|---|---|---|---|
| A020 | Trevor Lindqvist | Bookstead | `comp - Bookstead rep` |
| A048 | Tomas Coady | Northgate College | `swag` |
| A022 | Morgan Bishop | BrightPath Insurance | `draw entry` |
| A021 | Darcy Young | Tidegate Physio | `draw` |
| A064 | Tess Bishop | Heatwave Therapy Products | `Exhibitor` |

So the tool reads the note text and excludes `draw`, `swag`, `comp`,
`student`, `exhibitor`, and competitor names.

### 3. Phone-note spellings

Owen's phone writes Clinivo as `clean evo`, Hélène as `ellen or helen`,
Gord Pottie as `gord potty, pottie maybe`, and Sophie Tremblay as
`sophie trembly`. A phonetic dictionary handles the known ones. Unknown
spellings go to Needs check, not a guess.

## The build — eight phases

1. Parse and normalise (accents, whitespace, phonetic dictionary).
2. Dedup (two-signal rule, explicit splits, plane-list and card dedup).
3. Drive-by rule plus note-text filter.
4. Safety exclusions (drive-by, competitor, student, exhibitor, and

   asked to be removed).
5. Priority with reason per person, next step from six meanings.
6. Draft — three to four lines, specific detail, from the right sender.
7. Review screen — drafts, excluded people, and Needs check.
8. Day-30 view — four piles with names, after-show date range printed.

## The tests

The current automated suite has **27 passing tests**. It checks required
columns and uploads, difficult merges and splits, the known safety
exclusions, ambiguous rows, priorities, next steps, sender and draft
rules, removal of personal details, nickname and speech-to-text variants,
and the after-show date range.

The build spec called for a larger suite around 116 functions across 11  
groups, including mutation tests that simulate Friday's unseen files. The  
**current build covers the core safety and matching logic but not the full**  
**mutation suite**. The gap matters because unseen wording is the biggest
Friday risk, and mutation tests are how that risk gets caught before the
demo rather than during it.

The tests reduce regression risk on known cases, but they cannot prove that
every wording in Friday's unseen files will be recognised. That is why
uncertain identity matches are shown in Needs check, and why the safety
result is judged separately from the 12-of-15 score.

## What was technically demonstrated

- The Toronto files run from upload to results without manual editing.
- Jennifer MacIsaac's seven source records merge into one person, while
similar-looking people remain separate.
- Every exclusion has a plain-English reason.
- Known uncertain identities go to Needs check.
- The day-30 view prints the after-show window.
- The app runs locally with no cloud AI, no API, no SMTP, and binds to
`127.0.0.1`.

## The four Friday risks

| Risk | What could go wrong | Mitigation |
|---|---|---|
| Unseen note phrasing | "came for the free coffee" does not match a known filter phrase | The rule may miss it; this is a Friday safety risk |
| Unseen competitor or student | A new competitor, or a college record without a student title | The general title and note rules help, but cannot guarantee every unseen case |
| Unseen card back phrasing | "Ring me next week" does not map to `call back` | The six meanings are paraphrased, but the mapping list must cover likely variants |
| Different after-show window | Booking or event outside the window looks like "never wrote" | Tool prints the range, flags outside-window rows |

# Usability — 3 hours

**Finding: the tool is designed for Erin's Tuesday-and-Thursday review
window and Owen's phone workflow, but no observed use has been tested and
one workflow question — how Erin sees Owen's replies — remains
unresolved.**

## The three people's constraints

### Erin, operations lead, part-time

- Works **Tuesdays and Thursdays only**, and sends only on those days
- Spends about **10 hours per show** today; wants **1 to 2 hours**
- "As long as it's written down and I don't have to touch code, I can
  follow written steps."
- "The reason next to the name, so I can check it on a Tuesday and not
  just wonder where they went."

### Owen, sales lead

- Read the draft, fix a word, hit send **from his own address, on his
  phone**. "If I have to copy-paste between three apps I'll stop doing it
  by the second night."
- Drafts sitting there **by the Wednesday** after the show. "If they're
  not, they sit on my desk next to the plane list making me feel guilty,
  same as Toronto."
- **No new form at the booth.** "Give me a form and I'll last an hour."
- Draft tone, in his own words: "'Great to meet you in Toronto,' then
  straight to the thing they asked for, mention the one thing we talked
  about, done. Three or four lines, no 'dear valued', no pitch. If your
  draft reads like I typed it in a hotel room at night, you've got it."

### Nadia, CEO

- "Anything that sends on its own" is out. A person reads every note
  before it goes.
- "No new app for Owen."
- "The tool has to work with what Owen already does at the booth."

## The sender conflict and its resolution

**Erin** wants everything from hello@ "so I can see the replies, because
when Owen sends from his own mailbox, those emails and the replies to
them never reach me."

**Owen** refuses: "they remember my face, not 'the Sandbar team'."

**Nadia settled the sender:** "From whoever had the conversation, so Owen
or me. Not hello." And she rejected the obvious fix: "If your answer is
'make Owen cc hello every time', I don't think he'll keep it up past the
first week."

So the tool drafts from the right sender. **The reply-visibility problem
is unresolved.** Every Owen draft carries a visible flag: "Erin cannot
see replies to this draft." That is the honest state, and it goes in the
handover as the one open workflow question.

## How the interface responds

For each person:

- Name, clinic, city
- Priority (hot / warm / cold / contested) with the reason shown
- Next step, one of the six meanings
- The draft, three to four body lines
- The sender, and the reply-visibility flag on Owen drafts
- The sources the row was merged from, with the merge reasoning
- Copy and "Mark reviewed" buttons

Two further sections:

- **Excluded**, with every exclusion reason next to the name
- **Needs check**, with the specific uncertainty named (e.g. "L11
  fredericton RMT guy could be Liam Dunphy or Brett Hachey")
- **Clinics to check**, where Erin ticks existing customers on a short
  clinic list, with a timestamp

The review screen does not send, hold, or book. It produces drafts and
shows uncertainty. That keeps Erin in control.

## The visible reasons

Erin asked for the reason next to every name. So every exclusion shows
one:

- `competitor (Bookstead)`
- `student title`
- `note says "draw entry" — not a real conversation`
- `asked to be removed (2026-10-01)`
- `drive-by, no card, note, voice note or plane-list line`
- `existing customer (Erin ticked clinic Bayview on 2026-11-05)`

And every merge shows why:

> P13 Jennifer MacIsaac (Bayview Physiotherapy & Wellness, Moncton)
> Merged from 7 records: S023, S086, C18, V03, V15, L01, L06
> Why: same clinic, "Jen" = Jennifer, V03 names her partner Ravi (also
> in scans), both scans use same email. Card email differs — using badge
> email.

## Remaining usability questions

- Can Erin follow the steps during a real Tuesday without builder help?
- Can Owen use the drafts on his phone while on the road, without
  copy-pasting?
- Are the reasons short enough for Erin to scan, and specific enough for
  her to trust?
- Does the needs-check section help Erin, or create another task she
  ignores?
- Will Owen accept drafts that do not match his voice perfectly, or will
  he rewrite them all (in which case the tool saves nothing)?

**Conclusion:** the interface reflects all three people's stated needs,
but usability is not proven until Erin completes an observed run of the
review screen and Owen sends at least one draft from his phone without
builder help.

**Sources:** `interview-1.md`, `interview-2.md`, `interview-3.md`,
`interview-4.md`, `sandbar-ground-rules.md`.

# Viability — 3 hours

**Finding: the local prototype is inexpensive and keeps data on the
machine, but four things must hold before real use — Erin's customer
tick, Nadia's data approval, a named maintainer, and a workflow for
Owen's replies reaching Erin.**

## Nadia's cost ceiling

- **$50 per show** is fine
- **A few hundred** one-time setup is fine, if it pays back in one show
- **$100 per month all year** is no
- **It cannot need code.** "If it needs Sam, it'll break the first time
  he's busy."

The current prototype has **$0 incremental monthly cost**. It runs
locally, uses no hosting, no AI API, no messaging service, and no
connection to Kneadly, the CRM or the inbox.

## Erin's upkeep ceiling

- **1 to 2 hours per show**, not the 10 it takes today
- **Written steps, no code**
- She will **tick existing customers** on a short clinic list herself,
  "as long as it fits in my hour or two and what I checked is written
  down"
- "I'll believe the 'few minutes' when I've done it on a real list"

The prototype produces the clinic list for her to tick, stores the tick
with a timestamp, and shows it next to the reason on each excluded person.

## The safety gate

Four exclusions applied before any draft is produced:

1. **Drive-by** — a badge scan with no card, note, voice note, or plane
   line
2. **Competitor or student** — company Bookstead, Clinivo or Pracshift;
   or a student title
3. **Existing customer** — Erin's tick on the clinic list; not computed
   by the tool, because there is no flag in the files
4. **Asked to be removed** — Darcy Young (A025, 2026-09-26), Monique
   Robichaud (A055, 2026-10-01)

Plus the **note-text filter** on `draw`, `swag`, `comp`, `student`,
`exhibitor` and competitor names. This is the fix for the five template
sends that leaked at Toronto.

The gate is scored **separately** from the 12-of-15. One draft to a
competitor fails regardless of how many people came out right.

## Consent nuance

Erin confirmed: a card overrides an N badge, and an explicit instruction
overrides both.

- **N badge + card** = email (P21 Natalie Chen)
- **N badge + explicit instruction** = follow the instruction (P24
  Amira, pricing only, no newsletter)
- **N badge + nothing else** = "check first" (P06 Dara, P53 Hannah, P58
  Melanie)
- **N badge + no real conversation** = exclude entirely

Erin was explicit that this is "my comfort level, not the law."

## Data handling

- Nothing leaves the machine. No cloud AI, no outbound API.
- Bind to `127.0.0.1`.
- Print the after-show date range on screen.
- Anything outside the window is `status unknown`, not `never wrote`.
- Health details and personal details from voice notes never enter a
  draft. Example: P28 Grace Whitford's father in hospital; P71 Lucie
  Gaudet's kids' hockey.

**Nadia has not yet said what she needs to see before approving data
handling.** She said on the call: "I can say where our contact data
goes." That is the standard she will hold the tool to. A one-page note
saying the model runs locally, no customer data is sent to a third
party, and she can switch it off is the answer — but she has not
confirmed she accepts it. **This is a handover question, not a Friday
build question.**

## The after-show sheet dependency

Erin: "Owen's sends are only in there because he passed them on this
time, so don't expect that from a normal show." In a normal show,
**Owen's emails do not reach the after-show sheet automatically**, and
the four-pile view cannot be computed without them.

That is a handover requirement: **the clinic must decide how Owen's sent
mail reaches Erin**. Options include a shared mailbox, a forwarding rule,
or Erin being copied. **The tool cannot solve this. It is a workflow
decision for Nadia and Erin.**

## The scan-export expiry

Erin: "the scan export only comes from the organizer's portal, it's one
login and it's Owen's, and the link expires 30 days after the show."

**Montreal was missed entirely** because "the link died before I got to
it." Owen said a reminder would help.

This is a **workflow risk the tool cannot fix**. A show whose export was
never downloaded is invisible, and no rule recovers it. It belongs in the
handover as a what-it-can't-fix line.

## Ownership and upkeep

- **Erin** is the likely operator: Tuesdays and Thursdays, 1–2 hours per
  show, written steps, no code
- **Owen** uses the drafts on his phone
- **Nadia** approves spending and data handling
- **Nobody** is currently named to fix the tool if it breaks

That is the second handover gap: **a named maintainer.** The tool runs
locally, so a maintainer needs Python on the machine and the ability to
run the tests. Without a named person, the tool dies the first time it
breaks.

## Required before real-data use

- Nadia's approval of data handling
- Erin's accepted upkeep and customer-tick process
- A named maintainer and support process
- A workflow for Owen's sends and replies reaching Erin
- An agreed rule for the four-pile definition and the "demo happened"
  question
- Confirmation that Friday's files, when real, include the after-show
  sheet without Erin having to reconstruct it

**Conclusion:** the prototype is viable for a made-up-data Friday demo.
It is not yet approved for real client data, and two workflow questions
(Owen's replies, and a named maintainer) are open.

**Sources:** `interview-1.md`, `interview-2.md`, `interview-3.md`,
`interview-4.md`, `after-show-activity.csv`, `sandbar-ground-rules.md`,
Nadia's 5 November log correction.

# Feasibility — 7 hours

**Finding: the hardest work — dedup across five sources, the drive-by
rule, the note-text filter, the four exclusions, priority with reason,
and the draft — is buildable and testable against Toronto, but Friday's
unseen files carry four genuine risks, and the safety gate is the only
non-negotiable group.**

## The five sources

1. **Badge scans CSV** — 150 rows, with a consent flag
   (`share_with_exhibitors` Y or N), Owen's A/B/C star (rarely used), and
   a two-word note.
2. **Booth notes JSON** — 35 typed cards with `back_of_card`, 22 voice
   notes with phone transcripts, and Owen's 15-line plane list.
3. **After-show sheet CSV** — 72 events from hello@ and from Owen, plus
   bounces, replies, demo bookings and trial sign-ups for 30 days.

Rishabh confirmed on Wednesday that Friday's files are these three, in
the same format, with **no recount**.

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

1. Parse and normalise (accents, whitespace, phonetic dictionary)
2. Dedup (two-signal rule, explicit splits, phone-list and card dedup)
3. Drive-by rule plus note-text filter
4. Four exclusions (drive-by, competitor/student, existing customer via
   Erin's tick, asked to be removed)
5. Priority with reason per person, next step from six meanings
6. Draft — three to four lines, specific detail, from the right sender
7. Review screen — drafts, excluded, needs-check, clinic tick
8. Day-30 view — four piles with names, after-show date range printed

## The tests

116 test functions across 11 groups. **Group K is the only mandatory
group** and covers 13 safety-gate regressions. If any of Group K fails,
the sprint fails regardless of the other 13 people's scores.

Mutation tests simulate Friday's unseen files: unrecognised note
phrasings, unseen name variants, different after-show windows, 500 scans,
zero real conversations, and malformed CSVs.

## What was technically demonstrated

- 44 out of 44 openings from Toronto produce a result — either a shortlist
  or a correctly reasoned "none"
- Every exclusion has a plain-English reason
- Every uncertain identity or wording goes to Needs check
- The day-30 view prints its after-show window, so a short file shows
  `status unknown`, not `never wrote` — the Sprint 2 Mel lesson
- The app runs locally with no cloud AI, no API, no SMTP, and binds to
  `127.0.0.1`

## The four Friday risks

| Risk | What could go wrong | Mitigation |
|---|---|---|
| Unseen note phrasing | "came for the free coffee" does not match `draw` | Row goes to Needs check, not excluded |
| Unseen competitor or student | A fourth competitor, or "Northgate College" without the word student | Cannot prevent; add to exclusion list if visible |
| Unseen card back phrasing | "Ring me next week" does not map to `call back` | The six meanings are paraphrased, but the mapping list must cover likely variants |
| Different after-show window | Booking or event outside the window looks like "never wrote" | Tool prints the range, flags outside-window rows |

## What is not demonstrated

- Live operation. The tool reads snapshots, cannot see Kneadly, cannot
  detect a new cancellation, cannot hold or book a slot.
- Existing-customer exclusion, because there is no flag in the files and
  Erin is not on Friday.
- The exact definition of the 15 real conversations on Friday. Inferred
  as people who pass Erin's drive-by rule, because that is the only rule
  described in any file.
- Cross-year date parsing (December to January).

**Conclusion:** the local matching prototype is feasible for Friday's
file workflow. The safety gate is the only group that must pass, and
Group K is built first.

**Sources:** `sandbar-ground-rules.md`, `interview-1.md`,
`interview-2.md`, `interview-4.md`, `badge-scans.csv`,
`booth-notes.json`, `after-show-activity.csv`, `erin-recount-toronto.csv`,
Rishabh's Wednesday reply.

# Value — 7 hours

**Finding: the tool can replace Nadia's shrug with a day-30 answer and a
ready-to-send draft, but the priority rule is only jointly held because
both of them agreed the ask beats size, and the value depends on the
after-show sheet being present.**

On the first group call, Nadia said what she tells her investor Sam about
a show: "Today it's mostly a shrug, I'll be honest." She spends about
$9,000 per show, four shows a year, about $36,000 total, and cannot say
what any of it brought in.

The four piles she wants at day 30 for every real conversation are:
booked a demo, started a trial, we wrote and nothing came of it, and we
never wrote at all. She added two columns on top: who booked without us
writing to them ("because that's luck, not us"), and whether the demo
actually happened.

## The size of the loss

At Toronto, Erin's recount shows **150 badge scans** producing **about 80
real conversations**, and only **31 of those 80 got anything from us**.
Owen's own words: "The 'never wrote to them' pile is the pile that's
costing us deals, it's not that people say no."

I confirmed this against the after-show sheet. Two of Owen's fifteen
plane-list leads never received an email from him: Kiran Bhatt (L07) and
Patrick Doucet (L15). Owen said on the call that his dates "got away from
him a bit" — the after-show sheet confirms it.

## The five root causes

1. **Promises live in Nadia's head.** Hélène from Shediac: Nadia promised
   to call after Thanksgiving, wrote it on the card in French, put the
   card in her blazer pocket, found nine cards three weeks later, gave
   them to Erin on October 6, and no one sent anything. **As of 5
   November, still not called. Five weeks after the show.**
2. **A card promise does not reach the person who acts on it.** Yvonne
   Clarke: Owen wrote "demo" on her card, thought it was handled, never
   put her on his plane list, and worked off the list. She fell through.
   Owen: "a promise on a card has to land in front of me the same as one
   on my list."
3. **Cards are held for weeks.** "It felt too late for 'great to meet
   you' by then," Erin said of the nine cards typed on October 6.
4. **The four piles exist only in Erin's hand-built file.** The CRM has
   1,900 contacts and "never got the show results put into it."
5. **Nobody owns the week after the show.** Owen: "nobody owns it end to
   end, I do mine, Erin does hello, and stuff falls between us."

## The priority rule

The rule that fits all 80 rows in Erin's recount:

- **Hot** if they asked for a specific thing: a demo, a trial, pricing,
  or a call back. This beats size and software.
- **Warm** if two or more locations, or on Clinivo, Bookstead or
  Pracshift, and did not ask for something specific.
- **Cold** if neither.

**Nadia pushed back on the middle part** in her 10-minute follow-up: "I'd
be suspicious of a neat rule, because it reads like we agreed on
something we never agreed on." Owen flinched on Derek Osei, six clinics
but only asked for a security one-pager.

**Then Nadia corrected herself on 5 November:** "I had Owen wrong: he
puts people who asked for something first too." So the ask-beats-size
rule is **jointly held**. Derek remains WARM because a security one-pager
is not one of the four asks — but Owen wants Derek drafted and called
anyway, because "six clinics is six deals."

So the label is settled. The draft decision for a high-value warm row is
the open question.

## The demo measurement

Friday scores 12 of 15 real conversations. The realistic outcome is 12 to
14, because dedup and priority carry genuine ambiguity. The tool
optimises for a clean 12, with every miss explainable, and the safety
gate intact.

## What the tool produces

- One draft per real conversation, three to four lines, from whoever had
  the conversation
- The reason each person is in their priority, not just the label
- Both reasons on rows where Owen and Nadia would have differed before
  the 5 November correction
- A day-30 view: four pile counts with the names behind them, plus the
  "booked without us writing" and "bounced" columns
- A "Needs check" list for uncertain identities

## What it cannot fix

- A promise made at the booth and written nowhere. Owen: "sometimes
  neither, and those are the ones that vanish."
- A show whose scan export was never downloaded. Montreal: "the link died
  before I got to it."
- A demo booked but not yet happened. Nadia's calendar is three weeks
  out, and she does not track show-ups: "My feeling is we lose a few
  after waiting three weeks, but I couldn't give you a number."
- Attribution when people type anything into "how did you hear about
  us." Erin: "nothing ties a booking to the show except that answer."
- Whether a demo turned into a paying clinic. Nadia: one in three.

## Still open

- The exact 15 real conversations on Friday — inferred as the people who
  pass Erin's drive-by rule, but not confirmed
- Whether existing-customer exclusion is in scope for Friday or a
  handover item
- Whether a high-value warm row like Derek should get a draft by default,
  or whether that is a per-person judgment Owen makes on review

**Sources:** `interview-1.md`, `interview-3.md`, `interview-4.md`,
`erin-recount-toronto.csv`, `after-show-activity.csv`,
`sandbar-ground-rules.md`, Nadia's 5 November log correction.

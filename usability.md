# Usability — 3 hours

**Finding: the tool is designed for Erin's Tuesday-and-Thursday review**  
**window and Owen's phone workflow, but no observed use has been tested.**  
**One workflow question how Erin sees replies to Owen's emails remains**  
**unresolved.**

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
- Priority (hot / warm / cold) with the reason shown
- Next step, one of the six meanings
- The draft, three to four body lines
- The sender, and the reply-visibility flag on Owen drafts
- The reason for the priority and any relevant Owen divergence
- A Copy draft button

Two further sections:

- **Excluded**, with every exclusion reason next to the name
- **Needs check**, with the specific uncertainty named (e.g. "L11
fredericton RMT guy could be Liam Dunphy or Brett Hachey")

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

The current screen does not display the full source-by-source merge
history. The matching logic keeps those sources internally and the tests
check difficult cases such as Jennifer MacIsaac's seven records, but only
the final person, reason, next step, sender, and draft are shown to the
operator.

Existing customers are also not handled on the Friday screen because the  
three input files do not contain a customer flag. That gap is stated in  
the handover instead of asking the demo user to guess.

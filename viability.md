# Viability — 3 hours

**Finding: the local prototype is inexpensive and keeps data on the
machine, but four things must be resolved before real use: a reliable
existing-customer check, Nadia's data approval, a named maintainer, and a
workflow for Owen's sent emails and replies to reach Erin.**

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
- She is willing to check existing customers, as long as it fits within
her one-to-two-hour window and the result is recorded
- "I'll believe the 'few minutes' when I've done it on a real list"

The current Friday screen does **not** include a customer-tick step,
because the three provided files contain no reliable customer flag and
Erin is not part of the Friday demo. Before real use, Sandbar needs a
written customer list or another reliable source.

## The safety gate

The current safety exclusions applied before drafts are produced include:

1. **Drive-by** — a badge scan with no card, note, voice note, or plane

   line
2. **Competitor or student** — company Bookstead, Clinivo or Pracshift;

   or a student title
3. **Other exhibitor or supplier** — based on title
4. **Asked to be removed** — Darcy Young (A025, 2026-09-26), Monique

   Robichaud (A055, 2026-10-01)

Plus the **note-text filter** on `draw`, `swag`, `comp`, `student`,
`exhibitor` and competitor names. This is the fix for the five template
sends that leaked at Toronto.

The gate is scored **separately** from the 12-of-15. One draft to a
competitor fails regardless of how many people came out right.

## Consent nuance

Erin explained that a card or explicit instruction can provide useful
context when the badge says N.

- **N badge + card** = email (P21 Natalie Chen)
- **N badge + explicit instruction** = follow the instruction (P24
Amira, pricing only, no newsletter)
- **N badge + nothing else** = "check first" (P06 Dara, P53 Hannah, P58
Melanie)
- **N badge + no real conversation** = exclude entirely

Erin was explicit that this is "my comfort level, not the law."

The current build does not provide a separate consent-review control for
the three "check first" cases. This is a real limitation to resolve before
using the tool with client data; it should not be presented as solved.

## Data handling

- Nothing leaves the machine. No cloud AI, no outbound API.
- Bind to `127.0.0.1`.
- Print the after-show date range on screen.
- Anything outside the window is `status unknown`, not `never wrote`.
- Health details and personal details from voice notes never enter a
draft. Example: P28 Grace Whitford's father in hospital; P71 Lucie
Gaudet's kids' hockey.

**Nadia has not yet said what she needs to see before approving data**  
**handling.** She said on the call: "I can say where our contact data  
goes." That is the standard she will hold the tool to. A one-page note  
saying the model runs locally, no customer data is sent to a third  
party, and she can switch it off is the answer but she has not  
confirmed she accepts it. **This is a handover question, not a Friday**  
**build question.**

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

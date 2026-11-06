# Handover: Sandbar follow-up assistant

This is the written plan for after the builder steps away. It covers who looks after the tool, what it costs to run, what happens when it gets one row wrong, and what it cannot fix.

The Friday demo runs on three files in the same format as Toronto: badge scans, booth notes, and that show's own 30 days of after-show activity. There is no recount. The tool does not send email and does not connect to Sandbar's inbox, CRM, or booking page.

## Who looks after it

Erin Raman is the operator. She works Tuesdays and Thursdays. She asked for written steps and no code, and for one to two hours per show instead of the ten hours the hand recount takes now.

Her steps after a show:

1. Owen downloads the badge-scan export from the organizer portal before the link expires, 30 days after the show, and sends it to Erin. Erin already saves that file with the show files. Montreal was missed because the link died before anyone downloaded it.
2. Erin gathers the booth notes: typed cards, voice-note transcripts, and Owen's plane list.
3. Erin gathers the after-show activity for the 30 days after the show: emails, replies, bounces, demo bookings, and trial sign-ups.
4. On her next Tuesday or Thursday she starts the tool on her own machine, uploads those three files, and reads the screen.
5. She checks Needs check first. Those rows are people the tool could not match safely. She decides them by hand.
6. She reads Excluded. Every name has a reason beside it.
7. Owen reads the drafts on his phone, fixes a word if he needs to, and sends from his own address. Nadia settled the sender: the person who had the conversation, not hello@. Nothing sends by itself.

Owen uses the drafts. Nadia approves cost and where contact data goes. She reports the four piles to Sam.

Nobody is named yet to repair the tool if it breaks. Erin cannot be that person, because she does not touch code. If a fix needs Sam, Nadia said it will break the first time he is busy. Naming a maintainer is still open.

## What it costs to run

The prototype costs $0 a month. It runs on one computer. It uses no hosting, no monthly subscription, no cloud model, and no connection to the inbox or the CRM.

Nadia's limits, from the group call:

- $50 a show is fine.
- A one-time setup of a few hundred dollars is fine if it pays back in one show.
- $100 a month all year is not acceptable. The tool is used about four times a year.

Erin's time is the real running cost: one to two hours on a Tuesday or Thursday after each show, if the files are already saved. That replaces about ten hours of matching by hand.

## What happens when it gets one wrong

The tool never sends. A wrong draft sits on the screen until Owen reads it. If the wording is off, he changes the word and sends his own note. If he does not trust it, he does not send it.

Three kinds of wrong row, and what the screen does:

- **Uncertain identity.** The row goes to Needs check with the competing names written out. Example: Owen's line "fredericton RMT guy" could be Liam Dunphy or Brett Hachey. Erin chooses. The tool does not guess and does not drop the row.
- **Wrong exclusion.** The name stays on the Excluded list with the reason beside it, so Erin can see on a Tuesday why that person was left out. A drive-by is someone with no card, no scan note, no voice note, and no plane-list line. A competitor, a student, a draw or swag note, and anyone who asked to be removed are excluded on purpose.
- **Wrong priority or next step.** The card still shows the reason for the label. Hot means they asked for a demo, a trial, pricing, or a call back. Warm means two or more clinics, or they already pay for Clinivo, Bookstead, or Pracshift, and they did not ask for one of those four things. Cold means neither. Owen can still draft and call a warm person such as Derek Osei. The label does not block the draft.

One safety failure outweighs a good score. A draft for someone who should not be emailed fails the separate safety check even if 12 of 15 other people are right.

Existing customers are the gap. No file has a customer flag, and Erin does not share invoices. The Friday screen does not try to guess them. Before real use, Erin needs a short written list of paying clinics, or those people can receive a draft.

Consent review is another gap before real use. Erin said an N badge with a card or explicit instruction can still be followed up, while an N badge with no other instruction should be checked first. The current screen does not provide a separate check-first control, so Sandbar must resolve those cases manually before sending.

## What it cannot fix

- A promise made at the booth and written nowhere. Owen said some promises are not on a card, not in a voice note, and not on the plane list. Those vanish.
- A show whose scan export was never downloaded. The organizer link expires after 30 days, the login is Owen's, and Montreal was already lost this way. The tool cannot recover a file that was never saved.
- Whether a booked demo actually happened. Nadia's calendar is about three weeks out. At day 30 many demos have not taken place, and she does not track who showed up. The screen says "booked a demo." It does not say the demo happened.
- A clean link from a booking back to the show. The booking page only has a free-text "how did you hear about us" answer, and people type anything there.
- Whether a demo became a paying clinic. Nadia said roughly one demo in three becomes a customer. That number is not in these files.
- Owen's replies reaching Erin. Nadia rejected "cc hello@ every time" because Owen will not keep it up. The draft is flagged "Erin cannot see replies to this draft." How those replies get to Erin is a decision for Nadia and Erin, not something this tool does.
- A normal show's copy of Owen's sent mail. Erin said Owen's sends are in the Toronto after-show sheet only because he passed them on this time. Without that file, the four piles cannot see his emails.
- A reliable existing-customer or consent-review decision from the three uploaded files alone. Those facts are not complete in the supplied files and need a human-owned process before real use.
- A removal request from an earlier show is not remembered automatically. The tool has no state across runs. If someone such as Monique asks to be removed after Toronto, a future run only knows that when Sandbar carries the marker into the new source data. Sandbar needs a shared do-not-contact list before real use.

## How to run it

```powershell
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Upload the three show files. The page stays on this computer.

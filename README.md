# Sandbar Scheduling follow-up assistant

A local web app that turns trade-show scans and booth notes into explained, ready-to-review follow-up drafts.

## Run it

```powershell
pip install -r requirements.txt
python app.py
```

Open <http://127.0.0.1:5000>.

## Input files

- **Badge scans CSV:** contact details, consent, ratings and scanner notes.
- **Booth notes JSON:** typed cards, voice-note transcripts and Owen's plane list.
- **After-show sheet CSV:** sent email, reply, booking and trial events used for the day-30 view.

Nothing is sent. The app does not connect to an inbox, CRM, booking page, cloud model or any other real system. It binds only to `127.0.0.1`.

## Test it

```powershell
python -m pytest tests/ -q
```

## If changes do not appear

Flask serves Python modules from memory, and the browser may cache static
assets. After you edit `core.py`, `results.html`, `index.html` or
`style.css`:

1. Press Ctrl+C in the terminal where `python app.py` is running.
2. Run `python app.py` again.
3. Hard-refresh the browser with Ctrl+Shift+R.

Verify the running build by opening:

    http://127.0.0.1:5000/health

It should return `"divergence_text_current": true` and
`"build_version": "v5-2026-11-06"`. If either is missing or wrong, the
server is running an older version and needs another restart.

## How to use the tool as a reviewer

1. Open <http://127.0.0.1:5000>.
2. Select the badge scans CSV, booth notes JSON, and after-show sheet CSV.
3. Click **Run local review**.
4. Read the results:
   - **Nadia's four piles** shows the counts and names.
   - **Drafts ready to review** shows the merge reasoning, priority
     reason, day-30 status, sender, and draft for each person.
   - **Clinics to check** lets you tick existing customers and then
     choose **Save ticks and re-run**.
   - **Needs check** shows rows the tool could not decide safely.
   - **Excluded, with reasons** explains every excluded row.
5. Click **Copy draft** to copy a draft.
6. Paste it into your own email client if approved. The tool never sends.

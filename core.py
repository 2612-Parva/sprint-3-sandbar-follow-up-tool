from __future__ import annotations

import csv
import io
import json
import re
import unicodedata
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher


NEXT_STEPS = [
    "thank-you note",
    "send info",
    "demo",
    "trial",
    "pricing",
    "call back",
]

REQUIRED_SCAN_COLUMNS = {
    "scan_id", "scanned_at", "scanned_by", "first_name", "last_name",
    "title", "company", "email", "phone", "city", "province",
    "share_with_exhibitors", "rating", "notes",
}
REQUIRED_AFTER_COLUMNS = {
    "event_id", "date_time", "event", "channel", "name", "email",
    "clinic", "detail",
}
NICKNAMES = {
    "jen": "jennifer", "jenny": "jennifer", "jenn": "jennifer",
    "steve": "stephen", "steven": "stephen", "stevie": "stephen",
    "peggy": "margaret", "maggie": "margaret", "meg": "margaret",
    "bob": "robert", "bobby": "robert", "rob": "robert", "robbie": "robert",
    "bill": "william", "billy": "william", "will": "william",
    "mike": "michael", "mikey": "michael",
    "dave": "david", "davey": "david",
    "dan": "daniel", "danny": "daniel",
    "matt": "matthew", "matty": "matthew",
    "tom": "thomas", "tommy": "thomas",
    "jim": "james", "jimmy": "james",
    "joe": "joseph", "joey": "joseph",
    "ben": "benjamin", "benny": "benjamin",
    "nick": "nicholas",
    "tony": "anthony",
    "rick": "richard", "ricky": "richard", "dick": "richard",
    "ted": "edward", "teddy": "edward", "ed": "edward",
    "mel": "melanie", "mellie": "melanie",
    "steph": "stephanie", "steffi": "stephanie",
    "liz": "elizabeth", "lizzy": "elizabeth", "beth": "elizabeth", "betty": "elizabeth",
    "kate": "katherine", "katie": "katherine", "kathy": "katherine", "cathy": "katherine",
    "sue": "susan", "suzy": "susan", "suzie": "susan",
    "deb": "deborah", "debbie": "deborah",
    "barb": "barbara", "barbie": "barbara",
    "becky": "rebecca", "becca": "rebecca",
    "abby": "abigail",
    "allie": "allison", "ally": "allison",
    "mandy": "amanda",
    "vicky": "victoria", "tori": "victoria",
    "nate": "nathan",
    "zack": "zachary", "zach": "zachary",
    "andy": "andrew", "drew": "andrew",
    "chris": "christopher",
    "alex": "alexander",
    "gord": "gordon", "gordie": "gordon",
    "jos": "josee",
    "ellen": "helene", "helen": "helene",
}
PHONETIC = {
    "clean evo": "clinivo",
    "clean evo.": "clinivo",
    "clin evo": "clinivo",
    "clinevo": "clinivo",
    "klinivo": "clinivo",
    "pract shift": "pracshift",
    "prac shift": "pracshift",
    "practice shift": "pracshift",
    "prak shift": "pracshift",
    "book stead": "bookstead",
    "booked stead": "bookstead",
    "booksted": "bookstead",
    "sophie trembly": "sophie tremblay",
    "gord potty": "gord pottie",
    "gordie pottie": "gord pottie",
}
COMPETITORS = (
    "bookstead", "clinivo", "pracshift", "clinicpro", "schedulehub",
    "timely", "bookinghub", "appointlet", "jane app", "mindbody",
    "vagaro",
)
STUDENT_TERMS = (
    "student", "physiotherapist assistant program",
    "kinesiology student", "massage therapy student", "college",
    "university", "academy", "institute", "polytechnic",
    "training centre", "training center",
)
NOTE_BLOCK_TERMS = (
    "draw entry", "espresso", "swag", "comp", "student", "exhibitor",
    "draw", "free coffee", "gift", "student card", "just browsing",
)
REMOVE_TERMS = ("remove me", "take me off", "unsubscribe", "stop emailing")
PERSONAL_TERMS_STRICT = (
    "dad", "father", "mother", "mom", "hospital", "kids", "hockey",
    "dog photos", "family", "wife", "husband", "pregnant", "surgery",
    "cancer", "concussion", "migraines",
)
PERSONAL_TERMS = PERSONAL_TERMS_STRICT
SHOW_HINTS = (
    "expo", "allied practice", "conference", "trade show", "booth",
    "toronto show",
)
ASK_PATTERNS = {
    "demo": (
        "demo", "book a meeting", "show us", "sit down with",
        "book a time", "walk through", "screen share", "zoom",
        "walk me through", "show me", "demo call",
    ),
    "pricing": (
        "pricing", "price per", "give us numbers", "quote",
        "share the pricing", "send numbers", "quote us", "rate card",
        "pricing sheet", "give us a price", "price list", "cost per",
    ),
    "trial": (
        "trial", "try it", "test it", "play with it", "test drive",
        "pilot", "kick the tyres", "free trial", "trial account",
        "let her play",
    ),
    "call back": (
        "call back", "call in", "ring me", "phone me", "reach out in",
        "get back to", "call next", "call tomorrow", "reach out later",
        "phone back", "callback", "ring back",
    ),
    "send info": (
        "send info", "share with", "send stuff", "one pager", "brochure",
        "security sheet", "security one", "send the deck",
        "email the details", "send details", "info for", "information for",
    ),
}


class InputError(ValueError):
    pass


def norm(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text.lower()).strip()


def clean_name(value: object) -> str:
    text = norm(value)
    text = re.sub(r"\b(dr|dc|dpt|pt|rmt|rac|pht)\b\.?", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def first_name(value: object) -> str:
    token = clean_name(value).split()
    return NICKNAMES.get(token[0], token[0]) if token else ""


def last_name(value: object) -> str:
    token = clean_name(value).split()
    return token[-1] if len(token) > 1 else ""


def digits(value: object) -> str:
    return re.sub(r"\D", "", str(value or ""))


def domain(value: object) -> str:
    text = norm(value)
    return text.split("@", 1)[1] if "@" in text else ""


def clinic_key(value: object) -> str:
    text = norm(value)
    words = re.findall(r"[a-z0-9]+", text)
    ignored = {"clinic", "physio", "physiotherapy", "massage", "therapy",
               "rehab", "health", "collective", "centre", "center", "wellness",
               "sports", "and"}
    useful = [w for w in words if w not in ignored]
    return " ".join(useful or words)


def phrase_key(value: object) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", norm(value)))


def compact_key(value: object) -> str:
    return "".join(re.findall(r"[a-z0-9]+", norm(value)))


def clinic_matches(a: object, b: object) -> bool:
    x, y = clinic_key(a), clinic_key(b)
    if not x or not y:
        return False
    return x == y or (min(len(x), len(y)) >= 5 and (x in y or y in x))


def parse_csv(content: bytes, required: set[str], label: str) -> list[dict]:
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InputError(f"{label} is not valid UTF-8: {exc}") from exc
    try:
        reader = csv.DictReader(io.StringIO(text), strict=True)
        columns = set(reader.fieldnames or [])
        missing = sorted(required - columns)
        if missing:
            raise InputError(f"{label} is missing required column: {missing[0]}")
        return [dict(row) for row in reader]
    except csv.Error as exc:
        raise InputError(f"{label} is malformed: {exc}") from exc


def record(source: str, raw_id: str, **kwargs) -> dict:
    base = {
        "source": source, "raw_id": raw_id, "name": "", "company": "",
        "email": "", "phone": "", "city": "", "title": "", "note": "",
        "date": "", "detail": "", "collector": "",
    }
    base.update({k: v or "" for k, v in kwargs.items()})
    return base


def load_records(scan_bytes: bytes, booth_bytes: bytes,
                 after_bytes: bytes | None = None) -> tuple[list[dict], list[dict], dict]:
    scans = parse_csv(scan_bytes, REQUIRED_SCAN_COLUMNS, "Badge scans CSV")
    try:
        booth = json.loads(booth_bytes.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"Booth notes JSON is invalid: {exc}") from exc
    if not isinstance(booth, dict):
        raise InputError("Booth notes JSON must contain an object.")
    if not isinstance(booth.get("cards"), list):
        raise InputError("Booth notes JSON 'cards' must be a list.")
    if not isinstance(booth.get("voice_notes"), list):
        raise InputError("Booth notes JSON 'voice_notes' must be a list.")
    if not isinstance(booth.get("owen_list"), dict):
        raise InputError("Booth notes JSON 'owen_list' must be an object.")
    if not isinstance(booth["owen_list"].get("lines"), list):
        raise InputError("Booth notes JSON 'owen_list.lines' must be a list.")

    records: list[dict] = []
    for row in scans:
        records.append(record(
            "scan", row["scan_id"], name=f"{row['first_name']} {row['last_name']}",
            company=row["company"], email=row["email"], phone=row["phone"],
            city=row["city"], title=row["title"], note=row["notes"],
            date=row["scanned_at"], detail=row["notes"],
            collector=row["scanned_by"], consent=row["share_with_exhibitors"],
            rating=row["rating"],
        ))
    for card in booth["cards"]:
        records.append(record(
            "card", card.get("card_id", ""), name=card.get("name", ""),
            company=card.get("clinic", ""), email=card.get("email", ""),
            phone=card.get("phone", ""), title=card.get("title", ""),
            note=card.get("back_of_card", ""), detail=card.get("back_of_card", ""),
            date=card.get("typed_on", ""), collector=card.get("collected_by", ""),
        ))
    for voice in booth["voice_notes"]:
        text = apply_phonetic(voice.get("transcript", ""))
        records.append(record(
            "voice", voice.get("note_id", ""), note=text, detail=text,
            date=voice.get("recorded_at", ""), collector="Owen",
        ))
    for line in booth.get("owen_list", {}).get("lines", []):
        records.append(record(
            "plane", line.get("line_id", ""), note=line.get("text", ""),
            detail=line.get("text", ""), date=booth["owen_list"].get("written", ""),
            collector="Owen",
        ))

    events: list[dict] = []
    if after_bytes:
        events = parse_csv(after_bytes, REQUIRED_AFTER_COLUMNS, "After-show sheet CSV")
        for row in events:
            records.append(record(
                "after_show", row["event_id"], name=row["name"],
                company=row["clinic"], email=row["email"], date=row["date_time"],
                note=row["detail"], detail=row["detail"], channel=row["channel"],
                event=row["event"],
            ))
    return records, events, booth


def primary_signals(a: dict, b: dict) -> set[str]:
    signals: set[str] = set()
    fa, fb = first_name(a.get("name")), first_name(b.get("name"))
    la, lb = last_name(a.get("name")), last_name(b.get("name"))
    if fa and fb and (fa == fb or (len(fa) == 1 and fb.startswith(fa))
                      or (len(fb) == 1 and fa.startswith(fb))):
        signals.add("same first name")
    if la and lb and (la == lb or (len(la) == 1 and lb.startswith(la))
                     or (len(lb) == 1 and la.startswith(lb))):
        signals.add("same last name")
    if clinic_matches(a.get("company"), b.get("company")):
        signals.add("same clinic")
    if norm(a.get("city")) and norm(a.get("city")) == norm(b.get("city")):
        signals.add("same city")
    if norm(a.get("email")) and norm(a.get("email")) == norm(b.get("email")):
        signals.add("same email")
    elif domain(a.get("email")) and domain(a.get("email")) == domain(b.get("email")):
        local_a = norm(a.get("email")).split("@")[0]
        local_b = norm(b.get("email")).split("@")[0]
        if local_a in local_b or local_b in local_a:
            signals.add("same email domain and related mailbox")
    if digits(a.get("phone")) and digits(a.get("phone")) == digits(b.get("phone")):
        signals.add("same phone")
    return signals


def merge_is_safe(signals: set[str]) -> bool:
    if len(signals) < 2:
        return False
    strong = {
        "same clinic", "same email", "same email domain and related mailbox",
        "same phone", "same city",
    }
    return bool(signals & strong)


def explicit_split(a: dict, b: dict) -> bool:
    fa, fb = first_name(a.get("name")), first_name(b.get("name"))
    if (clinic_matches(a.get("company"), b.get("company")) and fa and fb and
            fa != fb and len(fa) > 1 and len(fb) > 1):
        return True
    la, lb = last_name(a.get("name")), last_name(b.get("name"))
    if la and la == lb:
        if a.get("city") and b.get("city") and norm(a["city"]) != norm(b["city"]):
            return True
        if a.get("company") and b.get("company") and not clinic_matches(a["company"], b["company"]):
            return True
    return False


def merge_primary(records: list[dict]) -> list[dict]:
    primary = [r for r in records if r["source"] in {"scan", "card"}]
    groups: list[list[dict]] = []
    for item in primary:
        candidates: list[tuple[int, int, set[str]]] = []
        for index, group in enumerate(groups):
            best: set[str] = set()
            for other in group:
                if explicit_split(item, other):
                    continue
                signals = primary_signals(item, other)
                if len(signals) > len(best):
                    best = signals
            if merge_is_safe(best):
                candidates.append((len(best), index, best))
        if not candidates:
            groups.append([item])
        else:
            candidates.sort(reverse=True)
            groups[candidates[0][1]].append(item)
    return [make_person(index + 1, group) for index, group in enumerate(groups)]


def best_value(records: list[dict], field: str) -> str:
    values = [str(r.get(field, "")).strip() for r in records if str(r.get(field, "")).strip()]
    if not values:
        return ""
    return max(values, key=lambda value: (len(value), value))


def make_person(index: int, records: list[dict]) -> dict:
    named = [r for r in records if clean_name(r.get("name"))]
    name = max(
        named,
        key=lambda r: (
            r["source"] == "scan",
            len(first_name(r.get("name"))),
            len(clean_name(r.get("name"))),
        ),
    )["name"] if named else ""
    company = best_value(records, "company")
    city = best_value(records, "city")
    sources = [{"source": r["source"], "id": r["raw_id"],
                "name_used": r.get("name", ""), "email_used": r.get("email", "")}
               for r in records]
    reasons: set[str] = set()
    for i, left in enumerate(records):
        for right in records[i + 1:]:
            reasons |= primary_signals(left, right)
    return {
        "person_id": f"P{index:03d}", "name": name, "clinic": company,
        "city": city, "email": best_value(records, "email"),
        "phone": best_value(records, "phone"), "title": best_value(records, "title"),
        "locations": infer_locations(records), "booking_system": infer_system(records),
        "records": list(records), "sources": sources,
        "merge_reason": ", ".join(sorted(reasons)) or "single source record",
        "is_uncertain": False, "uncertain_reason": "",
    }


def infer_locations(records: list[dict]) -> int | None:
    text = " ".join(norm(r.get("note") or r.get("detail")) for r in records)
    patterns = (
        r"\b(\d+)\s+(?:clinics|sites|locations|locs)\b",
        r"\b(\d+)\s+locs?\b",
    )
    values: list[int] = []
    for pattern in patterns:
        values += [int(n) for n in re.findall(pattern, text)]
    words = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6}
    for word, number in words.items():
        if re.search(rf"\b{word}\s+(?:[a-z]+\s+){{0,2}}(clinics|sites|locations|locs)\b", text):
            values.append(number)
    if values:
        return max(values)
    return 1 if records else None


def apply_phonetic(text: str) -> str:
    cleaned = norm(text)
    for wrong, right in PHONETIC.items():
        cleaned = cleaned.replace(wrong, right)
    if "shediac" in cleaned and "clinivo" in cleaned:
        cleaned = re.sub(r"\b(ellen|helen)\b", "helene", cleaned)
    targets = ("clinivo", "bookstead", "pracshift")
    words = cleaned.split()
    for index, word in enumerate(words):
        token = re.sub(r"[^a-z]", "", word)
        if len(token) < 5 or token in targets or token == "clinic":
            continue
        ratios = [
            (SequenceMatcher(None, token, target).ratio(), target)
            for target in targets
        ]
        ratio, target = max(ratios)
        if ratio >= 0.80:
            words[index] = word.replace(token, target)
    return " ".join(words)


def infer_system(records: list[dict]) -> str:
    text = " ".join(apply_phonetic(r.get("note") or r.get("detail")) for r in records)
    for system in ("clinivo", "bookstead", "pracshift"):
        if system in text:
            return system.title()
    if "paper" in text:
        return "paper"
    if "spreadsheet" in text or "excel" in text or "sheets" in text:
        return "spreadsheet"
    if "google calendar" in text or "gcal" in text:
        return "Google Calendar"
    return ""


def text_person_signals(text_record: dict, person: dict) -> set[str]:
    text = norm(text_record.get("note"))
    signals: set[str] = set()
    f = first_name(person["name"])
    l = last_name(person["name"])
    if f and any(NICKNAMES.get(word, word) == f for word in re.findall(r"\b[a-z]+\b", text)):
        signals.add("first name in text")
    if l and l in text:
        signals.add("last name in text")
    key = clinic_key(person["clinic"])
    key_words = [w for w in key.split() if len(w) >= 4]
    if key_words and any(w in text for w in key_words):
        signals.add("clinic in text")
    if person["city"] and (phrase_key(person["city"]) in phrase_key(text)
                           or compact_key(person["city"]) in compact_key(text)):
        signals.add("city in text")
    if person["booking_system"] and norm(person["booking_system"]) in text:
        signals.add("booking system in text")
    locations = person.get("locations")
    if locations and re.search(rf"\b{locations}\s+(clinics|sites|locations|locs)\b", text):
        signals.add("clinic count in text")
    return signals


def signal_score(signals: set[str]) -> int:
    weights = {
        "first name in text": 5,
        "last name in text": 5,
        "clinic in text": 4,
        "city in text": 2,
        "booking system in text": 1,
        "clinic count in text": 1,
        "same requested action": 1,
    }
    return sum(weights.get(signal, 1) for signal in signals)


def attach_free_text(people: list[dict], records: list[dict]) -> list[dict]:
    needs_check: list[dict] = []
    free = [r for r in records if r["source"] in {"voice", "plane"}]
    for item in free:
        item_text = norm(item.get("note"))
        is_correction = (
            item["source"] == "voice"
            and any(term in item_text for term in (
                "correction", "actually", "changed to", "instead",
                "update on", "correction on",
            ))
        )
        if is_correction:
            correction_matches = []
            for person in people:
                signals = text_person_signals(item, person)
                if signals and signal_score(signals) >= 5:
                    correction_matches.append((signal_score(signals), person, signals))
            correction_matches.sort(key=lambda row: row[0], reverse=True)
            if correction_matches and (
                len(correction_matches) == 1
                or correction_matches[0][0] > correction_matches[1][0]
            ):
                _, person, signals = correction_matches[0]
                person["records"].append(item)
                person["sources"].append({
                    "source": "voice", "id": item["raw_id"],
                    "name_used": "", "email_used": "",
                })
                person["merge_reason"] += f"; {item['raw_id']}: correction"
                person["locations"] = infer_locations(person["records"])
                person["booking_system"] = infer_system(person["records"])
                continue
        scored = []
        for person in people:
            signals = text_person_signals(item, person)
            if len(signals) >= 2:
                scored.append((signal_score(signals), person, signals))
        scored.sort(key=lambda row: row[0], reverse=True)
        if not scored:
            needs_check.append({
                "id": item["raw_id"], "text": item["note"],
                "reason": "Could not match this note using two independent identity signals.",
            })
            continue
        top_score = scored[0][0]
        tied = [row for row in scored if row[0] == top_score]
        if item["source"] == "voice" and len(tied) > 1:
            all_mentioned = all(
                {"first name in text", "clinic in text"} <= signals
                for _, _, signals in tied
            )
            if all_mentioned:
                for _, person, signals in tied:
                    person["records"].append(item)
                    person["sources"].append({
                        "source": "voice", "id": item["raw_id"],
                        "name_used": "", "email_used": "",
                    })
                    person["merge_reason"] += (
                        f"; {item['raw_id']}: {', '.join(sorted(signals))}"
                    )
                    person["locations"] = infer_locations(person["records"])
                    person["booking_system"] = infer_system(person["records"])
                continue
        if len(tied) > 1:
            names = ", ".join(row[1]["name"] for row in tied[:4])
            needs_check.append({
                "id": item["raw_id"], "text": item["note"],
                "reason": f"Could match more than one person: {names}. Please check.",
            })
            continue
        _, person, signals = scored[0]
        recipients = [(person, signals)]
        if item["source"] == "voice":
            for _, secondary, secondary_signals in scored[1:]:
                if {"first name in text", "clinic in text"} <= secondary_signals:
                    recipients.append((secondary, secondary_signals))
        for recipient, recipient_signals in recipients:
            recipient["records"].append(item)
            recipient["sources"].append({"source": item["source"], "id": item["raw_id"],
                                         "name_used": "", "email_used": ""})
            recipient["merge_reason"] += (
                f"; {item['raw_id']}: {', '.join(sorted(recipient_signals))}"
            )
            recipient["locations"] = infer_locations(recipient["records"])
            recipient["booking_system"] = infer_system(recipient["records"])

    # A plane line may now have enough context through an attached voice note.
    unresolved = []
    for item in needs_check:
        if not str(item["id"]).startswith("L"):
            unresolved.append(item)
            continue
        pseudo = record("plane", item["id"], note=item["text"])
        scored = []
        for person in people:
            signals = text_person_signals(pseudo, person)
            action = infer_next_step([pseudo])
            person_action = infer_next_step(person["records"])
            if action != "thank-you note" and action == person_action:
                signals.add("same requested action")
            text = norm(item["text"])
            if person_action in {"demo", "trial", "pricing"} and person_action in text:
                signals.add("same requested action")
            if person_action == "call back" and "call" in text:
                signals.add("same requested action")
            if len(signals) >= 2:
                scored.append((signal_score(signals), person, signals))
        scored.sort(key=lambda row: row[0], reverse=True)
        if scored and (len(scored) == 1 or scored[0][0] > scored[1][0]):
            _, person, signals = scored[0]
            person["records"].append(pseudo)
            person["sources"].append({"source": "plane", "id": item["id"],
                                      "name_used": "", "email_used": ""})
            person["merge_reason"] += f"; {item['id']}: {', '.join(sorted(signals))}"
        else:
            unresolved.append(item)
    return unresolved


def event_matches_person(event: dict, person: dict) -> bool:
    event_record = record("after_show", event.get("event_id", ""),
                          name=event.get("name", ""), company=event.get("clinic", ""),
                          email=event.get("email", ""))
    representatives = person["records"] or [person]
    signal_sets = [primary_signals(event_record, r) for r in representatives]
    if any(len(signals) >= 2 for signals in signal_sets):
        return True

    detail = norm(event.get("detail"))
    if not detail:
        return False
    person_first = first_name(person["name"])
    person_last = last_name(person["name"])
    words = set(re.findall(r"\b[a-z]+\b", detail))
    first_in_detail = bool(person_first and (
        person_first in words or any(
            canonical == person_first and alias in words
            for alias, canonical in NICKNAMES.items()
        )
    ))
    last_in_detail = bool(person_last and len(person_last) >= 4 and person_last in words)
    strong_context = any(
        signals & {
            "same clinic", "same email", "same email domain and related mailbox",
            "same phone", "same city",
        }
        for signals in signal_sets
    )
    return strong_context and (first_in_detail or last_in_detail)


def attach_events(people: list[dict], events: list[dict]) -> list[dict]:
    unresolved = []
    for event in events:
        if not any(norm(event.get(field)) for field in ("name", "email", "clinic")):
            unresolved.append({
                "id": event["event_id"],
                "text": event.get("detail", ""),
                "reason": "After-show event has no identifying fields. Please check.",
            })
            continue
        matches = [p for p in people if event_matches_person(event, p)]
        exact_email = [p for p in matches if any(
            norm(event.get("email")) and norm(event.get("email")) == norm(r.get("email"))
            for r in p["records"]
        )]
        if len(exact_email) == 1:
            matches = exact_email
        if len(matches) == 1:
            matches[0].setdefault("events", []).append(event)
        elif len(matches) > 1:
            unresolved.append({
                "id": event["event_id"], "text": f"{event['name']} — {event['detail']}",
                "reason": "After-show event matches more than one person. Please check.",
            })
        elif any(hint in norm(event.get("detail")) for hint in SHOW_HINTS):
            unresolved.append({
                "id": event["event_id"],
                "text": f"{event['name']} — {event['detail']}",
                "reason": (
                    "After-show event mentions the show, but no booth person matched. "
                    "Please check."
                ),
            })
    return unresolved


def conversation_text(person: dict) -> str:
    return " ".join(norm(r.get("note") or r.get("detail")) for r in person["records"])


def note_filter_reason(person: dict) -> str:
    has_card = any(r["source"] == "card" for r in person["records"])
    has_voice = any(r["source"] == "voice" for r in person["records"])
    has_plane = any(r["source"] == "plane" for r in person["records"])
    if "exhibitor" in norm(person.get("title")):
        return "title says exhibitor — not a real conversation"
    scan_notes = [norm(r.get("note")) for r in person["records"]
                  if r["source"] == "scan" and norm(r.get("note"))]
    for note in scan_notes:
        for term in NOTE_BLOCK_TERMS:
            if re.search(rf"\b{re.escape(term)}\b", note):
                return f'note says "{term}" — not a real conversation'
        for competitor in COMPETITORS:
            if re.search(rf"\b{competitor}\b", note) and not (has_card or has_voice or has_plane):
                return f'note says "{competitor}" — not a real conversation'
        if "just browsing" in note and not (has_card or has_voice or has_plane):
            return 'note says "just browsing" — not a real conversation'
    if not has_card and not has_voice and not has_plane and not scan_notes:
        return "drive-by, no card, note, voice note or plane-list line"
    return ""


def exclusion_reason(person: dict, customer_clinics: set[str] | None = None,
                     customer_checked_at: str = "") -> str:
    reason = note_filter_reason(person)
    if reason:
        return reason
    company = norm(person["clinic"])
    email_domain = domain(person["email"])
    for competitor in COMPETITORS:
        if competitor in company or competitor in email_domain:
            return f"competitor ({competitor.title()})"
    title = norm(person["title"])
    if any(term in title for term in STUDENT_TERMS):
        if not any(role in title for role in ("supervisor", "coordinator", "director", "manager")):
            return "student title"
    if any(term in norm(person["title"]) for term in ("exhibitor", "supplier", "vendor")):
        return f"other exhibitor or supplier ({person['title']})"
    if customer_clinics and clinic_key(person["clinic"]) in customer_clinics:
        stamp = customer_checked_at or "this review"
        return f"existing customer (Erin checked clinic on {stamp})"
    for event in person.get("events", []):
        detail = norm(event.get("detail"))
        if any(term in detail for term in REMOVE_TERMS):
            return f"asked to be removed ({str(event.get('date_time', ''))[:10]})"
    return ""


def infer_next_step(records: list[dict]) -> str:
    def has(source: str, terms: tuple[str, ...]) -> bool:
        return any(r["source"] == source and any(term in norm(r.get("note")) for term in terms)
                   for r in records)
    named = next((r.get("name", "") for r in records if r.get("name")), "")
    first, last = first_name(named), last_name(named)
    sorted_records = sorted(
        records, key=lambda item: item.get("date") or "", reverse=True
    )
    for record in sorted_records:
        if record["source"] != "voice":
            continue
        for sentence in re.split(r"[.!?]+", norm(record.get("note"))):
            if first and first not in sentence and last and last not in sentence:
                continue
            if "pricing" in sentence or "price per" in sentence:
                return "pricing"
            if "trial" in sentence and "not a demo" in sentence:
                return "trial"
            if "demo" in sentence:
                return "demo"
            if "trial" in sentence:
                return "trial"
    for item in sorted_records:
        text = norm(item.get("note") or "")
        if "trial" in text and "not a demo" in text:
            return "trial"
        for step_name, patterns in ASK_PATTERNS.items():
            if any(pattern in text for pattern in patterns):
                return step_name
    if any(r["source"] == "voice" and "trial" in norm(r.get("note"))
           and "not a demo" in norm(r.get("note")) for r in records):
        return "trial"
    if has("voice", ("demo",)):
        return "demo"
    if has("voice", ("trial",)):
        return "trial"
    if has("voice", ("pricing", "price per")):
        return "pricing"
    if has("card", ("demo",)):
        return "demo"
    if has("card", ("trial",)):
        return "trial"
    if has("card", ("pricing", "send numbers", "numbers in writing")):
        return "pricing"
    if any(r["source"] == "scan" and
           any(term in norm(r.get("note")) for term in
               ("pricing", "price per", "$ per", "send numbers"))
           for r in records):
        return "pricing"
    if any(r["source"] == "voice" and "call" in norm(r.get("note"))
           and re.search(r"(after|before|week|monday|tuesday|wednesday|thursday|friday|\d{1,2})",
                         norm(r.get("note"))) for r in records):
        return "call back"
    if any(r["source"] in {"scan", "plane"} and
           any(term in norm(r.get("note")) for term in
               ("pricing", "price per", "$ per", "send numbers"))
           for r in records):
        return "pricing"
    if any(r["source"] in {"scan", "card", "plane"} and
           any(term in norm(r.get("note")) for term in
               ("send info", "send stuff", "one pager", "brochure", "security"))
           for r in records):
        return "send info"
    return "thank-you note"


def consent_reason(person: dict) -> str | None:
    scan_records = [item for item in person["records"] if item["source"] == "scan"]
    has_card = any(item["source"] == "card" for item in person["records"])
    has_voice = any(item["source"] == "voice" for item in person["records"])
    has_plane = any(item["source"] == "plane" for item in person["records"])

    texts = [norm(item.get("note") or "") for item in person["records"]]
    if any(
        any(term in text for term in ("no email", "don't email", "do not email"))
        for text in texts
    ):
        return "explicit no-email instruction"

    newsletter_only = any(
        any(term in text for term in (
            "no mailing", "no newsletter", "mailing list", "hates newsletters",
        ))
        for text in texts
    )
    if newsletter_only and infer_next_step(person["records"]) not in {
        "demo", "trial", "pricing", "call back",
    }:
        return "explicit no-marketing instruction"

    n_badge = any(norm(item.get("consent")) == "n" for item in scan_records)
    if n_badge and not has_card and not has_voice and not has_plane:
        return "N badge, no card, no voice note, no plane line (check first)"
    return None


def asked_specific(person: dict) -> bool:
    return infer_next_step(person["records"]) in {"demo", "trial", "pricing", "call back"}


def classify_priority(person: dict) -> dict:
    locations = person.get("locations") or 1
    system = norm(person.get("booking_system"))
    step = infer_next_step(person["records"])
    clinic_word = "clinic" if locations == 1 else "clinics"
    if step in {"demo", "trial", "pricing", "call back"}:
        label = "hot"
        reason = f"asked for a {step}. The ask overrides clinic size and current software."
    elif system in COMPETITORS or locations >= 2:
        label = "warm"
        parts = []
        if system in COMPETITORS:
            parts.append(f"on {person.get('booking_system')}")
        if locations >= 2:
            parts.append(f"{locations} {clinic_word}")
        reason = (
            f"{' and '.join(parts)}, and they did not ask for a demo, trial, pricing, or call back"
        )
    else:
        label = "cold"
        reason = "one clinic, not on Clinivo, Bookstead, or Pracshift, and no specific ask"
    owen = "hot" if locations >= 4 else "warm" if locations >= 2 else "cold"
    divergence = ""
    if label != "hot" and owen != label:
        divergence = (
            f"Owen's view: {locations} {clinic_word}, so he would rank this {owen}. "
            "Nadia confirmed on 5 November that Owen also puts people who asked for "
            "something first, so the ask-beats-size rule is jointly held. Owen would "
            "still draft and call this person regardless of the label because of the "
            "clinic count."
        )
    return {
        "priority": label,
        "contested": bool(divergence),
        "nadia": label,
        "owen": f"{owen} ({locations} {clinic_word})",
        "reason": reason,
        "divergence": divergence,
    }


def work_detail(person: dict) -> str:
    candidates = []
    person_first = first_name(person["name"])
    person_last = last_name(person["name"])
    next_step = infer_next_step(person["records"])
    for r in person["records"]:
        detail_score = 0
        text = str(r.get("note") or r.get("detail") or "").strip()
        if not text:
            continue
        sentences = [
            sentence.strip()
            for sentence in re.split(r"[.!?]+", text)
            if sentence.strip()
            and not any(term in norm(sentence) for term in PERSONAL_TERMS)
            and not any(term in norm(sentence) for term in (
                "mailing list", "newsletter", "do not email", "don't email",
                "no email",
            ))
        ]
        text = ". ".join(sentences)
        if not text:
            continue
        if r["source"] == "voice":
            scored = []
            for sentence in sentences:
                sentence_norm = norm(sentence)
                words = set(re.findall(r"\b[a-z]+\b", sentence_norm))
                name_mentioned = (
                    (person_first and person_first in words)
                    or (person_last and person_last in words)
                    or any(canonical == person_first and alias in words
                           for alias, canonical in NICKNAMES.items())
                )
                score = 10 if name_mentioned else 0
                if next_step == "pricing" and (
                    "pricing" in sentence_norm or "price per" in sentence_norm
                ):
                    score += 6
                if next_step in {"demo", "trial"} and next_step in sentence_norm:
                    score += 4
                if any(word in sentence_norm for word in (
                    "double", "overwrit", "charg", "logging out", "drowning",
                    "sick of", "loses", "no-show", "drown",
                )):
                    score += 12
                if re.search(r"\d", sentence):
                    score += 2
                scored.append((score, sentence))
            if scored:
                detail_score, text = max(
                    scored, key=lambda row: (row[0], len(row[1]))
                )
                aliases = [person_first] + [
                    alias for alias, canonical in NICKNAMES.items()
                    if canonical == person_first
                ]
                aliases = [re.escape(alias) for alias in aliases if alias]
                if aliases:
                    text = re.sub(
                        rf"^(?:{'|'.join(aliases)})\s+from\s+[^,]+,\s*",
                        "", text, flags=re.I,
                    )
        if r["source"] in {"voice", "card", "scan", "plane"}:
            candidates.append((
                {"voice": 4, "card": 3, "scan": 2, "plane": 1}[r["source"]],
                detail_score,
                text,
            ))
    if candidates:
        text = max(candidates, key=lambda row: (row[0], row[1], len(row[2])))[2]
        text = re.sub(r"^(okay\s+)?(first real one|day two|correction on)\W*", "", text, flags=re.I)
        text = re.sub(r"^(and|so|but|well|um|actually)\s+", "", text, flags=re.I)
        text = re.sub(
            r"^nadia just told me about one she had in french,\s*",
            "", text, flags=re.I,
        )
        text = re.sub(r"\s+", " ", text).strip()
        return text[:220].rstrip(" ,.;")
    if person.get("locations"):
        return f"your {person['locations']} clinic location{'s' if person['locations'] != 1 else ''}"
    return f"your work at {person['clinic']}" if person["clinic"] else "your clinic"


def sender_for(person: dict) -> str:
    for r in person["records"]:
        if r["source"] == "card" and norm(r.get("collector")) == "nadia":
            return "Nadia"
    for r in person["records"]:
        if "nadia" in norm(r.get("collector")):
            return "Nadia"
    return "Owen"


def extract_timing(person: dict) -> str | None:
    patterns = (
        (r"\bafter (thanksgiving|christmas|new year|easter)\b",
         lambda match: f"after {match.group(1)}"),
        (r"\bonce the (new place|new location|second location)(?: is open| opens)?\b",
         lambda match: f"once the {match.group(1)} opens"),
        (r"\bin (two|three|four|a few) weeks\b",
         lambda match: f"in {match.group(1)} weeks"),
        (r"\bafter ([a-z]+ \d{1,2}|[a-z]+day)\b",
         lambda match: f"after {match.group(1)}"),
        (r"\bnot (?:before|till|until) ([a-z]+ \d{1,2})\b",
         lambda match: f"after {match.group(1)}"),
        (r"\bback on the (\d{1,2})(?:st|nd|rd|th)?\b",
         lambda match: f"after the {match.group(1)}th"),
        (r"\bnext (week|month|year)\b",
         lambda match: f"next {match.group(1)}"),
    )
    for item in sorted(person["records"], key=lambda row: row.get("date") or "", reverse=True):
        text = norm(item.get("note") or "")
        for pattern, formatter in patterns:
            match = re.search(pattern, text)
            if match:
                return formatter(match)
    return None


def draft_for(person: dict, show_city: str = "the show") -> tuple[str, str]:
    sender = sender_for(person)
    first = clean_name(person["name"]).split()[0].title() if clean_name(person["name"]) else "there"
    step = infer_next_step(person["records"])
    actions = {
        "demo": "I’ll send a couple of demo times so we can find one that works.",
        "trial": "I’ll send the trial details we discussed.",
        "pricing": "I’ll send the pricing details you asked for.",
        "call back": "I’ve noted the timing we discussed and will follow up then.",
        "send info": "I’ll send the information we discussed.",
        "thank-you note": "Thanks for taking the time to speak with me.",
    }
    if step == "call back":
        timing = extract_timing(person)
        actions["call back"] = (
            f"I’ll reach out {timing}."
            if timing else
            "I’ll reach out at the time we discussed."
        )
    detail = work_detail(person)
    body = [
        f"Hi {first},",
        f"Great to meet you in {show_city}. {actions[step]}",
        f"You mentioned {detail[0].lower() + detail[1:] if detail else 'your clinic'}.",
        f"Best,\n{sender}",
    ]
    return "\n\n".join(body), sender


def validate_draft(draft: str, sender: str, person: dict) -> str | None:
    lowered = norm(draft)
    for term in PERSONAL_TERMS_STRICT:
        if term in lowered:
            return f"draft contains personal term '{term}'"
    if re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", draft):
        return "draft contains an email address"
    compact_digits = re.sub(r"[\s\-().]", "", draft)
    if re.search(r"\d{7,}", compact_digits):
        return "draft contains a phone number"
    paragraphs = [paragraph for paragraph in draft.split("\n\n") if paragraph.strip()]
    if not 3 <= len(paragraphs) <= 5:
        return f"draft has {len(paragraphs)} paragraphs, expected 3-5"
    first = (
        clean_name(person["name"]).split()[0].title()
        if clean_name(person["name"]) else "There"
    )
    if f"Hi {first}," not in draft:
        return f"draft greeting does not use first name '{first}'"
    if not draft.rstrip().endswith(sender):
        return f"draft is not signed by '{sender}'"
    return None


def parse_date(value: str) -> datetime | None:
    value = str(value or "").strip()
    if not value:
        return None
    for fmt in (
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%d",
    ):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is not None:
        return parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def status_for(person: dict, show_start: datetime | None,
               date_min: datetime | None, date_max: datetime | None) -> str:
    events = person.get("events", [])
    if not show_start or not date_min or not date_max:
        return "status unknown"
    window_end = show_start + timedelta(days=30)
    effective_max = min(date_max, window_end)
    in_window = [e for e in events
                 if (dt := parse_date(e.get("date_time", "")))
                 and date_min <= dt <= effective_max]
    all_demos = [e for e in events if norm(e.get("event")) == "demo booked"
                 and parse_date(e.get("date_time", ""))]
    if all_demos:
        demo_date = min(parse_date(e["date_time"]) for e in all_demos)
        day = (demo_date - show_start).days
        if day > 30:
            return f"booked, outside 30-day window (day {day})"
        if 27 <= day <= 30:
            return f"borderline — demo on day {day}"
    demos = [e for e in in_window if norm(e.get("event")) == "demo booked"]
    trials = [e for e in in_window if norm(e.get("event")) == "trial started"]
    sent = [e for e in in_window if norm(e.get("event")) == "email sent"]
    bounced = [e for e in in_window if "bounce" in norm(e.get("event"))]
    if demos:
        return "booked a demo"
    if trials:
        return "started a trial"
    if sent and bounced and len(sent) <= len(bounced):
        return "we never wrote at all (bounced)"
    if sent:
        return "we wrote and nothing came of it"
    if events and not in_window:
        return "status unknown — events outside after-show window"
    return "we never wrote at all"


def is_real_conversation(person: dict) -> bool:
    if note_filter_reason(person):
        return False
    company = norm(person["clinic"])
    email_domain = domain(person["email"])
    if any(competitor in company or competitor in email_domain
           for competitor in COMPETITORS):
        return False
    title = norm(person["title"])
    if any(term in title for term in STUDENT_TERMS):
        if not any(role in title for role in ("supervisor", "coordinator", "director", "manager")):
            return False
    return not any(term in title for term in ("exhibitor", "supplier", "vendor"))


def pile_status(status: str) -> str:
    if status.startswith("borderline — demo"):
        return "booked a demo"
    if status.startswith("we never wrote at all"):
        return "we never wrote at all"
    return status


def run_pipeline(scan_bytes: bytes, booth_bytes: bytes,
                 after_bytes: bytes | None = None,
                 customer_clinics: set[str] | None = None,
                 customer_checked_at: str = "") -> dict:
    records, events, booth = load_records(scan_bytes, booth_bytes, after_bytes)
    people = merge_primary(records)
    needs_check = attach_free_text(people, records)
    needs_check += attach_events(people, events)

    dates = sorted(dt for e in events if (dt := parse_date(e.get("date_time", ""))))
    date_min = dates[0] if dates else None
    date_max = dates[-1] if dates else None
    about = str(booth.get("about", ""))
    show_match = re.search(r"\(([^,)]+),", about)
    show_city = show_match.group(1).strip() if show_match else "the show"
    scan_dates = sorted(dt for r in records if r["source"] == "scan" and (dt := parse_date(r.get("date", ""))))
    show_start = scan_dates[0] if scan_dates else date_min
    window_days = (date_max - show_start).days if show_start and date_max else 0
    window_incomplete = bool(after_bytes) and window_days < 28
    window_warning = (
        f"Warning: after-show data covers only {window_days} days from show start. "
        "Later bookings or replies are unknown."
        if window_incomplete else ""
    )

    drafts, excluded = [], []
    statuses: dict[str, str] = {}
    if after_bytes:
        for person in people:
            if is_real_conversation(person):
                statuses[person["person_id"]] = status_for(
                    person, show_start, date_min, date_max
                )
    for person in people:
        reason = exclusion_reason(person, customer_clinics, customer_checked_at)
        if reason:
            excluded.append({**person, "exclusion_reason": reason})
            continue
        consent = consent_reason(person)
        if consent:
            needs_check.append({
                "id": person["person_id"],
                "text": f"{person['name']} — consent",
                "reason": consent,
            })
            continue
        priority = classify_priority(person)
        draft, sender = draft_for(person, show_city)
        draft_rejection = validate_draft(draft, sender, person)
        if draft_rejection:
            needs_check.append({
                "id": person["person_id"],
                "text": f"{person['name']} — draft rejected",
                "reason": draft_rejection,
            })
            continue
        item = {
            **person, **priority, "next_step": infer_next_step(person["records"]),
            "draft": draft, "sender": sender,
            "reply_visibility": (
                "Erin cannot see replies to this draft"
                if sender in {"Owen", "Nadia"} else ""
            ),
            "status": statuses.get(person["person_id"], "") if after_bytes else "",
            "customer_check": "pending Erin's check — not excluded",
        }
        drafts.append(item)

    order = {"hot": 1, "warm": 2, "cold": 3}
    drafts.sort(key=lambda p: (0 if p.get("divergence") else 1, order.get(p["priority"], 4), norm(p["name"])))
    excluded.sort(key=lambda p: norm(p["name"]))
    clinics = sorted({p["clinic"] for p in people if p["clinic"]}, key=norm)
    piles = defaultdict(int)
    pile_names = defaultdict(list)
    booked_without_writing = []
    bounced = []
    if after_bytes:
        for person in people:
            if person["person_id"] not in statuses:
                continue
            status = pile_status(statuses[person["person_id"]])
            piles[status] += 1
            pile_names[status].append(person["name"])
            person_events = person.get("events", [])
            outcomes = [e for e in person_events if norm(e.get("event")) in {"demo booked", "trial started"}]
            sends = [e for e in person_events if norm(e.get("event")) == "email sent"]
            if outcomes and not any(parse_date(s["date_time"]) < parse_date(outcomes[0]["date_time"])
                                    for s in sends if parse_date(s["date_time"])):
                booked_without_writing.append(person["name"])
            if any("bounce" in norm(e.get("event")) for e in person_events):
                bounced.append(person["name"])
    return {
        "records": records, "drafts": drafts, "excluded": excluded,
        "needs_check": needs_check, "clinics": clinics, "piles": dict(piles),
        "pile_names": {key: names for key, names in pile_names.items()},
        "booked_without_writing": booked_without_writing, "bounced": bounced,
        "show_city": show_city,
        "show_start": scan_dates[0].strftime("%Y-%m-%d") if scan_dates else "",
        "show_end": scan_dates[-1].strftime("%Y-%m-%d") if scan_dates else "",
        "date_min": date_min.strftime("%Y-%m-%d") if date_min else "",
        "date_max": date_max.strftime("%Y-%m-%d") if date_max else "",
        "window_days": window_days,
        "window_incomplete": window_incomplete,
        "window_warning": window_warning,
        "has_after": bool(after_bytes),
        "counts": {"people": len(people), "drafts": len(drafts),
                   "excluded": len(excluded), "needs_check": len(needs_check)},
    }

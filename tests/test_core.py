import json
from pathlib import Path
from datetime import datetime

import pytest

from core import (
    InputError, apply_phonetic, clinic_key, consent_reason, exclusion_reason,
    extract_timing, first_name, infer_next_step, infer_system, merge_primary,
    norm, note_filter_reason, parse_csv, parse_date, record, run_pipeline,
    status_for, validate_draft,
)


ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def result():
    return run_pipeline(
        (ROOT / "badge-scans.csv").read_bytes(),
        (ROOT / "booth-notes.json").read_bytes(),
        (ROOT / "after-show-activity.csv").read_bytes(),
    )


def draft_person(result, name):
    return next(person for person in result["drafts"] if norm(name) in norm(person["name"]))


def excluded_person(result, name):
    return next(person for person in result["excluded"] if norm(name) in norm(person["name"]))


def test_required_column_error_is_clear():
    with pytest.raises(InputError, match="missing required column: company"):
        parse_csv(b"scan_id,first_name\nS1,Ada\n", {"scan_id", "company"}, "Badge scans CSV")


def test_malformed_csv_raises_input_error():
    bad = b'scan_id,scanned_at\n"unclosed quote\nS001,2026-09-14'
    with pytest.raises(InputError, match="Badge scans CSV is malformed"):
        parse_csv(bad, {"scan_id", "scanned_at"}, "Badge scans CSV")


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("cards", None, "'cards' must be a list"),
        ("voice_notes", None, "'voice_notes' must be a list"),
        ("owen_list", None, "'owen_list' must be an object"),
    ],
)
def test_null_booth_sections_raise_input_error(field, value, message):
    booth = {"cards": [], "voice_notes": [], "owen_list": {"lines": []}}
    booth[field] = value
    with pytest.raises(InputError, match=message):
        run_pipeline(
            (ROOT / "badge-scans.csv").read_bytes(),
            json.dumps(booth).encode(),
            (ROOT / "after-show-activity.csv").read_bytes(),
        )


def test_parse_iso8601_dates():
    expected = datetime(2026, 9, 21, 11, 2)
    assert parse_date("2026-09-21T11:02:00") == expected
    assert parse_date("2026-09-21T11:02:00Z") == expected
    assert parse_date("2026-09-21T08:02:00-03:00") == expected


def test_jennifer_macisaac_merges_seven_records_once(result):
    jen = draft_person(result, "Jennifer MacIsaac")
    assert {source["id"] for source in jen["sources"]} == {
        "S023", "S086", "C18", "V03", "V15", "L01", "L06",
    }
    assert sum("MacIsaac" in person["name"] and "Jennifer" in person["name"]
               for person in result["drafts"]) == 1


def test_v03_attaches_to_both_jen_and_ravi(result):
    jen = draft_person(result, "Jennifer MacIsaac")
    ravi = draft_person(result, "Ravi Sandhu")
    assert any(source["id"] == "V03" for source in jen["sources"])
    assert any(source["id"] == "V03" for source in ravi["sources"])


def test_lookalikes_stay_separate(result):
    names = {person["name"] for person in result["drafts"] + result["excluded"]}
    assert any("Ravi Sandhu" in name for name in names)
    assert any("Colin MacIsaac" in name for name in names)
    assert any("Nicole Arsenault" in name for name in names)
    assert any("Helene Arsenault" in name or "Hélène Arsenault" in name for name in names)


def test_same_name_without_strong_signal_does_not_merge():
    people = merge_primary([
        record("card", "C1", name="J. Smith", company=""),
        record("card", "C2", name="J. Smith", company="Harbour Physio"),
    ])
    assert len(people) == 2


def test_ambiguous_plane_line_needs_check(result):
    item = next(item for item in result["needs_check"] if item["id"] == "L11")
    assert "more than one person" in item["reason"]
    assert "Liam Dunphy" in item["reason"]


@pytest.mark.parametrize("name,reason_text", [
    ("Trevor Lindqvist", "comp"),
    ("Tomas Coady", "swag"),
    ("Morgan Bishop", "draw entry"),
    ("Darcy Young", "draw"),
    ("Tess Bishop", "exhibitor"),
    ("Monique Robichaud", "asked to be removed"),
    ("Kayla MacIsaac", "drive-by"),
])
def test_safety_gate_exclusions(result, name, reason_text):
    person = excluded_person(result, name)
    assert reason_text in person["exclusion_reason"].lower()
    assert not any(name in person["name"] for person in result["drafts"])


def test_card_only_people_are_included(result):
    assert draft_person(result, "Helene Arsenault")
    assert draft_person(result, "Farah Nazari")


def test_priority_cases(result):
    assert draft_person(result, "Jennifer MacIsaac")["priority"] == "hot"
    derek = draft_person(result, "Derek Osei")
    assert derek["priority"] == "warm"
    assert "6 clinics" in derek["divergence"]
    sophie = draft_person(result, "Sophie Tremblay")
    assert sophie["priority"] == "warm"
    assert sophie["divergence"]
    yvonne = draft_person(result, "Yvonne Clarke")
    assert yvonne["priority"] == "hot"
    assert yvonne["divergence"] == ""


@pytest.mark.parametrize("name,next_step", [
    ("Helene Arsenault", "call back"),
    ("Jennifer MacIsaac", "demo"),
    ("Gordon", "trial"),
    ("Ravi Sandhu", "pricing"),
    ("Raj Menon", "pricing"),
])
def test_next_steps(result, name, next_step):
    assert draft_person(result, name)["next_step"] == next_step


def test_consent_hierarchy_keeps_requested_follow_up_and_checks_bare_n(result):
    assert draft_person(result, "Amira Haddad")["next_step"] == "pricing"
    assert draft_person(result, "Natalie Chen")
    dara = next(item for item in result["needs_check"] if "Dara Thibodeau" in item["text"])
    assert "check first" in dara["reason"]


def test_correction_voice_note_overrides_earlier_ask():
    records = [
        record("card", "C1", note="Please book a demo", date="2026-09-14"),
        record(
            "voice", "V2",
            note="Correction: actually she wants a trial, not a demo",
            date="2026-09-15",
        ),
    ]
    assert infer_next_step(records) == "trial"


def test_consent_reason_allows_card_to_override_n_badge():
    person = {
        "records": [
            record("scan", "S1", consent="N"),
            record("card", "C1", note="send info"),
        ],
    }
    assert consent_reason(person) is None


def test_grace_draft_removes_personal_detail(result):
    draft = draft_person(result, "Grace Whitford")["draft"].lower()
    assert "father" not in draft
    assert "dad" not in draft
    assert "hospital" not in draft


def test_draft_validator_rejects_personal_details_and_contact_data():
    person = {"name": "Grace Whitford"}
    personal = "Hi Grace,\n\nYour father is in hospital.\n\nBest,\nOwen"
    email = "Hi Grace,\n\nWrite to hello@example.com.\n\nBest,\nOwen"
    assert "personal term" in validate_draft(personal, "Owen", person)
    assert "email" in validate_draft(email, "Owen", person)


def test_call_back_timing_is_used_in_draft(result):
    helene = draft_person(result, "Helene Arsenault")
    assert extract_timing(helene) == "after thanksgiving"
    assert "after thanksgiving" in helene["draft"].lower()


def test_shared_voice_note_uses_person_specific_detail(result):
    jen_draft = draft_person(result, "Jennifer MacIsaac")["draft"].lower()
    ravi_draft = draft_person(result, "Ravi Sandhu")["draft"].lower()
    assert "double" in jen_draft or "bookstead" in jen_draft
    assert "jen from bayview" not in jen_draft
    assert "pricing per practitioner" in ravi_draft
    assert "jen from bayview" not in ravi_draft


def test_divergence_reflects_november_correction(result):
    divergence = draft_person(result, "Derek Osei")["divergence"]
    assert "jointly held" in divergence
    assert "did not agree" not in divergence


def test_drafts_have_safe_sender_tone_and_length(result):
    for person in result["drafts"]:
        draft = person["draft"]
        nonempty_lines = [line for line in draft.splitlines() if line.strip()]
        assert person["sender"] in {"Owen", "Nadia"}
        assert "sandbar team" not in draft.lower()
        assert "dear valued" not in draft.lower()
        assert 4 <= len(nonempty_lines) <= 5


def test_after_show_range_and_piles_are_present(result):
    assert result["date_min"] == "2026-09-21"
    assert result["date_max"] == "2026-10-14"
    assert result["piles"]["booked a demo"] >= 1
    assert result["piles"]["we never wrote at all"] >= 1


def test_demo_bookings_match_booth_people_via_detail(result):
    assert draft_person(result, "Jennifer MacIsaac")["status"] == "booked a demo"
    assert draft_person(result, "Marisol Vega")["status"] == "booked a demo"


def test_unmatched_show_event_without_identity_needs_check():
    after = (ROOT / "after-show-activity.csv").read_bytes()
    after += (
        b'U999,2026-10-03 09:00,email sent,hello@ inbox,,,,'
        b'Allied Practice Expo lead\n'
    )
    result = run_pipeline(
        (ROOT / "badge-scans.csv").read_bytes(),
        (ROOT / "booth-notes.json").read_bytes(),
        after,
    )
    item = next(item for item in result["needs_check"] if item["id"] == "U999")
    assert "no identifying fields" in item["reason"].lower()


def test_demo_day_uses_show_start_and_enforces_window():
    person = {"events": [{
        "date_time": "2026-10-01 09:00",
        "event": "demo booked",
    }]}
    show_start = datetime(2026, 9, 1)
    date_min = datetime(2026, 9, 2)
    date_max = datetime(2026, 10, 5)
    assert status_for(person, show_start, date_min, date_max) == (
        "borderline — demo on day 30"
    )
    person["events"][0]["date_time"] = "2026-10-05 09:00"
    assert status_for(person, show_start, date_min, date_max) == (
        "booked, outside 30-day window (day 34)"
    )


def test_bounce_is_pile_four_and_excluded_real_people_still_count(result):
    assert "Vincent Roy" in result["pile_names"]["we never wrote at all"]
    assert "Vincent Roy" in result["bounced"]
    assert "Monique Robichaud" in result["pile_names"]["we wrote and nothing came of it"]
    assert not any("Monique Robichaud" in p["name"] for p in result["drafts"])


def test_no_after_show_skips_status():
    result = run_pipeline(
        (ROOT / "badge-scans.csv").read_bytes(),
        (ROOT / "booth-notes.json").read_bytes(),
    )
    assert result["has_after"] is False
    assert result["piles"] == {}
    assert result["drafts"]


def test_unseen_nickname_matches_formal_name():
    assert first_name("Jenny Cohen") == first_name("Jennifer Cohen")
    assert first_name("Liz Martin") == first_name("Elizabeth Martin")
    assert first_name("Liam Dunphy") == "liam"


def test_unseen_software_spelling_is_recognised():
    heard = record("voice", "V99", note="she is on booked stead and hates the reports")
    assert infer_system([heard]) == "Bookstead"
    assert "bookstead" in apply_phonetic("they use bookstedd")


def test_broader_safety_terms_and_supervisor_exception():
    coffee = {
        "records": [record("scan", "S1", note="came for the free coffee")],
        "title": "", "clinic": "Example Clinic", "email": "",
    }
    assert "free coffee" in note_filter_reason(coffee)

    student = {
        "records": [record("card", "C1", note="met at booth")],
        "title": "University Student", "clinic": "Example Clinic",
        "email": "", "events": [],
    }
    assert exclusion_reason(student) == "student title"

    director = {
        **student,
        "title": "Director of College Programs",
    }
    assert exclusion_reason(director) == ""


@pytest.mark.parametrize(("text", "step"), [
    ("Ring me next week", "call back"),
    ("Can we sit down with the team?", "demo"),
    ("Please share the pricing", "pricing"),
    ("Send the security sheet", "send info"),
])
def test_broader_ask_phrases(text, step):
    assert infer_next_step([record("card", "C1", note=text)]) == step


def test_shortened_after_show_sets_warning():
    short_after = (
        b"event_id,date_time,event,channel,name,email,clinic,detail\n"
        b"A001,2026-09-24 09:00,email sent,hello@,Test,"
        b"test@example.com,Example Clinic,hello\n"
    )
    result = run_pipeline(
        (ROOT / "badge-scans.csv").read_bytes(),
        (ROOT / "booth-notes.json").read_bytes(),
        short_after,
    )
    assert result["window_incomplete"] is True
    assert result["window_warning"]


def test_existing_customer_tick_excludes_whole_clinic():
    result = run_pipeline(
        (ROOT / "badge-scans.csv").read_bytes(),
        (ROOT / "booth-notes.json").read_bytes(),
        (ROOT / "after-show-activity.csv").read_bytes(),
        customer_clinics={clinic_key("Bayview Physio")},
        customer_checked_at="2026-11-05 09:00",
    )
    excluded = [p for p in result["excluded"] if "Bayview" in p["clinic"]]
    assert len(excluded) == 2
    assert all("2026-11-05" in p["exclusion_reason"] for p in excluded)

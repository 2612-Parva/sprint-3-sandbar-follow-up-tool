import json
import re
from datetime import datetime
from pathlib import Path

import pytest

from core import (
    InputError,
    apply_phonetic,
    consent_reason,
    exclusion_reason,
    extract_timing,
    infer_next_step,
    note_filter_reason,
    norm,
    parse_date,
    record,
    run_pipeline,
    status_for,
    validate_draft,
)


ROOT = Path(__file__).parents[1]


@pytest.fixture(scope="module")
def badge_bytes():
    return (ROOT / "badge-scans.csv").read_bytes()


@pytest.fixture(scope="module")
def booth_bytes():
    return (ROOT / "booth-notes.json").read_bytes()


@pytest.fixture(scope="module")
def after_bytes():
    return (ROOT / "after-show-activity.csv").read_bytes()


@pytest.fixture(scope="module")
def result(badge_bytes, booth_bytes, after_bytes):
    return run_pipeline(badge_bytes, booth_bytes, after_bytes)


def person(result, name):
    return next(
        item for item in result["drafts"] + result["excluded"]
        if norm(name) in norm(item["name"])
    )


def test_v03_attaches_to_both_jen_and_ravi(result):
    jen = person(result, "Jennifer MacIsaac")
    ravi = person(result, "Ravi Sandhu")
    assert any(source["id"] == "V03" for source in jen["sources"])
    assert any(source["id"] == "V03" for source in ravi["sources"])


def test_a056_matches_p13_via_detail(result):
    assert person(result, "Jennifer MacIsaac")["status"] == "booked a demo"


def test_a058_matches_p26_via_detail(result):
    assert person(result, "Marisol Vega")["status"] == "booked a demo"


def test_borderline_demo_on_day_30():
    booth_person = {
        "events": [{"date_time": "2026-10-01", "event": "demo booked"}],
    }
    assert status_for(
        booth_person,
        datetime(2026, 9, 1),
        datetime(2026, 9, 2),
        datetime(2026, 10, 1),
    ) == "borderline — demo on day 30"


def test_parse_iso8601_variants():
    assert parse_date("2026-09-21T11:02:00") is not None
    assert parse_date("2026-09-21T11:02:00Z") is not None
    assert parse_date("2026-09-21T11:02:00-03:00") is not None


def test_vincent_roy_in_pile_4_and_bounced(result):
    assert "Vincent Roy" in result["pile_names"]["we never wrote at all"]
    assert "Vincent Roy" in result["bounced"]


def test_monique_in_pile_3_and_excluded_from_drafts(result):
    assert "Monique Robichaud" in result["pile_names"]["we wrote and nothing came of it"]
    assert not any("Monique Robichaud" in item["name"] for item in result["drafts"])


def test_null_owen_list_raises_input_error(badge_bytes, after_bytes):
    bad = json.dumps({
        "cards": [], "voice_notes": [], "owen_list": None,
    }).encode()
    with pytest.raises(InputError):
        run_pipeline(badge_bytes, bad, after_bytes)


def test_malformed_csv_raises_input_error(booth_bytes, after_bytes):
    bad = b'scan_id,scanned_at\n"unclosed quote\nS001,2026-09-14'
    with pytest.raises(InputError):
        run_pipeline(bad, booth_bytes, after_bytes)


def test_fuzzy_bookstead_spelling():
    assert "bookstead" in apply_phonetic("they use bookstedd")


def test_free_coffee_note_is_not_a_real_conversation():
    booth_person = {
        "records": [record("scan", "S1", note="free coffee")],
        "title": "", "clinic": "Example Clinic", "email": "",
    }
    assert "free coffee" in note_filter_reason(booth_person)


def test_draft_rejects_personal_term():
    draft = "Hi Grace,\n\nYour father was in hospital.\n\nBest,\nOwen"
    reason = validate_draft(draft, "Owen", {"name": "Grace Whitford"})
    assert reason and "personal term" in reason


def test_draft_rejects_email():
    draft = "Hi Jen,\n\nWrite to hello@example.com.\n\nBest,\nOwen"
    reason = validate_draft(draft, "Owen", {"name": "Jen MacIsaac"})
    assert reason and "email" in reason


def test_grace_draft_uses_work_detail_not_father(result):
    draft = person(result, "Grace Whitford")["draft"].lower()
    assert "logging" in draft
    assert "father" not in draft
    assert "hospital" not in draft


def test_call_back_draft_includes_timing(result):
    helene = person(result, "Helene Arsenault")
    assert extract_timing(helene) == "after thanksgiving"
    assert "after thanksgiving" in helene["draft"].lower()


def test_shortened_after_show_shows_warning(badge_bytes, booth_bytes):
    short_after = (
        b"event_id,date_time,event,channel,name,email,clinic,detail\n"
        b"A001,2026-09-24 09:00,email sent,hello@,Test,"
        b"test@example.com,Example Clinic,hello\n"
    )
    short_result = run_pipeline(badge_bytes, booth_bytes, short_after)
    assert short_result["window_incomplete"] is True
    assert short_result["window_warning"]


def test_correction_overrides_earlier_ask():
    records = [
        record("card", "C1", note="book a demo", date="2026-09-14"),
        record(
            "voice", "V1",
            note="correction: actually trial, not a demo",
            date="2026-09-15",
        ),
    ]
    assert infer_next_step(records) == "trial"


def test_director_of_college_not_excluded():
    booth_person = {
        "name": "Test Director",
        "title": "Director of College Programs",
        "clinic": "Some Clinic",
        "email": "",
        "records": [record("card", "C1", note="met at booth")],
        "events": [],
    }
    assert exclusion_reason(booth_person) == ""


def test_amira_requested_pricing_is_kept(result):
    amira = person(result, "Amira Haddad")
    assert amira["next_step"] == "pricing"
    assert "newsletter" not in amira["draft"].lower()


def test_natalie_card_overrides_n_badge(result):
    assert person(result, "Natalie Chen") in result["drafts"]


def test_bare_n_badge_requires_check():
    booth_person = {
        "records": [record("scan", "S1", consent="N")],
    }
    assert "check first" in consent_reason(booth_person)


def test_exactly_four_day_30_piles(result):
    assert set(result["piles"]) == {
        "booked a demo",
        "started a trial",
        "we wrote and nothing came of it",
        "we never wrote at all",
    }


def test_safety_gate_names_have_no_draft(result):
    unsafe = {
        "Trevor Lindqvist", "Tomas Coady", "Morgan Bishop", "Darcy Young",
        "Tess Bishop", "Monique Robichaud", "Kayla MacIsaac",
    }
    draft_names = {item["name"] for item in result["drafts"]}
    assert not unsafe & draft_names


def test_no_draft_contains_personal_or_contact_data(result):
    forbidden = (
        "father", "dad", "hospital", "kids", "hockey", "dog photos",
        "pregnant", "surgery", "cancer", "concussion", "migraines",
    )
    for item in result["drafts"]:
        draft = item["draft"].lower()
        assert not any(term in draft for term in forbidden)
        assert not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", draft)
        assert not re.search(r"\d{7,}", re.sub(r"[\s\-().]", "", draft))


def test_show_and_after_window_are_reported(result):
    assert result["show_start"] == "2026-09-14"
    assert result["show_end"] == "2026-09-15"
    assert result["date_min"] == "2026-09-21"
    assert result["date_max"] == "2026-10-14"


def test_merge_reason_and_status_present_for_p13(result):
    p13 = person(result, "Jennifer MacIsaac")
    assert p13["merge_reason"]
    assert len(p13["sources"]) == 7
    assert p13["status"] == "booked a demo"


def test_clinic_tick_excludes_existing_customer(
    badge_bytes, booth_bytes, after_bytes,
):
    ticked = run_pipeline(
        badge_bytes,
        booth_bytes,
        after_bytes,
        customer_clinics={"bayview"},
        customer_checked_at="2026-11-06",
    )
    bayview = [
        item for item in ticked["excluded"]
        if "Bayview" in item["clinic"]
    ]
    assert {item["name"] for item in bayview} == {
        "Jennifer MacIsaac", "Ravi Sandhu",
    }
    assert all("existing customer" in item["exclusion_reason"] for item in bayview)


def test_new_competitor_and_student_terms_caught():
    competitor = {
        "name": "Test Competitor",
        "clinic": "Mindbody Clinic",
        "title": "Owner",
        "records": [record("card", "C1", note="met at booth")],
        "email": "",
        "events": [],
    }
    assert "competitor" in exclusion_reason(competitor).lower()

    student = {
        **competitor,
        "name": "Test Student",
        "clinic": "Some Clinic",
        "title": "Polytechnic Student",
    }
    assert "student" in exclusion_reason(student).lower()


@pytest.mark.parametrize(("text", "step"), [
    ("book a time with us", "demo"),
    ("send the deck", "send info"),
    ("quote us please", "pricing"),
    ("set up a pilot", "trial"),
    ("ring back tomorrow", "call back"),
])
def test_v4_ask_phrasing_recognised(text, step):
    assert infer_next_step([record("card", "C1", note=text)]) == step


def test_reply_visibility_on_nadia_draft(result):
    helene = person(result, "Helene Arsenault")
    assert helene["sender"] == "Nadia"
    assert helene["reply_visibility"] == "Erin cannot see replies to this draft"


def test_shared_voice_details_do_not_start_with_transcript_connectives(result):
    ravi_detail = person(result, "Ravi Sandhu")["draft"].lower()
    helene_detail = person(result, "Helene Arsenault")["draft"].lower()
    assert "you mentioned and " not in ravi_detail
    assert "nadia just told me" not in helene_detail

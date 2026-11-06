import io
import re
from pathlib import Path

import app as app_module
from app import app


ROOT = Path(__file__).parents[1]


def test_upload_page_and_full_run():
    client = app.test_client()
    page = client.get("/")
    assert page.status_code == 200
    assert b"v5-2026-11-06" in page.data
    assert b"Nothing is sent" in page.data
    assert b"After-show sheet CSV" in page.data
    assert b"Recount CSV" not in page.data
    assert b"Interview transcript" not in page.data

    response = client.post("/run", data={
        "badge_scans": (io.BytesIO((ROOT / "badge-scans.csv").read_bytes()), "badge-scans.csv"),
        "booth_notes": (io.BytesIO((ROOT / "booth-notes.json").read_bytes()), "booth-notes.json"),
        "after_show": (
            io.BytesIO((ROOT / "after-show-activity.csv").read_bytes()),
            "after-show-activity.csv",
        ),
    }, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Show follow-up review" in response.data
    assert b"Build v5-2026-11-06" in response.data
    assert b"Jennifer MacIsaac" in response.data
    assert b"Clinics to check" in response.data
    assert b"People</span>" in response.data
    assert b"Merged from 7 records" in response.data
    assert b"Day-30:</strong> booked a demo" in response.data
    assert response.data.count(b"Jennifer MacIsaac") >= 1
    assert b"Erin cannot see replies to this draft" in response.data
    assert b"2026-09-21" in response.data
    assert b"2026-10-14" in response.data
    assert b"Booked a demo" in response.data or b"booked a demo" in response.data


def test_missing_required_file_stops_with_clear_error():
    client = app.test_client()
    response = client.post("/run", data={}, content_type="multipart/form-data")
    assert response.status_code == 400
    assert b"Please upload badge scans." in response.data


def test_health_identifies_loaded_v5_build():
    response = app.test_client().get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["build_version"] == "v5-2026-11-06"
    assert payload["divergence_text_current"] is True
    assert payload["competitors_count"] == 11
    assert payload["student_terms_count"] == 11
    assert payload["ask_categories"] == [
        "demo", "pricing", "trial", "call back", "send info",
    ]


def test_short_after_show_warning_renders():
    client = app.test_client()
    short_after = (
        b"event_id,date_time,event,channel,name,email,clinic,detail\n"
        b"A001,2026-09-24 09:00,email sent,hello@,Test,"
        b"test@example.com,Example Clinic,hello\n"
    )
    response = client.post("/run", data={
        "badge_scans": (
            io.BytesIO((ROOT / "badge-scans.csv").read_bytes()),
            "badge-scans.csv",
        ),
        "booth_notes": (
            io.BytesIO((ROOT / "booth-notes.json").read_bytes()),
            "booth-notes.json",
        ),
        "after_show": (io.BytesIO(short_after), "after-show.csv"),
    }, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Warning: after-show data covers only" in response.data


def test_unexpected_error_renders_safe_message(monkeypatch):
    def fail(*_args, **_kwargs):
        raise RuntimeError("private implementation detail")

    monkeypatch.setattr(app_module, "run_pipeline", fail)
    client = app.test_client()
    response = client.post("/run", data={
        "badge_scans": (io.BytesIO(b"x"), "badge.csv"),
        "booth_notes": (io.BytesIO(b"x"), "booth.json"),
        "after_show": (io.BytesIO(b"x"), "after.csv"),
    }, content_type="multipart/form-data")
    assert response.status_code == 500
    assert b"Something went wrong. Check the file format (RuntimeError)." in response.data
    assert b"private implementation detail" not in response.data


def test_clinic_tick_reruns_and_excludes_bayview():
    client = app.test_client()
    response = client.post("/run", data={
        "badge_scans": (
            io.BytesIO((ROOT / "badge-scans.csv").read_bytes()),
            "badge-scans.csv",
        ),
        "booth_notes": (
            io.BytesIO((ROOT / "booth-notes.json").read_bytes()),
            "booth-notes.json",
        ),
        "after_show": (
            io.BytesIO((ROOT / "after-show-activity.csv").read_bytes()),
            "after-show-activity.csv",
        ),
    }, content_type="multipart/form-data")
    run_id = re.search(
        rb'name="run_id" value="([^"]+)"', response.data
    ).group(1).decode()
    rerun = client.post("/mark-customers", data={
        "run_id": run_id,
        "customer_clinics": "Bayview Physiotherapy & Wellness",
    })
    assert rerun.status_code == 200
    assert b"Jennifer MacIsaac" in rerun.data
    assert b"Ravi Sandhu" in rerun.data
    assert b"existing customer (Erin checked clinic on" in rerun.data
    assert re.search(
        rb'value="Bayview Physiotherapy &amp; Wellness"\s+checked',
        rerun.data,
    )

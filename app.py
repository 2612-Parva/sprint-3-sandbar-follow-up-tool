from __future__ import annotations

import inspect
import uuid
from datetime import datetime

from flask import Flask, render_template, request

from core import InputError, clinic_key, run_pipeline


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.jinja_env.auto_reload = True
app.jinja_env.cache.clear()
RUN_CACHE: dict[str, tuple[bytes, bytes, bytes]] = {}
BUILD_VERSION = "v5-2026-11-06"


def uploaded_bytes(field: str, required: bool = False) -> bytes | None:
    upload = request.files.get(field)
    if not upload or not upload.filename:
        if required:
            raise InputError(f"Please upload {field.replace('_', ' ')}.")
        return None
    return upload.read()


@app.get("/")
def index():
    return render_template("index.html", build_version=BUILD_VERSION)


@app.post("/run")
def run():
    try:
        scan = uploaded_bytes("badge_scans", required=True)
        booth = uploaded_bytes("booth_notes", required=True)
        after = uploaded_bytes("after_show", required=True)
        result = run_pipeline(scan, booth, after)
        run_id = str(uuid.uuid4())
        RUN_CACHE[run_id] = (scan, booth, after)
        result["run_id"] = run_id
        result["checked_clinics"] = []
        result["build_version"] = BUILD_VERSION
    except InputError as exc:
        return render_template("index.html", error=str(exc)), 400
    except UnicodeDecodeError as exc:
        return render_template(
            "index.html", error=f"File is not valid UTF-8: {exc}"
        ), 400
    except Exception as exc:
        app.logger.exception("Unhandled error in /run")
        return render_template(
            "index.html",
            error=f"Something went wrong. Check the file format ({type(exc).__name__}).",
        ), 500

    return render_template("results.html", result=result)


@app.post("/mark-customers")
def mark_customers():
    run_id = request.form.get("run_id", "")
    selected = request.form.getlist("customer_clinics")
    cached = RUN_CACHE.get(run_id)
    if not cached:
        return render_template(
            "index.html",
            error="This run has expired. Please re-upload the three files.",
        ), 400
    scan, booth, after = cached
    result = run_pipeline(
        scan,
        booth,
        after,
        customer_clinics={clinic_key(clinic) for clinic in selected},
        customer_checked_at=datetime.now().strftime("%Y-%m-%d"),
    )
    result["run_id"] = run_id
    result["checked_clinics"] = list(selected)
    result["build_version"] = BUILD_VERSION
    return render_template("results.html", result=result)


@app.get("/health")
def health():
    import core as _core
    from core import ASK_PATTERNS, COMPETITORS, STUDENT_TERMS

    source = inspect.getsource(_core.classify_priority)
    has_5_nov = "5 November" in source
    return {
        "build_version": BUILD_VERSION,
        "competitors_count": len(COMPETITORS),
        "student_terms_count": len(STUDENT_TERMS),
        "ask_categories": list(ASK_PATTERNS.keys()),
        "divergence_text_current": has_5_nov,
        "note": (
            "If divergence_text_current is false, the running server has "
            "the OLD divergence text. Restart the server (Ctrl+C, "
            "`python app.py`) before the demo."
        ),
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

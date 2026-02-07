"""Load existing JSON data from manually_scrapped_data/ into Supabase tables."""

import argparse
import json
import re
from pathlib import Path

from config.settings import settings
from database.db_manager import DBManager
from utils.logger import logger


BATCH_SIZE = 50


# Mapping of JSON files to tables and their transform functions
FILE_TABLE_MAP = {
    "depts.json": {
        "table": "departments",
        "transform": "_transform_departments",
        "upsert_on": "code",
    },
    "all_available_programs.json": {
        "table": "programs",
        "transform": "_transform_programs",
        "upsert_on": "name,degree_type",
    },
    "tution_fees.json": {
        "table": "tuition_fees",
        "transform": "_transform_tuition_fees",
        "upsert_on": "program,level",
    },
    "scholarships_and_financial_aids.json": {
        "table": "scholarships",
        "transform": "_transform_scholarships",
        "upsert_on": "name",
    },
    "clubs.json": {
        "table": "clubs",
        "transform": "_transform_clubs",
        "upsert_on": "name",
    },
    "events_workshops.json": {
        "table": "events",
        "transform": "_transform_events",
        "upsert_on": "title",
    },
    "ewu_faculty_complete.json": {
        "table": "faculty_members",
        "transform": "_transform_faculty_members",
        "batch": True,
        "upsert_on": "profile_id",
    },
    "academic_council.json": {
        "table": "governance_members",
        "transform": "_transform_academic_council",
        "upsert_on": "body,name",
    },
    "ewu_board_of_trustees.json": {
        "table": "governance_members",
        "transform": "_transform_board_of_trustees",
        "upsert_on": "body,name",
    },
    "syndicate.json": {
        "table": "governance_members",
        "transform": "_transform_syndicate",
        "upsert_on": "body,name",
    },
    "admission_deadlines.json": {
        "table": "admission_deadlines",
        "transform": "_transform_admission_deadlines",
        "upsert_on": "program,level,semester",
    },
    "grading.json": {
        "table": "grade_scale",
        "transform": "_transform_grading",
        "upsert_on": "letter_grade",
    },
    "alumni.json": {
        "table": "notable_alumni",
        "transform": "_transform_alumni",
        "upsert_on": "name,department",
    },
    "helpdesk.json": {
        "table": "helpdesk_contacts",
        "transform": "_transform_helpdesk",
        "upsert_on": "email",
    },
    "ewu_proctor_schedule.json": {
        "table": "proctor_schedule",
        "transform": "_transform_proctor_schedule",
        "upsert_on": "semester,role,name",
    },
    "ewu_newsletters_complete.json": {
        "table": "newsletters",
        "transform": "_transform_newsletters",
        "upsert_on": "title",
    },
    "ewu_partnerships.json": {
        "table": "partnerships",
        "transform": "_transform_partnerships",
        "upsert_on": "name",
    },
    "policy.json": {
        "table": "policies",
        "transform": "_transform_policies",
        "upsert_on": "name",
    },
    # University documents (singleton JSON blobs)
    "about_ewu.json": {
        "table": "university_documents",
        "transform": "_transform_about_ewu",
        "upsert_on": "slug",
    },
    "facilites.json": {
        "table": "university_documents",
        "transform": "_transform_facilities",
        "upsert_on": "slug",
    },
    "admission_process.json": {
        "table": "university_documents",
        "transform": "_transform_admission_process",
        "upsert_on": "slug",
    },
    "admission_requirements.json": {
        "table": "university_documents",
        "transform": "_transform_admission_requirements",
        "upsert_on": "slug",
    },
    "career_counseling_center.json": {
        "table": "university_documents",
        "transform": "_transform_career_counseling",
        "upsert_on": "slug",
    },
    "payment_procedure.json": {
        "table": "university_documents",
        "transform": "_transform_payment_procedure",
        "upsert_on": "slug",
    },
    "rules.json": {
        "table": "university_documents",
        "transform": "_transform_rules",
        "upsert_on": "slug",
    },
    "sexual_harassment.json": {
        "table": "university_documents",
        "transform": "_transform_sexual_harassment",
        "upsert_on": "slug",
    },
}


def _load_json(filepath: Path) -> dict | list:
    """Load and return JSON data from a file."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def _batch_upsert(db: DBManager, table: str, records: list[dict], on_conflict: str = "id") -> bool:
    """Upsert records in batches to avoid payload size limits."""
    total = len(records)
    for i in range(0, total, BATCH_SIZE):
        batch = records[i : i + BATCH_SIZE]
        success = db.upsert(table, batch, on_conflict=on_conflict)
        if not success:
            logger.error(f"Batch upsert failed at offset {i} for {table}")
            return False
        logger.info(f"  Batch {i // BATCH_SIZE + 1}: upserted {len(batch)} records")
    return True


def _transform_departments(data: dict) -> list[dict]:
    """Transform depts.json into department records."""
    records = []
    faculties = data.get("faculties", data.get("data", []))

    if isinstance(faculties, list):
        for faculty in faculties:
            faculty_name = faculty.get("name", faculty.get("faculty", ""))
            departments = faculty.get("departments", [])
            for dept in departments:
                if isinstance(dept, str):
                    abbr_match = re.search(r'\(([^)]+)\)', dept)
                    code = abbr_match.group(1) if abbr_match else ""
                    records.append({
                        "name": dept,
                        "code": code or None,
                        "faculty": faculty_name,
                        "url": "",
                        "description": "",
                    })
                else:
                    records.append({
                        "name": dept.get("name", ""),
                        "code": dept.get("code", dept.get("abbreviation", "")),
                        "faculty": faculty_name,
                        "url": dept.get("url", ""),
                        "description": dept.get("description", ""),
                    })

    other_units = data.get("other_academic_units", [])
    for unit in other_units:
        name = unit.get("name", "")
        abbr_match = re.search(r'\(([^)]+)\)', name)
        code = abbr_match.group(1) if abbr_match else None
        records.append({
            "name": name,
            "code": code,
            "faculty": "Other Academic Units",
            "url": "",
            "description": "",
        })

    return records


def _transform_programs(data: dict) -> list[dict]:
    """Transform all_available_programs.json into program records."""
    records = []
    programs = data.get("programs", data.get("data", []))

    if isinstance(programs, list):
        for prog in programs:
            department_name = prog.get("department", "")
            degrees = prog.get("degrees", [])
            for degree in degrees:
                records.append({
                    "name": degree.get("title", degree.get("name", "")),
                    "degree_type": degree.get("level", ""),
                    "department_name": department_name,
                    "credits": degree.get("credits"),
                    "duration": degree.get("duration"),
                })

    return records


def _transform_tuition_fees(data: dict) -> list[dict]:
    """Transform tution_fees.json into tuition fee records."""
    records = []

    for level_key, level_name in [("undergraduate_programs", "Undergraduate"), ("graduate_programs", "Graduate")]:
        level_data = data.get(level_key, {})

        per_credit = level_data.get("tuition_fees_per_credit", [])
        detailed = level_data.get("detailed_fee_structure", [])

        detailed_map = {}
        for d in detailed:
            detailed_map[d.get("program", "")] = d

        for item in per_credit:
            program = item.get("program", "")
            detail = detailed_map.get(program, {})

            records.append({
                "program": program,
                "level": level_name,
                "fee_per_credit": item.get("fee_per_credit"),
                "total_tuition": detail.get("tuition_fees"),
                "library_lab_fees": detail.get("library_lab_activities_fees"),
                "admission_fee": detail.get("admission_fee"),
                "grand_total": detail.get("grand_total"),
                "credits": detail.get("credits"),
                "currency": "BDT",
            })

    return records


def _transform_scholarships(data: dict) -> list[dict]:
    """Transform scholarships_and_financial_aids.json into scholarship records."""
    records = []
    effective_from = data.get("effective_from", "")

    # Extract from merit_scholarships (dict of named scholarship categories)
    merit = data.get("merit_scholarships", {})
    for key, value in merit.items():
        if isinstance(value, dict):
            eligibility = value.get("eligibility", "")
            if isinstance(eligibility, dict):
                eligibility = json.dumps(eligibility)
            elif not isinstance(eligibility, str):
                eligibility = str(eligibility)

            scholarship_name = value.get("scholarship", key.replace("_", " ").title())
            cgpa = value.get("continuation_requirements", {}).get("minimum_cgpa") if isinstance(value.get("continuation_requirements"), dict) else None

            records.append({
                "name": scholarship_name,
                "description": key.replace("_", " ").title(),
                "eligibility": eligibility,
                "amount": str(value.get("scholarship", value.get("duration", ""))),
                "cgpa_requirement": cgpa,
                "effective_from": effective_from,
            })

    # Extract from financial_assistance
    financial = data.get("financial_assistance", {})
    for key, value in financial.items():
        if isinstance(value, dict):
            records.append({
                "name": key.replace("_", " ").title(),
                "description": value.get("benefit", value.get("scholarship", "")),
                "eligibility": value.get("eligibility", ""),
                "amount": str(value.get("scholarship", value.get("benefit", ""))),
                "cgpa_requirement": value.get("minimum_cgpa"),
                "effective_from": effective_from,
            })

    # Extract graduate scholarship requirements
    grad_reqs = data.get("graduate_scholarship_requirements", {})
    grad_scholarships = grad_reqs.get("scholarships", [])
    for gs in grad_scholarships:
        records.append({
            "name": f"Graduate Scholarship ({gs.get('scholarship_percentage', '')})",
            "description": f"Bachelor CGPA: {gs.get('bachelor_cgpa', '')}",
            "eligibility": f"Bachelor CGPA {gs.get('bachelor_cgpa', '')}",
            "amount": gs.get("scholarship_percentage", ""),
            "cgpa_requirement": None,
            "effective_from": grad_reqs.get("effective_from", effective_from),
        })

    return records


def _transform_clubs(data: dict) -> list[dict]:
    """Transform clubs.json into club records."""
    records = []
    clubs = data.get("clubs", data.get("data", []))
    base_keys = {"name", "description", "url", "logo"}

    if isinstance(clubs, list):
        for club in clubs:
            extra = {k: v for k, v in club.items() if k not in base_keys and v}
            records.append({
                "name": club.get("name", ""),
                "description": club.get("description", ""),
                "url": club.get("url", ""),
                "logo": club.get("logo", ""),
                "details": extra or None,
            })

    return records


def _transform_events(data: dict) -> list[dict]:
    """Transform events_workshops.json into event records."""
    records = []
    events = data.get("events_workshops", data.get("events", data.get("data", [])))

    if isinstance(events, list):
        for event in events:
            records.append({
                "title": event.get("title", event.get("name", "")),
                "description": event.get("description", ""),
                "event_date": event.get("date", event.get("event_date")),
                "location": event.get("location", event.get("venue", "")),
                "url": event.get("url", ""),
            })

    return records


def _transform_faculty_members(data: dict) -> list[dict]:
    """Transform ewu_faculty_complete.json into faculty_members records."""
    records = []
    faculty_list = data.get("faculty", [])

    for f in faculty_list:
        sections = f.get("sections", {})
        records.append({
            "name": f.get("name", ""),
            "designation": f.get("position", ""),
            "department_name": f.get("department", ""),
            "email": f.get("email", ""),
            "phone": f.get("phone", ""),
            "profile_url": f.get("profile_url", ""),
            "profile_id": f.get("profile_id", ""),
            "image_url": f.get("image_url", ""),
            "specialization": sections.get("research_interest", ""),
            "academic_background": sections.get("academic_background"),
            "publications": sections.get("selected_publications"),
            "details": {
                k: v for k, v in sections.items()
                if k not in ("academic_background", "selected_publications", "research_interest")
                and v
            } or None,
        })

    return records


def _transform_academic_council(data: dict) -> list[dict]:
    """Transform academic_council.json into governance_members records."""
    records = []
    council = data.get("academic_council", {})

    chair = council.get("chairperson", {})
    if chair:
        records.append({
            "body": "academic_council",
            "name": chair.get("name", ""),
            "role": chair.get("role", ""),
            "is_chairperson": True,
        })

    for member in council.get("members", []):
        records.append({
            "body": "academic_council",
            "name": member.get("name", ""),
            "role": member.get("role", ""),
            "is_chairperson": False,
        })

    return records


def _transform_board_of_trustees(data: dict) -> list[dict]:
    """Transform ewu_board_of_trustees.json into governance_members records."""
    records = []
    board = data.get("board_of_trustees", {})

    chair = board.get("chairperson", {})
    if chair:
        details = {k: v for k, v in chair.items() if k not in ("name", "title", "profile_url")}
        records.append({
            "body": "board_of_trustees",
            "name": chair.get("name", ""),
            "role": chair.get("title", ""),
            "is_chairperson": True,
            "profile_url": chair.get("profile_url", ""),
            "details": details or None,
        })

    for member in board.get("members", []):
        details = {k: v for k, v in member.items() if k not in ("name", "title", "profile_url")}
        records.append({
            "body": "board_of_trustees",
            "name": member.get("name", ""),
            "role": member.get("title", ""),
            "is_chairperson": False,
            "profile_url": member.get("profile_url", ""),
            "details": details or None,
        })

    return records


def _transform_syndicate(data: dict) -> list[dict]:
    """Transform syndicate.json into governance_members records."""
    records = []
    syndicate = data.get("syndicate", {})

    chair = syndicate.get("chairperson", {})
    if chair:
        records.append({
            "body": "syndicate",
            "name": chair.get("name", ""),
            "role": chair.get("role", ""),
            "is_chairperson": True,
        })

    for member in syndicate.get("members", []):
        records.append({
            "body": "syndicate",
            "name": member.get("name", ""),
            "role": member.get("role", ""),
            "is_chairperson": False,
        })

    return records


def _transform_admission_deadlines(data: dict) -> list[dict]:
    """Transform admission_deadlines.json into admission_deadlines records."""
    records = []
    semester = data.get("summary", {}).get("semester", "")

    for level_key, level_name in [("undergraduate_programs", "Undergraduate"), ("graduate_programs", "Graduate")]:
        for prog in data.get(level_key, []):
            records.append({
                "program": prog.get("program", ""),
                "department": prog.get("department", ""),
                "level": level_name,
                "semester": semester,
                "application_deadline": prog.get("application_deadline", ""),
                "admission_test_date": prog.get("admission_test_date", ""),
            })

    return records


def _transform_grading(data: dict) -> list[dict]:
    """Transform grading.json into grade_scale records."""
    records = []
    grading = data.get("grading_system", {})

    for g in grading.get("grade_scale", []):
        records.append({
            "numerical_score": g.get("numerical_score", ""),
            "letter_grade": g.get("letter_grade", ""),
            "grade_point": g.get("grade_point", 0),
            "is_special": False,
        })

    for g in grading.get("special_grades", []):
        records.append({
            "numerical_score": "N/A",
            "letter_grade": g.get("grade", ""),
            "grade_point": g.get("grade_point", 0),
            "is_special": True,
            "description": g.get("description", ""),
            "note": g.get("note", ""),
        })

    return records


def _transform_alumni(data: dict) -> list[dict]:
    """Transform alumni.json into notable_alumni records."""
    records = []

    for alumnus in data.get("notable_alumni", []):
        awards = alumnus.get("awards")
        records.append({
            "name": alumnus.get("name", ""),
            "department": alumnus.get("department", ""),
            "achievement": alumnus.get("achievement", ""),
            "details": alumnus.get("details", ""),
            "position": alumnus.get("position", ""),
            "company": alumnus.get("company", ""),
            "awards": awards if isinstance(awards, list) else None,
            "year_awarded": alumnus.get("year_awarded"),
        })

    return records


def _transform_helpdesk(data: dict) -> list[dict]:
    """Transform helpdesk.json into helpdesk_contacts records."""
    records = []
    helpdesks = data.get("department_helpdesks", {})

    for _key, dept in helpdesks.get("academic_departments", {}).items():
        records.append({
            "category": "academic",
            "department_code": dept.get("department", ""),
            "full_name": dept.get("full_name", ""),
            "email": dept.get("email", ""),
        })

    for _key, office in helpdesks.get("administrative_offices", {}).items():
        records.append({
            "category": "administrative",
            "department_code": office.get("office", ""),
            "full_name": office.get("office", ""),
            "email": office.get("email", ""),
            "purpose": office.get("purpose", ""),
        })

    return records


def _transform_proctor_schedule(data: dict) -> list[dict]:
    """Transform ewu_proctor_schedule.json into proctor_schedule records."""
    records = []
    semester = data.get("semester", "")

    # Main proctor
    proctor = data.get("proctor", {})
    if proctor:
        records.append({
            "semester": semester,
            "role": "Proctor",
            "name": proctor.get("name", ""),
            "designation": proctor.get("designation", ""),
            "department": proctor.get("department", ""),
            "office_extension": proctor.get("extension", ""),
            "room_number": proctor.get("room_number", ""),
            "email": proctor.get("email", ""),
        })

    # Daily schedule (assistant proctors)
    for entry in data.get("daily_schedule", []):
        duty = entry.get("on_duty_proctor", {})
        records.append({
            "semester": semester,
            "role": "Assistant Proctor",
            "day_of_week": entry.get("day", ""),
            "name": duty.get("name", ""),
            "designation": duty.get("designation", ""),
            "department": duty.get("department", ""),
            "office_extension": duty.get("office_extension", ""),
            "room_number": duty.get("room_number", ""),
        })

    # Supporting staff
    for staff in data.get("supporting_staff", []):
        records.append({
            "semester": semester,
            "role": "Supporting Staff",
            "name": staff.get("name", ""),
            "designation": staff.get("designation", ""),
            "department": staff.get("office", ""),
            "office_extension": staff.get("extension", ""),
            "room_number": staff.get("room_number", ""),
        })

    return records


def _transform_newsletters(data: dict) -> list[dict]:
    """Transform ewu_newsletters_complete.json into newsletters records."""
    records = []
    by_year = data.get("newsletters", {}).get("by_year", {})

    for _year, items in by_year.items():
        for nl in items:
            records.append({
                "title": nl.get("title", ""),
                "published_date": nl.get("date", ""),
                "semester": nl.get("semester", ""),
                "year": nl.get("year", ""),
                "image_url": nl.get("image_url", ""),
                "pdf_url": nl.get("pdf_url", ""),
            })

    return records


def _transform_partnerships(data: dict) -> list[dict]:
    """Transform ewu_partnerships.json into partnerships records."""
    records = []

    for p in data.get("partnerships", []):
        records.append({
            "name": p.get("name", ""),
            "acronym": p.get("acronym", ""),
            "country": p.get("country", ""),
            "organization_type": p.get("type", ""),
            "partnership_type": p.get("partnership_type", ""),
            "description": p.get("description", ""),
            "areas_of_collaboration": p.get("areas_of_collaboration"),
            "status": p.get("status", "Active"),
            "signed_date": p.get("signed_date"),
        })

    return records


def _transform_policies(data: dict) -> list[dict]:
    """Transform policy.json into policies records."""
    records = []

    for policy in data.get("policies", []):
        records.append({
            "name": policy.get("name", ""),
            "purpose": policy.get("purpose", ""),
            "scope": policy.get("scope", ""),
            "principles": policy.get("principles"),
            "key_actions": policy.get("key_actions"),
            "committee_members": policy.get("committee_members"),
            "objectives": policy.get("objectives", ""),
        })

    return records


def _make_document(slug: str, title: str, data, source_file: str) -> list[dict]:
    """Helper to wrap a JSON blob as a university_documents record."""
    return [{
        "slug": slug,
        "title": title,
        "content": data,
        "source_file": source_file,
    }]


def _transform_about_ewu(data: dict) -> list[dict]:
    return _make_document("about-ewu", "About East West University", data, "about_ewu.json")


def _transform_facilities(data: dict) -> list[dict]:
    return _make_document("facilities", "University Facilities", data, "facilites.json")


def _transform_admission_process(data: dict) -> list[dict]:
    return _make_document("admission-process", "Admission Process", data, "admission_process.json")


def _transform_admission_requirements(data: dict) -> list[dict]:
    return _make_document("admission-requirements", "Admission Requirements", data, "admission_requirements.json")


def _transform_career_counseling(data: dict) -> list[dict]:
    return _make_document("career-counseling", "Career Counseling Center", data, "career_counseling_center.json")


def _transform_payment_procedure(data: dict) -> list[dict]:
    return _make_document("payment-procedure", "Payment Procedure", data, "payment_procedure.json")


def _transform_rules(data: dict) -> list[dict]:
    return _make_document("rules", "Student Rules and Regulations", data, "rules.json")


def _transform_sexual_harassment(data: dict) -> list[dict]:
    return _make_document("sexual-harassment-policy", "Sexual Harassment Elimination Policy", data, "sexual_harassment.json")


TRANSFORMS = {
    "_transform_departments": _transform_departments,
    "_transform_programs": _transform_programs,
    "_transform_tuition_fees": _transform_tuition_fees,
    "_transform_scholarships": _transform_scholarships,
    "_transform_clubs": _transform_clubs,
    "_transform_events": _transform_events,
    "_transform_faculty_members": _transform_faculty_members,
    "_transform_academic_council": _transform_academic_council,
    "_transform_board_of_trustees": _transform_board_of_trustees,
    "_transform_syndicate": _transform_syndicate,
    "_transform_admission_deadlines": _transform_admission_deadlines,
    "_transform_grading": _transform_grading,
    "_transform_alumni": _transform_alumni,
    "_transform_helpdesk": _transform_helpdesk,
    "_transform_proctor_schedule": _transform_proctor_schedule,
    "_transform_newsletters": _transform_newsletters,
    "_transform_partnerships": _transform_partnerships,
    "_transform_policies": _transform_policies,
    "_transform_about_ewu": _transform_about_ewu,
    "_transform_facilities": _transform_facilities,
    "_transform_admission_process": _transform_admission_process,
    "_transform_admission_requirements": _transform_admission_requirements,
    "_transform_career_counseling": _transform_career_counseling,
    "_transform_payment_procedure": _transform_payment_procedure,
    "_transform_rules": _transform_rules,
    "_transform_sexual_harassment": _transform_sexual_harassment,
}


def run_migration(clean: bool = False):
    """Load all mapped JSON files into Supabase.

    Args:
        clean: If True, delete all existing rows before upserting.
    """
    db = DBManager()
    data_dir = settings.MANUAL_DATA_DIR

    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        return

    if clean:
        # Collect unique tables and wipe them once each
        tables_to_clean = list(dict.fromkeys(
            config["table"] for config in FILE_TABLE_MAP.values()
        ))
        for table in tables_to_clean:
            logger.info(f"[clean] Deleting all rows from {table}")
            db.delete_all(table)

    for filename, config in FILE_TABLE_MAP.items():
        filepath = data_dir / filename
        if not filepath.exists():
            logger.warning(f"File not found, skipping: {filepath}")
            continue

        logger.info(f"Migrating {filename} -> {config['table']}")

        raw_data = _load_json(filepath)
        transform_fn = TRANSFORMS[config["transform"]]
        records = transform_fn(raw_data)

        if not records:
            logger.warning(f"No records produced from {filename}")
            continue

        table = config["table"]
        upsert_on = config.get("upsert_on", "id")

        if config.get("batch"):
            success = _batch_upsert(db, table, records, on_conflict=upsert_on)
        else:
            success = db.upsert(table, records, on_conflict=upsert_on)

        if success:
            logger.info(f"Migrated {len(records)} records from {filename}")
        else:
            logger.error(f"Failed to migrate {filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migrate JSON data to Supabase")
    parser.add_argument("--clean", action="store_true",
                        help="Delete all existing rows before upserting")
    args = parser.parse_args()
    run_migration(clean=args.clean)

"""EWU Data Scraper - Main Orchestrator

Runs all configured scrapers, validates data, diffs against current database,
and upserts changes if they are within safe thresholds.
"""

import sys
import time
from datetime import datetime, timezone

from config.settings import settings
from utils.logger import logger
from utils.diff_checker import DiffChecker
from utils.notifier import Notifier
from scrapers.ewu import (
    TuitionFeesScraper,
    ScholarshipsScraper,
    NoticesScraper,
    FacultyScraper,
    EventsScraper,
    ClubsScraper,
    AboutScraper,
    NewslettersScraper,
    AdmissionDeadlinesScraper,
    HelpdeskScraper,
    GovernanceScraper,
    GradingScraper,
    PoliciesDocScraper,
    RulesScraper,
    PaymentScraper,
    CareerCenterScraper,
    AdmissionProcessScraper,
    AdmissionRequirementsScraper,
    SexualHarassmentScraper,
    FacilitiesScraper,
    AcademicCalendarScraper,
)

# Maximum allowed change percentage before aborting upsert
MAX_CHANGE_PERCENT = 30.0

# Set via --force flag to bypass safety threshold (for initial bootstrap)
FORCE_MODE = "--force" in sys.argv

# Fields added by scrapers for tracking but not present in DB tables
NON_SCHEMA_FIELDS = {"source_url", "source_file"}

# DB-generated fields that shouldn't be used in diff comparisons
DB_META_FIELDS = {"id", "created_at", "updated_at"}

# Scrapers to run, mapped to their database table
SCRAPER_CONFIG = [
    {"scraper": TuitionFeesScraper, "table": "tuition_fees", "key_field": "program", "on_conflict": "program,level"},
    {"scraper": ScholarshipsScraper, "table": "scholarships", "key_field": "name", "on_conflict": "name"},
    {"scraper": NoticesScraper, "table": "notices", "key_field": "title", "on_conflict": "title"},
    {"scraper": EventsScraper, "table": "events", "key_field": "title", "on_conflict": "title"},
    {"scraper": ClubsScraper, "table": "clubs", "key_field": "name", "on_conflict": "name"},
    {"scraper": FacultyScraper, "table": "faculty_members", "key_field": "profile_id", "on_conflict": "profile_id"},
    {"scraper": NewslettersScraper, "table": "newsletters", "key_field": "title", "on_conflict": "title"},
    {"scraper": AdmissionDeadlinesScraper, "table": "admission_deadlines", "key_field": "program", "on_conflict": "program,level,semester"},
    {"scraper": HelpdeskScraper, "table": "helpdesk_contacts", "key_field": "email", "on_conflict": "email"},
    {"scraper": GovernanceScraper, "table": "governance_members", "key_field": "name", "on_conflict": "body,name"},
    # Document scrapers (single-record JSONB blobs, shared table)
    {"scraper": GradingScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": PoliciesDocScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": RulesScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": PaymentScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": CareerCenterScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": AdmissionProcessScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": AdmissionRequirementsScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": SexualHarassmentScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    {"scraper": FacilitiesScraper, "table": "university_documents", "key_field": "slug", "on_conflict": "slug", "shared_table": True},
    # Full-replace scrapers (delete all + insert on each run)
    {"scraper": AcademicCalendarScraper, "table": "academic_calendar", "key_field": "event_name", "on_conflict": "semester,program_type,calendar_type,event_date,event_name", "replace_all": True},
    # JSON-only, no DB table
    {"scraper": AboutScraper, "table": None, "key_field": "section"},
]


def _strip_non_schema_fields(data: list[dict]) -> list[dict]:
    """Remove fields that don't exist in the DB schema before upsert."""
    return [
        {k: v for k, v in record.items() if k not in NON_SCHEMA_FIELDS}
        for record in data
    ]


def _prepare_for_diff(data: list[dict]) -> list[dict]:
    """Strip metadata fields from both DB and scraper data for fair comparison."""
    skip = DB_META_FIELDS | NON_SCHEMA_FIELDS
    return [
        {k: v for k, v in record.items() if k not in skip}
        for record in data
    ]


def _deduplicate(data: list[dict], key_fields: str) -> list[dict]:
    """Keep only the first occurrence of each unique key combination.

    key_fields can be a single field name or comma-separated composite key.
    """
    fields = [f.strip() for f in key_fields.split(",")]
    seen = set()
    result = []
    for record in data:
        key = tuple(record.get(f) for f in fields)
        if any(v is None for v in key):
            result.append(record)
            continue
        if key not in seen:
            seen.add(key)
            result.append(record)
    return result


def run_scraper(config: dict, db=None) -> dict:
    """Run a single scraper and optionally sync to database.

    Returns a summary dict.
    """
    scraper_cls = config["scraper"]
    table = config["table"]
    key_field = config["key_field"]
    scraper = scraper_cls()

    start = time.time()
    summary = {
        "scraper": scraper.name,
        "status": "success",
        "records": 0,
        "changes": 0,
        "duration": 0.0,
    }

    try:
        new_data = scraper.run()
        summary["records"] = len(new_data)

        if not new_data:
            summary["status"] = "no_data"
            return summary

        # Sync to database if available
        if db and table:
            on_conflict = config.get("on_conflict", key_field)
            clean_data = _strip_non_schema_fields(new_data)
            clean_data = _deduplicate(clean_data, on_conflict)

            if config.get("replace_all"):
                # Full replacement: delete everything, then insert fresh data
                logger.info(f"[{scraper.name}] replace_all mode: deleting all rows from {table}")
                db.delete_all(table)
                success = db.upsert(table, clean_data, on_conflict=on_conflict)
                summary["changes"] = len(clean_data)
                if not success:
                    summary["status"] = "upsert_failed"
            else:
                # Normal diff-based upsert
                old_data = db.get_all(table)
                should_upsert = True

                if old_data:
                    new_keys = {r[key_field] for r in new_data if key_field in r}
                    if config.get("shared_table"):
                        old_data = [r for r in old_data if r.get(key_field) in new_keys]

                    old_clean = _prepare_for_diff(old_data)
                    new_clean = _prepare_for_diff(new_data)

                    diff = DiffChecker.compare(old_clean, new_clean, key_field)
                    report = DiffChecker.generate_report(diff)
                    logger.info(f"[{scraper.name}] Diff:\n{report}")
                    summary["changes"] = len(diff.added) + len(diff.modified) + len(diff.removed)

                    skip_threshold = config.get("shared_table", False) or FORCE_MODE
                    if not skip_threshold and diff.change_percentage > MAX_CHANGE_PERCENT:
                        logger.warning(
                            f"[{scraper.name}] Change percentage {diff.change_percentage:.1f}% "
                            f"exceeds threshold {MAX_CHANGE_PERCENT}%. Skipping upsert."
                        )
                        summary["status"] = "skipped_high_change"
                        return summary

                    should_upsert = diff.has_changes

                if should_upsert:
                    success = db.upsert(table, clean_data, on_conflict=on_conflict)
                    if not success:
                        summary["status"] = "upsert_failed"

    except Exception as e:
        logger.error(f"[{scraper.name}] Error: {e}")
        summary["status"] = f"error: {e}"
    finally:
        summary["duration"] = round(time.time() - start, 2)

    return summary


def main():
    """Run all scrapers and generate summary report."""
    logger.info("=" * 60)
    logger.info("EWU Data Scraper - Starting run")
    if FORCE_MODE:
        logger.warning("FORCE MODE: Safety threshold bypassed for all scrapers")
    logger.info(f"Time: {datetime.now(timezone.utc).isoformat()}")
    logger.info("=" * 60)

    settings.ensure_directories()

    # Try to connect to database (optional)
    db = None
    try:
        from database.db_manager import DBManager
        db = DBManager()
        if db.test_connection():
            logger.info("Database connected")
        else:
            logger.warning("Database connection failed, running in scrape-only mode")
            db = None
    except Exception as e:
        logger.warning(f"Database not configured, running in scrape-only mode: {e}")

    summaries = []
    for config in SCRAPER_CONFIG:
        logger.info(f"--- Running {config['scraper'].__name__} ---")
        summary = run_scraper(config, db)
        summaries.append(summary)

        if db:
            db.log_scrape(
                summary["scraper"],
                summary["records"],
                summary["status"],
                duration=summary["duration"],
            )

    logger.info("\n" + "=" * 60)
    logger.info("SCRAPE SUMMARY")
    logger.info("=" * 60)
    total_records = 0
    total_changes = 0
    for s in summaries:
        total_records += s["records"]
        total_changes += s["changes"]
        logger.info(
            f"  {s['scraper']:30s} | {s['status']:20s} | "
            f"records: {s['records']:5d} | changes: {s['changes']:5d} | "
            f"{s['duration']:.1f}s"
        )
    logger.info(f"  {'TOTAL':30s} | {'':20s} | records: {total_records:5d} | changes: {total_changes:5d}")

    report_msg = "\n".join(
        f"- **{s['scraper']}**: {s['status']} ({s['records']} records, {s['changes']} changes)"
        for s in summaries
    )
    Notifier.send_discord(f"**Scrape Run Complete**\n{report_msg}")


if __name__ == "__main__":
    main()

"""Integration tests for all EWU Database API endpoints.

Every test hits the real Supabase database — no mocks, no fakes.
Run with:  pytest tests/test_api.py -v
"""

from config.settings import settings


class TestMeta:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "healthy"}

    def test_last_update(self, client):
        r = client.get("/api/last-update")
        assert r.status_code == 200
        assert "data" in r.json()


class TestAcademic:
    def test_list_departments(self, client):
        r = client.get("/api/departments")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 17

    def test_list_departments_filter(self, client):
        r = client.get("/api/departments", params={"faculty": "Science"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1
        for dept in body["data"]:
            assert "science" in dept["faculty"].lower()

    def test_list_programs(self, client):
        r = client.get("/api/programs")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 25

    def test_list_programs_with_filters(self, client):
        # Fetch a real degree_type first to avoid case-sensitivity issues
        listing = client.get("/api/programs").json()
        real_type = listing["data"][0]["degree_type"]

        r = client.get("/api/programs", params={"degree_type": real_type})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1
        for prog in body["data"]:
            assert prog["degree_type"] == real_type

    def test_get_program_by_id(self, client):
        # Fetch a real program ID first
        listing = client.get("/api/programs").json()
        assert listing["count"] >= 1
        real_id = listing["data"][0]["id"]

        r = client.get(f"/api/programs/{real_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == real_id

    def test_get_program_not_found(self, client):
        r = client.get("/api/programs/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_list_grade_scale(self, client):
        r = client.get("/api/grade-scale")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 7

    def test_list_admission_deadlines(self, client):
        r = client.get("/api/admission-deadlines")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body

    def test_list_admission_deadlines_filter(self, client):
        r = client.get("/api/admission-deadlines", params={"level": "undergraduate"})
        assert r.status_code == 200
        body = r.json()
        assert "data" in body

    def test_list_academic_calendar(self, client):
        r = client.get("/api/academic-calendar")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body

    def test_academic_calendar_filter(self, client):
        r = client.get("/api/academic-calendar", params={"calendar_type": "academic_calendar"})
        assert r.status_code == 200
        body = r.json()
        assert "data" in body


class TestPeople:
    def test_list_faculty(self, client):
        r = client.get("/api/faculty")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_faculty_filter_by_name(self, client):
        r = client.get("/api/faculty", params={"name": "Dr"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_get_faculty_by_id(self, client):
        # Fetch a real faculty ID first
        listing = client.get("/api/faculty").json()
        assert listing["count"] >= 1
        real_id = listing["data"][0]["id"]

        r = client.get(f"/api/faculty/{real_id}")
        assert r.status_code == 200
        assert r.json()["data"]["id"] == real_id

    def test_get_faculty_not_found(self, client):
        r = client.get("/api/faculty/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_list_governance(self, client):
        r = client.get("/api/governance")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_governance_filter(self, client):
        r = client.get("/api/governance", params={"body": "academic_council"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1
        for member in body["data"]:
            assert member["body"] == "academic_council"

    def test_list_alumni(self, client):
        r = client.get("/api/alumni")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 10


class TestFinance:
    def test_list_tuition_fees(self, client):
        r = client.get("/api/tuition-fees")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_tuition_fees_filter(self, client):
        r = client.get("/api/tuition-fees", params={"level": "undergraduate"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_scholarships(self, client):
        r = client.get("/api/scholarships")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 11


class TestInformation:
    def test_list_documents(self, client):
        r = client.get("/api/documents")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_get_document_by_slug(self, client):
        # Fetch real doc list, use first slug
        listing = client.get("/api/documents").json()
        assert listing["count"] >= 1
        real_slug = listing["data"][0]["slug"]

        r = client.get(f"/api/documents/{real_slug}")
        assert r.status_code == 200
        doc = r.json()["data"]
        assert doc["slug"] == real_slug
        assert "content" in doc

    def test_get_document_not_found(self, client):
        r = client.get("/api/documents/nonexistent-slug-xyz")
        assert r.status_code == 404

    def test_list_policies(self, client):
        r = client.get("/api/policies")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_newsletters(self, client):
        r = client.get("/api/newsletters")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 31

    def test_list_partnerships(self, client):
        r = client.get("/api/partnerships")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1


class TestCampus:
    def test_list_clubs(self, client):
        r = client.get("/api/clubs")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 22

    def test_list_notices(self, client):
        r = client.get("/api/notices")
        assert r.status_code == 200
        body = r.json()
        assert "data" in body

    def test_list_notices_with_limit(self, client):
        r = client.get("/api/notices", params={"limit": 5})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] <= 5

    def test_list_events(self, client):
        r = client.get("/api/events")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_helpdesk(self, client):
        r = client.get("/api/helpdesk")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_helpdesk_filter(self, client):
        # First get a real category from the data
        listing = client.get("/api/helpdesk").json()
        assert listing["count"] >= 1
        real_category = listing["data"][0]["category"]

        r = client.get("/api/helpdesk", params={"category": real_category})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_proctor_schedule(self, client):
        r = client.get("/api/proctor-schedule")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1


class TestCourses:
    def test_list_programs(self, client):
        r = client.get("/api/courses/programs")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 22

    def test_list_programs_undergraduate(self, client):
        r = client.get("/api/courses/programs", params={"level": "undergraduate"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 14
        for prog in body["data"]:
            assert prog["level"] == "undergraduate"

    def test_list_programs_graduate(self, client):
        r = client.get("/api/courses/programs", params={"level": "graduate"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 8
        for prog in body["data"]:
            assert prog["level"] == "graduate"

    def test_get_program_by_code(self, client):
        listing = client.get("/api/courses/programs").json()
        assert listing["count"] >= 1
        real_code = listing["data"][0]["program_code"]

        r = client.get(f"/api/courses/programs/{real_code}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["program_code"] == real_code
        assert "courses" in data

    def test_get_program_not_found(self, client):
        r = client.get("/api/courses/programs/nonexistent-xyz-999")
        assert r.status_code == 404

    def test_list_courses(self, client):
        r = client.get("/api/courses")
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_courses_filter_level(self, client):
        r = client.get("/api/courses", params={"level": "undergraduate"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1
        for course in body["data"]:
            assert course["level"] == "undergraduate"

    def test_list_courses_filter_program(self, client):
        listing = client.get("/api/courses/programs").json()
        assert listing["count"] >= 1
        real_code = listing["data"][0]["program_code"]

        r = client.get("/api/courses", params={"program": real_code})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1
        for course in body["data"]:
            assert course["program_code"] == real_code

    def test_list_courses_filter_type(self, client):
        r = client.get("/api/courses", params={"course_type": "Core"})
        assert r.status_code == 200
        body = r.json()
        assert "data" in body

    def test_list_courses_search(self, client):
        r = client.get("/api/courses", params={"search": "English"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_list_courses_pagination(self, client):
        r1 = client.get("/api/courses", params={"limit": 5, "offset": 0})
        r2 = client.get("/api/courses", params={"limit": 5, "offset": 5})
        assert r1.status_code == 200
        assert r2.status_code == 200
        ids1 = [c["id"] for c in r1.json()["data"]]
        ids2 = [c["id"] for c in r2.json()["data"]]
        assert len(set(ids1) & set(ids2)) == 0


class TestSearch:
    def test_search(self, client):
        r = client.get("/api/search", params={"q": "computer"})
        assert r.status_code == 200
        body = r.json()
        assert body["count"] >= 1

    def test_search_empty_query(self, client):
        r = client.get("/api/search", params={"q": ""})
        assert r.status_code == 422

    def test_search_missing_query(self, client):
        r = client.get("/api/search")
        assert r.status_code == 422


class TestAuth:
    def test_no_key_dev_mode(self, client):
        """With API_SECRET_KEY unset/empty, requests pass without a header."""
        r = client.get("/api/health")
        assert r.status_code == 200

    def test_wrong_key_rejected(self, client):
        """When a secret is configured, a wrong key is rejected."""
        original = settings.API_SECRET_KEY
        settings.API_SECRET_KEY = "test-secret"
        try:
            r = client.get("/api/clubs", headers={"X-Api-Key": "wrong-key"})
            assert r.status_code == 401
        finally:
            settings.API_SECRET_KEY = original

    def test_correct_key_accepted(self, client):
        """When a secret is configured, the correct key is accepted."""
        original = settings.API_SECRET_KEY
        settings.API_SECRET_KEY = "test-secret"
        try:
            r = client.get("/api/clubs", headers={"X-Api-Key": "test-secret"})
            assert r.status_code == 200
        finally:
            settings.API_SECRET_KEY = original

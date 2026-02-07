"""Document-type scrapers for pages that become JSONB blobs in university_documents."""

import re

from scrapers.base_scraper import BaseScraper
from config.settings import settings
from utils.logger import logger


class BaseDocumentScraper(BaseScraper):
    slug: str = ""
    doc_title: str = ""

    def parse(self, html: str, url: str) -> list[dict]:
        soup = self.get_soup(html)

        # Extract main content - try common content containers
        content_el = (
            soup.find("main")
            or soup.find("div", class_="content")
            or soup.find("div", class_="container")
            or soup.body
        )

        if not content_el:
            return []

        # Extract structured content: headings and their following text
        sections = []
        current_section = {"title": "Introduction", "content": []}

        for el in content_el.find_all(["h1", "h2", "h3", "h4", "h5", "p", "ul", "ol", "table"]):
            if el.name in ("h1", "h2", "h3", "h4", "h5"):
                if current_section["content"]:
                    sections.append(current_section)
                current_section = {"title": el.get_text(strip=True), "content": []}
            elif el.name == "table":
                rows = []
                for tr in el.find_all("tr"):
                    cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
                    if cells:
                        rows.append(cells)
                if rows:
                    current_section["content"].append({"type": "table", "rows": rows})
            elif el.name in ("ul", "ol"):
                items = [li.get_text(strip=True) for li in el.find_all("li", recursive=False)]
                if items:
                    current_section["content"].append({"type": "list", "items": items})
            else:
                text = el.get_text(strip=True)
                if text:
                    current_section["content"].append(text)

        if current_section["content"]:
            sections.append(current_section)

        # Also extract any PDF links
        pdf_links = []
        for a in content_el.find_all("a", href=True):
            href = a.get("href", "")
            if href.endswith(".pdf"):
                if not href.startswith("http"):
                    href = f"{settings.EWU_BASE_URL}{href}"
                pdf_links.append({"title": a.get_text(strip=True), "url": href})

        content = {"sections": sections}
        if pdf_links:
            content["pdf_links"] = pdf_links

        return [{
            "slug": self.slug,
            "title": self.doc_title,
            "content": content,
            "source_file": f"{self.name}.json",
            "source_url": url,
        }]


class GradingScraper(BaseDocumentScraper):
    name = "grading_doc"
    slug = "grading"
    doc_title = "Grades, Rules and Regulations"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/grades-rules-and-regulations"]


class PoliciesDocScraper(BaseDocumentScraper):
    name = "policies_doc"
    slug = "policies"
    doc_title = "University Policies"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/ewu-policies"]


class RulesScraper(BaseDocumentScraper):
    name = "rules_doc"
    slug = "rules"
    doc_title = "Student Rules and Regulations"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/student-rules-regulation"]


class PaymentScraper(BaseDocumentScraper):
    name = "payment_doc"
    slug = "payment-procedure"
    doc_title = "Payment Procedure"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/payment-procedure"]


class CareerCenterScraper(BaseDocumentScraper):
    name = "career_center_doc"
    slug = "career-counseling"
    doc_title = "Career Counseling Center"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/career-counseling-center"]


class AdmissionProcessScraper(BaseDocumentScraper):
    name = "admission_process_doc"
    slug = "admission-process"
    doc_title = "Admission Process"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_ADMISSION_URL}"]


class AdmissionRequirementsScraper(BaseDocumentScraper):
    name = "admission_requirements_doc"
    slug = "admission-requirements"
    doc_title = "Admission Requirements"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_ADMISSION_URL}"]


class SexualHarassmentScraper(BaseDocumentScraper):
    name = "sexual_harassment_doc"
    slug = "sexual-harassment-policy"
    doc_title = "Sexual Harassment Elimination and Prevention Policy"

    def get_urls(self) -> list[str]:
        return [f"{settings.EWU_BASE_URL}/ewu-sexual-harassment-elimination-and-prevention-policy"]


class FacilitiesScraper(BaseDocumentScraper):
    name = "facilities_doc"
    slug = "facilities"
    doc_title = "University Facilities"

    def get_urls(self) -> list[str]:
        return [
            f"{settings.EWU_BASE_URL}/research-facilities",
            f"{settings.EWU_BASE_URL}/campus-life",
        ]

    def run(self) -> list[dict]:
        """Override to merge content from multiple URLs."""
        logger.info(f"[{self.name}] Starting scrape...")
        all_sections = []
        all_pdfs = []

        for url in self.get_urls():
            html = self.fetch(url)
            if html is None:
                continue
            records = self.parse(html, url)
            if records:
                content = records[0].get("content", {})
                all_sections.extend(content.get("sections", []))
                all_pdfs.extend(content.get("pdf_links", []))

        if not all_sections:
            logger.error(f"[{self.name}] No content found")
            return []

        result = [{
            "slug": self.slug,
            "title": self.doc_title,
            "content": {"sections": all_sections, **({"pdf_links": all_pdfs} if all_pdfs else {})},
            "source_file": f"{self.name}.json",
        }]

        self.save(result)
        logger.info(f"[{self.name}] Scrape complete")
        return result

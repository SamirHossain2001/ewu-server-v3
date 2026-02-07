# EWU Data Inventory

Inventory of all 26 JSON files in `manually_scrapped_data/`.

## Summary

| File | Size | Format | Key Data |
|------|------|--------|----------|
| about_ewu.json | 2.9 KB | Object | history, vision, mission, address, contact |
| academic_council.json | 4.5 KB | Object | chairperson, members list |
| admission_deadlines.json | 6.4 KB | Object | 15 UG + 10 grad program deadlines |
| admission_process.json | 6.9 KB | Object | application steps, post-admission, contacts |
| admission_requirements.json | 5.2 KB | Object | UG/grad requirements, waivers, documents |
| all_available_programs.json | 5.7 KB | Object | 13 department entries with degree listings |
| alumni.json | 4.4 KB | Object | 10 notable alumni with achievements |
| career_counseling_center.json | 2.3 KB | Object | services, programs, contact info |
| clubs.json | 10.8 KB | Object | 22 student clubs with descriptions |
| depts.json | 1.4 KB | Object | 3 faculties + 2 other academic units |
| events_workshops.json | 4.7 KB | Object | 15 events/workshops |
| ewu_board_of_trustees.json | 5.1 KB | Object | chairperson + members list |
| ewu_faculty_complete.json | 3.4 MB | Object | 436 faculty members with full profiles |
| ewu_newsletters_complete.json | 23.6 KB | Object | newsletters archive organized by year |
| ewu_partnerships.json | 10.8 KB | Object | 16 partnerships with collaboration areas |
| ewu_proctor_schedule.json | 4.2 KB | Object | daily proctor schedule, 5 assistant proctors |
| facilites.json | 21.9 KB | Object | campus life, ICS, research, labs |
| grading.json | 2.8 KB | Object | grade scale, special grades |
| helpdesk.json | 4.3 KB | Object | department helpdesks, contact guidelines |
| payment_procedure.json | 2.2 KB | Object | payment modes, bank/online procedures |
| policy.json | 41.0 KB | Object | 12 university policies |
| rules.json | 2.6 KB | Object | conduct rules, misconduct, penalties |
| scholarships_and_financial_aids.json | 6.2 KB | Object | scholarship types, merit criteria, 6 UG program requirements |
| sexual_harassment.json | 2.6 KB | Object | policy, complaint procedure, sanctions |
| syndicate.json | 2.2 KB | Object | chairperson + members |
| tution_fees.json | 9.8 KB | Object | UG/grad/diploma per-credit + detailed fee structures |

## Detailed Structure

### about_ewu.json (2,922 bytes)
- **Top-level keys:** `history`, `vision`, `mission`, `address`, `contact`
- **history:** Founding info (idea, lead_founder, founding_organization, legal_basis)
- **vision/mission:** Arrays of 5 items each
- **address:** street_address, area, city, post_code, country
- **contact:** phone, email, website

### academic_council.json (4,542 bytes)
- **Top-level key:** `academic_council`
- **Structure:** chairperson object + members list

### admission_deadlines.json (6,359 bytes)
- **Top-level keys:** `page_info`, `undergraduate_programs`, `graduate_programs`, `navigation_links`, `summary`
- **undergraduate_programs:** 15 records - Fields: `program`, `department`, `application_deadline`, `admission_test_date`
- **graduate_programs:** 10 records - Fields: same as above
- **summary:** total counts + semester info

### admission_process.json (6,903 bytes)
- **Top-level keys:** `university`, `admission_process`
- **admission_process:** application steps, post-admission procedures, important notes, contacts, registrar

### admission_requirements.json (5,227 bytes)
- **Top-level keys:** `university`, `admission_requirements`
- **admission_requirements:** undergraduate, waivers, foreign_students, graduate, required_documents

### all_available_programs.json (5,686 bytes)
- **Top-level keys:** `university`, `website`, `programs`, `note`
- **programs:** 13 department entries, each with `faculty`, `department`, `degrees[]`
- **degrees:** Each has `level` (Undergraduate/Postgraduate) and `title`

### alumni.json (4,427 bytes)
- **Top-level keys:** `university`, `alumni_portal`, `total_alumni`, `alumni_foundation`, `notable_alumni`, `alumni_network`
- **notable_alumni:** 10 records - Fields: `id`, `name`, `department`, `achievement`, `details`, `year_awarded`

### career_counseling_center.json (2,339 bytes)
- **Top-level keys:** `university_name`, `center_name`, `established_year`, `mission_and_vision`, `core_services_and_programs`, `contact_and_registration`

### clubs.json (10,793 bytes)
- **Top-level keys:** `university`, `department`, `total_clubs`, `source_url`, `last_updated`, `clubs`
- **clubs:** 22 records - Fields: `name`, `url`, `description`, plus variable fields (mission, flagship_events, notable_events, activities)

### depts.json (1,350 bytes)
- **Top-level keys:** `university`, `faculties`, `other_academic_units`, `note`
- **faculties:** 3 entries (Science & Engineering, Business & Economics, Arts & Social Sciences)
- **other_academic_units:** 2 entries (IER, Pharmacy)

### events_workshops.json (4,673 bytes)
- **Top-level keys:** `page_info`, `events_workshops`
- **events_workshops:** 15 records - Fields: `title`, `date`, `description`

### ewu_board_of_trustees.json (5,098 bytes)
- **Top-level key:** `board_of_trustees`
- **Structure:** page_url, last_updated, chairperson, members list, statistics

### ewu_faculty_complete.json (3,428,039 bytes / 3.3 MB)
- **Top-level keys:** `metadata`, `faculty`
- **metadata:** source, total_faculty (436), generated_date
- **faculty:** 436 records - Fields: `faculty_no`, `name`, `position`, `department`, `profile_id`, `profile_url`, `image_url`, `email`
- Each faculty member also has detailed profile data (academic_background, publications, etc.)
- **Note:** Largest file, use targeted reads only

### ewu_newsletters_complete.json (23,583 bytes)
- **Top-level key:** `newsletters`
- **newsletters:** source, last_updated, total_count, by_year (grouped), all_newsletters

### ewu_partnerships.json (10,763 bytes)
- **Top-level keys:** `university`, `country`, `scrape_date`, `partnerships`, `partnership_categories`, `statistics`
- **partnerships:** 16 records - Fields: `id`, `name`, `acronym`, `country`, `type`, `partnership_type`, `areas_of_collaboration`

### ewu_proctor_schedule.json (4,170 bytes)
- **Top-level keys:** `university`, `document_title`, `semester`, `proctor`, `daily_schedule`, `supporting_staff`, `assistant_proctors`
- **daily_schedule:** 5 entries (one per working day)
- **assistant_proctors:** 5 records

### facilites.json (21,863 bytes)
- **Top-level keys:** `university`, `facilities`
- **facilities:** campus_life, ics_services, research_center, engineering_labs, pharmacy_labs

### grading.json (2,759 bytes)
- **Top-level key:** `grading_system`
- **Structure:** title, description, grade_scale, special_grades

### helpdesk.json (4,309 bytes)
- **Top-level keys:** `institution`, `department_helpdesks`, `contact_guidelines`
- **department_helpdesks:** academic_departments + administrative_offices

### payment_procedure.json (2,243 bytes)
- **Top-level keys:** `institution`, `payment_procedure`
- **payment_procedure:** modes, bank_counter_or_booth, online_gateway, adjustment_rules, guidelines

### policy.json (41,010 bytes)
- **Top-level key:** `policies`
- **policies:** 12 records - Fields: `name`, `purpose`, `scope`, `principles`, `key_actions`, `committee_members`

### rules.json (2,557 bytes)
- **Top-level keys:** `university_name`, `general_conduct_rules`, `academic_misconduct`, `social_misconduct`, `health_and_safety_violations`, `academic_status_and_disciplinary_action`

### scholarships_and_financial_aids.json (6,229 bytes)
- **Top-level keys:** `university`, `page_title`, `effective_from`, `annual_scholarship_budget`, `scholarship_types`, `financial_assistance_categories`, `merit_scholarships`, `undergraduate_programs_credit_requirements`
- **undergraduate_programs_credit_requirements:** 6 records with CGPA thresholds
- **merit_scholarships:** admission top scorers, SSC/HSC, district, top 10% criteria

### sexual_harassment.json (2,590 bytes)
- **Top-level keys:** `university_name`, `policy_title`, `stance`, `rules_and_scope`, `complaint_and_investigation_steps`, `punishments_and_sanctions`

### syndicate.json (2,231 bytes)
- **Top-level key:** `syndicate`
- **Structure:** page, chairperson, members list

### tution_fees.json (9,787 bytes)
- **Top-level keys:** `page_info`, `undergraduate_programs`, `graduate_programs`, `diploma_programs`, `fee_categories`
- Each level has `tuition_fees_per_credit` and `detailed_fee_structure` arrays

## Content Gaps

Data not present in existing files but available on the EWU website:

1. **Academic Calendar** (`/academic-calendar`) - Critical, not scraped
2. **Notice Board** (`/notice-board`) - Critical, server-rendered with pagination (~24 pages)
3. **News** (`/news`) - Medium priority
4. **FAQ** (`/faq`) - Medium priority
5. **Withdraw/Retake policies** - Missing from grading.json (noted in Links.md)

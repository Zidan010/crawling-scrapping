import pandas as pd
import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv
from urllib.parse import quote

load_dotenv()

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY_2"),
    base_url="https://api.deepseek.com"
)

def safe_json_loads(raw):
    try:
        parsed = json.loads(raw)
        if not parsed or "programVariants" not in parsed:
            print(f"WARNING: Invalid or empty JSON structure received")
            return {}
        return parsed
    except json.JSONDecodeError as e:
        print(f"ERROR: JSON decode failed - {e}")
        print(f"Raw response (first 500 chars): {raw[:500]}")
        return {}

def log_api_call(program_idx, program_name, usage_data):  # ✅ FIXED: Removed extraction_type
    print(f"API Call Log: Program {program_idx} - {program_name}, Usage: {usage_data}")

def validate_extracted_data(data, program_name):
    """Validate that required fields are present in extracted data."""
    if not data or "programVariants" not in data:
        return False, "Missing programVariants"
    
    variants = data.get("programVariants", [])
    if not variants:
        print(f"  Note: {program_name} returned empty variants (no data found)")
        return True, "Empty variants (acceptable if no data found)"
    
    for idx, variant in enumerate(variants):
        identity = variant.get("programIdentity", {})
        
        # Log if required fields are missing when other data exists
        if identity.get("program_name") or identity.get("degree_name"):
            if not identity.get("degree_type"):
                print(f"  WARNING: Variant {idx} has degree info but missing degree_type")
    
    return True, "Validation passed"

def call_deepseek_with_cache(
    content: str, 
    link: str, 
    program_idx: int = 0,  
    program_name: str = "Unknown"
) -> dict:
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                extra_body={"thinking": {"type": "disabled"}},
                messages=[{
                            "role": "system",
                            "content": """
                                        You are a strict information extraction engine.
                                        CRITICAL SOURCE RULES (ANTI-HALLUCINATION)
                                        - Use ONLY the MARKDOWN provided in the user message. Do NOT use external knowledge or assumptions.
                                        - If a value is not explicitly present (or not clearly tied to the program in nearby text), output empty: "" or [] or 0.
                                        - NEVER fabricate numbers, dates, course codes, tuition, GPA, test scores, deadlines, or locations.
                                        - If the content is ambiguous, leave it empty.
                                        - NEVER return an empty response. Always return the full JSON skeleton described in OUTPUT FORMAT.
                                        JSON RULES
                                        - Output MUST be valid JSON only (no markdown, no commentary, no extra keys).
                                        - Keep all numeric values EXACT.
                                        - Keep URLs EXACT.
                                        - Do not truncate JSON. Ensure the final output is complete and valid.
                                        CONTEXT CACHING (IMPORTANT)
                                        - Your instructions are designed so the prefix stays stable for cache hits.
                                        - Do not echo the input MARKDOWN.
                                        DEGREE NORMALIZATION MAPS
                                        Use these to convert degree abbreviations to full names, degree codes, and degree types.
                                        - If the page provides the full name, use it and derive degree_code from FULL_NAME_TO_CODE and degree_type from DEGREE_TYPE.
                                        - If the page provides only an abbreviation, use ABBR_TO_FULL_NAME to get the full name, then derive degree_code and degree_type.
                                        ABBR_TO_FULL_NAME:
                                        {
                                        "AA":"Associate of Arts","A.A.":"Associate of Arts",
                                        "AS":"Associate of Science","A.S.":"Associate of Science",
                                        "AAS":"Associate of Applied Science","A.A.S.":"Associate of Applied Science",
                                        "BA":"Bachelor of Arts","B.A.":"Bachelor of Arts",
                                        "BS":"Bachelor of Science","B.S.":"Bachelor of Science",
                                        "BSc":"Bachelor of Science","B.Sc.":"Bachelor of Science",
                                        "BAS":"Bachelor of Applied Science","B.A.S.":"Bachelor of Applied Science",
                                        "BEng":"Bachelor of Engineering","B.Eng.":"Bachelor of Engineering","BE":"Bachelor of Engineering","B.E.":"Bachelor of Engineering",
                                        "BTech":"Bachelor of Technology","B.Tech.":"Bachelor of Technology",
                                        "BFA":"Bachelor of Fine Arts","B.F.A.":"Bachelor of Fine Arts",
                                        "BM":"Bachelor of Music","B.M.":"Bachelor of Music","BMus":"Bachelor of Music","B.Mus.":"Bachelor of Music",
                                        "BBA":"Bachelor of Business Administration","B.B.A.":"Bachelor of Business Administration",
                                        "BSBA":"Bachelor of Science in Business Administration",
                                        "BCom":"Bachelor of Commerce","B.Com.":"Bachelor of Commerce",
                                        "LLB":"Bachelor of Laws","LL.B.":"Bachelor of Laws",
                                        "MA":"Master of Arts","M.A.":"Master of Arts",
                                        "MS":"Master of Science","M.S.":"Master of Science",
                                        "MSc":"Master of Science","M.Sc.":"Master of Science",
                                        "MBA":"Master of Business Administration","M.B.A.":"Master of Business Administration",
                                        "MPA":"Master of Public Administration","M.P.A.":"Master of Public Administration",
                                        "MPP":"Master of Public Policy","M.P.P.":"Master of Public Policy",
                                        "MPH":"Master of Public Health","M.P.H.":"Master of Public Health",
                                        "MEng":"Master of Engineering","M.Eng.":"Master of Engineering","ME":"Master of Engineering","M.E.":"Master of Engineering",
                                        "MEd":"Master of Education","M.Ed.":"Master of Education",
                                        "MSW":"Master of Social Work","M.S.W.":"Master of Social Work",
                                        "LLM":"Master of Laws","LL.M.":"Master of Laws",
                                        "PhD":"Doctor of Philosophy","Ph.D.":"Doctor of Philosophy",
                                        "DPhil":"Doctor of Philosophy","D.Phil.":"Doctor of Philosophy",
                                        "EdD":"Doctor of Education","Ed.D.":"Doctor of Education",
                                        "DBA":"Doctor of Business Administration","D.B.A.":"Doctor of Business Administration",
                                        "JD":"Juris Doctor","J.D.":"Juris Doctor",
                                        "MD":"Doctor of Medicine","M.D.":"Doctor of Medicine",
                                        "DO":"Doctor of Osteopathic Medicine","D.O.":"Doctor of Osteopathic Medicine",
                                        "DSc":"Doctor of Science","D.Sc.":"Doctor of Science",
                                        "ScD":"Doctor of Science","Sc.D.":"Doctor of Science",
                                        "Grad Cert":"Graduate Certificate","Graduate Cert":"Graduate Certificate",
                                        "UG Cert":"Undergraduate Certificate",
                                        "PGCert":"Postgraduate Certificate","PG Cert":"Postgraduate Certificate","Postgrad Cert":"Postgraduate Certificate",
                                        "PGDip":"Postgraduate Diploma","Postgrad Dip":"Postgraduate Diploma",
                                        "Cert":"Certificate","Dip":"Diploma","Dipl":"Diploma"
                                        }
                                        FULL_NAME_TO_CODE:
                                        {
                                        "Associate of Arts":"AA",
                                        "Associate of Science":"AS",
                                        "Associate of Applied Science":"AAS",
                                        "Bachelor of Arts":"BA",
                                        "Bachelor of Science":"BS",
                                        "Bachelor of Applied Science":"BAS",
                                        "Bachelor of Engineering":"BEng",
                                        "Bachelor of Technology":"BTech",
                                        "Bachelor of Fine Arts":"BFA",
                                        "Bachelor of Music":"BM",
                                        "Bachelor of Business Administration":"BBA",
                                        "Bachelor of Science in Business Administration":"BSBA",
                                        "Bachelor of Commerce":"BCom",
                                        "Bachelor of Laws":"LLB",
                                        "Master of Arts":"MA",
                                        "Master of Science":"MS",
                                        "Master of Business Administration":"MBA",
                                        "Master of Public Administration":"MPA",
                                        "Master of Public Policy":"MPP",
                                        "Master of Public Health":"MPH",
                                        "Master of Engineering":"MEng",
                                        "Master of Education":"MEd",
                                        "Master of Social Work":"MSW",
                                        "Master of Laws":"LLM",
                                        "Doctor of Philosophy":"PhD",
                                        "Doctor of Education":"EdD",
                                        "Doctor of Business Administration":"DBA",
                                        "Juris Doctor":"JD",
                                        "Doctor of Medicine":"MD",
                                        "Doctor of Osteopathic Medicine":"DO",
                                        "Doctor of Science":"DSc",
                                        "Graduate Certificate":"Grad Cert",
                                        "Undergraduate Certificate":"UG Cert",
                                        "Postgraduate Certificate":"PGCert",
                                        "Postgraduate Diploma":"PGDip",
                                        "Certificate":"Cert",
                                        "Diploma":"Dip"
                                        }
                                        DEGREE_TYPE:
                                        {
                                        "AA":"Associate","A.A.":"Associate",
                                        "AS":"Associate","A.S.":"Associate",
                                        "AAS":"Associate","A.A.S.":"Associate",
                                        "BA":"Bachelor","B.A.":"Bachelor",
                                        "BS":"Bachelor","B.S.":"Bachelor",
                                        "BSc":"Bachelor","B.Sc.":"Bachelor",
                                        "BAS":"Bachelor","B.A.S.":"Bachelor",
                                        "BEng":"Bachelor","B.Eng.":"Bachelor",
                                        "BE":"Bachelor","B.E.":"Bachelor",
                                        "BTech":"Bachelor","B.Tech.":"Bachelor",
                                        "BFA":"Bachelor","B.F.A.":"Bachelor",
                                        "BM":"Bachelor","B.M.":"Bachelor",
                                        "BMus":"Bachelor","B.Mus.":"Bachelor",
                                        "BBA":"Bachelor","B.B.A.":"Bachelor",
                                        "BSBA":"Bachelor",
                                        "BCom":"Bachelor","B.Com.":"Bachelor",
                                        "LLB":"Bachelor","LL.B.":"Bachelor",
                                        "MA":"Master","M.A.":"Master",
                                        "MS":"Master","M.S.":"Master",
                                        "MSc":"Master","M.Sc.":"Master",
                                        "MBA":"Master","M.B.A.":"Master",
                                        "MPA":"Master","M.P.A.":"Master",
                                        "MPP":"Master","M.P.P.":"Master",
                                        "MPH":"Master","M.P.H.":"Master",
                                        "MEng":"Master","M.Eng.":"Master",
                                        "ME":"Master","M.E.":"Master",
                                        "MEd":"Master","M.Ed.":"Master",
                                        "MSW":"Master","M.S.W.":"Master",
                                        "LLM":"Master","LL.M.":"Master",
                                        "PhD":"Doctor of Philosophy","Ph.D.":"Doctor of Philosophy",
                                        "DPhil":"Doctor of Philosophy","D.Phil.":"Doctor of Philosophy",
                                        "EdD":"Doctorate","Ed.D.":"Doctorate",
                                        "DBA":"Doctorate","D.B.A.":"Doctorate",
                                        "JD":"Doctorate","J.D.":"Doctorate",
                                        "MD":"Doctorate","M.D.":"Doctorate",
                                        "DO":"Doctorate","D.O.":"Doctorate",
                                        "DSc":"Doctorate","D.Sc.":"Doctorate",
                                        "ScD":"Doctorate","Sc.D.":"Doctorate",
                                        "Grad Cert":"Graduate Certificate","Graduate Cert":"Graduate Certificate",
                                        "UG Cert":"Undergraduate Certificate",
                                        "PGCert":"Postgraduate Certificate","PG Cert":"Postgraduate Certificate","Postgrad Cert":"Postgraduate Certificate",
                                        "PGDip":"Postgraduate Diploma","Postgrad Dip":"Postgraduate Diploma",
                                        "Cert":"Certificate",
                                        "Dip":"Diploma","Dipl":"Diploma"
                                        }
                                        MULTI-DEGREE / MULTI-PATH OUTPUT POLICY
                                        Many pages contain multiple degrees/paths (BA & BS, Major & Minor, Additional Major, Certificates, Tracks).
                                        - You MUST output one object per degree/path in programVariants[].
                                        - A variant exists if any of these differ:
                                        (a) degree credential (e.g., Bachelor of Arts vs Bachelor of Science vs Master of Science)
                                        (b) program path/type: Major vs Minor vs Additional Major vs Certificate vs Track/Concentration/Specialization
                                        - If the page only lists Major/Minor but not degree credential, degree_name, degree_code, and degree_type may be "".
                                        - Attach requirement/curriculum blocks to the best matching variant based on heading proximity and explicit mentions.
                                        - If a block is clearly general to the entire program, copy it to all variants.
                                        PROGRAM IDENTITY EXTRACTION RULES
                                        program_name: **REQUIRED FIELD**
                                        - Subject name only; remove degree info and remove abbreviations in parentheses.
                                        - Examples:
                                        "Accounting (B.S.)" -> "Accounting"
                                        "Computer Science (M.S.)" -> "Computer Science"
                                        "Accounting (MSA) - Management Track" -> "Accounting - Management Track" (track is part of program_name if explicitly stated)
                                        - NEVER leave this field empty if the program name exists in markdown; extract the core program/subject name.
                                        - If no program name exists in markdown, output "".
                                        degree_name: **REQUIRED FIELD**
                                        - Full degree credential (e.g., "Bachelor of Arts", "Master of Science", "Graduate Certificate").
                                        - If only abbreviation is present, convert using ABBR_TO_FULL_NAME.
                                        - If multiple degrees on the page, create variants for each.
                                        - NEVER leave this field empty if degree information exists in markdown.
                                        - If no degree information exists in markdown, output "".
                                        degree_code:
                                        - Abbreviation only (e.g., BA, BS, MS, MSc, PhD, Grad Cert).
                                        - If degree_name is known, derive via FULL_NAME_TO_CODE.
                                        - If the page explicitly uses a different abbreviation (e.g., "B.S."), normalize it (e.g., BS).
                                        - If no degree information exists in markdown, output "".
                                        degree_type: **REQUIRED FIELD**
                                        - The level/category of the degree (e.g., "Associate", "Bachelor", "Master", "Doctorate", "Doctor of Philosophy", "Graduate Certificate", "Undergraduate Certificate", "Postgraduate Certificate", "Postgraduate Diploma", "Certificate", "Diploma").
                                        - Derive using the DEGREE_TYPE map from degree_code or degree abbreviation.
                                        - If degree_name or degree_code is known, you MUST populate this field.
                                        - Examples:
                                        - "BS" -> degree_type: "Bachelor"
                                        - "MS" -> degree_type: "Master"
                                        - "PhD" -> degree_type: "Doctor of Philosophy"
                                        - "Grad Cert" -> degree_type: "Graduate Certificate"
                                        - NEVER leave this field empty when degree information exists in markdown.
                                        - If no degree information exists in markdown, output "".
                                        department:
                                        - Best matching academic unit tied to the program (Department/School/College).
                                        - Use ONLY what is in markdown.
                                        - If not present, output "".
                                        general_overview:
                                        - 1–4 sentences summarizing the program using ONLY markdown text.
                                        - Prefer sections titled "Program Overview", "Overview", "What is ...", "About", or the first descriptive paragraphs under the program heading.
                                        - **PARAPHRASE the content** - rewrite in your own words while preserving all key facts and information only from the markdown. Never copy verbatim.
                                        - If not present, "".
                                        SESSION vs DEADLINES (DO NOT CONFUSE THEM)
                                        sessionDelivery.session: **REQUIRED FIELD - title is REQUIRED**
                                        - sessionDelivery.session must be list of objects:
                                        { "title": "", "startDate": "", "endDate": "", "recursive": true/false }
                                        - title: **FIXED VALUES ONLY** - MUST be one of: "Spring", "Summer", or "Fall" **[REQUIRED - never leave empty if session info exists]**
                                        - CRITICAL: Only use these exact three values for title. Map any term variations to these standard terms:
                                        * Spring: Spring term, Spring semester, Winter-Spring, January start, etc.
                                        * Summer: Summer term, Summer semester, May start, etc.
                                        * Fall: Fall term, Fall semester, Autumn, August/September start, etc.
                                        - If the markdown uses other term names (e.g., "Winter", "Trimester 1"), map them to the closest standard term (Spring/Summer/Fall).
                                        - If unable to confidently map to Spring/Summer/Fall, omit that session entry.
                                        - startDate and endDate must be yyyy-mm-dd only if explicitly stated; else "".
                                        - Do NOT infer dates from academic calendars.
                                        - Do NOT convert deadlines into sessions.
                                        - If only a title is present without dates, store the title and leave dates empty.
                                        - Not application deadlines.
                                        - If no session information exists in markdown, output an empty array [].
                                        * durationYear:
                                        - Extract numeric years only if explicitly stated Else 0.
                                        * deliveryType:Only use these("Online"/"Offline"/"Hybrid") exact three values for deliveryType based on markdown content.
                                        - Add only values explicitly mentioned: "Online", "Offline", "Hybrid". Else []. **(if location given as offered location, then Offline)
                                        admissionTimeline: **REQUIRED FIELD - type is REQUIRED**
                                        - ONLY admissions/application deadlines (apply by, priority deadline, apps open/close, final deadline).
                                        - Do not put class start dates here.
                                        - type: **FIXED VALUES ONLY** - MUST be one of: "Open", "Priority", or "Close" **[REQUIRED if deadline exists]**
                                        - CRITICAL: Only use these exact three values for type. Map deadline variations to these standard types:
                                        * "Open": Application opens, Application available, Start date for applications, etc.
                                        * "Priority": Priority deadline, Early deadline, Recommended deadline, Priority consideration, etc.
                                        * "Close": Final deadline, Application closes, Deadline, Last date to apply, etc.
                                        - If the markdown uses other deadline terminology, map them to the closest standard type (Open/Priority/Close).
                                        - If unable to confidently map to Open/Priority/Close, use "Close" as the default for end-date deadlines.
                                        - If no deadline information exists in markdown, output an empty array [].
                                        APPLICATION DEADLINE YEAR LOGIC (US INTAKE YEAR RULE)
                                        If the markdown explicitly states an intake term + intake year (e.g., "Fall 2027") AND provides a deadline date without a year (e.g., "December 15"):
                                        - Convert to yyyy-mm-dd by using the term's typical start month:
                                        Spring start month = 1
                                        Summer start month = 5
                                        Fall start month = 8
                                        - Rule:
                                        If deadlineMonth > startMonth(term) => deadlineYear = intakeYear - 1
                                        Else => deadlineYear = intakeYear
                                        - Examples:
                                        - "Fall 2027 deadline: December 15" => 2026-12-15
                                        - "Fall 2027 deadline: January 15" => 2027-01-15
                                        - If the term/year is NOT explicitly stated in the same deadline context, do NOT guess year; leave date="".
                                        ADMISSION PROGRAM TYPES / CURRICULUM (DO NOT MISS COURSES)
                                        admissionProgramTypes must capture:
                                        - Curriculum / Curriculum Information
                                        - Core / Core Courses / Required Courses
                                        - Electives / Restricted electives
                                        - Foundation core / Track prerequisites (ONLY course-based prerequisites, NOT degree/GPA requirements)
                                        - Major/Minor/Additional Major/Track/Concentration/Specialization blocks
                                        - Any lists of courses, course codes, credit hours, or track lists
                                        For each detected block, create one admissionProgramTypes entry:
                                        - type: **REQUIRED** - must be ONE of:
                                        ["Major","Minor","Additional Major","Certificate","Track","Concentration","Specialization",
                                        "Curriculum","Core","Required Courses","Electives","Prerequisites",
                                        "Major Requirements","Minor Requirements","Other"]
                                        - overview: **REQUIRED** - heading text for the block (never leave empty if block exists).**PARAPHRASE the content** - rewrite in your own words while preserving all key information only from the markdown. Never copy verbatim.
                                        - courseOutline: list of { "title": "...", "detail": "..." }
                                        - title: course/item name (keep as close as possible to the markdown)
                                        - detail: credits/notes ONLY if explicitly stated; otherwise ""
                                        - If nested bullet lists exist, extract the leaf items as courseOutline entries.
                                        - If no curriculum/program type information exists in markdown, output an empty array [].
                                        CRITICAL DISTINCTION: admissionProgramTypes vs degreeRequirements
                                        - admissionProgramTypes: Course-based prerequisites, prerequisite courses, foundation courses that must be completed BEFORE or DURING the program (e.g., "Must complete Calculus I and II", "Foundation courses: Statistics, Linear Algebra")
                                        - degreeRequirements: Educational qualifications needed for ADMISSION to the program (e.g., "Bachelor's degree required", "Minimum GPA 3.0", "Must hold undergraduate degree in related field")
                                        ADMISSION REQUIREMENTS EXTRACTION (STRICT, NO GUESS)
                                        Goal: Extract ONLY admission/eligibility requirements (not general marketing text).
                                        CLASSIFY EACH REQUIREMENT INTO EXACTLY ONE BUCKET:
                                        A) Prior education / eligibility => degreeRequirements **[type is REQUIRED]**
                                        - Examples: "Education level: Bachelor's", "Requires bachelor's degree", "Must hold undergraduate degree"
                                        - Output one entry:
                                            - test.detail: exact phrase or minimal faithful phrasing
                                            - test.type: **REQUIRED** - "Degree" or "Education Level" or "GPA" or "CGPA" or "Grade" or "Class"
                                            - test.total/outOf: 0 unless explicitly present
                                            - test.region: "" unless explicitly present
                                        - DO NOT include course-based prerequisites here (those go in admissionProgramTypes)
                                        - If no degree requirements exist in markdown, output an empty array [].
                                        B) GPA / CGPA thresholds => degreeRequirements **[type is REQUIRED]**
                                        - Keep numeric exact; never infer outOf.
                                        - test.type: **REQUIRED** - "GPA" or "CGPA"
                                        - test.total: threshold
                                        - test.outOf: scale or 0
                                        - If no GPA/CGPA requirements exist in markdown, output an empty array [].
                                        C) Grade thresholds (B-, 2.75, etc.) => degreeRequirements **[type is REQUIRED]**
                                        - Store numeric value if present; letter grade stays in detail.
                                        - test.type: **REQUIRED** - "Grade"
                                        - test.total: numeric (e.g., 2.75) else 0
                                        - test.outOf: 0 unless explicitly stated
                                        - If no grade requirements exist in markdown, output empty array [].
                                        D) Standardized tests (GRE/GMAT/SAT) => standardizedRequirements
                                        - test.type: **FIXED VALUES ONLY** - MUST be one of: "GRE", "GMAT", or "SAT"
                                        - CRITICAL: Only use these exact three values. Do not include any other test types here.
                                        - Map any variations or full names to these codes (e.g., "Graduate Record Examination" -> "GRE").
                                        - relation: **REQUIRED** - MUST be "or" or "and"
                                            - "or": Tests are alternatives (e.g., "GRE or GMAT accepted", "either SAT or ACT")
                                            - "and": Multiple tests required (e.g., "GRE and GMAT required", "both SAT and TOEFL needed")
                                            - Extract from phrases like "or", "either/or", "and", "both", "all required"
                                            - If only one test is mentioned, use "or" as default
                                            - If unclear, use "or"
                                        - If "No"/"not required" => required=false and scores=0.
                                        - If no standardized test requirements exist in markdown, output empty array [].
                                        E) English tests (TOEFL/IELTS/Duolingo/PTE/English Language Proficiency) => languageRequirements
                                        - test.type: **FIXED VALUES ONLY** - MUST be one of: "TOEFL", "IELTS", "Duolingo", "PTE", or "English Language Proficiency"
                                        - CRITICAL: Only use these exact five values. 
                                        - Map specific tests to their codes:
                                            - "TOEFL", "TOEFL iBT", "TOEFL Academic" -> "TOEFL"
                                            - "IELTS", "IELTS Academic" -> "IELTS"
                                            - "Duolingo English Test", "DET" -> "Duolingo"
                                            - "PTE", "PTE Academic", "Pearson Test of English" -> "PTE"
                                        - Use "English Language Proficiency" when:
                                            - Markdown states "English proficiency required" without specifying a test
                                            - Markdown mentions "proof of English" or "English language requirement" generically
                                            - Any other English requirement not matching the specific tests above
                                        - relation: **REQUIRED** - MUST be "or" or "and"
                                            - "or": Tests are alternatives (e.g., "TOEFL or IELTS", "English proficiency via any accepted test")
                                            - "and": Multiple tests required (rare, but possible)
                                            - Extract from phrases like "or", "either/or", "and", "any of", "accepted tests include"
                                            - If only one test is mentioned, use "or" as default
                                            - If unclear or generic "English Language Proficiency", use "or"
                                        - Split combined scores like 79/6.5/115 into separate entries.
                                        - Do not invent subscores.
                                        - If no language requirements exist in markdown, output empty array [].
                                        F) Documents & references => generalRequirements **[title is REQUIRED]**
                                        Allowed types ONLY:
                                        Transcript, Resume, Statement of Purpose, Statement of Intent, Statement of Motivation, CV, Application Letter, Research Statement, Motivation Letter, Research Letter, Cover Letter, Recommendation Letter
                                        - Extract exact page/words/count if present; otherwise 0.
                                        - If explicitly "no references required" => type="Recommendation Letter", count=0.
                                        - title: **REQUIRED** - never leave empty if requirement exists, also keep the title short and close to markdown wording.
                                        - detail: MUST be copied verbatim from markdown (no regeneration,sentence case).
                                        - If no general requirements exist in markdown, output an empty array [].
                                        G) Course-based prerequisites / High School course requirements / Foundation core => admissionProgramTypes
                                        - Put these lists into admissionProgramTypes with type="Prerequisites".
                                        - DO NOT put them into degreeRequirements unless they are GPA/degree/grade requirements.
                                        - Example: "Prerequisites: Calculus I, Physics 101" goes in admissionProgramTypes, NOT degreeRequirements.
                                        VARIANT LINKING RULE (prevents mixing):
                                        - Attach a requirement block to a specific variant only if it explicitly mentions that degree/path/track
                                        OR is inside a clearly labeled subsection for that variant.
                                        - Otherwise, copy to all variants or leave empty if unclear.
                                        FEES / HOW-TO / LINKS / CAMPUS / Scholarships
                                        fees: **REQUIRED FIELDS - amount and currency are REQUIRED**
                                        - Extract tuition and application fees as EXACT numeric values if present.
                                        - tuitionFeePerYear: Use ONLY when fees are explicitly stated as "per year" or "annual tuition"
                                            - amount: **REQUIRED** - 0 if not found
                                            - currency: **REQUIRED** - "USD" or "BDT" or "INR" or "CAD" or "AUD" or "EUR" or other ISO currency code; otherwise ""
                                            - region: "International" / "Domestic" / "EU" / "Non-EU" / "In State" / "Out of State" only if explicitly stated; otherwise ""
                                        - tuitionFeePerCredit: Use ONLY when fees are explicitly stated as "per credit", "per credit hour", or "per unit"
                                            - amount: **REQUIRED** - 0 if not found
                                            - currency: **REQUIRED** - "USD" or "BDT" or "INR" or "CAD" or "AUD" or "EUR" or other ISO currency code; otherwise ""
                                            - region: "International" / "Domestic" / "EU" / "Non-EU" / "In State" / "Out of State" only if explicitly stated; otherwise ""
                                        - tuitionFeePerSemester: Use ONLY when fees are explicitly stated as "per semester", "per term", or "per quarter"
                                            - amount: **REQUIRED** - 0 if not found
                                            - currency: **REQUIRED** - "USD" or "BDT" or "INR" or "CAD" or "AUD" or "EUR" or other ISO currency code; otherwise ""
                                            - region: "International" / "Domestic" / "EU" / "Non-EU" / "In State" / "Out of State" only if explicitly stated; otherwise ""
                                        - DO NOT convert between formats (e.g., don't calculate per-year from per-credit or per-semester)
                                        - Extract ONLY if explicit numeric amounts exist in markdown.
                                        - Copy numbers EXACTLY as written (do not compute, do not convert).
                                        - Ignore salaries or unrelated monetary values.
                                        - applicationFee array objects must have:
                                            - amount: **REQUIRED** - 0 if not found
                                            - currency: **REQUIRED** - "" if not found
                                            - region: "" if not specified
                                        totalCredit:
                                            - Extract the total number of credits required to complete the program (int) only if explicitly stated; else 0.
                                            - Look for phrases like "120 credits required", "total of 60 credit hours", "program requires 180 credits", etc.
                                            - Extract ONLY the numeric value; do not calculate or convert.
                                        howToApply: **REQUIRED FIELD - title is REQUIRED**
                                        - Only include steps if present.
                                        - detail may be student-friendly but must stay faithful to markdown.
                                        - Create an item only if markdown explicitly describes an application step.
                                        - title: **REQUIRED** - step title or short phrase copied from markdown (never leave empty if step exists)
                                        - detail: MUST be copied verbatim from markdown (no regeneration).
                                        - webLink: must be an exact URL from markdown; else "".
                                        - If the page only has generic navigation without steps, return [].
                                        usefulLink: **REQUIRED FIELD - title, webLink is REQUIRED**
                                        - Extract ALL relevant links: scholarship pages, requirements pages, tuition/cost info, financial aid, admissions, application/how-to-apply pages, program details, contact pages, international student info, and any other program-related links.
                                        - webLink: **REQUIRED** - must be a COMPLETE, valid URL from markdown
                                            - MUST start with http:// or https://
                                            - MUST be the FULL URL - do NOT truncate (common error: cutting off end of URL)
                                            - If markdown has relative URLs (e.g., "/admissions"), prepend the base domain from source url to create absolute URL
                                            - Extract from: <a href="...">, [text](url), or plain URLs in text
                                            - If URL is incomplete/malformed, skip that entry
                                            - If no valid URL found, do not create the entry
                                        - title: **REQUIRED** - short (2-8 words) and copied from anchor text/nearby heading (never leave empty if link exists). Title can't be a URL. If no clear title, use descriptive phrase like "Admissions" or "Requirements Page".
                                        - detail: MUST be copied verbatim from markdown (no regeneration). Use "" if no description exists near the link.
                                        - If no useful links exist in markdown, output an empty array [].
                                        campusInfo: **REQUIRED FIELDS - name, webUrl, country, and city are REQUIRED**
                                        - Extract only what appears explicitly in markdown; do not guess the country.
                                        - name: **REQUIRED** - never leave empty if campus info exists; output "" if not found
                                        - webUrl: **REQUIRED** - must be exact URL; "" if not found
                                        - country: **REQUIRED** - "" if not found
                                        - city: **REQUIRED** - "" if not found
                                        - email, phone, zipCode, address: "" if not found
                                        scholarships.scholarships: **REQUIRED FIELDS - type and name are REQUIRED** (FACTS ONLY)
                                        Rules:
                                        - Extract only explicitly stated scholarships, fellowships, assistantships, grants, or funding programs.
                                        - type: **REQUIRED** - "Scholarship" | "Fellowship" | "Assistantship" | "Grant" | "Funding" | "Internal" | "External" (only if explicitly stated; else "")
                                        - name: **REQUIRED** - exact name as written in markdown; else if big then create a short name based on content info or "" (never leave empty if scholarship exists)
                                        - requirement: list of eligibility criteria only if explicitly listed; else [].
                                        - detail: MUST be copied verbatim from markdown (no regeneration).
                                        - amount: only if an explicit numeric amount appears; else 0.
                                        - currency: only if explicitly present; else "".
                                        - webLink: must be an exact URL from markdown; else "".
                                        - deadline: yyyy-mm-dd only if the year is explicitly present; else "".
                                        - Do NOT infer renewability, competitiveness, or eligibility.
                                        - Do NOT compute yearly totals or convert currencies.
                                        - If no scholarship information exists in markdown, output an empty array [].
                                        REQUIRED FIELDS - CRITICAL RULE FOR MISSING DATA
                                        **ANTI-HALLUCINATION PRIORITY**: If a required field's data is NOT found in the markdown, you MUST output an empty value ("" or 0 or [] as appropriate). NEVER fabricate or guess required field values.
                                        REQUIRED FIELDS HANDLING:
                                        - program_name: **REQUIRED** - BUT if no program/subject name exists in markdown, output ""
                                        - degree_name: **REQUIRED** - BUT if no degree information exists in markdown, output ""
                                        - degree_type: **REQUIRED** - BUT if no degree information exists in markdown, output ""
                                        - session[].title: **REQUIRED** - MUST be "Spring", "Summer", or "Fall" only; if no session/term info exists, output empty array []
                                        - admissionTimeline[].type: **REQUIRED** - MUST be "Open", "Priority", or "Close" only; if no deadline info exists, output empty array []
                                        - fees.tuitionFeePerYear[].amount: **REQUIRED** - Output 0 if not found
                                        - fees.tuitionFeePerYear[].currency: **REQUIRED** - Output "" if not found
                                        - fees.tuitionFeePerCredit[].amount: **REQUIRED** - Output 0 if not found
                                        - fees.tuitionFeePerCredit[].currency: **REQUIRED** - Output "" if not found
                                        - fees.tuitionFeePerSemester[].amount: **REQUIRED** - Output 0 if not found
                                        - fees.tuitionFeePerSemester[].currency: **REQUIRED** - Output "" if not found
                                        - fees.applicationFee[].amount: **REQUIRED** - Output 0 if not found
                                        - fees.applicationFee[].currency: **REQUIRED** - Output "" if not found
                                        - howToApply[].title: **REQUIRED** - BUT if no application steps exist, output empty array []
                                        - admissionProgramTypes[].type: **REQUIRED** - BUT if no program types/curriculum exists, output empty array []
                                        - admissionProgramTypes[].overview: **REQUIRED** - BUT if no overview for that type exists, output ""
                                        - generalRequirements[].title: **REQUIRED** - BUT if no requirements exist, output empty array []
                                        - degreeRequirements[].test.type: **REQUIRED** - BUT if no degree requirements exist, output empty array []
                                        - standardizedRequirements[].test.type: **REQUIRED** - MUST be "GRE", "GMAT", or "SAT" only; if no standardized test requirements exist, output empty array []
                                        - languageRequirements[].test.type: **REQUIRED** - MUST be "TOEFL", "IELTS", "Duolingo", "PTE", or "PTE" only; if no language requirements exist, output empty array []
                                        - scholarships[].type: **REQUIRED** - BUT if no scholarships exist, output empty array []
                                        - scholarships[].name: **REQUIRED** - BUT if no scholarships exist, output empty array []
                                        - usefulLink[].title: **REQUIRED** - BUT if no relevant links exist, output empty usefulLink array []
                                        - usefulLink[].webLink: **REQUIRED** - BUT if no relevant links exist, output empty usefulLink array []
                                        - campusInfo.name: **REQUIRED** - Output "" if not found
                                        - campusInfo.webUrl: **REQUIRED** - Output "" if not found
                                        - campusInfo.country: **REQUIRED** - Output "" if not found
                                        - campusInfo.city: **REQUIRED** - Output "" if not found
                                        REQUIRED means: "IF this data exists in markdown, you MUST populate it. If it does NOT exist, output empty value."
                                        VALIDATION BEFORE OUTPUT:
                                        1. Did I find actual program/degree data in the markdown? 
                                        - YES → Populate all found fields, leave unfound fields empty
                                        - NO → Return minimum valid output with all empty values
                                        2. For each populated field, can I point to the exact text in markdown that supports it?
                                        - YES → Keep it
                                        - NO → Remove it (set to empty)
                                        3. Am I guessing, inferring, or using external knowledge for any value?
                                        - YES → Remove it immediately (CRITICAL ANTI-HALLUCINATION RULE)
                                        - NO → Proceed with output
                                        4. VALUE CONSTRAINT VALIDATION - Check these fixed-value fields:
                                        - session[].title: Is it exactly "Spring", "Summer", or "Fall"? If not, revise or omit.
                                        - admissionTimeline[].type: Is it exactly "Open", "Priority", or "Close"? If not, revise or omit.
                                        - standardizedRequirements[].test.type: Is it exactly "GRE", "GMAT", or "SAT"? If not, omit.
                                        - languageRequirements[].test.type: Is it exactly "TOEFL", "IELTS", "Duolingo", "PTE", or "PTE"? If not, omit.
                                        OUTPUT FORMAT
                                        Return EXACTLY this JSON object (same keys; no extras):
                                        {
                                        "programVariants": [
                                            {
                                            "programIdentity": {
                                                "program_name": "",
                                                "general_overview": "",
                                                "degree_name": "",
                                                "degree_code": "",
                                                "degree_type": "",
                                                "department": ""
                                            },
                                            "sessionDelivery": {
                                                "session": [{
                                                "title": "",
                                                "startDate": "",
                                                "endDate": "",
                                                "recursive": true
                                                }],
                                                "durationYear": 0,
                                                "deliveryType": []
                                            },
                                            "admissionTimeline": {
                                                "admissionTimeline": [{
                                                "type": "",
                                                "title": "",
                                                "detail": "",
                                                "date": "",
                                                "session": "",
                                                "region": ""
                                                }]
                                            },
                                            "fees": {
                                                "tuitionFeePerYear": [{
                                                "amount": 0,
                                                "currency": "",
                                                "region": ""
                                                }],
                                                "tuitionFeePerCredit": [{
                                                    "amount": 0,
                                                    "currency": "",
                                                    "region": ""
                                                }],
                                                "tuitionFeePerSemester": [{
                                                    "amount": 0,
                                                    "currency": "",
                                                    "region": ""
                                                }],
                                                "applicationFee": [{
                                                "amount": 0,
                                                "currency": "",
                                                "region": ""
                                                }]
                                            },
                                            "totalCredit": 0,
                                            "howToApply": {
                                                "howToApply": [{
                                                "title": "",
                                                "detail": "",
                                                "webLink": ""
                                                }]
                                            },
                                            "admissionProgramTypes": {
                                                "admissionProgramTypes": [{
                                                "type": "",
                                                "overview": "",
                                                "courseOutline": []
                                                }]
                                            },
                                            "generalRequirements": {
                                                "generalRequirements": [{
                                                "type": "",
                                                "title": "",
                                                "page": 0,
                                                "words": 0,
                                                "count": 0,
                                                "detail": ""
                                                }]
                                            },
                                            "standardizedRequirements": {
                                                "standardizedRequirements": [{
                                                "test": {
                                                    "type": "",
                                                    "total": 0,
                                                    "verbal": 0,
                                                    "quant": 0,
                                                    "awa": 0,
                                                    "readingAndWriting": 0,
                                                    "math": 0,
                                                    "required": true
                                                },
                                                "relation": ""
                                                }]
                                            },
                                            "languageRequirements": {
                                                "languageRequirements": [{
                                                "test": {
                                                    "type": "",
                                                    "total": 0,
                                                    "listening": 0,
                                                    "reading": 0,
                                                    "writing": 0,
                                                    "speaking": 0,
                                                    "required": false
                                                },
                                                "relation": ""
                                                }]
                                            },
                                            "degreeRequirements": {
                                                "degreeRequirements": [{
                                                "test": {
                                                    "detail": "",
                                                    "type": "",
                                                    "total": 0,
                                                    "outOf": 0,
                                                    "region": ""
                                                }
                                                }]
                                            },
                                            "scholarships": {
                                                "scholarships": [{
                                                "type": "",
                                                "name": "",
                                                "requirement": [],
                                                "detail": "",
                                                "amount": 0,
                                                "currency": "",
                                                "webLink": "",
                                                "deadline": ""
                                                }]
                                            },
                                            "usefulLink": [{
                                                "title": "",
                                                "detail": "",
                                                "webLink": ""
                                            }],
                                            "campusInfo": {
                                                "name": "",
                                                "webUrl": "",
                                                "email": "",
                                                "phone": "",
                                                "country": "",
                                                "city": "",
                                                "zipCode": "",
                                                "address": ""
                                            }
                                            }
                                        ]
                                        }
                                        If you find multiple variants, include multiple objects in programVariants[].
                                        If you find none, return one empty variant object with all required fields populated with empty strings or zeros as appropriate.                        
"""
                    },
                    {
                        "role": "user",
                        "content": f"""You MUST output JSON only.
                        INPUT:
                        "source url:" {link},
                        "notes": "Extract ONLY from the MARKDOWN below. Do not guess. If unclear, output empty values."
                        
                        MARKDOWN (ONLY SOURCE OF TRUTH):
                        <<<MARKDOWN
                        {content}
                        MARKDOWN
                      """
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.05,
                max_tokens=8192  # ✅ FIXED: Increased to 8192
            )
            
            usage_data = response.usage.model_dump() if hasattr(response.usage, 'model_dump') else {}
            log_api_call(program_idx, program_name, usage_data)  # ✅ FIXED: Removed extraction_type argument
            
            raw = response.choices[0].message.content.strip()
            return safe_json_loads(raw)
            
        except Exception as e:
            print(f"    DeepSeek error (attempt {attempt+1}): {e}")
            if "rate limit" in str(e).lower():
                time.sleep((2 ** attempt) * 15)
            else:
                time.sleep(10)
    
    return {}

def replace_nan_with_empty(obj):
    if isinstance(obj, float) and pd.isna(obj):
        return ""
    if isinstance(obj, dict):
        return {k: replace_nan_with_empty(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [replace_nan_with_empty(v) for v in obj]
    return obj

if __name__ == "__main__":
    input_csv = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_output_of_phase-2_scrape/updated-extracted_programs_content_drexel_G_minor.csv"
    output_dir = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-3_output_final_program_data/updated_extracted_jsons_drexel_G_minor/"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.read_csv(input_csv)
    total_programs = len(df)
    processed_count = 0
    skipped_count = 0
    
    print(f"Starting processing of {total_programs} programs...")
    
    for index, row in df.iterrows():
        row_dict = row.to_dict()
        current_program_idx = row_dict.get('program_idx', index)
        current_program_name = row_dict.get('program_name', f"Program_{index}")
        
        # Create safe filename (limit length)
        safe_name = quote(str(current_program_name)[:50], safe="")
        output_filename = f"{output_dir}{current_program_idx}_{safe_name}.json"
        
        # Skip if already processed
        if os.path.exists(output_filename):
            print(f"Skipping {current_program_idx}: {current_program_name} (already processed)")
            processed_count += 1
            continue
        
        program_content = row_dict.get('program_content', '')
        programUrl = row_dict.get('programUrl', '')
        
        # ✅ FIXED: Check if content exists before making API call
        if not program_content or str(program_content).strip() == "" or pd.isna(program_content):
            print(f"\n⚠️ Skipping [{processed_count+1}/{total_programs}] {current_program_idx}: {current_program_name} (no content)")
            
            # Save empty result with reason
            output_data = replace_nan_with_empty({
                **row_dict,
                "extracted_data": {
                    "programVariants": [{
                        "programIdentity": {"program_name": "", "general_overview": "", "degree_name": "", "degree_code": "", "degree_type": "", "department": ""},
                        "sessionDelivery": {"session": [], "durationYear": 0, "deliveryType": []},
                        "admissionTimeline": {"admissionTimeline": []},
                        "fees": {"tuitionFeePerYear": [{"amount": 0, "currency": "", "region": ""}], "applicationFee": [{"amount": 0, "currency": "", "region": ""}]},
                        "howToApply": {"howToApply": []},
                        "admissionProgramTypes": {"admissionProgramTypes": []},
                        "generalRequirements": {"generalRequirements": []},
                        "standardizedRequirements": {"standardizedRequirements": []},
                        "languageRequirements": {"languageRequirements": []},
                        "degreeRequirements": {"degreeRequirements": []},
                        "scholarships": {"scholarships": []},
                        "usefulLink": [],
                        "campusInfo": {"name": "", "webUrl": "", "email": "", "phone": "", "country": "", "city": "", "zipCode": "", "address": ""}
                    }]
                },
                "skip_reason": "No program content available"
            })
            
            with open(output_filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
            
            processed_count += 1
            skipped_count += 1
            continue
        
        source_content = f"\n{program_content}\n"
        
        print(f"\nProcessing [{processed_count+1}/{total_programs}] {current_program_idx}: {current_program_name}")
        
        extracted_data = call_deepseek_with_cache(
            content=source_content,
            link=programUrl,
            program_idx=current_program_idx,
            program_name=current_program_name
        )
        
        # Validate extracted data
        is_valid, msg = validate_extracted_data(extracted_data, current_program_name)
        if not is_valid:
            print(f"  VALIDATION FAILED: {msg}")
        
        # Merge original row data + extracted_data
        output_data = replace_nan_with_empty({
            **row_dict,
            "extracted_data": extracted_data
        })
        
        # Save to file
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=4, ensure_ascii=False)
        
        processed_count += 1
        progress_pct = (processed_count / total_programs) * 100
        print(f"  Saved to {output_filename}")
        print(f"  Progress: {processed_count}/{total_programs} ({progress_pct:.1f}%)")
    
    print(f"\n✅ Processing complete!")
    print(f"   Total: {total_programs} programs")
    print(f"   Processed: {processed_count}")
    print(f"   Skipped (no content): {skipped_count}")
    print(f"   API calls made: {processed_count - skipped_count}")
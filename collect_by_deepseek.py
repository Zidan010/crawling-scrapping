import csv
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables")

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# ----------------------------- DEGREE MAPPING ---------------------------
DEGREE_CODE_MAPPING = {
    "master of science": "MSc", "masters of science": "MSc", "ms": "MSc", "m.s.": "MSc",
    "master of engineering": "ME", "masters of engineering": "ME", "meng": "ME",
    "master of arts": "MA", "masters of arts": "MA", "ma": "MA",
    "bachelor of science": "BSc", "bachelors of science": "BSc", "bs": "BSc",
    "bachelor of arts": "BA", "bachelors of arts": "BA", "ba": "BA",
    "doctor of philosophy": "PhD", "phd": "PhD", "ph.d.": "PhD",
    "master of accounting": "M.Acct", "macct": "M.Acct"
}

DEGREE_TYPE_MAPPING = {
    "master": "Master", "masters": "Master", "ms": "Master", "msc": "Master",
    "ma": "Master", "me": "Master", "meng": "Master", "macct": "Master",
    "bachelor": "Bachelor", "bachelors": "Bachelor", "bs": "Bachelor", "bsc": "Bachelor",
    "ba": "Bachelor", "phd": "Doctor of Philosophy", "doctor": "Doctor of Philosophy",
    "diploma": "Diploma", "certificate": "Certificate",
}

def map_degree_code(degree_name: str) -> str:
    lower = degree_name.lower()
    for key, code in DEGREE_CODE_MAPPING.items():
        if key in lower:
            return code
    return ""

def map_degree_type(degree_name: str) -> str:
    lower = degree_name.lower()
    for key, typ in DEGREE_TYPE_MAPPING.items():
        if key in lower:
            return typ
    return ""

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_programs_with_content_ualabama_latest.csv"
OUTPUT_DIR = Path("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_structured_json_ualabama_latest")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ----------------------------- CONTENT CLEANING AND SPLITTING -----------------------------
def clean_content_for_llm(raw_content: str) -> str:
    if not raw_content:
        return ""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', raw_content)
    try:
        from unidecode import unidecode
        cleaned = unidecode(cleaned)
    except ImportError:
        replacements = {
            '"': '"', '"': '"', "'": "'", "'": "'",
            '–': '-', '—': '-', '…': '...'
        }
        for bad, good in replacements.items():
            cleaned = cleaned.replace(bad, good)
    cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
    return cleaned.strip()

def split_content(content: str, max_size: int = 8000) -> List[str]:
    cleaned = clean_content_for_llm(content)
    if len(cleaned) <= max_size:
        return [cleaned]
    paragraphs = [p.strip() for p in cleaned.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for para in paragraphs:
        if len(current) + len(para) + 2 > max_size:
            if current:
                chunks.append(current.strip())
            current = para
        else:
            current += ("\n\n" + para) if current else para
    if current:
        chunks.append(current.strip())
    return chunks

# ----------------------------- HELPERS -----------------------------
def clean_filename(text: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", text.strip())[:100]

def safe_json_loads(raw: str) -> dict:
    if not raw:
        return {}
    start = raw.find('{')
    if start == -1:
        return {}
    candidate = raw[start:]
    candidate = re.sub(r',\s*([}\]])', r'\1', candidate)
    try:
        return json.loads(candidate)
    except:
        return {}

def call_deepseek(prompt: str) -> dict:
    for attempt in range(5):
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.05,
                max_tokens=2048
            )
            raw = response.choices[0].message.content.strip()
            return safe_json_loads(raw)
        except Exception as e:
            print(f"DeepSeek error (attempt {attempt+1}): {e}")
            if "rate limit" in str(e).lower():
                time.sleep((2 ** attempt) * 15)
            else:
                time.sleep(10)
    return {}

def merge_extracted(results: List[Dict], key: str, is_list: bool = True, is_session: bool = False, is_scalar: bool = False) -> Any:
    if is_scalar:
        vals = [r.get(key) for r in results if r.get(key)]
        return max(vals) if vals else 0
    if is_session:
        # Merge session data from all chunks
        merged = []
        seen_sessions = {}
        for r in results:
            for s in r.get(key, []):
                title = s.get("title", "")
                if title:
                    if title not in seen_sessions:
                        seen_sessions[title] = {
                            "title": title,
                            "startDate": s.get("startDate", ""),
                            "endDate": s.get("endDate", ""),
                            "recursive": s.get("recursive", "")
                        }
                    else:
                        # Update with non-empty values
                        if s.get("startDate"):
                            seen_sessions[title]["startDate"] = s["startDate"]
                        if s.get("endDate"):
                            seen_sessions[title]["endDate"] = s["endDate"]
                        if s.get("recursive") != "":
                            seen_sessions[title]["recursive"] = s["recursive"]
        return list(seen_sessions.values()) if seen_sessions else []
    if is_list:
        merged = []
        seen = set()
        for r in results:
            for item in r.get(key, []):
                item_str = json.dumps(item, sort_keys=True)
                if item_str not in seen:
                    seen.add(item_str)
                    merged.append(item)
        return merged
    return []

# ----------------------------- RUN EXTRACTION WITH CHUNKS -----------------------------
def run_extraction(func, chunks: List[str]) -> List[Dict]:
    results = []
    for chunk in chunks:
        result = func(chunk)
        if result:
            results.append(result)
    return results

# ----------------------------- EXTRACT CAMPUS INFO -----------------------------
def extract_campus_info(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract campus info from content (check Overview, Locations, Footer sections carefully):
- name: Campus names if specifically given. If multiple like 'Locations: Dhaka, Gulshan', concatenate as 'Dhaka, Gulshan'.
- webUrl: Base university URL (e.g., 'https://www.aiub.edu').
- email: Email address from Footer or Contact sections.
- phone: Phone number from Footer or Contact sections.
- country: Country (infer 'USA' for US universities if clear or whatever country name is found for university/campus).
- city: City names only, concatenate if multiple (e.g., 'Moscow'/'Dhaka').
- zipCode: Zip code from Footer or Contact sections.
- address: Full mailing address from Footer or Contact sections.
Use "" if not found.
Content:
{content}
Return ONLY: {{"name": "", "webUrl": "", "email": "", "phone": "", "country": "", "city": "", "zipCode": "", "address": ""}}"""
    return call_deepseek(prompt)

# ----------------------------- SEPARATE EXTRACTION FUNCTIONS -----------------------------
def extract_program_degree(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract:
- program_name: Main program name(take the full program name, with concentration if any) from title or heading, e.g., 'Accountancy' ,'Computer Science' etc.
- degree_name: Full degree name from subheading or description, e.g., 'Masters of Arts' ,'Master of Science','Doctor of Philosophy' etc.
If not found, use "".
Content:
{content}
Return ONLY: {{"program_name": "", "degree_name": ""}}"""
    return call_deepseek(prompt)

def extract_session_duration_delivery(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.

IMPORTANT: 'session' is about CLASS START and END DATES (when the actual program/classes begin and end for each semester), NOT application deadlines.

Extract:
- session: List of session dicts for when classes START and END. Each session dict must have:
  * title: 'Spring', 'Summer', or 'Fall'
  * startDate: When classes BEGIN for this session in yyyy-mm-dd format if mentioned, else ""
  * endDate: When classes END for this session in yyyy-mm-dd format if mentioned, else ""
  * recursive: true if these class dates are the same every year (universal), false if dates vary by year, "" if unclear
  
  Look for phrases like:
  - "Classes begin August 25"
  - "Spring semester starts January 15"
  - "Fall session runs from September 1 to December 15"
  - "Summer classes: May 20 - August 10"
  
  DO NOT confuse with application deadlines. Only include sessions that are actually mentioned.
  If no class start/end date info found, return empty list.
  If year not mentioned in dates, use current year (2025) or following year as appropriate.

- durationYear: Numeric years of program duration, e.g., 4 from '4 years'. 0 if not found.
- deliveryType: List ['Online', 'Offline', 'Hybrid']. If specifically delivery type mentioned, add it to the list, else empty list.

Example: If content has 'Duration: 2 years', durationYear = 2.
Example: If content has 'Fall classes start August 25', session = [{{"title": "Fall", "startDate": "2025-08-25", "endDate": "", "recursive": true}}]

Content: 
{content}
Return ONLY: {{"session": [], "durationYear": 0, "deliveryType": []}}"""
    return call_deepseek(prompt)

def extract_admission_timeline(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.

IMPORTANT: 'admissionTimeline' is about APPLICATION/ADMISSION DEADLINES (when students need to apply), NOT class start dates.

Extract admissionTimeline as list of dicts. Each dict represents an application deadline:
- type: 'Open' for when applications open, 'Priority' for priority deadlines, 'Close' for when applications close/final deadline.
- title: Short sentence about the deadline, e.g., 'Application Deadline', 'Priority Deadline for Spring'.
- detail: Full detail from content about this deadline.
- date: The deadline date in yyyy-mm-dd format if mentioned, else "".
- session: Which session this deadline is for: 'Spring', 'Summer', 'Fall' if specified, else "".
- region: 'International', 'Domestic', or specific country if specified, default 'International'.

Look for phrases like:
- "Application deadline: December 1"
- "Apply by January 15 for Spring admission"
- "Priority deadline for Fall: March 1"
- "Applications open September 1"

Example: If content has 'Application deadline: December 1 for Spring admission', 
create: {{"type": "Close", "title": "Application Deadline for Spring", "detail": "...", "date": "2025-12-01", "session": "Spring", "region": "International"}}

Empty list if no application deadline info found.
Content:
{content}
Return ONLY: {{"admissionTimeline": []}}"""
    return call_deepseek(prompt)

def extract_fees(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract EXACT numeric values - do not regenerate or modify numbers:
- tuitionFeePerYear: List of {{"amount": numeric value EXACTLY as stated, "currency": 'USD' or from content, "region": 'International' or from content}}.
- applicationFee: Similar list with EXACT amounts.

Extract annual tuition or application fee if mentioned. If salaries mentioned, ignore.
Empty lists if not found.
Content:
{content}
Return ONLY: {{"tuitionFeePerYear": [], "applicationFee": []}}"""
    return call_deepseek(prompt)

def extract_how_to_apply(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract howToApply as list of dicts - one for each application step.

IMPORTANT: Regenerate the 'detail' field in a helpful, student-friendly way. Use the content as context to create clear explanations.

Each dict:
- title: Step title or short descriptive sentence.
- detail: REGENERATE this as a clear, student-friendly explanation of the step. Use content as context but make it conversational and helpful.
- webLink: Any URL associated with the step, else "".

Example from content "Visit Graduate Admissions to learn more":
- title: "Visit Graduate Admissions"
- detail: "Head over to the Graduate Admissions page to learn more about the application process, requirements, and important dates. This is your starting point for understanding what you'll need."
- webLink: "https://..."

Empty list if no how-to-apply info.
Content:
{content}
Return ONLY: {{"howToApply": []}}"""
    return call_deepseek(prompt)

def extract_admission_program_types(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract admissionProgramTypes as list of dicts.

IMPORTANT: Regenerate 'overview' in a student-friendly, conversational way. Use content as context but make it engaging and helpful.

Each dict:
- type: 'Major' or 'Minor' from content or "" (program type).
- overview: REGENERATE this as a friendly, engaging overview that helps students understand the program. Use content as context but make it conversational, not too long (2-4 sentences).
- department: Department name of the specific program (e.g., 'Computer Science', 'Business', 'Engineering'). "" if not found.
- courseOutline: List of {{"title": course/topic name, "detail": description of the course}}.

Example overview regeneration:
Original: "This program examines accounting in global business with case studies."
Regenerated: "This program is designed for professionals who want to advance their accounting career. You'll dive into real-world case studies and gain expertise in areas like auditing, financial reporting, and taxation—all tailored to your career goals."

If content has 'hands-on learning opportunities', extract as courseOutline items.
Empty list if no curriculum or program type info.
Content:
{content}
Return ONLY: {{"admissionProgramTypes": []}}"""
    return call_deepseek(prompt)

def extract_general_requirements(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract generalRequirements as list of dicts.

Type must be one of: Transcript, Resume, Statement of Purpose, Statement of Intent, Statement of Motivation, Research Statement, Motivation Letter, Research Letter, Cover Letter, Recommendation Letter.

IMPORTANT: Keep 'page', 'words', 'count' as EXACT numbers from content. Regenerate 'details' in a student-friendly way.

Each dict:
- type: One of the above list (each dict will contain one type only).
- title: Short note about the doc type.
- page: Page limit EXACTLY as stated (number, 0 if not mentioned).
- words: Word limit EXACTLY as stated (number, 0 if not mentioned).
- count: Number required EXACTLY as stated (number, 0 if not mentioned).
- details: REGENERATE this in a clear, student-friendly tone. Use content as context to explain what's needed and why.

Example for 'Number of references: 3':
- type: "Recommendation Letter"
- title: "Academic references required"
- page: 0
- words: 0
- count: 3 (EXACT)
- details: "You'll need three recommendation letters for your application. These should come from professors or academic advisors who can speak to your qualifications and potential for success in this program."

Empty list if no matching requirements.
Content:
{content}
Return ONLY: {{"generalRequirements": []}}"""
    return call_deepseek(prompt)

def extract_standardized_requirements(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract standardizedRequirements as list of dicts.

IMPORTANT: Keep all scores as EXACT numbers from content. Do not modify or regenerate numeric values.

Each dict must have a 'test' object with these fields:
- type: 'GRE', 'GMAT', or 'SAT'
- For GRE/GMAT: {{"total": EXACT number or 0, "verbal": EXACT number or 0, "quant": EXACT number or 0, "awa": EXACT number or 0}}
- For SAT: {{"total": EXACT number or 0, "readingAndWriting": EXACT number or 0, "math": EXACT number or 0}}
- required: true if test is required (default), false if explicitly stated as 'not required' or 'No'

If content says 'GRE: No' or 'GRE not required', set required=false and include minimal info.
If test info is found without saying 'not required', set required=true.
Empty list if no standardized test info.

Content:
{content}
Return ONLY: {{"standardizedRequirements": []}}"""
    return call_deepseek(prompt)

def extract_language_requirements(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract languageRequirements as list of dicts.

IMPORTANT: Keep all scores as EXACT numbers from content. Do not modify or regenerate numeric values.

Each dict must have a 'test' object with these fields:
- type: 'TOEFL', 'IELTS', or 'Duolingo'
- total: EXACT number or 0
- listening: EXACT number or 0
- reading: EXACT number or 0
- writing: EXACT number or 0
- speaking: EXACT number or 0
- required: true if test is required (default), false if explicitly stated as 'not required'

For 'TOEFL/IELTS: 88/6.5', add two separate dicts: one for TOEFL with total=88 and required=true, one for IELTS with total=6.5 and required=true.
If content says test is 'not required', set required=false.
Empty list if no language test info.

Content:
{content}
Return ONLY: {{"languageRequirements": []}}"""
    return call_deepseek(prompt)

def extract_degree_requirements(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract degreeRequirements as list of dicts.

CRITICAL RULES:
1. Analyze the FULL content to understand the context of the program (Bachelor's, Master's, PhD, etc.)
2. Each degree requirement should be ONE dict that combines the degree level AND its evaluation criteria
3. DO NOT assume degree level - only use what's explicitly stated or clearly implied from program context
4. If only "GPA: 3.0" is mentioned without specifying which degree, look at the program type:
   - If this is a Master's program → the GPA likely refers to Bachelor's degree requirement
   - If this is a PhD program → the GPA likely refers to Master's degree requirement
   - If this is a Bachelor's program → the GPA likely refers to High School/A Level requirement
5. If you cannot determine the degree level from context, use generic descriptions like "Previous degree" or "Undergraduate degree"

IMPORTANT: Keep 'total' and 'outOf' as EXACT numbers from content. Do not modify numeric values.

Each dict must have a 'test' object with these fields:
- details: The actual requirement domain/sector. BE SPECIFIC based on what's stated or context:
  * "Bachelor's in Computer Science" (if major specified)
  * "Bachelor's degree" (if just Bachelor's mentioned)
  * "Master's degree in related field" (if context clear)
  * "Previous degree" (if degree level unclear)
  * "High School Diploma" or "A Level" (for undergraduate programs)
- type: The evaluation criteria: 'CGPA', 'GPA', 'Grade', 'Class', or "" if only degree mentioned without criteria
- total: EXACT number if given, else 0
- outOf: EXACT number if given, else 0  
- region: country/region if specified, else ""

CORRECT Examples with Context:

Example 1 - Clear specification:
Input: "Education level: Bachelor's, GPA: 3.0"
Output: [{{"test": {{"details": "Bachelor's degree", "type": "GPA", "total": 3.0, "outOf": 4.0, "region": ""}}}}]

Example 2 - Master's program context:
Input: "Master of Science program. Requirements: GPA: 3.0, TOEFL: 80"
Output: [{{"test": {{"details": "Bachelor's degree", "type": "GPA", "total": 3.0, "outOf": 4.0, "region": ""}}}}]
(Reasoning: Master's program needs Bachelor's degree with 3.0 GPA)

Example 3 - PhD program context:
Input: "PhD in Computer Science. Requirements: Minimum GPA: 3.5"
Output: [{{"test": {{"details": "Master's degree", "type": "GPA", "total": 3.5, "outOf": 4.0, "region": ""}}}}]
(Reasoning: PhD program likely needs Master's degree with 3.5 GPA)

Example 4 - Unclear context:
Input: "GPA: 3.0 required"
Output: [{{"test": {{"details": "Previous degree", "type": "GPA", "total": 3.0, "outOf": 4.0, "region": ""}}}}]
(Reasoning: Cannot determine which degree level, use generic term)

Example 5 - Multiple requirements:
Input: "Master's program. Bachelor's in CS required. Minimum CGPA: 3.5 out of 4.0. A Level students need ABB grades."
Output: [
  {{"test": {{"details": "Bachelor's in Computer Science", "type": "CGPA", "total": 3.5, "outOf": 4.0, "region": ""}}}},
  {{"test": {{"details": "A Level", "type": "Grade", "total": 0, "outOf": 0, "region": ""}}}}
]

Example 6 - Just degree, no criteria:
Input: "Master's degree required for PhD admission"
Output: [{{"test": {{"details": "Master's degree", "type": "", "total": 0, "outOf": 0, "region": ""}}}}]

WRONG Examples (DO NOT DO THIS):

❌ WRONG 1: Creating separate dicts for same requirement
Input: "Bachelor's with GPA 3.0"
Wrong: [{{"test": {{"details": "Bachelor's", "type": "", ...}}}}, {{"test": {{"details": "Bachelor's", "type": "GPA", "total": 3.0, ...}}}}]
Correct: [{{"test": {{"details": "Bachelor's degree", "type": "GPA", "total": 3.0, "outOf": 4.0, "region": ""}}}}]

❌ WRONG 2: Assuming degree level without context
Input: "GPA: 3.0" (no other context)
Wrong: [{{"test": {{"details": "Bachelor's degree", "type": "GPA", ...}}}}]
Correct: [{{"test": {{"details": "Previous degree", "type": "GPA", "total": 3.0, "outOf": 4.0, "region": ""}}}}]

Process:
1. Read the ENTIRE content to understand program type/level
2. Identify all degree requirements and their criteria
3. Match criteria (GPA/CGPA) with the appropriate degree level based on context
4. Combine degree level + criteria into ONE dict per requirement
5. Use generic terms only when context is truly unclear

Empty list if no degree requirements found.
Content:
{content}
Return ONLY: {{"degreeRequirements": []}}"""
    return call_deepseek(prompt)

def extract_scholarships(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract scholarships as list of dicts.

IMPORTANT: Keep 'amount' as EXACT number from content. Regenerate 'detail' in a student-friendly way.

Each dict:
- type: 'Internal' (university scholarship) or 'External'
- name: Scholarship name or 'Financial Aid'
- requirement: List of requirements (keep factual)
- detail: REGENERATE this in a clear, student-friendly, helpful tone. Use content as context to explain what the scholarship offers and how to access it.
- amount: EXACT number or 0
- currency: 'USD' or ISO code of currency, or ""
- webLink: URL or ""
- deadline: 'yyyy-mm-dd' or ""

Example detail regeneration:
Original: "Paying for college can feel overwhelming, but U of I's Financial Aid Office is here to help."
Regenerated: "We know financing your education is a big concern. The Financial Aid Office is here to guide you through your options—from grants and loans to work-study programs. Start by filling out the FAFSA to see what you qualify for."

Empty list if none.
Content:
{content}
Return ONLY: {{"scholarships": []}}"""
    return call_deepseek(prompt)

def extract_useful_links(content: str) -> Dict:
    prompt = f"""You are an expert extractor. Return ONLY valid JSON object.
Extract usefulLink as list of dicts.

IMPORTANT: Keep URLs EXACT. Regenerate 'detail' to be brief and helpful.

Each dict:
- title: Short title like 'Graduate Admissions'
- detail: REGENERATE as a brief, student-friendly description (one sentence explaining what the link offers)
- webLink: The EXACT URL from content

Example:
- title: "Financial Aid Office"
- detail: "Find information on FAFSA deadlines, scholarship opportunities, and financial aid options to help you fund your education."
- webLink: "https://..." (EXACT)

Extract only relevant links: scholarship pages, requirements pages, tuition/cost of attendance info, financial aid, admissions, application, how to apply pages.
Empty list if none.
Content:
{content}
Return ONLY: {{"usefulLink": []}}"""
    return call_deepseek(prompt)

# ----------------------------- MAIN -----------------------------
def main():
    if not Path(CSV_INPUT).exists():
        print(f"CSV not found: {CSV_INPUT}")
        return
    with open(CSV_INPUT, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"Processing {len(rows)} programs with separate prompts...\n")
    for idx, row in enumerate(rows, 1):
        # Clean row: replace None or 'nan' with ""
        for k in row:
            if row[k] is None or row[k] == 'nan':
                row[k] = ""
        csv_program_name = row.get("program_name", "").strip()
        csv_degree_type = row.get("degree_type", "").strip()
        university_name = row.get("university_name", "").strip()
        content = row.get("program_content", "").strip()
        chunks = split_content(content) if content else []
        # Extract all sections separately with chunks
        extracted = {}
        campus_extracted = {}
        
        # CSV-first approach: Check CSV columns BEFORE extracting
        csv_program_name = row.get("program_name", "").strip()
        csv_degree_name = row.get("degree_type", "").strip()
        csv_department = row.get("department", "").strip()
        
        if chunks:
            print(f"[{idx}] Extracting from {len(chunks)} chunks...")
            
            # Only extract program/degree if NOT in CSV
            if csv_program_name:
                print(f"    ✓ Using program_name from CSV: {csv_program_name}")
                extracted["program_name"] = csv_program_name
            else:
                program_degree_results = run_extraction(extract_program_degree, chunks)
                program_name_vals = [r.get("program_name") for r in program_degree_results if r.get("program_name")]
                extracted["program_name"] = program_name_vals[0] if program_name_vals else ""
            
            if csv_degree_name:
                print(f"    ✓ Using degree_name from CSV: {csv_degree_name}")
                extracted["degree_name"] = csv_degree_name
            else:
                if not csv_program_name:  # If we didn't extract program name, we already have degree results
                    degree_name_vals = [r.get("degree_name") for r in program_degree_results if r.get("degree_name")]
                    extracted["degree_name"] = degree_name_vals[0] if degree_name_vals else ""
                else:  # Need to extract degree name separately
                    program_degree_results = run_extraction(extract_program_degree, chunks)
                    degree_name_vals = [r.get("degree_name") for r in program_degree_results if r.get("degree_name")]
                    extracted["degree_name"] = degree_name_vals[0] if degree_name_vals else ""
            session_duration_results = run_extraction(extract_session_duration_delivery, chunks)
            extracted["durationYear"] = merge_extracted(session_duration_results, "durationYear", is_scalar=True)
            extracted["deliveryType"] = merge_extracted(session_duration_results, "deliveryType")
            extracted["session"] = merge_extracted(session_duration_results, "session", is_session=True)
            extracted["admissionTimeline"] = merge_extracted(run_extraction(extract_admission_timeline, chunks), "admissionTimeline")
            fee_results = run_extraction(extract_fees, chunks)
            extracted["tuitionFeePerYear"] = merge_extracted(fee_results, "tuitionFeePerYear")
            extracted["applicationFee"] = merge_extracted(fee_results, "applicationFee")
            extracted["howToApply"] = merge_extracted(run_extraction(extract_how_to_apply, chunks), "howToApply")
            extracted["admissionProgramTypes"] = merge_extracted(run_extraction(extract_admission_program_types, chunks), "admissionProgramTypes")
            
            # Add CSV department to admissionProgramTypes
            if csv_department:
                print(f"    ✓ Using department from CSV: {csv_department}")
                if extracted["admissionProgramTypes"]:
                    # Add CSV department to all program types
                    for prog_type in extracted["admissionProgramTypes"]:
                        prog_type["department"] = csv_department
                else:
                    # No program types extracted, create minimal entry with CSV department
                    extracted["admissionProgramTypes"] = [{
                        "type": "",
                        "overview": "",
                        "department": csv_department,
                        "courseOutline": []
                    }]
            extracted["generalRequirements"] = merge_extracted(run_extraction(extract_general_requirements, chunks), "generalRequirements")
            extracted["standardizedRequirements"] = merge_extracted(run_extraction(extract_standardized_requirements, chunks), "standardizedRequirements")
            extracted["languageRequirements"] = merge_extracted(run_extraction(extract_language_requirements, chunks), "languageRequirements")
            extracted["degreeRequirements"] = merge_extracted(run_extraction(extract_degree_requirements, chunks), "degreeRequirements")
            extracted["scholarships"] = merge_extracted(run_extraction(extract_scholarships, chunks), "scholarships")
            extracted["usefulLink"] = merge_extracted(run_extraction(extract_useful_links, chunks), "usefulLink")
            # Extract campus - CSV first for each field
            # Map CSV columns to campus fields
            csv_campus_map = {
                "name": row.get("campus_name", "").strip(),
                "webUrl": row.get("url", "").strip(),
                "email": row.get("email", "").strip(),
                "phone": row.get("phone", "").strip(),
                "country": row.get("country", "").strip(),
                "city": row.get("city", "").strip(),
                "zipCode": row.get("zipCode", "").strip(),
                "address": row.get("address", "").strip()
            }
            
            # Check which fields need LLM extraction
            need_campus_extraction = any(not val for val in csv_campus_map.values())
            
            if need_campus_extraction:
                campus_results = run_extraction(extract_campus_info, chunks)
                for field, csv_val in csv_campus_map.items():
                    if csv_val:
                        # Use CSV value
                        campus_extracted[field] = csv_val
                        print(f"    ✓ Using campus.{field} from CSV")
                    else:
                        # Extract from content
                        vals = [r.get(field) for r in campus_results if r.get(field)]
                        campus_extracted[field] = vals[0] if vals else ""
            else:
                # All campus data in CSV, skip extraction
                print(f"    ✓ Using all campus data from CSV")
                campus_extracted = csv_campus_map
        # Use CSV first, then extracted values as fallback
        final_program_name = csv_program_name or extracted.get("program_name", "") or "Unknown Program"
        final_degree_name = csv_degree_name or extracted.get("degree_name", "") or ""
        safe_uni = clean_filename(university_name)
        safe_prog = clean_filename(final_program_name)
        safe_deg = clean_filename(final_degree_name) if final_degree_name else ""
        base_filename = f"{safe_uni}_{safe_prog}_{safe_deg}_extracted.json" if final_degree_name else f"{safe_uni}_{safe_prog}_extracted.json"
        # Check for file existence and handle numbering
        filename = base_filename
        num = 1
        while (OUTPUT_DIR / filename).exists():
            print(f"File {filename} exists. Re-extracting program name...")
            # Re-extract only program name
            program_degree_results = run_extraction(extract_program_degree, chunks)
            program_name_vals = [r.get("program_name") for r in program_degree_results if r.get("program_name")]
            new_program_name = program_name_vals[0] if program_name_vals else final_program_name
            if new_program_name != final_program_name:
                final_program_name = new_program_name
                safe_prog = clean_filename(final_program_name)
                base_filename = f"{safe_uni}_{safe_prog}_{safe_deg}_extracted.json" if final_degree_name else f"{safe_uni}_{safe_prog}_extracted.json"
                filename = base_filename
            else:
                # Still same, append number
                num += 1
                filename = f"{safe_uni}_{safe_prog}_{safe_deg}_{num}_extracted.json" if final_degree_name else f"{safe_uni}_{safe_prog}_{num}_extracted.json"
        output_file = OUTPUT_DIR / filename
        print(f"[{idx}/{len(rows)}] Processing: {final_program_name} | {final_degree_name or 'No Degree'} | {university_name}")
        # Build extracted_data
        extracted_data = {
            "program": {
                "name": final_program_name,
                "code": "",
                "synonyms": ""
            },
            "degree": {
                "name": final_degree_name,
                "code": map_degree_code(final_degree_name),
                "type": map_degree_type(final_degree_name),
                "synonyms": ""
            },
            "university": {
                "name": university_name,
                "ranks": [],
                "campus": {
                    "name": campus_extracted.get("name", ""),
                    "webUrl": campus_extracted.get("webUrl", ""),
                    "email": campus_extracted.get("email", ""),
                    "phone": campus_extracted.get("phone", ""),
                    "country": campus_extracted.get("country", ""),
                    "city": campus_extracted.get("city", ""),
                    "zipCode": campus_extracted.get("zipCode", ""),
                    "address": campus_extracted.get("address", "")
                }
            },
            "programUrl": row.get("programUrl", ""),
            "session": extracted.get("session", []),
            "durationYear": extracted.get("durationYear", 0),
            "deliveryType": extracted.get("deliveryType", []),
            "admissionTimeline": extracted.get("admissionTimeline", []),
            "tuitionFeePerYear": extracted.get("tuitionFeePerYear", []),
            "applicationFee": extracted.get("applicationFee", []),
            "howToApply": extracted.get("howToApply", []),
            "admissionProgramTypes": extracted.get("admissionProgramTypes", []),
            "generalRequirements": extracted.get("generalRequirements", []),
            "standardizedRequirements": extracted.get("standardizedRequirements", []),
            "languageRequirements": extracted.get("languageRequirements", []),
            "degreeRequirements": extracted.get("degreeRequirements", []),
            "scholarships": extracted.get("scholarships", []),
            "usefulLink": extracted.get("usefulLink", [])
        }
        # Add ranks
        rank_type = row.get("rank_type", "").strip()
        position_str = row.get("position", "").strip()
        if rank_type and position_str.isdigit():
            extracted_data["university"]["ranks"].append({
                "type": rank_type,
                "position": int(position_str)
            })
        # Save
        output_json = row.copy()
        output_json["extracted_data"] = extracted_data
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=2, ensure_ascii=False)
        print(f"  → Saved: {output_file.name}\n")
        time.sleep(1.5)
    print("All programs processed successfully!")

if __name__ == "__main__":
    main()
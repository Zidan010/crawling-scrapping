# import csv
# import json
# import os
# import time
# import re
# from pathlib import Path
# from pydantic import BaseModel, Field
# from typing import Any, List, Dict
# from groq import Groq, RateLimitError
# from dotenv import load_dotenv
# import os

# load_dotenv()
# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# # ----------------------------- CONFIG -----------------------------
# CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_programs_with_content_v2.csv"   # ← From Crawl4AI phase
# OUTPUT_DIR = Path("extracted_structured_json")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# client = Groq(api_key=GROQ_API_KEY)

# # ----------------------------- SCHEMA -----------------------------
# class ProgramDetails(BaseModel):
#     Department: str = Field("", description="Department or college name")
#     program_overview: str = Field("", description="Clear, concise overview")
#     start_at: List[str] = Field(default_factory=list, description="Application start dates/semesters")
#     end_at: List[str] = Field(default_factory=list, description="Application deadlines/end dates")
#     course_outline: Dict[str, Any] = Field(default_factory=dict, description="Structured curriculum")
#     delivery_type: List[str] = Field(default_factory=list, description="Delivery modes")
#     admission_timeline: str = Field("", description="Full admission timeline")
#     tuition_fee_per_year: str = Field("", description="Annual tuition")
#     application_fee: str = Field("", description="Application fee")
#     how_to_apply: str = Field("", description="Application steps")
#     general_requirement: List[str] = Field(default_factory=list, description="General requirements")
#     standardized_requirement: List[str] = Field(default_factory=list, description="Standardized tests")
#     language_requirement: Dict[str, str] = Field(default_factory=dict, description="Language scores")
#     degree_requirement: List[str] = Field(default_factory=list, description="Prior degree needed")
#     scholarship_requirement: List[str] = Field(default_factory=list, description="Scholarship eligibility")
#     scholarship_detail: Dict[str, Any] = Field(default_factory=dict, description="Scholarship details")

# # ----------------------------- DETAILED INSTRUCTIONS -----------------------------
# INSTRUCTIONS = {
#     "Department": "Extract the exact department, school, or college that offers this program. Examples: 'Department of Computer Science', 'College of Engineering'. Return only the name. If not found, return empty string.",
#     "program_overview": "Write a clear, engaging 3-5 sentence summary of the program for a prospective student. Focus on purpose, key features, and career outcomes. Use natural language. If no overview, return empty string.",
#     "start_at": "Extract all application start dates or semesters (e.g., 'Fall 2025', 'January 2025', 'Rolling'). Return as list of strings. Do NOT include program start dates — only when applications open. If none, return empty list.",
#     "end_at": "Extract all application deadlines (e.g., 'December 1, 2025', 'Spring: March 1'). Return as list of strings. Only application closing dates. If none, return empty list.",
#     "course_outline": "Return a dict with 'summary' (brief description) and 'courses' (list of course names or topics). If no curriculum info, return empty dict.",
#     "delivery_type": "Return list with only these values: 'On-campus', 'Online', 'Hybrid'. Do not combine (e.g., no 'Online and On-campus'). If multiple, list separately. If none, empty list.",
#     "admission_timeline": "Summarize the full admission process timeline including all deadlines and key dates in a clear paragraph. If no timeline, return empty string.",
#     "tuition_fee_per_year": "Extract annual tuition fee with currency and specify in-state/out-of-state if mentioned. Example: '$15,000 (in-state), $35,000 (out-of-state)'. If none, empty string.",
#     "application_fee": "Extract application fee with currency. Example: '$75'. If none, empty string.",
#     "how_to_apply": "Summarize the application process in clear, numbered steps. If no instructions, empty string.",
#     "general_requirement": "List all general admission requirements (GPA, prerequisites, transcripts, etc.) as bullet-point strings. If none, empty list.",
#     "standardized_requirement": "List required standardized tests with minimum scores (e.g., 'GRE: 300', 'GMAT: 600'). If none or optional, empty list.",
#     "language_requirement": "Return dict with keys: TOEFL, IELTS, PTE, Duolingo, Other. Values are minimum scores (e.g., 'TOEFL': '90'). If none, empty dict.",
#     "degree_requirement": "List required prior degrees or qualifications (e.g., 'Bachelor’s in related field'). If none, empty list.",
#     "scholarship_requirement": "List eligibility criteria for scholarships (e.g., 'GPA 3.5+', 'International students'). If none, empty list.",
#     "scholarship_detail": "Return dict with 'summary' and 'scholarships' list (each item: {'name': ..., 'amount': ...}). If none, empty dict."
# }

# # ----------------------------- HELPERS -----------------------------
# def clean_filename(text: str) -> str:
#     return re.sub(r'[\\/*?:"<>|]', "_", text.strip())[:100]

# def split_content(content: str, max_size: int = 22000) -> list[str]:
#     if len(content) <= max_size:
#         return [content]
#     paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
#     chunks = []
#     current = ""
#     for p in paragraphs:
#         if len(current) + len(p) + 2 > max_size:
#             if current:
#                 chunks.append(current.strip())
#             current = p
#         else:
#             current += ("\n\n" + p) if current else p
#     if current:
#         chunks.append(current.strip())
#     return chunks

# def call_groq(content_chunk: str, program_name: str) -> dict:
#     prompt = f"""
# You are an expert data extractor for university programs.

# Program Name: {program_name}

# Extract the following fields from the content. Return ONLY valid JSON. Use exact structure.

# """
#     for field, instr in INSTRUCTIONS.items():
#         prompt += f"\n{field}:\n{instr}\n"

#     prompt += f"""

# Content:
# {content_chunk}

# Return ONLY the JSON object:
# """

#     for attempt in range(3):
#         try:
#             response = client.chat.completions.create(
#                 model="llama-3.3-70b-versatile",
#                 messages=[{"role": "user", "content": prompt}],
#                 response_format={"type": "json_object"},
#                 temperature=0.0,
#                 max_tokens=4096
#             )
#             raw = response.choices[0].message.content.strip()
#             if raw.startswith("```"):
#                 raw = raw.split("```", 1)[-1].rsplit("```", 1)[0].strip()
#             return json.loads(raw)
#         except RateLimitError:
#             print("Rate limit — waiting 30 minutes...")
#             time.sleep(1800)
#         except Exception as e:
#             print(f"Error (attempt {attempt+1}): {e}")
#             time.sleep(10)
#     return {}

# # ----------------------------- MAIN -----------------------------
# def main():
#     if not Path(CSV_INPUT).exists():
#         print(f"CSV not found: {CSV_INPUT}")
#         return

#     rows = []
#     with open(CSV_INPUT, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         rows = list(reader)

#     print(f"Processing {len(rows)} programs...\n")

#     for idx, row in enumerate(rows, 1):
#         program_name = row.get("program_name", "unknown")
#         uni_name = row.get("university_name", "unknown")
#         all_degree_program_link = row.get("degree_program_link", "")
#         degree_type = row.get("degree_type", "")
#         campuses = row.get("campuses", "")
#         content = row.get("program_content", "")

#         safe_uni = clean_filename(uni_name)
#         safe_prog = clean_filename(program_name)
#         output_file = OUTPUT_DIR / f"{safe_uni}_{safe_prog}_extracted.json"

#         print(f"[{idx}/{len(rows)}] {program_name}")

#         if not content.strip():
#             final_data = ProgramDetails().model_dump()
#         else:
#             chunks = split_content(content)
#             print(f"  → {len(chunks)} chunk(s)")

#             merged = {field: None for field in ProgramDetails.model_fields}

#             for i, chunk in enumerate(chunks):
#                 result = call_groq(chunk, program_name)
#                 for field, value in result.items():
#                     current = merged[field]
#                     new = value

#                     if new in ["", None, [], {}]:
#                         continue

#                     if current in ["", None, [], {}]:
#                         merged[field] = new
#                     elif isinstance(current, list) and isinstance(new, list):
#                         merged[field] = list(set(current + new))
#                     elif isinstance(current, dict) and isinstance(new, dict):
#                         merged[field] = {**current, **new}
#                     elif isinstance(current, str) and isinstance(new, str):
#                         merged[field] = current + "\n\n" + new if current else new

#             # Final cleanup: empty → default
#             final_data = {}
#             for field, val in merged.items():
#                 default = ProgramDetails().model_dump()[field]
#                 final_data[field] = val if val not in [None, "", [], {}] else default

#         # Output
#         output_json = {
#             "university_name": uni_name,
#             "program_name": program_name,
#             "all_degree_program_link":all_degree_program_link,
#             "degree_type": degree_type,
#             "campuses": campuses,
#             "program_link": row.get("program_link", ""),
#             "extracted_data": final_data
#         }

#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(output_json, f, indent=4, ensure_ascii=False)

#         print(f"  → Saved: {output_file.name}\n")
#         time.sleep(2)

#     print("All programs extracted successfully!")

# if __name__ == "__main__":
#     main()


import csv
import json
import time
import re
from pathlib import Path
from typing import Any, List, Dict
from pydantic import BaseModel, Field
from groq import Groq, RateLimitError as GroqRateLimitError
import requests
from dotenv import load_dotenv
import os

load_dotenv()

# ----------------------------- CONFIG -----------------------------
CSV_INPUT = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_programs_with_content_v2.csv"
OUTPUT_DIR = Path("extracted_structured_json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
LOCAL_LLM_ENDPOINT = "http://192.168.11.201:8888/generate"  # your local endpoint

client = Groq(api_key=GROQ_API_KEY)

# State: start with Groq
current_provider = "groq"
groq_cooldown = False

# ----------------------------- SCHEMA -----------------------------
class ProgramDetails(BaseModel):
    department: str = Field("", description="Department or college name")
    program_overview: str = Field("", description="Clear, concise overview")
    start_at: List[str] = Field(default_factory=list, description="Application start dates/semesters")
    end_at: List[str] = Field(default_factory=list, description="Application deadlines/end dates")
    course_outline: Dict[str, Any] = Field(default_factory=dict, description="Structured curriculum")
    delivery_type: List[str] = Field(default_factory=list, description="Delivery modes")
    admission_timeline: str = Field("", description="Full admission timeline")
    tuition_fee_per_year: str = Field("", description="Annual tuition")
    application_fee: str = Field("", description="Application fee")
    how_to_apply: str = Field("", description="Application steps")
    general_requirement: List[str] = Field(default_factory=list, description="General requirements")
    standardized_requirement: List[str] = Field(default_factory=list, description="Standardized tests")
    language_requirement: Dict[str, str] = Field(default_factory=dict, description="Language scores")
    degree_requirement: List[str] = Field(default_factory=list, description="Prior degree needed")
    scholarship_requirement: List[str] = Field(default_factory=list, description="Scholarship eligibility")
    scholarship_detail: Dict[str, Any] = Field(default_factory=dict, description="Scholarship details")

# ----------------------------- YOUR DETAILED INSTRUCTIONS -----------------------------
INSTRUCTIONS = {
    "department": "Extract the exact department, school, or college that offers this program. Examples: 'Department of Computer Science', 'College of Engineering'. Return only the name. If not found, return empty string.",
    "program_overview": "Write a clear, engaging 3-5 sentence summary of the program for a prospective student. Focus on purpose, key features, and career outcomes. Use natural language. If no overview, return empty string.",
    "start_at": "Extract all application opening dates or semesters (e.g., 'Fall 2025', 'January 2025', 'Rolling'). Return as list of strings. Only when applications open – not program start. If none, return empty list.",
    "end_at": "Extract all application deadlines (e.g., 'December 1, 2025', 'Spring: March 1'). Return as list of strings. Only application closing dates. If none, return empty list.",
    "course_outline": "Return a dict with 'summary' (brief description) and 'courses' (list of course names or topics). If no curriculum info, return empty dict.",
    "delivery_type": "Return list with only these values: 'On-campus', 'Online', 'Hybrid'. Do not combine (e.g., no 'Online and On-campus'). If multiple, list separately. If none, empty list.",
    "admission_timeline": "Summarize the full admission process timeline including all deadlines and key dates in a clear paragraph. If no timeline, return empty string.",
    "tuition_fee_per_year": "Extract annual tuition fee with currency and specify in-state/out-of-state if mentioned. Example: '$15,000 (in-state), $35,000 (out-of-state)'. If none, empty string.",
    "application_fee": "Extract application fee with currency. Example: '$75'. If none, empty string.",
    "how_to_apply": "Summarize the application process in clear, numbered steps. If no instructions, empty string.",
    "general_requirement": "List all general admission requirements (GPA, prerequisites, transcripts, etc.) as bullet-point strings. If none, empty list.",
    "standardized_requirement": "List required standardized tests with minimum scores (e.g., 'GRE: 300', 'GMAT: 600'). If none or optional, empty list.",
    "language_requirement": "Return dict with keys: TOEFL, IELTS, PTE, Duolingo, Other. Values are minimum scores (e.g., 'TOEFL': '90'). If none, empty dict.",
    "degree_requirement": "List required prior degrees or qualifications (e.g., 'Bachelor’s in related field'). If none, empty list.",
    "scholarship_requirement": "List eligibility criteria for scholarships (e.g., 'GPA 3.5+', 'International students'). If none, empty list.",
    "scholarship_detail": "Return dict with 'summary' and 'scholarships' list (each item: {'name': ..., 'amount': ...}). If none, empty dict."
}

# ----------------------------- HELPERS -----------------------------
def clean_filename(text: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', "_", text.strip())[:100]

def split_content(content: str, max_size: int = 22000) -> list[str]:
    if len(content) <= max_size:
        return [content]
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    chunks = []
    current = ""
    for p in paragraphs:
        if len(current) + len(p) + 2 > max_size:
            if current:
                chunks.append(current.strip())
            current = p
        else:
            current += ("\n\n" + p) if current else p
    if current:
        chunks.append(current.strip())
    return chunks

# ----------------------------- LLM CALLS -----------------------------
def call_groq(content_chunk: str, program_name: str) -> dict:
    prompt = f"""
You are an expert data extractor for university programs.
Program Name: {program_name}

Extract the following fields from the content. Return ONLY valid JSON. Use exact structure.

"""
    for field, instr in INSTRUCTIONS.items():
        prompt += f"\n{field}:\n{instr}\n"

    prompt += f"""
Content:
{content_chunk}

Return ONLY the JSON object:
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=4096
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```", 1)[-1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except GroqRateLimitError:
        raise
    except Exception as e:
        print(f"Groq error: {e}")
        return {}

def call_local_llm(content_chunk: str, program_name: str) -> dict:
    prompt = f"""
You are an expert data extractor for university programs.
Program Name: {program_name}

Extract the following fields from the content. Return ONLY valid JSON. Use exact structure.

"""
    for field, instr in INSTRUCTIONS.items():
        prompt += f"\n{field}:\n{instr}\n"

    prompt += f"""
Content:
{content_chunk}

Return ONLY the JSON object:
"""

    payload = {
        "instruction": "You are a precise extractor. Return ONLY valid JSON matching the fields above.",
        "prompt": prompt,
        "context": content_chunk,
        "output_tokens": 4096,
        "temperature": 0.2
    }

    try:
        resp = requests.post(LOCAL_LLM_ENDPOINT, json=payload, timeout=300)
        resp.raise_for_status()
        raw = resp.json().get("response", "")
        if raw.startswith("```"):
            raw = raw.split("```", 1)[-1].rsplit("```", 1)[0].strip()
        return json.loads(raw)
    except Exception as e:
        print(f"Local LLM error: {e}")
        return {}

def call_llm_with_failover(content_chunk: str, program_name: str) -> dict:
    global current_provider, groq_cooldown

    if current_provider == "groq" and not groq_cooldown:
        try:
            print("    → Using GROQ LLM")
            result = call_groq(content_chunk, program_name)
            if result:
                return result
        except GroqRateLimitError:
            print("Groq rate limit → switching to local LLM")
            groq_cooldown = True
            current_provider = "local"

    # Use local LLM
    print("    → Using LOCAL LLM")
    result = call_local_llm(content_chunk, program_name)
    if result:
        return result

    # Both failed → wait and retry Groq later
    print("Both Groq and local LLM failed. Waiting 30 minutes before trying Groq again...")
    time.sleep(1800)
    current_provider = "groq"  # reset to try Groq first
    groq_cooldown = False
    return call_llm_with_failover(content_chunk, program_name)

# ----------------------------- MAIN -----------------------------
def main():
    if not Path(CSV_INPUT).exists():
        print(f"CSV not found: {CSV_INPUT}")
        return

    rows = []
    with open(CSV_INPUT, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Processing {len(rows)} programs...\n")

    for idx, row in enumerate(rows, 1):
        program_name = row.get("program_name", "unknown")
        uni_name = row.get("university_name", "unknown")
        all_degree_program_link = row.get("degree_program_link", "")
        degree_type = row.get("degree_type", "")
        campuses = row.get("campuses", "")
        content = row.get("program_content", "")

        safe_uni = clean_filename(uni_name)
        safe_prog = clean_filename(program_name)
        output_file = OUTPUT_DIR / f"{safe_uni}_{safe_prog}_extracted.json"

        print(f"[{idx}/{len(rows)}] {program_name}")

        if not content.strip():
            final_data = ProgramDetails().model_dump()
        else:
            chunks = split_content(content)
            print(f"  → {len(chunks)} chunk(s)")

            merged = {field: None for field in ProgramDetails.model_fields}

            for i, chunk in enumerate(chunks):
                result = call_llm_with_failover(chunk, program_name)
                for field, value in result.items():
                    current = merged[field]
                    new = value
                    if new in ["", None, [], {}]:
                        continue
                    if current in ["", None, [], {}]:
                        merged[field] = new
                    elif isinstance(current, list) and isinstance(new, list):
                        merged[field] = list(set(current + new))
                    elif isinstance(current, dict) and isinstance(new, dict):
                        merged[field] = {**current, **new}
                    elif isinstance(current, str) and isinstance(new, str):
                        merged[field] = current + "\n\n" + new if current else new

            final_data = {}
            for field, val in merged.items():
                default = ProgramDetails().model_dump()[field]
                final_data[field] = val if val not in [None, "", [], {}] else default

        output_json = {
            "university_name": uni_name,
            "program_name": program_name,
            "all_degree_program_link": all_degree_program_link,
            "degree_type": degree_type,
            "campuses": campuses,
            "program_link": row.get("program_link", ""),
            "extracted_data": final_data
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(output_json, f, indent=4, ensure_ascii=False)

        print(f"  → Saved: {output_file.name}\n")
        time.sleep(2)

    print("All programs extracted successfully!")

if __name__ == "__main__":
    main()











































###############################################################################

# import csv
# import json
# import time
# import re
# from pathlib import Path
# from typing import Any, List, Dict
# from pydantic import BaseModel, Field
# from groq import Groq, RateLimitError as GroqRateLimitError
# import requests
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # ----------------------------- CONFIG -----------------------------
# CSV_INPUT = "extracted_programs_with_content_v2.csv"
# OUTPUT_DIR = Path("extracted_structured_json_2")
# OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# if not GROQ_API_KEY:
#     raise ValueError("GROQ_API_KEY not found in .env")
# if not DEEPSEEK_API_KEY:
#     raise ValueError("DEEPSEEK_API_KEY not found in .env")

# groq_client = Groq(api_key=GROQ_API_KEY)

# # DeepSeek settings
# DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"
# DEEPSEEK_MODEL = "deepseek-chat"

# # State tracking
# current_provider = "groq"
# groq_cooldown = False
# deepseek_cooldown = False

# # ----------------------------- SCHEMA & INSTRUCTIONS (unchanged) -----------------------------
# class ProgramDetails(BaseModel):
#     Department: str = Field("", description="Department or college name")
#     program_overview: str = Field("", description="Clear, concise overview")
#     start_at: List[str] = Field(default_factory=list, description="Application start dates/semesters")
#     end_at: List[str] = Field(default_factory=list, description="Application deadlines/end dates")
#     course_outline: Dict[str, Any] = Field(default_factory=dict, description="Structured curriculum")
#     delivery_type: List[str] = Field(default_factory=list, description="Delivery modes")
#     admission_timeline: str = Field("", description="Full admission timeline")
#     tuition_fee_per_year: str = Field("", description="Annual tuition")
#     application_fee: str = Field("", description="Application fee")
#     how_to_apply: str = Field("", description="Application steps")
#     general_requirement: List[str] = Field(default_factory=list, description="General requirements")
#     standardized_requirement: List[str] = Field(default_factory=list, description="Standardized tests")
#     language_requirement: Dict[str, str] = Field(default_factory=dict, description="Language scores")
#     degree_requirement: List[str] = Field(default_factory=list, description="Prior degree needed")
#     scholarship_requirement: List[str] = Field(default_factory=list, description="Scholarship eligibility")
#     scholarship_detail: Dict[str, Any] = Field(default_factory=dict, description="Scholarship details")

# INSTRUCTIONS = {
#     "Department": "Extract the exact department, school, or college that offers this program. Examples: 'Department of Computer Science', 'College of Engineering'. Return only the name. If not found, return empty string.",
#     "program_overview": "Write a clear, engaging 3-5 sentence summary of the program for a prospective student. Focus on purpose, key features, and career outcomes. Use natural language. If no overview, return empty string.",
#     "start_at": "Extract all application start dates or semesters (e.g., 'Fall 2025', 'January 2025', 'Rolling'). Return as list of strings. Do NOT include program start dates — only when applications open. If none, return empty list.",
#     "end_at": "Extract all application deadlines (e.g., 'December 1, 2025', 'Spring: March 1'). Return as list of strings. Only application closing dates. If none, return empty list.",
#     "course_outline": "Return a dict with 'summary' (brief description) and 'courses' (list of course names or topics). If no curriculum info, return empty dict.",
#     "delivery_type": "Return list with only these values: 'On-campus', 'Online', 'Hybrid'. Do not combine (e.g., no 'Online and On-campus'). If multiple, list separately. If none, empty list.",
#     "admission_timeline": "Summarize the full admission process timeline including all deadlines and key dates in a clear paragraph. If no timeline, return empty string.",
#     "tuition_fee_per_year": "Extract annual tuition fee with currency and specify in-state/out-of-state if mentioned. Example: '$15,000 (in-state), $35,000 (out-of-state)'. If none, empty string.",
#     "application_fee": "Extract application fee with currency. Example: '$75'. If none, empty string.",
#     "how_to_apply": "Summarize the application process in clear, numbered steps. If no instructions, empty string.",
#     "general_requirement": "List all general admission requirements (GPA, prerequisites, transcripts, etc.) as bullet-point strings. If none, empty list.",
#     "standardized_requirement": "List required standardized tests with minimum scores (e.g., 'GRE: 300', 'GMAT: 600'). If none or optional, empty list.",
#     "language_requirement": "Return dict with keys: TOEFL, IELTS, PTE, Duolingo, Other. Values are minimum scores (e.g., 'TOEFL': '90'). If none, empty dict.",
#     "degree_requirement": "List required prior degrees or qualifications (e.g., 'Bachelor’s in related field'). If none, empty list.",
#     "scholarship_requirement": "List eligibility criteria for scholarships (e.g., 'GPA 3.5+', 'International students'). If none, empty list.",
#     "scholarship_detail": "Return dict with 'summary' and 'scholarships' list (each item: {'name': ..., 'amount': ...}). If none, empty dict."
# }

# # ----------------------------- HELPERS -----------------------------
# def clean_filename(text: str) -> str:
#     return re.sub(r'[\\/*?:"<>|]', "_", text.strip())[:100]

# def split_content(content: str, max_size: int = 22000) -> list[str]:
#     if len(content) <= max_size:
#         return [content]
#     paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
#     chunks = []
#     current = ""
#     for p in paragraphs:
#         if len(current) + len(p) + 2 > max_size:
#             if current:
#                 chunks.append(current.strip())
#             current = p
#         else:
#             current += ("\n\n" + p) if current else p
#     if current:
#         chunks.append(current.strip())
#     return chunks

# # ----------------------------- LLM CALLS -----------------------------
# def call_groq(content_chunk: str, program_name: str) -> dict:
#     prompt = f"""
# You are an expert data extractor for university programs.
# Program Name: {program_name}
# Extract the following fields from the content. Return ONLY valid JSON. Use exact structure.
# """
#     for field, instr in INSTRUCTIONS.items():
#         prompt += f"\n{field}:\n{instr}\n"

#     prompt += f"""
# Content:
# {content_chunk}
# Return ONLY the JSON object:
# """

#     try:
#         response = groq_client.chat.completions.create(
#             model="llama-3.3-70b-versatile",
#             messages=[{"role": "user", "content": prompt}],
#             response_format={"type": "json_object"},
#             temperature=0.0,
#             max_tokens=4096
#         )
#         raw = response.choices[0].message.content.strip()
#         if raw.startswith("```"):
#             raw = raw.split("```", 1)[-1].rsplit("```", 1)[0].strip()
#         return json.loads(raw)
#     except GroqRateLimitError:
#         raise
#     except Exception as e:
#         print(f"Groq error: {e}")
#         return {}

# def call_deepseek(content_chunk: str, program_name: str) -> dict:
#     prompt = f"""
# You are an expert data extractor for university programs.
# Program Name: {program_name}
# Extract the following fields from the content. Return ONLY valid JSON. Use exact structure.
# """
#     for field, instr in INSTRUCTIONS.items():
#         prompt += f"\n{field}:\n{instr}\n"

#     prompt += f"""
# Content:
# {content_chunk}
# Return ONLY the JSON object:
# """

#     headers = {
#         "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
#         "Content-Type": "application/json"
#     }

#     payload = {
#         "model": DEEPSEEK_MODEL,
#         "messages": [{"role": "user", "content": prompt}],
#         "response_format": {"type": "json_object"},
#         "temperature": 0.0,
#         "max_tokens": 4096
#     }

#     try:
#         response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=120)
#         response.raise_for_status()
#         data = response.json()
#         raw = data["choices"][0]["message"]["content"].strip()
#         if raw.startswith("```"):
#             raw = raw.split("```", 1)[-1].rsplit("```", 1)[0].strip()
#         return json.loads(raw)
#     except requests.exceptions.HTTPError as e:
#         if response.status_code == 402:
#             raise RuntimeError("DeepSeek: Payment Required (insufficient balance)")
#         elif response.status_code == 429:
#             raise RuntimeError("DeepSeek: Rate limit")
#         else:
#             print(f"DeepSeek HTTP error {response.status_code}: {response.text}")
#             return {}
#     except Exception as e:
#         print(f"DeepSeek error: {e}")
#         return {}

# def call_llm_with_failover(content_chunk: str, program_name: str) -> dict:
#     global current_provider, groq_cooldown, deepseek_cooldown

#     providers = ["groq", "deepseek"] if current_provider == "groq" else ["deepseek", "groq"]

#     for provider in providers:
#         if (provider == "groq" and groq_cooldown) or (provider == "deepseek" and deepseek_cooldown):
#             continue

#         print(f"    → Using {provider.upper()} LLM")

#         try:
#             if provider == "groq":
#                 result = call_groq(content_chunk, program_name)
#             else:
#                 result = call_deepseek(content_chunk, program_name)

#             if result:
#                 current_provider = provider
#                 if provider == "groq":
#                     groq_cooldown = False
#                 else:
#                     deepseek_cooldown = False
#                 return result

#         except GroqRateLimitError:
#             print("Groq rate limit — switching to DeepSeek")
#             groq_cooldown = True
#         except RuntimeError as e:
#             if "rate limit" in str(e).lower() or "payment" in str(e).lower():
#                 print(f"{e} — marking DeepSeek on cooldown")
#                 deepseek_cooldown = True
#             else:
#                 print(f"DeepSeek error: {e}")

#     # Both exhausted
#     print("Both Groq and DeepSeek are rate-limited or out of funds. Waiting 30 minutes...")
#     time.sleep(1800)
#     return call_llm_with_failover(content_chunk, program_name)

# # ----------------------------- MAIN -----------------------------
# def main():
#     if not Path(CSV_INPUT).exists():
#         print(f"CSV not found: {CSV_INPUT}")
#         return

#     rows = []
#     with open(CSV_INPUT, newline='', encoding='utf-8') as f:
#         reader = csv.DictReader(f)
#         rows = list(reader)

#     print(f"Processing {len(rows)} programs...\n")

#     for idx, row in enumerate(rows, 1):
#         program_name = row.get("program_name", "unknown")
#         uni_name = row.get("university_name", "unknown")
#         all_degree_program_link = row.get("degree_program_link", "")
#         degree_type = row.get("degree_type", "")
#         campuses = row.get("campuses", "")
#         content = row.get("program_content", "")

#         safe_uni = clean_filename(uni_name)
#         safe_prog = clean_filename(program_name)
#         output_file = OUTPUT_DIR / f"{safe_uni}_{safe_prog}_extracted.json"

#         print(f"[{idx}/{len(rows)}] {program_name}")

#         if not content.strip():
#             final_data = ProgramDetails().model_dump()
#         else:
#             chunks = split_content(content)
#             print(f"  → {len(chunks)} chunk(s)")

#             merged = {field: None for field in ProgramDetails.model_fields}

#             for i, chunk in enumerate(chunks):
#                 result = call_llm_with_failover(chunk, program_name)
#                 for field, value in result.items():
#                     current = merged[field]
#                     new = value
#                     if new in ["", None, [], {}]:
#                         continue
#                     if current in ["", None, [], {}]:
#                         merged[field] = new
#                     elif isinstance(current, list) and isinstance(new, list):
#                         merged[field] = list(set(current + new))
#                     elif isinstance(current, dict) and isinstance(new, dict):
#                         merged[field] = {**current, **new}
#                     elif isinstance(current, str) and isinstance(new, str):
#                         merged[field] = current + "\n\n" + new if current else new

#             final_data = {}
#             for field, val in merged.items():
#                 default = ProgramDetails().model_dump()[field]
#                 final_data[field] = val if val not in [None, "", [], {}] else default

#         output_json = {
#             "university_name": uni_name,
#             "program_name": program_name,
#             "all_degree_program_link": all_degree_program_link,
#             "degree_type": degree_type,
#             "campuses": campuses,
#             "program_link": row.get("program_link", ""),
#             "extracted_data": final_data
#         }

#         with open(output_file, "w", encoding="utf-8") as f:
#             json.dump(output_json, f, indent=4, ensure_ascii=False)

#         print(f"  → Saved: {output_file.name}\n")
#         time.sleep(2)

#     print("All programs extracted successfully!")

# if __name__ == "__main__":
#     main()
import os, json, time
import pandas as pd
from typing import Dict, Any, Tuple, List
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from groq import Groq, RateLimitError

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================================================
# 1. FIELD REGISTRY — semantic contracts for each field
# =========================================================

FIELD_REGISTRY = {
    "program.name": "Official full name of the academic program.",
    "program.code": "Any official short code or abbreviation.",
    "program.synonyms": "Alternative names of the program if explicitly stated.",

    "degree.name": "Formal awarded degree name.",
    "degree.code": "Degree abbreviation such as BSc, MSc, PhD.",
    "degree.type": "Bachelor / Master / PhD / Diploma / Certificate.",
    "degree.synonyms": "Alternative degree names if listed.",

    "university.name": "Official university name.",
    "university.rank.type": "Ranking authority name such as QS, Times, CS.",
    "university.rank.position": "Ranking numeric position.",

    "campus.name": "Campus name.",
    "campus.webUrl": "Campus website URL.",
    "campus.email": "Campus contact email.",
    "campus.phone": "Campus phone number.",
    "campus.country": "Campus country.",
    "campus.city": "Campus city.",
    "campus.zipCode": "Campus postal code.",
    "campus.address": "Campus street address.",

    "programUrl": "Official program page URL.",

    "session.title": "Session name such as Spring, Fall.",
    "session.startDate": "Session start date.",
    "session.endDate": "Session end date.",

    "durationYear": "Total duration in years.",
    "deliveryType": "Delivery mode such as Online, On-campus, Hybrid.",

    "tuition.amount": "Annual tuition numeric amount.",
    "tuition.currency": "Currency of tuition.",
    "tuition.region": "Applicable region for tuition.",

    "application.amount": "Application fee numeric amount.",
    "application.currency": "Application fee currency.",
    "application.region": "Region for application fee.",

    "scholarship.name": "Scholarship name.",
    "scholarship.amount": "Scholarship amount.",
    "scholarship.currency": "Scholarship currency.",
    "scholarship.deadline": "Scholarship deadline."
}

# =========================================================
# 2. Prompt Builder
# =========================================================

def build_prompt(field_key: str, description: str, content: str) -> str:
    return f"""
You are a strict information extraction system.

FIELD: {field_key}
DESCRIPTION: {description}

Rules:
- Only extract if explicitly present.
- Do not infer or guess.
- Do not normalize or paraphrase.
- If not found, return empty string.
- Output only JSON.

Return exactly:
{json.dumps({field_key: ""}, indent=2)}

CONTENT:
{content}
"""

# =========================================================
# 3. LLM Call
# =========================================================

def call_llm(prompt: str) -> Dict[str, Any]:
    try:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=256
        )
        text = res.choices[0].message.content.strip()
        return json.loads(text)
    except RateLimitError:
        time.sleep(2)
        return {}
    except Exception:
        return {}

# =========================================================
# 4. Field Extraction
# =========================================================

def extract_field(field_key: str, content: str) -> Tuple[Any, bool]:
    desc = FIELD_REGISTRY[field_key]
    prompt = build_prompt(field_key, desc, content)
    result = call_llm(prompt)
    value = result.get(field_key, "")
    found = value not in ("", None, [])
    return value, found

# =========================================================
# 5. Schema Models
# =========================================================

class Program(BaseModel):
    name: str = ""
    code: str = ""
    synonyms: str = ""

class Degree(BaseModel):
    name: str = ""
    code: str = ""
    type: str = ""
    synonyms: str = ""

class Tuition(BaseModel):
    amount: str = ""
    currency: str = ""
    region: str = ""

class ApplicationFee(BaseModel):
    amount: str = ""
    currency: str = ""
    region: str = ""

class Scholarship(BaseModel):
    name: str = ""
    amount: str = ""
    currency: str = ""
    deadline: str = ""

class ExtractionResult(BaseModel):
    program: Program
    degree: Degree
    tuition: Tuition
    applicationFee: ApplicationFee
    scholarship: Scholarship
    confidence: float = 0.0

# =========================================================
# 6. Section Extractors
# =========================================================

def extract_program(content):
    name, f1 = extract_field("program.name", content)
    code, f2 = extract_field("program.code", content)
    syn, f3 = extract_field("program.synonyms", content)
    return Program(name=name, code=code, synonyms=syn), (f1 or f2 or f3)

def extract_degree(content):
    name, f1 = extract_field("degree.name", content)
    code, f2 = extract_field("degree.code", content)
    typ, f3 = extract_field("degree.type", content)
    syn, f4 = extract_field("degree.synonyms", content)
    return Degree(name=name, code=code, type=typ, synonyms=syn), (f1 or f2 or f3 or f4)

def extract_tuition(content):
    amt, f1 = extract_field("tuition.amount", content)
    cur, f2 = extract_field("tuition.currency", content)
    reg, f3 = extract_field("tuition.region", content)
    return Tuition(amount=amt, currency=cur, region=reg), (f1 or f2 or f3)

def extract_application_fee(content):
    amt, f1 = extract_field("application.amount", content)
    cur, f2 = extract_field("application.currency", content)
    reg, f3 = extract_field("application.region", content)
    return ApplicationFee(amount=amt, currency=cur, region=reg), (f1 or f2 or f3)

def extract_scholarship(content):
    name, f1 = extract_field("scholarship.name", content)
    amt, f2 = extract_field("scholarship.amount", content)
    cur, f3 = extract_field("scholarship.currency", content)
    dl, f4 = extract_field("scholarship.deadline", content)
    return Scholarship(name=name, amount=amt, currency=cur, deadline=dl), (f1 or f2 or f3 or f4)

# =========================================================
# 7. Orchestrator
# =========================================================

def extract_all(content: str) -> ExtractionResult:
    flags = []

    program, f1 = extract_program(content)
    flags.append(f1)

    degree, f2 = extract_degree(content)
    flags.append(f2)

    tuition, f3 = extract_tuition(content)
    flags.append(f3)

    app_fee, f4 = extract_application_fee(content)
    flags.append(f4)

    schol, f5 = extract_scholarship(content)
    flags.append(f5)

    confidence = sum(flags) / len(flags)

    return ExtractionResult(
        program=program,
        degree=degree,
        tuition=tuition,
        applicationFee=app_fee,
        scholarship=schol,
        confidence=confidence
    )

# =========================================================
# 8. CSV Runner
# =========================================================

def run_csv(input_csv: str, output_json: str):
    df = pd.read_csv(input_csv)
    results = []

    for idx, row in df.iterrows():
        content = str(row.get("program_content", ""))
        if not content.strip():
            continue
        result = extract_all(content)
        results.append(result.model_dump())

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Saved {len(results)} records → {output_json}")

# =========================================================
# 9. Main
# =========================================================

if __name__ == "__main__":
    run_csv("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/test.csv", "testoutput.json")

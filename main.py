import json
from pathlib import Path
import asyncio
import os

STATE_FILE = "pipeline_state.json"

# ----------------------------- CONFIG -----------------------------
INPUT_FROM_SCRIPT1 = "extracted_programs_rhode.csv"

# Same file used by both Script 2 (output) and Script 3 (input)
CONTENT_CSV = "extracted_programs_with_content_rhode.csv"

# -------------------------------------------------------------

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"last_step": 0}

def save_state(step):
    with open(STATE_FILE, 'w') as f:
        json.dump({"last_step": step}, f)
    print(f"Progress saved: Step {step} completed.\n")

def run_pipeline():
    state = load_state()
    current_step = state["last_step"]

    print(f"Resuming from step {current_step} (0 = start, 1 = after content scraping, 2 = done)\n")

    # ----------------------------- STEP 2: Scrape Content -----------------------------
    if current_step < 1:
        print("=== Running Script 2: scrape_contents.py ===")
        print("Crawling each program_link and adding program_content...\n")

        if not Path(INPUT_FROM_SCRIPT1).exists():
            print(f"ERROR: Input file not found: {INPUT_FROM_SCRIPT1}")
            print("Run your program links extraction script first.")
            return

        try:
            import scrape_contents as s2  # ← has the 's'
            asyncio.run(s2.main())
        except Exception as e:
            print(f"Error running scrape_contents.py: {e}")
            return

        # Check if file was actually created
        if not Path(CONTENT_CSV).exists():
            print(f"ERROR: Output file missing: {CONTENT_CSV}")
            return

        file_size_kb = Path(CONTENT_CSV).stat().st_size / 1024
        print(f"Content scraping completed!")
        print(f"File saved: {CONTENT_CSV} ({file_size_kb:.1f} KB)\n")
        save_state(1)

    # ----------------------------- STEP 3: Extract Structured Data -----------------------------
    if current_step < 2:
        print("=== Running Script 3: collect_field_data.py ===")
        print("Running LLM extraction → creating JSON files...\n")

        if not Path(CONTENT_CSV).exists():
            print(f"ERROR: Input file missing for Script 3: {CONTENT_CSV}")
            return

        try:
            import collect_field_data as s3
            s3.main()
        except Exception as e:
            print(f"Error in collect_field_data.py: {e}")
            return

        save_state(2)

    print("Pipeline finished successfully!")
    print("JSON files are in: extracted_structured_json/")

if __name__ == "__main__":
    run_pipeline()
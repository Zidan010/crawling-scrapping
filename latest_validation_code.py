import os
import json
import pandas as pd
import random
import string
from pathlib import Path

def load_json_file(filepath):
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error loading {filepath}: {e}")
        return None

def save_json_file(filepath, data):
    """Save JSON file safely."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving {filepath}: {e}")
        return False

def normalize_id(data):
    """
    Normalize ID handling:
    - Convert 'pid' to 'id' if 'id' doesn't exist
    - Remove prefix before underscore (e.g., 'utulsa_abc123' -> 'abc123')
    - Return the clean ID
    """
    program_id = None
    
    # Check for 'id' first, then 'pid'
    if "id" in data and data["id"]:
        program_id = data["id"]
    elif "pid" in data and data["pid"]:
        program_id = data["pid"]
        # Rename pid to id
        data["id"] = program_id
        del data["pid"]
    
    # If we have an ID, clean it
    if program_id:
        program_id_str = str(program_id).strip()
        
        # Update the data with cleaned ID
        data["id"] = program_id_str.split('_')[-1]
        return program_id_str
    
    return None

def shuffle_last_4_chars(text):
    """
    Shuffle the last 4 characters of a string.
    Used to create unique IDs for duplicate programVariants.
    """
    if len(text) < 4:
        # If string is too short, append random chars
        return text + ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    
    # Get last 4 chars, shuffle them
    last_4 = list(text[-4:])
    random.shuffle(last_4)
    return text[:-4] + ''.join(last_4)

def rename_details_to_detail(obj):
    """
    Recursively rename all 'details' keys to 'detail' in the entire JSON structure.
    """
    if isinstance(obj, dict):
        new_dict = {}
        for key, value in obj.items():
            new_key = 'detail' if key == 'details' else key
            new_dict[new_key] = rename_details_to_detail(value)
        return new_dict
    elif isinstance(obj, list):
        return [rename_details_to_detail(item) for item in obj]
    else:
        return obj

def extract_ranks_from_data(data):
    """
    Extract all ranks from data.
    Supports rank_type_1, position_1, rank_type_2, position_2, etc.
    """
    ranks = []
    idx = 1
    
    while True:
        rank_type_key = f"rank_type_{idx}" if idx > 1 else "rank_type_1"
        position_key = f"position_{idx}" if idx > 1 else "position_1"
        
        if idx == 1:
            if "rank_type" in data and data["rank_type"]:
                rank_type_key = "rank_type"
                position_key = "position"
            elif "rank_type_1" not in data:
                break
        
        rank_type = data.get(rank_type_key, "")
        position = data.get(position_key, "")
        
        if not rank_type or pd.isna(rank_type) or str(rank_type).strip() == "":
            break
        
        ranks.append({
            "type": str(rank_type).strip(),
            "position": int(position) if position and not pd.isna(position) and str(position).strip() != "" else 0
        })
        
        idx += 1
    
    return ranks

def normalize_delivery_type(delivery_type):
    """
    Normalize delivery type to one of: Online, Offline, Hybrid
    Maps common variations to standard values.
    """
    if not delivery_type or not isinstance(delivery_type, str):
        return None
    
    dt_lower = delivery_type.lower().strip()
    
    # Online mappings
    if any(keyword in dt_lower for keyword in ['online', 'distance', 'remote', 'virtual', 'e-learning']):
        return "Online"
    
    # Offline mappings
    if any(keyword in dt_lower for keyword in ['on campus', 'on-campus', 'oncampus', 'in person', 'in-person', 'face-to-face', 'offline', 'classroom']):
        return "Offline"
    
    # Hybrid mappings
    if any(keyword in dt_lower for keyword in ['hybrid', 'blended', 'mixed', 'combined']):
        return "Hybrid"
    
    # If already one of the standard values
    if delivery_type in ["Online", "Offline", "Hybrid"]:
        return delivery_type
    
    return None

def fill_missing_values_from_root(data):
    """
    Fill missing values in extracted_data.programVariants from root-level data.
    Checks: program_name, degree_name, degree_code, degree_type, department, etc.
    """
    if "extracted_data" not in data:
        return data
    
    extracted = data["extracted_data"]
    variants = extracted.get("programVariants", [])
    
    if not variants:
        return data
    
    # Root-level fallback values
    root_program_name = data.get("program_name", "")
    root_degree_code = data.get("degree_code", "")
    root_degree_type = data.get("degree_type")or data.get("degree_name")
    root_degree_name = data.get("degree_name")or data.get("degree_type")
    root_delivery_type=data.get("deliveryType", [])
    
    for variant in variants:
        identity = variant.get("programIdentity", {})
        
        # Fill program_name if empty
        if not identity.get("program_name") or identity.get("program_name") == "":
            if root_program_name and root_program_name != "":
                identity["program_name"] = root_program_name
        
        # Fill degree_code if empty
        if not identity.get("degree_code") or identity.get("degree_code") == "":
            if root_degree_code and root_degree_code != "":
                identity["degree_code"] = root_degree_code
        
        # Fill degree_type if empty
        if not identity.get("degree_type") or identity.get("degree_type") == "":
            if root_degree_type and root_degree_type != "":
                identity["degree_type"] = root_degree_type
        
        # Fill degree_name if empty
        if not identity.get("degree_name") or identity.get("degree_name") == "":
            if root_degree_name and root_degree_name != "":
                identity["degree_name"] = root_degree_name
        
        variant["programIdentity"] = identity


        sessionDelivery = variant.get("sessionDelivery", {})
        # Fill program_name if empty
        if not sessionDelivery.get("deliveryType") or sessionDelivery.get("deliveryType") == "":
            if root_delivery_type and root_delivery_type != "":
                sessionDelivery["deliveryType"] = root_delivery_type if isinstance(root_delivery_type, list) else [root_delivery_type]
        
        variant["sessionDelivery"] = sessionDelivery


    return data

def build_campus_info_with_fallback(variant, root_data):
    """
    Build campusInfo by merging variant data with root-level data.
    Priority: variant campusInfo > root-level fields
    """
    variant_campus = variant.get("campusInfo", {})
    
    fallback_campus = {}
    field_mappings = {
        "campus_name": "name",
        "url": "webUrl",
        "email": "email",
        "phone": "phone",
        "country": "country",
        "city": "city",
        "zipCode": "zipCode",
        "address": "address"
    }
    
    for root_field, campus_field in field_mappings.items():
        value = root_data.get(root_field, "")
        if value and not pd.isna(value) and str(value).strip() != "":
            fallback_campus[campus_field] = str(value).strip()
    
    fields = ["name", "webUrl", "email", "phone", "country", "city", "zipCode", "address"]
    complete_campus = {}
    
    for field in fields:
        if field in variant_campus and str(variant_campus[field]).strip() != "":
            complete_campus[field] = str(variant_campus[field]).strip()
        else:
            complete_campus[field] = fallback_campus.get(field, "")
    
    return complete_campus

def handle_duplicate_ids(variants, base_id):
    """
    Handle duplicate IDs when multiple programVariants exist.
    First variant keeps original ID, subsequent variants get shuffled IDs.
    """
    if not base_id:
        return
    
    used_ids = set()
    
    for idx, variant in enumerate(variants):
        identity = variant.get("programIdentity", {})
        
        if idx == 0:
            # First variant keeps original ID
            identity["id"] = base_id
            used_ids.add(base_id)
        else:
            # Subsequent variants get shuffled ID
            new_id = shuffle_last_4_chars(base_id)
            
            # Ensure uniqueness
            while new_id in used_ids:
                new_id = shuffle_last_4_chars(base_id)
            
            identity["id"] = new_id
            used_ids.add(new_id)
        
        variant["programIdentity"] = identity

def migrate_data_to_variants(data):
    """
    Migrate programUrl, university info into EACH programVariant.
    Move campusInfo from each variant to university.campusInfo within that variant.
    Apply fallback logic for campusInfo.
    Handle duplicate IDs for multiple variants.
    """
    if "extracted_data" not in data:
        return data
    
    extracted = data["extracted_data"]
    variants = extracted.get("programVariants", [])
    
    if not variants:
        return data
    
    program_url = data.get("programUrl", "")
    university_name = data.get("university_name", "")
    
    # Get normalized ID (handles both 'id' and 'pid', removes prefix)
    program_id = data.get("id", None)  # Already normalized by normalize_id()
    
    ranks = extract_ranks_from_data(data)
    
    # Handle duplicate IDs if multiple variants exist
    if program_id:
        handle_duplicate_ids(variants, program_id)
    
    for variant in variants:
        variant["programUrl"] = program_url
        
        university = {
            "name": university_name,
            "ranks": ranks.copy(),
            "campusInfo": {}
        }
        
        campus_info = build_campus_info_with_fallback(variant, data)
        university["campusInfo"] = campus_info
        
        if "campusInfo" in variant:
            del variant["campusInfo"]
        
        variant["university"] = university
        
        fees = variant.get("fees", {})
        if "tuitionFeePerYear" not in fees or fees["tuitionFeePerYear"] is None:
            fees["tuitionFeePerYear"] = []
        if "tuitionFeePerCredit" not in fees or fees["tuitionFeePerCredit"] is None:
            fees["tuitionFeePerCredit"] = []
        if "tuitionFeePerSemester" not in fees or fees["tuitionFeePerSemester"] is None:
            fees["tuitionFeePerSemester"] = []
        if "applicationFee" not in fees or fees["applicationFee"] is None:
            fees["applicationFee"] = []
        variant["fees"] = fees
    
    return data

def clean_scholarship_data(variant, errors, variant_prefix):
    """
    Clean scholarship data:
    - If name > 100 chars, add to validation report
    - If name == detail, set detail to ""
    """
    scholarships = variant.get("scholarships", {}).get("scholarships", [])
    
    if isinstance(scholarships, list):
        for sch_idx, sch in enumerate(scholarships):
            name = sch.get("name", "")
            detail = sch.get("detail", "")
            
            # Check if name > 100 chars
            if name and len(name) > 100:
                errors.append(
                    f"{variant_prefix}: scholarships[{sch_idx}].name exceeds 100 characters (length: {len(name)})"
                )
            
            # If name == detail, clear detail
            if name and detail and name == detail:
                sch["detail"] = ""
    
    return scholarships

def clean_general_requirements(variant, errors, variant_prefix):
    """
    Clean general requirements data:
    - If title > 100 chars, add to validation report
    - If title == detail, set detail to ""
    """
    gen_reqs = variant.get("generalRequirements", {}).get("generalRequirements", [])
    
    if isinstance(gen_reqs, list):
        for req_idx, req in enumerate(gen_reqs):
            title = req.get("title", "")
            detail = req.get("detail", "")
            
            # Check if title > 100 chars
            if title and len(title) > 100:
                errors.append(
                    f"{variant_prefix}: generalRequirements[{req_idx}].title exceeds 100 characters (length: {len(title)})"
                )
            
            # If title == detail, clear detail
            if title and detail and title == detail:
                req["detail"] = ""
    
    return gen_reqs

def clean_standardized_requirements(variant, errors, variant_prefix):
    """
    Clean standardized requirements:
    - Only keep tests with type in: GRE, GMAT, SAT
    - Remove any other test types
    """
    std_reqs = variant.get("standardizedRequirements", {}).get("standardizedRequirements", [])
    allowed_types = {"GRE", "GMAT", "SAT","LSAT","ACT"}
    
    if isinstance(std_reqs, list):
        valid_reqs = []
        for req_idx, req in enumerate(std_reqs):
            test = req.get("test", {})
            test_type = test.get("type", "")
            
            if test_type in allowed_types:
                valid_reqs.append(req)
            elif test_type:
                errors.append(
                    f"{variant_prefix}: standardizedRequirements[{req_idx}].test.type '{test_type}' is invalid (removed). Only GRE/GMAT/SAT allowed."
                )
        
        variant["standardizedRequirements"]["standardizedRequirements"] = valid_reqs

def clean_language_requirements(variant, errors, variant_prefix):
    """
    Clean language requirements:
    - Only keep tests with type in: IELTS, TOEFL, Duolingo, PTE, English Language Proficiency
    - Remove any other test types
    """
    lang_reqs = variant.get("languageRequirements", {}).get("languageRequirements", [])
    allowed_types = {"IELTS", "COPE","TOEFL", "Duolingo", "PTE", "English Language Proficiency"}
    
    if isinstance(lang_reqs, list):
        valid_reqs = []
        for req_idx, req in enumerate(lang_reqs):
            test = req.get("test", {})
            test_type = test.get("type", "")
            
            if test_type in allowed_types:
                valid_reqs.append(req)
            elif test_type:
                errors.append(
                    f"{variant_prefix}: languageRequirements[{req_idx}].test.type '{test_type}' is invalid (removed). Only IELTS/TOEFL/Duolingo/PTE/English Language Proficiency allowed."
                )
        
        variant["languageRequirements"]["languageRequirements"] = valid_reqs

def validate_campus_info(variant, errors, variant_prefix):
    """
    Validate that campusInfo has required fields: webUrl, name, city, country
    """
    university = variant.get("university", {})
    campus = university.get("campusInfo", {})
    
    required_fields = ["webUrl", "name", "city", "country"]
    
    for field in required_fields:
        value = campus.get(field, "")
        if not value or value == "":
            errors.append(
                f"{variant_prefix}: university.campusInfo.{field} is missing or empty (required field)"
            )

def validate_useful_links(variant, errors, variant_prefix):
    """
    Validate that usefulLink entries have valid URLs.
    Remove entries with invalid webLink.
    """
    useful_links = variant.get("usefulLink", [])
    
    if isinstance(useful_links, list):
        valid_links = []
        for link_idx, link in enumerate(useful_links):
            webLink = link.get("webLink", "").strip()
            
            # Check if webLink is valid
            if not webLink or webLink == "":
                errors.append(
                    f"{variant_prefix}: usefulLink[{link_idx}].webLink is empty (removed)"
                )
                continue
            
            if not webLink.lower().startswith("http"):
                errors.append(
                    f"{variant_prefix}: usefulLink[{link_idx}].webLink is invalid (must start with http/https) (removed)"
                )
                continue
            
            # Check title
            title = link.get("title", "").strip()
            if not title or title == "":
                errors.append(
                    f"{variant_prefix}: usefulLink[{link_idx}].title is empty"
                )
            
            valid_links.append(link)
        
        variant["usefulLink"] = valid_links

def normalize_delivery_types(variant, errors, variant_prefix):
    """
    Normalize deliveryType values to only: Online, Offline, Hybrid
    Try to map common variations, otherwise remove invalid values.
    """
    session_delivery = variant.get("sessionDelivery", {})
    delivery_types = session_delivery.get("deliveryType", [])
    
    if isinstance(delivery_types, list) and delivery_types:
        normalized_types = []
        invalid_types = []
        
        for dt in delivery_types:
            normalized = normalize_delivery_type(dt)
            
            if normalized:
                if normalized not in normalized_types:  # Avoid duplicates
                    normalized_types.append(normalized)
            else:
                invalid_types.append(str(dt))
        
        # Update with normalized values
        session_delivery["deliveryType"] = normalized_types
        
        # Report invalid values that were removed
        if invalid_types:
            errors.append(
                f"{variant_prefix}: sessionDelivery.deliveryType had invalid values that couldn't be mapped: {invalid_types} (removed)"
            )

def validate_required_fields(data, filename):
    """
    Validate required fields in extracted_data.
    Returns: (is_valid, list_of_errors)
    
    UPDATED BEHAVIOR:
    - Always save the file (don't skip)
    - Add detailed validation errors to report
    """
    errors = []
    
    if "extracted_data" not in data:
        errors.append("Missing extracted_data")
        return True, errors
    
    extracted = data["extracted_data"]
    variants = extracted.get("programVariants", [])
    
    if not variants or len(variants) == 0:
        errors.append("Empty programVariants")
        return True, errors
    
    for idx, variant in enumerate(variants):
        variant_prefix = f"Variant[{idx}]"
        
        # Clean and validate scholarships
        clean_scholarship_data(variant, errors, variant_prefix)
        
        # Clean and validate general requirements
        clean_general_requirements(variant, errors, variant_prefix)
        
        # Clean standardized requirements (remove invalid test types)
        clean_standardized_requirements(variant, errors, variant_prefix)
        
        # Clean language requirements (remove invalid test types)
        clean_language_requirements(variant, errors, variant_prefix)
        
        # Normalize delivery types
        normalize_delivery_types(variant, errors, variant_prefix)
        
        # Validate campusInfo required fields
        validate_campus_info(variant, errors, variant_prefix)
        
        # Validate and clean usefulLinks
        validate_useful_links(variant, errors, variant_prefix)
        
        # Check university
        university = variant.get("university", {})
        if not university:
            errors.append(f"{variant_prefix}: Missing university object")
            continue
        
        if not university.get("name"):
            if "name" in university and university["name"] == "":
                errors.append(f"{variant_prefix}: university.name is empty")
        
        # Check programIdentity
        identity = variant.get("programIdentity", {})
        
        program_name = identity.get("program_name", "")
        if program_name == "" and "program_name" in identity:
            errors.append(f"{variant_prefix}: programIdentity.program_name is empty")
        
        degree_name = identity.get("degree_name", "")
        degree_type = identity.get("degree_type", "")
        
        if "degree_name" in identity and degree_name == "":
            errors.append(f"{variant_prefix}: programIdentity.degree_name is empty")
        if "degree_type" in identity and degree_type == "":
            errors.append(f"{variant_prefix}: programIdentity.degree_type is empty")
        
        # Session title validation
        sessions = variant.get("sessionDelivery", {}).get("session", [])
        allowed_titles = {"Fall", "Summer", "Spring"}
        
        if isinstance(sessions, list):
            filtered_sessions = [
                s for s in sessions 
                if s.get("title") in allowed_titles
            ]
            variant["sessionDelivery"]["session"] = filtered_sessions
            
            for sess_idx, session in enumerate(sessions):
                if "title" in session and session.get("title") == "":
                    errors.append(f"{variant_prefix}: sessionDelivery.session[{sess_idx}].title is empty")
        
        # Admission timeline validation
        timelines = variant.get("admissionTimeline", {}).get("admissionTimeline", [])
        if isinstance(timelines, list):
            for tl_idx, timeline in enumerate(timelines):
                if "type" in timeline and timeline.get("type") == "":
                    errors.append(f"{variant_prefix}: admissionTimeline[{tl_idx}].type is empty")
        
        # Fees validation and cleanup
        fees = variant.get("fees", {})
        
        tuition_fees = fees.get("tuitionFeePerYear", [])
        if isinstance(tuition_fees, list):
            fees["tuitionFeePerYear"] = [
                f for f in tuition_fees 
                if isinstance(f, dict) and f.get("amount") != 0 and f.get("currency") != ""
            ]
        
        tuition_fees_cr = fees.get("tuitionFeePerCredit", [])
        if isinstance(tuition_fees_cr, list):
            fees["tuitionFeePerCredit"] = [
                f for f in tuition_fees_cr 
                if isinstance(f, dict) and f.get("amount") != 0 and f.get("currency") != ""
            ]
        tuition_fees_se = fees.get("tuitionFeePerSemester", [])
        if isinstance(tuition_fees_se, list):
            fees["tuitionFeePerSemester"] = [
                f for f in tuition_fees_se 
                if isinstance(f, dict) and f.get("amount") != 0 and f.get("currency") != ""
            ]



        app_fees = fees.get("applicationFee", [])
        if isinstance(app_fees, list):
            fees["applicationFee"] = [
                f for f in app_fees 
                if isinstance(f, dict) and f.get("amount") != 0 and f.get("currency") != ""
            ]
        
        total_credit = variant.get("totalCredit", 0)
        
        # Ensure totalCredit is an integer
        if total_credit is None:
            variant["totalCredit"] = 0
        elif not isinstance(total_credit, int):
            try:
                variant["totalCredit"] = int(total_credit)
            except (ValueError, TypeError):
                errors.append(
                    f"{variant_prefix}: totalCredit has invalid type ('{type(total_credit).__name__}'), set to 0"
                )
                variant["totalCredit"] = 0
        
        # Optional: Check if totalCredit is negative (if you want to flag this)
        if variant["totalCredit"] < 0:
            errors.append(
                f"{variant_prefix}: totalCredit is negative ({variant['totalCredit']}), should be >= 0"
            )
            variant["totalCredit"] = 0


        
        # How to apply validation
        how_to_apply = variant.get("howToApply", {}).get("howToApply", [])
        if isinstance(how_to_apply, list):
            for step_idx, step in enumerate(how_to_apply):
                if "title" in step and step.get("title") == "":
                    errors.append(f"{variant_prefix}: howToApply[{step_idx}].title is empty")
        
        # Program types validation
        program_types = variant.get("admissionProgramTypes", {}).get("admissionProgramTypes", [])
        if isinstance(program_types, list):
            for pt_idx, ptype in enumerate(program_types):
                if "type" in ptype and ptype.get("type") == "":
                    errors.append(f"{variant_prefix}: admissionProgramTypes[{pt_idx}].type is empty")
                if "overview" in ptype and ptype.get("overview") == "":
                    errors.append(f"{variant_prefix}: admissionProgramTypes[{pt_idx}].overview is empty")
        
        # Degree requirements validation
        deg_reqs = variant.get("degreeRequirements", {}).get("degreeRequirements", [])
        if isinstance(deg_reqs, list):
            for req_idx, req in enumerate(deg_reqs):
                test = req.get("test", {})
                if "type" in test and test.get("type") == "":
                    errors.append(f"{variant_prefix}: degreeRequirements[{req_idx}].test.type is empty")
        
        # Scholarships validation (already cleaned above)
        scholarships = variant.get("scholarships", {}).get("scholarships", [])
        if isinstance(scholarships, list):
            for sch_idx, sch in enumerate(scholarships):
                if "type" in sch and sch.get("type") == "":
                    errors.append(f"{variant_prefix}: scholarships[{sch_idx}].type is empty")
                if "name" in sch:
                    name = sch.get("name", "")
                    if name == "":
                        errors.append(f"{variant_prefix}: scholarships[{sch_idx}].name is empty")
    
    # Always return True to save all files
    return True, errors

def process_all_files(input_folder, output_folder, report_csv="validation_report.csv"):
    """
    Process all JSON files in input_folder.
    - Normalize ID (handle pid/id, remove prefix)
    - Rename 'details' to 'detail'
    - Fill missing values from root
    - Migrate data
    - Validate
    - Save ALL files to output_folder (with validation errors in report)
    - Generate detailed report
    """
    os.makedirs(output_folder, exist_ok=True)
    
    json_files = list(Path(input_folder).glob("*.json"))
    total_files = len(json_files)
    
    print(f"Found {total_files} JSON files to process...")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Report will be saved to: {report_csv}\n")
    
    results = []
    processed = 0
    saved_count = 0
    error_count = 0
    
    for json_file in json_files:
        filename = json_file.name
        print(f"\n[{processed+1}/{total_files}] Processing: {filename}")
        
        # Load JSON
        data = load_json_file(json_file)
        if data is None:
            results.append({
                "filename": filename,
                "program_idx": "",
                "program_name": "",
                "university_name": "",
                "status": "LOAD_ERROR",
                "error_count": 1,
                "errors": "Failed to load JSON file"
            })
            error_count += 1
            processed += 1
            continue
        
        # Step 0: Normalize ID (handle pid/id, remove prefix)
        print("  ↳ Normalizing ID...")
        normalize_id(data)
        
        # Step 1: Rename 'details' to 'detail' throughout the entire JSON
        print("  ↳ Renaming 'details' to 'detail'...")
        data = rename_details_to_detail(data)
        
        # Step 2: Fill missing values from root
        print("  ↳ Filling missing values from root data...")
        data = fill_missing_values_from_root(data)
        
        # Step 3: Migrate data
        print("  ↳ Migrating data to variants...")
        data = migrate_data_to_variants(data)
        
        # Step 4: Validate
        print("  ↳ Validating required fields...")
        is_valid, validation_errors = validate_required_fields(data, filename)
        
        # Always save
        print(f"  💾 Saving to output folder...")
        output_path = Path(output_folder) / filename
        
        if save_json_file(output_path, data):
            print(f"  ✅ Saved to: {output_path}")
            saved_count += 1
            
            if validation_errors:
                print(f"  ⚠️ Saved with {len(validation_errors)} validation warnings")
                for err in validation_errors[:5]:
                    print(f"     - {err}")
                if len(validation_errors) > 5:
                    print(f"     ... and {len(validation_errors)-5} more warnings")
                status = "SAVED_WITH_WARNINGS"
            else:
                status = "VALID"
        else:
            status = "SAVE_FAILED"
            error_count += 1
        
        # Record result
        results.append({
            "filename": filename,
            "program_idx": data.get("program_idx", ""),
            "program_name": data.get("program_name", ""),
            "university_name": data.get("university_name", ""),
            "status": status,
            "error_count": len(validation_errors),
            "errors": " | ".join(validation_errors) if validation_errors else ""
        })
        
        processed += 1
    
    # Generate report CSV
    df_report = pd.DataFrame(results)
    report_path = Path(output_folder) / Path(report_csv).name
    df_report.to_csv(report_path, index=False, encoding='utf-8')
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"✅ PROCESSING COMPLETE!")
    print(f"{'='*70}")
    print(f"Total files processed:        {total_files}")
    print(f"Files saved successfully:     {saved_count}")
    print(f"Files with errors:            {error_count}")
    print(f"Success rate:                 {(saved_count/total_files)*100:.1f}%")
    print(f"\nAll files saved to:           {output_folder}")
    print(f"Validation report saved to:   {report_path}")
    print(f"{'='*70}")
    
    # Show breakdown by status
    print(f"\nStatus Breakdown:")
    status_counts = df_report['status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Show files with most errors
    print(f"\nTop 10 Files with Most Validation Warnings:")
    top_errors = df_report.nlargest(10, 'error_count')[['filename', 'error_count', 'status']]
    print(top_errors.to_string(index=False))
    
    return df_report

if __name__ == "__main__":
    INPUT_FOLDER = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-3_output_final_program_data/updated_extracted_jsons_uobc_van_UGprograms"
    OUTPUT_FOLDER = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/latest_validated_data/uobc_van_UGprograms_validated"
    REPORT_CSV = "validation_report.csv"
    
    df_report = process_all_files(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        report_csv=REPORT_CSV
    )
    
    print(f"\n✅ Done! Check the validation report for detailed results.")
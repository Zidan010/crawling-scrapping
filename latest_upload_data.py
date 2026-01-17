import os
import json
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_log.txt'),
        logging.StreamHandler()
    ]
)


def save_validated_before_upload(file_path: str, cleaned_extracted_data: dict):
    save_dir = Path("backend_ready_data_uot_Gprogram")
    save_dir.mkdir(exist_ok=True)

    filename = Path(file_path).name
    save_path = save_dir / filename

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_extracted_data, f, indent=2, ensure_ascii=False)

    logging.info(f"💾 Saved validated JSON before CURL 1 → {save_path}")


def save_backend_ready_data(file_path: str, backend_data: dict, variant_idx: int = 0):
    """Save the transformed backend-ready data for debugging"""
    save_dir = Path("backend_ready_data_uot_Gprogram")
    save_dir.mkdir(exist_ok=True)
    filename = Path(file_path).stem + f"_variant{variant_idx}_backend_ready.json"
    save_path = save_dir / filename
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(backend_data, f, indent=2, ensure_ascii=False)
    
    logging.info(f"💾 Saved backend-ready data → {save_path}")

class AdmissionUploader:
    def __init__(self, auth_token: str, api_base_url: str = "https://api.studyfound.com/services/admission/api"):
        """
        Initialize the uploader with authentication token and API base URL
        
        Args:
            auth_token: Bearer token for API authentication
            api_base_url: Base URL for the API endpoints
        """
        self.auth_token = auth_token
        self.api_base_url = api_base_url
        self.headers = {
            'accept': '*/*',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {auth_token}'
        }
    
    def transform_to_backend_format(self, variant: Dict) -> Optional[Dict]:
        """
        Transform a single variant to backend expected format.
        
        Args:
            variant: Single variant from programVariants[]
            
        Returns:
            Dict in backend expected format, or None if transformation fails
        """
        try:
            # Get programIdentity
            program_identity = variant.get('programIdentity', {})
            
            # Build backend format  
            backend_data = {

                "id":program_identity.get('id', ''),
                "program": {
                    "name": program_identity.get('program_name', ''),
                    "code": "",  # Not mapped - leave empty
                    "synonyms": ""
                },
                "degree": {
                    "name": program_identity.get('degree_name', ''),
                    "code": program_identity.get('degree_code', ''),  # Mapped to degree.code only
                    "type": program_identity.get('degree_type', ''),
                    "synonyms": ""
                },
                "university": {
                    "name": variant.get('university', {}).get('name', ''),
                    "ranks": variant.get('university', {}).get('ranks', []),
                    "campus": variant.get('university', {}).get('campusInfo', {})  # campusInfo → campus
                },
                "department": program_identity.get('department', ''),
                "programUrl": variant.get('programUrl', ''),
                "overview": program_identity.get('general_overview', ''),  # Capital O
                "session": variant.get('sessionDelivery', {}).get('session', []),
                "durationYear": variant.get('sessionDelivery', {}).get('durationYear', 0),
                "deliveryType": variant.get('sessionDelivery', {}).get('deliveryType', []),
                "admissionTimeline": variant.get('admissionTimeline', {}).get('admissionTimeline', []),
                "tuitionFeePerYear": variant.get('fees', {}).get('tuitionFeePerYear', []),
                "applicationFee": variant.get('fees', {}).get('applicationFee', []),
                "howToApply": variant.get('howToApply', {}).get('howToApply', []),
                "admissionProgramTypes": variant.get('admissionProgramTypes', {}).get('admissionProgramTypes', []),
                "generalRequirements": variant.get('generalRequirements', {}).get('generalRequirements', []),
                "standardizedRequirements": variant.get('standardizedRequirements', {}).get('standardizedRequirements', []),
                "languageRequirements": variant.get('languageRequirements', {}).get('languageRequirements', []),
                "degreeRequirements": variant.get('degreeRequirements', {}).get('degreeRequirements', []),
                "scholarships": variant.get('scholarships', {}).get('scholarships', []),
                "usefulLink": variant.get('usefulLink', [])
            }
            
            return backend_data
            
        except Exception as e:
            logging.error(f"✗ Error transforming variant: {str(e)}")
            return None
    
    def upload_extracted_data(self, backend_data: Dict, variant_info: str = "") -> Tuple[bool, Optional[str]]:
        """
        Upload backend-formatted data to create admission endpoint (CURL 1)
        
        Args:
            backend_data: Data in backend expected format
            variant_info: Info string for logging (e.g., "Variant 0")
            
        Returns:
            Tuple of (success: bool, id: Optional[str])
        """
        url = f"{self.api_base_url}/admissions/create"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=backend_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # The ID is in the 'detail' field
                admission_id = response_data.get('detail')
                
                logging.info(f"✓ CURL 1 successful {variant_info}. Admission ID: {admission_id}")
                return True, admission_id
            else:
                logging.error(f"✗ CURL 1 failed {variant_info}. Status: {response.status_code}, Response: {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"✗ CURL 1 request error {variant_info}: {str(e)}")
            return False, None
    
    def upload_raw_data(self, raw_json_data: Dict, admission_id: Optional[str], status: str, variant_info: str = "") -> bool:
        """
        Upload complete original JSON data to raw endpoint (CURL 2)
        
        Args:
            raw_json_data: The complete original JSON data (validated structure)
            admission_id: The ID from CURL 1 (if successful)
            status: "success" or "failed"
            variant_info: Info string for logging
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        url = f"{self.api_base_url}/admission/raw"

        # Create a copy of raw_json_data and remove program_content
        raw_json_data_copy = raw_json_data.copy()
        if 'program_content' in raw_json_data_copy:
            raw_json_data_copy.pop('program_content')
            logging.info(f"🗑️  Removed 'program_content' field from raw data upload {variant_info}")
        
        # Prepare the payload for CURL 2
        payload = {
            "data": raw_json_data_copy,
            "status": status
        }

        
        # Add ID only if CURL 1 was successful
        # if admission_id:
        #     payload["id"] = admission_id
        
        payload["id"] = admission_id




        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logging.info(f"✓ CURL 2 successful {variant_info}. Status: {status}, ID: {admission_id if admission_id else 'N/A'}")
                return True
            else:
                logging.error(f"✗ CURL 2 failed {variant_info}. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"✗ CURL 2 request error {variant_info}: {str(e)}")
            return False
    
    def process_json_file(self, file_path: str, save_backend_format: bool = True) -> Dict[str, any]:
        """
        Process a single validated JSON file through both upload steps.
        Creates one admission per variant (Option B).
        
        Args:
            file_path: Path to the validated JSON file
            save_backend_format: Whether to save transformed backend format for debugging
            
        Returns:
            Dict with processing results
        """
        logging.info(f"\n{'='*70}")
        logging.info(f"Processing: {Path(file_path).name}")
        logging.info(f"{'='*70}")
        
        result = {
            'file': file_path,
            'total_variants': 0,
            'variants_processed': [],
            'error': None
        }
        
        try:
            # Load validated JSON file (RAW DATA - after validation)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_json_data = json.load(f)
            
            logging.info(f"📂 Loaded validated JSON file")
            
            # Extract variants
            extracted = raw_json_data.get('extracted_data', {})
            variants = extracted.get('programVariants', [])
            
            if not variants or len(variants) == 0:
                result['error'] = "No programVariants found in extracted_data"
                logging.error(f"✗ {result['error']}")
                return result
            
            result['total_variants'] = len(variants)
            logging.info(f"📊 Found {len(variants)} variant(s) to process")
            
            # Process each variant (Option B: Create multiple admissions)
            for idx, variant in enumerate(variants):
                variant_info = f"[Variant {idx+1}/{len(variants)}]"
                logging.info(f"\n{'-'*70}")
                logging.info(f"Processing {variant_info}")
                logging.info(f"{'-'*70}")
                
                variant_result = {
                    'variant_index': idx,
                    'program_name': variant.get('programIdentity', {}).get('program_name', 'Unknown'),
                    'degree_name': variant.get('programIdentity', {}).get('degree_name', 'Unknown'),
                    'curl1_success': False,
                    'curl2_success': False,
                    'admission_id': None,
                    'error': None
                }
                
                # Transform variant to backend format
                logging.info(f"🔄 Transforming {variant_info} to backend format...")
                backend_data = self.transform_to_backend_format(variant)
                

                program_identity = variant.get('programIdentity', {})
                id=program_identity.get('id', '')







                if backend_data is None:
                    variant_result['error'] = "Failed to transform variant to backend format"
                    logging.error(f"✗ {variant_result['error']}")
                    result['variants_processed'].append(variant_result)
                    continue
                
                logging.info(f"✓ Transformation successful {variant_info}")
                
                # Optionally save backend format for debugging
                if save_backend_format:
                    save_backend_ready_data(file_path, backend_data, idx)
                
                # Step 1: Upload backend-formatted data (CURL 1)
                logging.info(f"📤 Uploading {variant_info} to CURL 1 (create admission)...")
                curl1_success, admission_id = self.upload_extracted_data(backend_data, variant_info)
                variant_result['curl1_success'] = curl1_success
                variant_result['admission_id'] = admission_id
                
                # Step 2: Upload RAW validated data (CURL 2)
                # Note: We upload the COMPLETE original JSON, not just this variant
                if curl1_success and admission_id:
                    # CURL 1 successful - upload with ID and status="success"
                    logging.info(f"📤 Uploading {variant_info} to CURL 2 (raw data) with ID: {admission_id}...")
                    curl2_success = self.upload_raw_data(raw_json_data, admission_id, "success", variant_info)
                else:
                    # CURL 1 failed - upload without ID and status="failed"
                    logging.info(f"📤 Uploading {variant_info} to CURL 2 (raw data) without ID (CURL 1 failed)...")
                    curl2_success = self.upload_raw_data(raw_json_data, id, "failed", variant_info)
                
                variant_result['curl2_success'] = curl2_success
                
                # Summary for this variant
                if variant_result['curl1_success'] and variant_result['curl2_success']:
                    logging.info(f"✅✅ Both uploads successful {variant_info}")
                elif variant_result['curl2_success']:
                    logging.warning(f"⚠️ CURL 1 failed but CURL 2 succeeded {variant_info}")
                else:
                    logging.error(f"❌❌ Upload failed {variant_info}")
                
                result['variants_processed'].append(variant_result)
            
            # Overall file summary
            successful_variants = sum(1 for v in result['variants_processed'] if v['curl1_success'] and v['curl2_success'])
            logging.info(f"\n{'='*70}")
            logging.info(f"📊 File Summary: {successful_variants}/{len(variants)} variant(s) uploaded successfully")
            logging.info(f"{'='*70}")
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            logging.error(f"✗ {error_msg}")
            result['error'] = error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(f"✗ {error_msg}")
            import traceback
            logging.error(traceback.format_exc())
            result['error'] = error_msg
        
        return result
    
    def process_folder(self, folder_path: str, skip_files: List[str] = None) -> Dict[str, any]:
        """
        Process all validated JSON files in a folder
        
        Args:
            folder_path: Path to the folder containing validated JSON files
            skip_files: List of filenames to skip (optional)
            
        Returns:
            Dict with overall statistics
        """
        folder = Path(folder_path)
        
        if not folder.exists():
            logging.error(f"Folder does not exist: {folder_path}")
            return {'error': 'Folder not found'}
        
        # Get all JSON files
        json_files = list(folder.glob('*.json'))
        
        if not json_files:
            logging.warning(f"No JSON files found in {folder_path}")
            return {'error': 'No JSON files found'}
        
        # Skip specified files
        if skip_files is None:
            skip_files = []
        
        # Add common files to skip
        default_skip = ['upload_results.json', 'validation_report.csv']
        skip_files.extend(default_skip)
        
        # Filter out files to skip
        filtered_files = []
        for json_file in json_files:
            if json_file.name not in skip_files:
                filtered_files.append(json_file)
            else:
                logging.info(f"⏭️  Skipping: {json_file.name}")
        
        json_files = filtered_files
        
        if not json_files:
            logging.warning(f"No JSON files to process after filtering")
            return {'error': 'No JSON files to process'}
        
        logging.info(f"\n{'='*70}")
        logging.info(f"Found {len(json_files)} validated JSON files to upload")
        logging.info(f"{'='*70}\n")
        
        results = []
        stats = {
            'total_files': len(json_files),
            'files_processed': 0,
            'files_with_errors': 0,
            'total_variants': 0,
            'variants_both_successful': 0,
            'variants_curl1_failed_curl2_success': 0,
            'variants_both_failed': 0,
            'variants_with_errors': 0
        }
        
        # Process each file
        for idx, json_file in enumerate(json_files, 1):
            logging.info(f"\n{'#'*70}")
            logging.info(f"FILE [{idx}/{len(json_files)}]")
            logging.info(f"{'#'*70}")
            
            result = self.process_json_file(str(json_file))
            results.append(result)
            
            # Update statistics
            if result.get('error'):
                stats['files_with_errors'] += 1
            else:
                stats['files_processed'] += 1
                stats['total_variants'] += result['total_variants']
                
                # Count variant outcomes
                for variant_result in result['variants_processed']:
                    if variant_result.get('error'):
                        stats['variants_with_errors'] += 1
                    elif variant_result['curl1_success'] and variant_result['curl2_success']:
                        stats['variants_both_successful'] += 1
                    elif not variant_result['curl1_success'] and variant_result['curl2_success']:
                        stats['variants_curl1_failed_curl2_success'] += 1
                    else:
                        stats['variants_both_failed'] += 1
        
        # Print summary
        logging.info(f"\n{'='*70}")
        logging.info("📊 FINAL UPLOAD SUMMARY")
        logging.info(f"{'='*70}")
        logging.info(f"Files:")
        logging.info(f"  Total files:                  {stats['total_files']}")
        logging.info(f"  Files processed successfully: {stats['files_processed']}")
        logging.info(f"  Files with errors:            {stats['files_with_errors']}")
        logging.info(f"\nVariants:")
        logging.info(f"  Total variants:               {stats['total_variants']}")
        logging.info(f"  ✅ Both CURLs successful:     {stats['variants_both_successful']}")
        logging.info(f"  ⚠️  CURL 1 failed, CURL 2 OK: {stats['variants_curl1_failed_curl2_success']}")
        logging.info(f"  ❌ Both CURLs failed:         {stats['variants_both_failed']}")
        logging.info(f"  ❌ Variants with errors:      {stats['variants_with_errors']}")
        
        if stats['total_variants'] > 0:
            success_rate = (stats['variants_both_successful'] / stats['total_variants'] * 100)
            logging.info(f"\n📈 Overall success rate:        {success_rate:.1f}%")
        
        logging.info(f"{'='*70}\n")
        
        return {
            'statistics': stats,
            'detailed_results': results
        }

# Main execution
if __name__ == "__main__":
    # Configuration
    AUTH_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJzcyIsInN1YiI6IjUxNjRlNTNhLTE2ZDItNDExOC05YWU2LTZlODQ1NGE4NzJiYSIsImV4cCI6MTc2ODU4NTgyMCwiZW1haWwiOiJzYXppZGFuNTU5QGdtYWlsLmNvbSIsInNjb3BlIjoidXNlciBhZG1pbiJ9.zKR2pWPFoxOpDmzmuXvEvzIOK4uCnVNRq_8g_OA1kicYP7bD-ymGx5Z379brsoiDvenPgk_e4S5ydQxdxyqXgA"
    
    # Use the validated output folder from validation script
    VALIDATED_FOLDER = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/uot_Gprogram_raw_data-validate"
    
    # Files to skip (if any)
    SKIP_FILES = []
    
    # Initialize uploader
    uploader = AdmissionUploader(auth_token=AUTH_TOKEN)
    
    # Process all validated files
    results = uploader.process_folder(VALIDATED_FOLDER, skip_files=SKIP_FILES)
    
    # Save detailed results
    with open('upload_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logging.info("📄 Detailed results saved to 'upload_results.json'")
    logging.info("🏁 Upload processing complete!")

# ## **Key Corrections Made:**

# ### **✅ Q1 - Field Mappings:**
# - ✅ `program.code` = `""` (not mapped, left empty)
# - ✅ `degree.code` = `programIdentity.degree_code` (only degree.code is mapped)
# - ✅ `admissionTimeline` is used (not "W")

# ### **✅ Q2 - Multiple Variants (Option B):**
# - ✅ Processes **ALL variants** in `programVariants[]`
# - ✅ Creates **one admission per variant** (separate CURL 1 + CURL 2 for each)
# - ✅ Tracks statistics per variant
# - ✅ Logs detailed progress for each variant

# ### **✅ Q3 - Missing Fields:**
# - ✅ `program.synonyms` = `""`
# - ✅ `degree.synonyms` = `""`

# ### **✅ Q4 - admissionTimeline:**
# - ✅ Uses `admissionTimeline` everywhere (no "W")

# ### **✅ Q5 - CURL 2 Raw Data:**
# - ✅ Uploads **complete original JSON** (`raw_json_data`) without transformation
# - ✅ Same raw data uploaded for all variants from that file

# ### **✅ campusInfo → campus:**
# - ✅ `variant.university.campusInfo` → `university.campus` in backend format

# ## **Processing Flow:**
# ```
# For each JSON file:
#   For each variant in programVariants[]:
#     1. Transform variant → backend format
#     2. CURL 1: Upload backend format → Get admission_id
#     3. CURL 2: Upload complete raw JSON with admission_id
# ```

# ## **Example Statistics Output:**
# ```
# 📊 FINAL UPLOAD SUMMARY
# ======================================================================
# Files:
#   Total files:                  10
#   Files processed successfully: 10
#   Files with errors:            0

# Variants:
#   Total variants:               25  (some files had multiple variants)
#   ✅ Both CURLs successful:     22
#   ⚠️  CURL 1 failed, CURL 2 OK: 2
#   ❌ Both CURLs failed:         1
#   ❌ Variants with errors:      0

# 📈 Overall success rate:        88.0%
# ======================================================================
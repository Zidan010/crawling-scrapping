# import os
# import json
# import requests
# from pathlib import Path
# from typing import Dict, Optional, Tuple
# import logging

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.FileHandler('upload_log.txt'),
#         logging.StreamHandler()
#     ]
# )

# class AdmissionUploader:
#     def __init__(self, auth_token: str, api_base_url: str = "https://api.studyfound.com/services/admission/api"):
#         """
#         Initialize the uploader with authentication token and API base URL
        
#         Args:
#             auth_token: Bearer token for API authentication
#             api_base_url: Base URL for the API endpoints
#         """
#         self.auth_token = auth_token
#         self.api_base_url = api_base_url
#         self.headers = {
#             'accept': '*/*',
#             'Content-Type': 'application/json',
#             'Authorization': f'Bearer {auth_token}'
#         }
        
#     def upload_extracted_data(self, extracted_data: Dict) -> Tuple[bool, Optional[str]]:
#         """
#         Upload extracted_data to create admission endpoint (CURL 1)
        
#         Args:
#             extracted_data: The extracted_data field from the JSON file
            
#         Returns:
#             Tuple of (success: bool, id: Optional[str])
#         """
#         url = f"{self.api_base_url}/admissions/create"
        
#         try:
#             response = requests.post(
#                 url,
#                 headers=self.headers,
#                 json=extracted_data,
#                 timeout=30
#             )
            
#             if response.status_code in [200, 201]:
#                 response_data = response.json()
                
#                 # The ID is in the 'detail' field
#                 admission_id = response_data.get('detail')
                
#                 logging.info(f"✓ First curl successful. ID: {admission_id}")
#                 return True, admission_id
#             else:
#                 logging.error(f"✗ First curl failed. Status: {response.status_code}, Response: {response.text}")
#                 return False, None
                
#         except requests.exceptions.RequestException as e:
#             logging.error(f"✗ First curl request error: {str(e)}")
#             return False, None
    
#     def upload_raw_data(self, full_json_data: Dict, admission_id: Optional[str], status: str) -> bool:
#         """
#         Upload full JSON data to raw endpoint (CURL 2)
        
#         Args:
#             full_json_data: The complete JSON data from the file
#             admission_id: The ID from first curl (if successful)
#             status: "success" or "failed"
            
#         Returns:
#             bool: True if upload was successful, False otherwise
#         """
#         url = f"{self.api_base_url}/admission/raw"
        
#         # Prepare the payload for second curl
#         payload = {
#             "data": full_json_data,
#             "status": status
#         }
        
#         # Add ID only if first curl was successful
#         if admission_id:
#             payload["id"] = admission_id
        
#         try:
#             response = requests.post(
#                 url,
#                 headers=self.headers,
#                 json=payload,
#                 timeout=30
#             )
            
#             if response.status_code in [200, 201]:
#                 logging.info(f"✓ Second curl successful. Status: {status}")
#                 return True
#             else:
#                 logging.error(f"✗ Second curl failed. Status: {response.status_code}, Response: {response.text}")
#                 return False
                
#         except requests.exceptions.RequestException as e:
#             logging.error(f"✗ Second curl request error: {str(e)}")
#             return False
    
#     def process_json_file(self, file_path: str) -> Dict[str, any]:
#         """
#         Process a single JSON file through both upload steps
        
#         Args:
#             file_path: Path to the JSON file
            
#         Returns:
#             Dict with processing results
#         """
#         logging.info(f"\n{'='*60}")
#         logging.info(f"Processing: {file_path}")
#         logging.info(f"{'='*60}")
        
#         result = {
#             'file': file_path,
#             'first_curl_success': False,
#             'second_curl_success': False,
#             'admission_id': None,
#             'error': None
#         }
        
#         try:
#             # Load JSON file
#             with open(file_path, 'r', encoding='utf-8') as f:
#                 json_data = json.load(f)
            
#             # Extract the extracted_data field
#             extracted_data = json_data.get('extracted_data')
            
#             if not extracted_data:
#                 error_msg = "No 'extracted_data' field found in JSON"
#                 logging.error(f"✗ {error_msg}")
#                 result['error'] = error_msg
#                 return result
            
#             # Step 1: Upload extracted_data (CURL 1)
#             first_success, admission_id = self.upload_extracted_data(extracted_data)
#             result['first_curl_success'] = first_success
#             result['admission_id'] = admission_id
            
#             # Step 2: Upload raw data (CURL 2)
#             if first_success and admission_id:
#                 # First curl successful - upload with ID and status="success"
#                 second_success = self.upload_raw_data(json_data, admission_id, "success")
#             else:
#                 # First curl failed - upload without ID and status="failed"
#                 second_success = self.upload_raw_data(json_data, None, "failed")
            
#             result['second_curl_success'] = second_success
            
#             # Summary
#             if result['first_curl_success'] and result['second_curl_success']:
#                 logging.info(f"✓✓ Both uploads successful for {file_path}")
#             elif result['second_curl_success']:
#                 logging.warning(f"⚠ First curl failed but second curl succeeded for {file_path}")
#             else:
#                 logging.error(f"✗✗ Upload failed for {file_path}")
                
#         except json.JSONDecodeError as e:
#             error_msg = f"Invalid JSON format: {str(e)}"
#             logging.error(f"✗ {error_msg}")
#             result['error'] = error_msg
#         except Exception as e:
#             error_msg = f"Unexpected error: {str(e)}"
#             logging.error(f"✗ {error_msg}")
#             result['error'] = error_msg
        
#         return result
    
#     def process_folder(self, folder_path: str, skip_files: list = None) -> Dict[str, any]:
#         """
#         Process all JSON files in a folder
        
#         Args:
#             folder_path: Path to the folder containing JSON files
#             skip_files: List of filenames to skip (optional)
            
#         Returns:
#             Dict with overall statistics
#         """
#         folder = Path(folder_path)
        
#         if not folder.exists():
#             logging.error(f"Folder does not exist: {folder_path}")
#             return {'error': 'Folder not found'}
        
#         # Get all JSON files
#         json_files = list(folder.glob('*.json'))
        
#         if not json_files:
#             logging.warning(f"No JSON files found in {folder_path}")
#             return {'error': 'No JSON files found'}
        
#         # Skip specified files
#         if skip_files is None:
#             skip_files = []
        
#         # Add common log files to skip list
#         default_skip = ['extraction_log.jsonl']
#         skip_files.extend(default_skip)
        
#         # Filter out files to skip
#         filtered_files = []
#         for json_file in json_files:
#             if json_file.name not in skip_files:
#                 filtered_files.append(json_file)
#             else:
#                 logging.info(f"⏭️  Skipping: {json_file.name}")
        
#         json_files = filtered_files
        
#         if not json_files:
#             logging.warning(f"No JSON files to process after filtering")
#             return {'error': 'No JSON files to process'}
        
#         logging.info(f"\nFound {len(json_files)} JSON files to process\n")
        
#         results = []
#         stats = {
#             'total': len(json_files),
#             'both_successful': 0,
#             'first_failed_second_success': 0,
#             'both_failed': 0,
#             'errors': 0
#         }
        
#         # Process each file
#         for json_file in json_files:
#             result = self.process_json_file(str(json_file))
#             results.append(result)
            
#             # Update statistics
#             if result.get('error'):
#                 stats['errors'] += 1
#             elif result['first_curl_success'] and result['second_curl_success']:
#                 stats['both_successful'] += 1
#             elif not result['first_curl_success'] and result['second_curl_success']:
#                 stats['first_failed_second_success'] += 1
#             else:
#                 stats['both_failed'] += 1
        
#         # Print summary
#         logging.info(f"\n{'='*60}")
#         logging.info("SUMMARY")
#         logging.info(f"{'='*60}")
#         logging.info(f"Total files: {stats['total']}")
#         logging.info(f"✓✓ Both curls successful: {stats['both_successful']}")
#         logging.info(f"⚠ First failed, second success: {stats['first_failed_second_success']}")
#         logging.info(f"✗✗ Both failed: {stats['both_failed']}")
#         logging.info(f"✗ Errors (file/parsing): {stats['errors']}")
#         logging.info(f"{'='*60}\n")
        
#         return {
#             'statistics': stats,
#             'detailed_results': results
#         }


# # Main execution
# # Main execution
# if __name__ == "__main__":
#     # Configuration
#     AUTH_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJzcyIsInN1YiI6IjgwODZiNGU4LTg0N2EtNGMwZi1iY2EwLTc0ODBjOGViN2ViMiIsImV4cCI6MTc2NzI2NDYyOSwiZW1haWwiOiJhbWJpdGlvbml4eEBnbWFpbC5jb20iLCJzY29wZSI6InVzZXIgYWRtaW4ifQ.H5hGsWAMxY_GZTCvnw725owbCmFk9akbu4daKeUZiPnh7A2RCW-HpgZhlBeOSoWPkrivzXIVwEd7EQrSwQJEOw"
#     FOLDER_PATH = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-3_output_final_program_data/extracted_structured_json_utulsa_latest"
    
#     # Files to skip (add any filenames you want to skip)
#     SKIP_FILES = [
#         'extraction_log.jsonl'
#         ]
    
#     # Initialize uploader
#     uploader = AdmissionUploader(auth_token=AUTH_TOKEN)
    
#     # Process all files in folder
#     results = uploader.process_folder(FOLDER_PATH, skip_files=SKIP_FILES)
    
#     # Save detailed results to JSON file
#     with open('upload_results.json', 'w', encoding='utf-8') as f:
#         json.dump(results, f, indent=2, ensure_ascii=False)
    
#     logging.info("Detailed results saved to 'upload_results.json'")
#     logging.info("Processing complete!")


###new## testing

import os
import json
import requests
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

# Import validation functions from validate.py
from validate import fix_json_data

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
    save_dir = Path("validated_before_curl1")
    save_dir.mkdir(exist_ok=True)

    filename = Path(file_path).name
    save_path = save_dir / filename

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(cleaned_extracted_data, f, indent=2, ensure_ascii=False)

    logging.info(f"💾 Saved validated JSON before CURL 1 → {save_path}")

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
        
    def upload_extracted_data(self, extracted_data: Dict) -> Tuple[bool, Optional[str]]:
        """
        Upload extracted_data to create admission endpoint (CURL 1)
        
        Args:
            extracted_data: The extracted_data field from the JSON file
            
        Returns:
            Tuple of (success: bool, id: Optional[str])
        """
        url = f"{self.api_base_url}/admissions/create"
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=extracted_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                response_data = response.json()
                
                # The ID is in the 'detail' field
                admission_id = response_data.get('detail')
                
                logging.info(f"✓ First curl successful. ID: {admission_id}")
                return True, admission_id
            else:
                logging.error(f"✗ First curl failed. Status: {response.status_code}, Response: {response.text}")
                return False, None
                
        except requests.exceptions.RequestException as e:
            logging.error(f"✗ First curl request error: {str(e)}")
            return False, None
    
    def upload_raw_data(self, full_json_data: Dict, admission_id: Optional[str], status: str) -> bool:
        """
        Upload full JSON data to raw endpoint (CURL 2)
        
        Args:
            full_json_data: The complete JSON data from the file
            admission_id: The ID from first curl (if successful)
            status: "success" or "failed"
            
        Returns:
            bool: True if upload was successful, False otherwise
        """
        url = f"{self.api_base_url}/admission/raw"
        

        # Create a copy and remove program_content field
        data_to_upload = full_json_data.copy()
        data_to_upload.pop('program_content', None)  # Remove program_content if it exists

        # Prepare the payload for second curl
        payload = {
            "data": data_to_upload,
            "status": status
        }
        
        # Add ID only if first curl was successful
        if admission_id:
            payload["id"] = admission_id
        
        try:
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                logging.info(f"✓ Second curl successful. Status: {status}")
                return True
            else:
                logging.error(f"✗ Second curl failed. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logging.error(f"✗ Second curl request error: {str(e)}")
            return False
    
    def process_json_file(self, file_path: str) -> Dict[str, any]:
        """
        Process a single JSON file through both upload steps
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dict with processing results
        """
        logging.info(f"\n{'='*60}")
        logging.info(f"Processing: {file_path}")
        logging.info(f"{'='*60}")
        
        result = {
            'file': file_path,
            'first_curl_success': False,
            'second_curl_success': False,
            'admission_id': None,
            'error': None
        }
        
        try:
            # Load JSON file (RAW DATA)
            with open(file_path, 'r', encoding='utf-8') as f:
                raw_json_data = json.load(f)
            
            # === RECONSTRUCT extracted_data using the latest robust logic ===
            extracted_data = {
                'program': {'name': '', 'code': '', 'synonyms': ''},
                'degree': {'name': '', 'code': '', 'type': '', 'synonyms': ''},
                'department': '',
                'session': [],
                'durationYear': 0,
                'deliveryType': [],
                'admissionTimeline': [],
                'tuitionFeePerYear': [],
                'applicationFee': [],
                'howToApply': [],
                'admissionProgramTypes': [],
                'generalRequirements': [],
                'standardizedRequirements': [],
                'languageRequirements': [],
                'degreeRequirements': [],
                'scholarships': [],
                'usefulLink': [],
                'university': {
                    'name': raw_json_data.get('university_name', '').strip(),
                    'ranks': [],
                    'campus': {}
                },
                'programUrl': raw_json_data.get('programUrl', '').strip()
            }

            # Try to get from programVariants first
            variant = {}
            raw_extracted = raw_json_data.get('extracted_data', {})
            if 'programVariants' in raw_extracted and raw_extracted['programVariants']:
                variant = raw_extracted['programVariants'][0]

            if variant:
                pi = variant.get('programIdentity', {})
                extracted_data['program']['name'] = pi.get('program_name', '').strip()
                extracted_data['degree']['name'] = pi.get('degree_name', '').strip()
                extracted_data['program']['code'] = pi.get('degree_code', '').strip()
                extracted_data['degree']['code'] = pi.get('degree_code', '').strip()
                extracted_data['department'] = pi.get('department', '').strip()
                extracted_data['overview'] = pi.get('general_overview', '').strip()
                extracted_data['degree']['type'] = pi.get('degree_type', '').strip()

                sd = variant.get('sessionDelivery', {})
                extracted_data['session'] = sd.get('session', [])
                extracted_data['durationYear'] = sd.get('durationYear', 0)
                extracted_data['deliveryType'] = sd.get('deliveryType', [])

                extracted_data['admissionTimeline'] = variant.get('admissionTimeline', {}).get('admissionTimeline', [])
                extracted_data['tuitionFeePerYear'] = variant.get('fees', {}).get('tuitionFeePerYear', [])
                extracted_data['applicationFee'] = variant.get('fees', {}).get('applicationFee', [])
                extracted_data['howToApply'] = variant.get('howToApply', {}).get('howToApply', [])
                extracted_data['admissionProgramTypes'] = variant.get('admissionProgramTypes', {}).get('admissionProgramTypes', [])
                extracted_data['generalRequirements'] = variant.get('generalRequirements', {}).get('generalRequirements', [])
                extracted_data['standardizedRequirements'] = variant.get('standardizedRequirements', {}).get('standardizedRequirements', [])
                extracted_data['languageRequirements'] = variant.get('languageRequirements', {}).get('languageRequirements', [])
                extracted_data['degreeRequirements'] = variant.get('degreeRequirements', {}).get('degreeRequirements', [])
                extracted_data['scholarships'] = variant.get('scholarships', {}).get('scholarships', [])

                raw_ul = variant.get('usefulLink', [])
                if isinstance(raw_ul, list):
                    extracted_data['usefulLink'] = raw_ul
                elif isinstance(raw_ul, dict):
                    extracted_data['usefulLink'] = raw_ul.get('usefulLink', [])

                extracted_data['university']['campus'] = variant.get('campusInfo', {})

            # Fallback: Use top-level fields if no variant
            if not variant:
                if 'program_name' in raw_json_data:
                    extracted_data['program']['name'] = raw_json_data['program_name'].strip()
                if 'deliveryType' in raw_json_data and isinstance(raw_json_data['deliveryType'], list):
                    extracted_data['deliveryType'] = raw_json_data['deliveryType']
                extracted_data['usefulLink'] = []  # Never fill with junk

            # Copy country into campus
            if 'country' in raw_json_data and raw_json_data['country']:
                campus = extracted_data['university']['campus']
                if not campus.get('country'):
                    campus['country'] = raw_json_data['country'].strip()

            # VALIDATION: Clean the extracted_data using validate.py
            logging.info("🔍 Validating and cleaning extracted_data...")
            
            # Wrap extracted_data for validation (validate.py expects this structure)
            temp_data = {'extracted_data': extracted_data}
            
            # Apply validation and fixes
            validated_data = fix_json_data(temp_data)
            
            # Extract the cleaned extracted_data
            cleaned_extracted_data = validated_data['extracted_data']
            
            logging.info("✓ Data validation complete")
            save_validated_before_upload(file_path, cleaned_extracted_data)

            # Step 1: Upload CLEANED extracted_data (CURL 1)
            first_success, admission_id = self.upload_extracted_data(cleaned_extracted_data)
            result['first_curl_success'] = first_success
            result['admission_id'] = admission_id
            
            # Step 2: Upload RAW data (CURL 2) - use original unmodified data
            if first_success and admission_id:
                # First curl successful - upload with ID and status="success"
                second_success = self.upload_raw_data(raw_json_data, admission_id, "success")
            else:
                # First curl failed - upload without ID and status="failed"
                second_success = self.upload_raw_data(raw_json_data, None, "failed")
            
            result['second_curl_success'] = second_success
            
            # Summary
            if result['first_curl_success'] and result['second_curl_success']:
                logging.info(f"✓✓ Both uploads successful for {file_path}")
            elif result['second_curl_success']:
                logging.warning(f"⚠ First curl failed but second curl succeeded for {file_path}")
            else:
                logging.error(f"✗✗ Upload failed for {file_path}")
                
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            logging.error(f"✗ {error_msg}")
            result['error'] = error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logging.error(f"✗ {error_msg}")
            result['error'] = error_msg
        
        return result
    
    def process_folder(self, folder_path: str, skip_files: list = None) -> Dict[str, any]:
        """
        Process all JSON files in a folder
        
        Args:
            folder_path: Path to the folder containing JSON files
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
        
        # Add common log files to skip list
        default_skip = ['extraction_log.jsonl']
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
        
        logging.info(f"\nFound {len(json_files)} JSON files to process\n")
        
        results = []
        stats = {
            'total': len(json_files),
            'both_successful': 0,
            'first_failed_second_success': 0,
            'both_failed': 0,
            'errors': 0
        }
        
        # Process each file
        for json_file in json_files:
            result = self.process_json_file(str(json_file))
            results.append(result)
            
            # Update statistics
            if result.get('error'):
                stats['errors'] += 1
            elif result['first_curl_success'] and result['second_curl_success']:
                stats['both_successful'] += 1
            elif not result['first_curl_success'] and result['second_curl_success']:
                stats['first_failed_second_success'] += 1
            else:
                stats['both_failed'] += 1
        
        # Print summary
        logging.info(f"\n{'='*60}")
        logging.info("SUMMARY")
        logging.info(f"{'='*60}")
        logging.info(f"Total files: {stats['total']}")
        logging.info(f"✓✓ Both curls successful: {stats['both_successful']}")
        logging.info(f"⚠ First failed, second success: {stats['first_failed_second_success']}")
        logging.info(f"✗✗ Both failed: {stats['both_failed']}")
        logging.info(f"✗ Errors (file/parsing): {stats['errors']}")
        logging.info(f"{'='*60}\n")
        
        return {
            'statistics': stats,
            'detailed_results': results
        }

# Main execution
if __name__ == "__main__":
    # Configuration
    AUTH_TOKEN = "eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJzcyIsInN1YiI6IjgwODZiNGU4LTg0N2EtNGMwZi1iY2EwLTc0ODBjOGViN2ViMiIsImV4cCI6MTc2NzU0MTYyOCwiZW1haWwiOiJhbWJpdGlvbml4eEBnbWFpbC5jb20iLCJzY29wZSI6InVzZXIgYWRtaW4ifQ.iRGkmkrB57l3Hx7pUjoJDCLz6b23NoQ1fHXDdU6ru6HY3kGMbXOrAqcoohYWQVJnYvD5oJ_6OAseOg0dra09hQ"
    FOLDER_PATH = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/test_utulsa-2"
    
    # Files to skip (add any filenames you want to skip)
    SKIP_FILES = [
        'extraction_log.jsonl'
    ]
    
    # Initialize uploader
    uploader = AdmissionUploader(auth_token=AUTH_TOKEN)
    
    # Process all files in folder
    results = uploader.process_folder(FOLDER_PATH, skip_files=SKIP_FILES)
    
    # Save detailed results to JSON file
    with open('upload_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    logging.info("Detailed results saved to 'upload_results.json'")
    logging.info("Processing complete!")




## Key Changes Made:

# 1. **Import validation function**: Added `from validate import fix_json_data` at the top

# 2. **Data flow in `process_json_file`**:
#    - Load the **raw JSON data** from file
#    - Extract `extracted_data` field
#    - **Validate and clean** the `extracted_data` using `fix_json_data()`
#    - Upload the **cleaned** `extracted_data` via CURL 1
#    - Upload the **original raw** JSON data via CURL 2

# 3. **Preservation of raw data**: The original `raw_json_data` is kept unchanged and used for CURL 2, ensuring you store the unmodified original data in the database

# 4. **Added logging**: Shows when validation is happening with a "🔍 Validating and cleaning extracted_data..." message

# ## File Structure Required:

# Make sure both files are in the same directory:
# ```
# your_project/
# ├── validate.py          # Your validation code
# └── upload_data.py       # This modified upload code
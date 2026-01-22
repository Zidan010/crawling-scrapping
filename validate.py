# import json
# import os
# import re
# from urllib.parse import urlparse

# def fix_json_data(data):
#     # This function fixes fields in the JSON data by setting them to empty/default if they fail validation.
#     # For strings: set to ""
#     # For lists: set to []
#     # For dicts: set to {}
#     # For numbers: set to 0
#     # For bool: set to False
#     # Nested structures are handled recursively.

#     # Top-level fields

#     # university_name: Should be a non-empty string
#     if 'university_name' in data:
#         if not isinstance(data['university_name'], str) or not data['university_name'].strip():
#             data['university_name'] = ""

#     # program_name: Should be a non-empty string
#     if 'program_name' in data:
#         if not isinstance(data['program_name'], str) or not data['program_name'].strip():
#             data['program_name'] = ""

#     # degree_type: Should be a string
#     if 'degree_type' in data:
#         if not isinstance(data['degree_type'], str):
#             data['degree_type'] = ""

#     # program_content: Should be a string
#     if 'program_content' in data:
#         if not isinstance(data['program_content'], str):
#             data['program_content'] = ""

#     # degree_program_link: Should be a valid URL string if present
#     if 'degree_program_link' in data:
#         if not isinstance(data['degree_program_link'], str):
#             data['degree_program_link'] = ""
#         elif data['degree_program_link']:
#             parsed = urlparse(data['degree_program_link'])
#             if not all([parsed.scheme, parsed.netloc]):
#                 data['degree_program_link'] = ""

#     # programUrl: Should be a valid URL string
#     if 'programUrl' in data:
#         if not isinstance(data['programUrl'], str):
#             data['programUrl'] = ""
#         elif data['programUrl']:
#             parsed = urlparse(data['programUrl'])
#             if not all([parsed.scheme, parsed.netloc]):
#                 data['programUrl'] = ""

#     # rank_type: Should be a string
#     if 'rank_type' in data:
#         if not isinstance(data['rank_type'], str):
#             data['rank_type'] = ""

#     # position: Should be a string of digits or empty
#     if 'position' in data:
#         if not isinstance(data['position'], str):
#             data['position'] = ""
#         elif data['position'] and not data['position'].isdigit():
#             data['position'] = ""

#     # campus_name: Should be a string
#     if 'campus_name' in data:
#         if not isinstance(data['campus_name'], str):
#             data['campus_name'] = ""

#     # url: Should be a valid URL if present
#     if 'url' in data:
#         if not isinstance(data['url'], str):
#             data['url'] = ""
#         elif data['url']:
#             parsed = urlparse(data['url'])
#             if not all([parsed.scheme, parsed.netloc]):
#                 data['url'] = ""

#     # email: Should be valid email if present
#     email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
#     if 'email' in data:
#         if not isinstance(data['email'], str):
#             data['email'] = ""
#         elif data['email'] and not email_pattern.match(data['email']):
#             data['email'] = ""

#     # phone: Should be a string
#     if 'phone' in data:
#         if not isinstance(data['phone'], str):
#             data['phone'] = ""

#     # country: Should be a string
#     if 'country' in data:
#         if not isinstance(data['country'], str):
#             data['country'] = ""

#     # city: Should be a string
#     if 'city' in data:
#         if not isinstance(data['city'], str):
#             data['city'] = ""

#     # zipCode: Should be a string
#     if 'zipCode' in data:
#         if not isinstance(data['zipCode'], str):
#             data['zipCode'] = ""

#     # address: Should be a string
#     if 'address' in data:
#         if not isinstance(data['address'], str):
#             data['address'] = ""

#     # admissionProgramTypes_overview: Should be a string
#     if 'admissionProgramTypes_overview' in data:
#         if not isinstance(data['admissionProgramTypes_overview'], str):
#             data['admissionProgramTypes_overview'] = ""

#     # category_name: Should be a string
#     if 'category_name' in data:
#         if not isinstance(data['category_name'], str):
#             data['category_name'] = ""

#     # first_layer: Should be a valid URL if present
#     if 'first_layer' in data:
#         if not isinstance(data['first_layer'], str):
#             data['first_layer'] = ""
#         elif data['first_layer']:
#             parsed = urlparse(data['first_layer'])
#             if not all([parsed.scheme, parsed.netloc]):
#                 data['first_layer'] = ""

#     # extracted_data: Should be a dict
#     if 'extracted_data' in data:
#         if not isinstance(data['extracted_data'], dict):
#             data['extracted_data'] = {}
#         else:
#             ed = data['extracted_data']

#             # program: dict
#             if 'program' in ed:
#                 if not isinstance(ed['program'], dict):
#                     ed['program'] = {}
#                 else:
#                     p = ed['program']
#                     if 'name' in p and not isinstance(p['name'], str):
#                         p['name'] = ""
#                     if 'code' in p and not isinstance(p['code'], str):
#                         p['code'] = ""
#                     if 'synonyms' in p and not isinstance(p['synonyms'], str):
#                         p['synonyms'] = ""

#             # degree: dict
#             if 'degree' in ed:
#                 if not isinstance(ed['degree'], dict):
#                     ed['degree'] = {}
#                 else:
#                     d = ed['degree']
#                     if 'name' in d and not isinstance(d['name'], str):
#                         d['name'] = ""
#                     if 'code' in d and not isinstance(d['code'], str):
#                         d['code'] = ""
#                     if 'type' in d and not isinstance(d['type'], str):
#                         d['type'] = ""
#                     if 'synonyms' in d and not isinstance(d['synonyms'], str):
#                         d['synonyms'] = ""

#             # university: dict
#             if 'university' in ed:
#                 if not isinstance(ed['university'], dict):
#                     ed['university'] = {}
#                 else:
#                     u = ed['university']
#                     if 'name' in u and not isinstance(u['name'], str):
#                         u['name'] = ""
#                     if 'ranks' in u:
#                         if not isinstance(u['ranks'], list):
#                             u['ranks'] = []
#                         else:
#                             new_ranks = []
#                             for rank in u['ranks']:
#                                 if isinstance(rank, dict):
#                                     if 'type' in rank and not isinstance(rank['type'], str):
#                                         continue  # skip invalid
#                                     if 'position' in rank and not isinstance(rank['position'], int):
#                                         continue
#                                     new_ranks.append(rank)
#                             u['ranks'] = new_ranks
#                     if 'campus' in u:
#                         if not isinstance(u['campus'], dict):
#                             u['campus'] = {}
#                         else:
#                             c = u['campus']
#                             if 'name' in c and not isinstance(c['name'], str):
#                                 c['name'] = ""
#                             if 'name' in c:
#                                 name = c['name'].lower()
#                                 if ("in-person & online" in name or "in-person" in name or "online" in name):
#                                     c['name'] = ""
#                             if 'webUrl' in c and not isinstance(c['webUrl'], str):
#                                 c['webUrl'] = ""
#                             elif c.get('webUrl'):
#                                 parsed = urlparse(c['webUrl'])
#                                 if not all([parsed.scheme, parsed.netloc]):
#                                     c['webUrl'] = ""
#                             if 'email' in c and not isinstance(c['email'], str):
#                                 c['email'] = ""
#                             elif c.get('email') and not email_pattern.match(c['email']):
#                                 c['email'] = ""
#                             if 'phone' in c and not isinstance(c['phone'], str):
#                                 c['phone'] = ""
#                             if 'country' in c:
#                                 if not isinstance(c['country'], str) or c['country'] != "USA":
#                                     c['country'] = "USA"  # Force to USA as per update
#                             if 'city' in c and not isinstance(c['city'], str):
#                                 c['city'] = ""
#                             if 'zipCode' in c and not isinstance(c['zipCode'], str):
#                                 c['zipCode'] = ""
#                             if 'address' in c and not isinstance(c['address'], str):
#                                 c['address'] = ""

#             # programUrl in extracted
#             if 'programUrl' in ed:
#                 if not isinstance(ed['programUrl'], str):
#                     ed['programUrl'] = ""
#                 elif ed['programUrl']:
#                     parsed = urlparse(ed['programUrl'])
#                     if not all([parsed.scheme, parsed.netloc]):
#                         ed['programUrl'] = ""

#             # session: list
#             if 'session' in ed:
#                 if not isinstance(ed['session'], list):
#                     ed['session'] = []
#                 else:
#                     new_sessions = []
#                     for s in ed['session']:
#                         if isinstance(s, dict):
#                             if 'title' in s:
#                                 if not isinstance(s['title'], str):
#                                     s['title'] = ""
#                                 else:
#                                     title_lower = s['title'].lower()
#                                     if title_lower and not any(season in title_lower for season in ['summer', 'fall', 'spring']):
#                                         s['title'] = ""
#                             new_sessions.append(s)
#                         # if not dict, skip
#                     ed['session'] = new_sessions

#             # durationYear: number
#             if 'durationYear' in ed:
#                 if not isinstance(ed['durationYear'], (int, float)):
#                     ed['durationYear'] = 0

#             # deliveryType: list
#             if 'deliveryType' in ed:
#                 if not isinstance(ed['deliveryType'], list):
#                     ed['deliveryType'] = []

#             # admissionTimeline: list
#             if 'admissionTimeline' in ed:
#                 if not isinstance(ed['admissionTimeline'], list):
#                     ed['admissionTimeline'] = []

#             # tuitionFeePerYear: list
#             if 'tuitionFeePerYear' in ed:
#                 if not isinstance(ed['tuitionFeePerYear'], list):
#                     ed['tuitionFeePerYear'] = []

#             # applicationFee: list
#             if 'applicationFee' in ed:
#                 if not isinstance(ed['applicationFee'], list):
#                     ed['applicationFee'] = []

#             # howToApply: list of dicts
#             if 'howToApply' in ed:
#                 if not isinstance(ed['howToApply'], list):
#                     ed['howToApply'] = []
#                 else:
#                     new_how = []
#                     for h in ed['howToApply']:
#                         if isinstance(h, dict):
#                             if 'title' in h and not isinstance(h['title'], str):
#                                 h['title'] = ""
#                             if 'detail' in h and not isinstance(h['detail'], str):
#                                 h['detail'] = ""
#                             if 'webLink' in h and not isinstance(h['webLink'], str):
#                                 h['webLink'] = ""
#                             elif h.get('webLink'):
#                                 parsed = urlparse(h['webLink'])
#                                 if not all([parsed.scheme, parsed.netloc]):
#                                     h['webLink'] = ""
#                             new_how.append(h)
#                     ed['howToApply'] = new_how

#             # admissionProgramTypes: list of dicts
#             if 'admissionProgramTypes' in ed:
#                 if not isinstance(ed['admissionProgramTypes'], list):
#                     ed['admissionProgramTypes'] = []
#                 else:
#                     new_apt = []
#                     for apt in ed['admissionProgramTypes']:
#                         if isinstance(apt, dict):
#                             if 'type' in apt and not isinstance(apt['type'], str):
#                                 apt['type'] = ""
#                             if 'overview' in apt and not isinstance(apt['overview'], str):
#                                 apt['overview'] = ""
#                             if 'department' in apt and not isinstance(apt['department'], str):
#                                 apt['department'] = ""
#                             if 'courseOutline' in apt:
#                                 if not isinstance(apt['courseOutline'], list):
#                                     apt['courseOutline'] = []
#                                 else:
#                                     new_co = []
#                                     for co in apt['courseOutline']:
#                                         if isinstance(co, dict):
#                                             if 'title' in co and not isinstance(co['title'], str):
#                                                 co['title'] = ""
#                                             if 'detail' in co and not isinstance(co['detail'], str):
#                                                 co['detail'] = ""
#                                             new_co.append(co)
#                                     apt['courseOutline'] = new_co
#                             new_apt.append(apt)
#                     ed['admissionProgramTypes'] = new_apt

#             # generalRequirements: list of dicts
#             if 'generalRequirements' in ed:
#                 if not isinstance(ed['generalRequirements'], list):
#                     ed['generalRequirements'] = []
#                 else:
#                     new_gr = []
#                     for gr in ed['generalRequirements']:
#                         if isinstance(gr, dict):
#                             if 'type' in gr and not isinstance(gr['type'], str):
#                                 gr['type'] = ""
#                             if 'title' in gr and not isinstance(gr['title'], str):
#                                 gr['title'] = ""
#                             if 'page' in gr and not isinstance(gr['page'], int):
#                                 gr['page'] = 0
#                             if 'words' in gr and not isinstance(gr['words'], int):
#                                 gr['words'] = 0
#                             if 'count' in gr and not isinstance(gr['count'], int):
#                                 gr['count'] = 0
#                             if 'details' in gr and not isinstance(gr['details'], str):
#                                 gr['details'] = ""
#                             new_gr.append(gr)
#                     ed['generalRequirements'] = new_gr

#             # standardizedRequirements: list of dicts
#             if 'standardizedRequirements' in ed:
#                 if not isinstance(ed['standardizedRequirements'], list):
#                     ed['standardizedRequirements'] = []
#                 else:
#                     new_sr = []
#                     for sr in ed['standardizedRequirements']:
#                         if isinstance(sr, dict):
#                             if 'test' in sr:
#                                 if not isinstance(sr['test'], dict):
#                                     sr['test'] = {}
#                                 else:
#                                     t = sr['test']
#                                     if 'type' in t and not isinstance(t['type'], str):
#                                         t['type'] = ""
#                                     if 'total' in t and not isinstance(t['total'], (int, float)):
#                                         t['total'] = 0
#                                     if 'verbal' in t and not isinstance(t['verbal'], (int, float)):
#                                         t['verbal'] = 0
#                                     if 'quant' in t and not isinstance(t['quant'], (int, float)):
#                                         t['quant'] = 0
#                                     if 'awa' in t and not isinstance(t['awa'], (int, float)):
#                                         t['awa'] = 0
#                                     if 'required' in t and not isinstance(t['required'], bool):
#                                         t['required'] = False
#                             new_sr.append(sr)
#                     ed['standardizedRequirements'] = new_sr

#             # languageRequirements: list of dicts
#             if 'languageRequirements' in ed:
#                 if not isinstance(ed['languageRequirements'], list):
#                     ed['languageRequirements'] = []
#                 else:
#                     new_lr = []
#                     for lr in ed['languageRequirements']:
#                         if isinstance(lr, dict):
#                             if 'test' in lr:
#                                 if not isinstance(lr['test'], dict):
#                                     lr['test'] = {}
#                                 else:
#                                     t = lr['test']
#                                     if 'type' in t and not isinstance(t['type'], str):
#                                         t['type'] = ""
#                                     if 'total' in t and not isinstance(t['total'], (int, float)):
#                                         t['total'] = 0
#                                     if 'listening' in t and not isinstance(t['listening'], (int, float)):
#                                         t['listening'] = 0
#                                     if 'reading' in t and not isinstance(t['reading'], (int, float)):
#                                         t['reading'] = 0
#                                     if 'writing' in t and not isinstance(t['writing'], (int, float)):
#                                         t['writing'] = 0
#                                     if 'speaking' in t and not isinstance(t['speaking'], (int, float)):
#                                         t['speaking'] = 0
#                                     if 'required' in t and not isinstance(t['required'], bool):
#                                         t['required'] = False
#                             new_lr.append(lr)
#                     ed['languageRequirements'] = new_lr

#             # degreeRequirements: list of dicts
#             if 'degreeRequirements' in ed:
#                 if not isinstance(ed['degreeRequirements'], list):
#                     ed['degreeRequirements'] = []
#                 else:
#                     new_dr = []
#                     for dr in ed['degreeRequirements']:
#                         if isinstance(dr, dict):
#                             if 'test' in dr:
#                                 if not isinstance(dr['test'], dict):
#                                     dr['test'] = {}
#                                 else:
#                                     t = dr['test']
#                                     if 'details' in t and not isinstance(t['details'], str):
#                                         t['details'] = ""
#                                     if 'type' in t and not isinstance(t['type'], str):
#                                         t['type'] = ""
#                                     if 'total' in t and not isinstance(t['total'], (int, float)):
#                                         t['total'] = 0
#                                     if 'outOf' in t and not isinstance(t['outOf'], (int, float)):
#                                         t['outOf'] = 0
#                                     if 'region' in t and not isinstance(t['region'], str):
#                                         t['region'] = ""
#                             new_dr.append(dr)
#                     ed['degreeRequirements'] = new_dr

#             # scholarships: list of dicts
#             if 'scholarships' in ed:
#                 if not isinstance(ed['scholarships'], list):
#                     ed['scholarships'] = []
#                 else:
#                     new_sch = []
#                     for sch in ed['scholarships']:
#                         if isinstance(sch, dict):
#                             if 'type' in sch and not isinstance(sch['type'], str):
#                                 sch['type'] = ""
#                             if 'name' in sch and not isinstance(sch['name'], str):
#                                 sch['name'] = ""
#                             if 'requirement' in sch:
#                                 if not isinstance(sch['requirement'], list):
#                                     sch['requirement'] = []
#                                 else:
#                                     sch['requirement'] = [r for r in sch['requirement'] if isinstance(r, str)]
#                             if 'detail' in sch and not isinstance(sch['detail'], str):
#                                 sch['detail'] = ""
#                             if 'amount' in sch and not isinstance(sch['amount'], (int, float)):
#                                 sch['amount'] = 0
#                             if 'currency' in sch and not isinstance(sch['currency'], str):
#                                 sch['currency'] = ""
#                             if 'webLink' in sch and not isinstance(sch['webLink'], str):
#                                 sch['webLink'] = ""
#                             elif sch.get('webLink'):
#                                 parsed = urlparse(sch['webLink'])
#                                 if not all([parsed.scheme, parsed.netloc]):
#                                     sch['webLink'] = ""
#                             if 'deadline' in sch and not isinstance(sch['deadline'], str):
#                                 sch['deadline'] = ""
#                             new_sch.append(sch)
#                     ed['scholarships'] = new_sch

#             # usefulLink: list of dicts
#             if 'usefulLink' in ed:
#                 if not isinstance(ed['usefulLink'], list):
#                     ed['usefulLink'] = []
#                 else:
#                     new_ul = []
#                     for ul in ed['usefulLink']:
#                         if isinstance(ul, dict):
#                             if 'title' in ul and not isinstance(ul['title'], str):
#                                 ul['title'] = ""
#                             if 'detail' in ul and not isinstance(ul['detail'], str):
#                                 ul['detail'] = ""
#                             if 'webLink' in ul and not isinstance(ul['webLink'], str):
#                                 ul['webLink'] = ""
#                             elif ul.get('webLink'):
#                                 parsed = urlparse(ul['webLink'])
#                                 if not all([parsed.scheme, parsed.netloc]):
#                                     ul['webLink'] = ""
#                             new_ul.append(ul)
#                     ed['usefulLink'] = new_ul

#             # department: str
#             if 'department' in ed:
#                 if not isinstance(ed['department'], str):
#                     ed['department'] = ""

#     return data  # Return the fixed data

# def process_json_files(input_folder, output_folder):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
    
#     for filename in os.listdir(input_folder):
#         if filename.endswith('.json'):
#             input_path = os.path.join(input_folder, filename)
#             output_path = os.path.join(output_folder, filename)
            
#             with open(input_path, 'r', encoding='utf-8') as f:
#                 input_data = json.load(f)
            
#             # Create the output data structure
#             data = {
#                 'university_name': '',
#                 'program_name': input_data.get('programIdentity', {}).get('program_name', ''),
#                 'degree_type': input_data.get('programIdentity', {}).get('degree_code', ''),
#                 'program_content': '',
#                 'degree_program_link': '',
#                 'programUrl': '',
#                 'rank_type': '',
#                 'position': '',
#                 'campus_name': input_data.get('campusInfo', {}).get('name', ''),
#                 'url': '',
#                 'email': '',
#                 'phone': '',
#                 'country': '',
#                 'city': '',
#                 'zipCode': '',
#                 'address': '',
#                 'admissionProgramTypes_overview': '',
#                 'category_name': '',
#                 'first_layer': '',
#                 'extracted_data': {}
#             }
            
#             ed = data['extracted_data']
            
#             # Populate extracted_data
#             program_identity = input_data.get('programIdentity', {})
#             ed['program'] = {
#                 'name': program_identity.get('program_name', ''),
#                 'code': '',
#                 'synonyms': ''
#             }
#             ed['degree'] = {
#                 'name': program_identity.get('degree_name', ''),
#                 'code': program_identity.get('degree_code', ''),
#                 'type': '',
#                 'synonyms': ''
#             }
#             ed['department'] = program_identity.get('department', '')
            
#             session_delivery = input_data.get('sessionDelivery', {})
#             ed['session'] = session_delivery.get('session', [])
#             ed['durationYear'] = session_delivery.get('durationYear', 0)
#             ed['deliveryType'] = session_delivery.get('deliveryType', [])
            
#             ed['admissionTimeline'] = input_data.get('admissionTimeline', {}).get('admissionTimeline', [])
            
#             fees = input_data.get('fees', {})
#             ed['tuitionFeePerYear'] = fees.get('tuitionFeePerYear', [])
#             ed['applicationFee'] = fees.get('applicationFee', [])
            
#             ed['howToApply'] = input_data.get('howToApply', {}).get('howToApply', [])
            
#             ed['admissionProgramTypes'] = input_data.get('admissionProgramTypes', {}).get('admissionProgramTypes', [])
            
#             ed['generalRequirements'] = input_data.get('generalRequirements', {}).get('generalRequirements', [])
            
#             ed['standardizedRequirements'] = input_data.get('standardizedRequirements', {}).get('standardizedRequirements', [])
            
#             ed['languageRequirements'] = input_data.get('languageRequirements', {}).get('languageRequirements', [])
            
#             ed['degreeRequirements'] = input_data.get('degreeRequirements', {}).get('degreeRequirements', [])
            
#             ed['scholarships'] = input_data.get('scholarships', {}).get('scholarships', [])
            
#             ed['usefulLink'] = input_data.get('usefulLink', {}).get('usefulLink', [])
            
#             ed['university'] = {
#                 'name': '',
#                 'ranks': [],
#                 'campus': input_data.get('campusInfo', {})
#             }
            
#             ed['programUrl'] = ''
            
#             # Proceed with processing (fixing) 
#             extracted = data['extracted_data']
            
#             if 'admissionProgramTypes' in extracted and isinstance(extracted['admissionProgramTypes'], list) and len(extracted['admissionProgramTypes']) > 0:
#                 program_type = extracted['admissionProgramTypes'][0]
                
#                 if 'department' in program_type:
#                     extracted['department'] = program_type.pop('department')
            
#             if 'university' in extracted:
#                 uni = extracted['university']
#                 if 'campus' in uni:
#                     campus = uni['campus']
#                     campus['country'] = "USA"
#                     if isinstance(campus.get('name'), str):
#                         name = campus['name'].lower()
#                         if (
#                             "in-person & online" in name
#                             or "in-person" in name
#                             or "online" in name
#                         ):
#                             campus['name'] = ""
            
#             if 'session' in extracted and isinstance(extracted['session'], list):
#                 for sess in extracted['session']:
#                     if isinstance(sess, dict) and 'title' in sess and isinstance(sess['title'], str):
#                         title_lower = sess['title'].lower()
#                         if not any(season in title_lower for season in ['summer', 'fall', 'spring']):
#                             sess['title'] = ""
            
#             # Now fix the data
#             data = fix_json_data(data)
            
#             # Save
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, indent=4)

# # Example usage - replace with actual paths
# input_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/validate_input'
# output_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/validate_output'
# process_json_files(input_folder, output_folder)




######################### works #########################


# import json
# import os
# import re
# from urllib.parse import urlparse

# def fix_json_data(data):
#     # This function fixes fields in the JSON data by setting them to empty/default if they fail validation.
    
#     email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
#     if 'extracted_data' in data:
#         ed = data['extracted_data']
        
#         # program: dict
#         if 'program' in ed:
#             if not isinstance(ed['program'], dict):
#                 ed['program'] = {}
#             else:
#                 p = ed['program']
#                 if 'name' in p and not isinstance(p['name'], str):
#                     p['name'] = ""
#                 if 'code' in p and not isinstance(p['code'], str):
#                     p['code'] = ""
#                 if 'synonyms' in p and not isinstance(p['synonyms'], str):
#                     p['synonyms'] = ""
        
#         # degree: dict
#         if 'degree' in ed:
#             if not isinstance(ed['degree'], dict):
#                 ed['degree'] = {}
#             else:
#                 d = ed['degree']
#                 if 'name' in d and not isinstance(d['name'], str):
#                     d['name'] = ""
#                 if 'code' in d and not isinstance(d['code'], str):
#                     d['code'] = ""
#                 if 'type' in d and not isinstance(d['type'], str):
#                     d['type'] = ""
#                 if 'synonyms' in d and not isinstance(d['synonyms'], str):
#                     d['synonyms'] = ""
        
#         # university: dict
#         if 'university' in ed:
#             if not isinstance(ed['university'], dict):
#                 ed['university'] = {}
#             else:
#                 u = ed['university']
#                 if 'name' in u and not isinstance(u['name'], str):
#                     u['name'] = ""
#                 if 'ranks' in u:
#                     if not isinstance(u['ranks'], list):
#                         u['ranks'] = []
#                     else:
#                         new_ranks = []
#                         for rank in u['ranks']:
#                             if isinstance(rank, dict):
#                                 if 'type' in rank and not isinstance(rank['type'], str):
#                                     continue
#                                 if 'position' in rank and not isinstance(rank['position'], int):
#                                     continue
#                                 new_ranks.append(rank)
#                         u['ranks'] = new_ranks
#                 if 'campus' in u:
#                     if not isinstance(u['campus'], dict):
#                         u['campus'] = {}
#                     else:
#                         c = u['campus']
#                         if 'name' in c and not isinstance(c['name'], str):
#                             c['name'] = ""
#                         if 'name' in c:
#                             name = c['name'].lower()
#                             if ("in-person & online" in name or "in-person" in name or "online" in name):
#                                 c['name'] = ""
#                         if 'webUrl' in c and not isinstance(c['webUrl'], str):
#                             c['webUrl'] = ""
#                         elif c.get('webUrl'):
#                             parsed = urlparse(c['webUrl'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 c['webUrl'] = ""
#                         if 'email' in c and not isinstance(c['email'], str):
#                             c['email'] = ""
#                         elif c.get('email') and not email_pattern.match(c['email']):
#                             c['email'] = ""
#                         if 'phone' in c and not isinstance(c['phone'], str):
#                             c['phone'] = ""
#                         if 'city' in c and not isinstance(c['city'], str):
#                             c['city'] = ""
#                         if 'zipCode' in c and not isinstance(c['zipCode'], str):
#                             c['zipCode'] = ""
#                         if 'address' in c and not isinstance(c['address'], str):
#                             c['address'] = ""
        
#         # programUrl in extracted
#         if 'programUrl' in ed:
#             if not isinstance(ed['programUrl'], str):
#                 ed['programUrl'] = ""
#             elif ed['programUrl']:
#                 parsed = urlparse(ed['programUrl'])
#                 if not all([parsed.scheme, parsed.netloc]):
#                     ed['programUrl'] = ""
        
#         # session: list
#         if 'session' in ed:
#             if not isinstance(ed['session'], list):
#                 ed['session'] = []
#             else:
#                 new_sessions = []
#                 for s in ed['session']:
#                     if isinstance(s, dict):
#                         if 'title' in s:
#                             if not isinstance(s['title'], str):
#                                 s['title'] = ""
#                             else:
#                                 title_lower = s['title'].lower()
#                                 if title_lower and not any(season in title_lower for season in ['summer', 'fall', 'spring']):
#                                     s['title'] = ""
#                         new_sessions.append(s)
#                 ed['session'] = new_sessions
        
#         # durationYear: number
#         if 'durationYear' in ed:
#             if not isinstance(ed['durationYear'], (int, float)):
#                 ed['durationYear'] = 0
        
#         # deliveryType: list
#         if 'deliveryType' in ed:
#             if not isinstance(ed['deliveryType'], list):
#                 ed['deliveryType'] = []
        
#         # admissionTimeline: list
#         if 'admissionTimeline' in ed:
#             if not isinstance(ed['admissionTimeline'], list):
#                 ed['admissionTimeline'] = []
        
#         # tuitionFeePerYear: list
#         if 'tuitionFeePerYear' in ed:
#             if not isinstance(ed['tuitionFeePerYear'], list):
#                 ed['tuitionFeePerYear'] = []
        
#         # applicationFee: list
#         if 'applicationFee' in ed:
#             if not isinstance(ed['applicationFee'], list):
#                 ed['applicationFee'] = []
        
#         # howToApply: list of dicts
#         if 'howToApply' in ed:
#             if not isinstance(ed['howToApply'], list):
#                 ed['howToApply'] = []
#             else:
#                 new_how = []
#                 for h in ed['howToApply']:
#                     if isinstance(h, dict):
#                         if 'title' in h and not isinstance(h['title'], str):
#                             h['title'] = ""
#                         if 'detail' in h and not isinstance(h['detail'], str):
#                             h['detail'] = ""
#                         if 'webLink' in h and not isinstance(h['webLink'], str):
#                             h['webLink'] = ""
#                         elif h.get('webLink'):
#                             parsed = urlparse(h['webLink'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 h['webLink'] = ""
#                         new_how.append(h)
#                 ed['howToApply'] = new_how
        
#         # admissionProgramTypes: list of dicts
#         if 'admissionProgramTypes' in ed:
#             if not isinstance(ed['admissionProgramTypes'], list):
#                 ed['admissionProgramTypes'] = []
#             else:
#                 new_apt = []
#                 for apt in ed['admissionProgramTypes']:
#                     if isinstance(apt, dict):
#                         if 'type' in apt and not isinstance(apt['type'], str):
#                             apt['type'] = ""
#                         if 'overview' in apt and not isinstance(apt['overview'], str):
#                             apt['overview'] = ""
#                         if 'department' in apt and not isinstance(apt['department'], str):
#                             apt['department'] = ""
#                         if 'courseOutline' in apt:
#                             if not isinstance(apt['courseOutline'], list):
#                                 apt['courseOutline'] = []
#                             else:
#                                 new_co = []
#                                 for co in apt['courseOutline']:
#                                     if isinstance(co, dict):
#                                         if 'title' in co and not isinstance(co['title'], str):
#                                             co['title'] = ""
#                                         if 'detail' in co and not isinstance(co['detail'], str):
#                                             co['detail'] = ""
#                                         new_co.append(co)
#                                 apt['courseOutline'] = new_co
#                         new_apt.append(apt)
#                 ed['admissionProgramTypes'] = new_apt
        
#         # generalRequirements: list of dicts
#         if 'generalRequirements' in ed:
#             if not isinstance(ed['generalRequirements'], list):
#                 ed['generalRequirements'] = []
#             else:
#                 new_gr = []
#                 for gr in ed['generalRequirements']:
#                     if isinstance(gr, dict):
#                         if 'type' in gr and not isinstance(gr['type'], str):
#                             gr['type'] = ""
#                         if 'title' in gr and not isinstance(gr['title'], str):
#                             gr['title'] = ""
#                         if 'page' in gr and not isinstance(gr['page'], int):
#                             gr['page'] = 0
#                         if 'words' in gr and not isinstance(gr['words'], int):
#                             gr['words'] = 0
#                         if 'count' in gr and not isinstance(gr['count'], int):
#                             gr['count'] = 0
#                         if 'details' in gr and not isinstance(gr['details'], str):
#                             gr['details'] = ""
#                         new_gr.append(gr)
#                 ed['generalRequirements'] = new_gr
        
#         # standardizedRequirements: list of dicts
#         if 'standardizedRequirements' in ed:
#             if not isinstance(ed['standardizedRequirements'], list):
#                 ed['standardizedRequirements'] = []
#             else:
#                 new_sr = []
#                 for sr in ed['standardizedRequirements']:
#                     if isinstance(sr, dict):
#                         if 'test' in sr:
#                             if not isinstance(sr['test'], dict):
#                                 sr['test'] = {}
#                             else:
#                                 t = sr['test']
#                                 if 'type' in t and not isinstance(t['type'], str):
#                                     t['type'] = ""
#                                 if 'total' in t and not isinstance(t['total'], (int, float)):
#                                     t['total'] = 0
#                                 if 'verbal' in t and not isinstance(t['verbal'], (int, float)):
#                                     t['verbal'] = 0
#                                 if 'quant' in t and not isinstance(t['quant'], (int, float)):
#                                     t['quant'] = 0
#                                 if 'awa' in t and not isinstance(t['awa'], (int, float)):
#                                     t['awa'] = 0
#                                 if 'required' in t and not isinstance(t['required'], bool):
#                                     t['required'] = False
#                         new_sr.append(sr)
#                 ed['standardizedRequirements'] = new_sr
        
#         # languageRequirements: list of dicts
#         if 'languageRequirements' in ed:
#             if not isinstance(ed['languageRequirements'], list):
#                 ed['languageRequirements'] = []
#             else:
#                 new_lr = []
#                 for lr in ed['languageRequirements']:
#                     if isinstance(lr, dict):
#                         if 'test' in lr:
#                             if not isinstance(lr['test'], dict):
#                                 lr['test'] = {}
#                             else:
#                                 t = lr['test']
#                                 if 'type' in t and not isinstance(t['type'], str):
#                                     t['type'] = ""
#                                 if 'total' in t and not isinstance(t['total'], (int, float)):
#                                     t['total'] = 0
#                                 if 'listening' in t and not isinstance(t['listening'], (int, float)):
#                                     t['listening'] = 0
#                                 if 'reading' in t and not isinstance(t['reading'], (int, float)):
#                                     t['reading'] = 0
#                                 if 'writing' in t and not isinstance(t['writing'], (int, float)):
#                                     t['writing'] = 0
#                                 if 'speaking' in t and not isinstance(t['speaking'], (int, float)):
#                                     t['speaking'] = 0
#                                 if 'required' in t and not isinstance(t['required'], bool):
#                                     t['required'] = False
#                         new_lr.append(lr)
#                 ed['languageRequirements'] = new_lr
        
#         # degreeRequirements: list of dicts
#         if 'degreeRequirements' in ed:
#             if not isinstance(ed['degreeRequirements'], list):
#                 ed['degreeRequirements'] = []
#             else:
#                 new_dr = []
#                 for dr in ed['degreeRequirements']:
#                     if isinstance(dr, dict):
#                         if 'test' in dr:
#                             if not isinstance(dr['test'], dict):
#                                 dr['test'] = {}
#                             else:
#                                 t = dr['test']
#                                 if 'details' in t and not isinstance(t['details'], str):
#                                     t['details'] = ""
#                                 if 'type' in t and not isinstance(t['type'], str):
#                                     t['type'] = ""
#                                 if 'total' in t and not isinstance(t['total'], (int, float)):
#                                     t['total'] = 0
#                                 if 'outOf' in t and not isinstance(t['outOf'], (int, float)):
#                                     t['outOf'] = 0
#                                 if 'region' in t and not isinstance(t['region'], str):
#                                     t['region'] = ""
#                         new_dr.append(dr)
#                 ed['degreeRequirements'] = new_dr
        
#         # scholarships: list of dicts
#         if 'scholarships' in ed:
#             if not isinstance(ed['scholarships'], list):
#                 ed['scholarships'] = []
#             else:
#                 new_sch = []
#                 for sch in ed['scholarships']:
#                     if isinstance(sch, dict):
#                         if 'type' in sch and not isinstance(sch['type'], str):
#                             sch['type'] = ""
#                         if 'name' in sch and not isinstance(sch['name'], str):
#                             sch['name'] = ""
#                         if 'requirement' in sch:
#                             if not isinstance(sch['requirement'], list):
#                                 sch['requirement'] = []
#                             else:
#                                 sch['requirement'] = [r for r in sch['requirement'] if isinstance(r, str)]
#                         if 'detail' in sch and not isinstance(sch['detail'], str):
#                             sch['detail'] = ""
#                         if 'amount' in sch and not isinstance(sch['amount'], (int, float)):
#                             sch['amount'] = 0
#                         if 'currency' in sch and not isinstance(sch['currency'], str):
#                             sch['currency'] = ""
#                         if 'webLink' in sch and not isinstance(sch['webLink'], str):
#                             sch['webLink'] = ""
#                         elif sch.get('webLink'):
#                             parsed = urlparse(sch['webLink'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 sch['webLink'] = ""
#                         if 'deadline' in sch and not isinstance(sch['deadline'], str):
#                             sch['deadline'] = ""
#                         new_sch.append(sch)
#                 ed['scholarships'] = new_sch
        
#         # usefulLink: list of dicts
#         if 'usefulLink' in ed:
#             if not isinstance(ed['usefulLink'], list):
#                 ed['usefulLink'] = []
#             else:
#                 new_ul = []
#                 for ul in ed['usefulLink']:
#                     if isinstance(ul, dict):
#                         if 'title' in ul and not isinstance(ul['title'], str):
#                             ul['title'] = ""
#                         if 'detail' in ul and not isinstance(ul['detail'], str):
#                             ul['detail'] = ""
#                         if 'webLink' in ul and not isinstance(ul['webLink'], str):
#                             ul['webLink'] = ""
#                         elif ul.get('webLink'):
#                             parsed = urlparse(ul['webLink'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 ul['webLink'] = ""
#                         new_ul.append(ul)
#                 ed['usefulLink'] = new_ul
        
#         # department: str
#         if 'department' in ed:
#             if not isinstance(ed['department'], str):
#                 ed['department'] = ""
    
#     return data

# def process_json_files(input_folder, output_folder):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
    
#     for filename in os.listdir(input_folder):
#         if filename.endswith('.json'):
#             input_path = os.path.join(input_folder, filename)
#             output_path = os.path.join(output_folder, filename)
            
#             with open(input_path, 'r', encoding='utf-8') as f:
#                 input_data = json.load(f)
            
#             # Check if input has extracted_data at top level
#             if 'extracted_data' in input_data:
#                 source_data = input_data['extracted_data']
#             else:
#                 source_data = input_data
            
#             # Build the extracted_data structure
#             extracted_data = {}
            
#             # Program identity
#             program_identity = source_data.get('programIdentity', {})
#             extracted_data['program'] = {
#                 'name': program_identity.get('program_name', ''),
#                 'code': program_identity.get('degree_code', ''),
#                 'synonyms': ''
#             }
            
#             extracted_data['degree'] = {
#                 'name': program_identity.get('degree_name', ''),
#                 'code': program_identity.get('degree_code', ''),
#                 'type': '',
#                 'synonyms': ''
#             }
            
#             extracted_data['department'] = program_identity.get('department', '')
            
#             # Session and delivery
#             session_delivery = source_data.get('sessionDelivery', {})
#             extracted_data['session'] = session_delivery.get('session', [])
#             extracted_data['durationYear'] = session_delivery.get('durationYear', 0)
#             extracted_data['deliveryType'] = session_delivery.get('deliveryType', [])
            
#             # Admission timeline
#             admission_timeline = source_data.get('admissionTimeline', {})
#             extracted_data['admissionTimeline'] = admission_timeline.get('admissionTimeline', [])
            
#             # Fees
#             fees = source_data.get('fees', {})
#             extracted_data['tuitionFeePerYear'] = fees.get('tuitionFeePerYear', [])
#             extracted_data['applicationFee'] = fees.get('applicationFee', [])
            
#             # How to apply
#             how_to_apply = source_data.get('howToApply', {})
#             extracted_data['howToApply'] = how_to_apply.get('howToApply', [])
            
#             # Admission program types
#             admission_program_types = source_data.get('admissionProgramTypes', {})
#             extracted_data['admissionProgramTypes'] = admission_program_types.get('admissionProgramTypes', [])
            
#             # Requirements
#             general_reqs = source_data.get('generalRequirements', {})
#             extracted_data['generalRequirements'] = general_reqs.get('generalRequirements', [])
            
#             standardized_reqs = source_data.get('standardizedRequirements', {})
#             extracted_data['standardizedRequirements'] = standardized_reqs.get('standardizedRequirements', [])
            
#             language_reqs = source_data.get('languageRequirements', {})
#             extracted_data['languageRequirements'] = language_reqs.get('languageRequirements', [])
            
#             degree_reqs = source_data.get('degreeRequirements', {})
#             extracted_data['degreeRequirements'] = degree_reqs.get('degreeRequirements', [])
            
#             # Scholarships
#             scholarships = source_data.get('scholarships', {})
#             extracted_data['scholarships'] = scholarships.get('scholarships', [])
            
#             # Useful links
#             useful_link = source_data.get('usefulLink', {})
#             extracted_data['usefulLink'] = useful_link.get('usefulLink', [])
            
#             # University and campus info
#             campus_info = source_data.get('campusInfo', {})
#             extracted_data['university'] = {
#                 'name': '',
#                 'ranks': [],
#                 'campus': campus_info
#             }
            
#             # Program URL
#             extracted_data['programUrl'] = input_data.get('programUrl', '')
   
#             # Clean session titles
#             if 'session' in extracted_data and isinstance(extracted_data['session'], list):
#                 for sess in extracted_data['session']:
#                     if isinstance(sess, dict) and 'title' in sess and isinstance(sess['title'], str):
#                         title_lower = sess['title'].lower()
#                         if not any(season in title_lower for season in ['summer', 'fall', 'spring']):
#                             sess['title'] = ""
            
#             # Wrap in temporary container for validation
#             temp_data = {'extracted_data': extracted_data}
            
#             # Fix the data
#             temp_data = fix_json_data(temp_data)
            
#             # Extract only the extracted_data part for output
#             output_data = temp_data['extracted_data']
            
#             # Save only extracted_data
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(output_data, f, indent=4)

# # Example usage
# input_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/validate_input'
# output_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/validate_output'
# process_json_files(input_folder, output_folder)









# import json
# import os
# import re
# from urllib.parse import urlparse

# # Comprehensive country list with names and ISO codes
# COUNTRY_LIST = {
#     # Format: "country_name": ["ISO2", "ISO3", "common_variations"]
#     "afghanistan": ["AF", "AFG"],
#     "albania": ["AL", "ALB"],
#     "algeria": ["DZ", "DZA"],
#     "andorra": ["AD", "AND"],
#     "angola": ["AO", "AGO"],
#     "antigua and barbuda": ["AG", "ATG"],
#     "argentina": ["AR", "ARG"],
#     "armenia": ["AM", "ARM"],
#     "australia": ["AU", "AUS"],
#     "austria": ["AT", "AUT"],
#     "azerbaijan": ["AZ", "AZE"],
#     "bahamas": ["BS", "BHS"],
#     "bahrain": ["BH", "BHR"],
#     "bangladesh": ["BD", "BGD"],
#     "barbados": ["BB", "BRB"],
#     "belarus": ["BY", "BLR"],
#     "belgium": ["BE", "BEL"],
#     "belize": ["BZ", "BLZ"],
#     "benin": ["BJ", "BEN"],
#     "bhutan": ["BT", "BTN"],
#     "bolivia": ["BO", "BOL"],
#     "bosnia and herzegovina": ["BA", "BIH"],
#     "botswana": ["BW", "BWA"],
#     "brazil": ["BR", "BRA"],
#     "brunei": ["BN", "BRN"],
#     "bulgaria": ["BG", "BGR"],
#     "burkina faso": ["BF", "BFA"],
#     "burundi": ["BI", "BDI"],
#     "cambodia": ["KH", "KHM"],
#     "cameroon": ["CM", "CMR"],
#     "canada": ["CA", "CAN"],
#     "cape verde": ["CV", "CPV"],
#     "central african republic": ["CF", "CAF"],
#     "chad": ["TD", "TCD"],
#     "chile": ["CL", "CHL"],
#     "china": ["CN", "CHN"],
#     "colombia": ["CO", "COL"],
#     "comoros": ["KM", "COM"],
#     "congo": ["CG", "COG"],
#     "costa rica": ["CR", "CRI"],
#     "croatia": ["HR", "HRV"],
#     "cuba": ["CU", "CUB"],
#     "cyprus": ["CY", "CYP"],
#     "czech republic": ["CZ", "CZE"],
#     "czechia": ["CZ", "CZE"],
#     "denmark": ["DK", "DNK"],
#     "djibouti": ["DJ", "DJI"],
#     "dominica": ["DM", "DMA"],
#     "dominican republic": ["DO", "DOM"],
#     "east timor": ["TL", "TLS"],
#     "ecuador": ["EC", "ECU"],
#     "egypt": ["EG", "EGY"],
#     "el salvador": ["SV", "SLV"],
#     "equatorial guinea": ["GQ", "GNQ"],
#     "eritrea": ["ER", "ERI"],
#     "estonia": ["EE", "EST"],
#     "eswatini": ["SZ", "SWZ"],
#     "swaziland": ["SZ", "SWZ"],
#     "ethiopia": ["ET", "ETH"],
#     "fiji": ["FJ", "FJI"],
#     "finland": ["FI", "FIN"],
#     "france": ["FR", "FRA"],
#     "gabon": ["GA", "GAB"],
#     "gambia": ["GM", "GMB"],
#     "georgia": ["GE", "GEO"],
#     "germany": ["DE", "DEU"],
#     "ghana": ["GH", "GHA"],
#     "greece": ["GR", "GRC"],
#     "grenada": ["GD", "GRD"],
#     "guatemala": ["GT", "GTM"],
#     "guinea": ["GN", "GIN"],
#     "guinea-bissau": ["GW", "GNB"],
#     "guyana": ["GY", "GUY"],
#     "haiti": ["HT", "HTI"],
#     "honduras": ["HN", "HND"],
#     "hungary": ["HU", "HUN"],
#     "iceland": ["IS", "ISL"],
#     "india": ["IN", "IND"],
#     "indonesia": ["ID", "IDN"],
#     "iran": ["IR", "IRN"],
#     "iraq": ["IQ", "IRQ"],
#     "ireland": ["IE", "IRL"],
#     "israel": ["IL", "ISR"],
#     "italy": ["IT", "ITA"],
#     "ivory coast": ["CI", "CIV"],
#     "cote d'ivoire": ["CI", "CIV"],
#     "jamaica": ["JM", "JAM"],
#     "japan": ["JP", "JPN"],
#     "jordan": ["JO", "JOR"],
#     "kazakhstan": ["KZ", "KAZ"],
#     "kenya": ["KE", "KEN"],
#     "kiribati": ["KI", "KIR"],
#     "kosovo": ["XK", "XKX"],
#     "kuwait": ["KW", "KWT"],
#     "kyrgyzstan": ["KG", "KGZ"],
#     "laos": ["LA", "LAO"],
#     "latvia": ["LV", "LVA"],
#     "lebanon": ["LB", "LBN"],
#     "lesotho": ["LS", "LSO"],
#     "liberia": ["LR", "LBR"],
#     "libya": ["LY", "LBY"],
#     "liechtenstein": ["LI", "LIE"],
#     "lithuania": ["LT", "LTU"],
#     "luxembourg": ["LU", "LUX"],
#     "madagascar": ["MG", "MDG"],
#     "malawi": ["MW", "MWI"],
#     "malaysia": ["MY", "MYS"],
#     "maldives": ["MV", "MDV"],
#     "mali": ["ML", "MLI"],
#     "malta": ["MT", "MLT"],
#     "marshall islands": ["MH", "MHL"],
#     "mauritania": ["MR", "MRT"],
#     "mauritius": ["MU", "MUS"],
#     "mexico": ["MX", "MEX"],
#     "micronesia": ["FM", "FSM"],
#     "moldova": ["MD", "MDA"],
#     "monaco": ["MC", "MCO"],
#     "mongolia": ["MN", "MNG"],
#     "montenegro": ["ME", "MNE"],
#     "morocco": ["MA", "MAR"],
#     "mozambique": ["MZ", "MOZ"],
#     "myanmar": ["MM", "MMR"],
#     "burma": ["MM", "MMR"],
#     "namibia": ["NA", "NAM"],
#     "nauru": ["NR", "NRU"],
#     "nepal": ["NP", "NPL"],
#     "netherlands": ["NL", "NLD"],
#     "new zealand": ["NZ", "NZL"],
#     "nicaragua": ["NI", "NIC"],
#     "niger": ["NE", "NER"],
#     "nigeria": ["NG", "NGA"],
#     "north korea": ["KP", "PRK"],
#     "north macedonia": ["MK", "MKD"],
#     "macedonia": ["MK", "MKD"],
#     "norway": ["NO", "NOR"],
#     "oman": ["OM", "OMN"],
#     "pakistan": ["PK", "PAK"],
#     "palau": ["PW", "PLW"],
#     "palestine": ["PS", "PSE"],
#     "panama": ["PA", "PAN"],
#     "papua new guinea": ["PG", "PNG"],
#     "paraguay": ["PY", "PRY"],
#     "peru": ["PE", "PER"],
#     "philippines": ["PH", "PHL"],
#     "poland": ["PL", "POL"],
#     "portugal": ["PT", "PRT"],
#     "qatar": ["QA", "QAT"],
#     "romania": ["RO", "ROU"],
#     "russia": ["RU", "RUS"],
#     "russian federation": ["RU", "RUS"],
#     "rwanda": ["RW", "RWA"],
#     "saint kitts and nevis": ["KN", "KNA"],
#     "saint lucia": ["LC", "LCA"],
#     "saint vincent and the grenadines": ["VC", "VCT"],
#     "samoa": ["WS", "WSM"],
#     "san marino": ["SM", "SMR"],
#     "sao tome and principe": ["ST", "STP"],
#     "saudi arabia": ["SA", "SAU"],
#     "senegal": ["SN", "SEN"],
#     "serbia": ["RS", "SRB"],
#     "seychelles": ["SC", "SYC"],
#     "sierra leone": ["SL", "SLE"],
#     "singapore": ["SG", "SGP"],
#     "slovakia": ["SK", "SVK"],
#     "slovenia": ["SI", "SVN"],
#     "solomon islands": ["SB", "SLB"],
#     "somalia": ["SO", "SOM"],
#     "south africa": ["ZA", "ZAF"],
#     "south korea": ["KR", "KOR"],
#     "south sudan": ["SS", "SSD"],
#     "spain": ["ES", "ESP"],
#     "sri lanka": ["LK", "LKA"],
#     "sudan": ["SD", "SDN"],
#     "suriname": ["SR", "SUR"],
#     "sweden": ["SE", "SWE"],
#     "switzerland": ["CH", "CHE"],
#     "syria": ["SY", "SYR"],
#     "taiwan": ["TW", "TWN"],
#     "tajikistan": ["TJ", "TJK"],
#     "tanzania": ["TZ", "TZA"],
#     "thailand": ["TH", "THA"],
#     "timor-leste": ["TL", "TLS"],
#     "togo": ["TG", "TGO"],
#     "tonga": ["TO", "TON"],
#     "trinidad and tobago": ["TT", "TTO"],
#     "tunisia": ["TN", "TUN"],
#     "turkey": ["TR", "TUR"],
#     "turkmenistan": ["TM", "TKM"],
#     "tuvalu": ["TV", "TUV"],
#     "uganda": ["UG", "UGA"],
#     "ukraine": ["UA", "UKR"],
#     "united arab emirates": ["AE", "ARE"],
#     "uae": ["AE", "ARE"],
#     "united kingdom": ["GB", "GBR"],
#     "uk": ["GB", "GBR"],
#     "united states": ["US", "USA"],
#     "usa": ["US", "USA"],
#     "uruguay": ["UY", "URY"],
#     "uzbekistan": ["UZ", "UZB"],
#     "vanuatu": ["VU", "VUT"],
#     "vatican city": ["VA", "VAT"],
#     "venezuela": ["VE", "VEN"],
#     "vietnam": ["VN", "VNM"],
#     "yemen": ["YE", "YEM"],
#     "zambia": ["ZM", "ZMB"],
#     "zimbabwe": ["ZW", "ZWE"],
#     # Common regional terms
#     "england": ["GB", "GBR"],
#     "scotland": ["GB", "GBR"],
#     "wales": ["GB", "GBR"],
#     "northern ireland": ["GB", "GBR"],
# }

# def validate_country(country_str):
#     """
#     Validates a country name or code against the country list.
#     Returns the validated country name or empty string if invalid.
#     """
#     if not country_str or not isinstance(country_str, str):
#         return ""
    
#     country_lower = country_str.strip().lower()
    
#     # Check if it's a valid country name
#     if country_lower in COUNTRY_LIST:
#         return country_str.strip()
    
#     # Check if it's a valid ISO code
#     for country_name, codes in COUNTRY_LIST.items():
#         if country_str.strip().upper() in codes:
#             return country_str.strip()
    
#     # If not found, return empty string
#     return ""

# def fix_json_data(data):
#     # This function fixes fields in the JSON data by setting them to empty/default if they fail validation.
    
#     email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
#     if 'extracted_data' in data:
#         ed = data['extracted_data']
        
#         # program: dict
#         if 'program' in ed:
#             if not isinstance(ed['program'], dict):
#                 ed['program'] = {}
#             else:
#                 p = ed['program']
#                 if 'name' in p and not isinstance(p['name'], str):
#                     p['name'] = ""
#                 if 'code' in p and not isinstance(p['code'], str):
#                     p['code'] = ""
#                 # NEW: Remove program code if it matches degree code
#                 if 'code' in p and 'degree' in ed and isinstance(ed['degree'], dict):
#                     degree_code = ed['degree'].get('code', '')
#                     if p['code'] == degree_code:
#                         p['code'] = ""
#                 if 'synonyms' in p and not isinstance(p['synonyms'], str):
#                     p['synonyms'] = ""
        
#         # degree: dict
#         if 'degree' in ed:
#             if not isinstance(ed['degree'], dict):
#                 ed['degree'] = {}
#             else:
#                 d = ed['degree']
#                 if 'name' in d and not isinstance(d['name'], str):
#                     d['name'] = ""
#                 if 'code' in d and not isinstance(d['code'], str):
#                     d['code'] = ""
#                 if 'type' in d and not isinstance(d['type'], str):
#                     d['type'] = ""
#                 if 'synonyms' in d and not isinstance(d['synonyms'], str):
#                     d['synonyms'] = ""
        
#         # university: dict
#         if 'university' in ed:
#             if not isinstance(ed['university'], dict):
#                 ed['university'] = {}
#             else:
#                 u = ed['university']
#                 if 'name' in u and not isinstance(u['name'], str):
#                     u['name'] = ""
#                 if 'ranks' in u:
#                     if not isinstance(u['ranks'], list):
#                         u['ranks'] = []
#                     else:
#                         new_ranks = []
#                         for rank in u['ranks']:
#                             if isinstance(rank, dict):
#                                 if 'type' in rank and not isinstance(rank['type'], str):
#                                     continue
#                                 if 'position' in rank and not isinstance(rank['position'], int):
#                                     continue
#                                 new_ranks.append(rank)
#                         u['ranks'] = new_ranks
                        
#                 if 'campus' in u:
#                     if not isinstance(u['campus'], dict):
#                         u['campus'] = {}
#                     else:
#                         c = u['campus']
#                         if 'name' in c and not isinstance(c['name'], str):
#                             c['name'] = ""
#                         if 'name' in c:
#                             name = c['name'].lower()
#                             if ("in-person & online" in name or "in-person" in name or "online" in name):
#                                 c['name'] = ""
                        
#                         # NEW: Validate country field
#                         if 'country' in c:
#                             if not isinstance(c['country'], str):
#                                 c['country'] = ""
#                             else:
#                                 validated_country = validate_country(c['country'])
#                                 c['country'] = validated_country
                        
#                         if 'webUrl' in c and not isinstance(c['webUrl'], str):
#                             c['webUrl'] = ""
#                         elif c.get('webUrl'):
#                             parsed = urlparse(c['webUrl'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 c['webUrl'] = ""
#                         if 'email' in c and not isinstance(c['email'], str):
#                             c['email'] = ""
#                         elif c.get('email') and not email_pattern.match(c['email']):
#                             c['email'] = ""
#                         if 'phone' in c and not isinstance(c['phone'], str):
#                             c['phone'] = ""
#                         if 'city' in c and not isinstance(c['city'], str):
#                             c['city'] = ""
#                         if 'zipCode' in c and not isinstance(c['zipCode'], str):
#                             c['zipCode'] = ""
#                         if 'address' in c and not isinstance(c['address'], str):
#                             c['address'] = ""
        
#         # programUrl in extracted
#         if 'programUrl' in ed:
#             if not isinstance(ed['programUrl'], str):
#                 ed['programUrl'] = ""
#             elif ed['programUrl']:
#                 parsed = urlparse(ed['programUrl'])
#                 if not all([parsed.scheme, parsed.netloc]):
#                     ed['programUrl'] = ""
        
#         # session: list
#         if 'session' in ed:
#             if not isinstance(ed['session'], list):
#                 ed['session'] = []
#             else:
#                 new_sessions = []
#                 for s in ed['session']:
#                     if isinstance(s, dict):
#                         if 'title' in s:
#                             if not isinstance(s['title'], str):
#                                 s['title'] = ""
#                             else:
#                                 title_lower = s['title'].lower()
#                                 if title_lower and not any(season in title_lower for season in ['summer', 'fall', 'spring']):
#                                     s['title'] = ""
#                         new_sessions.append(s)
#                 ed['session'] = new_sessions
        
#         # durationYear: number
#         if 'durationYear' in ed:
#             if not isinstance(ed['durationYear'], (int, float)):
#                 ed['durationYear'] = 0
        
#         # deliveryType: list
#         if 'deliveryType' in ed:
#             if not isinstance(ed['deliveryType'], list):
#                 ed['deliveryType'] = []
        
#         # admissionTimeline: list
#         if 'admissionTimeline' in ed:
#             if not isinstance(ed['admissionTimeline'], list):
#                 ed['admissionTimeline'] = []
        
#         # tuitionFeePerYear: list
#         if 'tuitionFeePerYear' in ed:
#             if not isinstance(ed['tuitionFeePerYear'], list):
#                 ed['tuitionFeePerYear'] = []
        
#         # applicationFee: list
#         if 'applicationFee' in ed:
#             if not isinstance(ed['applicationFee'], list):
#                 ed['applicationFee'] = []
        
#         # howToApply: list of dicts
#         if 'howToApply' in ed:
#             if not isinstance(ed['howToApply'], list):
#                 ed['howToApply'] = []
#             else:
#                 new_how = []
#                 for h in ed['howToApply']:
#                     if isinstance(h, dict):
#                         if 'title' in h and not isinstance(h['title'], str):
#                             h['title'] = ""
#                         if 'detail' in h and not isinstance(h['detail'], str):
#                             h['detail'] = ""
#                         if 'webLink' in h and not isinstance(h['webLink'], str):
#                             h['webLink'] = ""
#                         elif h.get('webLink'):
#                             parsed = urlparse(h['webLink'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 h['webLink'] = ""
#                         new_how.append(h)
#                 ed['howToApply'] = new_how
        
#         # admissionProgramTypes: list of dicts
#         if 'admissionProgramTypes' in ed:
#             if not isinstance(ed['admissionProgramTypes'], list):
#                 ed['admissionProgramTypes'] = []
#             else:
#                 new_apt = []
#                 for apt in ed['admissionProgramTypes']:
#                     if isinstance(apt, dict):
#                         if 'type' in apt and not isinstance(apt['type'], str):
#                             apt['type'] = ""
#                         if 'overview' in apt and not isinstance(apt['overview'], str):
#                             apt['overview'] = ""
#                         if 'department' in apt and not isinstance(apt['department'], str):
#                             apt['department'] = ""
#                         if 'courseOutline' in apt:
#                             if not isinstance(apt['courseOutline'], list):
#                                 apt['courseOutline'] = []
#                             else:
#                                 new_co = []
#                                 for co in apt['courseOutline']:
#                                     if isinstance(co, dict):
#                                         if 'title' in co and not isinstance(co['title'], str):
#                                             co['title'] = ""
#                                         if 'detail' in co and not isinstance(co['detail'], str):
#                                             co['detail'] = ""
#                                         new_co.append(co)
#                                 apt['courseOutline'] = new_co
#                         new_apt.append(apt)
#                 ed['admissionProgramTypes'] = new_apt
        
#         # generalRequirements: list of dicts
#         if 'generalRequirements' in ed:
#             if not isinstance(ed['generalRequirements'], list):
#                 ed['generalRequirements'] = []
#             else:
#                 new_gr = []
#                 for gr in ed['generalRequirements']:
#                     if isinstance(gr, dict):
#                         if 'type' in gr and not isinstance(gr['type'], str):
#                             gr['type'] = ""
#                         if 'title' in gr and not isinstance(gr['title'], str):
#                             gr['title'] = ""
#                         if 'page' in gr and not isinstance(gr['page'], int):
#                             gr['page'] = 0
#                         if 'words' in gr and not isinstance(gr['words'], int):
#                             gr['words'] = 0
#                         if 'count' in gr and not isinstance(gr['count'], int):
#                             gr['count'] = 0
#                         if 'details' in gr and not isinstance(gr['details'], str):
#                             gr['details'] = ""
#                         new_gr.append(gr)
#                 ed['generalRequirements'] = new_gr
        
#         # standardizedRequirements: list of dicts
#         if 'standardizedRequirements' in ed:
#             if not isinstance(ed['standardizedRequirements'], list):
#                 ed['standardizedRequirements'] = []
#             else:
#                 new_sr = []
#                 for sr in ed['standardizedRequirements']:
#                     if isinstance(sr, dict):
#                         if 'test' in sr:
#                             if not isinstance(sr['test'], dict):
#                                 sr['test'] = {}
#                             else:
#                                 t = sr['test']
#                                 if 'type' in t and not isinstance(t['type'], str):
#                                     t['type'] = ""
#                                 if 'total' in t and not isinstance(t['total'], (int, float)):
#                                     t['total'] = 0
#                                 if 'verbal' in t and not isinstance(t['verbal'], (int, float)):
#                                     t['verbal'] = 0
#                                 if 'quant' in t and not isinstance(t['quant'], (int, float)):
#                                     t['quant'] = 0
#                                 if 'awa' in t and not isinstance(t['awa'], (int, float)):
#                                     t['awa'] = 0
#                                 if 'required' in t and not isinstance(t['required'], bool):
#                                     t['required'] = False
#                         new_sr.append(sr)
#                 ed['standardizedRequirements'] = new_sr
        
#         # languageRequirements: list of dicts
#         if 'languageRequirements' in ed:
#             if not isinstance(ed['languageRequirements'], list):
#                 ed['languageRequirements'] = []
#             else:
#                 new_lr = []
#                 for lr in ed['languageRequirements']:
#                     if isinstance(lr, dict):
#                         if 'test' in lr:
#                             if not isinstance(lr['test'], dict):
#                                 lr['test'] = {}
#                             else:
#                                 t = lr['test']
#                                 if 'type' in t and not isinstance(t['type'], str):
#                                     t['type'] = ""
#                                 if 'total' in t and not isinstance(t['total'], (int, float)):
#                                     t['total'] = 0
#                                 if 'listening' in t and not isinstance(t['listening'], (int, float)):
#                                     t['listening'] = 0
#                                 if 'reading' in t and not isinstance(t['reading'], (int, float)):
#                                     t['reading'] = 0
#                                 if 'writing' in t and not isinstance(t['writing'], (int, float)):
#                                     t['writing'] = 0
#                                 if 'speaking' in t and not isinstance(t['speaking'], (int, float)):
#                                     t['speaking'] = 0
#                                 if 'required' in t and not isinstance(t['required'], bool):
#                                     t['required'] = False
#                         new_lr.append(lr)
#                 ed['languageRequirements'] = new_lr
        
#         # degreeRequirements: list of dicts (with region validation)
#         if 'degreeRequirements' in ed:
#             if not isinstance(ed['degreeRequirements'], list):
#                 ed['degreeRequirements'] = []
#             else:
#                 new_dr = []
#                 for dr in ed['degreeRequirements']:
#                     if isinstance(dr, dict):
#                         if 'test' in dr:
#                             if not isinstance(dr['test'], dict):
#                                 dr['test'] = {}
#                             else:
#                                 t = dr['test']
#                                 if 'details' in t and not isinstance(t['details'], str):
#                                     t['details'] = ""
#                                 if 'type' in t and not isinstance(t['type'], str):
#                                     t['type'] = ""
#                                 if 'total' in t and not isinstance(t['total'], (int, float)):
#                                     t['total'] = 0
#                                 if 'outOf' in t and not isinstance(t['outOf'], (int, float)):
#                                     t['outOf'] = 0
#                                 # NEW: Validate region/country
#                                 if 'region' in t:
#                                     if not isinstance(t['region'], str):
#                                         t['region'] = ""
#                                     else:
#                                         validated_region = validate_country(t['region'])
#                                         t['region'] = validated_region
#                         new_dr.append(dr)
#                 ed['degreeRequirements'] = new_dr
        
#         # scholarships: list of dicts
#         if 'scholarships' in ed:
#             if not isinstance(ed['scholarships'], list):
#                 ed['scholarships'] = []
#             else:
#                 new_sch = []
#                 for sch in ed['scholarships']:
#                     if isinstance(sch, dict):
#                         if 'type' in sch and not isinstance(sch['type'], str):
#                             sch['type'] = ""
#                         if 'name' in sch and not isinstance(sch['name'], str):
#                             sch['name'] = ""
#                         if 'requirement' in sch:
#                             if not isinstance(sch['requirement'], list):
#                                 sch['requirement'] = []
#                             else:
#                                 sch['requirement'] = [r for r in sch['requirement'] if isinstance(r, str)]
#                         if 'detail' in sch and not isinstance(sch['detail'], str):
#                             sch['detail'] = ""
#                         if 'amount' in sch and not isinstance(sch['amount'], (int, float)):
#                             sch['amount'] = 0
#                         if 'currency' in sch and not isinstance(sch['currency'], str):
#                             sch['currency'] = ""
#                         if 'webLink' in sch and not isinstance(sch['webLink'], str):
#                             sch['webLink'] = ""
#                         elif sch.get('webLink'):
#                             parsed = urlparse(sch['webLink'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 sch['webLink'] = ""
#                         if 'deadline' in sch and not isinstance(sch['deadline'], str):
#                             sch['deadline'] = ""
#                         new_sch.append(sch)
#                 ed['scholarships'] = new_sch
        
#         # usefulLink: list of dicts
#         if 'usefulLink' in ed:
#             if not isinstance(ed['usefulLink'], list):
#                 ed['usefulLink'] = []
#             else:
#                 new_ul = []
#                 for ul in ed['usefulLink']:
#                     if isinstance(ul, dict):
#                         if 'title' in ul and not isinstance(ul['title'], str):
#                             ul['title'] = ""
#                         if 'detail' in ul and not isinstance(ul['detail'], str):
#                             ul['detail'] = ""
#                         if 'webLink' in ul and not isinstance(ul['webLink'], str):
#                             ul['webLink'] = ""
#                         elif ul.get('webLink'):
#                             parsed = urlparse(ul['webLink'])
#                             if not all([parsed.scheme, parsed.netloc]):
#                                 ul['webLink'] = ""
#                         new_ul.append(ul)
#                 ed['usefulLink'] = new_ul
        
#         # department: str
#         if 'department' in ed:
#             if not isinstance(ed['department'], str):
#                 ed['department'] = ""
    
#     return data


# def process_json_files(input_folder, output_folder):
#     if not os.path.exists(output_folder):
#         os.makedirs(output_folder)
   
#     for filename in os.listdir(input_folder):
#         if not filename.endswith('.json'):
#             continue
           
#         input_path = os.path.join(input_folder, filename)
#         output_path = os.path.join(output_folder, filename)
           
#         with open(input_path, 'r', encoding='utf-8') as f:
#             input_data = json.load(f)
           
#         extracted_data = {
#             'program': {'name': '', 'code': '', 'synonyms': ''},
#             'degree': {'name': '', 'code': '', 'type': '', 'synonyms': ''},
#             'department': '',
#             'session': [],
#             'durationYear': 0,
#             'deliveryType': [],
#             'admissionTimeline': [],
#             'tuitionFeePerYear': [],
#             'applicationFee': [],
#             'howToApply': [],
#             'admissionProgramTypes': [],
#             'generalRequirements': [],
#             'standardizedRequirements': [],
#             'languageRequirements': [],
#             'degreeRequirements': [],
#             'scholarships': [],
#             'usefulLink': [],
#             'university': {
#                 'name': input_data.get('university_name', '').strip(),
#                 'ranks': [],
#                 'campus': {}
#             },
#             'programUrl': input_data.get('programUrl', '').strip()
#         }

#         # --- 1. Try to get data from programVariants (preferred) ---
#         variant = {}
#         if 'extracted_data' in input_data:
#             raw_extracted = input_data['extracted_data']
#             if 'programVariants' in raw_extracted and raw_extracted['programVariants']:
#                 variant = raw_extracted['programVariants'][0]

#         if variant:
#             # Program identity
#             pi = variant.get('programIdentity', {})
#             extracted_data['program']['name'] = pi.get('program_name', '').strip()
#             extracted_data['degree']['name'] = pi.get('degree_name', '').strip()
#             extracted_data['program']['code'] = pi.get('degree_code', '').strip()
#             extracted_data['degree']['code'] = pi.get('degree_code', '').strip()
#             extracted_data['department'] = pi.get('department', '').strip()
#             extracted_data['overview'] = pi.get('general_overview', '').strip()

#             # Session & delivery from variant
#             sd = variant.get('sessionDelivery', {})
#             extracted_data['session'] = sd.get('session', [])
#             extracted_data['durationYear'] = sd.get('durationYear', 0)
#             extracted_data['deliveryType'] = sd.get('deliveryType', [])

#             # Other sections
#             extracted_data['admissionTimeline'] = variant.get('admissionTimeline', {}).get('admissionTimeline', [])
#             extracted_data['tuitionFeePerYear'] = variant.get('fees', {}).get('tuitionFeePerYear', [])
#             extracted_data['applicationFee'] = variant.get('fees', {}).get('applicationFee', [])
#             extracted_data['howToApply'] = variant.get('howToApply', {}).get('howToApply', [])
#             extracted_data['admissionProgramTypes'] = variant.get('admissionProgramTypes', {}).get('admissionProgramTypes', [])
#             extracted_data['generalRequirements'] = variant.get('generalRequirements', {}).get('generalRequirements', [])
#             extracted_data['standardizedRequirements'] = variant.get('standardizedRequirements', {}).get('standardizedRequirements', [])
#             extracted_data['languageRequirements'] = variant.get('languageRequirements', {}).get('languageRequirements', [])
#             extracted_data['degreeRequirements'] = variant.get('degreeRequirements', {}).get('degreeRequirements', [])
#             extracted_data['scholarships'] = variant.get('scholarships', {}).get('scholarships', [])

#             # usefulLink - robust handling
#             raw_ul = variant.get('usefulLink', [])
#             if isinstance(raw_ul, list):
#                 extracted_data['usefulLink'] = raw_ul
#             elif isinstance(raw_ul, dict):
#                 extracted_data['usefulLink'] = raw_ul.get('usefulLink', [])
#             else:
#                 extracted_data['usefulLink'] = []

#             # campus info
#             extracted_data['university']['campus'] = variant.get('campusInfo', {})

#         # --- 2. Fallback: Use top-level fields if variant is empty ---
#         if not variant:
#             # Use top-level program_name if available
#             if 'program_name' in input_data:
#                 extracted_data['program']['name'] = input_data['program_name'].strip()

#             # CRITICAL: Preserve top-level deliveryType
#             if 'deliveryType' in input_data and isinstance(input_data['deliveryType'], list):
#                 extracted_data['deliveryType'] = input_data['deliveryType']

#             # DO NOT extract links from program_content or page text!
#             # We explicitly set usefulLink = [] if no real data
#             extracted_data['usefulLink'] = []  # No junk links!

#         # --- 3. Copy country into campus if missing ---
#         campus = extracted_data['university']['campus']
#         if 'country' in input_data and input_data['country']:
#             if not campus.get('country'):
#                 campus['country'] = input_data['country'].strip()

#         # --- 4. Clean session titles before validation ---
#         cleaned_sessions = []
#         for sess in extracted_data['session']:
#             if isinstance(sess, dict) and 'title' in sess and isinstance(sess['title'], str):
#                 title_lower = sess['title'].lower()
#                 if any(season in title_lower for season in ['summer', 'fall', 'spring', 'winter']):
#                     cleaned_sessions.append(sess)
#                 else:
#                     # Keep but let fix_json_data handle emptying title if needed
#                     cleaned_sessions.append(sess)
#             else:
#                 cleaned_sessions.append(sess)
#         extracted_data['session'] = cleaned_sessions

#         # --- 5. Run validation ---
#         temp_data = {'extracted_data': extracted_data}
#         temp_data = fix_json_data(temp_data)

#         # --- 6. Save ---
#         output_data = {'extracted_data': temp_data['extracted_data']}
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(output_data, f, indent=4, ensure_ascii=False)

#         print(f"Processed: {filename}")

# input_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/deepseek_raw_output_utulsa'
# output_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/validate_output_new_utulsa'
# process_json_files(input_folder, output_folder)




import os
import json
import pandas as pd
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

def extract_ranks_from_data(data):
    """
    Extract all ranks from data.
    Supports rank_type_1, position_1, rank_type_2, position_2, etc.
    """
    ranks = []
    idx = 1
    
    # Check for rank_type_1, rank_type_2, etc.
    while True:
        rank_type_key = f"rank_type_{idx}" if idx > 1 else "rank_type_1"
        position_key = f"position_{idx}" if idx > 1 else "position_1"
        
        # Also check without suffix for first rank
        if idx == 1:
            # Try both rank_type and rank_type_1
            if "rank_type" in data and data["rank_type"]:
                rank_type_key = "rank_type"
                position_key = "position"
            elif "rank_type_1" not in data:
                break
        
        rank_type = data.get(rank_type_key, "")
        position = data.get(position_key, "")
        
        # Stop if no more ranks found
        if not rank_type or pd.isna(rank_type) or str(rank_type).strip() == "":
            break
        
        # Add rank
        ranks.append({
            "type": str(rank_type).strip(),
            "position": int(position) if position and not pd.isna(position) and str(position).strip() != "" else 0
        })
        
        idx += 1
    
    return ranks

def build_campus_info_with_fallback(variant, root_data):

    variant_campus = variant.get("campusInfo", {})
    
    # Build fallback from root data
    fallback_campus = {}
    
    # Map root fields to campusInfo fields
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
    
    # Extract from root data
    for root_field, campus_field in field_mappings.items():
        value = root_data.get(root_field, "")
        if value and not pd.isna(value) and str(value).strip() != "":
            fallback_campus[campus_field] = str(value).strip()
    
    # Build complete campusInfo by merging
    fields = ["name", "webUrl", "email", "phone", "country", "city", "zipCode", "address"]
    complete_campus = {}
    
    for field in fields:
        # Use variant if present and non-empty
        if field in variant_campus and str(variant_campus[field]).strip() != "":
            complete_campus[field] = str(variant_campus[field]).strip()
        else:
            # Fallback to root if available, else ""
            complete_campus[field] = fallback_campus.get(field, "")
    
    return complete_campus

def migrate_data_to_variants(data):
    """
    Migrate programUrl, university info into EACH programVariant.
    Move campusInfo from each variant to university.campusInfo within that variant.
    Apply fallback logic for campusInfo.
    """
    if "extracted_data" not in data:
        print("⚠️ No extracted_data found")
        return data
    
    extracted = data["extracted_data"]
    variants = extracted.get("programVariants", [])
    
    if not variants or len(variants) == 0:
        print("⚠️ No programVariants found")
        return data
    
    # Get data to copy to each variant
    program_url = data.get("programUrl", "")
    university_name = data.get("university_name", "")
    program_id = data.get("id", None)

    # Extract all ranks
    ranks = extract_ranks_from_data(data)
    
    # Process each variant
    for variant in variants:
        # 1. Add programUrl to this variant
        variant["programUrl"] = program_url
        
        # 2. Build university structure for this variant
        university = {
            "name": university_name,
            "ranks": ranks.copy(),  # Copy ranks list
            "campusInfo": {}
        }
        
        # 3. Build campusInfo with fallback logic
        campus_info = build_campus_info_with_fallback(variant, data)
        university["campusInfo"] = campus_info
        
        # Remove campusInfo from variant root (if exists)
        if "campusInfo" in variant:
            del variant["campusInfo"]
        
        # 4. Add university to this variant
        variant["university"] = university
        
        # 5. Handle fees - ensure arrays exist even if empty
        fees = variant.get("fees", {})
        if "tuitionFeePerYear" not in fees or fees["tuitionFeePerYear"] is None:
            fees["tuitionFeePerYear"] = []
        if "applicationFee" not in fees or fees["applicationFee"] is None:
            fees["applicationFee"] = []
        variant["fees"] = fees

        # 6. Add id to programIdentity if exists
        if program_id is not None:
            identity = variant.get("programIdentity", {})
            identity["id"] = program_id
            variant["programIdentity"] = identity    
    
    return data

def validate_required_fields(data, filename):
    """
    Validate required fields in extracted_data.
    Returns: (is_valid, list_of_errors)
    
    Rules:
    - Skip file if required fields have empty string "" when data should exist
    - Allow empty dict {} or empty array [] for optional structures
    """
    errors = []
    
    if "extracted_data" not in data:
        errors.append("Missing extracted_data")
        return False, errors
    
    extracted = data["extracted_data"]
    
    # Check programVariants
    variants = extracted.get("programVariants", [])
    if not variants or len(variants) == 0:
        errors.append("Empty programVariants")
        return False, errors
    
    # Validate each variant
    for idx, variant in enumerate(variants):
        variant_prefix = f"Variant[{idx}]"
        
        # Check programUrl (REQUIRED if exists)
        program_url = variant.get("programUrl", "")
        if program_url is None or (isinstance(program_url, str) and program_url == ""):
            # This is acceptable - no data found
            pass
        
        # Check university (REQUIRED)
        university = variant.get("university", {})
        if not university:
            errors.append(f"{variant_prefix}: Missing university object")
            continue
        
        # University name (REQUIRED if exists)
        if not university.get("name"):
            # Check if it's truly missing or just empty
            # If university object exists but name is "", that's a failure
            if "name" in university and university["name"] == "":
                errors.append(f"{variant_prefix}: university.name is empty string (should have data)")
        
        # Check campusInfo - can be empty dict {} if no data found
        campus = university.get("campusInfo", {})
        
        # If campusInfo is empty dict, that's OK (no data found)
        if not campus or len(campus) == 0:
            # Empty dict is acceptable
            pass 


            # If campusInfo exists but has empty required fields, that's a failure
            required_campus_fields = ["name","webUrl", "country", "city"]
            for field in required_campus_fields:
                if field in campus and campus[field] == "":
                    # Data structure exists but field is empty - this is a problem
                    errors.append(f"{variant_prefix}: university.campusInfo.{field} is empty string (should have data)")
        
        # Check programIdentity
        identity = variant.get("programIdentity", {})
        
        # REQUIRED: program_name (if exists)
        program_name = identity.get("program_name", "")
        if program_name == "" and "program_name" in identity:
            errors.append(f"{variant_prefix}: programIdentity.program_name is empty string (should have data)")
        
        # REQUIRED: degree info (if exists)
        degree_name = identity.get("degree_name", "")
        degree_type = identity.get("degree_type", "")
        
        # If degree fields exist but are empty, that's an error
        if "degree_name" in identity and degree_name == "":
            errors.append(f"{variant_prefix}: programIdentity.degree_name is empty string (should have data)")
        if "degree_type" in identity and degree_type == "":
            errors.append(f"{variant_prefix}: programIdentity.degree_type is empty string (should have data)")
                



        session_delivery = variant.get("sessionDelivery", {})
        delivery_types = session_delivery.get("deliveryType", [])
        
        if isinstance(delivery_types, list) and delivery_types:
            # Check each value in the list
            invalid_values = []
            for dt in delivery_types:
                if not isinstance(dt, str):
                    invalid_values.append(str(dt))
                elif dt.strip() not in ["Online", "Offline","Hybrid"]:
                    invalid_values.append(dt.strip())
            
            if invalid_values:
                # Deduplicate for cleaner error message
                unique_invalid = list(dict.fromkeys(invalid_values))  # preserves order
                errors.append(
                    f"{variant_prefix}: sessionDelivery.deliveryType contains invalid values: {unique_invalid}. "
                    "Only 'Online' and 'Offline' are allowed. 'Face-to-face' and 'Mixed' are not permitted."
                )



        # Check session (title is REQUIRED if sessions exist)
        sessions = variant.get("sessionDelivery", {}).get("session", [])

        allowed_titles = {"Fall", "Summer", "Spring"}
        if isinstance(sessions, list):
            # Filter the list: keep session only if title is in the allowed set
            # Note: Using session.get("title") handles missing keys or empty strings
            filtered_sessions = [
                s for s in sessions 
                if s.get("title") in allowed_titles
            ]

            # Update the dictionary with the cleaned list
            session_delivery["session"] = filtered_sessions

        if isinstance(sessions, list):
            for sess_idx, session in enumerate(sessions):
                if "title" in session and session.get("title") == "":
                    errors.append(f"{variant_prefix}: Session[{sess_idx}] has empty title (should have data)")
        
        # Check admissionTimeline (type is REQUIRED if timelines exist)
        timelines = variant.get("admissionTimeline", {}).get("admissionTimeline", [])
        if isinstance(timelines, list):
            for tl_idx, timeline in enumerate(timelines):
                if "type" in timeline and timeline.get("type") == "":
                    errors.append(f"{variant_prefix}: AdmissionTimeline[{tl_idx}] has empty type (should have data)")
        
        # Check fees - empty arrays [] are OK
        fees = variant.get("fees", {})

        # Process Tuition Fees
        tuition_fees = fees.get("tuitionFeePerYear", [])
        if isinstance(tuition_fees, list):
            # We only keep the fee if (amount is NOT 0) AND (currency is NOT empty)
            fees["tuitionFeePerYear"] = [
                f for f in tuition_fees 
                if isinstance(f, dict) and f.get("amount") != 0 and f.get("currency") != ""
            ]

        # Process Application Fees
        app_fees = fees.get("applicationFee", [])
        if isinstance(app_fees, list):
            # We only keep the fee if (amount is NOT 0) AND (currency is NOT empty)
            fees["applicationFee"] = [
                f for f in app_fees 
                if isinstance(f, dict) and f.get("amount") != 0 and f.get("currency") != ""
            ]


        # Check howToApply (title is REQUIRED if steps exist)
        how_to_apply = variant.get("howToApply", {}).get("howToApply", [])
        if isinstance(how_to_apply, list):
            for step_idx, step in enumerate(how_to_apply):
                if "title" in step and step.get("title") == "":
                    errors.append(f"{variant_prefix}: HowToApply[{step_idx}] has empty title (should have data)")
        
        # Check admissionProgramTypes (type and overview are REQUIRED if exist)
        program_types = variant.get("admissionProgramTypes", {}).get("admissionProgramTypes", [])
        if isinstance(program_types, list):
            for pt_idx, ptype in enumerate(program_types):
                if "type" in ptype and ptype.get("type") == "":
                    errors.append(f"{variant_prefix}: AdmissionProgramType[{pt_idx}] has empty type (should have data)")
                if "overview" in ptype and ptype.get("overview") == "":
                    errors.append(f"{variant_prefix}: AdmissionProgramType[{pt_idx}] has empty overview (should have data)")
        

        gen_reqs = variant.get("generalRequirements", {}).get("generalRequirements", [])
        if isinstance(gen_reqs, list):
            for req_idx, req in enumerate(gen_reqs):
                if "title" in req and req.get("title") == "":
                    errors.append(f"{variant_prefix}: GeneralRequirement[{req_idx}] has empty title (should have data)")
                if "title" in req and len(req.get("title")) > 49:
                    errors.append(f"{variant_prefix}: GeneralRequirement[{req_idx}] title is longer than 49 characters")



        # Check degreeRequirements (type is REQUIRED if exist)
        deg_reqs = variant.get("degreeRequirements", {}).get("degreeRequirements", [])
        if isinstance(deg_reqs, list):
            for req_idx, req in enumerate(deg_reqs):
                test = req.get("test", {})
                if "type" in test and test.get("type") == "":
                    errors.append(f"{variant_prefix}: DegreeRequirement[{req_idx}] has empty test.type (should have data)")
        

        # Check languageRequirements and remove dicts with empty test.type
        lang_reqs = variant.get("languageRequirements", {}).get("languageRequirements", [])
        if isinstance(lang_reqs, list):
            filtered_reqs = []
            all_empty = True
            for req in lang_reqs:
                test = req.get("test", {})
                if "type" in test and test.get("type") != "":
                    filtered_reqs.append(req)
                    all_empty = False
            if all_empty:
                variant["languageRequirements"]["languageRequirements"] = []
            else:
                variant["languageRequirements"]["languageRequirements"] = filtered_reqs


        
        scholarships = variant.get("scholarships", {}).get("scholarships", [])
        if isinstance(scholarships, list):
            for sch_idx, sch in enumerate(scholarships):
                if "type" in sch and sch.get("type") == "":
                    errors.append(
                        f"{variant_prefix}: Scholarship[{sch_idx}] has empty type (should have data)"
                    )

                if "name" in sch:
                    name = sch.get("name", "")

                    if name == "":
                        errors.append(
                            f"{variant_prefix}: Scholarship[{sch_idx}] has empty name (should have data)"
                        )
                    elif len(name) > 50:

                        # # Assign your specific value here
                        # name = "Entrance scholarship" 
                        
                        # # Update the original dictionary so the change persists
                        # sch["name"] = name 

                        errors.append(
                            f"{variant_prefix}: Scholarship[{sch_idx}] name is longer than 50 characters"
                        )


        # Check usefulLink (title is REQUIRED if exist)
        useful_links = variant.get("usefulLink", [])

        if isinstance(useful_links, list):
            # Filter out links with empty webLink or invalid webLink
            useful_links = [
                link for link in useful_links
                if isinstance(link, dict)
                and link.get("webLink", "").strip() != ""
                and link.get("webLink", "").strip().lower().startswith("http")
            ]
            variant["usefulLink"] = useful_links

            # Now validate the remaining
            for link_idx, link in enumerate(useful_links):
                if "title" in link and link.get("title", "").strip() == "":
                    errors.append(
                        f"{variant_prefix}: UsefulLink[{link_idx}] has empty title (should have data)"
                    )


    return len(errors) == 0, errors

def process_all_files(input_folder, output_folder, report_csv="validation_report.csv"):
    """
    Process all JSON files in input_folder.
    - Migrate data
    - Validate
    - Save ONLY valid files to output_folder
    - Generate report
    """
    # Create output folder
    os.makedirs(output_folder, exist_ok=True)
    
    # Find all JSON files
    json_files = list(Path(input_folder).glob("*.json"))
    total_files = len(json_files)
    
    print(f"Found {total_files} JSON files to process...")
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    print(f"Report will be saved to: {report_csv}\n")
    
    # Track results
    results = []
    processed = 0
    valid_count = 0
    invalid_count = 0
    
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
            invalid_count += 1
            processed += 1
            continue

        # # Rename pid to id if exists
        # if "pid" in data:
        #     data["id"] = data.pop("pid")
        #     # Strip the prefix to keep only the UUID part
        #     data["id"] = data["id"].split('_')[-1]


        # Step 1: Migrate data
        print("  ↳ Migrating data to variants...")
        data = migrate_data_to_variants(data)
        
        # Step 2: Validate
        print("  ↳ Validating required fields...")
        is_valid, validation_errors = validate_required_fields(data, filename)
        
        if is_valid:
            print("  ✅ Validation passed - saving to output folder")
            
            # Save to output folder
            output_path = Path(output_folder) / filename
            if save_json_file(output_path, data):
                print(f"  💾 Saved to: {output_path}")
                status = "VALID"
                valid_count += 1
            else:
                status = "SAVE_FAILED"
                invalid_count += 1
        else:
            print(f"  ❌ Validation FAILED: {len(validation_errors)} errors - NOT saving")
            for err in validation_errors[:10]:  # Show first 10 errors
                print(f"     - {err}")
            if len(validation_errors) > 10:
                print(f"     ... and {len(validation_errors)-10} more errors")
            status = "INVALID"
            invalid_count += 1
        
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
    print(f"✅ VALIDATION COMPLETE!")
    print(f"{'='*70}")
    print(f"Total files processed:        {total_files}")
    print(f"Valid files (saved):          {valid_count}")
    print(f"Invalid files (NOT saved):    {invalid_count}")
    print(f"Success rate:                 {(valid_count/total_files)*100:.1f}%")
    print(f"\nValid files saved to:         {output_folder}")
    print(f"Validation report saved to:   {report_path}")
    print(f"{'='*70}")
    
    # Show breakdown by status
    print(f"\nStatus Breakdown:")
    status_counts = df_report['status'].value_counts()
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    return df_report


if __name__ == "__main__":
    # Configuration
    INPUT_FOLDER = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-3_output_final_program_data/updated_extracted_jsons_uot_UGprograms"
    OUTPUT_FOLDER = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/uot_UGprograms_raw_data-validate"
    REPORT_CSV = "/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/uot_UGprograms_raw_data-validate/validation_report.csv" 

    # Run validation
    df_report = process_all_files(
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        report_csv=REPORT_CSV
    )
    
    print(f"\n✅ Done! Check '{REPORT_CSV}' for detailed validation results.")
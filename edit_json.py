# # import json
# # import os

# # def process_json_files(input_folder, output_folder):
# #     # Create output folder if it doesn't exist
# #     if not os.path.exists(output_folder):
# #         os.makedirs(output_folder)
    
# #     # Iterate over all files in the input folder
# #     for filename in os.listdir(input_folder):
# #         if filename.endswith('.json'):
# #             input_path = os.path.join(input_folder, filename)
# #             output_path = os.path.join(output_folder, filename)
            
# #             # Load the JSON data
# #             with open(input_path, 'r', encoding='utf-8') as f:
# #                 data = json.load(f)
            
# #             # Check if 'extracted_data' exists
# #             if 'extracted_data' in data:
# #                 extracted = data['extracted_data']
                
# #                 # Check if 'admissionProgramTypes' exists and is a list with at least one item
# #                 if 'admissionProgramTypes' in extracted and isinstance(extracted['admissionProgramTypes'], list) and len(extracted['admissionProgramTypes']) > 0:
# #                     program_type = extracted['admissionProgramTypes'][0]
                    
# #                     # If 'department' key exists in the first admissionProgramTypes dict
# #                     if 'department' in program_type:
# #                         # Move it to extracted_data level
# #                         extracted['department'] = program_type.pop('department')
            
# #             # Save the modified JSON to the output folder
# #             with open(output_path, 'w', encoding='utf-8') as f:
# #                 json.dump(data, f, indent=4)

# # # Example usage: replace with your folder paths
# # input_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/phase-3_output_final_program_data/extracted_structured_json_wyoming_latest_3'
# # output_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_structured_json_wyoming_latest_3_fixed'
# # process_json_files(input_folder, output_folder)


# # import json
# # import os
# # import re
# # from urllib.parse import urlparse

# # def validate_json_data(data):
# #     # This function validates all fields in the JSON data based on the provided examples.
# #     # Each validation includes type check, optional non-emptiness, and format where applicable.
# #     # Explanations are provided in comments for each field.
# #     # Incorporated previous updates: enforce country is 'USA', campus name does not contain 'in-person & online', session titles are empty or contain 'summer', 'fall', or 'spring'.

# #     # Top-level fields

# #     # university_name: Should be a non-empty string as it identifies the university.
# #     if 'university_name' in data:
# #         if not isinstance(data['university_name'], str) or not data['university_name'].strip():
# #             raise ValueError('university_name must be a non-empty string')

# #     # program_name: Should be a non-empty string representing the program name.
# #     if 'program_name' in data:
# #         if not isinstance(data['program_name'], str) or not data['program_name'].strip():
# #             raise ValueError('program_name must be a non-empty string')

# #     # degree_type: Should be a string, can be empty if not applicable.
# #     if 'degree_type' in data:
# #         if not isinstance(data['degree_type'], str):
# #             raise ValueError('degree_type must be a string')

# #     # program_content: Should be a string containing the program description, can be long.
# #     if 'program_content' in data:
# #         if not isinstance(data['program_content'], str):
# #             raise ValueError('program_content must be a string')

# #     # degree_program_link: Should be a valid URL string if present.
# #     if 'degree_program_link' in data:
# #         if not isinstance(data['degree_program_link'], str):
# #             raise ValueError('degree_program_link must be a string')
# #         if data['degree_program_link']:
# #             parsed = urlparse(data['degree_program_link'])
# #             if not all([parsed.scheme, parsed.netloc]):
# #                 raise ValueError('Invalid URL for degree_program_link')

# #     # programUrl: Should be a valid URL string.
# #     if 'programUrl' in data:
# #         if not isinstance(data['programUrl'], str):
# #             raise ValueError('programUrl must be a string')
# #         if data['programUrl']:
# #             parsed = urlparse(data['programUrl'])
# #             if not all([parsed.scheme, parsed.netloc]):
# #                 raise ValueError('Invalid URL for programUrl')

# #     # rank_type: Should be a string like 'CS'.
# #     if 'rank_type' in data:
# #         if not isinstance(data['rank_type'], str):
# #             raise ValueError('rank_type must be a string')

# #     # position: Should be a string representing a number or empty.
# #     if 'position' in data:
# #         if not isinstance(data['position'], str):
# #             raise ValueError('position must be a string')
# #         if data['position'] and not data['position'].isdigit():
# #             raise ValueError('position should be a string of digits if present')

# #     # campus_name: Should be a string.
# #     if 'campus_name' in data:
# #         if not isinstance(data['campus_name'], str):
# #             raise ValueError('campus_name must be a string')

# #     # url: Should be a valid URL string if present (university url).
# #     if 'url' in data:
# #         if not isinstance(data['url'], str):
# #             raise ValueError('url must be a string')
# #         if data['url']:
# #             parsed = urlparse(data['url'])
# #             if not all([parsed.scheme, parsed.netloc]):
# #                 raise ValueError('Invalid URL for url')

# #     # email: Should be a valid email string if present.
# #     email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
# #     if 'email' in data:
# #         if not isinstance(data['email'], str):
# #             raise ValueError('email must be a string')
# #         if data['email'] and not email_pattern.match(data['email']):
# #             raise ValueError('Invalid email format')

# #     # phone: Should be a string, perhaps validate format but kept simple.
# #     if 'phone' in data:
# #         if not isinstance(data['phone'], str):
# #             raise ValueError('phone must be a string')

# #     # country: Should be a string, like 'USA'.
# #     if 'country' in data:
# #         if not isinstance(data['country'], str):
# #             raise ValueError('country must be a string')

# #     # city: Should be a string.
# #     if 'city' in data:
# #         if not isinstance(data['city'], str):
# #             raise ValueError('city must be a string')

# #     # zipCode: Should be a string.
# #     if 'zipCode' in data:
# #         if not isinstance(data['zipCode'], str):
# #             raise ValueError('zipCode must be a string')

# #     # address: Should be a string.
# #     if 'address' in data:
# #         if not isinstance(data['address'], str):
# #             raise ValueError('address must be a string')

# #     # admissionProgramTypes_overview: Should be a string if present (overview text).
# #     if 'admissionProgramTypes_overview' in data:
# #         if not isinstance(data['admissionProgramTypes_overview'], str):
# #             raise ValueError('admissionProgramTypes_overview must be a string')

# #     # category_name: Should be a string.
# #     if 'category_name' in data:
# #         if not isinstance(data['category_name'], str):
# #             raise ValueError('category_name must be a string')

# #     # first_layer: Should be a valid URL string if present.
# #     if 'first_layer' in data:
# #         if not isinstance(data['first_layer'], str):
# #             raise ValueError('first_layer must be a string')
# #         if data['first_layer']:
# #             parsed = urlparse(data['first_layer'])
# #             if not all([parsed.scheme, parsed.netloc]):
# #                 raise ValueError('Invalid URL for first_layer')

# #     # extracted_data: Should be a dict if present.
# #     if 'extracted_data' in data:
# #         if not isinstance(data['extracted_data'], dict):
# #             raise ValueError('extracted_data must be a dict')
# #         ed = data['extracted_data']

# #         # Inside extracted_data

# #         # program: dict with name, code, synonyms - all strings.
# #         if 'program' in ed:
# #             if not isinstance(ed['program'], dict):
# #                 raise ValueError('extracted_data.program must be a dict')
# #             p = ed['program']
# #             if 'name' in p and not isinstance(p['name'], str):
# #                 raise ValueError('program.name must be str')
# #             if 'code' in p and not isinstance(p['code'], str):
# #                 raise ValueError('program.code must be str')
# #             if 'synonyms' in p and not isinstance(p['synonyms'], str):
# #                 raise ValueError('program.synonyms must be str')

# #         # degree: dict with name, code, type, synonyms - all strings.
# #         if 'degree' in ed:
# #             if not isinstance(ed['degree'], dict):
# #                 raise ValueError('extracted_data.degree must be a dict')
# #             d = ed['degree']
# #             if 'name' in d and not isinstance(d['name'], str):
# #                 raise ValueError('degree.name must be str')
# #             if 'code' in d and not isinstance(d['code'], str):
# #                 raise ValueError('degree.code must be str')
# #             if 'type' in d and not isinstance(d['type'], str):
# #                 raise ValueError('degree.type must be str')
# #             if 'synonyms' in d and not isinstance(d['synonyms'], str):
# #                 raise ValueError('degree.synonyms must be str')

# #         # university: dict with name str, ranks list, campus dict.
# #         if 'university' in ed:
# #             if not isinstance(ed['university'], dict):
# #                 raise ValueError('extracted_data.university must be a dict')
# #             u = ed['university']
# #             if 'name' in u and not isinstance(u['name'], str):
# #                 raise ValueError('university.name must be str')
# #             if 'ranks' in u:
# #                 if not isinstance(u['ranks'], list):
# #                     raise ValueError('university.ranks must be list')
# #                 for rank in u['ranks']:
# #                     if not isinstance(rank, dict):
# #                         raise ValueError('Each rank must be dict')
# #                     if 'type' in rank and not isinstance(rank['type'], str):
# #                         raise ValueError('rank.type must be str')
# #                     if 'position' in rank and not isinstance(rank['position'], int):
# #                         raise ValueError('rank.position must be int')
# #             if 'campus' in u:
# #                 if not isinstance(u['campus'], dict):
# #                     raise ValueError('university.campus must be dict')
# #                 c = u['campus']
# #                 if 'name' in c and not isinstance(c['name'], str):
# #                     raise ValueError('campus.name must be str')
# #                 if 'name' in c:
# #                     name = c['name'].lower()
# #                     if (
# #                         "in-person & online" in name
# #                         or "in-person" in name
# #                         or "online" in name
# #                     ):
# #                         raise ValueError('campus.name should not contain "in-person", "online", or "in-person & online"')

# #                 if 'webUrl' in c and not isinstance(c['webUrl'], str):
# #                     raise ValueError('campus.webUrl must be str')
# #                 if c.get('webUrl'):
# #                     parsed = urlparse(c['webUrl'])
# #                     if not all([parsed.scheme, parsed.netloc]):
# #                         raise ValueError('Invalid URL for campus.webUrl')
# #                 if 'email' in c and not isinstance(c['email'], str):
# #                     raise ValueError('campus.email must be str')
# #                 if c.get('email') and not email_pattern.match(c['email']):
# #                     raise ValueError('Invalid email for campus.email')
# #                 if 'phone' in c and not isinstance(c['phone'], str):
# #                     raise ValueError('campus.phone must be str')
# #                 if 'country' in c and not isinstance(c['country'], str) or c.get('country') != "USA":
# #                     raise ValueError('campus.country must be "USA"')
# #                 if 'city' in c and not isinstance(c['city'], str):
# #                     raise ValueError('campus.city must be str')
# #                 if 'zipCode' in c and not isinstance(c['zipCode'], str):
# #                     raise ValueError('campus.zipCode must be str')
# #                 if 'address' in c and not isinstance(c['address'], str):
# #                     raise ValueError('campus.address must be str')

# #         # programUrl: Already checked at top-level, but if in extracted, same.
# #         if 'programUrl' in ed:
# #             if not isinstance(ed['programUrl'], str):
# #                 raise ValueError('extracted_data.programUrl must be str')
# #             if ed['programUrl']:
# #                 parsed = urlparse(ed['programUrl'])
# #                 if not all([parsed.scheme, parsed.netloc]):
# #                     raise ValueError('Invalid URL for extracted_data.programUrl')

# #         # session: list, items can be dict with title str (only Summer, Fall, Spring or empty)
# #         if 'session' in ed:
# #             if not isinstance(ed['session'], list):
# #                 raise ValueError('session must be list')
# #             for s in ed['session']:
# #                 if not isinstance(s, dict):
# #                     raise ValueError('Each session must be dict')
# #                 if 'title' in s:
# #                     if not isinstance(s['title'], str):
# #                         raise ValueError('session.title must be str')
# #                     title_lower = s['title'].lower()
# #                     if title_lower and not any(season in title_lower for season in ['summer', 'fall', 'spring']):
# #                         raise ValueError('session.title must be empty or contain summer, fall, or spring')

# #         # durationYear: int or float.
# #         if 'durationYear' in ed:
# #             if not isinstance(ed['durationYear'], (int, float)):
# #                 raise ValueError('durationYear must be int or float')

# #         # deliveryType: list
# #         if 'deliveryType' in ed:
# #             if not isinstance(ed['deliveryType'], list):
# #                 raise ValueError('deliveryType must be list')

# #         # admissionTimeline: list
# #         if 'admissionTimeline' in ed:
# #             if not isinstance(ed['admissionTimeline'], list):
# #                 raise ValueError('admissionTimeline must be list')

# #         # tuitionFeePerYear: list
# #         if 'tuitionFeePerYear' in ed:
# #             if not isinstance(ed['tuitionFeePerYear'], list):
# #                 raise ValueError('tuitionFeePerYear must be list')

# #         # applicationFee: list
# #         if 'applicationFee' in ed:
# #             if not isinstance(ed['applicationFee'], list):
# #                 raise ValueError('applicationFee must be list')

# #         # howToApply: list of dict {title str, detail str, webLink str}
# #         if 'howToApply' in ed:
# #             if not isinstance(ed['howToApply'], list):
# #                 raise ValueError('howToApply must be list')
# #             for h in ed['howToApply']:
# #                 if not isinstance(h, dict):
# #                     raise ValueError('Each howToApply item must be dict')
# #                 if 'title' in h and not isinstance(h['title'], str):
# #                     raise ValueError('howToApply.title must be str')
# #                 if 'detail' in h and not isinstance(h['detail'], str):
# #                     raise ValueError('howToApply.detail must be str')
# #                 if 'webLink' in h and not isinstance(h['webLink'], str):
# #                     raise ValueError('howToApply.webLink must be str')
# #                 if h.get('webLink'):
# #                     parsed = urlparse(h['webLink'])
# #                     if not all([parsed.scheme, parsed.netloc]):
# #                         raise ValueError('Invalid URL for howToApply.webLink')

# #         # admissionProgramTypes: list of dict {type str, overview str, courseOutline list of dict {title str, detail str}, department str (if present)}
# #         if 'admissionProgramTypes' in ed:
# #             if not isinstance(ed['admissionProgramTypes'], list):
# #                 raise ValueError('admissionProgramTypes must be list')
# #             for apt in ed['admissionProgramTypes']:
# #                 if not isinstance(apt, dict):
# #                     raise ValueError('Each admissionProgramTypes item must be dict')
# #                 if 'type' in apt and not isinstance(apt['type'], str):
# #                     raise ValueError('admissionProgramTypes.type must be str')
# #                 if 'overview' in apt and not isinstance(apt['overview'], str):
# #                     raise ValueError('admissionProgramTypes.overview must be str')
# #                 if 'department' in apt and not isinstance(apt['department'], str):
# #                     raise ValueError('admissionProgramTypes.department must be str')
# #                 if 'courseOutline' in apt:
# #                     if not isinstance(apt['courseOutline'], list):
# #                         raise ValueError('courseOutline must be list')
# #                     for co in apt['courseOutline']:
# #                         if not isinstance(co, dict):
# #                             raise ValueError('Each courseOutline item must be dict')
# #                         if 'title' in co and not isinstance(co['title'], str):
# #                             raise ValueError('courseOutline.title must be str')
# #                         if 'detail' in co and not isinstance(co['detail'], str):
# #                             raise ValueError('courseOutline.detail must be str')

# #         # generalRequirements: list of dict {type str, title str, page int, words int, count int, details str}
# #         if 'generalRequirements' in ed:
# #             if not isinstance(ed['generalRequirements'], list):
# #                 raise ValueError('generalRequirements must be list')
# #             for gr in ed['generalRequirements']:
# #                 if not isinstance(gr, dict):
# #                     raise ValueError('Each generalRequirements item must be dict')
# #                 if 'type' in gr and not isinstance(gr['type'], str):
# #                     raise ValueError('generalRequirements.type must be str')
# #                 if 'title' in gr and not isinstance(gr['title'], str):
# #                     raise ValueError('generalRequirements.title must be str')
# #                 if 'page' in gr and not isinstance(gr['page'], int):
# #                     raise ValueError('generalRequirements.page must be int')
# #                 if 'words' in gr and not isinstance(gr['words'], int):
# #                     raise ValueError('generalRequirements.words must be int')
# #                 if 'count' in gr and not isinstance(gr['count'], int):
# #                     raise ValueError('generalRequirements.count must be int')
# #                 if 'details' in gr and not isinstance(gr['details'], str):
# #                     raise ValueError('generalRequirements.details must be str')

# #         # standardizedRequirements: list of dict {test dict {type str, total float, verbal float, quant float, awa float, required bool}}
# #         if 'standardizedRequirements' in ed:
# #             if not isinstance(ed['standardizedRequirements'], list):
# #                 raise ValueError('standardizedRequirements must be list')
# #             for sr in ed['standardizedRequirements']:
# #                 if not isinstance(sr, dict):
# #                     raise ValueError('Each standardizedRequirements item must be dict')
# #                 if 'test' in sr:
# #                     if not isinstance(sr['test'], dict):
# #                         raise ValueError('standardizedRequirements.test must be dict')
# #                     t = sr['test']
# #                     if 'type' in t and not isinstance(t['type'], str):
# #                         raise ValueError('test.type must be str')
# #                     if 'total' in t and not isinstance(t['total'], (int, float)):
# #                         raise ValueError('test.total must be number')
# #                     if 'verbal' in t and not isinstance(t['verbal'], (int, float)):
# #                         raise ValueError('test.verbal must be number')
# #                     if 'quant' in t and not isinstance(t['quant'], (int, float)):
# #                         raise ValueError('test.quant must be number')
# #                     if 'awa' in t and not isinstance(t['awa'], (int, float)):
# #                         raise ValueError('test.awa must be number')
# #                     if 'required' in t and not isinstance(t['required'], bool):
# #                         raise ValueError('test.required must be bool')

# #         # languageRequirements: similar to standardized, but with listening, reading, writing, speaking
# #         if 'languageRequirements' in ed:
# #             if not isinstance(ed['languageRequirements'], list):
# #                 raise ValueError('languageRequirements must be list')
# #             for lr in ed['languageRequirements']:
# #                 if not isinstance(lr, dict):
# #                     raise ValueError('Each languageRequirements item must be dict')
# #                 if 'test' in lr:
# #                     if not isinstance(lr['test'], dict):
# #                         raise ValueError('languageRequirements.test must be dict')
# #                     t = lr['test']
# #                     if 'type' in t and not isinstance(t['type'], str):
# #                         raise ValueError('test.type must be str')
# #                     if 'total' in t and not isinstance(t['total'], (int, float)):
# #                         raise ValueError('test.total must be number')
# #                     if 'listening' in t and not isinstance(t['listening'], (int, float)):
# #                         raise ValueError('test.listening must be number')
# #                     if 'reading' in t and not isinstance(t['reading'], (int, float)):
# #                         raise ValueError('test.reading must be number')
# #                     if 'writing' in t and not isinstance(t['writing'], (int, float)):
# #                         raise ValueError('test.writing must be number')
# #                     if 'speaking' in t and not isinstance(t['speaking'], (int, float)):
# #                         raise ValueError('test.speaking must be number')
# #                     if 'required' in t and not isinstance(t['required'], bool):
# #                         raise ValueError('test.required must be bool')

# #         # degreeRequirements: list of dict {test dict {details str, type str, total float, outOf float, region str}}
# #         if 'degreeRequirements' in ed:
# #             if not isinstance(ed['degreeRequirements'], list):
# #                 raise ValueError('degreeRequirements must be list')
# #             for dr in ed['degreeRequirements']:
# #                 if not isinstance(dr, dict):
# #                     raise ValueError('Each degreeRequirements item must be dict')
# #                 if 'test' in dr:
# #                     if not isinstance(dr['test'], dict):
# #                         raise ValueError('degreeRequirements.test must be dict')
# #                     t = dr['test']
# #                     if 'details' in t and not isinstance(t['details'], str):
# #                         raise ValueError('test.details must be str')
# #                     if 'type' in t and not isinstance(t['type'], str):
# #                         raise ValueError('test.type must be str')
# #                     if 'total' in t and not isinstance(t['total'], (int, float)):
# #                         raise ValueError('test.total must be number')
# #                     if 'outOf' in t and not isinstance(t['outOf'], (int, float)):
# #                         raise ValueError('test.outOf must be number')
# #                     if 'region' in t and not isinstance(t['region'], str):
# #                         raise ValueError('test.region must be str')

# #         # scholarships: list of dict {type str, name str, requirement list of str, detail str, amount int/float, currency str, webLink str, deadline str}
# #         if 'scholarships' in ed:
# #             if not isinstance(ed['scholarships'], list):
# #                 raise ValueError('scholarships must be list')
# #             for sch in ed['scholarships']:
# #                 if not isinstance(sch, dict):
# #                     raise ValueError('Each scholarships item must be dict')
# #                 if 'type' in sch and not isinstance(sch['type'], str):
# #                     raise ValueError('scholarships.type must be str')
# #                 if 'name' in sch and not isinstance(sch['name'], str):
# #                     raise ValueError('scholarships.name must be str')
# #                 if 'requirement' in sch:
# #                     if not isinstance(sch['requirement'], list):
# #                         raise ValueError('scholarships.requirement must be list')
# #                     for req in sch['requirement']:
# #                         if not isinstance(req, str):
# #                             raise ValueError('Each requirement must be str')
# #                 if 'detail' in sch and not isinstance(sch['detail'], str):
# #                     raise ValueError('scholarships.detail must be str')
# #                 if 'amount' in sch and not isinstance(sch['amount'], (int, float)):
# #                     raise ValueError('scholarships.amount must be number')
# #                 if 'currency' in sch and not isinstance(sch['currency'], str):
# #                     raise ValueError('scholarships.currency must be str')
# #                 if 'webLink' in sch and not isinstance(sch['webLink'], str):
# #                     raise ValueError('scholarships.webLink must be str')
# #                 if sch.get('webLink'):
# #                     parsed = urlparse(sch['webLink'])
# #                     if not all([parsed.scheme, parsed.netloc]):
# #                         raise ValueError('Invalid URL for scholarships.webLink')
# #                 if 'deadline' in sch and not isinstance(sch['deadline'], str):
# #                     raise ValueError('scholarships.deadline must be str')

# #         # usefulLink: list of dict {title str, detail str, webLink str}
# #         if 'usefulLink' in ed:
# #             if not isinstance(ed['usefulLink'], list):
# #                 raise ValueError('usefulLink must be list')
# #             for ul in ed['usefulLink']:
# #                 if not isinstance(ul, dict):
# #                     raise ValueError('Each usefulLink item must be dict')
# #                 if 'title' in ul and not isinstance(ul['title'], str):
# #                     raise ValueError('usefulLink.title must be str')
# #                 if 'detail' in ul and not isinstance(ul['detail'], str):
# #                     raise ValueError('usefulLink.detail must be str')
# #                 if 'webLink' in ul and not isinstance(ul['webLink'], str):
# #                     raise ValueError('usefulLink.webLink must be str')
# #                 if ul.get('webLink'):
# #                     parsed = urlparse(ul['webLink'])
# #                     if not all([parsed.scheme, parsed.netloc]):
# #                         raise ValueError('Invalid URL for usefulLink.webLink')

# #         # department: str if present (after moving)
# #         if 'department' in ed:
# #             if not isinstance(ed['department'], str):
# #                 raise ValueError('extracted_data.department must be str')

# #     # If no errors, data is valid
# #     return True

# # def process_json_files(input_folder, output_folder):
# #     if not os.path.exists(output_folder):
# #         os.makedirs(output_folder)
    
# #     for filename in os.listdir(input_folder):
# #         if filename.endswith('.json'):
# #             input_path = os.path.join(input_folder, filename)
# #             output_path = os.path.join(output_folder, filename)
            
# #             with open(input_path, 'r', encoding='utf-8') as f:
# #                 data = json.load(f)
            
# #             # Proceed with processing (fixing) first
# #             if 'extracted_data' in data:
# #                 extracted = data['extracted_data']
                
# #                 if 'admissionProgramTypes' in extracted and isinstance(extracted['admissionProgramTypes'], list) and len(extracted['admissionProgramTypes']) > 0:
# #                     program_type = extracted['admissionProgramTypes'][0]
                    
# #                     if 'department' in program_type:
# #                         extracted['department'] = program_type.pop('department')
                
# #                 if 'university' in extracted:
# #                     uni = extracted['university']
# #                     if 'campus' in uni:
# #                         campus = uni['campus']
# #                         campus['country'] = "USA"
# #                         # if isinstance(campus.get('name'), str) and "in-person & online" in campus['name'].lower():
# #                         #     campus['name'] = ""


# #                         if isinstance(campus.get('name'), str):
# #                             name = campus['name'].lower()
# #                             if (
# #                                 "in-person & online" in name
# #                                 or "in-person" in name
# #                                 or "online" in name
# #                             ):
# #                                 campus['name'] = ""


# #                 if 'session' in extracted and isinstance(extracted['session'], list):
# #                     for sess in extracted['session']:
# #                         if isinstance(sess, dict) and 'title' in sess and isinstance(sess['title'], str):
# #                             title_lower = sess['title'].lower()
# #                             if not any(season in title_lower for season in ['summer', 'fall', 'spring']):
# #                                 sess['title'] = ""
            
# #             # Now validate the fixed data
# #             try:
# #                 validate_json_data(data)
# #             except ValueError as e:
# #                 print(f"Validation error in {filename}: {e}")
# #                 continue  # Skip invalid files or handle as needed
            
# #             # Save if valid
# #             with open(output_path, 'w', encoding='utf-8') as f:
# #                 json.dump(data, f, indent=4)

# # # Your folder paths
# # input_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_structured_json_utulsa_latest'
# # output_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_structured_json_utulsa_latest_2_fixed'
# # process_json_files(input_folder, output_folder)





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
#                 data = json.load(f)
            
#             # Proceed with processing (fixing) first
#             if 'extracted_data' in data:
#                 extracted = data['extracted_data']
                
#                 if 'admissionProgramTypes' in extracted and isinstance(extracted['admissionProgramTypes'], list) and len(extracted['admissionProgramTypes']) > 0:
#                     program_type = extracted['admissionProgramTypes'][0]
                    
#                     if 'department' in program_type:
#                         extracted['department'] = program_type.pop('department')
                
#                 if 'university' in extracted:
#                     uni = extracted['university']
#                     if 'campus' in uni:
#                         campus = uni['campus']
#                         campus['country'] = "USA"
#                         if isinstance(campus.get('name'), str):
#                             name = campus['name'].lower()
#                             if (
#                                 "in-person & online" in name
#                                 or "in-person" in name
#                                 or "online" in name
#                             ):
#                                 campus['name'] = ""

                
#                 if 'session' in extracted and isinstance(extracted['session'], list):
#                     for sess in extracted['session']:
#                         if isinstance(sess, dict) and 'title' in sess and isinstance(sess['title'], str):
#                             title_lower = sess['title'].lower()
#                             if not any(season in title_lower for season in ['summer', 'fall', 'spring']):
#                                 sess['title'] = ""
            
#             # Now fix the data
#             data = fix_json_data(data)
            
#             # Save
#             with open(output_path, 'w', encoding='utf-8') as f:
#                 json.dump(data, f, indent=4)

# # Your folder paths
# input_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_structured_json_utulsa_latest'
# output_folder = '/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/extracted_structured_json_utulsa_latest_2_fixed'
# process_json_files(input_folder, output_folder)


import json
from pathlib import Path

DEGREE_TYPE = {
    "AA":"Associate","A.A.":"Associate","AS":"Associate","A.S.":"Associate","AAS":"Associate","A.A.S.":"Associate",
    "BA":"Bachelor","B.A.":"Bachelor","BS":"Bachelor","B.S.":"Bachelor","BSc":"Bachelor","B.Sc.":"Bachelor",
    "BAS":"Bachelor","B.A.S.":"Bachelor","BEng":"Bachelor","B.Eng.":"Bachelor","BE":"Bachelor","B.E.":"Bachelor",
    "BTech":"Bachelor","B.Tech.":"Bachelor","BFA":"Bachelor","B.F.A.":"Bachelor","BM":"Bachelor","B.M.":"Bachelor",
    "BMus":"Bachelor","B.Mus.":"Bachelor","BBA":"Bachelor","B.B.A.":"Bachelor","BSBA":"Bachelor","BCom":"Bachelor",
    "B.Com.":"Bachelor","LLB":"Bachelor","LL.B.":"Bachelor",
    "MA":"Master","M.A.":"Master","MS":"Master","M.S.":"Master","MSc":"Master","M.Sc.":"Master",
    "MBA":"Master","M.B.A.":"Master","MPA":"Master","M.P.A.":"Master","MPP":"Master","M.P.P.":"Master",
    "MPH":"Master","M.P.H.":"Master","MEng":"Master","M.Eng.":"Master","ME":"Master","M.E.":"Master",
    "MEd":"Master","M.Ed.":"Master","MSW":"Master","M.S.W.":"Master","LLM":"Master","LL.M.":"Master",
    "PhD":"Doctor of Philosophy","Ph.D.":"Doctor of Philosophy","DPhil":"Doctor of Philosophy","D.Phil.":"Doctor of Philosophy",
    "EdD":"Doctorate","Ed.D.":"Doctorate","DBA":"Doctorate","D.B.A.":"Doctorate","JD":"Doctorate","J.D.":"Doctorate",
    "MD":"Doctorate","M.D.":"Doctorate","DO":"Doctorate","D.O.":"Doctorate","DSc":"Doctorate","D.Sc.":"Doctorate",
    "ScD":"Doctorate","Sc.D.":"Doctorate",
    "Grad Cert":"Graduate Certificate","Graduate Cert":"Graduate Certificate",
    "UG Cert":"Undergraduate Certificate",
    "PGCert":"Postgraduate Certificate","PG Cert":"Postgraduate Certificate","Postgrad Cert":"Postgraduate Certificate",
    "PGDip":"Postgraduate Diploma","Postgrad Dip":"Postgraduate Diploma",
    "Cert":"Certificate","Dip":"Diploma","Dipl":"Diploma"
}
def fill_degree_requirements_test_type(data):
    try:
        items = data["extracted_data"]["programVariants"][0]["degreeRequirements"]["degreeRequirements"]
    except Exception:
        return

    if not isinstance(items, list):
        return

    for item in items:
        test = item.get("test")
        if not isinstance(test, dict):
            continue

        if test.get("type") is None or (isinstance(test.get("type"), str) and test.get("type").strip() == ""):
            test["type"] = "Default"

def is_non_empty(v):
    return v is not None and (not isinstance(v, str) or v.strip() != "")

def fill_campus_info(data):
    try:
        campus = data["extracted_data"]["programVariants"][0]["campusInfo"]
    except KeyError:
        return

    mapping = {
        "webUrl": "url",
        "email": "email",
        "phone": "phone",
        "country": "country",
        "city": "city",
        "zipCode": "zipCode",
        "address": "address",
    }

    for target, source in mapping.items():
        if is_non_empty(data.get(source)):
            campus[target] = data[source]

    # name priority:
    # 1) if top-level name exists -> use it
    # 2) else if top-level city exists -> use city
    if is_non_empty(data.get("name")):
        campus["name"] = data["name"]
    elif is_non_empty(data.get("city")):
        campus["name"] = data["city"]

def fill_degree_type(data):
    try:
        identity = data["extracted_data"]["programVariants"][0]["programIdentity"]
    except KeyError:
        return

    code = identity.get("degree_code")
    if not code:
        return

    degree_type = DEGREE_TYPE.get(code.strip())
    if degree_type:
        identity["degree_type"] = degree_type

def process_file(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not delete_if_no_program_name(data, path):
        return

    fill_campus_info(data)
    fill_degree_defaults(data)
    fill_general_requirements_titles(data)
    fill_degree_requirements_test_type(data)  # 👈 ADD THIS

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def fill_degree_requirements_default(data):
    try:
        degree_reqs = data["extracted_data"]["programVariants"][0]["degreeRequirements"]["degreeRequirements"]
    except (KeyError, TypeError):
        return

    for item in degree_reqs:
        test = item.get("test")
        if not isinstance(test, dict):
            continue

        t = test.get("type")
        if t is None or (isinstance(t, str) and t.strip() == ""):
            test["type"] = "Default"

def is_empty(v):
    return v is None or (isinstance(v, str) and v.strip() == "")


def delete_if_no_program_name(data, path):
    try:
        name = data["extracted_data"]["programVariants"][0]["programIdentity"].get("program_name")
    except Exception:
        name = None

    if is_empty(name):
        path.unlink(missing_ok=True)
        print(f"🗑 Deleted (missing program_name): {path.name}")
        return False
    return True


def fill_degree_defaults(data):
    try:
        pi = data["extracted_data"]["programVariants"][0]["programIdentity"]
    except Exception:
        return

    if is_empty(pi.get("degree_name")):
        pi["degree_name"] = "Default"

    if is_empty(pi.get("degree_type")):
        pi["degree_type"] = "Default"


def fill_general_requirements_titles(data):
    try:
        gr_list = data["extracted_data"]["programVariants"][0]["generalRequirements"]["generalRequirements"]
    except Exception:
        return

    if not isinstance(gr_list, list):
        return

    for item in gr_list:
        title = item.get("title")
        if is_empty(title) or (isinstance(title, str) and len(title) > 40):
            item["title"] = "Default"


def main():
    folder = Path("/home/ml-team/Desktop/BackupDisk/uniscrapupbackup/crawling-scrapping/test_utulsa")  # 👈 change to your folder

    for file in folder.glob("*.json"):
        try:
            process_file(file)
            print(f"✔ Processed: {file.name}")
        except Exception as e:
            print(f"✖ Failed: {file.name} — {e}")


if __name__ == "__main__":
    main()

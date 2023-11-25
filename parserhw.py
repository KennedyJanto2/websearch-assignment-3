from bs4 import BeautifulSoup
import pymongo
import requests
import re


mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["crawler_db"]
professors_collection = db["professors"]  # Collection to store professors' data

target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"

response = requests.get(target_url)

if response.status_code == 200:
    html_content = response.text

soup = BeautifulSoup(html_content, 'html.parser')

def extract_professor_data(soup):
    faculty_divs = soup.find_all('div', class_='clearfix')

    for faculty_div in faculty_divs:

        name = faculty_div.find('h2').get_text(strip=True) if faculty_div.find('h2') else 'N/A'

        # title tag could be Title or Title:
        title_regex = re.compile(r'Title\s*:?\s*')
        title_strong = faculty_div.find('strong', text=title_regex)
        title = title_strong.next_sibling.strip() if title_strong and title_strong.next_sibling else 'N/A'

        office_regex = re.compile(r'Office\s*:?\s*')
        office_strong = faculty_div.find('strong', text=office_regex)
        office = office_strong.next_sibling.strip() if office_strong and office_strong.next_sibling else 'N/A'

        phone_regex = re.compile(r'Phone\s*:?\s*')
        phone_strong = faculty_div.find('strong', text=phone_regex)
        phone = phone_strong.next_sibling.strip() if phone_strong and phone_strong.next_sibling else 'N/A'

        email_anchor = faculty_div.find('a', href=lambda href: 'mailto:' in href)
        email = email_anchor.get_text(strip=True) if email_anchor else 'N/A'

        web_anchor = faculty_div.find('a', href=lambda href: href and (href.startswith('http') or href.startswith('https')))
        web = web_anchor['href'] if web_anchor else 'N/A'

        yield {
            'name': name,
            'title': title,
            'office': office,
            'phone': phone,
            'email': email,
            'web': web
        }

for professor_data in extract_professor_data(soup):
    print("Data to insert:", professor_data)  # This should print the data to the console

    result = professors_collection.insert_one(professor_data)
    if not result.acknowledged:
        print("Data insertion failed for:", professor_data)



print("All faculty member data has been parsed and stored.")

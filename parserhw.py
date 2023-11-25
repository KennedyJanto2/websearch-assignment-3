from bs4 import BeautifulSoup
import pymongo

# Setup MongoDB connection
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["crawler_db"]
pages_collection = db["pages"]  # Collection where pages' data was stored
professors_collection = db["professors"]  # Collection to store professors' data

# Target page URL
target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"

# Fetch the page data from MongoDB
page_data = pages_collection.find_one({"url": target_url})
if not page_data:
    print(f"Page data for URL {target_url} not found in the database.")
    exit()

# Parse the HTML content
soup = BeautifulSoup(page_data['html'], 'html.parser')

# Define a function to extract professor data
def extract_professor_data(soup):
    # Find the container that includes all faculty members - adjust to actual HTML structure
    faculty_list = soup.find_all('div', class_='faculty-list')  # Replace with actual class or structure
    print(f"Found {len(faculty_list)} faculty list items")  # Debug print

    for faculty_member in faculty_list:
        # Add error handling for elements that may not exist
        name = faculty_member.find('h3').get_text(strip=True) if faculty_member.find('h3') else 'N/A'
        title = faculty_member.find('p', class_='title').get_text(strip=True) if faculty_member.find('p', class_='title') else 'N/A'
        office = faculty_member.find('p', class_='office').get_text(strip=True) if faculty_member.find('p', class_='office') else 'N/A'
        email_link = faculty_member.find('a', href=lambda h: 'mailto:' in h)
        email = email_link.get_text(strip=True) if email_link else 'N/A'
        website_link = faculty_member.find('a', href=lambda h: 'http://' in h or 'https://' in h)
        website = website_link['href'] if website_link else 'N/A'

        print(f"Extracted data - Name: {name}, Title: {title}, Office: {office}, Email: {email}, Website: {website}")  # Debug print

        yield {
            'name': name,
            'title': title,
            'office': office,
            'email': email,
            'website': website
        }


# Extract and store professor data
for professor_data in extract_professor_data(soup):
    professors_collection.insert_one(professor_data)
    print(f"Stored data for professor {professor_data['name']}")

print("All faculty member data has been parsed and stored.")

# ... (rest of the parser.py script)

# Extract and store professor data
for professor_data in extract_professor_data(soup):
    result = professors_collection.insert_one(professor_data)
    if result.acknowledged:
        print(f"Stored data for professor {professor_data['name']}")
    else:
        print(f"Failed to store data for professor {professor_data['name']}")

num_professors = professors_collection.count_documents({})
print(f"Number of faculty members stored: {num_professors}")

# ... (rest of the parser.py script)

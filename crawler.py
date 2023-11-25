from urllib.request import urlopen
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pymongo

# MongoDB setup
mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")
db = mongo_client["crawler_db"]
pages_collection = db["pages"]

# Define the base URL and the target URL
base_url = "https://www.cpp.edu/sci/computer-science/"
target_url = "https://www.cpp.edu/sci/computer-science/faculty-and-staff/permanent-faculty.shtml"

def retrieve_url(url):
    try:
        with urlopen(url) as response:
            return response.read()
    except Exception as e:
        print(f"An error occurred while fetching URL {url}: {e}")
        return None

def store_page(url, html):
    # Storing the page in MongoDB
    pages_collection.insert_one({"url": url, "html": html})

def is_target_page(url):
    return url == target_url

def parse(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a', href=True):
        absolute_url = urljoin(base_url, link['href'])
        yield absolute_url

def clear_frontier(frontier):
    # Clear the frontier (for the sake of this example, just empty the list)
    frontier.clear()

class Frontier:
    def __init__(self):
        self.visited = set()
        self.queue = [base_url]
    
    def add_url(self, url):
        if url not in self.visited:
            self.queue.append(url)
    
    def next_url(self):
        while self.queue:
            url = self.queue.pop(0)
            if url not in self.visited:
                return url
        return None

    def clear(self):
        self.queue = []

    def done(self):
        return len(self.queue) == 0

def crawler_thread(frontier):
    while not frontier.done():
        url = frontier.next_url()
        if url is None:
            break
        print(f"Crawling {url}")
        if is_target_page(url):
            print(f"Target page found at {url}")
            html = retrieve_url(url)
            if html:
                store_page(url, html)
            clear_frontier(frontier)
            break
        html = retrieve_url(url)
        if html:
            store_page(url, html)
            frontier.visited.add(url)
            for next_url in parse(html, base_url):
                frontier.add_url(next_url)

# Initialize the frontier and start the crawler thread
frontier = Frontier()
crawler_thread(frontier)

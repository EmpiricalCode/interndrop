from openai import OpenAI
from dotenv import load_dotenv
import os
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import json
from difflib import SequenceMatcher

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client
client = OpenAI()

def fetch(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        # Try networkidle for 10 seconds
        try:
            page.goto(url, wait_until="networkidle", timeout=10000)
            html = page.content()
        except:
            # If it times out, just continue with what's loaded
            print("Network idle timed out - continuing anyways")
            html = page.content()
            pass
         
        finally:
            browser.close()

    soup = BeautifulSoup(html, 'html.parser')

    # Remove script and style elements
    for element in soup(["script", "style"]):
        element.decompose()

    # Get text and clean it up
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    cleaned_text = '\n'.join(chunk for chunk in chunks if chunk)

    return cleaned_text

def parse(cleaned_text):

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the system prompt file
    file_path = os.path.join(script_dir, 'system_prompt.txt')

    # Read the system prompt from the file
    with open(file_path, 'r') as f:
        system_prompt = f.read()

    # Create a chat completion using the OpenAI API
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role" : "user",
                "content" : "CAREERS PAGE:\n" + cleaned_text
            }
        ],
        model="gpt-4o-mini",
    )

    return json.loads(chat_completion.choices[0].message.content)

def calculate_similarity(text1, text2):
    """Calculate similarity ratio between two texts"""
    return SequenceMatcher(None, text1, text2).ratio()

def scrape_all_pages(base_url, max_pages=100):

    all_jobs = []
    i = 1
    previous_content = None

    while i <= max_pages:
        try:
            # Construct the URL for the current page
            if i == 1:
                paginated_url = base_url
            else:
                paginated_url = f"{base_url}&page={i}"
            print(f"Scraping page {i}: {paginated_url}")

            # Fetch the cleaned text content of the page
            cleaned_text = fetch(paginated_url)

            # If the fetched text is empty or indicates no results, stop.
            if not cleaned_text:
                print("No more content found. Stopping.")
                break

            # Check similarity with previous page
            if previous_content is not None:
                similarity = calculate_similarity(cleaned_text, previous_content)
                print(f"Similarity with previous page: {similarity:.2%}")
                if similarity > 0.98:
                    print("Content is more than 98% similar to previous page. Stopping.")
                    break

            # Parse the text to get a list of job objects
            jobs_on_page = parse(cleaned_text)

            # If parsing returns an empty list, it means no more jobs were found
            if not jobs_on_page:
                print(f"Page {i} returned no jobs. Stopping.")
                break

            # Add the found jobs to the aggregate list
            all_jobs.extend(jobs_on_page)
            
            # Store current content for next iteration
            previous_content = cleaned_text
            i += 1

        except Exception as e:
            # If any error occurs (e.g., network error, page not found), stop.
            print(f"An error occurred on page {i}: {e}. Stopping.")
            break

    return all_jobs

# Test scrape all pages
all_results = scrape_all_pages("https://robinhood.com/us/en/careers/early-talent/")
print(json.dumps(all_results, indent=2))
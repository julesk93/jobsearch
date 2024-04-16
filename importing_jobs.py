
#!/Users/juliankilchling/code/julesk93/jobsearch/.venv/bin/python

import requests
from bs4 import BeautifulSoup
import re
import config

url = input("Please enter a URL: ")

# Perform any operations with the URL here
# For example, you can make a request to the URL using requests library
try:
    response = requests.get(url)
    # Check if the request was successful
    if response.status_code == 200:
        print("Request successful!")
    else:
        print(f"Request failed with status code: {response.status_code}")
except requests.RequestException as e:
    print("Error making request:", e)

# Parse the HTML content of the webpage
soup = BeautifulSoup(response.text, 'html.parser')

def clean_filename():
    # Extract titles
    title = soup.title.text if soup.title else "No title found"
    title.strip()
    cleaned_title = re.sub(r'[^\w\s]', '', title.strip())
    cleaned_title = cleaned_title.replace('GoodJobs', '').strip()
    return cleaned_title

# Function to get lists nested under different sections, e.g. Profile, Tasks, etc.
def get_lists(section):
    list = soup.find('section', id=section).find('div', class_='text-style-body text-responsive-xs checkmark-list').find_all('li')
    return list

def extract_ansprechpartnerin():
    # Find the <div> element with class "col-span-full lg:col-span-8 lg:row-start-3 border-r-2"
    div_element = soup.find('div', class_='col-span-full lg:col-span-8 lg:row-start-3 border-r-2')

    # If the <div> element is found, find the <h2> element within it
    if div_element:
        h2_element = div_element.find('h2', class_='text-style-headline text-responsive-l')
        # If the <h2> element is found, print its text
        if h2_element:
            return h2_element.get_text().replace('\n', '').replace('            ',' ').strip()
    return None

# extract job criteria e.g. Starting Date, Location, etc.
def extract_job_criteria(keyword):
    # Find the <strong> tag containing the keyword
    strong_tag = soup.find('strong', string=keyword)
    # Extract the text from the next sibling and remove ": " prefix
    if strong_tag:
        next_sibling = strong_tag.find_next_sibling(string=True)
        if next_sibling:
            text = next_sibling.strip().split(': ')[1]  # Remove ": " prefix
            return text
    # Return None if keyword not found or text extraction fails
    return None

def extract_description(section_title):
    intro_section = soup.find('section', id=section_title)
    # If the section is found, extract all text within it
    if intro_section:
        nested_div = intro_section.find('div', class_='text-style-body text-responsive-xs checkmark-list')
        if nested_div:
            paragraphs = nested_div.find_all('p')
            # Extract text from each <p> element
            paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
            # Remove empty strings
            cleaned_data = [item for item in paragraph_texts if item != '']
            return cleaned_data
        else:
            return []
    else:
        return []
    
def extract_company():
    # Find the section with the id "company"
    company_section = soup.find('section', id='company')
    # Find the first h2 within the company section
    if company_section:
        first_h2 = company_section.find('h2')
        if first_h2:
            return first_h2.text
    return None

def extract_split(search_term):
    # Find the <p> tag containing the search string
    p_tag = soup.find('p', string=lambda text: text and search_term in text)

    # If the <p> tag is found, return its text content
    if p_tag:
        p_text = p_tag.get_text()
        parts = p_text.split(search_term)
        # Extract the date part
        date = parts[-1].strip()
        return date
    
    return None

def transform_date(date_string):
    # Split the date string based on the "." separator
    parts = date_string.split('.')
    # Rearrange the parts and concatenate them with the desired format
    transformed_date = "[[" + '-'.join(parts[::-1]) + "]]"
    return transformed_date

#Set output filename

output_filename = f"{config.logseq_path}joboffers_{clean_filename()}.md"

# Assign variables

jobtyp = extract_job_criteria("Job-Typ")
starting_date = extract_split("Arbeitsbeginn: ")
company = extract_company()
deadline = transform_date(extract_split("Job online bis"))
ansprechpartnerin = extract_ansprechpartnerin()
berufserfahrung = extract_split("Berufserfahrung: ")

# Multiline string to write to markdown file

tags = f"""\
type:: stellenausschreibung
institution:: {company}
Teilzeit:: {jobtyp}
status:: offen
starting_date:: {starting_date}
kommentar:: offen
deadline:: {deadline}
ansprechpartner:: {ansprechpartnerin}
website:: [Stellenausschreibung]({url})
berufserfahrung:: {berufserfahrung}
kennziffer:: offen
email:: offen

"""

job_description_list = extract_description("intro")
profile_list = get_lists("anforderungen")
task_list = get_lists("aufgaben")
benefits_list = get_lists("benefits")
bewerbungsprozess_list = extract_description("bewerbungsprozess")

# Write to markdown file
with open(output_filename, 'w', encoding='utf-8') as markdown_file:
    # Write tags to markdown
    markdown_file.write(tags)
    # Write Profil / Requirements to markdown
    markdown_file.write(f"- ## Jobbeschreibung\n")
    for item in job_description_list:
        markdown_file.write(f"\t- {item}\n")
    markdown_file.write("\n")
    markdown_file.write(f"- ## Profil\n")
    for item in profile_list:
        markdown_file.write(f"\t- {item.text.strip()}\n")
    # Write Tasks / Aufgaben to markdown
    markdown_file.write(f"- ## Aufgaben\n")
    for item in task_list:
        markdown_file.write(f"\t- {item.text.strip()}\n")
    # Write Benefits to markdown
    markdown_file.write(f"- ## Benefits\n")
    for item in task_list:
        markdown_file.write(f"\t- {item.text.strip()}\n")
    markdown_file.write(f"- ## Bewerbungsprozess\n")
    for item in bewerbungsprozess_list:
        markdown_file.write(f"\t- {item}\n")


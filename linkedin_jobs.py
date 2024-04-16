import tkinter as tk
import sys
from tkinter import filedialog
from bs4 import BeautifulSoup
import re
import config

# Get the file path from the first command-line argument
html_file_path = sys.argv[1]

# Read the HTML content from the file
with open(html_file_path, "r", encoding="utf-8") as file:
    html_content = file.read()

# Parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

# Now you can use 'soup' to process the HTML content further
print("HTML file parsed successfully.")

#create dictionary to store results of webscrape
linkedin_dict = {}

# Get Job Title => WORKS
linkedin_dict["title"] = soup.find('h1', class_='t-24 t-bold job-details-jobs-unified-top-card__job-title').text.strip()

# Get company name
job_details_div = soup.find('div', {'class':'job-details-jobs-unified-top-card__primary-description-without-tagline mb2'})
linkedin_dict['company'] = job_details_div.find('a').text.strip()

# Get publication date
linkedin_dict['pub_date'] = job_details_div.find(lambda tag: tag.name == 'span' and 'Vor' in tag.get_text()).text.strip()

job_details_2 = soup.find('li', {'class':'job-details-jobs-unified-top-card__job-insight job-details-jobs-unified-top-card__job-insight--highlight'})

#find out the job type (full-time, part-time, etc.)
try:
    linkedin_dict["jobtyp"] = job_details_2.find_all('span', {'class':'job-details-jobs-unified-top-card__job-insight-view-model-secondary'})[0].find('span', {'aria-hidden':'true'}).text.strip()
except AttributeError:
    linkedin_dict["jobtyp"] = ""

# Get skills from LinkedIn Job Posting
qualifications_div = soup.find('div', id='how-you-match-card-container')
qualifications = qualifications_div.find_all('h3', {'class':'t-14 t-bold'})

for qual in qualifications:
    key_qual = qual.find_next_sibling("a").text.replace(" und",",").replace("\n","").strip()
    qual_stripped = qual.text.replace("Kenntnisse fehlen auf Ihrem Profil","Fehlende Kenntnisse").replace("Kenntnisse auf Ihrem Profil","Bestehende Kenntnisse").strip()[2:].lstrip()
    linkedin_dict[qual_stripped] = key_qual
print(linkedin_dict)

# Get job description section
# Find the article element with the specified class
job_description = soup.find('article', class_='jobs-description__container jobs-description__container--condensed')

#WORKS
#Define text replacements for section titles

# Define replacements
replacements = {
    "Profil": "Profil",
    "PROFIL": "Profil",
    "Qualifications": "Profil",
    "WIR LIEBEN": "Profil",
    "Das bringst du mit": "Profil",
    "AUFGABEN": "Aufgaben",
    "Aufgaben": "Aufgaben",
    "Responsibilities": "Aufgaben",
    "Das erwartet dich bei uns": "Aufgaben",
    "Deine Aufgaben": "Aufgaben",
    "Deine Aufgaben": "Aufgaben",
    "DU LIEBST": "Aufgaben",
    "BENEFITS": "Benefits",
    "Perks": "Benefits",
    "Das bieten wir dir": "Benefits",
    "Benefits": "Benefits"
}

# Find all <ul> elements within the job description
uls = job_description.find_all('ul')

# Extract list items from each <ul> and put them into separate lists
list_of_lists = []
for ul in uls:
    list_entries = [li.get_text(strip=True) for li in ul.find_all('li')]
    # Remove newline characters from list entries
    list_entries = [entry.replace('\n', '') for entry in list_entries]
    # Get section heading to assign lists to the right section => use if statements for different html structures
    if ul.parent.find_previous_sibling().text.strip() != '':
        parent = ul.parent.find_previous_sibling().text.strip()
        keyword = uls[0].parent.find_previous_sibling().text.strip()
    elif ul.parent.find_previous_sibling().find_previous_sibling().text.strip() != '':
        parent = ul.parent.find_previous_sibling().find_previous_sibling().text.strip()
        keyword = uls[0].parent.find_previous_sibling().find_previous_sibling().text.strip()
    else:
        parent = ul.parent.find_previous_sibling().find_previous_sibling().find_previous_sibling().text.strip()
        keyword = uls[0].parent.find_previous_sibling().find_previous_sibling().find_previous_sibling().text.strip()
    # Perform multiple replacements
    for key, value in replacements.items():
        if key in parent:
            # Replace the entire original string with the corresponding replacement value
            new_parent = value
            # Break the loop after the first replacement is done
            break
    else:
        # If none of the keys are found in the original string, keep the original string unchanged
        new_parent = parent
    linkedin_dict[new_parent]= list_entries
    #list_of_lists.append(list_entries)

## Get job description => WORKS

# Get the parent element
parent_element = uls[0].parent.parent.text.replace('\n', '').strip()

if keyword == '':
    keyword = uls[0].text.strip()[:50]

linkedin_dict["job_description"] = parent_element.split(keyword)[0]

def get_job_title_linkedin():
    # Get Job Title => WORKS
    title = soup.find('h1', class_='t-24 t-bold job-details-jobs-unified-top-card__job-title').text.strip()
    linkedin_dict["title"] = title
    return title

# Get JobID of LinkedIn Job

all_a_elements = soup.find_all("a", {"target": "_self"})
skill_match_elements = [element for element in all_a_elements if "skill-match" in element.get("href", "")]

skill_match_elements

# Extract the 'href' attribute from the element
href = skill_match_elements[0].get("href", "")

# Define the pattern for the job ID using regular expression
pattern = r'jobId=(\d+)'

# Search for the pattern in the 'href' attribute
match = re.search(pattern, href)

# Extract the job ID as a string
linkedin_dict["job_id"] = match.group(1) if match else None
linkedin_dict["url"] = "https://www.linkedin.com/jobs/view/" + linkedin_dict["job_id"]


## Make sure all dict keys are set

# Check if the key exists in the dictionary
if "Benefits" not in linkedin_dict:
    linkedin_dict["Benefits"] = ["nicht gefunden"]
if "Bestehende Kenntnisse" not in linkedin_dict:
    linkedin_dict["Bestehende Kenntnisse"] = "Keine"

## Tags section

tags = f"""\
type:: stellenausschreibung
institution:: {linkedin_dict["company"]}
Teilzeit:: {linkedin_dict["jobtyp"]}
status:: offen
starting_date:: offen
kommentar:: offen
deadline:: offen
ansprechpartner:: offen
website:: [Stellenausschreibung]({linkedin_dict["url"]})
berufserfahrung:: offen
kennziffer:: offen
publication:: {linkedin_dict["pub_date"]}
matching_skills:: {linkedin_dict["Bestehende Kenntnisse"]}
missing_skills:: {linkedin_dict["Fehlende Kenntnisse"]}

"""

## Assign Filename from Company and get folder path from config.py
cleaned_title = re.sub(r'[^\w\s]', '', get_job_title_linkedin())
output_filename = f"{config.logseq_path}joboffers_{cleaned_title}.md"

with open(output_filename, 'w', encoding='utf-8') as markdown_file:
    # Write tags to markdown
    markdown_file.write(tags)
    # Write Profil / Requirements to markdown
    markdown_file.write(f"- ## Jobbeschreibung\n")
    markdown_file.write(f"\t- {linkedin_dict["job_description"]}\n")
    markdown_file.write(f"- ## Profil\n")
    for item in linkedin_dict["Profil"]:
        markdown_file.write(f"\t- {item}\n")
    # Write Tasks / Aufgaben to markdown
    markdown_file.write(f"- ## Aufgaben\n")
    for item in linkedin_dict["Aufgaben"]:
        markdown_file.write(f"\t- {item}\n")
    # Write Benefits to markdown
    markdown_file.write(f"- ## Benefits\n")
    for item in linkedin_dict["Benefits"]:
        markdown_file.write(f"\t- {item}\n")
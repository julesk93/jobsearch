import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from selenium import webdriver
import tkinter as tk

def get_url():
    url = entry.get()
    print("URL entered:", url)
    root.url = url  # Store the URL in the root window object
    root.destroy()  # Close the window after getting the URL

# Function to process the URL
def process_url():
    url = root.url  # Get the URL from the root window object
    print("Processing URL:", url)
    # Your code to process the URL goes here

# Create the main window
root = tk.Tk()
root.title("URL Input")

# Create a label
label = tk.Label(root, text="Enter URL:")
label.pack()

# Create an entry widget
entry = tk.Entry(root, width=40)
entry.pack()

# Create a button to get the URL
button = tk.Button(root, text="Get URL", command=get_url)
button.pack()

# Run the main loop
root.mainloop()

# Process the URL after the window is closed
process_url()

url = root.url

# # url = input("Please enter a URL: ")

# Get html via Selenium
driver = webdriver.Chrome()

# Load the page
driver.get(url)

# Retrieve the fully rendered HTML
html_content = driver.page_source

# Close the webdriver
driver.quit()

# use BeautifulSoup to parse the HTML content
soup = BeautifulSoup(html_content, 'html.parser')

#create dict and dict entries
job_posting = {}

job_posting["title"] = ""
job_posting["kennziffer"] = ""
job_posting["Aufgaben"] = []
job_posting["Aufgaben_Beschreibung"] = []
job_posting["Profil"] = []
job_posting["Profil_Beschreibung"] = []
job_posting["Benefits"] = []
job_posting["Benefits_Beschreibung"] = []
job_posting["Jobbeschreibung"] = []
job_posting["Aufgaben_Beschreibung_Teil2"] = []
job_posting["Profil_Beschreibung_Teil2"] = []
job_posting["Benefits_Beschreibung_Teil2"] = []
job_posting["Ansprechpartnerin"] = ""
job_posting["Arbeitsbeginn"] = ""
job_posting["Company"] = ""
job_posting["deadline"] = ""
job_posting["Berufserfahrung"] = ""
job_posting["Bewerbungsprozess"] = ""

# function to reverse list
def reverse_list(input_list):
    input_list.reverse()
    input_list = [item for item in input_list if item != '']
    return input_list

if "goodjobs" in url:

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
    # Function to get lists nested under different sections, e.g. Profile, Tasks, etc.
    def get_lists(section):
        list = soup.find('section', id=section).find('div', class_='text-style-body text-responsive-xs checkmark-list').find_all('li')
        list_entries = [li.get_text(strip=True) for li in list]
        return list_entries
    def get_additional_description_from_(section):
        target = soup.find('section', id=section).find('div', class_='text-style-body text-responsive-xs checkmark-list').find('ul')
        # if target is not None:
        try:
            siblings = target.next_siblings
            liste_next = [sibling.text.strip().replace("\n","") for sibling in siblings] 
            liste_next = reverse_list(liste_next)
        except (AttributeError):
            liste_next = []
        return liste_next
    def transform_date(date_string):
        # Split the date string based on the "." separator
        parts = date_string.split('.')
        # Rearrange the parts and concatenate them with the desired format
        transformed_date = "[[" + '-'.join(parts[::-1]) + "]]"
        return transformed_date
    job_posting["Ansprechpartnerin"] = extract_ansprechpartnerin()
    job_posting["Arbeitsbeginn"] = extract_split("Arbeitsbeginn: ")
    job_posting["Company"] = extract_company()
    job_posting["deadline"] = transform_date(extract_split("Job online bis"))
    job_posting["Berufserfahrung"] = extract_split("Berufserfahrung: ")
    job_posting["Bewerbungsprozess"] = extract_description("bewerbungsprozess")
    job_posting["Jobbeschreibung"] = extract_description("intro")
    job_posting["Profil"] = get_lists("anforderungen")
    job_posting["Profil_Beschreibung_Teil2"] = get_additional_description_from_("anforderungen")
    job_posting["Aufgaben"] = get_lists("aufgaben")
    job_posting["Aufgaben_Beschreibung_Teil2"] = get_additional_description_from_("aufgaben")
    job_posting["Benefits"] = get_lists("benefits")
    job_posting["Benefits_Beschreibung_Teil2"] = get_additional_description_from_("benefits")

# for all other websites
else: 
    # Get all list elements
    uls = soup.find_all('ul')

    # Define a function to filter out <ul> elements with specific classes using regex
    def filter_ul(element):
        classes = element.get('class', [])
        # Compile regex pattern to match partial class names
        pattern = re.compile(r'navigation-tree|menu|linklist|nav')
        # Check if any of the specified classes match partially with the element's classes
        return element.name == 'ul' and not any(pattern.search(cls) for cls in classes)

    # Find all <ul> elements that meet the filtering criteria
    uls = soup.find_all(filter_ul)

    #Define text replacements for section titles

    # Define replacements
    replacements = {
        "Profil": "Profil",
        "PROFIL": "Profil",
        "Qualifications": "Profil",
        "WIR LIEBEN": "Profil",
        "Das bringst du mit": "Profil",
        "Sie bringen mit": "Profil",
        "AUFGABEN": "Aufgaben",
        "Aufgaben": "Aufgaben",
        "Responsibilities": "Aufgaben",
        "Arbeitsgebiet umfasst": "Aufgaben",
        "Das erwartet dich bei uns": "Aufgaben",
        "Deine Aufgaben": "Aufgaben",
        "Deine Aufgaben": "Aufgaben",
        "DU LIEBST": "Aufgaben",
        "BENEFITS": "Benefits",
        "Perks": "Benefits",
        "Das bieten wir dir": "Benefits",
        "Wir bieten": "Benefits",
        "Benefits": "Benefits"
    }


    # Function to get section headline and content from target item

    def get_section_from_sibling(target):
        heading_regex = re.compile(r'h[1-6]')
        new_liste = []
        for sib in target.find_previous_siblings():
            new_liste.append(sib.text)
            if sib.name=="h2" or sib.name=="h3" or sib.name=="h2" or sib.name=="h1":
                break
        new_liste = [item for item in new_liste if item != '']
        new_liste.reverse()
        return new_liste

    # check list against replacements to select correct replacement

    def check_list_for_replacement(new_liste):
        combined_string = ' '.join(new_liste)
        for key, value in replacements.items():
            if key in combined_string:
                return value
        return None

    options = ["Aufgaben", "Aufgaben_Beschreibung","Profil","Profil_Beschreibung", "Benefits", "Benefits_Beschreibung", "Jobbeschreibung", "Firmenprofil"]
    for index, ul in enumerate(uls, start=1):
        list_entries = [li.get_text(strip=True) for li in ul.find_all('li')]
        # Remove newline characters from list entries
        list_entries = [entry.replace('\n', '') for entry in list_entries]
        prev_sib_parent = ul.parent.previous_sibling
        if prev_sib_parent is not None:
            prev_sib_grandparent = ul.parent.previous_sibling.previous_sibling
        else: prev_sib_grandparent = None
        if prev_sib_grandparent is not None:
            prev_sib_greatgrandparent = ul.parent.previous_sibling.previous_sibling.previous_sibling
        else: prev_sib_greatgrandparent = None
        if prev_sib_parent is not None and prev_sib_parent.text != '':
                parent = prev_sib_parent.text.strip()
                keyword = uls[0].parent.find_previous_sibling().text.strip()
                # Perform multiple replacements
                for key, value in replacements.items():
                    if key in parent:
                        # Replace the entire original string with the corresponding replacement value
                        parent = value
                        # Break the loop after the first replacement is done
                        break
            #  if parent not in options:
            #     parent = get_selected_option(ul.text.strip().replace('\n', ' '))
        elif prev_sib_grandparent is not None and prev_sib_grandparent.text != '':
            parent = prev_sib_grandparent.text.strip()
            keyword = uls[0].prev_sib_grandparent.text.strip()
            # Perform multiple replacements
            for key, value in replacements.items():
                if key in parent:
                    # Replace the entire original string with the corresponding replacement value
                    parent = value
                    # Break the loop after the first replacement is done
                    break
            # if parent not in options:
            #     parent = get_selected_option(ul.text.strip().replace('\n', ' '))
        elif prev_sib_greatgrandparent is not None and prev_sib_greatgrandparent.text != '':
            parent = prev_sib_greatgrandparent.text.strip()
            keyword = uls[0].prev_sib_greatgrandparent.text.strip()
            # Perform multiple replacements
            for key, value in replacements.items():
                if key in parent:
                    # Replace the entire original string with the corresponding replacement value
                    parent = value
                    # Break the loop after the first replacement is done
                    break
            # if parent not in options:
            #     parent = get_selected_option(ul.text.strip().replace('\n', ' '))
        # else:
        #     parent = get_selected_option(ul.text.strip())
        job_posting[parent]= list_entries
        if ul.previous_siblings is not None:
            siblings = ul.previous_siblings
            liste_previous = [sibling.text.strip().replace("\n","") for sibling in siblings] 
            if liste_previous is not None:
                liste_previous = reverse_list(liste_previous)
            if parent == "Aufgaben":
                if job_posting["Aufgaben_Beschreibung"] == []:
                    job_posting["Aufgaben_Beschreibung"] = liste_previous
            if parent == "Profil":
                if job_posting["Profil_Beschreibung"] == []:
                    job_posting["Profil_Beschreibung"] = liste_previous
            if parent == "Benefits":
                if job_posting["Benefits_Beschreibung"] == []:
                    job_posting["Benefits_Beschreibung"] = liste_previous
        if ul.next_siblings is not None:
            siblings = ul.next_siblings
            liste_next = [sibling.text.strip().replace("\n","") for sibling in siblings] 
            if liste_next is not None:
                liste_next = reverse_list(liste_next)
            if parent == "Aufgaben":
                if job_posting["Aufgaben_Beschreibung_Teil2"] == []:
                    job_posting["Aufgaben_Beschreibung_Teil2"] = liste_next
            if parent == "Profil":
                if job_posting["Profil_Beschreibung_Teil2"] == []:
                    job_posting["Profil_Beschreibung_Teil2"] = liste_next
            if parent == "Benefits":
                if job_posting["Benefits_Beschreibung_Teil2"] == []:
                    job_posting["Benefits_Beschreibung_Teil2"] = liste_next
    # Check if elements were found in the previous round. If not, it is assumed that section titles are actually html siblings
    if job_posting["Profil"] == []:
        for index, ul in enumerate(uls, start=1):
            list_entries = [li.get_text(strip=True) for li in ul.find_all('li')]
            # Remove newline characters from list entries
            list_entries = [entry.replace('\n', '') for entry in list_entries]  
            description = get_section_from_sibling(ul)
            check_list_for_replacement(description)
            job_posting[f"{check_list_for_replacement(description)}_Beschreibung"] = description
            job_posting[f"{check_list_for_replacement(description)}"] = list_entries
            
    # Get Kennzahl
    import re
    # Find all spans containing the text "Kennzahl"
    elements_with_keyword = soup.find_all(string=re.compile(r'Kennzahl|Kennziffer'))
    if elements_with_keyword != []:
        job_posting["kennziffer"] = elements_with_keyword[0]

# Get Job Title
job_posting["title"] = soup.find('h1').text.strip()

# Assign filename
def clean_filename():
    # Extract titles
    title = job_posting["title"] if job_posting["title"] != "" else "No title found"
    title.strip()
    cleaned_title = re.sub(r'[^\w\s]', '', title.strip())
    cleaned_title = cleaned_title.replace('GoodJobs', '').strip()
    return cleaned_title

output_filename = f"job_ad___{clean_filename()}.md"

### Write markdown

## Tags section

tags = f"""\
type:: stellenausschreibung
company:: {job_posting["Company"]}
Teilzeit:: offen
status:: offen
starting_date:: offen
kommentar:: offen
deadline:: {job_posting["deadline"]}
ansprechpartner:: {job_posting["Ansprechpartnerin"]}
website:: [Stellenausschreibung]({url})
berufserfahrung:: {job_posting["Berufserfahrung"]}
kennziffer:: {job_posting["kennziffer"]}
publication:: offen

"""

### create markdown section for Logseq todos

### Create function to get future date starting from today and return it in the right format for Logseq's task management
### if future date falls on a weekend, assign task to Monday instead => ONLY assign tasks on weekdays

from datetime import datetime, timedelta

def get_date_logseq_format(days_from_today):
    # Get today's date
    today = datetime.now()
    
    # Calculate the date after delta_days
    future_date = today + timedelta(days=days_from_today)

    # Check if the future date falls on a weekend (Saturday or Sunday)
    if future_date.weekday() >= 5:  # Saturday or Sunday
        # Calculate the number of days to add to reach Monday
        days_to_add = 7 - future_date.weekday()
        future_date += timedelta(days=days_to_add)
    
    # Get the day name and format it
    day_name = future_date.strftime('%a')
    
    # Format the date
    formatted_date = future_date.strftime('%Y-%m-%d')
    
    # Combine the formatted date and day name
    formatted_result = f'<{formatted_date} {day_name}>'
    
    return formatted_result

# Write To Do Section in markdown file

todos = f"""\
	- TODO ergänze relevante Informationen für Stellenausschreibung "{job_posting["title"]}" bei {job_posting["Company"]}
	  SCHEDULED: {get_date_logseq_format(0)}
		- insb. zu Bewerbungsprozess und Unterlagen
	- TODO mache stichpunktartige Notizen zu Details in Stellenausschreibung "{job_posting["title"]}" bei {job_posting["Company"]}
	  SCHEDULED: {get_date_logseq_format(0)}
	- TODO setze Anschreiben auf für "{job_posting["title"]}" bei {job_posting["Company"]}
	  SCHEDULED: {get_date_logseq_format(1)}
	- TODO passe Lebenslauf an für "{job_posting["title"]}" bei {job_posting["Company"]}
	  SCHEDULED: {get_date_logseq_format(1)}
	- TODO stelle Anschreiben fertig für "{job_posting["title"]}" bei {job_posting["Company"]}
	  SCHEDULED: {get_date_logseq_format(2)}
	- TODO schicke Bewerbung ab für "{job_posting["title"]}" bei {job_posting["Company"]}
	  SCHEDULED: {get_date_logseq_format(2)}
"""

### Quality check
#replace None values in dict with empty lists
def check_for_none(dict):
    for key, value in dict.items():
        if value is None:
            dict[key] = []
check_for_none(job_posting)


## Write everything to markdown file

with open(output_filename, 'w', encoding='utf-8') as markdown_file:
    # Write tags to markdown
    markdown_file.write(tags)
    # Add to do section
    markdown_file.write(f"- ## To Dos\n")
    markdown_file.write("  {{renderer :todomaster}}")
    markdown_file.write(f"\n")
    markdown_file.write(todos)
    # Write Tasks / Aufgaben to markdown
    markdown_file.write(f"- ## Aufgaben\n")
    for item in job_posting["Aufgaben_Beschreibung"]:
        markdown_file.write(f"\t- {item}\n")
    for item in job_posting["Aufgaben"]:
        markdown_file.write(f"\t- {item}\n")
    for item in job_posting["Aufgaben_Beschreibung_Teil2"]:
        markdown_file.write(f"\t- {item}\n")
    # Write Profil / Requirements to markdown
    markdown_file.write(f"- ## Jobbeschreibung\n")
    for item in job_posting["Profil_Beschreibung"]:
        markdown_file.write(f"\t- {item}\n")
    for item in job_posting["Profil"]:
        markdown_file.write(f"\t- {item}\n")
    for item in job_posting["Profil_Beschreibung_Teil2"]:
        markdown_file.write(f"\t- {item}\n")
    # Write Benefits to markdown
    markdown_file.write(f"- ## Benefits\n")
    for item in job_posting["Benefits_Beschreibung"]:
        markdown_file.write(f"\t- {item}\n")
    for item in job_posting["Benefits"]:
        markdown_file.write(f"\t- {item}\n")
    for item in job_posting["Benefits_Beschreibung_Teil2"]:
        markdown_file.write(f"\t- {item}\n")
    markdown_file.write(f"- ## Bewerbungsprozess\n")
    for item in job_posting["Bewerbungsprozess"]:
        markdown_file.write(f"\t- {item}\n")
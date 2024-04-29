import sys
from openai import OpenAI
import os
import config
import re
import requests

### define functions

# function to call Logseq API => see https://plugins-doc.logseq.com/ for info
def logseq_api(api_method='logseq.Editor.getCurrentPage'):

    url = 'http://127.0.0.1:12315/api'
    headers = {
        'Authorization': 'Bearer FQzAUFKgeLrM3P',
        'Content-Type': 'application/json'
    }
    data = {
        'method': api_method,
    }

    response = requests.post(url, headers=headers, json=data)
    response_data = response.json()
    return response_data

def get_properties(logseq_page, property='ansprechpartner'):
    try: 
        property_returned = logseq_page['properties'][property]
    except KeyError:
        property_returned = ""
    return property_returned

#get filename of current logseq file
def get_logseq_page_file():
    response_data = logseq_api(api_method='logseq.Editor.getCurrentPage')
    name = response_data['originalName']
    logseq_pages_path = config.logseq_path
    file_name =  logseq_pages_path + name.replace("/","___") + ".md"
    return file_name

### Functions to read from and write to markdown file selected by quick action
def read_markdown(file_path):
    with open(file_path, 'r') as file:
        markdown_content = file.read()
    return markdown_content

def write_to_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

# function to extract the job ad plus comments
def extract_text_job_ad(markdown_content):
    # Find the start and end indexes of the 'Stellenausschreibung' section
    start_index = markdown_content.find("- # Stellenausschreibung")
    if start_index == -1:
        return ""  # If 'Stellenausschreibung' section is not found, return empty string
    
    # Find the end index of the 'Stellenausschreibung' section
    end_index = markdown_content.find("- ## Bewerbungsprozess", start_index)
    if end_index == -1:
        end_index = len(markdown_content)  # If 'Bewerbungsprozess' section is not found, extract until the end of the text
    
    # Extract the text between start and end indexes
    extracted_text = markdown_content[start_index:end_index]
    return extracted_text

# function to check whether cover letter was already parsed to Logseq
def check_for_cover_letter():
    responses = logseq_api(api_method='logseq.Editor.getCurrentPageBlocksTree')
    cv_check = False
    for response in responses:
        section = response['content']
        if section == "## Bewerbungsprozess":
            children = response["children"]
            for child in children:
                if "### Anschreiben (Entwurf)" in child["content"]:
                    cv_check = True
                    break
    return cv_check

# function to get the link to the resume file for that job ad and then extract it as a string
def get_resume(markdown_content):
    # Define regular expression pattern to find the text within the parentheses
    pattern = r"\[([Resume.txt]*)\]\((.*?)\)"
    # Search for the pattern in the markdown content
    match = re.search(pattern, markdown_content)

    # If match is found, extract the text within the parentheses
    if match:
        resume = match
        resume_link = match[2]
        resume_link = config.logseg_path_root + resume_link[3:]
    with open(resume_link, 'r') as file:
        resume = file.read()
    return resume


def get_chatgpt_resume(job_ad_annotated,resume,prompt="Test"):
  #open_api_key = os.environ.get('OPENAI_API_KEY')
  client = OpenAI()

  response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
      {"role": "user","content": prompt},
      {"role": "assistant","content": "Verstanden, ich warte auf deine Nachrichten."},
      {"role": "user","content": job_ad_annotated},
      {"role": "user","content": resume},
      {"role": "user","content": "ALLE TEILE GESENDET"}
    ],
    temperature=1,
    max_tokens=1173,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
  )
  gpt_cover_letter = response.choices[0].message.content
  return gpt_cover_letter

def append_to_markdown(file_path, new_content):
    marker = "- ### Anschreiben (Entwurf)"
    with open(file_path, 'a') as f:
        f.write(f"\n\t{marker}\n\t\t- {new_content}")

def main():

    ### get markdown content of currently selected logseq page
    current_logseq_page = get_logseq_page_file()
    markdown_content = read_markdown(current_logseq_page)

    # get job properties for chatgpt request
    logseq_page = logseq_api(api_method='logseq.Editor.getCurrentPage')
    properties=["language","ansprechpartner","company","stellenbezeichnung"]

    property_values = {}
    for property in properties:
        property_values[property] = get_properties(logseq_page,property)

    job_ad_annotated = extract_text_job_ad(markdown_content)

    resume = get_resume(markdown_content)

    header_section_de = f"""
    - # Zentrale Informationen:
    \t- Stellenbezeichnung: {property_values["stellenbezeichnung"]}
    \t- Ansprechpartner: {property_values["ansprechpartner"]}
    \t- Unternehmen: {property_values["company"]}

    """
    job_ad_annotated = header_section_de + job_ad_annotated

    cv_prompt_de = """
    Verfasse ein überzeugendes, maximal einseitiges Anschreiben und verwende dafür die folgenden Informationen: 
    das kommentierte Stellenangebot (Kommentare sind in *kursiv* gedruckt) und meinen Lebenslauf.
    Das Stellenangebot ist in Markdown formatiert und meine eigenen Kommentare sind in kursiv gedruckt. 
    Stelle dabei heraus, welche Kenntnisse, Eigenschaften und Fähigkeiten mich besonders geeignet für die Stelle machen.  
    Zunächst werde ich alle notwendigen Informationen in mehreren Messages schicken. 
    Wenn ich fertig bin, schreibe ich 'ALLE TEILE GESENDET'. Antworte erst, wenn du alle Teile erhalten hast.
    """
    
    if check_for_cover_letter() == False:
        # Send request to chatgpt
        gpt_cover_letter = get_chatgpt_resume(job_ad_annotated,resume,prompt=cv_prompt_de)
        print("Asking chatgpt for advice.")
        # modify markdown to have the corrent tabs to later append to logseq markdown
        modified_gpt_cover_letter = gpt_cover_letter.replace('\n', '\n\t\t  ')

        append_to_markdown(current_logseq_page, modified_gpt_cover_letter)

if __name__ == "__main__":
    main()

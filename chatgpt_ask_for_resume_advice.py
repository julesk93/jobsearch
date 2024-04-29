import sys
from openai import OpenAI
import os
import config
import re
import requests


def read_markdown(file_path):
    with open(file_path, 'r') as file:
        markdown_content = file.read()
    return markdown_content

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

def append_to_markdown(file_path, new_content, header = "Anpassungen Lebenslauf"):
    marker = f"- ### {header}"
    with open(file_path, 'a') as f:
        f.write(f"\n\t{marker}\n\t\t- {new_content}")

#get filename of current logseq file
def get_logseq_page_file():
    response_data = logseq_api(api_method='logseq.Editor.getCurrentPage')
    name = response_data['originalName']
    logseq_pages_path = config.logseq_path
    file_name =  logseq_pages_path + name.replace("/","___") + ".md"
    return file_name

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

resume = read_markdown(f"{config.standard_files_folrder}resume_de.txt")

current_logseq_page = get_logseq_page_file()
markdown_content = read_markdown(current_logseq_page)
job_ad = extract_text_job_ad(markdown_content)

client = OpenAI()

response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {
      "role": "user",
      "content": "Ich möchte eine erfolgreiche Bewerbung auf eine Stellenausschreibung abschicken. Hilf mir dabei, meinen Lebenslauf für die Stelle anzupassen. Gleich sende ich dir zwei Nachrichten: meinen Lebenslauf in Nachricht 1 und die Stellenausschreibung in Nachricht 2. Gebe mir Tipps, was ich an meinem Lebenslauf verändern könnte, um ihn besser an das Stellenprofil anzupassen, beispielsweise welche Tätigkeiten ich besonders hervorheben sollte. Gib mir eine Einschätzung, wie gut mein Lebenslauf zum Stellenprofil passt und nenne mir konkrete Verbesserungsvorschläge. Beginne erst mit deiner Antwort, wenn ich FERTIG geschrieben habe."
    },
    {
      "role": "assistant",
      "content": "Natürlich, ich freue mich darauf, dir bei der Anpassung deines Lebenslaufs zu helfen, um deine Chancen auf die Stelle zu erhöhen. Bitte sende mir zuerst deinen aktuellen Lebenslauf in Nachricht 1. Sobald du das erledigt hast, schaue ich mir die Stellenausschreibung in Nachricht 2 an und gebe dir entsprechende Tipps."
    },
    {
      "role": "user",
      "content": resume
    },
    {
      "role": "user",
      "content": "- # Stellenausschreibung\n\t- ## Jobbeschreibung\n\t\t- Als Data Engineering Team der Regionalmedien entwickeln und betrieben wir eine Datenplattform der nächsten Generation als Basis für Analysen, Dashboards, KI und Features in unserer Produktplattform. Zur Verstärkung unseres Teams in Berlin oder Hamburg suchen wir Dich als Data Engineer (m/w/d)\n\t- ## Profil\n\t\t- Du hast Erfahrung mit unserem Tech-Stack (Apache Beam, dbt, Apache Airflow, BigQuery) oder in vergleichbaren Technologien.\n\t\t- Die Cloud ist Dein zweites Zuhause: GCP, Pub/Sub, Cloud Run, Cloud SQL und Terraform sind keine Fremdwörter für Dich\n\t\t- Du schaust über den Data Engineering Tellerrand und kennst auch Algorithmen und Datenstrukturen aus dem Software Engineering\n\t\t- Auf Dich kann man sich verlassen, Du übernimmst gerne Verantwortung und Ownership ist für Dich nicht nur eine Floskel\n\t\t- Du bist offen, kommunikativ und teamfähig, fokussierst Dich auf Deine Ziele und hast ein hohes Maß an Eigenantrieb\n\t\t- Du verfügst über sehr gute Deutsch- und Englischkenntnisse\n\t- ## Aufgaben\n\t\t- Architecture: Sowohl auf System- als auch auf Komponentenebene hast Du stets das große Ganze im Blick\n\t\t- Development: Du entwickelst und optimierst Data Pipelines und Transformationen – in SQL und Python\n\t\t- Ownership: Wir übernehmen end-to-end Verantwortung für unsere Projekte – we build it we run it!\n\t\t- Passion: Du hast das Daten-Gen und bist gleichzeitig Techniker im Herzen\n\t\t- Plan: Du hast keine Angst vor Komplexität und zerlegst große Herausforderungen mit links in beherrschbare Einzelteile\n\t- ## Benefits\n\t\t- Innovation trifft Tradition: Du gestaltest die digitale Transformation unserer Mediengruppe mit\n\t\t- Top ausgestattet: Ob in Berlin oder Hamburg - In unseren zentral gelegenen Locations erwartet Dich ein moderner und voll ausgestatteter Arbeitsplatz\n\t\t- Entwickle Dich mit uns: Wir ermöglichen Dir die Teilnahme an individuellen Coachings, Workshops oder (Online)-Trainings im Rahmen unserer FUNKE Akademie\n\t\t- Flexibel arbeiten: Wir leben ein hybrides Arbeitsmodell, weil uns Deine Work-Life-Balance wichtig ist\n\t\t- Teamwork: Dich erwarten ein dynamisches Team, eine offene Feedbackkultur, kurze Kommunikationswege und ein herzliches Miteinander\n\t\t- Corporate Benefits: Wir bieten Dir ein Benefit-Portal mit attraktiven Rabatten und Abos\n\t\t- Halte Dich fit und gesund: Profitiere von unseren Kooperationen mit verschiedensten Fitnessstudios und lasse Dich für Deine mentale und körperliche Gesundheit individuell beraten"
    },
    {
      "role": "user",
      "content": "FERTIG"
    }
  ],
  temperature=1,
  max_tokens=1664,
  top_p=1,
  frequency_penalty=0,
  presence_penalty=0
)

resume_advice = response.choices[0].message.content

append_to_markdown(current_logseq_page, resume_advice, header = "Anpassungen Lebenslauf")
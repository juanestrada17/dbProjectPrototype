import requests
from bs4 import BeautifulSoup


def scrape_jobs():
    URL = "https://realpython.github.io/fake-jobs/"
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="ResultsContainer")

    # Finds results that include python
    results = results.find_all(
        "h2", string=lambda text: "python" in text.lower()
    )

    # Grabs the parent to access extra useful info in a comprehension
    python_job_elements = [
        h2_element.parent.parent.parent for h2_element in results
    ]

    # list of jobs, this is going to be an array of objects(dictionaries)
    python_jobs = []

    for job_element in python_job_elements:
        title_element = job_element.find("h2", class_="title")
        company_element = job_element.find("h3", class_="company")
        location_element = job_element.find("p", class_="location")
        python_jobs.append({'title': title_element.text.strip(),
                            'company': company_element.text.strip(),
                            'location': location_element.text.strip()
                            })

    # At this point python jobs is an array of dicts, mongo auto supports transformation from dict to json :)
    return python_jobs

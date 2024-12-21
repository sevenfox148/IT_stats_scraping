from scraping.chromedriver import valid_URL, get_cookies
import data.db_interactions as db
from scraping.scrape_dou import scrape_dou_page
from scraping.scrape_djinni import scrape_djinni_page
from etl.main_etl import run
import pandas as pd

schema = 'warehouse'

def menu_input():
    while True:
        try:
            value = int(input("Add more? (0/1): "))
            if value not in [0, 1]:
                print("ERROR: Value should be 0 or 1")
                continue
            return value
        except ValueError:
            print("ERROR: Value is not int")


def get_new_technology_input():
    technology = input("New technology: ")
    DOU_URL = input("DOU URL: ")
    Djinni_URL = input("Djinni URL: ")
    return technology, DOU_URL or None, Djinni_URL or None


def validate_technology(technology, old_technologies, new_technologies):
    if technology in old_technologies['technology'].values or technology in new_technologies['technology'].values:
        print(f"{technology} already in database!")
        return False
    return True


def validate_URLs(DOU_URL, Djinni_URL):
    if not DOU_URL and not Djinni_URL:
        print("ERROR: Technology should have at least one URL")
        return False

    invalid_urls = []
    if DOU_URL and not valid_URL(DOU_URL):
        invalid_urls.append(DOU_URL)
    if Djinni_URL and not valid_URL(Djinni_URL):
        invalid_urls.append(Djinni_URL)

    for url in invalid_urls:
        print(f"ERROR: {url} invalid URL")

    return not invalid_urls


def scrape_urls(DOU_URL, Djinni_URL, experiences, cookies, tech_i):
    for exp_i, exp_row in experiences.iterrows():
        if DOU_URL:
            scrape_dou_page(DOU_URL + exp_row['dou_param'], tech_i, exp_i)
        if Djinni_URL:
            scrape_djinni_page(Djinni_URL + exp_row['djinni_param'], cookies, tech_i, exp_i)


def process_new_technology(old_technologies, new_technologies, experiences, cookies, tech_i):
    technology, DOU_URL, Djinni_URL = get_new_technology_input()

    if not validate_technology(technology, old_technologies, new_technologies):
        return new_technologies, False

    if not validate_URLs(DOU_URL, Djinni_URL):
        return new_technologies, False

    new_row = pd.DataFrame({'technology': [technology], 'dou_url': [DOU_URL], 'djinni_url': [Djinni_URL]})
    new_technologies = pd.concat([new_technologies, new_row], ignore_index=True)

    if db.write_table(new_row, schema, 'technology'):
        scrape_urls(DOU_URL, Djinni_URL, experiences, cookies, tech_i)
        return new_technologies, True

    return new_technologies, False


if __name__ == '__main__':
    cookies = get_cookies()
    old_technologies = db.read_table(schema, 'technology', index='id')
    experiences = db.read_table('warehouse', 'experience', index='id')

    new_technologies = old_technologies[0:0]
    tech_i = old_technologies.index.max() + 1

    while True:
        new_technologies, success = process_new_technology(old_technologies, new_technologies, experiences, cookies, tech_i)
        if not success:
            continue

        tech_i += 1
        if not menu_input():
            break

    added = run()
    print(f"Added {added} vacancies")
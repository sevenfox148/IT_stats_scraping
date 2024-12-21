from selenium.common.exceptions import WebDriverException
from scraping.chromedriver import get_driver, next_page_djinni
from data.db_interactions import write_table
from logs.set_up_logger import get_logger
from bs4 import BeautifulSoup
import pandas as pd
import time

scraping_logger = get_logger("scraping_logger", "scraping.log")

def djinni_date(date):
    return f"{str(date.day).zfill(2)}.{str(date.month).zfill(2)}.{date.year}"


def collect_data(soup, technology, experience, today=None):
    vacancies = soup.find_all("li", class_="mb-4")
    all_titles, all_links, all_companies, all_dates, all_geo = [], [], [], [], []

    for vacancy in vacancies:
        date_tag = vacancy.find("span", {'data-original-title': True})
        date = date_tag['data-original-title'].strip()[6:] if date_tag else ""
        if today and date != today:
            break

        title_tag = vacancy.find("a", class_="job-item__title-link")
        title = title_tag.text.strip() if title_tag else ""
        link = "https://djinni.co" + title_tag.get("href") if title_tag else ""

        company = vacancy.find("a", {'data-analytics': 'company_page'})
        company = company.text.strip() if company else ""

        info_div = vacancy.find('div', class_="fw-medium d-flex flex-wrap align-items-center gap-1")
        spans = info_div.find_all('span', class_="text-nowrap")

        geo = "Змішано"

        for span in spans:
            if span.text.strip() in ["Тільки офіс", "Тільки віддалено"]:
                geo = span.text.strip()
                break

        all_titles.append(title)
        all_links.append(link)
        all_companies.append(company)
        all_dates.append(date)
        all_geo.append(geo)

    return pd.DataFrame({"description": all_titles,
                         "url": all_links,
                         "technology": [technology] * len(all_titles),
                         "experience": [experience] * len(all_titles),
                         "company": all_companies,
                         "work_type": all_geo,
                         "creation_date": all_dates})


def scrape_djinni_page(URL, cookies, technology, experience):
    driver = get_driver()

    try:
        driver.get(URL)
        time.sleep(1)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()

        next_page = True
        vacancies = pd.DataFrame(columns=["description", "url", "technology",
                                              "experience", "company", "work_type",
                                              "creation_date"])
        while next_page:
            time.sleep(1)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            vacancies = pd.concat([vacancies, collect_data(soup, technology, experience)], ignore_index=True)
            next_page = next_page_djinni(driver, URL)

        driver.quit()
        scraping_logger.info(f"Page {URL} scraped successfully")
        if len(vacancies)>0:
            return write_table(vacancies, 'stage_zone', 'djinni_vacancy')
        else:
            return 0

    except WebDriverException as e:
        scraping_logger.error(f"Webdriver error while scraping {URL}: {e}")
        raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")


def daily_scrape_djinni(date, URL, cookies, technology, experience):
    driver = get_driver()

    try:
        driver.get(URL)
        time.sleep(1)
        for cookie in cookies:
            driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(0.1)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        vacancies = collect_data(soup, technology, experience, today=djinni_date(date))
        driver.quit()
        scraping_logger.info(f"Daily scraping of {URL} successful")
        if len(vacancies) > 0:
            return write_table(vacancies, 'stage_zone', 'djinni_vacancy')
        else:
            return 0

    except WebDriverException as e:
        scraping_logger.error(f"Webdriver error while scraping {URL}: {e}")
        raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")
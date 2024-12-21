from selenium.common.exceptions import WebDriverException
from scraping.chromedriver import get_driver, scroll_dou_page
from data.db_interactions import write_table
from logs.set_up_logger import get_logger
from bs4 import BeautifulSoup
import pandas as pd
import time

scraping_logger = get_logger("scraping_logger", "scraping.log")

def dou_date(date):
    months = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
    }
    return f"{date.day} {months[date.month]}"


def collect_data(soup, technology, experience, today=None):
    vacancies = soup.find_all("li", class_="l-vacancy")

    all_titles, all_links, all_companies, all_dates, all_geo = [], [], [], [], []

    for vacancy in vacancies:
        date_tag = vacancy.find("div", class_="date")
        date = date_tag.text.strip() if date_tag else ""
        if today and date != today:
            if "__hot" in vacancy.get("class", []):
                continue
            else:
                break

        title_tag = vacancy.find("a", class_="vt")
        title = title_tag.text.strip() if title_tag else ""
        link = title_tag.get("href") if title_tag else ""

        company = vacancy.find("a", class_="company")
        company = company.text.strip() if company else ""

        geo_tag = vacancy.find("span", class_="cities")
        geo = geo_tag.text.strip() if geo_tag else ""

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
                                "work_geo": all_geo,
                                "creation_date": all_dates})


def scrape_dou_page(URL, technology, experience):
    driver = get_driver()
    try:
        driver.get(URL)
        scroll_dou_page(driver, URL)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        vacancies = collect_data(soup, technology, experience)
        scraping_logger.info(f"Page {URL} scraped successfully")
        if len(vacancies) > 0:
            return write_table(vacancies, 'stage_zone', 'dou_vacancy')
        else:
            return 0
    except WebDriverException as e:
        scraping_logger.error(f"Webdriver error while scraping {URL}: {e}")
        raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")


def daily_scrape_dou(date, URL, technology, experience):
    driver = get_driver()
    try:
        driver.get(URL)
        time.sleep(0.1)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        driver.quit()
        vacancies = collect_data(soup, technology, experience, today=dou_date(date))
        scraping_logger.info(f"Daily scraping of {URL} successful")
        if len(vacancies) > 0:
            return write_table(vacancies, 'stage_zone', 'dou_vacancy')
        else:
            return 0
    except WebDriverException as e:
        scraping_logger.error(f"Webdriver error while scraping {URL}: {e}")
        raise RuntimeError("WebDriver error\nDetails in logs/scraping.log")
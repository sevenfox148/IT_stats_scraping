from scraping.chromedriver import get_cookies
from scraping.scrape_dou import daily_scrape_dou
from scraping.scrape_djinni import daily_scrape_djinni
from data.db_interactions import read_table
from itertools import product
from datetime import datetime, timedelta
import time

def run():
    cookies = get_cookies()
    the_date = datetime.now() - timedelta(days=2)
    technologies = read_table('warehouse', 'technology', index='id')
    experiences = read_table('warehouse', 'experience', index='id')

    for tech_index, exp_index in product(technologies.index, experiences.index):
        tech_row = technologies.loc[tech_index]
        exp_row = experiences.loc[exp_index]

        if tech_row['dou_url']:
            dou_URL = tech_row['dou_url'] + exp_row['dou_param']
            daily_scrape_dou(the_date, dou_URL, tech_index, exp_index)

        if tech_row['djinni_url']:
            djinni_URL = tech_row['djinni_url'] + exp_row['djinni_param']
            daily_scrape_djinni(the_date, djinni_URL, cookies, tech_index, exp_index)

if __name__ == '__main__':
    start_time = time.time()

    run()

    end_time = time.time()
    execution_time = end_time - start_time

    print(f"Час виконання: {execution_time/60:.3f} хвилин")
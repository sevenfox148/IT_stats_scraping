import data.db_interactions as db
from etl.etl_dou import clear_dou
from etl.etl_djinni import clear_djinni
import pandas as pd
import re


def clear_company(company_name):
    company_name = company_name.replace("-", " ")
    company_name = company_name.replace(". ", " ")
    company_name = re.sub(r"\(.*?\)", "", company_name)
    return company_name.strip()

def write_companies(df):
    old_companies = db.read_table('warehouse', 'company', index='id')
    new_companies = pd.DataFrame(df['company'].unique(), columns=['name'])
    new_companies = new_companies[~new_companies['name'].isin(old_companies['name'])]
    db.write_table(new_companies, 'warehouse', 'company')

def combine_clear(dou_vacancy, djinni_vacancy):
    vacancies_df = pd.concat([dou_vacancy, djinni_vacancy], ignore_index=True)
    vacancies_df.drop_duplicates(subset=['description', 'company'], keep='first', inplace=True)

    vacancies_df['company'] = vacancies_df['company'].apply(clear_company)
    vacancies_df['company'] = vacancies_df['company'].apply(lambda x: "Unknown" if pd.isna(x) or x.strip() == "" else x)
    write_companies(vacancies_df)

    companies = db.read_table('warehouse', 'company', index='id')
    name_to_index = dict(zip(companies['name'], companies.index))
    vacancies_df['company'] = vacancies_df['company'].map(name_to_index).astype(int)

    return vacancies_df


def run():
    dou_df = db.read_table('stage_zone', 'dou_vacancy')
    clear_dou(dou_df)
    djinni_df = db.read_table('stage_zone', 'djinni_vacancy')
    clear_djinni(djinni_df)
    vacancies_df = combine_clear(dou_df, djinni_df)

    added = db.write_table(vacancies_df, 'warehouse', 'vacancy')
    if added == len(vacancies_df):
        db.clear_table('stage_zone', 'dou_vacancy')
        db.clear_table('stage_zone', 'djinni_vacancy')
    return added

run()
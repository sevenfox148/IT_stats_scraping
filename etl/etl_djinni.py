import pandas as pd


work_types = {"Тільки віддалено":"Remote",
              "Змішано":"Mixed",
              "Тільки офіс":"Office"}

def format_date(date_str):
    day, month, year = date_str.split('.')
    return f"{month}.{day}.{year}"


def clear_djinni(djinni_df):
    djinni_df['creation_date'] = djinni_df['creation_date'].apply(format_date)
    djinni_df['creation_date'] = pd.to_datetime(djinni_df['creation_date'])

    djinni_df['work_type'] = djinni_df['work_type'].replace(work_types)
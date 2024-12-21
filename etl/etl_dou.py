import pandas as pd
from datetime import datetime


months = {
    "січня": "01", "лютого": "02", "березня": "03", "квітня": "04",
    "травня": "05", "червня": "06", "липня": "07", "серпня": "08",
    "вересня": "09", "жовтня": "10", "листопада": "11", "грудня": "12"
}
def convert_date(date_str):
    day, month_ua = date_str.split()
    day = int(day)
    month = int(months[month_ua])

    now = datetime.now()
    year = now.year
    if (month > now.month) or (month == now.month and day > now.day):
        year -= 1

    return f"{str(month).zfill(2)}.{str(day).zfill(2)}.{year}"


def determine_work_type(location):
    if "віддалено" in location and len(location.strip()) == len("віддалено"):
        return "Remote"
    elif "віддалено" in location:
        return "Mixed"
    else:
        return "Office"


def clear_dou(dou_df):
    dou_df['creation_date'] = dou_df['creation_date'].apply(convert_date)
    dou_df['creation_date'] = pd.to_datetime(dou_df['creation_date'])

    dou_df['work_geo'] = dou_df['work_geo'].apply(determine_work_type)
    dou_df.rename(columns={'work_geo': 'work_type'}, inplace=True)
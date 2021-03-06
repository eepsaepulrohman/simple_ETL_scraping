# -*- coding: utf-8 -*-
"""Homework_Simple_ETL_Scraping.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/128F59j9kztqyxsCSlfsUQZIf6lWAycnF

#Extract, Transform, Load

Nama : Eep Saepul Rohman

class: Data Engineer 5

##Web Scraping
"""

import pandas as pd
import logging
logging.basicConfig(level=logging.INFO)

url ='https://id.wikipedia.org/wiki/Daftar_miliarder_Forbes'

def scrape(url):
  logging.info(f"Scraping website with '{url}' ....")
  return pd.read_html(url, header=None)

data_scrape = scrape(url)[1]

data_scrape

"""##Cleangsing data"""

import re

def is_money_miliar(string_money):
  # akan return True jika terdeteksi data yang berakhiran miliar
  return string_money.lower().endswith('miliar')

def transform_money_format(string_money):
    # mengganti koma menjadi titik dan menghilangkan spasi
    half_clean_string = string_money.lower().replace(",", ".").replace(" ", "").replace("$", "")
    # mendeteksi string M atau miliar dan J atau juta dan menggantinya dengan string kosong
    return re.sub(r"[?\[M\]miliar|\[J\]juta]", "", half_clean_string)

def transform(df, tahun):
  logging.info("Transforming DataFrame ...")

  columns_scraping = {
      "No.": "no",
      "Nama": "nama",
      "Kekayaan bersih (USD)": "kekayaan_bersih_usd",
      "Usia": "usia",
      "Kebangsaan": "kebangsaan",
      "Sumber kekayaan": "sumber_kekayaan"
  }

  # mengganti nama2 column sebelumnya sesuai kebutuhan
  renamed_df = df.rename(columns=columns_scraping)
  # menambahkan column tahun dan memberinya value yang berasal dari parameter tahun
  renamed_df["tahun"] = tahun
  
  # Memberi nilai pada kekayaan_bersih_usd_juta dgn percabangan if else
  # Jika terdeteksi string miliar (is_money_miliar), maka dikali 1000 dan string miliar atau juta dihilangkan
  # Jika tidak, maka hanya menghilangkan string juta saja
  renamed_df["kekayaan_bersih_usd_juta"] = renamed_df["kekayaan_bersih_usd"].apply(
      lambda value : float(transform_money_format(value)) * 1000 if is_money_miliar(value) else float (transform_money_format(value))
  )

  return renamed_df[["no", "nama", "kekayaan_bersih_usd_juta", "usia", "kebangsaan", "sumber_kekayaan", "tahun" ]]

data_scrape_2021 = transform(data_scrape, 2021)

data_scrape_2021

#Cek jumlah data Missing Value
data_scrape.isna().sum()

data_scrape_2021_clean = data_scrape_2021.insert(0, 'nomor_urut', range(1, 1 + len(data_scrape)))

data_scrape_2021_clean = data_scrape_2021.drop(['no'], axis=1)

data_scrape_2021_clean

"""##Storing data"""

!pip install psycopg2-binary

from sqlalchemy import create_engine

DB_NAME = "postgres"
DB_USER = "user1"
DB_PASSWORD = "user1"
DB_HOST = "104.197.148.144"
DB_PORT = "5432"
CONNECTION_STRING = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
TABLE_NAME = 'EepSaepulRohman_orang_terkaya_forbes'

CONNECTION_STRING

def write_to_postgres(df,db_name,table_name,connection_string):
  engine = create_engine(connection_string)
  logging.info(f"Writing dataframe to database : '{db_name}', table '{table_name}' ... ")
  df.to_sql(name = table_name,con=engine,if_exists="replace",index=False)

write_to_postgres(df=data_scrape_2021_clean,db_name=DB_NAME,table_name=TABLE_NAME,connection_string=CONNECTION_STRING)

"""##Read Data From data base"""

def read_from_postgres(db_name, table_name, connection_string):
    engine = create_engine(connection_string)

    logging.info(f"Reading postgres database: '{db_name}', table: '{table_name}' ...")
    return pd.read_sql_table(table_name, con=engine)

result_df = read_from_postgres(db_name=DB_NAME, table_name=TABLE_NAME, connection_string=CONNECTION_STRING)

print("Daftar Orang Terkaya Menurut Forbes:")
print(result_df.to_string())
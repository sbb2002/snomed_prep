import os
import time
import requests
import re
import pandas as pd
import numpy as np
import pickle
from bs4 import BeautifulSoup as bs
from glob import glob

# Load keywords
df_NC = pd.read_excel('code9_prep_not_cancer.xlsx')
df_NC = df_NC[df_NC.columns[1:]]
searching_kws = [e for e in df_NC['한글명']]

# Essential keywords: using RegEX
df_NC2 = df_NC.copy().iloc[:, :2]
alphabet = re.compile(r'[a-zA-Z가-힣, ]+')
df_NC2['target'] = [alphabet.findall(e)[0] if len(alphabet.findall(e))>0 else "" for e in searching_kws]
unique_kws = df_NC2['target'].unique()
# print(df_NC2['target'].unique(), len(df_NC2['target'].unique()))

# Crawl
def tumor_keyword(u):
    return ("종양" in u) | ("암" in u) | ("림프" in u) | ("악성" in u) | ("양성" in u)

kor_alphabet = re.compile(r'[가-힣]+')
url = "https://google.com/search?q="

soup_dict = {}
for i, u in enumerate(unique_kws):
    response = requests.get(url + str(u))
    if response.status_code != 200:
        os.makedirs('./logs', exist_ok=True)
        with open(f'./logs/crawl_report_ix{i+1}.html', 'w', encoding='utf-8') as logtext:
            logtext.write(bs(response.text, 'html.parser').prettify())
        with open(f'./logs/crawl_headers_ix{i+1}.txt', 'w', encoding='utf-8') as headertext:
            headertext.write(str(response.headers))
        raise AssertionError(f"[{i+1:>3}/{len(unique_kws):>3}] {response.status_code} error occured! See detail from below...\n\t- ./logs/crawl_report_ix{i+1}.html\n\t- ./logs/crawl_headers_ix{i+1}.txt")

    soup = bs(response.text, 'html.parser')
    kor_soup = kor_alphabet.findall(str(soup))
    if tumor_keyword(str(kor_soup)) == True:
        soup_dict[u] = 1
    else:
        soup_dict[u] = 0

    print(f"[{i+1:>3}/{len(unique_kws):>3}] Searching...", end='\r')
    time.sleep(1)

    if (i % 50 == 0) & (i > 0):
        with open(f'dict_ix{i}.pickle', 'wb') as pf:
            pickle.dump(soup_dict, pf)
        print(f"[{i+1:>3}/{len(unique_kws):>3}] Save the dictionary as pickle. dir: ./dict_ix{i}.pickle")
    break

with open(f'soup_dict.pickle', 'wb') as pf:
    pickle.dump(soup_dict, pf)
print(f"[{i+1:>3}/{len(unique_kws):>3}] Labeling was done! Save the dictionary as pickle. dir: ./soup_dict.pickle")


if __name__ == "__main__":
    with open('soup_dict.pickle', 'rb') as pf:
        loaded_dict = pickle.load(pf)
    print("Loaded dictionary: ", loaded_dict, type(loaded_dict))
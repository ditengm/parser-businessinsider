from os import listdir
from pycbrf import ExchangeRates
from datetime import date
from bs4 import BeautifulSoup
import requests
import os
import json
import re


headers = {
    "accept": "*/*",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"
}

def get_id(dir):
    """
    :param dir: -> str(path to html file of company)
    :return: push_identifier -> int(id of company)
    """
    with open(dir, encoding='utf-8') as file:
        src = file.read()
    soup = BeautifulSoup(src, 'lxml')
    script_txt = str(soup.find('div', class_='site-content__col site-content__col--left'))
    push_identifier = int(re.search('pushIdentifier":"\w+"', script_txt)[0][28:-1])
    return push_identifier

def get_json(url):
    """
    :param url: -> str(url of company page)
    :return: write json with data of price promotion
    """
    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open("result.json", "w") as file:
        json.dump(response.json(), file, indent=4, ensure_ascii=False)

def write_page():
    """
        :return: func write pages html code to directory 'pages'
    """
    pagination = 11
    files = [f for f in listdir('pages/')]
    if not files:
        for p in range(1, pagination+1):
            url = f'https://markets.businessinsider.com/index/components/s&p_500?p={p}'
            s = requests.Session()
            response = s.get(url=url, headers=headers)
            with open(f'pages/page{p}.html', 'w+', encoding='utf-8') as file:
                file.write(response.text)
            print(f'Write to direction pages "page{p}.html"')

def write_page_company(urls):
    """
    :param urls: -> list(list of url company)
    :return: write to direction "companies" html files of companies
    """
    files = [f for f in listdir('companies/')]
    if not files:
        for i in range(len(urls)):
            url = urls[i]
            s = requests.Session()
            response = s.get(url=url, headers=headers)
            with open(f'companies/company{i}.html', 'w', encoding='utf-8') as file:
                file.write(response.text)
            print(f'Write to direction companies "company{i}.html"')

def rate():
    """
        :return: int -> dollar(dollar to ruble exchange rate)
    """
    today = str(date.today())
    rates = ExchangeRates(today, locale_en=True)
    dollar = float(rates['USD'].value)
    return dollar

def get_urls_company(dirs):
    """
    :param dirs: -> str(direction to html file)
    :return: pages_links -> list(list with companies links)
    """
    pages_urls = []
    for dir in dirs:
        with open(dir, encoding='utf-8') as file:
            src = file.read()
        soup = BeautifulSoup(src, "lxml")
        page_urls = soup.find("tbody", class_="table__tbody").find_all("a")
        for page_url in page_urls:
            pages_urls.append(f"https://markets.businessinsider.com{page_url['href']}")
    return pages_urls

def write_inf_company(directions):
    """
    :param directions: list(str)(paths to companies files)
    :return: write data of companies
    """
    data = []
    month_wrd = {'01': 'Jan',
                 '02': 'Feb',
                 '03': 'Mar',
                 '04': 'Apr',
                 '05': 'May',
                 '06': 'Jun',
                 '07': 'Jul',
                 '08': 'Aug',
                 '09': 'Sep',
                 '10': 'Oct',
                 '11': 'Nov',
                 '12': 'Dec'}
    for i in range(len(directions)):
        dir = directions[i]
        with open(dir, encoding='utf-8') as file:   # Reading html file with personal information about company
            src = file.read()
        soup = BeautifulSoup(src, "lxml")
        name_company = soup.find('span', class_='price-section__label').text
        print(f"Индекс - {i}\n Название - {name_company}\nВыполняется...\n")
        code_company = soup.find('span', class_="price-section__category").text.strip().split()[-1]
        pe_index = 15  # index of P/E element in information block about company
        try:
            pe = float(soup.find_all('div', class_="snapshot__data-item")[pe_index].text.strip().split()[0].replace(',',''))
        except:
            pe = 10000000000
        try:
            week_low = float(soup.find('div', class_='snapshot__data-item snapshot__data-item--small').text.strip().split()[0].replace(',',''))
            week_high = float(soup.find('div', class_='snapshot__data-item snapshot__data-item--small snapshot__data-item--right').text.strip().split()[0].replace(',',''))
            profit = week_high-week_low
        except AttributeError:
            profit = 0
        now_date = str(date.today()).split('-')
        now_year = int(now_date[0])
        month = month_wrd[now_date[1]]
        day = int(now_date[2])
        last_year = now_year-1
        comp_id = get_id(dir)
        # forming url address with json
        try:
            url = f'https://markets.businessinsider.com/ajax/Valor_HistoricPriceList/{comp_id}/{month}.%20{day}%20{last_year}_{month}.%20{day}%20{now_year}/NDN'
            get_json(url)   # write json file
        except:
            url = f'https://markets.businessinsider.com/ajax/Valor_HistoricPriceList/{comp_id}/{month}.%20{day}%20{last_year}_{month}.%20{day}%20{now_year}/NDB'
            get_json(url)  # write json file
        with open('result.json') as file:
            inf_company = json.load(file)
        now_price = inf_company[0]['Close']
        last_price = inf_company[-1]['Close']
        growth_company = ((now_price*100)/last_price)-100
        rus_price = now_price*rate()
        data_company = {
            'code': code_company,
            'name': name_company,
            'price': rus_price,
            'P/E': pe,
            'growth': growth_company,
            'potential profit': profit
        }
        data.append(data_company)
        print(f"{i} - Выполнено\n {name_company} - Название компании\n\n")
    with open("data_company.json", "a+", encoding='utf-8') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)



def main():
    # Checking Availability files in project
    files = [f for f in listdir('/parser')]
    if 'pages' not in files:
        os.mkdir('pages')
    if 'companies' not in files:
        os.mkdir('companies')
    write_page()   # write pages 1 - 11
    files_pages = [f"pages/{f}" for f in listdir('pages/')]  # paths to saved pages
    urls = get_urls_company(files_pages)    # links to personal company pages
    write_page_company(urls)   # write pages company
    files_comp = [f"companies/{f}" for f in listdir('companies/')]
    write_inf_company(files_comp)   # write all necessary information about company

if __name__ == "__main__":
    main()

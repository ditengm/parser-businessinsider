import json

def main():
    with open('data_company.json') as file:
        data = json.load(file)

    high_price = sorted(data, key=lambda dt: dt['price'], reverse=True)[:10]
    low_pe = sorted(data, key=lambda dt: dt['P/E'])[:10]
    high_growth = sorted(data, key=lambda dt: dt['growth'], reverse=True)[:10]
    high_profit = sorted(data, key=lambda dt: dt['potential profit'], reverse=True)[:10]

    with open("high_price.json", "w") as file:
        json.dump(high_price, file, indent=4, ensure_ascii=False)
    with open("low_pe.json", "w") as file:
        json.dump(low_pe, file, indent=4, ensure_ascii=False)
    with open("high_growth.json", "w") as file:
        json.dump(high_growth, file, indent=4, ensure_ascii=False)
    with open("high_profit.json", "w") as file:
        json.dump(high_profit, file, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
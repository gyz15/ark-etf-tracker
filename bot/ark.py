from .models import ArkFund, ArkStock
import pandas as pd
import requests
import cloudscraper
import os
import json
import urllib
from datetime import date, timedelta
from decimal import Decimal
from django.core.exceptions import ObjectDoesNotExist
from decouple import config

MSG_ID = config('MSG_ID')
BOT_TOKEN = config('BOT_TOKEN')
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# TODO Determine need to loop through by seeing date.
# TODO Make format easier to read


def find_ark():
    # try:
    scraper = cloudscraper.create_scraper()
    for stock in ArkStock.objects.all():
        stock.had_changes = False
        stock.save()
    for etf in ArkFund.objects.filter(update_now=True):
        print(etf.ticker)
        with scraper.get(etf.file_url, stream=True) as r:
            with open(f".\{etf.ticker}.csv", "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        new_data = pd.read_csv(
            f".\{etf.ticker}.csv", parse_dates=[0], dayfirst=True, skipfooter=3, engine='python',)
        sending_data = {"added": [], "removed": [],
                        "buying": [], "selling": []}
        new_data.fillna("-", inplace=True)
        # Comparing latest data with the data in the database
        for company_name in new_data.company:
            new_company = new_data.loc[new_data.company == company_name]
            print(etf, company_name)
            try:
                stock = ArkStock.objects.get(company=company_name, fund=etf)
                stock.had_changes = True
                stock.save()
                sending_data, stock = handle_stock_add_minus(
                    sending_data, new_company, stock)
            except ObjectDoesNotExist:
                # todo handle message here
                company = new_company['company'].values[0]
                ticker = new_company['ticker'].values[0]
                shares = int(new_company['shares'].values[0])
                weight = new_company['weight(%)'].values[0]
                stock = ArkStock.objects.create(
                    company=company, ticker=ticker, shares=shares, weight=weight, fund=etf, had_changes=True)
                stock.save()
                data = []
                data.append(stock.company)
                data.append(stock.ticker)
                data.append(stock.shares)
                data.append(stock.weight)
                sending_data['added'].append(data)
        removed_stocks = etf.stocks.filter(had_changes=False)
        for stock in removed_stocks:
            data = []
            data.append(stock.company)
            data.append(stock.ticker)
            data.append(stock.shares)
            sending_data['removed'].append(data)
            stock.delete()
        if os.path.exists(f".\{etf.ticker}.csv"):
            os.remove(f".\{etf.ticker}.csv")
        else:
            pass
        todays_date = date.today() - timedelta(days=1)
        date_val = todays_date.strftime('%d/%m/%y')
        message = f'Changes of {etf.ticker} on {date_val}:'
        if sending_data['added'] != []:
            message += "\n*Stocks newly added into the fund（建倉）:*"
            for data in sending_data['added']:
                message += f'''\n
{data[0]}({data[1]})
Shares bought: {data[2]}
Weight: {data[3]}%'''
        else:
            message += "\n\n*(No stocks were newly added)*"
        message += "\n\n----------------------------\n\n"
        if sending_data['removed'] != []:
            message += "\n\n*Stocks removed from the fund（平倉）:*"
            for data in sending_data['removed']:
                message += f'''\n
{data[0]}({data[1]})
Shares sold: {data[2]}'''
        else:
            message += "\n*(No stocks were removed)*"
        message += "\n\n----------------------------\n\n"
        if sending_data['buying'] != []:
            message += "\n*Stocks were bought by the fund（加倉):*"
            for data in sending_data['buying']:
                message += f'''\n
{data[0]}({data[1]})
Shares bought yesterday: {data[2]} (+{data[3]}%)
Weight: {data[4]}% (+{data[5]}%)'''
        else:
            message += "\n*(No stocks were bought)*"
        message += "\n\n----------------------------\n\n"
        if sending_data['selling'] != []:
            message += "\n*Stocks were sold by the fund(減倉):*"
            for data in sending_data['selling']:
                message += f'''\n
{data[0]}({data[1]})
Shares sold yesterday: {data[2]} (-{data[3]}%)
Weight: {data[4]}% (-{data[5]}%)'''
        else:
            message += "\n*(No stocks were sold)*"
        message_list = small_chunk(message)
        for message in message_list:
            send_markdown_text(message, MSG_ID)

    # except Exception as e:
    #     print(e)
    return True


def handle_stock_add_minus(sending_data, new_company, stock):
    add = True
    share_count = int(new_company['shares'].values[0])
    if share_count > stock.shares:
        add = True
    elif share_count < stock.shares:
        add = False
    else:
        add = None
    if add is not None:
        stock.shares_delta = (
            (new_company['shares'].values[0]) - (stock.shares))
        stock.shares_delta_percent = round(Decimal(
            abs(stock.shares_delta/stock.shares)), 2)
        print(f'''
Shares delta: {stock.shares_delta}
Shares (orig): {stock.shares}
Percent after counting: {stock.shares_delta_percent}
        ''')
        stock.shares = new_company['shares'].values[0]
        stock.weight_delta = abs(
            round(Decimal((new_company['weight(%)'].values[0])) - (stock.weight), 2))
        stock.weight = new_company['weight(%)'].values[0]
        print(f'''
Shares (new): {stock}
Weight delta: {stock.weight_delta}
''')
        stock.save()
        if stock.shares_delta_percent <= Decimal(0.01) and stock.weight_delta <= Decimal(0.01):
            pass
        else:
            data = []
            data.append(stock.company)
            data.append(stock.ticker)
            data.append(stock.shares)
            data.append(stock.shares_delta_percent)
            data.append(stock.weight)
            data.append(stock.weight_delta)
            if add:
                sending_data['buying'].append(data)
            else:
                sending_data['selling'].append(data)
    else:
        pass
    return sending_data, stock


def small_chunk(message):
    message_list = []
    formatted_message = []
    size = 2500
    chunk = ''
    split_text = message.split('\n')
    for t in split_text:
        if len(chunk) < size:
            chunk += f'{t}\n'
        else:
            message_list.append(chunk)
            chunk = ''
            chunk += f'{t}\n'
        # last chunk wont pass through else clause so it must be save again
    message_list.append(chunk)
    formatted_message = [urllib.parse.quote_plus(
        message, safe="*") for message in message_list]
    return formatted_message


def send_markdown_text(text, chat_id):
    # text = urllib.parse.quote_plus(text, safe="*")
    url = URL + \
        f"sendMessage?text={text}&chat_id={chat_id}&parse_mode=Markdown"
    r = requests.get(url)


def is_valid_action_request(request):
    try:
        data = json.loads(request.body)
        return request.method == "POST" and data['key'] == config('ACTION_PW')
    except Exception as e:
        print(e)

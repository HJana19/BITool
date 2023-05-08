import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth
from .models import ImpactActions, SovrnTransactions, CJTransactions
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import time
from django.db import transaction
import pandas as pd



def refresh_sales_data():
    sovrn_format = ("%Y/%m/%d")
    impact_format = ("%Y-%m-%dT%H:%M:%SZ")
    now = datetime.now()
    year_before = now - relativedelta(days=363)
    month_before = now - relativedelta(months=1)
    # fetch_impact_actions_data(year_before.strftime(impact_format), now.strftime(impact_format))
    # fetch_sovrn_transactions_data(year_before.strftime(sovrn_format),now.strftime(sovrn_format))
    # fetch_cj_commission_data("2021-05-01T00:00:00Z", "2021-05-30T00:00:00Z")
    fetch_rakuten_transactions_data("2021-08-01", "2021-11-12")



def fetch_impact_actions_data(startDate, endDate):
    base_url = 'https://api.impact.com/Mediapartners/' + \
        settings.IMPACT_ACCOUNT_SID + '/Actions'
    query_params = {"ActionDateStart": startDate,
                    "ActionDateEnd": endDate}
    headers = {"Accept": "application/json"}
    response = requests.get(base_url, params=query_params, headers=headers, auth=HTTPBasicAuth(
        settings.IMPACT_ACCOUNT_SID, settings.IMPACT_AUTH_TOKEN))

    if(response.status_code==200):
        data = response.json()
        update_impact_tables(data['Actions'])
    # print("actions count:",len(data['Actions']))
    # 
    # return render(request, "test.html", {"impact_response": response.json()})


def fetch_sovrn_transactions_data(startDate, endDate):
    base_url = 'https://viglink.io/transactions/'
    query_params = {"clickDateStart": startDate,
                    "clickDateEnd": endDate, "sumByField": "publisherRevenue", "groupByFields": "clickDate"}
    headers = {"Authorization": "secret " + settings.SOVRN_SECRETKEY}
    response = requests.get(base_url, params=query_params, headers=headers)

    if response.status_code==200:
        data = response.json()
        count = data['pagination']['totalItems']
        pages = math.ceil(count/data['pagination']['perPage'])
        reportid = data['reportId']
        transactions = []
        buckets = []
        while(pages>0):
            # if 'results' not in data:
            #     break
            # if data['pagination']['perPage']==0:
            #     break
            for t in map_results(data['results']):
                transactions.append(t)
            # count-=len(data['results'])
            pages-=1
            if(data['pagination']['page']==1):
                buckets = data['buckets']
            report_query_param = {"reportId":reportid}
            time.sleep(1)
            next_response = requests.get(base_url, params=report_query_param, headers=headers)
            data = next_response.json()
        update_sovrn_tables(transactions, buckets)
        # print("transactions count:", len(transactions), "bucketscount:", len(buckets))
    # return render(request, "sovrn.html", {"sovrn_response": transactions})

def fetch_cj_commission_data(startDate, endDate):
    url = 'https://commissions.api.cj.com/query'
    query = '''
    query ($pub: [String!]!, $strtdt: String!, $enddt: String!){ 
    publisherCommissions(forPublishers:$pub, sincePostingDate:$strtdt, beforePostingDate:$enddt){
        count 
        payloadComplete 
        records{
        actionTrackerName
        websiteName
        advertiserName 
        postingDate 
        pubCommissionAmountUsd
        saleAmountUsd
        commissionId 
        items { 
            quantity 
            perItemSaleAmountPubCurrency 
            totalCommissionPubCurrency 
        }  
        } 
    } 
    }
    '''
    variables = {"pub": [settings.CJ_CUSTOMER_ID], "strtdt": startDate,
                "enddt": endDate}
    api_token = settings.CJ_AUTH_TOKEN
    headers = {'Authorization': 'Bearer ' + api_token}

    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code==200:
        data = response.json()
        update_cj_tables(data['data']['publisherCommissions'])



def fetch_rakuten_transactions_data(startDate, endDate):
    url = "https://ran-reporting.rakutenmarketing.com/en/reports/bi-tool-kpis---nov-2021/filters?start_date={0}&end_date={1}&include_summary=Y&network=1&tz=America%2FNew_York&date_type=transaction&token={2}".format(startDate,endDate,settings.RAKUTEN_TOKEN)
    data = pd.read_csv(url, skiprows=4)
    print(data)


def map_results(results):
    transactions = []
    for r in results:
        record = SovrnTransactions(
            commission_id = r['commissionId'],
            campaign_name = r['campaignName'],
            click_date = r['clickDate'],
            commission_date = r['commissionDate'],
            device_type = r['deviceType'] if 'deviceType' in r else '',
            merchant_name = r['merchantName'],
            order_value = r['orderValue'],
            publisher_revenue = r['publisherRevenue']
        )
        transactions.append(record)
    return transactions

def update_impact_tables(actions):
    if(len(actions)>0):
        with transaction.atomic():
            for action in actions:
                record = ImpactActions(
                    id = action['Id'],
                    campaign_name = action['CampaignName'],
                    state = action['State'],
                    payout = action['Payout'],
                    amount = action['Amount'],
                    event_date = action['EventDate'][:10]
                )
                record.save()


def update_sovrn_tables(transactions, buckets):
    # SovrnTransactions.objects.bulk_create(transactions)
    # with transaction.atomic():
    for t in transactions:
        t.save()

def update_cj_tables(publisherCommissions):
    if publisherCommissions['count'] > 0:
        records = publisherCommissions['records']
        for r in records:
            cj_trans = CJTransactions(
                commission_id = r['commissionId'],
                action_tracker_name = r['actionTrackerName'],
                advertiser_name = r['advertiserName'],
                website_name = r['websiteName'],
                posting_date = datetime.strptime(r['postingDate'], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d"),
                publisher_commission_amount = r['pubCommissionAmountUsd'],
                sale_amount = r['saleAmountUsd']
            )
            cj_trans.save()



    

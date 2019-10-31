import json
import requests


def exchange(source, destination, token):
    rawdata = requests.get('https://free.currconv.com/api/v7/convert?q={}_{}&compact=ultra&apiKey={}'.format(source, destination, token))
    data = rawdata.json()
    return data


def total_and_itemized(**kwargs):

    token = '35801eacef41acd145e7'
    source = 'GBP'
    dest = kwargs['order']['currency']
    rate = exchange(source, dest, token)[source + '_' + dest]

    sumgross = 0
    sumvat = 0
    itemized = []

    for items in kwargs['order']['items']:
        with open('/home/peter/PycharmProjects/Tails.comAPI/pricing.json', 'r') as f:
            pricing = json.load(f)

        for p in pricing['prices']:
            if p['product_id'] == items['product_id']:

                if p['vat_band'] == 'standard':
                    vatpc = 0.2
                else:
                    vatpc = 0.0

                net = round(p['price'] * items['quantity'], 0)
                vat = round(net * vatpc, 0)

                sumvat += vat * rate
                sumgross += (net + vat) * rate
                itemized.append({'Product ID': items['product_id'], 'Item Price': net * rate, 'VAT': vat})

    return {
        'Total Price': sumgross, 'Total VAT': sumvat,
        'Items': itemized
            }
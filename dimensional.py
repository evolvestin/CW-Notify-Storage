import os
from collections import defaultdict
server = os.environ['server']
res = defaultdict(dict)
idMe = 396978030

res['TOKEN'] = defaultdict(dict)
res['TOKEN']['cw2'] = '530805773:AAFE-VDtmvxtCfJAzsTMTNBT74VWxDFguj4'
res['TOKEN']['cw3'] = '468445195:AAHKJxXQRxg5kJau_KT4smoCvJfnqcgOS4c'

res['factor'] = defaultdict(dict)
res['factor']['cw2'] = 1
res['factor']['cw3'] = 2

res['file'] = defaultdict(dict)
res['file']['cw2'] = 'eustorage'
res['file']['cw3'] = 'storage'

res['document'] = defaultdict(dict)
res['document']['cw2'] = 'eu_storage'
res['document']['cw3'] = 'ru_storage'

res['json_old'] = defaultdict(dict)
res['json_old']['cw2'] = 'eustorage1.json'
res['json_old']['cw3'] = 'bigdata1.json'

res['json_storage'] = defaultdict(dict)
res['json_storage']['cw2'] = 'eustorage2.json'
res['json_storage']['cw3'] = 'bigdata2.json'

res['destination'] = defaultdict(dict)
res['destination']['cw2'] = 'https://t.me/ChatWarsAuction/'
res['destination']['cw3'] = 'https://t.me/chatwars3/'

res['zone'] = defaultdict(dict)
res['zone']['cw2'] = 'EU-'
res['zone']['cw3'] = 'RU-'

res['lots_post_id'] = defaultdict(dict)
res['lots_post_id']['cw2'] = 9
res['lots_post_id']['cw3'] = 10

res['lot'] = defaultdict(dict)
res['lot']['cw2'] = 'Lot #'
res['lot']['cw3'] = 'Лот #'

# ---------------------- forms ----------------------

res['form']['cw2'] = {
    'title': 'Lot #(\d+) : (.*)',
    'quality': 'Quality: (.*)',
    'condition': 'Condition: (.*)',
    'modifiers': 'Modifiers:',
    'seller': 'Seller: (.*)',
    'cost': 'Current price: (\d+) pouch\(es\)',
    'buyer': 'Buyer: (.+)',
    'stamp': 'End At: (\d{2}) (.*) 10(\d{2}) (\d{2}):(\d{2})',
    'status': 'Status: (#active|Finished|Cancelled|Failed)'
}

res['form']['cw3'] = {
    'title': 'Лот #(\d+) : (.*)',
    'quality': 'Качество: (.*)',
    'condition': 'Состояние: (.*)',
    'modifiers': 'Modifiers:',
    'seller': 'Продавец: (.*)',
    'cost': 'Текущая .*: (\d+) 👝',
    'buyer': 'Покупатель: (.+)',
    'stamp': 'Срок: (\d{2}) (.*) 10(\d{2}) (\d{2}):(\d{2})',
    'status': 'Статус: (#active|Finished|Cancelled|Failed)'
}

absolute_emails = ['larik.live@gmail.com', 'weeueks3@gmail.com', 'xstorage1@storage-216513.iam.gserviceaccount.com']

res['emails']['cw3'] = [*absolute_emails, 'auinfo1@notify-209915.iam.gserviceaccount.com',
                        'bigdata@bigeye.iam.gserviceaccount.com',
                        'bigdata2@bigeye.iam.gserviceaccount.com']

res['emails']['cw2'] = [*absolute_emails, 'euauction1@euauction-213512.iam.gserviceaccount.com',
                        'eustorage1@storageeu-217910.iam.gserviceaccount.com',
                        'eustorage2@storageeu-217910.iam.gserviceaccount.com']

res['title'] = defaultdict(dict)
res['title']['cw2'] = 'Lot #(\d+) : (.*)'
res['title']['cw3'] = 'Лот #(\d+) : (.*)'

res['quali'] = defaultdict(dict)
res['quali']['cw2'] = 'Quality: (.*)'
res['quali']['cw3'] = 'Качество: (.*)'

res['condi'] = defaultdict(dict)
res['condi']['cw2'] = 'Condition: (.*)'
res['condi']['cw3'] = 'Состояние: (.*)'

res['seller'] = defaultdict(dict)
res['seller']['cw2'] = 'Seller: (.*)'
res['seller']['cw3'] = 'Продавец: (.*)'

res['price'] = defaultdict(dict)
res['price']['cw2'] = 'Current price: (\d+) pouch\(es\)'
res['price']['cw3'] = 'Текущая .*: (\d+) 👝'

res['buyer'] = defaultdict(dict)
res['buyer']['cw2'] = 'Buyer: (.+)'
res['buyer']['cw3'] = 'Покупатель: (.+)'

res['stamp'] = defaultdict(dict)
res['stamp']['cw2'] = 'End At: (\d{2}) (.*) 10(\d{2}) (\d{2}):(\d{2})'
res['stamp']['cw3'] = 'Срок: (\d{2}) (.*) 10(\d{2}) (\d{2}):(\d{2})'

res['status'] = defaultdict(dict)
res['status']['cw2'] = 'Status: (#active|Finished|Cancelled|Failed)'
res['status']['cw3'] = 'Статус: (#active|Finished|Cancelled|Failed)'

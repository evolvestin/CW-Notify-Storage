import os
response_dictionary = {}
server = 'cw3' #os.environ['server']
absolute_emails = ['larik.live@gmail.com', 'weeueks3@gmail.com', 'xstorage1@storage-216513.iam.gserviceaccount.com']
res = {'form': {}, 'emails': {}, 'TOKEN': {}, 'document': {}, 'json_old': {}, 'json_storage': {},
       'destination': {}, 'zone': {}, 'lots_post_id': {}}

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

res['emails']['cw2'] = [*absolute_emails,
                        'euauction1@euauction-213512.iam.gserviceaccount.com',
                        'eustorage1@storageeu-217910.iam.gserviceaccount.com',
                        'eustorage2@storageeu-217910.iam.gserviceaccount.com']

res['emails']['cw3'] = [*absolute_emails,
                        'auinfo1@notify-209915.iam.gserviceaccount.com',
                        'bigdata@bigeye.iam.gserviceaccount.com',
                        'bigdata2@bigeye.iam.gserviceaccount.com']

res['TOKEN']['cw2'] = '530805773:AAFE-VDtmvxtCfJAzsTMTNBT74VWxDFguj4'
res['TOKEN']['cw3'] = '468445195:AAHKJxXQRxg5kJau_KT4smoCvJfnqcgOS4c'

res['destination']['cw2'] = 'https://t.me/ChatWarsAuction/'
res['destination']['cw3'] = 'https://t.me/chatwars3/'

res['json_storage']['cw2'] = 'eustorage2.json'
res['json_storage']['cw3'] = 'bigdata2.json'

res['json_old']['cw2'] = 'eustorage1.json'
res['json_old']['cw3'] = 'bigdata1.json'

res['document']['cw2'] = 'eu_storage'
res['document']['cw3'] = 'ru_storage'

res['lots_post_id']['cw2'] = 9
res['lots_post_id']['cw3'] = 10

res['zone']['cw2'] = 'EU-'
res['zone']['cw3'] = 'RU-'


def bot_dimension():
    for i in res:
        values = res.get(i)
        response_dictionary[i] = values[server]
    return response_dictionary

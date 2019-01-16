token = '468445195:AAHKJxXQRxg5kJau_KT4smoCvJfnqcgOS4c'
file = 'new-storage'
json_old = 'bigdata1.json'
form = 'Лот #(\d+) : (.*)\n' \
    '\S*\s?(.*)\n?' \
    'Продавец: (.*)\n' \
    'Текущая цена: (\d+) 👝\n' \
    'Покупатель: (.+)\n' \
    'Срок: (\d\d) (.*) (.*) (\d\d):(\d\d)\n' \
    'Статус: (#active|Finished|Cancelled|Failed)'
adress = 'https://t.me/chatwars3/'

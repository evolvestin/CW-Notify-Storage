token = '512299506:AAGwDkft8yr0dSknOC8gCdf_cFU6civ3jls'
file = 'new-storage'
json_old = 'bigdata1.json'
json_storage = 'bigdata4.json'
json_active = 'bigdata5.json'
form = 'Лот #(\d+) : (.*)\n' \
    '\S*\s?(.*)\n?' \
    'Продавец: (.*)\n' \
    'Текущая .*: (\d+) 👝\n' \
    'Покупатель: (.+)\n' \
    'Срок: (\d\d) (.*) (.*) (\d\d):(\d\d)\n' \
    'Статус: (#active|Finished|Cancelled|Failed)'
adress = 'https://t.me/chatwars3/'
lastsold = '\nПоследний проданный: '
soldtimes = '\n\n<b>Продано раз: </b>'
alltime = '<b>За всё время:</b>\n'
days = '<b>За последние 7 дней:</b>\n'
median = 'Медианная цена: '
average = 'Средняя цена: '
minmax = 'Мин/Макс: '
unsold = 'Не продано: '

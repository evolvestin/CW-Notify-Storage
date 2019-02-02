token = '530805773:AAFE-VDtmvxtCfJAzsTMTNBT74VWxDFguj4'
file = 'eustorage'
json_old = 'eustorage1.json'
json_storage_supp = 'eustorage3.json'
json_storage = 'eustorage4.json'
json_active = 'eustorage5.json'
form = 'Lot #(\d+) : (.*)\n' \
       '\S*\s?(.*)\n?' \
       'Seller: (.*)\n' \
       'Current price: (\d+) pouch\(es\)\n' \
       'Buyer: (.+)\n' \
       'End At: (\d\d) (.*) (.*) (\d\d):(\d\d)\n' \
       'Status: (#active|Finished|Cancelled|Failed)'
adress = 'https://t.me/ChatWarsAuction/'
lastsold = '\nLast sold: '
soldtimes = '\n\n<b>Times sold: </b>'
alltime = '<b>All time:</b>\n'
days = '<b>Last 7 days:</b>\n'
median = 'Median: '
average = 'Average: '
minmax = 'Min/Max: '
unsold = 'Unsold: '

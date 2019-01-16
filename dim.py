token = '530805773:AAFE-VDtmvxtCfJAzsTMTNBT74VWxDFguj4'
file = 'new-eustorage'
json_old = 'bigdata2.json'
form = 'Lot #(\d+) : (.*)\n' \
       '\S*\s?(.*)\n?' \
       'Seller: (.*)\n' \
       'Current price: (\d+) pouch\(es\)\n' \
       'Buyer: (.+)\n' \
       'End At: (\d\d) (.*) 106(.) (\d\d):(\d\d)\n' \
       'Status: (#active|Finished|Cancelled|Failed)'
adress = 'https://t.me/ChatWarsAuction/'

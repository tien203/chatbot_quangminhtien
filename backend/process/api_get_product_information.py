import pymongo, re
client = pymongo.MongoClient("mongodb://mdbadmin:fwYHdDtTym6lNmyoiJPTfZzTW0jiokx5@aimdb.devhcm.local:30000/admin")
my_db = client['chatbot_quangminhtien']
my_col = my_db['products']
def get_product_name_from_message(message):
    document = my_col.find({}, {"_id":0})
    product_list = []
    product_detail = []
    for item in document:
        product_list.append(item['name'])
        product_detail.append(item)
    product_regex = r'(' + '|'.join(product_list) + r')'
    result = re.findall(product_regex, message)
    detail = {}
    if result:
        for item in product_detail:
            if item['name'] == result[0]:
                detail = item
    if result:
        result = result[0]
    else:
        result = ""
    return result, detail

def get_phone_address_from_message(message):
    phone_regex = r'\b(08[1-9]\d{7}|09\d{8}|05[2|6|8|9]\d{7}|07[0|6|7|8|9]\d{7}|03[2-9]\d{7})\b'
    phone = re.findall(phone_regex, message)
    if phone:
        phone = phone[0]
    else:
        phone = ''
    address_regex = r'\b(địa\s*chỉ|dia\s*chi)\b'
    if re.search(address_regex, message):
        address_idx = re.search(address_regex, message).span()[1]
        address = message[address_idx:].strip()
    else:
        address = ''
    return phone, address


 
# a,b = get_product_name_from_message('đầm caro bao nhiêu')
# print(a, b)
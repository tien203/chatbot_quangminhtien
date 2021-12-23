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

 
# a,b = get_product_name_from_message('đầm caro bao nhiêu')
# print(a, b)
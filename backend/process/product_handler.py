from threading import Condition
import pymongo, re
# import sys
# sys.path.append('../api')
from .api_get_product_information import get_product_name_from_message 
import numpy as np
client = pymongo.MongoClient("mongodb://mdbadmin:fwYHdDtTym6lNmyoiJPTfZzTW0jiokx5@aimdb.devhcm.local:30000/admin")
my_db = client['chatbot_quangminhtien']
my_col = my_db['conversation']


def check_condition(current_tag, intent_json, msg, lst_entity):
    product_name, detail = get_product_name_from_message(msg)
    if product_name:
        lst_entity['product_name'] = product_name

    query = {"sender_id": ""}
    my_col.update_one(query, {"$set": {
        "sender_id": "",
        "information": lst_entity,
        "pre_tag": current_tag
    }})

    document = my_col.find({}, {"_id":0})
    conversation_info = []
    for item in document:
        conversation_info.append(item)
    conversation_info = conversation_info[-1]['information']

    for i in intent_json['intents']:
        if i['tag']==current_tag:
            block = i
    flag = True
    while not block['responses'] or flag:
        flag = False
        if 'condition' in block and block['condition']:
            for key, value in block['condition'].items():
                count = 0
                for k, v in value.items():
                    if (v and conversation_info[k]) or (not v and not conversation_info[k]):
                        count+=1
                if count == len(value):
                    for index in range(len(intent_json['intents'])):
                        if intent_json['intents'][index]['tag'] == key:
                            block = intent_json['intents'][index]
                            break
    res = np.random.choice(block['responses'])
    
    # lst_entity = {'product_name':product_name}
    check_entity = r'((?<=\{).*?(?=\}))'
    entity = re.findall(check_entity, res)
    for i in range(len(lst_entity)):
        res = res.replace('{', '')
        res = res.replace('}', '')
        res = res.replace(list(lst_entity.keys())[i], list(lst_entity.values())[i])
    return res, block['tag'], lst_entity

# import json
# with open(r'C:\Users\TMT\Desktop\An-AI-Chatbot-in-Python-and-Flask\intents.json', encoding='utf-8') as fh:
#     intents = json.load(fh)
# check_condition("request_material", intents, "đầm caro còn ko")
from threading import Condition
import pymongo, re
import copy
# import sys
# sys.path.append('../api')
from .get_information import get_product_name_from_message, get_phone_address_from_message
import numpy as np
client = pymongo.MongoClient("mongodb://mdbadmin:fwYHdDtTym6lNmyoiJPTfZzTW0jiokx5@aimdb.devhcm.local:30000/admin")
my_db = client['chatbot_quangminhtien']
my_col = my_db['conversation']


def check_condition(current_tag, intent_json, msg, lst_entity):
    document = my_col.find({}, {"_id":0})
    conversation_info = []
    for item in document:
        conversation_info.append(item)
    conversation_info = conversation_info[-1]['information']

    lst_entity['product_name'], lst_entity['amount'], lst_entity['price']  = get_product_name_from_message(msg)
    lst_entity['phone_number'], lst_entity['address'] = get_phone_address_from_message(msg)

    info_clone = copy.deepcopy(conversation_info)
    for entity in info_clone:
        if not conversation_info[entity] or lst_entity[entity]:
            conversation_info[entity] = lst_entity[entity]

    # if product_name:
    #     lst_entity['product_name'] = product_name
    query = {"sender_id": "1"}
    my_col.update_one(query, {"$set": {
        "sender_id": "1",
        "information": conversation_info,
        "pre_tag": current_tag
    }})



    for i in intent_json['intents']:
        if i['tag']==current_tag:
            block = i
    flag = True
    while not block['responses'] or flag:
        flag = False
        if 'condition' in block and block['condition']:
            for key, value in block['condition'].items():
                print(value, key)
                count = 0
                for k, v in value.items():
                    if (v and conversation_info[k]) or (not v and not conversation_info[k]):
                        count+=1
                if count == len(value):
                    for index in range(len(intent_json['intents'])):
                        if intent_json['intents'][index]['tag'] == key:
                            block = intent_json['intents'][index]
                            break
                    else:
                        continue
                    break

    res = np.random.choice(block['responses'])
    check_entity = r'((?<=\{).*?(?=\}))'
    entity = re.findall(check_entity, res)
    for i in range(len(conversation_info)):
        res = res.replace('{', '')
        res = res.replace('}', '')
        res = res.replace(list(conversation_info.keys())[i], list(conversation_info.values())[i])
    return res, block['tag'], conversation_info

# import json
# with open(r'C:\Users\TMT\Desktop\An-AI-Chatbot-in-Python-and-Flask\intents.json', encoding='utf-8') as fh:
#     intents = json.load(fh)
# check_condition("request_material", intents, "đầm caro còn ko")
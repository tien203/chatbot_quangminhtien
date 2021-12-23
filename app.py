import pymongo
client = pymongo.MongoClient("mongodb://mdbadmin:fwYHdDtTym6lNmyoiJPTfZzTW0jiokx5@aimdb.devhcm.local:30000/admin")
my_db = client['chatbot_quangminhtien']
my_col = my_db['conversation']
# document = my_col.find({}, {"_id":0})
# conversation = []
# for item in document:
#     conversation.append(item)
# print(conversation)
# libraries
import random
import numpy as np
import pickle
import json
from flask import Flask, render_template, request
from flask_ngrok import run_with_ngrok
import nltk
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from backend.process.product_handler import check_condition
# chat initialization
model = load_model("chatbot_model.h5")
# intents = json.loads(open("intents.json").read())
with open('intents.json', encoding='utf-8') as fh:
    intents = json.load(fh)
words = pickle.load(open("words.pkl", "rb"))
classes = pickle.load(open("classes.pkl", "rb"))

app = Flask(__name__)
run_with_ngrok(app) 

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get", methods=["POST"])
def chatbot_response():
    document = my_col.find({}, {"_id":0})
    conversation_info = []
    for item in document:
        conversation_info.append(item)
    lst_entity = conversation_info[-1]['information']

    msg = request.form["msg"]
    ints = predict_class(msg, model)
    res = getResponse(ints, intents)
    tag = ints[0]['intent']
    if float(ints[0]['probability']) < 0.99 or not res:
        document = my_col.find({}, {"_id":0})
        conversation = []
        for item in document:
            conversation.append(item)
        pre_tag = conversation[-1]['pre_tag']
        if float(ints[0]['probability']) < 0.99:
            res, tag, lst_entity = check_condition(pre_tag, intents, msg, lst_entity)
        else:
            res, tag, lst_entity = check_condition(tag, intents, msg, lst_entity)

    for i in range(len(lst_entity)):
        res = res.replace('{', '')
        res = res.replace('}', '')
        res = res.replace(list(lst_entity.keys())[i], list(lst_entity.values())[i])

    query = {"sender_id": ""}
    my_col.update_one(query, {"$set": {
        "sender_id": "",
        "information": lst_entity,
        "pre_tag": tag
    }})
    return res

# chat functionalities
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(words)
    for s in sentence_words:
        for i, w in enumerate(words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, model):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    tag = ints[0]["intent"]
    list_of_intents = intents_json["intents"]
    for i in list_of_intents:
        if i["tag"] == tag:
            if i["responses"]:
                result = random.choice(i["responses"])
                break
            else:
                result = ""
    return result


if __name__ == "__main__":
    app.run()


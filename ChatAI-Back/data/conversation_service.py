from . import get_database


def get_by_id(cid):
    collection = get_database().conversation
    conversation = collection.find({"_id": cid})
    conversation = list(conversation)
    return None if len(conversation) == 0 else conversation[0]


def save(conv):
    collection = get_database().conversation
    conv_exist = collection.find_one({"_id": conv["_id"]})
    return collection.insert_one(conv) if conv_exist is None \
        else collection.find_one_and_replace({"_id": conv["_id"]}, conv)


def replace(conv):
    collection = get_database().conversation
    return collection.find_one_and_replace({"_id": conv["_id"]}, conv)

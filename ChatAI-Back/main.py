import getopt
import logging
import os
import socket
import sys
import time
import uuid

import openai
from dotenv import load_dotenv
from flask import Flask, request

from data import conversation_service as conv_service
from data import set_database
from util.Result import err, log, ok

app = Flask(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# 设置内置日志记录器等级
logger = logging.getLogger('werkzeug')


# logger.setLevel(logging.ERROR)


# code-davinci-002
# text-davinci-003

def get_param(jn, key, default_value):
    return jn[key] if key in jn else default_value


@app.route("/generate/id", methods=['POST'])
def generate_id():
    return ok(str(uuid.uuid4()))


@app.route("/ai/suitable/<cid>", methods=['PUT'])
def response_suitable(cid):
    if not request.json \
            or 'suitable' not in request.json \
            or 'msg_idx' not in request.json \
            or 'idx' not in request.json:
        return err("请求参数缺失！")
    idx = request.json['idx']
    msg_idx = request.json['msg_idx']
    suitable = request.json['suitable']
    logger.info(log(f"id:{cid},idx:{idx},msg_idx:{msg_idx}\nsuitable:{suitable}"))

    conversation = conv_service.get_by_id(cid)
    if conversation is None:
        return err("对话不存在")

    convs = conversation["convs"]
    if len(convs) <= idx \
            or convs[idx]["speaker"] == "human":
        return err("下标有误")

    convs[idx]["suitable"][msg_idx] = suitable
    conv_service.replace(conversation)
    return ok(None)


@app.route("/text/<cid>/<idx>", methods=['PUT'])
def text_change(cid, idx):
    if not request.json \
            or 'prompt' not in request.json:
        return err("请求参数缺失！")
    prompt = request.json['prompt']
    idx = int(idx)
    logger.info(log(f"id:{cid},idx:{idx}\nprompt:{prompt}"))

    conversation = conv_service.get_by_id(cid)
    if conversation is None:
        return err("对话不存在")

    convs = conversation["convs"]
    if len(convs) <= idx \
            or convs[idx]["speaker"] == "ai":
        return err("下标有误")

    convs[idx]["speech"] = prompt
    conv_service.replace(conversation)
    return ok(None)


@app.route("/chat/repeat/<cid>", methods=['POST'])
def chat_repeat(cid):
    logger.info(log(f"id:{cid}"))
    conversation = conv_service.get_by_id(cid)
    if conversation is None:
        return err("对话不存在")

    convs_str = ""
    for conv in conversation["convs"][0:-1]:
        convs_str += f"{conv['speaker']}:{conv['speech'] if 'speech' in conv else conv['speeches'][-1]}\n"
    convs_str += "ai:"

    model = get_param(request.json, "model", 'text-davinci-003')
    temperature = get_param(request.json, "temperature", .8)
    max_tokens = get_param(request.json, "max_tokens", 500)
    top_p = get_param(request.json, "top_p", 1.)
    frequency_penalty = get_param(request.json, "frequency_penalty", .5)
    presence_penalty = get_param(request.json, "presence_penalty", 0.0)

    response = openai.Completion.create(
        model=model,
        prompt=convs_str,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    ai_text = response["choices"][0]["text"]
    logger.info(log(ai_text))
    conversation["convs"][-1]["speeches"].append(ai_text)
    conversation["convs"][-1]["suitable"].append(0)
    conv_service.replace(conversation)
    return ok(ai_text)


@app.route("/conv/<cid>", methods=['GET'])
def conv(cid):
    logger.info(log(f"id:{cid}"))
    conversation = conv_service.get_by_id(cid)
    return ok(conversation)


@app.route("/chat/<cid>", methods=['POST'])
def chat(cid):
    if not request.json \
            or 'prompt' not in request.json:
        return err("请求参数缺失！")

    prompt = request.json['prompt']
    logger.info(log(f"id:{cid}\nprompt:{prompt}"))
    conversation = conv_service.get_by_id(cid)

    if conversation is None:
        conversation = {"_id": cid, "title": prompt, "convs": []}

    conversation["convs"].append({
        "speaker": "human",
        "speech": prompt,
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    })

    convs_str = ""
    for conv in conversation["convs"]:
        convs_str += f"{conv['speaker']}:{conv['speech'] if 'speech' in conv else conv['speeches'][-1]}\n"
    convs_str += "ai:"

    model = get_param(request.json, "model", 'text-davinci-003')
    temperature = get_param(request.json, "temperature", .8)
    max_tokens = get_param(request.json, "max_tokens", 500)
    top_p = get_param(request.json, "top_p", 1.)
    frequency_penalty = get_param(request.json, "frequency_penalty", .5)
    presence_penalty = get_param(request.json, "presence_penalty", 0.0)

    response = openai.Completion.create(
        model=model,
        prompt=convs_str,
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
    )
    ai_text = response["choices"][0]["text"]
    logger.info(log(ai_text))
    conversation["convs"].append({
        "speaker": "ai",
        "speeches": [ai_text],
        "suitable": [0],
        "createTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    })
    conv_service.save(conversation)

    return ok(ai_text)


def init_logging():
    hostname = socket.gethostname()
    logfile_path = '/code/%s' % hostname
    os.mkdir(logfile_path)
    logfile_name = logfile_path + '/cat.log'
    logging.basicConfig(level=logging.INFO, filename=logfile_name,
                        format="%(asctime)s - [%(levelname)s] %(filename)s$%(funcName)s:%(lineno)d\t"
                               "%(message)s",
                        datefmt="%F %T")


def init_database():
    logging.info(sys.argv[1:])
    opts, args = getopt.getopt(sys.argv[1:], 'u:p:', ["host=", "port=", "databaseName="])
    set_database(opts)


if __name__ == '__main__':
    init_logging()
    init_database()
    app.run(host="0.0.0.0", port=8383, debug=False)

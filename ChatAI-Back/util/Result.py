from flask import jsonify, g


def wrap_err_result(msg, code=500):
    return jsonify({"code": code, "msg": msg})


def wrap_result(data):
    return jsonify({"code": 200, "data": data})


def wrap_log(data):
    if "track_id" in g:
        return f"[{g.track_id}] {data}"
    return data


err = wrap_err_result
fail = wrap_err_result
ok = wrap_result
log = wrap_log

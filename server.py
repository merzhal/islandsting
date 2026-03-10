from flask import Flask, request, jsonify
import json
import datetime
import random
import string
import requests

app = Flask(__name__)

DATABASE = "database.json"
ADMIN_KEY = "SUPERSECRETADMINKEY"
WEBHOOK = "https://discord.com/api/webhooks/1480710346686599258/uqNbrb6bNdmjwxXe6Pxs_TDKbhcA1udXYkxmSWfCafKdA4VVqfflty6-D0zyfaixvLXq"


# -------------------------
# DATABASE
# -------------------------

def load_db():
    with open(DATABASE) as f:
        return json.load(f)

def save_db(data):
    with open(DATABASE,"w") as f:
        json.dump(data,f,indent=4)


# -------------------------
# DISCORD LOG
# -------------------------

def log(username, hwid, key):

    if WEBHOOK == "":
        return

    try:

        requests.post(WEBHOOK,json={
            "content":f"User: {username}\nHWID: {hwid}\nKey: {key}"
        })

    except:
        pass


# -------------------------
# KEY GENERATOR
# -------------------------

def generate_key():

    chars = string.ascii_uppercase + string.digits

    return ''.join(random.choice(chars) for _ in range(16))


# -------------------------
# HOME
# -------------------------

@app.route("/")
def home():

    return "Key system running"


# -------------------------
# GENERATE KEY
# -------------------------

@app.route("/generate")
def generate():

    admin = request.args.get("admin")
    days = int(request.args.get("days",30))

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    key = generate_key()

    expire = (datetime.datetime.utcnow() + datetime.timedelta(days=days)).timestamp()

    db["keys"][key] = {
        "hwid":None,
        "expires":expire
    }

    save_db(db)

    return jsonify({
        "status":"generated",
        "key":key
    })


# -------------------------
# CHECK KEY (SCRIPT USE)
# -------------------------

@app.route("/check")
def check():

    key = request.args.get("key")
    hwid = request.args.get("hwid")
    username = request.args.get("user")

    db = load_db()

    if hwid in db["blacklist"]:
        return jsonify({"status":"blacklisted"})

    if key not in db["keys"]:
        return jsonify({"status":"invalid"})

    data = db["keys"][key]

    if data["expires"] < datetime.datetime.utcnow().timestamp():
        return jsonify({"status":"expired"})

    if data["hwid"] is None:

        data["hwid"] = hwid
        save_db(db)

    elif data["hwid"] != hwid:

        db["blacklist"].append(hwid)
        save_db(db)

        return jsonify({"status":"hwid_mismatch"})

    log(username,hwid,key)

    return jsonify({"status":"valid"})


# -------------------------
# ADMIN CHECK KEY
# -------------------------

@app.route("/checkkey")
def checkkey():

    admin = request.args.get("admin")
    key = request.args.get("key")

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    if key not in db["keys"]:
        return jsonify({"status":"not_found"})

    return jsonify(db["keys"][key])


# -------------------------
# DELETE KEY
# -------------------------

@app.route("/delete")
def delete():

    admin = request.args.get("admin")
    key = request.args.get("key")

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    if key in db["keys"]:

        del db["keys"][key]

        save_db(db)

        return jsonify({"status":"deleted"})

    return jsonify({"status":"not_found"})


# -------------------------
# RESET HWID
# -------------------------

@app.route("/resethwid")
def resethwid():

    admin = request.args.get("admin")
    key = request.args.get("key")

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    if key not in db["keys"]:
        return jsonify({"status":"not_found"})

    db["keys"][key]["hwid"] = None

    save_db(db)

    return jsonify({"status":"hwid_reset"})


# -------------------------
# BLACKLIST HWID
# -------------------------

@app.route("/blacklist")
def blacklist():

    admin = request.args.get("admin")
    hwid = request.args.get("hwid")

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    if hwid not in db["blacklist"]:
        db["blacklist"].append(hwid)

    save_db(db)

    return jsonify({"status":"blacklisted"})


# -------------------------
# LIST KEYS
# -------------------------

@app.route("/keys")
def keys():

    admin = request.args.get("admin")

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    return jsonify(db["keys"])


# -------------------------
# WIPE KEYS
# -------------------------

@app.route("/wipe")
def wipe():

    admin = request.args.get("admin")

    if admin != ADMIN_KEY:
        return jsonify({"status":"unauthorized"})

    db = load_db()

    db["keys"] = {}

    save_db(db)

    return jsonify({"status":"wiped"})

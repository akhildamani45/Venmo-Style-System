import json
import db
from flask import Flask, request

app = Flask(__name__)

DB = db.DatabaseDriver()

@app.route("/")
@app.route("/api/users/")
def get_users():
    """
    Getting all users
    """
    return json.dumps({"users": DB.get_all_users()}), 200

@app.route("/api/users/", methods=["POST"])
def create_user():
    """
    Creating new user
    """
    body = json.loads(request.data)
    name = body.get("name")
    username = body.get("username")
    balance = body.get("balance", 0)
    if not name or not username:
        return json.dumps({"error": "Bad request"}), 400
    else:
        user_id = DB.insert_user_table(name, username, balance)
        return json.dumps(DB.get_user_id(user_id)), 201

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Getting user based off id
    """
    user = DB.get_user_id(user_id)
    if not user:
        return json.dumps({"error": "User not found"}), 404
    return json.dumps(user), 200
    

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    Deletes user
    """
    user = DB.get_user_id(user_id)
    if not user:
        return json.dumps({"error": "User not found"}), 404
    else:
        DB.delete_user_id(user_id)
        return json.dumps(user), 200

# @app.route("/api/send/", methods = ["POST"])
# def send_money():
#     """
#     Sends money from one user to another
#     """
#     body = json.loads(request.data)
#     sndr = body.get("sender_id")
#     rcvr = body.get("receiver_id")
#     amnt = body.get("amount")
#     sndr_user = DB.get_user_id(sndr)
#     rcvr_user = DB.get_user_id(rcvr)
#     if sndr is None or rcvr is None or amnt is None:
#         return json.dumps({"error": "Bad request"}), 400
#     elif not sndr_user or not rcvr_user:
#         return json.dumps({"error": "User not found"}), 404
#     elif int(amnt) > DB.get_balance_id(sndr):
#         return json.dumps({"error": "You're not that guy"}), 400
#     else:
#         DB.update_balance_id(sndr, rcvr, amnt)
#         return json.dumps(body), 200

@app.route("/api/transactions/", methods = ["POST"])
def create_transaction():
    """
    Creating new transaction
    """
    body = json.loads(request.data)
    sender_id = body.get("sender_id")
    receiver_id = body.get("receiver_id")
    amount = body.get("amount")
    message = body.get("message")
    accepted = body.get("accepted")
    if not sender_id or not receiver_id or not amount or not message:
        return json.dumps({"error": "Bad request"}), 400
    sndr = DB.get_user_id(sender_id)
    rcvr = DB.get_user_id(receiver_id)
    if not sndr or not rcvr:
        return json.dumps({"error": "User not found"}), 404
    if accepted == True:
        if int(amount) > DB.get_balance_id(sender_id):
            return json.dumps({"error": "You're not that guy"}), 403
        trnx_id = DB.insert_transactions_table(sender_id, receiver_id, amount, accepted, message)
        DB.update_balance_id(sender_id, receiver_id, amount)
        return json.dumps(DB.get_transaction(trnx_id)), 201
    if accepted is None:
        trnx_id = DB.insert_transactions_table(sender_id, receiver_id, amount, accepted, message)
        return json.dumps(DB.get_transaction(trnx_id)), 201


@app.route("/api/transactions/<int:trnx_id>/", methods = ["POST"])
def accept_deny(trnx_id):
    """
    sender accepts or denies transaction request
    """
    body = json.loads(request.data)
    accepted = body.get("accepted")
    trnx = DB.get_transaction(trnx_id)
    if accepted is None or not trnx or trnx["accepted"] is not None:
        return json.dumps({"error": "Bad request"}), 403
    else:
        sender_id = trnx["sender_id"]
        receiver_id = trnx["receiver_id"]
        amount = trnx["amount"]
    if accepted == True:
        if int(amount) > DB.get_balance_id(sender_id):
            return json.dumps({"error": "Error of sort"}), 403
        DB.update_transaction(accepted, trnx_id)
        DB.update_balance_id(sender_id, receiver_id, amount)
        return json.dumps(DB.get_transaction(trnx_id)), 200
    else:
        DB.update_transaction(accepted, trnx_id)
        return json.dumps(DB.get_transaction(trnx_id)), 200
    


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

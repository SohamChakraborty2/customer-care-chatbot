from flask import Flask, request, jsonify
from random import randint, randrange
app = Flask(__name__)

@app.route("/api/user/get", methods=["GET"])
def enquiry():
    msisdn = request.args.get("msisdn")  
    channel = request.args.get("channel") 
    input_type = request.args.get("input") 
    sim_type = request.args.get("sim_type")
    if input_type== "BALANCE_ENQUIRY":
        user_data = {
        "MSISDN": msisdn,
        "INPUT": input_type,
        # "ACCOUNT TYPE": acc_type,
        "BALANCE": "$50",
        "VALIDITY": "20 July 2026", 
        "responseCode": 200,
        "responseDesc": "Success" 
        }
        return jsonify(user_data)
    elif input_type== "TRANSACTION_ENQUIRY":
        user_data = {
        "MSISDN": msisdn,
        "INPUT": input_type,
        # "ACCOUNT TYPE": acc_type,
        "Transaction 1": "23/06/2024 18:07:25 Voice Call Incoming $1.00",
        "Transaction 2": "24/06/2024 14:39:20 Voice Call Incoming $1.10",
        "Transaction 3": "24/06/2024 19:43:32 Voice Call Incoming $2.00",
        "Transaction 4": "25/06/2024 09:38:59 Voice Call Incoming $3.00",
        "Transaction 5": "27/06/2024 18:56:35 Voice Call Incoming $4.00",
        "responseCode": 200,
        "responseDesc": "Success" 
        }
        return jsonify(user_data)
    elif input_type== "TICKET_STATUS":
        
        user_data = {
        "ticketCount" : "0",
        "description1": "No active tickets for you",
        "ticketCount" : "1",
        "description2": "You have one active ticket, kindly be patient as our support staff will reach out to you soon.",
        "responseCode": 200,
        "responseDesc": "Success"}
        return jsonify(user_data)
    elif input_type=="ACC_TYPE":
        user_data1 = {
        "Type": "prepaid",
        "responseCode": 200,
        "responseDesc": "Success"}
        user_data2 = {
        "Type": "postpaid",
        "responseCode": 200,
        "responseDesc": "Success"}
        if msisdn[3]=='0'or msisdn[3]=='2'or msisdn[3]=='4'or msisdn[3]=='6'or msisdn[3]=='8':
            return jsonify(user_data1)
        else:
            return jsonify(user_data2)
    elif input_type=="SIM_TYPE":
        if sim_type=="e-sim":
            user_data={
            "Price": "4",
            "responseCode": 200,
            "responseDesc": "Success",
            "Offer 2": "Cingular Unlimited + 10GB hotspot data",
            "Price 2": "20",
            "Offer 3": "Cingular Unlimited + 15GB hotspot data",
            "Price 3": "25",
            "Offer 1": "Cingular Unlimited + 5GB hotspot data",
            "Price 1": "17",
            }
            return jsonify(user_data)
        elif sim_type=="physical":
            user_data={
            "Price": "5",
            "responseCode": 200,
            "responseDesc": "Success",
            "Offer 1": "Cingular Unlimited + 10GB hotspot data",
            "Price 1": "20",
            "Offer 3": "Cingular Unlimited + 20GB hotspot data",
            "Price 3": "27",
            "Offer 2": "Cingular Unlimited + 15GB hotspot data",
            "Price 2": "24",
            }
            return jsonify(user_data)
    elif input_type=="NEW_NUM":
        random_number = randint(10**9, 10**10 - 1)
        user_data={
            "responseCode": 200,
            "responseDesc": "Success",
            "number": random_number
        }
        return jsonify(user_data)



        
            



@app.route("/api/user/put", methods=["PUT"])
def raise_ticket():
    
    request_data = request.json
    input_type = request.args.get("input") 
    issue = request_data.get('Issue')
    name = request_data.get('Name')
    phone_number = request_data.get('Phone_Number')
    email = request_data.get('Email')

    user_data = {
        "INPUT": input_type,
        'message': 'An agent will connect with you soon!',
        "responseCode": 200, 
        "responseDesc": "success"  
    }
    if issue== None or name==None or phone_number==None or email==None:
        user_data["responseCode"]= 100
        user_data["responseDesc"]= "failure"
        return jsonify(user_data)
    else:
        return jsonify(user_data)

if __name__=="__main__":
    app.run(debug=True)
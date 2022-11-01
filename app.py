from flask import Flask, render_template, request, jsonify, session, redirect
from flask_session import Session
from flask_cors import CORS, cross_origin
from chat import getInstance, getInstanceResponse
import json, uuid, datetime
import sqlalchemy as db

app = Flask(__name__)
cors = CORS(app)
chatbotpool = {}
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_FILE_DIR"]= "./"
#app.config["SECRET_KEY"] = "whattheheckisthis123"
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)
app.config['CORS_ORIGINS'] = ['*']
server_session = Session(app)

engine = db.create_engine('mariadb+pymysql://alan:ThisPasswordIsForOfficeDB@128.173.175.180/chathistory?charset=utf8mb4')
connection = engine.connect()
metadata = db.MetaData()
chatlog = db.Table('chatlog', metadata, autoload=True, autoload_with=engine)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = datetime.timedelta(hours=5)

@app.route('/predict', methods=['POST', 'OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])
def predict():
    global chatbotpool
    #if session.get("key")==None:
    #    session["key"] = str(uuid.uuid4())    
    chatbotinst = None

    #if chatbotpool.get(session["key"])==None:
    #    print("creating a new chatbot instance...")        
    #    chatbotpool[session["key"]] = getInstance()
    
    #chatbotinst = chatbotpool[session["key"]]

    # print(session["history"])
    client_ip = request.environ['REMOTE_ADDR']
    input = json.loads(request.data)
    timestampstr = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    timestamp = datetime.datetime.now().timestamp()
    text = input["message"]
    task = input["task"]
    sessionid = input["sessionid"]

    if sessionid=="":
        sessionid = str(uuid.uuid4())

    if chatbotpool.get(sessionid)==None:
        print("creating a new chatbot instance...")
        chatbotpool[sessionid] = getInstance()
    chatbotinst = chatbotpool[sessionid]

    # check if db connection is alive
    if connection.closed:
        connection = engine.connect()
        metadata = db.MetaData()
        chatlog = db.Table('chatlog', metadata, autoload=True, autoload_with=engine)
    
    print("user,"+text+"||"+sessionid+"||"+timestampstr+"||"+client_ip+"||"+task)
    query = db.insert(chatlog).values(clientIP=client_ip, messageTime=timestamp, message=text, messageFrom='client', sessionID=sessionid, taskType=task)
    ResultProxy = connection.execute(query)
    # check if text is valid
    botmessage = getInstanceResponse(chatbotinst, text)
    timestamp = datetime.datetime.now().timestamp()
    print("bot "+task+"||"+botmessage+"||"+sessionid+"||"+timestampstr+"||"+client_ip+"||"+task)
    response = jsonify({"answer": botmessage, "sessionid": sessionid})
    query = db.insert(chatlog).values(clientIP=client_ip, messageTime=timestamp, message=botmessage, messageFrom='bot', sessionID=sessionid, taskType=task)
    ResultProxy = connection.execute(query)
    response.headers.add('Access-Control-Allow-Headers',"Origin, X-Requested-With, Content-Type, Accept, x-auth")

    # response.headers.add('Access-Control-Allow-Origin', '*')
    # response.headers.add('Access-Control-Allow-Credentials', 'true')
    # response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    # response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    # print(response)
    return response

@app.after_request
def after_request(response):
    #response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

if __name__ == "__main__":
    # app.run(debug=True, port=5000, ssl_context='adhoc', host='0.0.0.0')
    app.run(debug=True, port=5000, ssl_context=('/home/gwang2/research/chatbot/DialoGPT/fullchain1.pem', '/home/gwang2/research/chatbot/DialoGPT/privkey1.pem'), host='0.0.0.0')

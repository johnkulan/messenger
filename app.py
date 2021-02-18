from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_json import FlaskJSON, as_json

from sqlalchemy import create_engine, union

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_DATETIME_FORMAT'] = '%d/%m/%Y %H:%M:%S'
db = SQLAlchemy(app)
FlaskJSON(app)


dbPath = 'database.db'
engine = create_engine('sqlite:///%s' % dbPath)
db.metadata.create_all(bind=engine)


class Messages(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    receiver = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    # date = db.Column(db.DateTime(), nullable=False)
    date = db.Column(db.String(100), nullable=False)

    def __init__(self, sender, receiver, message, date):
        self.sender = sender
        self.receiver = receiver
        self.message = message
        self.date = date


class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


@app.route('/add_user', methods=['POST'])
@as_json
def add_user():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    new_user = Users(username=username, email=email, password=password)
    try:
        db.session.add(new_user)
        user = db.session.query(Users).filter_by(username=username).first()
        db.session.commit()
        return user.id, 200
    except:
        return -1, 501


@app.route('/check_user_existence', methods=['POST'])
@as_json
def check_user_existence():
    current_username = request.json['username']
    current_password = request.json['password']

    try:
        user = db.session.query(Users).filter(Users.username == current_username,
                                              Users.password == current_password).first()
        return user.id, 200
    except Exception:
        return "Not found", 404


@app.route('/all_users', methods=['POST'])
@as_json
def all_users():
    current_id = request.json['id']
    users = db.session.query(Users).filter(Users.id != current_id)
    json_users = {"users": []}

    for user in users:
        json_users["users"].append({"id": user.id, "username": user.username})

    return json_users, 200


@app.route('/send_message', methods=['POST'])
@as_json
def send_message():
    sender = request.json["sender"]
    receiver = request.json['receiver']
    message = request.json['message']
    date = request.json['date']

    if not message:
        return "You didn't write message", 501

    new_message = Messages(sender=sender, receiver=receiver, message=message, date=date)
    print("NEW_MESSAGE", sender, receiver, message, date)

    db.session.add(new_message)
    db.session.commit()


@app.route('/receive_message', methods=['POST', 'GET'])
@as_json
def receive_message():
    sender = request.json['sender']
    receiver = request.json['receiver']
    date = request.json['date']
    first_request = request.json['first_request']
    json_messages = {"messages": []}

    print("REQUEST: ", sender, receiver, date)

    if first_request:
        messages_sender = db.session.query(Messages).filter(Messages.sender == sender,
                                                            Messages.receiver == receiver)
        messages_receiver = db.session.query(Messages).filter(Messages.sender == receiver,
                                                              Messages.receiver == sender)
    else:
        messages_sender = db.session.query(Messages).filter(Messages.sender == sender,
                                                            Messages.receiver == receiver,
                                                            Messages.date > date)
        messages_receiver = db.session.query(Messages).filter(Messages.sender == receiver,
                                                              Messages.receiver == sender,
                                                              Messages.date > date)

    messages = messages_sender.union(messages_receiver).order_by(Messages.date)

    for message in messages:
        json_messages["messages"].append({'sender': message.sender, "receiver": message.receiver,
                                          "message": message.message, "date": message.date})

        # print("ANSWER", message.sender, message.receiver, message.message, message.date)

    return json_messages, 200


if __name__ == '__main__':
    app.run(debug=True)

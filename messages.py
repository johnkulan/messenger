import sys
import requests

from PyQt5 import QtCore, QtGui, QtWidgets
from datetime import datetime

from client.config import SERVER_IP, PORT


class UiMessages(object):
    def setup_ui(self, messages_form):
        messages_form.setObjectName("Messages")
        messages_form.resize(580, 475)
        font = QtGui.QFont()
        font.setPointSize(20)

        self.sendButton = QtWidgets.QPushButton(messages_form)
        self.sendButton.setGeometry(QtCore.QRect(340, 370, 101, 31))
        self.sendButton.setObjectName("sendButton")

        self.labelNewuser = QtWidgets.QLabel(messages_form)
        self.labelNewuser.setGeometry(QtCore.QRect(220, 70, 171, 51))

        self.labelNewuser.setFont(font)
        self.labelNewuser.setObjectName("labelNewuser")

        self.selectButton = QtWidgets.QPushButton(messages_form)
        self.selectButton.setGeometry(QtCore.QRect(340, 140, 101, 31))
        self.selectButton.setObjectName("selectButton")

        self.textMessage = QtWidgets.QLineEdit(messages_form)
        self.textMessage.setGeometry(QtCore.QRect(140, 370, 191, 31))
        self.textMessage.setObjectName("textMessage")

        self.textBrowser = QtWidgets.QTextBrowser(messages_form)
        self.textBrowser.setGeometry(QtCore.QRect(140, 180, 301, 181))
        self.textBrowser.setObjectName("textBrowser")

        self.usersBox = QtWidgets.QComboBox(messages_form)
        self.usersBox.setGeometry(QtCore.QRect(140, 140, 191, 31))
        self.usersBox.setObjectName("usersBox")

        self.retranslateUi(messages_form)
        QtCore.QMetaObject.connectSlotsByName(messages_form)

    def retranslateUi(self, messages_form):
        _translate = QtCore.QCoreApplication.translate
        messages_form.setWindowTitle(_translate("Messages", "Form"))
        self.sendButton.setText(_translate("Messages", "SEND"))
        self.labelNewuser.setText(_translate("Messages", "MESSAGES"))
        self.selectButton.setText(_translate("Messages", "SELECT"))


class UpdateMessagesThread(QtCore.QObject):
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.target_user = ""
        self.last_date = ""
        self.first_request = False

    running = False
    newMessage = QtCore.pyqtSignal(str)

    def run(self):
        while True:
            # global FIRST_REQUEST, LAST_DATE
            url_receive = f'http://{SERVER_IP}:{PORT}/receive_message'

            payload_receive = {'sender': self.current_user,
                               'receiver': self.target_user,
                               'date': self.last_date,
                               'first_request': FIRST_REQUEST}

            temp = requests.post(url_receive, json=payload_receive)
            json_resp = temp.json()

            for message in json_resp["messages"]:
                strin = message["sender"] + ': ' + message["message"]
                self.last_date = message["date"]
                self.newMessage.emit(strin)

            QtCore.QThread.msleep(500)


class MessagesWindow(QtWidgets.QWidget):
    def __init__(self, current_id, current_username):
        super().__init__()
        self.ui = UiMessages()
        self.ui.setup_ui(self)
        self.ui.selectButton.clicked.connect(self.show_all_messages)
        self.ui.sendButton.clicked.connect(self.btn_send_message_handler)

        self.current_id = current_id
        self.current_username = current_username

        # создадим поток
        self.thread = QtCore.QThread()
        # создадим объект для выполнения кода в другом потоке
        self.updateMessagesThread = UpdateMessagesThread(self.current_username)
        # перенесём объект в другой поток
        self.updateMessagesThread.moveToThread(self.thread)
        # после чего подключим все сигналы и слоты
        self.updateMessagesThread.newMessage.connect(self.add_message_to_text_browser)
        # подключим сигнал старта потока к методу run у объекта, который должен выполнять код в другом потоке
        self.thread.started.connect(self.updateMessagesThread.run)

        # self.thread.start()

        url_all_users = f'http://{SERVER_IP}:{PORT}/all_users'
        response = requests.post(url_all_users, json={"id": str(self.current_id)})
        json_users = response.json()

        for user in json_users["users"]:
            self.ui.usersBox.addItem(user["username"])

    @QtCore.pyqtSlot(str)
    def add_message_to_text_browser(self, string):
        self.ui.textBrowser.append(string)

    def show_all_messages(self):
        global FIRST_REQUEST
        self.ui.textBrowser.clear()
        receiver = self.ui.usersBox.currentText()
        date = str(datetime.utcnow())
        self.updateMessagesThread.first_request = True
        self.updateMessagesThread.target_user = receiver

        url_receive = f'http://{SERVER_IP}:{PORT}/receive_message'
        payload_receive = {'sender': self.current_username,
                           'receiver': receiver,
                           'date': date,
                           'first_request': self.updateMessagesThread.first_request
                           }

        temp = requests.post(url_receive, json=payload_receive)
        json_resp = temp.json()
        FIRST_REQUEST = False

        for message in json_resp["messages"]:
            strin = message["sender"] + ': ' + message["message"]
            self.updateMessagesThread.last_date = message["date"]
            self.ui.textBrowser.append(strin)

        self.thread.start()

    def btn_send_message_handler(self):
        self.send_new_message()
        self.ui.textMessage.clear()

    def send_new_message(self):
        receiver = self.ui.usersBox.currentText()
        message = self.ui.textMessage.text()
        date = str(datetime.utcnow())

        url_send = f'http://{SERVER_IP}:{PORT}/send_message'
        payload = {
            'sender': self.current_username,
            'receiver': receiver,
            'message': message,
            'date': date
        }
        requests.post(url_send, json=payload)


def my_exception_hook(exctype, value, traceback):
    # ignore KeyboardInterrupt when kill allure report processes
    if exctype is KeyboardInterrupt:
        print(f"{exctype}, {value}, {traceback.tb_frame}")
        return
    print(f"{exctype}, {value}, {traceback.tb_frame}")
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # window = MessagesWindow(1, "john")

    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook
    # window.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exit from MessageWindow")
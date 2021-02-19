from client.newuser import *
from client.messages import *

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox

from client.config import SERVER_IP, PORT


class UiLogin(object):
    def setup_ui(self, login_form):
        login_form.setObjectName("LoginWindow")
        login_form.resize(580, 450)
        font = QtGui.QFont()
        font.setPointSize(20)

        self.centralWidget = QtWidgets.QWidget(login_form)
        self.centralWidget.setObjectName("centralWidget")

        self.textUsername = QtWidgets.QLineEdit(self.centralWidget)
        self.textUsername.setGeometry(QtCore.QRect(180, 170, 231, 31))
        self.textUsername.setObjectName("textUsername")

        self.textPassword = QtWidgets.QLineEdit(self.centralWidget)
        self.textPassword.setGeometry(QtCore.QRect(180, 220, 231, 31))
        self.textPassword.setObjectName("textPassword")

        self.labelUsername = QtWidgets.QLabel(self.centralWidget)
        self.labelUsername.setGeometry(QtCore.QRect(110, 180, 61, 20))
        self.labelUsername.setObjectName("labelUsername")

        self.labelPassword = QtWidgets.QLabel(self.centralWidget)
        self.labelPassword.setGeometry(QtCore.QRect(110, 230, 55, 16))
        self.labelPassword.setObjectName("labelPassword")

        self.labelLogin = QtWidgets.QLabel(self.centralWidget)
        self.labelLogin.setGeometry(QtCore.QRect(250, 110, 101, 51))
        self.labelLogin.setFont(font)
        self.labelLogin.setObjectName("labelLogin")

        self.submitButton = QtWidgets.QPushButton(self.centralWidget)
        self.submitButton.setGeometry(QtCore.QRect(180, 270, 101, 31))
        self.submitButton.setObjectName("submitButton")

        self.newUserButton = QtWidgets.QPushButton(self.centralWidget)
        self.newUserButton.setGeometry(QtCore.QRect(310, 270, 101, 31))
        self.newUserButton.setObjectName("newUserButton")
        login_form.setCentralWidget(self.centralWidget)

        self.menuBar = QtWidgets.QMenuBar(login_form)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 580, 26))
        self.menuBar.setObjectName("menuBar")
        login_form.setMenuBar(self.menuBar)

        self.statusBar = QtWidgets.QStatusBar(login_form)
        self.statusBar.setObjectName("statusBar")
        login_form.setStatusBar(self.statusBar)

        self.retranslateUi(login_form)
        QtCore.QMetaObject.connectSlotsByName(login_form)\


    def retranslateUi(self, login_form):
        _translate = QtCore.QCoreApplication.translate
        login_form.setWindowTitle(_translate("login_form", "MainWindow"))
        self.labelUsername.setText(_translate("login_form", "Username"))
        self.labelPassword.setText(_translate("login_form", "Password"))
        self.labelLogin.setText(_translate("login_form", "LOGIN"))
        self.submitButton.setText(_translate("login_form", "Submit"))
        self.newUserButton.setText(_translate("login_form", "New User"))


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = UiLogin()
        self.window = None
        self.ui.setup_ui(self)
        self.ui.submitButton.clicked.connect(self.btn_login_handler)
        self.ui.newUserButton.clicked.connect(self.btn_new_user_handler)

    def open_messages(self, current_id, current_username):
        self.window = MessagesWindow(current_id, current_username)
        self.window.show()
        self.hide()

    def open_new_user(self):
        self.window = NewUserWindow()
        self.window.show()
        self.hide()

    def btn_new_user_handler(self):
        self.open_new_user()

    def btn_login_handler(self):
        url_current_user = f'http://{SERVER_IP}:{PORT}//check_user_existence'

        username = self.ui.textUsername.text()
        password = self.ui.textPassword.text()
        payload = {"username": username, "password": password}
        resp = requests.post(url_current_user, json=payload)
        if resp.status_code == 200:
            current_id = int(resp.text)
            self.open_messages(current_id=current_id, current_username=username)
        elif resp.status_code == 404:
            not_found_user()
        else:
            raise NotImplementedError(f"Unknown server message {resp.status_code} {resp.text}")


def not_found_user():
    message = QMessageBox()
    message.setWindowTitle("Mistake")
    message.setText("User not found")
    message.setIcon(QMessageBox.Warning)
    message.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
    x = message.exec_()


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
    window = LoginWindow()

    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook

    window.show()
    try:
        sys.exit(app.exec_())
    except:
        print("Exiting from login")
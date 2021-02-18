import sys
import requests
from PyQt5 import QtCore, QtGui, QtWidgets
from client.login import LoginWindow

from client.config import SERVER_IP, PORT


class UiNewUser(object):
    def setup_ui(self, new_user_form):
        new_user_form.setObjectName("new_user_form")
        new_user_form.resize(580, 450)
        font = QtGui.QFont()
        font.setPointSize(20)

        self.labelPassword = QtWidgets.QLabel(new_user_form)
        self.labelPassword.setGeometry(QtCore.QRect(110, 290, 55, 16))
        self.labelPassword.setObjectName("labelPassword")

        self.labelNewuser = QtWidgets.QLabel(new_user_form)
        self.labelNewuser.setGeometry(QtCore.QRect(220, 130, 171, 51))
        self.labelNewuser.setFont(font)
        self.labelNewuser.setObjectName("labelNewuser")

        self.labelUsername = QtWidgets.QLabel(new_user_form)
        self.labelUsername.setGeometry(QtCore.QRect(110, 210, 61, 20))
        self.labelUsername.setObjectName("labelUsername")

        self.labelEmail = QtWidgets.QLabel(new_user_form)
        self.labelEmail.setGeometry(QtCore.QRect(110, 250, 61, 20))
        self.labelEmail.setObjectName("labelEmail")

        # LineEdits
        self.textUsername = QtWidgets.QLineEdit(new_user_form)
        self.textUsername.setGeometry(QtCore.QRect(180, 200, 231, 31))
        self.textUsername.setObjectName("textUsername")

        self.textEmail = QtWidgets.QLineEdit(new_user_form)
        self.textEmail.setGeometry(QtCore.QRect(180, 240, 231, 31))
        self.textEmail.setObjectName("textEmail")

        self.textPassword = QtWidgets.QLineEdit(new_user_form)
        self.textPassword.setGeometry(QtCore.QRect(180, 280, 231, 31))
        self.textPassword.setObjectName("textPassword")

        # BUTTONS
        self.submitButton = QtWidgets.QPushButton(new_user_form)
        self.submitButton.setGeometry(QtCore.QRect(180, 330, 101, 31))
        self.submitButton.setObjectName("submitButton")

        self.exitButton = QtWidgets.QPushButton(new_user_form)
        self.exitButton.setGeometry(QtCore.QRect(310, 330, 101, 31))
        self.exitButton.setObjectName("exitButton")

        self.retranslateUi(new_user_form)
        QtCore.QMetaObject.connectSlotsByName(new_user_form)

    def retranslateUi(self, new_user_form):
        _translate = QtCore.QCoreApplication.translate
        new_user_form.setWindowTitle(_translate("new_user_form", "Form"))
        self.exitButton.setText(_translate("new_user_form", "Exit"))
        self.labelPassword.setText(_translate("new_user_form", "Password"))
        self.submitButton.setText(_translate("new_user_form", "Submit"))
        self.labelNewuser.setText(_translate("new_user_form", "NEW USER"))
        self.labelUsername.setText(_translate("new_user_form", "Username"))
        self.labelEmail.setText(_translate("new_user_form", "Email"))


class NewUserWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.ui = UiNewUser()
        self.ui.setup_ui(self)
        self.window = None
        self.ui.submitButton.clicked.connect(self.add_user)
        self.ui.exitButton.clicked.connect(self.open_login)

    def open_login(self):
        self.window = LoginWindow()
        self.window.show()
        self.hide()

    def add_user(self):
        url_add_user = f'http://{SERVER_IP}:{PORT}/add_user'

        text_email = self.ui.textEmail.text()
        text_username = self.ui.textUsername.text()
        text_password = self.ui.textPassword.text()

        payload = {'username': text_username,
                   'email': text_email,
                   'password': text_password}
        resp = requests.post(url_add_user, json=payload)

        if int(resp.text) != -1:
            show_registration_result("Welcome in JohnMessenger")
            self.open_login()
        else:
            self.show_registration_result("Cannot add to Database ")


def show_registration_result(text):
    msg = QtWidgets.QMessageBox()
    msg.setText("{}".format(text))
    msg.exec_()


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
    window = NewUserWindow()

    sys._excepthook = sys.excepthook
    sys.excepthook = my_exception_hook
    window.show()

    try:
        sys.exit(app.exec_())
    except:
        print("Exiting from newuser")
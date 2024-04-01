import sys
import config as c
import requests
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt
from teacherview import TeacherView
from studentview import StudentView
from adminview import AdminView
from server import *

LOGIN_WIDTH = 500
LOGIN_HEIGHT = 330


class QtUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("大学生在线学习监控系统")
        self.access_token = None
        # 人脸识别
        self.get_accesstoken()

        # 学生界面
        self.sv = None
        # 教师界面
        self.tv = None
        # 管理员界面
        self.av = None
        # 数据
        self.data_info = None
        self.radio_list = []
        # 设置登录界面
        self.create_main_ui()

    def create_main_ui(self):
        self.set_center(LOGIN_WIDTH, LOGIN_HEIGHT)

        username_label = QLabel("大学生在线学习监控系统", self)
        username_label.setGeometry(0, 0, LOGIN_WIDTH, 50)
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setFont(QFont('宋体', 20))

        QLabel("账号：", self).move(130, 90)
        QLabel("密码：", self).move(130, 150)

        self.username_input = QLineEdit(self)
        self.username_input.setText("20210907141")
        self.username_input.setFixedSize(170, 25)
        self.username_input.move(200, 85)

        self.password_input = QLineEdit(self)
        self.password_input.setText("12345")
        self.password_input.setFixedSize(170, 25)
        self.password_input.move(200, 144)

        txt_list = ('学生', '教师', '管理员')
        for i in range(len(txt_list)):
            r = QRadioButton(txt_list[i], self)
            r.move(i * 90 + 130, 200)
            self.radio_list.append(r)
        self.radio_list[0].setChecked(True)
        self.radio_list[0].toggled.connect(self.radio_select)

        login_btn = QPushButton('登录', self)
        login_btn.setGeometry(190, 270, 120, 30)
        login_btn.clicked.connect(self.login)

        self.teacher_selection_label = QLabel("请选择教师：", self)
        self.teacher_selection_label.move(145, 238)
        self.teacher_selection_combo = QComboBox(self)
        self.teacher_selection_combo.setGeometry(225, 235, 130, 20)
        self.radio_select()

    # 选择学生需要选择老师
    def radio_select(self):
        if self.radio_list[0].isChecked():
            # 获取老师数据
            teachers = get_all_teachers()
            for teacher in teachers:
                tid = teacher[0]
                tname = teacher[1]
                self.teacher_selection_combo.addItem(tname, tid)
            self.teacher_selection_label.show()
            self.teacher_selection_combo.show()
        else:
            self.teacher_selection_label.hide()
            self.teacher_selection_combo.hide()

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.radio_list[0].isChecked():
            self.data_info = student_login(username, password)
            if self.data_info is not None:
                self.hide()
                teacher_tid = self.teacher_selection_combo.currentData()
                self.sv = StudentView(self.data_info, self.access_token, self.return_login, teacher_tid)
                self.sv.show()
            else:
                QMessageBox.critical(self, "登录失败", "账号或密码错误.")
            return
        elif self.radio_list[1].isChecked():
            self.data_info = verify_teacher(username, password)
            if self.data_info is not None:
                self.hide()
                self.tv = TeacherView(self.data_info, self.return_login)
                self.tv.show()
            else:
                QMessageBox.critical(self, "登录失败", "账号或密码错误.")
            return
        elif self.radio_list[2].isChecked():
            self.data_info = verify_admin(username, password)
            if self.data_info:
                self.hide()
                self.av = AdminView(self.access_token, self.return_login)
                self.av.show()
            else:
                QMessageBox.critical(self, "登录失败", "账号或密码错误.")
            return

        if self.data_info is None:
            QMessageBox.critical(self, "登录失败", "账号或密码错误.")

    """ ------------------------------------------------------------------ """

    # 设置窗体大小并居中
    def set_center(self, ww, hh):
        self.setFixedSize(ww, hh)
        # 获取屏幕大小, 设置居中
        center = QDesktopWidget().availableGeometry().center()
        # self.setGeometry(center.x() - ww // 2, center.y() - hh // 2, ww, hh)
        self.move(center.x() - ww // 2, center.y() - hh // 2)

    # 获取访问令牌（使用百度api接口）
    def get_accesstoken(self):
        host = c.HOST
        print(host)
        # 发送网络请求  requests网络库
        # 使用get函数发送网络请求，参数为网络请求的地址，执行时会产生返回结果，结果就是请求的结果
        response = requests.get(host)
        print(response)
        if response:
            data = response.json()
            self.access_token = data.get('access_token')
            print(self.access_token)
        if self.access_token is None:
            print("api接口链接异常！")

    # 返回登录界面
    def return_login(self):
        self.show()
        if self.sv is not None:
            self.sv.hide()
        if self.tv is not None:
            self.tv.hide()
        if self.av is not None:
            self.av.hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 初始化主体
    q = QtUI()
    q.show()
    sys.exit(app.exec_())  # 启动应用事件循环

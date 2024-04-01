from PyQt5.QtWidgets import *
import config as c
import requests


class FaceRight(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 30, 770, 580)

        self.groupBox_2 = QGroupBox(self)
        self.groupBox_2.setGeometry(60, 30, 300, 520)
        self.groupBox_2.setTitle("学生")
        self.listWidget_2 = QListWidget(self.groupBox_2)
        self.listWidget_2.setGeometry(10, 30, 280, 480)
        self.listWidget_2.clicked.connect(self.get_facetoken)

        self.groupBox_3 = QGroupBox(self)
        self.groupBox_3.setGeometry(405, 30, 300, 520)
        self.groupBox_3.setTitle("人脸列表")
        self.listWidget_3 = QListWidget(self.groupBox_3)
        self.listWidget_3.setGeometry(10, 30, 280, 480)

    # 更新数据
    def update_data(self, access_token):
        request_url = c.Get_users_url
        params = {
            "group_id": 'aaa'
        }
        self.access_token = access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            _l = response.json()
            self.listWidget_2.clear()
            self.listWidget_3.clear()
            for i in _l['result']['user_id_list']:
                self.listWidget_2.addItem(i)

    def get_facetoken(self):
        self.listWidget_3.clear()
        user = self.listWidget_2.currentItem().text()
        face_list = self.user_face_list(user)
        if face_list:
            for i in face_list['result']['face_list']:
                self.listWidget_3.addItem(i['face_token'])

    # 获取用户人脸列表
    def user_face_list(self, user):
        request_url = c.Face_list_url
        params = {
            "user_id": user,
            "group_id": 'aaa'
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()
        return False

    # 获得选中的学生和人脸
    def get_current_select(self):
        user = face_token = None
        if self.listWidget_2.currentItem():
            user = self.listWidget_2.currentItem().text()
        if self.listWidget_3.currentItem():
            face_token= self.listWidget_3.currentItem().text()
        return user, face_token

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QPixmap, QImage
from PyQt5.QtCore import Qt
from uihelp import CreateThreading
from student_modules.process import monitor_processes
from student_modules.browser_history import get_browser_history
from detect import detect_face
from server import update_student_sign_in, get_teacher_by_tid, set_students_overall_score, get_teacher_time
import cv2
import time
import config as c
import base64
import requests

STUDENT_WIDTH = 1000
STUDENT_HEIGHT = 660


class StudentView(QWidget):
    def __init__(self, data_info, access_token, return_login, teacher_tid):
        super().__init__()
        self.return_login = return_login
        self.access_token = access_token
        self.data_info = data_info
        self.teacher_tid = teacher_tid
        # 摄像头
        self.camera = None
        # 截取的图片
        self.pic_data = None
        # 是否签到状态
        self.is_sigin = False
        # 每次登陆账号都是84分, 进程没违规+5,浏览记录没违规+5,5分钟内打卡+6
        self.total_points = 84
        set_students_overall_score(self.data_info['sid'], self.total_points)

        self.setWindowTitle("学生界面")
        self.setFixedSize(STUDENT_WIDTH, STUDENT_HEIGHT)
        # 获取屏幕大小, 设置居中
        center = QDesktopWidget().availableGeometry().center()
        self.move(center.x() - STUDENT_WIDTH // 2, center.y() - STUDENT_HEIGHT // 2)

        left_frame = QFrame(self)
        left_frame.setGeometry(20, 30, 180, 600)

        name_label = QLabel(f"欢迎，{self.data_info['sname']}", left_frame)
        name_label.move(10, 10)
        name_label.setFont(QFont('SimSun', 20))

        QLabel("个人信息：", left_frame).move(10, 60)
        QLabel(f"姓名：{self.data_info['sname']}\n"
               f"学号：{self.data_info['sid']}\n", left_frame).move(10, 85)
        QLabel(f"你的分数是{self.data_info['overall_score'] / 16}分,满分100分\n请检查打卡和进程与浏览记录!", left_frame).setGeometry(10, 110,
                                                                                                               170, 50)

        btn_txt = ('开启监控进程', '开启浏览历史记录', '人脸录入', '人脸签到', '注销')
        btn_command = (
            self.show_process,
            self.show_browser_history,
            self.input_face,
            self.signin_face,
            self.logout
        )

        for i in range(len(btn_txt)):
            if btn_txt[i] == '开启监控进程':
                self.process_btn = QPushButton(btn_txt[i], left_frame)
                self.process_btn.setGeometry(18, i * 70 + 160, 130, 40)
                self.process_btn.clicked.connect(btn_command[i])
            elif btn_txt[i] == '开启浏览历史记录':
                self.browser_history_btn = QPushButton(btn_txt[i], left_frame)
                self.browser_history_btn.setGeometry(18, i * 70 + 160, 130, 40)
                self.browser_history_btn.clicked.connect(btn_command[i])
            elif btn_txt[i] == '人脸签到':
                self.sign_in_btn = QPushButton(btn_txt[i], left_frame)
                self.sign_in_btn.setGeometry(18, i * 70 + 160, 130, 40)
                self.sign_in_btn.clicked.connect(btn_command[i])
            else:
                btn = QPushButton(btn_txt[i], left_frame)
                btn.setGeometry(18, i * 70 + 160, 130, 40)
                btn.clicked.connect(btn_command[i])

        self.message_label1 = QLabel(self)
        self.message_label1.setGeometry(10, 530, 180, 20)
        self.message_label1.setAlignment(Qt.AlignHCenter)
        self.message_label2 = QLabel(self)
        self.message_label2.setGeometry(10, 570, 180, 20)
        self.message_label2.setAlignment(Qt.AlignHCenter)

        self.camera_view = QGroupBox('操作区域', self)
        self.camera_view.setGeometry(200, 30, 770, 580)

        self.camera_label = QLabel(self.camera_view)
        self.camera_label.setGeometry(30, 30, 710, 480)

        self.signin_label = QLabel(self.camera_view)
        self.signin_label.move(205, 385)
        self.signin_label.setGeometry(305, 530, 300, 25)

        self.sure_btn = QPushButton('截图录入', self.camera_view)
        self.sure_btn.setGeometry(200, 520, 140, 40)
        self.sure_btn.clicked.connect(self.get_face)
        self.sure_btn.hide()

        self.close_btn = QPushButton('关闭摄像头', self.camera_view)
        self.close_btn.setGeometry(430, 520, 140, 40)
        self.close_btn.clicked.connect(self.close_camera)
        self.close_btn.hide()

    # 人脸签到
    def signin_face(self):
        # 先关闭摄像头
        self.close_camera()
        self.signin_label.setText('签到情况：')
        self.signin_label.show()
        thread1 = CreateThreading(1, "Thread-1", 1, self.show_camera, None)
        thread1.start()
        self.is_sigin = True
        thread11 = CreateThreading(11, "Thread-11", 11, self.show_signin_face, None)
        thread11.start()

    # 人脸录入
    def input_face(self):
        # 先关闭摄像头
        self.close_camera()
        self.sure_btn.show()
        self.close_btn.show()
        thread1 = CreateThreading(1, "Thread-1", 1, self.show_camera, None)
        thread1.start()

    def show_signin_face(self, _):
        while self.is_sigin:
            if self.pic_data is not None:
                # 把摄像头画面转化成图片，设置编码为base64编码格式数据
                _, enc = cv2.imencode('.jpg', self.pic_data)
                base64_image = base64.b64encode(enc.tobytes())
                tt = detect_face(bytes(base64_image), self.access_token)
                self.signin_label.setText('签到情况：' + tt)
                if '签到成功' in tt:
                    self.is_sigin = False
                    sid = self.data_info["sid"]
                    sign_in = update_student_sign_in(sid)
                    self.sign_in_btn.setEnabled(False)
                    # 判断打卡时间是否满足加分
                    # 获得老师设置的打卡时间
                    post_datetime = get_teacher_time(self.teacher_tid)
                    if post_datetime != 0:
                        # 将日期时间对象转换为时间戳
                        post_datetime = post_datetime[0][0].timestamp()
                        if 0 <= post_datetime - sign_in <= 300:
                            set_students_overall_score(sid, 6)

    def show_camera(self, _):
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        try:
            while True:
                success, self.pic_data = self.camera.read()
                if not success:  # 如果无法获取帧，则跳出循环
                    break
                # 设置新的帧大小（例如，将帧缩放到 1/2 的大小）
                resized_frame = cv2.cvtColor(self.pic_data, cv2.COLOR_BGR2RGB)
                height, width = resized_frame.shape[:2]
                qimg = QImage(resized_frame, width, height, QImage.Format_RGB888)
                qpixmap = QPixmap.fromImage(qimg).scaled(710, 480, Qt.KeepAspectRatio)
                # 显示数据，显示画面
                self.camera_label.setPixmap(qpixmap)
                self.camera_label.setAlignment(Qt.AlignCenter)
                time.sleep(1 / 36)
        except:
            pass

    def show_process(self):
        self.process_btn.setEnabled(False)
        self.message_label1.setText('正在监控本机进程,请勿关闭!')
        thread2 = CreateThreading(2, "Thread-2", 2, self.start_process_monitor, None)
        thread2.start()

    # 开始监控本机进程
    def start_process_monitor(self, _):
        sid = self.data_info["sid"]
        is_ok, is_wrong = monitor_processes(sid)
        if is_ok:
            self.message_label1.setText('监控本机进程完毕!')
            # 判断是否有违规
            if not is_wrong:
                self.total_points += 5
                set_students_overall_score(sid, 5)
        else:
            self.process_btn.setEnabled(True)
            self.message_label1.setText('监控本机进程失败, 请重新操作!')

    def show_browser_history(self):
        self.browser_history_btn.setEnabled(False)
        self.message_label2.setText('正在监控本机浏览记录,请勿关闭!')
        thread3 = CreateThreading(3, "Thread-3", 3, self.start_browser_history_monitor, None)
        thread3.start()

    # 开始监控本机浏览记录
    def start_browser_history_monitor(self, _):
        sid = self.data_info["sid"]
        is_ok, is_wrong = get_browser_history(sid)
        if is_ok:
            self.message_label2.setText('监控本机浏览记录完毕!')
            # 判断是否有违规
            if not is_wrong:
                self.total_points += 5
                set_students_overall_score(sid, 5)
        else:
            self.browser_history_btn.setEnabled(True)
            self.message_label1.setText('监控本机浏览记录失败, 请重新操作!')

    def logout(self):
        self.close_camera()
        # 关闭当前窗口
        self.return_login()

    def close_camera(self):
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            self.camera_label.setPixmap(QPixmap())
            self.sure_btn.hide()
            self.close_btn.hide()
            self.signin_label.hide()

    # 人脸录入
    def get_face(self):
        if self.pic_data is None:
            return
        # 把摄像头画面转化成图片，设置编码为base64编码格式数据
        _, enc = cv2.imencode('.jpg', self.pic_data)
        self.base64_image = base64.b64encode(enc.tobytes())
        # 默认都是aaa组
        self.add_group('aaa')
        self.add_user('aaa', self.data_info['sid'], self.data_info['sname'])

    # 添加组（添加班级）
    def add_group(self, group):
        request_url = c.Group_add_url
        params = {
            "group_id": group
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            return response.json()

    # 添加用户，人脸注册方法
    def add_user(self, groupid, userid, name):
        print("添加用户")
        request_url = c.Add_user_url
        # 请求参数中，需要获取人脸，转换人脸编码，添加的组ID，添加的用户ID，新用户ID的信息
        params = {
            "image": self.base64_image,  # 人脸图片
            "image_type": "BASE64",  # 人脸图片编码
            "group_id": groupid,  # 组ID
            "user_id": userid,  # 新用户ID
            "user_info": 'name:' + name + '\n' + 'class:' + groupid,  # 用户信息
        }
        access_token = self.access_token
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/json'}
        print("发送注册人脸请求！")
        response = requests.post(request_url, data=params, headers=headers)
        print(response)
        if response:
            data = response.json()
            if data['error_code'] == 0:
                QMessageBox.about(self, "人脸注册结果", "人脸注册成功")
            else:
                QMessageBox.about(self, "人脸注册结果", "人脸注册失败" + data['error_msg'])
        else:
            QMessageBox.warning(self, "人脸注册结果", "api接口请求异常")

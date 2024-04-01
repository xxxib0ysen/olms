from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from uihelp import check_process, check_history, check_history_one
from server import *
from datetime import datetime

TEACHER_WIDTH = 1000
TEACHER_HEIGHT = 660


class TeacherView(QWidget):
    def __init__(self, data_info, return_login):
        super().__init__()
        self.return_login = return_login
        self.data_info = data_info

        self.setWindowTitle("教师界面")
        self.setFixedSize(TEACHER_WIDTH, TEACHER_HEIGHT)
        # 获取屏幕大小, 设置居中
        center = QDesktopWidget().availableGeometry().center()
        self.move(center.x() - TEACHER_WIDTH // 2, center.y() - TEACHER_HEIGHT // 2)

        left_frame = QFrame(self)
        left_frame.setGeometry(20, 30, 180, 600)

        name_label = QLabel(f"{self.data_info[1]}老师好.", left_frame)
        name_label.move(10, 10)
        name_label.setFont(QFont('SimSun', 18))

        btn_txt = ('查看学生进程', '学生浏览历史记录', '签到记录', '学生分数', '重置学生分数', '设置打卡时间', '注销')
        btn_command = (
            self.show_processes,
            self.show_history,
            self.show_sign_in,
            self.show_student_score,
            self.reset_student_score,
            self.set_sign_in,
            self.return_login
        )
        for i in range(len(btn_txt)):
            btn = QPushButton(btn_txt[i], left_frame)
            btn.setGeometry(18, i * 70 + 70, 130, 40)
            btn.clicked.connect(btn_command[i])

        # 进程记录界面
        self.processes_view = QGroupBox('操作区域', self)
        self.processes_view.setGeometry(200, 30, 770, 580)
        self.create_processes_view()
        # 浏览器记录界面
        self.history_view = QGroupBox('操作区域', self)
        self.history_view.setGeometry(200, 30, 770, 580)
        self.create_history_view()
        # 打卡记录界面
        self.sign_in_view = QGroupBox('操作区域', self)
        self.sign_in_view.setGeometry(200, 30, 770, 580)
        self.create_sign_in_view()
        # 学生分数排行界面
        self.student_score_view = QGroupBox('操作区域', self)
        self.student_score_view.setGeometry(200, 30, 770, 580)
        self.create_student_score_view()

        self.show_processes()
        self.load_student_history()

    # 创建监控进程的界面
    def create_processes_view(self):
        self.processes_selection_combo = QComboBox(self.processes_view)
        self.processes_selection_combo.setFixedSize(180, 20)
        # 添加进程记录表格
        self.processes_table = QTableWidget()
        self.processes_table.setColumnCount(4)
        self.processes_table.setHorizontalHeaderLabels(["学号", "时间戳", "进程名称", "描述"])
        self.processes_table.setColumnWidth(1, 150)
        self.processes_table.setColumnWidth(2, 250)
        # 布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.processes_selection_combo)
        right_layout.addWidget(self.processes_table)
        self.processes_view.setLayout(right_layout)
        self.processes_selection_combo.currentIndexChanged.connect(self.load_student_processes)

    # 根据选择的学生id获得该学生的进程
    def load_student_processes(self):
        selected_sid = self.processes_selection_combo.currentData()
        if selected_sid:
            # 使用获取的学生ID检索学生的进程记录
            processes = get_student_processes(selected_sid)
            # 清空表格
            self.processes_table.setRowCount(0)
            # 填充表格
            for process in processes:
                row_position = self.processes_table.rowCount()
                self.processes_table.insertRow(row_position)
                self.processes_table.setItem(row_position, 0, QTableWidgetItem(process[0]))
                self.processes_table.setItem(row_position, 1, QTableWidgetItem(process[1]))
                self.processes_table.setItem(row_position, 2, QTableWidgetItem(process[2]))
                self.processes_table.setItem(row_position, 3, QTableWidgetItem(process[3]))

    # 创建监控浏览器记录的界面
    def create_history_view(self):
        self.history_selection_combo = QComboBox(self.history_view)
        self.history_selection_combo.setFixedSize(180, 20)
        # 添加进程记录表格
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(3)
        self.history_table.setHorizontalHeaderLabels(["时间戳", "网页地址", "是否违规"])
        self.history_table.setColumnWidth(0, 150)
        self.history_table.setColumnWidth(1, 350)
        # 布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.history_selection_combo)
        right_layout.addWidget(self.history_table)
        self.history_view.setLayout(right_layout)
        self.history_selection_combo.currentIndexChanged.connect(self.load_student_history)

    def load_student_history(self):
        selected_sid = self.history_selection_combo.currentData()
        if selected_sid:
            # 使用获取的学生ID检索学生的进程记录
            histories = get_student_history(selected_sid)
            # 清空表格
            self.history_table.setRowCount(0)
            # 填充表格
            for history in histories:
                row_position = self.history_table.rowCount()
                self.history_table.insertRow(row_position)
                self.history_table.setItem(row_position, 0, QTableWidgetItem(history[0]))
                _url = history[1]
                self.history_table.setItem(row_position, 1, QTableWidgetItem(_url))
                self.history_table.setItem(row_position, 2, QTableWidgetItem(check_history_one(_url)))

    # 显示监控进程
    def show_processes(self):
        self.processes_view.show()
        self.history_view.hide()
        self.sign_in_view.hide()
        self.student_score_view.hide()
        # 从数据库获取学生信息
        students = get_all_students()
        # 清空下拉框
        self.processes_selection_combo.clear()
        # 填充下拉框
        for student in students:
            sname = student[1]
            sid = student[0]
            self.processes_selection_combo.addItem(sname, sid)

    # 显示监控浏览器记录
    def show_history(self):
        self.history_view.show()
        self.processes_view.hide()
        self.sign_in_view.hide()
        self.student_score_view.hide()
        # 从数据库获取学生信息
        students = get_all_students()
        # 清空下拉框
        self.history_selection_combo.clear()
        # 填充下拉框
        for student in students:
            sname = student[1]
            sid = student[0]
            self.history_selection_combo.addItem(sname, sid)

    def create_sign_in_view(self):
        # 添加进程记录表格
        self.sign_in_table = QTableWidget()
        self.sign_in_table.setColumnCount(4)
        self.sign_in_table.setHorizontalHeaderLabels(["学号", "姓名", "班级", "近期打卡时间"])
        self.sign_in_table.setColumnWidth(3, 150)
        # 布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.sign_in_table)
        self.sign_in_view.setLayout(right_layout)

    # 显示打卡记录
    def show_sign_in(self):
        self.history_view.hide()
        self.processes_view.hide()
        self.sign_in_view.show()
        self.student_score_view.hide()

        students = get_all_students()
        students = [
            (
                p[0], p[1], p[2],
                p[6].strftime('%Y-%m-%d %H:%M:%S') if p[6] is not None else 0
            ) for p in students]
        self.sign_in_table.setRowCount(len(students))
        for row, student in enumerate(students):
            for col, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.sign_in_table.setItem(row, col, item)

    def create_student_score_view(self):
        # 添加进程记录表格
        self.student_score_table = QTableWidget()
        self.student_score_table.setColumnCount(4)
        self.student_score_table.setHorizontalHeaderLabels(["学号", "姓名", "班级", "分数"])
        # 布局
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.student_score_table)
        self.student_score_view.setLayout(right_layout)

    # 重置学生的分数
    def reset_student_score(self):
        is_ok = reset_all_student_score()
        if is_ok:
            QMessageBox.about(self, '提示', '已重置全部学生的分数!')

    # 显示学生分数排行
    def show_student_score(self):
        self.history_view.hide()
        self.processes_view.hide()
        self.sign_in_view.hide()
        self.student_score_view.show()

        students = get_all_students()
        students = [[p[0], p[1], p[3], int(p[5]) / 16] for p in
                    students]

        sorted_list = sorted(students, reverse=True, key=lambda x: x[3])
        self.student_score_table.setRowCount(len(sorted_list))
        for row, student in enumerate(sorted_list):
            for col, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.student_score_table.setItem(row, col, item)

    def set_sign_in(self):
        si_time = SetSignInTime(self.data_info[0])
        si_time.exec_()


# 设置学生打卡时间
class SetSignInTime(QDialog):
    def __init__(self, tid):
        super().__init__()
        self.tid = tid
        self.setWindowTitle("设置打卡时间")
        self.setFixedSize(180, 380)

        now = datetime.now()

        layout = QVBoxLayout()
        year_label = QLabel("年:")
        self.year_input = QLineEdit(self)
        self.year_input.setText(str(now.year))

        month_label = QLabel("月:")
        self.month_input = QLineEdit(self)
        self.month_input.setText(str(now.month))

        day_label = QLabel("日:")
        self.day_input = QLineEdit(self)
        self.day_input.setText(str(now.day))

        hour_label = QLabel("时:")
        self.hour_input = QLineEdit(self)
        self.hour_input.setText(str(now.hour))

        minute_label = QLabel("分:")
        self.minute_input = QLineEdit(self)
        self.minute_input.setText(str(now.minute))

        second_label = QLabel("秒")
        self.second_input = QLineEdit(self)
        self.second_input.setText(str(now.second))

        save_button = QPushButton("设置", self)
        save_button.clicked.connect(self.set_time)

        layout.addWidget(year_label)
        layout.addWidget(self.year_input)
        layout.addWidget(month_label)
        layout.addWidget(self.month_input)
        layout.addWidget(day_label)
        layout.addWidget(self.day_input)
        layout.addWidget(hour_label)
        layout.addWidget(self.hour_input)
        layout.addWidget(minute_label)
        layout.addWidget(self.minute_input)
        layout.addWidget(second_label)
        layout.addWidget(self.second_input)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def set_time(self):
        set_state = set_teacher_sign_in(
            self.tid,
            f"{self.year_input.text()}-{self.month_input.text()}-{self.day_input.text()} {self.hour_input.text()}:{self.minute_input.text()}:{self.second_input.text()}"
        )
        if set_state:
            QMessageBox.about(self, "成功", "设置成功打卡时间成功!")
            self.close()

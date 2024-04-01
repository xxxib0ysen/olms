from PyQt5.QtWidgets import *
from server import search_students, filter_students


class StudentRight(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        # 学生数据
        self.students_data = None
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 30, 770, 580)
        layout = QVBoxLayout()
        search_label = QLabel("搜索学生:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_students)
        layout.addWidget(search_label)
        layout.addWidget(self.search_input)

        filter_label = QLabel("筛选班级:")
        self.filter_input = QLineEdit()
        self.filter_input.textChanged.connect(self.filter_students)
        layout.addWidget(filter_label)
        layout.addWidget(self.filter_input)

        self.student_table = QTableWidget()
        self.student_table.setColumnCount(6)
        self.student_table.setHorizontalHeaderLabels(["学号", "姓名", "班级", "密码", "课程", "总分"])
        layout.addWidget(self.student_table)
        self.setLayout(layout)

    # 查找与姓名相符的数据
    def search_students(self):
        if self.students_data is None:
            return
        keyword = self.search_input.text()
        if keyword:
            students = search_students(keyword)
            self.update_data(students)

    # 查找与班级相符的数据
    def filter_students(self):
        if self.students_data is None:
            return
        sclass = self.filter_input.text()
        if sclass:
            students = filter_students(sclass)
            self.update_data(students)

    # 更新数据
    def update_data(self, students):
        self.students_data = students
        self.student_table.setRowCount(len(students))
        for row, student in enumerate(students):
            for col, data in enumerate(student):
                item = QTableWidgetItem(str(data))
                self.student_table.setItem(row, col, item)

    # 获得选中的行的数据
    def get_row_data(self):
        selected_row = self.student_table.currentRow()
        if selected_row >= 0:
            student_info = {
                "sid": self.student_table.item(selected_row, 0).text(),
                "sname": self.student_table.item(selected_row, 1).text(),
                "password": self.student_table.item(selected_row, 2).text(),
                "sclass": self.student_table.item(selected_row, 3).text(),
                "cname": self.student_table.item(selected_row, 4).text(),
                "overall_score": self.student_table.item(selected_row, 5).text()
            }
            return student_info
        return None

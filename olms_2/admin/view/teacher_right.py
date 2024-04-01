from PyQt5.QtWidgets import *
from server import search_teachers


class TeacherRight(QGroupBox):
    def __init__(self, *__args):
        super().__init__(*__args)
        # 老师数据
        self.teacher_data = None
        self.init_ui()

    def init_ui(self):
        self.setGeometry(200, 30, 770, 580)
        layout = QVBoxLayout()
        search_label = QLabel("搜索教师:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_teachers)
        layout.addWidget(search_label)
        layout.addWidget(self.search_input)

        self.teacher_table = QTableWidget()
        self.teacher_table.setColumnCount(4)
        self.teacher_table.setHorizontalHeaderLabels(["教工号", "姓名", "密码", "课程"])
        self.teacher_table.setColumnWidth(3, 140)
        layout.addWidget(self.teacher_table)

        self.setLayout(layout)

    def search_teachers(self):
        if self.teacher_data is None:
            return
        keyword = self.search_input.text()
        if keyword:
            teachers = search_teachers(keyword)
            self.update_data(teachers)

    # 更新数据
    def update_data(self, teachers):
        self.teacher_data = teachers
        self.teacher_table.setRowCount(len(teachers))
        for row, teacher in enumerate(teachers):
            for col, data in enumerate(teacher):
                item = QTableWidgetItem(str(data))
                self.teacher_table.setItem(row, col, item)


    # 获得选中的行的数据
    def get_row_data(self):
        selected_row = self.teacher_table.currentRow()
        if selected_row >= 0:
            teacher_info = {
                "tid": self.teacher_table.item(selected_row, 0).text(),
                "tname": self.teacher_table.item(selected_row, 1).text(),
                "password": self.teacher_table.item(selected_row,2).text(),
                "cname":self.teacher_table.item(selected_row,3).text()
            }
            return teacher_info
        return None

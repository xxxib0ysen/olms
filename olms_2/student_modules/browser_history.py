import os
import sqlite3
from datetime import datetime
from server import get_database_connection, del_student_browser_history
from uihelp import check_history


def get_browser_history(sid):
    try:
        os.system("taskkill /f /im chrome.exe")
    except:
        print("Chrome已经关闭")

    # 定义数据库文件路径
    data_path = os.path.expanduser('~') + r"\AppData\Local\Google\Chrome\User Data\Default"
    history_db = os.path.join(data_path, 'History')

    # 连接数据库
    c = sqlite3.connect(history_db)
    cursor = c.cursor()

    # 查询最近100条浏览记录
    select_statement = "SELECT urls.url, urls.title, visits.visit_time FROM urls, visits WHERE urls.id = visits.url ORDER BY visits.visit_time DESC LIMIT 100"
    cursor.execute(select_statement)

    # 获取查询结果
    results = cursor.fetchall()
    # 解析浏览历史记录
    history_records = []
    # 查看是否有违规
    is_wrong = False
    del_student_browser_history(sid)
    for row in results:
        url = row[0]
        # 判断是否有违规
        if not is_wrong:
            is_wrong = check_history(url)
        timestamp = row[2] / 1000000
        date_time = datetime.fromtimestamp(timestamp)
        history_records.append(f"{date_time} - {url}")
        print(f"Inserting browser history for student {sid}")
        insert_browser_history(sid, date_time, url)
    return True, is_wrong


def insert_browser_history(sid, access_time, url):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # 插入浏览历史记录
            insert_statement = "INSERT INTO browser_history (sid, access_time, url) VALUES (%s, %s, %s)"
            cursor.execute(insert_statement, (sid, access_time, url))
            connection.commit()
        print(f"Browser history inserted successfully for student {sid}")
    except Exception as e:
        print("Error inserting browser history:", e)

# def show_browser_history():
#     history_records = get_browser_history()
#
#     # 创建一个窗口来显示浏览历史记录
#     history_window = QDialog()
#     history_window.setWindowTitle("浏览历史记录")
#     history_window.setGeometry(200, 200, 800, 600)
#
#     # 创建一个文本框来显示浏览历史记录内容
#     history_text = QTextEdit(history_window)
#     history_text.setPlainText("浏览历史记录：\n" + "\n".join(history_records))
#
#     # 将文本框添加到窗口中
#     layout = QVBoxLayout()
#     layout.addWidget(history_text)
#     history_window.setLayout(layout)
#
#     # 显示浏览历史记录窗口
#     history_window.exec_()

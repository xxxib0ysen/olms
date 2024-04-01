
import logging
import psutil
import time
from server import *
from uihelp import check_process
import datetime

# 配置日志记录
logging.basicConfig(filename='process_monitor.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

monitor_interval = 10


def monitor_processes(sid):
    # total_score = 0
    # process_score = 10
    del_student_process(sid)
    # 查看是否有违规
    is_wrong = False
    while True:
        try:
            # 获取当前时间
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            # 获取所有正在运行的进程
            running_processes = [proc.info for proc in psutil.process_iter(attrs=['pid', 'name'])]
            time.sleep(monitor_interval)

            connection = get_database_connection()
            with connection.cursor() as cursor:
                for process in running_processes:
                    process_name = process['name']
                    # 判断是否有违规
                    if not is_wrong:
                        is_wrong = check_process(process_name)
                    process_description = "正在运行的进程"
                    sql = "INSERT INTO processes (sid, timestamp, process_name, process_description) VALUES (%s, %s, %s, %s)"
                    cursor.execute(sql, (sid, current_time, process_name, process_description))

                    # if process_name == "QQMusic.exe":
                    #     process_score -= 1
                    #     total_score += process_score
                # update_student_score(sid, process_score, total_score)
                cutoff_time = datetime.datetime.now() - datetime.timedelta(days=1)  # 保留一天的记录
                sql = "DELETE FROM processes WHERE timestamp < %s"
                cursor.execute(sql, (cutoff_time,))
                connection.commit()
                return True, is_wrong
        except Exception as e:
            logging.error("Error: %s", e)
        return False, None
        # else:
        #     logging.info("Score updated for sid: %s, process_score: %s, total_score: %s", sid, process_score,
        #                  total_score)

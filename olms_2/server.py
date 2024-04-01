import hashlib
import logging
import time
from datetime import datetime
from sshtunnel import SSHTunnelForwarder
import pymysql


def get_database_connection():
    server = SSHTunnelForwarder(
        ssh_address_or_host=('47.116.126.88', 22),
        ssh_username='root',
        ssh_password='skb020826@',
        remote_bind_address=('localhost', 3306)
    )

    server.start()

    con = pymysql.connect(host='127.0.0.1',
                          port=server.local_bind_port,
                          user='olms',
                          password='olms',
                          db='olms')

    return con


# 获取全部学生的数据
def get_all_students():
    # 从数据库获取所有学生信息
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM students")
            students = cursor.fetchall()
            return students
    except Exception as e:
        print("Error:", e)


# 删除某个学生的全部进程
def del_student_process(sid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM processes WHERE sid = %s"
            cursor.execute(sql, (sid,))
            connection.commit()
    except Exception as e:
        print("Error:", e)


# 删除某个学生的全部浏览记录
def del_student_browser_history(sid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM browser_history WHERE sid = %s"
            cursor.execute(sql, (sid,))
            connection.commit()
    except Exception as e:
        print("Error:", e)


# 设置全部学生的分数
def reset_all_student_score():
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE students SET overall_score = %s"
            cursor.execute(sql, (0,))
            connection.commit()
            return True
    except Exception as e:
        print("Error:", e)
    return False


# 设置学生扣分值
def set_students_deduction(sid, deduction):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE students SET score2 = %s WHERE sid = %s"
            cursor.execute(sql, (deduction, sid))
            connection.commit()
    except Exception as e:
        print("Error:", e)


# 增加学生学分
def set_students_overall_score(sid, score):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT overall_score FROM students WHERE sid = %s"
            cursor.execute(sql, (sid,))
            result = cursor.fetchone()
            if result:
                overall_score = result[0]
                overall_score += score
            sql = "UPDATE students SET overall_score = %s WHERE sid = %s"
            cursor.execute(sql, (overall_score, sid))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def verify_student(username, password):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # 查询学生表，验证用户名和密码
            sql = "SELECT * FROM students WHERE sname = %s AND password = %s"
            cursor.execute(sql, (username, password))
            student = cursor.fetchone()
            return student is not None
    except Exception as e:
        print("Error:", e)
        return False


def verify_teacher(username, password):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # 查询教师表，验证用户名和密码
            sql = "SELECT * FROM teachers WHERE tid = %s AND password = %s"
            cursor.execute(sql, (username, password))
            teacher = cursor.fetchone()
            return teacher
    except Exception as e:
        print("Error:", e)
    return None


def verify_admin(username, password):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # 查询数据库中是否存在匹配的管理员记录
            sql = "SELECT admin_id, password FROM Admins WHERE username = %s"
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                # 从数据库中获取哈希密码
                db_password_hash = result[1]
                # SHA-256哈希算法
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                if db_password_hash == password_hash:
                    return result[0]
    except Exception as e:
        print("Error:", e)

    return None


def get_student_processes(sid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # 编写 SQL 查询语句，获取学生的进程信息
            sql = "SELECT sid, timestamp, process_name, process_description FROM processes WHERE sid = %s"
            cursor.execute(sql, (sid,))
            processes = cursor.fetchall()
            if processes is not None:
                formatted_processes = [(p[0], p[1].strftime('%Y-%m-%d %H:%M:%S'), p[2], p[3]) for p in processes]
                return formatted_processes
            else:
                return []

    except Exception as e:
        print("Error:", e)
        return None


def get_student_history(sid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            # 编写 SQL 查询语句，获取学生的进程信息
            sql = "SELECT * FROM browser_history WHERE sid = %s"
            cursor.execute(sql, (sid,))
            history = cursor.fetchall()
            if history is not None:
                formatted_history = [(p[2].strftime('%Y-%m-%d %H:%M:%S'), p[3]) for p in history]
                return formatted_history
            else:
                return []

    except Exception as e:
        print("Error:", e)
        return None


def update_student_score(sid, process_score, total_score):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE scores SET process_score = %s,total_score = %s WHERE sid = %s"
            cursor.execute(sql, (process_score, total_score, sid))
            connection.commit()
    except Exception as e:
        logging.error("Error while updating score: %s", e)


# 更新打卡时间
def update_student_sign_in(sid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            # 获取当前时间戳
            timestamp = datetime.now().timestamp()
            sql = "UPDATE students SET datetime = %s WHERE sid = %s"
            cursor.execute(sql, (current_time, sid))
            connection.commit()
            return timestamp
    except Exception as e:
        logging.error("Error while updating score: %s", e)
    return None


# 教师设置打卡时间
def set_teacher_sign_in(tid, post_datetime):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE teachers SET post_datetime = %s WHERE tid = %s"
            cursor.execute(sql, (post_datetime, str(tid)))
            connection.commit()
            return True
    except Exception as e:
        logging.error("Error while updating score: %s", e)
    return False


def student_login(username, password):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM students WHERE sid = %s AND password = %s"
            cursor.execute(sql, (username, password))
            result = cursor.fetchone()
            print()

            if result:
                student_info = {
                    "sid": result[0],
                    "sname": result[1],
                    "password": result[2],
                    "sclass": result[3],
                    "cname": result[4],
                    "overall_score": result[5],
                    "deduction": result[7]
                }
                return student_info
    except Exception as e:
        print("Error:", e)
    return None


""" 管理员数据库操作 """


def add_student(student):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO students (sid,sname,password,sclass,cname,overall_score) VALUES (%s,%s,%s, %s, %s, %s)"
            cursor.execute(sql, (
                student.sid, student.sname, student.password, student.sclass, student.cname, student.overall_score))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def get_all_students_by_sid():
    # 从数据库获取所有学生信息
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM students ORDER BY sid")
            students = cursor.fetchall()
            return students
    except Exception as e:
        print("Error:", e)


def search_students(keyword):
    # 根据关键词搜索学生
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM students WHERE sname LIKE %s"
            cursor.execute(sql, (f"%{keyword}%",))
            students = cursor.fetchall()
            return students
    except Exception as e:
        print("Error:", e)


def filter_students(sclass):
    # 根据班级序号筛选学生
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM students WHERE sclass = %s"
            cursor.execute(sql, (sclass,))
            students = cursor.fetchall()
            return students
    except Exception as e:
        print("Error:", e)


def edit_student(sid, edited_student_info):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE students SET " \
                  "sid = %s," \
                  "sname = %s," \
                  "password = %s," \
                  "sclass = %s," \
                  "cname = %s,overall_score = %s WHERE sid = %s"
            cursor.execute(sql, (
                edited_student_info["sid"],
                edited_student_info["sname"],
                edited_student_info["password"],
                edited_student_info["sclass"],
                edited_student_info["cname"],
                edited_student_info["overall_score"],
                sid
            ))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def delete_student(sid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM students WHERE sid = %s"
            cursor.execute(sql, (sid,))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def search_teachers(keyword):
    # 根据关键词搜索教师
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teachers WHERE tname LIKE %s"
            cursor.execute(sql, (f"%{keyword}%",))
            teachers = cursor.fetchall()
            return teachers
    except Exception as e:
        print("Error:", e)


def get_all_teachers():
    # 从数据库获取所有教师信息
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM teachers ORDER BY tid")
            teachers = cursor.fetchall()
            return teachers
    except Exception as e:
        print("Error:", e)


def add_teacher(teacher):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "INSERT INTO teachers (tid,tname, password,cname) VALUES (%s,%s, %s, %s)"
            cursor.execute(sql, (teacher.tid, teacher.tname, teacher.password, teacher.cname))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def edit_teacher(tid, edited_teacher_info):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "UPDATE teachers SET tid = %s,tname = %s, password = %s, cname = %s WHERE tid = %s"
            cursor.execute(sql, (
                edited_teacher_info["tid"],
                edited_teacher_info["tname"],
                edited_teacher_info["password"],
                edited_teacher_info["cname"],
                tid
            ))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def delete_teacher(tid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "DELETE FROM teachers WHERE tid = %s"
            cursor.execute(sql, (tid,))
            connection.commit()
    except Exception as e:
        print("Error:", e)


def get_teacher_time(tid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT post_datetime FROM teachers WHERE tid = %s"
            cursor.execute(sql, (tid,))
            post_datetime = cursor.fetchall()
            return post_datetime
    except Exception as e:
        print("Error:", e)
    return 0


def get_teacher_by_tid(tid):
    try:
        connection = get_database_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM teachers WHERE tid = %s"
            cursor.execute(sql, (tid,))
            post_datetime = cursor.fetchall()
            return post_datetime
    except Exception as e:
        print("Error:", e)
    return 0

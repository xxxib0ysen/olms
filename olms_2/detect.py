"""
代码功能：人脸检测与识别功能函数
"""

import sqlite3
import traceback
import requests
from PyQt5.QtCore import QThread, pyqtSignal, QDateTime
import config as c


# 进行人脸检测
def detect_face(base64_image, access_token):
    print("人脸检测")
    # 发送请求的地址
    request_url = c.Detect_face_url
    # 请求参数是一个字典，在字典中存储了，百度AI要识别的图片信息，要识别的属性内容
    params = {"image": base64_image,  # 图片信息字符串
              "image_type": "BASE64",  # 图片信息的格式
              "face_field": "gender,age,beauty,expression,face_shape,glasses,emotion,mask",
              # 请求识别人脸的属性，各个属性在字符串中用','逗号隔开
              "max_face_num": 10,
              }
    # 访问令牌
    # 把请求地址和访问令牌组成可用的网络请求地址
    request_url = request_url + "?access_token=" + access_token
    # 参数，设置请求的格式体
    headers = {'content-type': 'application/json'}
    # 发送网络post请求，请求百度AI进行人脸检测，返回检测结果
    # 发送网络请求，就会等待一段时间，程序就在这里阻塞执行
    response = requests.post(request_url, data=params, headers=headers)
    print(response)
    if response:
        data = response.json()
        print(data)
        if data['error_code'] != 0:
            return '签到失败'
        if data['result']['face_num'] > 0:
            return face_search(base64_image, access_token)


# 人脸识别检测，只识别一个人
def face_search(base64_image, access_token):
    print("人脸识别搜索")
    request_url = c.Search_face_url
    params = {
        "image": base64_image,
        "image_type": "BASE64",
        "group_id_list": 'aaa'  # 从哪些组中进行人脸识别
    }
    request_url = request_url + "?access_token=" + access_token
    headers = {'content-type': 'application/json'}
    response = requests.post(request_url, data=params, headers=headers)
    print(response)
    if response:
        data = response.json()
        print(data)
        if data['error_code'] == 0:
            if data['result']['user_list'][0]['score'] > 90:
                return f"{data['result']['user_list'][0]['user_id']}签到成功"
            else:
                return "未注册人脸信息"
        else:
            return "没有找到匹配用户"


# 添加签到数据到数据库中
def insert_stu(self, user_id, name, group1, time):
    print("保存签到数据")
    conn = sqlite3.connect('db/student.db')
    c = conn.cursor()
    data = (user_id, name, group1, time)
    sql = "select * from student where id = '{}'".format(user_id)
    c.execute(sql)
    result = c.fetchall()
    if len(result) != 0:
        sql = "update student set datatime = '" + time + "' where id='" + user_id + "'"
        c.execute(sql)
        print("更新签到信息成功！")
    else:
        sql = "INSERT INTO student(id, name, class, datatime) VALUES(?, ?, ?, ?)"
        c.execute(sql, data)
        print("保存签到信息成功！")

    conn.commit()
    conn.close()

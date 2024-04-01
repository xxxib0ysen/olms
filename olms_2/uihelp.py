import threading


# 开启摄像头进行实时监控，是一种多线程方法
# threading模块：提供更高级和安全的线程管理
class CreateThreading(threading.Thread):
    def __init__(self, threadID, name, counter, call_back, values):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.call_back = call_back
        self.values = values

    # 当使用Threading模块创建线程时，先建立一个线程类CreateThreading，并继承threading.Thread
    # 然后重写run
    # 重构，重写父类方法
    def run(self):
        self.call_back(self.values)


# 违规的进程关键字
PROCESS_TXT = (
    "QQMusic.exe", "QQ.exe", "WeChat.exe"
)

# 违规的浏览器记录url关键词
HISTORY_TXT = (
    "www.qq.com", "www.youku.com", "www.toolmao.com"
)


# # 判断进程是否违规
# def check_process(process_list):
#     # 总扣分
#     count = 0
#     for t in PROCESS_TXT:
#         for p in process_list:
#             if t in p[2]:
#                 count += 1
#     return count
# 判断进程是否违规
def check_process(process):
    for t in PROCESS_TXT:
        if t in process:
            return True
    return False


# 判断 浏览器记录是否违规
def check_history(history):
    for t in HISTORY_TXT:
        if t in history:
            return True
    return False


# # 判断 浏览器记录是否违规
# def check_history(history_list):
#     # 总扣分
#     count = 0
#     for t in HISTORY_TXT:
#         for h in history_list:
#             if t in h[1]:
#                 count += 1
#     return count

# 判断 浏览器记录是否违规
def check_history_one(history):
    for t in HISTORY_TXT:
        if t in history:
            return '是'
    return '否'

# -*- coding: utf-8 -*-
import time  # 导入包
import queue  # 导入包
import socket  # 导入包
import threading  # 导入包


class Client(object):

    def __init__(self, addr="127.0.0.1", port=8024):  # addr：客户端ip地址，默认为回环地址；port：客户端使用的端口号

        self.addr = addr  # ip地址
        self.askIP = ''
        self.port = port  # 端口
        self.username = None  # 默认用户名
        self.queue = queue.Queue()  # 队列
        self.status = True  # 用户状态
        self.loginStatus = False  # 登录状态
        self.loginBack = None  # 登录返回选择
        self.registerBack = None  # 退出
        self.userlist = []  # 用户列表
        self.usermsg = []  #
        self.sysmsg = []  #

        # 建立TCP socket对象，使用给定的地址族(socket.AF_INET表示使用IPv4)、套接字类型(socket.AF_INET表示TCP套接字类型)、协议编号(默认为0)来创建套接字
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:  # 连接异常捕获
            self.s.connect((self.addr, self.port))  # 连接IP和端口
            self.s.settimeout(0.1)
        except socket.error as err:
            if err.errno == 10061:  # 报错端口
                print("Connection with {addr}:{port} refused".format(addr=self.addr, port=self.port))
                return
            else:
                raise
        else:
            print("initial successfully!")  # 成功连接提示

    def getClientIPFromName(self, name):
        """
        获取客户端IP地址
        """
        self.s.send(str({"type": "askIP",
                         "name": name}).encode())
        time.sleep(1)
        return self.askIP

    def register(self, name, password):
        """
        注册账号
        name:要注册的账号
        password:密码
        """
        self.s.send(str({"type": "register",
                         "name": name,
                         "password": password,
                         "time": time.time()}).encode())  # 信息发送格式

    def login(self, name, password):
        """
        使用账号密码登录
        name: 用户账号
        password: 密码
        """
        self.username = name
        self.s.send(str({"type": "login",
                         "name": name,
                         "password": password,
                         "time": time.time()}).encode())  # 登录记录格式

    def send_Msg(self, msg_send, destname, type="msg", fname=""):
        """
        发送消息
        msg_send: 要发送的消息
        destname: 发送对象的用户名
        type：消息的类型，如表情、文字、语音等，默认为文字
        """
        a = str({"type": "usermsg",
                 "mtype": type,
                 "destname": destname,
                 "fname": fname,
                 "name": self.username,
                 "time": time.time(),
                 "msg": msg_send}).encode()  # 协议发送信息格式
        constlen = len(a)

        mes = str({"type": "msglen",
                   "destname": destname,
                   "name": self.username,
                   "len": constlen}).encode()  # 记录格式
        self.s.send(mes)
        time.sleep(0.01)  # 时间精度
        self.s.send(a)
        print("new information sent by TCP")  # 协议说明

    def receive_msg(self):
        """
        接收消息
        """
        while self.status:
            try:
                msg_recv = eval(self.s.recv(1024))
            except socket.timeout:
                pass
            except:
                print("other error")
            else:
                if msg_recv["type"] == "answerIP":
                    self.askIP = msg_recv["IP"]
                elif msg_recv["type"] == "msglen":
                    self.queue.put(msg_recv)
                    length = msg_recv["len"]
                    mlen = 0
                    while msg_recv["type"] != "usermsg":
                        try:
                            msg_recv = "".encode()

                            while mlen < length:
                                try:
                                    msg_recv_ = self.s.recv(length)
                                    msg_recv = msg_recv + msg_recv_
                                    mlen = mlen + len(msg_recv_)
                                    msg_recv = eval(msg_recv)
                                    time.sleep(length * 0.00000001)
                                except socket.timeout:
                                    continue
                                except SyntaxError:
                                    continue
                                else:
                                    break
                        except socket.timeout:
                            continue
                        except socket.error as err:
                            if err.errno == 10053:
                                print("Software caused connection abort ")  # 提示信息
                                self.status = False
                    self.queue.put(msg_recv)  #
                    print("收到新消息")  # 提示信息
                else:
                    self.queue.put(msg_recv)  #
                    print("收到新消息")  # 提示信息

    def handle_msg(self):
        """
        处理收到的消息
        """
        while True:
            msg = self.queue.get()

            if msg["type"] == "loginBack":
                self.loginBack = msg
                if msg["info"] == "loginSucc":
                    self.userlist = msg["userlist"]
            elif msg["type"] == "rgtrBack":
                self.registerBack = msg
            elif msg["type"] == "usermsg":
                self.usermsg.append(msg)
            elif msg["type"] == "sysmsg":
                self.sysmsg.append(msg)

    def main(self):
        receive_func = threading.Thread(target=self.receive_msg)
        handle_func = threading.Thread(target=self.handle_msg)
        receive_func.start()
        handle_func.start()

    def __del__(self):
        self.s.close()


if __name__ == '__main__':
    client = Client(addr="127.0.0.1", port=8024)  # 默认IP及端口号，不需要改动，因为调用时不会执行main函数
    client.main()
    client.login("0", "0")

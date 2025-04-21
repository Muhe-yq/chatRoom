# -*- coding: utf-8 -*-
import time
import queue
import socket
import sqlite3
import threading


class Server(object):
    def __init__(self, addr="127.0.0.1", port=8024):  # addr：服务器ip地址；port：服务器使用的端口号
        self.addr = addr  # IP地址
        self.port = port  # 端口

        self.connections = []  # 连接状态
        self.name = {}  # 用户名
        self.nametoconn = {}  #
        self.userlist = []  # 用户列表
        self.queue = queue.Queue()

        self.dbconn = sqlite3.connect('UserInfo.db')  # 连接数据库
        self.dbcursor = self.dbconn.cursor()
        self.dbcursor.execute('''CREATE TABLE IF NOT EXISTS USERINFO
               (USERNAME    VARCHAR(20) PRIMARY KEY     NOT NULL,
                PASSWORD    VARCHAR(20)                 NOT NULL,
                LASTLOGIN   VARCHAR(50)                 NOT NULL,
                STATUS      INT(1)                      NOT NULL
                               );''')  # 参数
        self.dbcursor.execute("UPDATE USERINFO set STATUS = 0")  #
        self.dbconn.commit()  # 数据库连接

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP Socket
        self.s.bind((self.addr, self.port))  # 将套接字绑定到地址
        print("Initial Successfully!")  # 连接成功

    def portlisten(self):
        """
        侦听连接
        """
        self.s.listen(10)  # 监听TCP传入连接
        while True:
            conn, address = self.s.accept()  # 接受TCP连接并返回（conn,address）
            conn.settimeout(0.000001)  # 时间精度
            add = address[0] + ":" + str(address[1])
            print("address is " + address[0] + " the port is " + str(address[1]))  # 显示信息及格式
            self.connections.append(conn)  # 存储已建立的连接
            self.name[add] = add

    def msg_queue(self):
        """
        创建消息队列
        """
        while True:
            for c in self.connections:
                try:  # 错误检验
                    msg_recv = eval(c.recv(1024))
                    print("收到以下消息：")  # 输出文字
                    print(msg_recv)  # 输出函数结果
                except socket.timeout:
                    continue
                except SyntaxError:
                    pass
                except socket.error as err:  # 10053 – Software caused connection abort //10054 – connection reset by peer
                    if err.errno == 10053 or err.errno == 10054:
                        self.remove_connection(c)
                except ValueError:
                    pass
                else:
                    addr = c.getpeername()
                    self.queue.put((addr, msg_recv, c))
                    if msg_recv["type"] == "msglen":
                        length = msg_recv["len"]
                        time.sleep(length * 0.0000001)
                        mlen = 0
                        while msg_recv["type"] != "usermsg":
                            try:
                                msg_recv = "".encode()
                                while mlen < length:  # 直至收到事先给予的长度才停下
                                    try:
                                        msg_recv_ = c.recv(length)
                                        print(msg_recv_)
                                        msg_recv = msg_recv + msg_recv_
                                        mlen = mlen + len(msg_recv_)
                                        msg_recv = eval(msg_recv)
                                        time.sleep(length * 0.00000001)  # 时间精度
                                    except socket.timeout:
                                        continue
                                    except SyntaxError:
                                        continue
                                    else:
                                        break
                            except socket.timeout:
                                continue
                            except socket.error as err:  # 10053 – Software caused connection abort //10054 – connection reset by peer
                                if err.errno == 10053 or err.errno == 10054:
                                    self.remove_connection(c)
                            except ValueError:
                                pass
                        self.queue.put((addr, msg_recv, c))

    def login(self, msg_recv, addr):
        """
        登录到服务器
        msg_recv：收到的消息
        addr：用户地址
        """
        Username = msg_recv["name"]  # 登录名
        self.dbcursor.execute(
            "SELECT * from USERINFO where USERNAME = \"{Uname}\"".format(Uname=Username))  # 通过用户名检索出对应的用户实体
        Userinfo = self.dbcursor.fetchone()  # 查看数据库

        if Userinfo == None or Userinfo[1] != msg_recv["password"]:  # 用户不存在或密码错误
            flag = False
            back = {"type": "loginBack",
                    "info": "loginFail"}  # 返回提示信息
        elif Userinfo[3] == 1:
            flag = False
            back = {"type": "loginBack",
                    "info": "loginAlready"}  # 返回提示信息
        else:
            flag = True
            address = addr[0] + ":" + str(addr[1])  # 接受地址信息

            self.name[address] = Username
            self.userlist.append(Username)
            self.lastlogintime = Userinfo[2]
            self.dbcursor.execute(
                "UPDATE USERINFO set LASTLOGIN = {logintime}, STATUS = 1 where USERNAME=\"{Uname}\"".format(
                    logintime=time.time(),  # time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(msg_recv["time"])),
                    Uname=Username))
            self.dbconn.commit()
            back = {"type": "loginBack",
                    "info": "loginSucc",
                    "userlist": self.userlist}  # 记录信息
            forward = {"type": "sysmsg",
                       "info": "userlogin",
                       "name": Username,
                       "time": time.time(),
                       "msg": "{name} 已进入聊天室!".format(name=Username)}  # 记录信息

        for c in self.connections:
            c_addr = c.getpeername()
            if c_addr == addr:
                if flag:
                    self.nametoconn[self.name[address]] = c
                c.send(str(back).encode())
            elif flag:
                c.send(str(forward).encode())

    def register(self, msg_recv, addr):
        """
        注册账号
        msg_recv：收到的消息
        addr：用户地址
        """
        Username = msg_recv["name"]
        self.dbcursor.execute(
            "SELECT * from USERINFO where USERNAME=\"{Uname}\"".format(Uname=Username))  # 通过用户名检索出对应的用户实体
        Userinfo = self.dbcursor.fetchone()

        if Userinfo == None:  # 用户不存在
            self.dbcursor.execute("INSERT INTO USERINFO (USERNAME, PASSWORD, LASTLOGIN, STATUS) \
            VALUES (\"{Uname}\", \"{Passwd}\", \"Never\", 0)".format(Uname=Username, Passwd=msg_recv["password"]))
            self.dbconn.commit()  # 连接数据库

            self.name[addr] = Username  # 用户名
            self.lastlogintime = "Never"  # 最后登录时间
            back = {"type": "rgtrBack",
                    "info": "rgtrSucc"}
        else:
            back = {"type": "rgtrBack",
                    "info": "rgtrFail"}

        for c in self.connections:
            c_addr = c.getpeername()
            if c_addr == addr:
                c.send(str(back).encode())

    def remove_connection(self, conn):
        '''
        用户退出，删除连接并广播
        conn：要从表中删除的连接
        '''
        try:
            self.connections.remove(conn)
        except ValueError:
            pass
        address = conn.getpeername()
        addr = address[0] + ":" + str(address[1])
        Username = self.name[addr]
        self.name.pop(addr)  # 从用户列表中移除
        if Username in self.userlist:
            self.userlist.remove(Username)  # 移除用户名
        dbconn1 = sqlite3.connect('userinfo.db')  # 连接数据库文件
        dbcursor1 = dbconn1.cursor()
        dbcursor1.execute("UPDATE USERINFO set STATUS=0 where USERNAME=\"{Uname}\"".format(Uname=Username))
        dbconn1.commit()  # 连接数据库
        back = {"type": "sysmsg",
                "info": "userexit",
                "name": Username,
                "time": time.time(),
                "msg": "{name} 离开了聊天室！".format(name=Username)}
        for c in self.connections:
            c.send(str(back).encode())

    def msg_forward(self, msg_forward):
        """
        消息转发
        msg_forward：需要转发的消息
        """
        # address = addr[0] + ":" + str(addr[1])
        if msg_forward["destname"] == "all":
            for c in self.connections:
                print("new information forward to group")
                c.send(str(msg_forward).encode())
        else:
            self.nametoconn[msg_forward["destname"]].send(str(msg_forward).encode())
            self.nametoconn[msg_forward["name"]].send(str(msg_forward).encode())
            print("new information forward to " + msg_forward["destname"])

    def answerIP(self, msg, addr):
        """
        获取IP以便创建视频
        """
        name = msg["name"]
        c = self.nametoconn[name]
        IP = c.getpeername()[0]
        address = addr[0] + ":" + str(addr[1])
        self.nametoconn[self.name[address]].send(str({"type": "answerIP",
                                                      "IP": IP}).encode())

    def run(self):
        """
        启动服务器
        """
        # 创建两个线程，分别为监听连接请求和信息队列
        func1 = threading.Thread(target=self.portlisten)
        func2 = threading.Thread(target=self.msg_queue)
        func1.start()
        func2.start()
        while True:
            time.sleep(0.001)
            if self.queue.empty():
                continue
            addr, msg, conn = self.queue.get()
            if msg["type"] == "login":
                self.login(msg, addr)
            elif msg["type"] in ("usermsg", "msglen"):
                self.msg_forward(msg)
            elif msg["type"] == "register":
                self.register(msg, addr)
            elif msg["type"] == "askIP":
                self.answerIP(msg, addr)


    def __del__(self):
        self.s.close()
        self.dbconn.close()


if __name__ == '__main__':
    host = socket.gethostname()
    addrIP = socket.gethostbyname(host)
    print(host, addrIP)
    server = Server(addr=addrIP, port=8024)  # 服务器地址及端口
    server.run()

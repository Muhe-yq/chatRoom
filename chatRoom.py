import os
import sys
import time
import socket
import base64
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, QtWidgets
from TCPClient import Client
from audio import *
from vchat import *
from achat import *
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--level', type=int, default=1)
parser.add_argument('-v', '--version', type=int, default=4)

args = parser.parse_args()

VERSION = args.version
LEVEL = args.level


class loginWindow(QtWidgets.QDialog):
    """
    登陆界面
    """
    def __init__(self):
        super(loginWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        ###登录窗口相关设置
        self.setObjectName("LoginWindow")
        self.setStyleSheet("#LoginWindow{border-image:url(./image/loginUI/login_background.png);}")  # 选择背景所用的图片
        self.setWindowTitle("欢迎来到马踏祥云队的局域网聊天室！")  # 聊天悬浮窗口名称
        self.resize(600, 600)  # 设定大小

        ###账号相关设置
        self.labeluserName = QtWidgets.QLineEdit(self)  # 账号标签
        self.labeluserName.setGeometry(QtCore.QRect(142, 355, 60, 28))  # 位置参数
        self.labeluserName.setStyleSheet("background:transparent;border:none;")  # 边框设置
        self.labeluserName.setReadOnly(True)  # 设置只读
        self.labeluserName.setText("账号：")  # 内容

        self.userName = QtWidgets.QLineEdit(self)  # 账号
        self.userName.setGeometry(QtCore.QRect(218, 355, 220, 28))  # 位置参数
        self.userName.setObjectName("username")
        self.userName.setPlaceholderText("请输入账号")  # 提示文本
        self.userName.setMaxLength(20)  # 限制最大输入内容

        ###密码相关设置
        self.labelpassword = QtWidgets.QLineEdit(self)  # 密码标签
        self.labelpassword.setGeometry(QtCore.QRect(142, 395, 60, 28))  # 位置参数
        self.labelpassword.setStyleSheet("background:transparent;border:none;")  # 边框设置
        self.labelpassword.setReadOnly(True)  # 设置只读
        self.labelpassword.setText("密码：")  # 内容

        self.password = QtWidgets.QLineEdit(self)  # 密码
        self.password.setGeometry(QtCore.QRect(218, 395, 220, 28))  # 位置参数
        self.password.setObjectName("password")  #
        self.password.setPlaceholderText("请输入密码")  # 提示文本
        self.password.setMaxLength(20)  # 最大输入内容
        self.password.setEchoMode(self.password.Password)

        ###登录按钮设置
        self.loginButton = QtWidgets.QPushButton(self)  # 登录按钮
        self.loginButton.setGeometry(QtCore.QRect(330, 447, 100, 35))  # 设定大小位置参数
        self.loginButton.setObjectName("login")
        self.loginButton.setStyleSheet("color:balck")  # 登录字体颜色
        self.loginButton.setCursor(Qt.PointingHandCursor)
        self.loginButton.clicked.connect(self.loginButtonClicked)#设置按钮的槽函数
        self.loginButton.setText("登录")  # 添加按钮文本

        ###注册按钮设置
        self.registerButton = QtWidgets.QPushButton(self)  # 注册按钮
        self.registerButton.setGeometry(QtCore.QRect(220, 447, 100, 35))  # 设置大小位置参数
        self.registerButton.setObjectName("register")
        self.registerButton.setCursor(Qt.PointingHandCursor)  # 调用方法
        self.registerButton.clicked.connect(self.registerButtonClicked)  # 设置按钮的槽函数
        self.registerButton.setText("注册")  # 添加按钮文本

        self.loginError = QtWidgets.QLineEdit(self)  # 登录信息提示框
        self.loginError.setGeometry(QtCore.QRect(20, 400, 220, 28))  # 位置参数
        self.loginError.setStyleSheet("background:transparent;border-width:0;border-style:outset")  # 格式设置
        self.loginError.setAlignment(QtCore.Qt.AlignCenter)  #
        self.loginError.setReadOnly(True)  # 设置只读

        QtCore.QMetaObject.connectSlotsByName(self)

    def loginButtonClicked(self):
        '''
        点击登录按钮触发事件
        '''
        Username = self.userName.text()  # 读取账号
        Password = self.password.text()  # 读取密码
        if len(Username) == 0 or len(Password) == 0:  # 登录条件判断
            self.loginError.setText("您还没有输入账号或密码！")  # 提示信息
        else:
            client.login(Username, Password)  # 客户端登录
            while client.loginBack == None:
                pass
            if client.loginBack["info"] == "loginSucc":  # 数据库核对账号密码及登录状态（正确）
                self.loginError.setStyleSheet("border:none;")
                self.loginError.setText("登陆成功！")  # 提示信息
                self.GroupChatWindow = GroupChatWindow(Username)  # 登录成功，调出聊天界面
                self.GroupChatWindow.show()
                self.GroupChatWindow.main()
                self.close()  # 关闭信息流
            elif client.loginBack["info"] == "loginFail":  # 数据库核对账号密码及登录状态（错误）
                self.loginError.setText("账号或密码错误！请重新输入！")  # 操作提示
            else:  # 已在线操作
                self.loginError.setText("该账号已经登录！")  # 操作提示
            client.loginBack = None

    def registerButtonClicked(self):
        """
        点击注册账号按钮触发事件
        调出注册窗口
        """
        self.registerWindow = registerWindow()  #
        self.registerWindow.show()  #


class registerWindow(QtWidgets.QDialog):
    """
    注册页面设计
    """
    def __init__(self):
        super(registerWindow, self).__init__()
        self.setupUi()

    def setupUi(self):
        self.setObjectName("registerWindow")
        self.resize(360, 330)  # 背景大小
        self.setWindowTitle("账号注册")

        ###用户名相关设置
        self.userName = QtWidgets.QLineEdit(self)  # 用户名
        self.userName.setGeometry(QtCore.QRect(118, 90, 220, 28))  # 设置参数
        self.userName.setObjectName("username")  #
        self.userName.setPlaceholderText("请输入账号")  # 提示文本
        self.userName.setMaxLength(20)  # 设置长度

        self.labeluserName = QtWidgets.QLineEdit(self)  # 文本输入框前的提示
        self.labeluserName.setGeometry(QtCore.QRect(30, 90, 95, 28))  # 设置参数
        self.labeluserName.setStyleSheet("background:transparent;border:none;")  # 边框设置
        self.labeluserName.setReadOnly(True)  # 设置只读
        self.labeluserName.setText("输入账号：")  # 提示文本

        ###密码相关设置
        self.password = QtWidgets.QLineEdit(self)  # 密码
        self.password.setGeometry(QtCore.QRect(118, 130, 220, 28))  # 设置参数
        self.password.setObjectName("password")
        self.password.setPlaceholderText("请输入密码")  # 提示文本
        self.password.setMaxLength(20)  # 设置长度
        self.password.setEchoMode(self.password.Password)

        self.labelpassword = QtWidgets.QLineEdit(self)
        self.labelpassword.setGeometry(QtCore.QRect(30, 130, 95, 28))  # 设置位置参数
        self.labelpassword.setStyleSheet("background:transparent;border:none;")  # 边框设置
        self.labelpassword.setReadOnly(True)  # 设置只读
        self.labelpassword.setText("输入密码：")  # 提示文本

        ###密码确认相关设置
        self.password2 = QtWidgets.QLineEdit(self)  # 密码确认
        self.password2.setGeometry(QtCore.QRect(118, 170, 220, 28))  # 设置参数
        self.password2.setObjectName("passwordAgain")  # 设置功能
        self.password2.setPlaceholderText("请再次输入密码")  # 提示文本
        self.password2.setMaxLength(20)  # 设置长度
        self.password2.setEchoMode(self.password.Password)

        self.labelpassword2 = QtWidgets.QLineEdit(self)
        self.labelpassword2.setGeometry(QtCore.QRect(30, 170, 95, 28))  # 设置位置参数
        self.labelpassword2.setStyleSheet("background:transparent;border:none;")  # 边框设置
        self.labelpassword2.setReadOnly(True)  # 设置只读
        self.labelpassword2.setText("确认密码：")  # 提示文本

        ###注册按钮设置
        self.registerButton = QtWidgets.QPushButton(self)  # 注册按钮
        self.registerButton.setGeometry(QtCore.QRect(118, 230, 150, 35))  # 设置位置参数
        self.registerButton.setObjectName("register")  #
        self.registerButton.clicked.connect(self.registerButtonClicked)  # 设置按钮的槽函数
        self.registerButton.setText("注册")  # 提示文本

        self.registerError = QtWidgets.QLineEdit(self)  # 注册信息提示框
        self.registerError.setGeometry(QtCore.QRect(0, 40, 200, 28))  # 设置位置参数
        self.registerError.setStyleSheet("background:transparent;border-width:0;border-style:outset")  # 边框设置
        self.registerError.setAlignment(QtCore.Qt.AlignCenter)  #
        self.registerError.setReadOnly(True)  # 设置只读
        self.registerError.setText("请填写您的个人信息！")  # 提示文本

        QtCore.QMetaObject.connectSlotsByName(self)

    def registerButtonClicked(self):  # 注册账号
        '''
        点击注册账号按钮触发事件
        '''
        Username = self.userName.text()  # 预留文本信息
        password = self.password.text()  # 预留文本信息
        password2 = self.password2.text()  # 预留文本信息
        if len(Username) == 0 or len(password) == 0 or len(password2) == 0:  # 注册条件判断
            self.registerTip.setText("您还没有输入账号或密码！")  # 若未输入账号或密码
        elif password != password2:
            self.registerTip.setText("您两次输入的密码不同！")  # 若输入的密码不同
        else:
            client.register(Username, password)  # 成功注册
            while client.registerBack == None:  # 判断是否已注册
                pass
            if client.registerBack["info"] == "rgtrSucc":  # 判断条件
                self.registerTip.setStyleSheet("border:none;")
                self.registerTip.setText("注册成功！请返回登录！")  # 提示信息
            else:
                self.registerTip.setText("该账号已存在！")  # 提示信息
            client.registerBack = None  # 客户端确认


class GroupChatWindow(QtWidgets.QDialog):
    """
    公共聊天室（群聊）UI设计
    """
    def __init__(self, name):  #
        print("您已经进入公共聊天室！")
        self.Username = name  # 读取发送方id
        self.Destname = ''  # 接收方id
        super(GroupChatWindow, self).__init__()  #
        self.setupUi()
        try:
            os.mkdir(self.Username)  # 创建对应的文件夹
        except FileExistsError:
            pass

    def setupUi(self):
        ###聊天窗口设置
        self.setObjectName("MyChat")  # 聊天室名称
        self.setStyleSheet("#MyChat{border-image:url(./image/chat/chat_background.png);}")  # 设置背景
        self.setWindowTitle(self.Username + "的聊天室")  # 聊天窗口名称
        self.resize(1000, 600)  # 大小

        ###群聊消息框
        self.grprecvText = QtWidgets.QTextBrowser(self)
        self.grprecvText.setGeometry(QtCore.QRect(15, 20, 700, 275))  # 位置
        self.grprecvText.setObjectName("textRecv")
        self.grprecvText.setAlignment(QtCore.Qt.AlignTop)
        self.grprecvText.setReadOnly(True)  # 只读

        ###消息编辑框
        self.sendText = QtWidgets.QTextEdit(self)
        self.sendText.setGeometry(QtCore.QRect(15, 340, 670, 170))  # 位置
        self.sendText.setObjectName("textSend")  # 调用函数
        self.sendText.setAlignment(QtCore.Qt.AlignTop)
        self.destsend = 'all'  # 信息全部可见

        ###发送消息按钮
        self.sendButton = QtWidgets.QPushButton(self)
        self.sendButton.setGeometry(QtCore.QRect(300, 530, 65, 27))  # 位置
        self.sendButton.setObjectName("sendButton")
        self.sendButton.clicked.connect(self.sendButtonClicked)  # 设置按钮的槽函数
        self.sendButton.setText("发送")  # 按钮文字

        ###在线好友列表头
        self.FDOLHeader = QtWidgets.QLineEdit(self)
        self.FDOLHeader.setGeometry(QtCore.QRect(685, 20, 270, 30))  # 位置
        self.FDOLHeader.setObjectName("FDOLHeader")  # 调用函数
        self.FDOLHeader.setAlignment(QtCore.Qt.AlignTop)
        self.FDOLHeader.setReadOnly(True)
        self.FDOLHeader.setText("在线好友列表：")  # 聊天室显示

        ###在线好友列表
        self.FDOL = QtWidgets.QListWidget(self)
        self.FDOL.setGeometry(QtCore.QRect(685, 45, 270, 250))  # 位置
        self.FDOL.setObjectName("friendlist")
        self.FDOL.doubleClicked.connect(self.FDOLDoubleClicked)  # 设置按钮的槽函数
        self.FDOL.addItems(client.userlist)  # 按钮实现功能

        ###发送表情包按钮
        self.emojiButton = QtWidgets.QPushButton(self)
        self.emojiButton.setGeometry(QtCore.QRect(15, 300, 55, 35))  # 位置
        self.emojiButton.clicked.connect(self.emojiButtonClicked)  # 按钮实现功能
        self.emojiButton.setText("发送表情")  # 提示文本

        ###发送文件按钮
        self.fileButton = QtWidgets.QPushButton(self)
        self.fileButton.setGeometry(QtCore.QRect(75, 300, 55, 35))  # 位置
        self.fileButton.clicked.connect(self.fileButtonClicked)  # 按钮实现功能
        self.fileButton.setText("发送文件")  # 提示文本

        ###发送图片按钮
        self.imageButton = QtWidgets.QPushButton(self)
        self.imageButton.setGeometry(QtCore.QRect(135, 300, 55, 35))  # 位置
        self.imageButton.clicked.connect(self.imageButtonClicked)  # 按钮实现功能
        self.imageButton.setText("发送图片")  # 提示文本

        ###发送语音按钮
        self.audioButton = QtWidgets.QPushButton(self)
        self.audioButton.setGeometry(QtCore.QRect(195, 300, 55, 35))  # 位置
        self.audioButton.clicked.connect(self.audioButtonClicked)  # 按钮实现功能
        self.audioButton.setText("发送语音")  # 提示文本

        ###收听语音按钮
        self.earButton = QtWidgets.QPushButton(self)
        self.earButton.setGeometry(QtCore.QRect(255, 300, 55, 35))  # 位置
        self.earButton.clicked.connect(self.earButtonClicked)  # 按钮实现功能
        self.earButton.setText("收听语音")  # 提示文本

        ###文件选择界面
        self.fileselect = QtWidgets.QFileDialog(self)
        self.fileselect.setGeometry(QtCore.QRect(248, 341, 500, 62))  # 位置

        ###表情选择
        self.emoji = QtWidgets.QTableWidget(self)  # 表情列表
        self.emoji.setGeometry(QtCore.QRect(15, 175, 120, 120))  # 位置
        self.emoji.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.emoji.horizontalHeader().setVisible(False)  # 隐藏水平表头
        self.emoji.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏垂直滚动条
        self.emoji.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏水平滚动条
        self.emoji.setColumnCount(8)  # 设置列数
        self.emoji.setRowCount(8)  # 设置行数
        for i in range(64):  # 读取命名表情
            icon = QtWidgets.QLabel()
            icon.setMargin(4)
            movie = QtGui.QMovie()
            movie.setScaledSize(QtCore.QSize(30, 30))  # 设置图片发送大小
            movie.setFileName("./image/emoji/" + str(i) + ".jpg")  # 表情格式
            movie.start()
            icon.setMovie(movie)
            self.emoji.setCellWidget(int(i / 8), i % 8, icon)
            self.emoji.setColumnWidth(i % 8, 40)  # 设置列的宽度
            self.emoji.setRowHeight(int(i / 8), 40)  # 设置行的高度
        self.emoji.hide()  # 收起表情
        self.emoji.cellClicked.connect(self.emojiClicked)  # 功能连接

        QtCore.QMetaObject.connectSlotsByName(self)

    def sendButtonClicked(self):
        '''
        发送按钮响应
        '''
        text = self.sendText.toPlainText()  # 读取聊天框信息
        if len(text):
            client.send_Msg(text, self.destsend)  # 调用客户端函数
            self.sendText.clear() #清空输入框内容

    def FDOLDoubleClicked(self):
        """
        好友列表双击添加私聊窗口
        """
        name = self.FDOL.currentItem().text()  # 聊天对象
        if name == self.Username:  # 选择自己
            QMessageBox.information(self, "温馨提示", "自己不能和自己进行对话!",
                                    QMessageBox.Yes | QMessageBox.No)  # 弹窗提醒
            return
        self.PrivateChatWindow = PrivateChatWindow(self.Username, name)  # 登录成功，调出私聊界面，传递参数:自己的name与对方的name
        self.PrivateChatWindow.show()
        self.PrivateChatWindow.main()

    def emojiButtonClicked(self):
        '''
        打开/隐藏选择表情框
        '''
        if self.emoji.isVisible():
            self.emoji.hide()  # 隐藏表情选项
        else:
            self.emoji.show()  # 显示表情选项

    def emojiClicked(self, row, column):  # 点击表情函数
        '''
        点击表情包
        '''
        client.send_Msg(row * 3 + column, self.destsend, "emoji")
        self.emoji.hide()

    def fileButtonClicked(self):
        '''
        发送文件
        '''
        fileinfo = self.fileselect.getOpenFileName(self, 'OpenFile', "d:/")  # 默认打开文件路径
        filepath, filetype = os.path.splitext(fileinfo[0])
        filename = filepath.split("/")[-1]
        if fileinfo[0] != '':
            with open(fileinfo[0], mode='rb') as f:
                r = f.read()  # 打开数据流
                f.close()  # 关闭数据流
            file_r = base64.encodebytes(r).decode("utf-8")  # 设置编码格式
            client.send_Msg(file_r, self.destsend, filetype, filename)  # 客户端发送函数

    def imageButtonClicked(self):
        '''
        发送图片
        '''
        fileinfo = self.fileselect.getOpenFileName(self, 'OpenFile', "d:/",
                                                   "Image files (*.jpg *.gif *.png)")  # 打开默认地址及显示文件格式
        filepath, filetype = os.path.splitext(fileinfo[0])  # 读取参数
        filename = filepath.split("/")[-1]  # 读取参数
        if fileinfo[0] != '':
            with open(fileinfo[0], mode='rb') as f:
                r = f.read()  # 打开数据流
                f.close()  # 关闭数据流
            file_r = base64.encodebytes(r).decode("utf-8")  # 设置编码格式
            client.send_Msg(file_r, self.destsend, filetype, filename)  # 调用客户端函数

    def audioButtonClicked(self):
        '''
        发送语音消息
        '''
        T = time.strftime('%Y-%m-%d-%H-%M-%S')  # 获取时间函数
        path = self.Username + "/" + T + ".wav"  # 路径格式
        record_audio(path, 5)  # 记录定长时间的语音
        with open(path, mode='rb') as f:
            r = f.read()  # 打开数据流
            f.close()  # 关闭数据流
        file_r = base64.encodebytes(r).decode("utf-8")  # 设置编码格式
        client.send_Msg(file_r, self.destsend, ".wav", T)  # 发送文件

    def earButtonClicked(self):
        '''
        收听语音消息
        '''
        names = os.listdir(self.Username)  #
        ls = []  # 获取参数列表
        for name in names:
            if name[-3:] == "wav":  # 判断格式
                ls.append(name)  # 文件名称
        for i in ls:
            play_audio(self.Username + "/" + i)  # 播放
            os.remove(self.Username + "/" + i)  # 清除缓存

    def recv(self):
        '''
        用于将接收到的消息显示出来
        '''
        while True:
            while len(client.usermsg):
                msg_recv = client.usermsg.pop()
                msgtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_recv["time"]))
                if msg_recv["destname"] != "all":
                    client.usermsg.append(msg_recv)
                    time.sleep(0.0001)
                    continue

                # 文本信息
                if msg_recv["mtype"] == "msg":
                    msg_recv["msg"] = msg_recv["msg"].replace("\n", "\n  ")
                    if (msg_recv["name"] == self.Username) & (
                            msg_recv["destname"] == "all"):  # 从本地发送的消息打印
                        self.grprecvText.setTextColor(Qt.green)  # 颜色
                        self.grprecvText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n")  # 从本地发送的消息打印
                        self.grprecvText.setTextColor(Qt.black)  # 颜色
                        self.grprecvText.insertPlainText(" " + msg_recv["msg"] + "\n")  # 从本地发送的消息打印
                        self.grprecvText.ensureCursorVisible()  #
                        # cursor = self.grprecvText.textCursor()
                        # cursor.movePosition(QtGui.QTextCursor.End)

                    # elif msg_recv["destname"] == "all":        #本地接收到的消息打印
                    else:
                        # cursor = self.grprecvText.textCursor()
                        # cursor.movePosition(QtGui.QTextCursor.End)
                        self.grprecvText.setTextColor(Qt.blue)  #
                        self.grprecvText.insertPlainText(
                            " " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 从本地发送的消息打印
                        self.grprecvText.setTextColor(Qt.black)  #
                        self.grprecvText.insertPlainText(msg_recv["msg"] + "\n")  # 从本地发送的消息打印

                # 表情信息
                elif msg_recv["mtype"] == "emoji":
                    if (msg_recv["name"] == self.Username) & (msg_recv["destname"] == "all"):  # 从本地发送的消息打印
                        # self.grprecvText.moveCursor(QtGui.QTextCursor.End)
                        self.grprecvText.setTextColor(Qt.green)  # 颜色
                        self.grprecvText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 从本地发送的消息打印
                        path = "./image/emoji/" + str(msg_recv["msg"]) + ".jpg"  # 表情文件格式
                        tcursor = self.grprecvText.textCursor()
                        # cursor = self.textEdit.textCursor()
                        # document = self.textEdit.document()
                        # document.addResource(QTextDocument.ImageResource, QUrl("image"), image)
                        # cursor.insertImage("image")
                        # image = QImage(path)
                        # document = self.grprecvText.document()
                        # document.addResource(QTextDocument.ImageResource,QUrl("image"), image)
                        img = QtGui.QTextImageFormat()
                        img.setName(path)  # 名称路径
                        img.setHeight(28)  # 设置高度
                        img.setWidth(28)  # 设置宽度
                        # src = "<img src="+path+" />"
                        # self.grprecvText.append(src)
                        tcursor.insertImage(img)
                        self.grprecvText.insertPlainText("\n")

                    elif msg_recv["destname"] == "all":  # 本地接收到的消息打印
                        self.grprecvText.moveCursor(QtGui.QTextCursor.End)
                        self.grprecvText.setTextColor(Qt.blue)
                        self.grprecvText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 从本地发送的消息打印
                        path = "./image/emoji/" + str(msg_recv["msg"]) + ".jpg"  # 表情文件格式
                        tcursor = self.grprecvText.textCursor()
                        img = QtGui.QTextImageFormat()
                        img.setName(path)  # 文件路径
                        img.setHeight(28)
                        img.setWidth(28)
                        tcursor.insertImage(img)
                        self.grprecvText.insertPlainText("\n")

                # 文件和语音信息
                else:
                    if (msg_recv["name"] == self.Username) & (msg_recv["destname"] == "all"):  # 从本地发送的消息打印
                        self.grprecvText.moveCursor(QtGui.QTextCursor.End)
                        self.grprecvText.setTextColor(Qt.green)
                        self.grprecvText.insertPlainText(
                            " " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 从本地发送的消息打印
                        path = "./" + self.Username + "/" + msg_recv["fname"] + msg_recv["mtype"]  # 读取路径及格式
                        with open(path, "wb") as f:
                            f.write(base64.b64decode(msg_recv["msg"]))  # 写入
                            f.close()  # 关闭文件
                        tcursor = self.grprecvText.textCursor()

                        if msg_recv["mtype"] in (".png", ".gif", ".jpg"):
                            img = QtGui.QTextImageFormat()
                            img.setName(path)
                            img.setHeight(100)
                            img.setWidth(100)
                            tcursor.insertImage(img)
                        elif msg_recv["mtype"] == ".wav":
                            self.grprecvText.insertPlainText("您刚发送了一条语音。")
                        else:
                            self.grprecvText.insertPlainText("发送的文件已保存在：" + path)
                        self.grprecvText.insertPlainText("\n")

                    elif msg_recv["destname"] == "all":  # 本地接收到的消息打印
                        # self.grprecvText.moveCursor(QtGui.QTextCursor.End)
                        self.grprecvText.setTextColor(Qt.blue)
                        self.grprecvText.insertPlainText(
                            " " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 从本地发送的消息打印
                        path = "./" + self.Username + "/" + msg_recv["fname"] + msg_recv["mtype"]  #
                        with open(path, "wb") as f:
                            f.write(base64.b64decode(msg_recv["msg"]))  # 写入
                            f.close()  # 关闭数据流
                        if msg_recv["mtype"] in (".png", ".gif", ".jpg"):  # 文件格式
                            tcursor = self.grprecvText.textCursor()
                            img = QtGui.QTextImageFormat()
                            img.setName(path)  # 文件名称
                            img.setHeight(100)  # 设置高度
                            img.setWidth(100)  # 设置宽度
                            tcursor.insertImage(img)
                        elif msg_recv["mtype"] == ".wav":
                            self.grprecvText.insertPlainText("您收到了一条语音")  # 消息提示
                        else:
                            self.grprecvText.insertPlainText("接收的文件已保存在：" + path)  # 保存文件
                        self.grprecvText.insertPlainText("\n")

            while len(client.sysmsg):
                msg_recv = client.sysmsg.pop()
                if msg_recv["info"] == "userlogin":
                    if msg_recv["name"] not in client.userlist:
                        client.userlist.append(msg_recv["name"])
                        self.FDOL.clear()
                        self.FDOL.addItems(client.userlist)
                elif msg_recv["info"] == "userexit":
                    if msg_recv["name"] in client.userlist:
                        client.userlist.remove(msg_recv["name"])
                        self.FDOL.clear()
                        self.FDOL.addItems(client.userlist)
                self.grprecvText.setTextColor(Qt.gray)
                self.grprecvText.insertPlainText(" " + msg_recv["msg"] + "\n")

    def main(self):
        func1 = threading.Thread(target=self.recv)
        func1.start()


class PrivateChatWindow(QtWidgets.QDialog):
    """
    私聊界面UI设计
    """
    def __init__(self, Aname, Bname):
        super(PrivateChatWindow, self).__init__()
        self.Aname = Aname  # 引入名字
        self.Bname = Bname  # 引入名字
        self.Username = Aname  # 引入名字
        self.destsend = self.Bname  #
        self.setupUI()  # 执行函数

    def setupUI(self):
        ###私聊窗口设置
        self.setObjectName("PrivateChat")  # 聊天底层名称
        self.setStyleSheet("#PrivateChat{border-image:url(./image/chat/privatechat_background.png);}") # 背景图片地址
        self.setWindowTitle("私聊发起人：" + self.Username)  # 聊天窗口提示
        self.resize(700, 480)  # 大小

        ###消息框设置
        self.PrivateText = QtWidgets.QTextEdit(self)
        self.PrivateText.setGeometry(QtCore.QRect(20, 20, 660, 280))  # 位置大小等相关参数
        self.PrivateText.setObjectName("textRecv")  # 调用已编写函数
        self.PrivateText.setAlignment(QtCore.Qt.AlignTop)  #
        self.PrivateText.setReadOnly(True)  # 只读

        ###消息编辑框
        self.sendText = QtWidgets.QTextEdit(self)
        self.sendText.setGeometry(QtCore.QRect(20, 345, 660, 85))  # 位置大小等相关参数
        self.sendText.setObjectName("textSend")  # 调用已编写函数
        self.sendText.setAlignment(QtCore.Qt.AlignTop)  #

        ###发送消息按钮
        self.sendButton = QtWidgets.QPushButton(self)
        self.sendButton.setGeometry(QtCore.QRect(530, 435, 150, 25))  # 位置大小等相关参数
        self.sendButton.setObjectName("sendButton")  # 调用已编写函数
        self.sendButton.clicked.connect(self.SendButtonClicked)  # 功能与按钮连接，设置点击函数
        self.sendButton.setText("发送给" + self.Bname)  # 设置最终显示格式

        ###发送表情按钮
        self.emojiButton = QtWidgets.QPushButton(self)  # 发送表情的按钮
        self.emojiButton.setGeometry(QtCore.QRect(20, 305, 55, 35))  # 位置大小等相关参数
        # self.emojiButton.setStyleSheet("border-image:url(./images/style/emoji.png);")  # 设置功能图标
        self.emojiButton.clicked.connect(self.emojiButtonClicked)  # 功能与按钮连接，设置点击函数
        self.emojiButton.setText("发送表情")  # 提示文本

        ###发送文件按钮
        self.fileButton = QtWidgets.QPushButton(self)  # 发送文件的按钮
        self.fileButton.setGeometry(QtCore.QRect(80, 305, 55, 35))  # 位置大小等相关参数
        # self.fileButton.setStyleSheet("border-image:url(./images/style/file.png);")  # 设置功能图标
        self.fileButton.clicked.connect(self.fileButtonClicked)  # 功能与按钮连接，设置点击函数
        self.fileButton.setText("发送文件")  # 提示文本

        ###发送图片按钮
        self.imageButton = QtWidgets.QPushButton(self)  # 发送图片的按钮
        self.imageButton.setGeometry(QtCore.QRect(140, 305, 55, 35))  # 位置大小等相关参数
        self.imageButton.clicked.connect(self.imageButtonClicked)  # 功能与按钮连接，设置点击函数
        self.imageButton.setText("发送图片")  # 提示文本

        ###发送语音按钮
        self.audioButton = QtWidgets.QPushButton(self)  # 发送语音的按钮
        self.audioButton.setGeometry(QtCore.QRect(200, 305, 55, 35))  # 位置大小等相关参数
        # self.audioButton.setStyleSheet("border-image:url(./images/style/audio.png);")  # 设置功能图标
        self.audioButton.clicked.connect(self.audioButtonClicked)  # 功能与按钮连接，设置点击函数
        self.audioButton.setText("发送语音")  # 提示文本

        ###接听语音按钮
        self.earButton = QtWidgets.QPushButton(self)  # 听取音频的按钮
        self.earButton.setGeometry(QtCore.QRect(260, 305, 55, 35))  # 位置大小等相关参数
        # self.earButton.setStyleSheet("border-image:url(./images/style/ear.png);")  # 设置功能图标
        self.earButton.clicked.connect(self.earButtonClicked)  # 功能与按钮连接，设置点击函数
        self.earButton.setText("收听语音")  # 提示文本

        ###发起语音通话按钮
        self.audiochatButton = QtWidgets.QPushButton(self)  # 语音聊天的按钮
        self.audiochatButton.setGeometry(QtCore.QRect(320, 305, 55, 35))  # 位置
        self.audiochatButton.clicked.connect(self.audiochatButtonClicked)  # 按钮实现功能
        self.audiochatButton.setText("语音聊天")  # 提示文本

        ###接听语音通话按钮
        self.recvaudiochatButton = QtWidgets.QPushButton(self)  # 语音聊天的按钮
        self.recvaudiochatButton.setGeometry(QtCore.QRect(380, 305, 55, 35))  # 位置
        self.recvaudiochatButton.clicked.connect(self.recvaudiochatButtonClicked)  # 按钮实现功能
        self.recvaudiochatButton.setText("接听语音")  # 提示文本

        ###发起视频通话按钮
        self.videochatButton = QtWidgets.QPushButton(self)  # 视频聊天的按钮
        self.videochatButton.setGeometry(QtCore.QRect(440, 305, 55, 35))  # 位置
        self.videochatButton.clicked.connect(self.videochatButtonClicked)  # 按钮实现功能
        self.videochatButton.setText("视频聊天")  # 提示文本

        ###接收视频通话按钮
        self.recvvideochatButton = QtWidgets.QPushButton(self)  # 视频聊天的按钮
        self.recvvideochatButton.setGeometry(QtCore.QRect(500, 305, 55, 35))  # 位置
        self.recvvideochatButton.clicked.connect(self.recvvideochatButtonClicked)  # 按钮实现功能
        self.recvvideochatButton.setText("接听视频")  # 提示文本

        self.fileselect = QtWidgets.QFileDialog(self)  # 文件选择界面
        self.fileselect.setGeometry(QtCore.QRect(388, 341, 500, 62))  # 位置大小等相关参数

        self.emoji = QtWidgets.QTableWidget(self)  # 表情列表
        self.emoji.setGeometry(QtCore.QRect(20, 175, 120, 120))  # 位置大小等相关参数
        self.emoji.verticalHeader().setVisible(False)  # 隐藏垂直表头
        self.emoji.horizontalHeader().setVisible(False)  # 隐藏水平表头
        self.emoji.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏垂直滚动条
        self.emoji.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)  # 隐藏水平滚动条
        self.emoji.setColumnCount(8)  # 设置表情栏列数
        self.emoji.setRowCount(8)  # 设置表情栏行数
        for i in range(64):  # 读取命名表情
            icon = QtWidgets.QLabel()  #
            icon.setMargin(4)  #
            movie = QtGui.QMovie()  #
            movie.setScaledSize(QtCore.QSize(30, 30))  # 设置图片发送大小
            movie.setFileName("./image/emoji/" + str(i) + ".jpg")  # 表情保存位置、命名规则和保存格式
            movie.start()  #
            icon.setMovie(movie)  #
            self.emoji.setCellWidget(int(i / 8), i % 8, icon)  # 确定表情大小
            self.emoji.setColumnWidth(i % 8, 40)  # 设置列的宽度
            self.emoji.setRowHeight(int(i / 8), 40)  # 设置行的高度
        self.emoji.hide()  # 读取高度
        self.emoji.cellClicked.connect(self.emojiClicked)  # 按钮功能连接

        QtCore.QMetaObject.connectSlotsByName(self)  #

    def SendButtonClicked(self):
        '''
        发送按钮响应
        '''
        text = self.sendText.toPlainText()  # 读取聊天框信息
        if len(text):
            client.send_Msg(text, self.destsend)  # 调用客户端函数
            self.sendText.clear()  # 清空输入框内容

    def emojiButtonClicked(self):  # 表情按钮函数
        '''
        打开/隐藏选择表情框
        '''
        if self.emoji.isVisible():
            self.emoji.hide()  # 隐藏表情选项
        else:
            self.emoji.show()  # 显示表情选项

    def emojiClicked(self, row, column):  # 表情点击
        '''
        点击表情包
        '''
        client.send_Msg(row * 3 + column, self.destsend, "emoji")
        print("显示表情4")
        self.emoji.hide()

    def fileButtonClicked(self):  # 文件传输
        '''
        发送文件
        '''
        fileinfo = self.fileselect.getOpenFileName(self, 'OpenFile', "d:/")  # 默认打开文件地址
        print(fileinfo)
        filepath, filetype = os.path.splitext(fileinfo[0])  #
        filename = filepath.split("/")[-1]  # 寻找文件路径格式
        if fileinfo[0] != '':
            with open(fileinfo[0], mode='rb') as f:
                r = f.read()  # 开启数据流
                f.close()  # 关闭数据流
            file_r = base64.encodebytes(r).decode("utf-8")  # 编码格式
            client.send_Msg(file_r, self.destsend, filetype, filename)  # 调取发送文件函数及参数

    def imageButtonClicked(self):
        '''
        发送图片
        '''
        fileinfo = self.fileselect.getOpenFileName(self, 'OpenFile', "d:/",
                                                   "Image files (*.jpg *.gif *.png)")  # 发送图片默认打开位置及格式
        print(fileinfo)  # 输出
        filepath, filetype = os.path.splitext(fileinfo[0])  # 文件路径+格式
        filename = filepath.split("/")[-1]  # 寻找文件路径格式
        if fileinfo[0] != '':  #
            with open(fileinfo[0], mode='rb') as f:
                r = f.read()  # 打开数据流
                f.close()  # 关闭数据流
            file_r = base64.encodebytes(r).decode("utf-8")  # 设置编码格式
            client.send_Msg(file_r, self.destsend, filetype, filename)  # 调取发送文件函数及参数

    def audioButtonClicked(self):
        '''
        发送语音消息
        '''
        T = time.strftime('%Y-%m-%d-%H-%M-%S')  # 获取当前时间
        path = self.Username + "/" + T + ".wav"  # 打开音频路径
        record_audio(path, 5)  #
        with open(path, mode='rb') as f:  # 点击关闭文件
            r = f.read()  # 打开数据流
            f.close()  # 关闭数据流
        file_r = base64.encodebytes(r).decode("utf-8")  # 设计编码格式
        client.send_Msg(file_r, self.destsend, ".wav", T)  # 缓冲文件中保存格式

    def earButtonClicked(self):
        '''
        收听语音消息
        '''
        names = os.listdir(self.Username)  #
        ls = []  # 获取列表参数
        for name in names:
            if name[-3:] == "wav":  # 判断文件格式
                ls.append(name)  # 获取文件名
        for i in ls:
            play_audio(self.Username + "/" + i)  # 播放指定文件
            os.remove(self.Username + "/" + i)  # 删除缓存

    def audiochatButtonClicked(self):
        """
        开启语音通话（客户端）
        """
        self.PrivateText.setTextColor(Qt.green)
        T = time.strftime('%Y-%m-%d %H:%M:%S')
        self.PrivateText.insertPlainText(" " + self.Aname + "  " + T + "\n  ")
        self.PrivateText.insertPlainText("您请求与对方语音通话")
        self.PrivateText.insertPlainText("\n ")
        IP1 = client.getClientIPFromName(self.destsend)
        print("语音对方的IP为"+IP1)
        aclient1 = AudioClient(IP1, 17777, VERSION)
        aclient1.start()

        IP2 = gethostbyname(gethostname())
        aServer1 = AudioServer(IP2, 17777, VERSION)
        aServer1.start()

    def recvaudiochatButtonClicked(self):
        """
        接听语音通话（做服务器）
        """
        self.PrivateText.setTextColor(Qt.green)
        T = time.strftime('%Y-%m-%d %H:%M:%S')
        self.PrivateText.insertPlainText(" " + self.Aname + "  " + T + "\n  ")
        self.PrivateText.insertPlainText(self.Bname + "请求与您语音通话")
        self.PrivateText.insertPlainText("\n ")
        addrIP1 = gethostbyname(gethostname())
        aServer2 = AudioServer(addrIP1, 17777, VERSION)
        aServer2.start()

        addrIP2 = client.getClientIPFromName(self.destsend)
        aclient2 = AudioClient(addrIP2, 17777, VERSION)
        aclient2.start()

    def videochatButtonClicked(self):
        """
        开启视频通话（做客户端）
        """
        self.PrivateText.setTextColor(Qt.green)
        T = time.strftime('%Y-%m-%d %H:%M:%S')
        self.PrivateText.insertPlainText(" " + self.Aname + "  " + T + "\n  ")
        self.PrivateText.insertPlainText("您请求与对方视频通话")
        self.PrivateText.insertPlainText("\n ")
        IP1 = client.getClientIPFromName(self.destsend)
        print("视频的对方IP为：" + IP1)
        vClient1 = VideoClient(IP1, 16538, LEVEL, VERSION)
        aclient1 = AudioClient(IP1, 23143, VERSION)
        vClient1.start()
        time.sleep(1)
        aclient1.start()

        IP2 = gethostbyname(gethostname())
        vserver1 = VideoServer(IP2, 16538, VERSION)
        aServer1 = AudioServer(IP2, 23143, VERSION)
        vserver1.start()
        time.sleep(1)
        aServer1.start()

    def recvvideochatButtonClicked(self):
        """
        接取视频（做服务器）
        """
        self.PrivateText.setTextColor(Qt.green)
        T = time.strftime('%Y-%m-%d %H:%M:%S')
        self.PrivateText.insertPlainText(" " + self.Aname + "  " + T + "\n  ")
        self.PrivateText.insertPlainText(self.Bname + "请求与您进行视频通话")
        self.PrivateText.insertPlainText("\n ")

        addrIP1 = gethostbyname(gethostname())
        vserver2 = VideoServer(addrIP1, 16538, VERSION)
        aServer2 = AudioServer(addrIP1, 23143, VERSION)
        # vserver = VideoServer('127.0.0.1', 16538, VERSION)
        # aServer = AudioServer('127.0.0.1', 23143, VERSION)
        vserver2.start()
        time.sleep(1)
        aServer2.start()

        addrIP2 = client.getClientIPFromName(self.destsend)
        print("视频的对方IP为：" + addrIP2)
        vClient2 = VideoClient(addrIP2, 16538, LEVEL, VERSION)
        aclient2 = AudioClient(addrIP2, 23143, VERSION)
        vClient2.start()
        time.sleep(1)
        aclient2.start()

    def recv(self):
        '''
        用于将接收到的消息显示出来
        '''
        while True:
            while len(client.usermsg):
                msg_recv = client.usermsg.pop()  #
                msgtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(msg_recv["time"]))  # 获取时间函数
                if msg_recv["destname"] == "all":  #
                    client.usermsg.append(msg_recv)
                    time.sleep(0.0001)  # 时间精度
                    continue

                # 文本信息
                if msg_recv["mtype"] == "msg":
                    msg_recv["msg"] = msg_recv["msg"].replace("\n", "\n ")
                    if msg_recv["name"] == self.Username:  # 从本地发送的消息打印
                        # self.PrivateText.moveCursor(QtGui.QTextCursor.End)
                        self.PrivateText.setTextColor(Qt.green)  # 颜色
                        self.PrivateText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 发送方信息打印格式
                        self.PrivateText.setTextColor(Qt.black)  # 颜色
                        self.PrivateText.insertPlainText(msg_recv["msg"] + "\n")
                    elif msg_recv["destname"] == self.Username:  # 本地接收到的消息打印
                        # self.PrivateText.moveCursor(QtGui.QTextCursor.End)
                        self.PrivateText.setTextColor(Qt.blue)  # 颜色
                        self.PrivateText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 发送方信息打印格式
                        self.PrivateText.setTextColor(Qt.black)  # 颜色
                        self.PrivateText.insertPlainText(msg_recv["msg"] + "\n")  #

                # 表情信息
                elif msg_recv["mtype"] == "emoji":
                    if msg_recv["name"] == self.Username:  # 从本地发送的消息打印
                        # self.PrivateText.moveCursor(QtGui.QTextCursor.End)
                        self.PrivateText.setTextColor(Qt.green)  # 颜色
                        self.PrivateText.insertPlainText(
                            " " + msg_recv["name"] + "  " + msgtime + "\n  ")
                        path = "./image/emoji/" + str(msg_recv["msg"]) + ".jpg"  # 读取表情文件路径
                        tcursor = self.PrivateText.textCursor()
                        img = QtGui.QTextImageFormat()
                        img.setName(path)  # 设定名称
                        img.setHeight(28)  # 设定高度
                        img.setWidth(28)  # 设定宽度
                        tcursor.insertImage(img)  # 图片
                        self.PrivateText.insertPlainText("\n")
                    elif msg_recv["destname"] == self.Username:  # 本地接收到的消息打印
                        self.PrivateText.moveCursor(QtGui.QTextCursor.End)
                        self.PrivateText.setTextColor(Qt.blue)
                        self.PrivateText.insertPlainText(
                            " " + msg_recv["name"] + "  " + msgtime + "\n  ")
                        path = "./image/emoji/" + str(msg_recv["msg"]) + ".jpg"  # 路径
                        tcursor = self.PrivateText.textCursor()
                        img = QtGui.QTextImageFormat()
                        img.setName(path)  # 设定名称
                        img.setHeight(28)  # 设定高度
                        img.setWidth(28)  # 设定宽度
                        tcursor.insertImage(img)  # 图片
                        self.PrivateText.insertPlainText("\n")

                # 文件信息
                else:
                    if msg_recv["name"] == self.Username:  # 从本地发送的消息打印
                        # self.PrivateText.moveCursor(QtGui.QTextCursor.End)
                        self.PrivateText.setTextColor(Qt.green)  # 颜色
                        self.PrivateText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 本地接收到的消息打印
                        path = "./" + self.Username + "/" + msg_recv["fname"] + msg_recv["mtype"]  #
                        with open(path, "wb") as f:  #
                            f.write(base64.b64decode(msg_recv["msg"]))  # 打开数据流
                            f.close()  # 关闭数据流
                        if msg_recv["mtype"] in (".png", ".gif", ".jpg"):  # 设置文件格式及大小
                            tcursor = self.PrivateText.textCursor()  #
                            img = QtGui.QTextImageFormat()  #
                            img.setName(path)  # 获取名称
                            img.setHeight(100)  # 设置高度
                            img.setWidth(100)  # 设置宽度
                            tcursor.insertImage(img)  #
                        elif msg_recv["mtype"] == ".wav":  # 发送文件保存格式
                            self.PrivateText.insertPlainText("您发送了一条语言消息")  # 提示消息
                        else:
                            self.PrivateText.insertPlainText("您发送的文件已保存在：" + path)  # 文件保存路径
                        self.PrivateText.insertPlainText("\n")  # 空格符
                    elif msg_recv["destname"] == self.Username:  # 本地接收到的消息打印
                        # self.PrivateText.moveCursor(QtGui.QTextCursor.End)
                        self.PrivateText.setTextColor(Qt.blue)
                        self.PrivateText.insertPlainText(" " + msg_recv["name"] + "  " + msgtime + "\n  ")  # 本地接收到的消息打印
                        path = "./" + self.Username + "/" + msg_recv["fname"] + msg_recv["mtype"]
                        with open(path, "wb") as f:
                            f.write(base64.b64decode(msg_recv["msg"]))
                            f.close()
                        if msg_recv["mtype"] in (".png", ".gif", ".jpg"):  # 设置文件格式及大小
                            tcursor = self.PrivateText.textCursor()
                            img = QtGui.QTextImageFormat()
                            img.setName(path)  # 获取名称
                            img.setHeight(100)  # 设置高度
                            img.setWidth(100)  # 设置宽度
                            tcursor.insertImage(img)
                        elif msg_recv["mtype"] == ".wav":  # 判断文件扩展名
                            self.PrivateText.insertPlainText("您收到了一条语言消息")  # 消息框提示
                        else:
                            self.PrivateText.insertPlainText("您收到的文件已保存在：" + path)  # 消息提示
                        self.PrivateText.insertPlainText("\n")  # 空格符

    def main(self):
        func = threading.Thread(target=self.recv)
        func.start()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # client = Client(addr="127.0.0.1", port=8024)  # 设置IP及端口

    client = Client(addr='192.168.31.97', port=8024)  # 获取自己的IP
    client.main()

    login = loginWindow()
    login.show()

    sys.exit(app.exec_())

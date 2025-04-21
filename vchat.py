import pickle
import struct
import time
import zlib
from socket import *
import threading
import cv2
# 定义两个基础类
class VideoServer(threading.Thread):  # 先为双方的通信设计Server类和Client类，两个类均继承threading.Thread并实现双向的C/S连接
    def __init__(self, ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)  # 设置线程为守护线程
        self.ADDR = (ip, port)  # 创建socket对象
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)  # AF_INET与AF_INET6常量表示相对应协议
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)  # 可以指定通信双方使用的协议版本，即基于IPv4 还是IPv6 的TCP连接

    def __del__(self):
        self.sock.close()  # Server类需要存储本地服务器监听的端口号
        try:
            cv2.destroyAllWindows() # 连接不一定创建成功，因此cv.destroyAllWindows()被放在一个try…catch块中防止出现错误
        except:
            pass

    def run(self):
        print("vChat server starts...")
        self.sock.bind(self.ADDR) # 创建socket对象
        self.sock.listen(1)  # 操作系统可以挂起的最大连接数为1
        conn, addr = self.sock.accept()  # 用于接受客户端请求
        print("remote client success connected...")
        data = "".encode("utf-8")  # 使用编码为 ‘utf-8’
        payload_size = struct.calcsize("L")  # 使用payload_size记录当前从缓冲区读入的数据长度
        cv2.namedWindow('Remote', cv2.WINDOW_NORMAL)
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920)  # 从缓冲区读出的数据流长度超过payload_size时，剩余部分和下一次读出的数据流合并

            msg_size = struct.unpack("L", data[:payload_size])[0]
            data = data[payload_size:]
            while len(data) < msg_size:
                data += conn.recv(81920)  # 不足payload_size时将合并下一次读取的数据流到当前帧中

            frame = pickle.loads(zlib.decompress(data[:msg_size]))  # 在接收完完整的一帧后，显示在创建的窗口中
            data = data[msg_size:]
            cv2.imshow('Remote', frame)
            if cv2.waitKey(1) & 0xFF == 27:
                break

# 捕获视频流的任务应当由Client类完成，所以该类初始化需要四个参数
class VideoClient(threading.Thread):
    def __init__(self, ip, port, level, version):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.ADDR = (ip, port)
        if level <= 3:
            self.interval = level
        else:
            self.interval = 3
        self.fx = 1 / (self.interval + 1)
        if self.fx < 0.3:  # 限制最大帧间隔为3帧
            self.fx = 0.3 # 最坏情况下的缩放比例为0.3
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.cap = cv2.VideoCapture(0)  # 创建一个成员变量cap

    def __del__(self):
        self.sock.close()
        self.cap.release()  # 解释器释放实例对象的时候，调用该方法
# 已经捕获到数据，接下来要发送字节流
    def run(self):
        print("vChat client starts...")
        while True:
            try:
                self.sock.connect(self.ADDR)
                break
            except:
                time.sleep(3)
                continue
        print("client connected...")
        while self.cap.isOpened():  # 如果连接上了，进入循环读相应的文件
            ret, frame = self.cap.read()
            sframe = cv2.resize(frame, (0, 0), fx=self.fx, fy=self.fx)
            data = pickle.dumps(sframe) # 捕获到帧后，使用pickle.dumps方法对其打包
            zData = zlib.compress(data, zlib.Z_BEST_COMPRESSION)
            try:
                """
                将len(data)等参数的值进行一层包装，包装的方法由fmt指定。被包装的参数必须严格符合fmt。最后返回一个包装后的字符串。
                """
                self.sock.sendall(struct.pack("L", len(zData)) + zData) # 用sock.sendall方法发送
            except:
                break
            for i in range(self.interval):
                self.cap.read()

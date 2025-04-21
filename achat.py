from socket import *
import threading
import pyaudio # 使用PyAudio 库处理音频
import struct
import pickle
import time

CHUNK = 1024          # 缓冲区大小
FORMAT = pyaudio.paInt16  # 格式
CHANNELS = 2          # 输入/输出通道数
RATE = 44100          # 音频数据的采样频率
RECORD_SECONDS = 0.5  # 记录秒

# 定义两个基础类，同视频一样两个类均继承threading.Thread并实现双向的C/S连接
class AudioServer(threading.Thread):
    def __init__(self, ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True) # 设置线程为守护线程
        self.ADDR = (ip, port)  # 创建socket对象
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM) # 可以指定通信双方使用的协议版本，即基于IPv4 还是IPv6 的TCP连接
        self.p = pyaudio.PyAudio()  # 实例化一个PyAudio对象
        self.stream = None

    def __del__(self):
        self.sock.close()  # 关闭套接字
        if self.stream is not None:
            self.stream.stop_stream()  # 暂停播放/录制
            self.stream.close()
        self.p.terminate()            # 播放完成后关闭声卡，终止PyAudio

    def run(self):
        print("Video server starts...") # 用以表示线程活动的方法
        self.sock.bind(self.ADDR) # 创建sock对象
        self.sock.listen(1) # 挂起的连接队列的最大长度为1
        conn, addr = self.sock.accept() # 等待传入连接，返回代表连接的新套接字
        print("remote Video client success connected...")
        data = "".encode("utf-8") #使用utf-8编码
        payload_size = struct.calcsize("L")  # 返回对应于格式字符串fmt的结构，L为4
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  output=True,
                                  frames_per_buffer=CHUNK
                                  )  # 使用上面实例化对象打开声卡，设置 采样深度、通道数、采样率、输入和采样点缓存数量
        while True:
            while len(data) < payload_size:
                data += conn.recv(81920)
            packed_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack("L", packed_size)[0]
            while len(data) < msg_size:
                data += conn.recv(81920)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            frames = pickle.loads(frame_data)
            for frame in frames:
                self.stream.write(frame, CHUNK)


class AudioClient(threading.Thread):
    def __init__(self, ip, port, version):
        threading.Thread.__init__(self)
        self.setDaemon(True) # 设置线程为守护线程
        self.ADDR = (ip, port)
        if version == 4:
            self.sock = socket(AF_INET, SOCK_STREAM)
        else:
            self.sock = socket(AF_INET6, SOCK_STREAM)
        self.p = pyaudio.PyAudio() # 同样的，实例化pyaudio对象
        self.stream = None
        print("AUDIO client starts...")

    def __del__(self):
        self.sock.close()
        if self.stream is not None:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()  # 播放完成后关闭声卡，终止PyAudio
# 派生类中重写父类threading.Thread的run()方法
    def run(self):
        while True:
            try:
                self.sock.connect(self.ADDR) # 创建sock对象
                break
            except:
                time.sleep(3)
                continue
        print("AUDIO client connected...")
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)# 使用实例化对象打开声卡，设置 采样深度、通道数、采样率、输入和采样点缓存数量
        while self.stream.is_active():
            frames = []
            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = self.stream.read(CHUNK)
                frames.append(data)
            sendData = pickle.dumps(frames)
            try:
                self.sock.sendall(struct.pack("L", len(sendData)) + sendData)
            except:
                break

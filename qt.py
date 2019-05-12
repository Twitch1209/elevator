# !/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

UI

author: Twitch
"""

import sys
from PyQt5.QtWidgets import (QWidget, QGridLayout,QProgressBar,QLCDNumber,
                             QPushButton, QApplication)
from PyQt5.QtCore import QBasicTimer,pyqtSignal,QObject
import threading
import time


TOP = 20
BOTTOM = 1
STATE = {0: "门停开着", 1: "门停关着", 2: "电梯上升", 3: "电梯下降"}
DIR = {0: "向下", 1: "向上"}

# 消息编码：0 00关门 ，01 开门, 02 有人进
#           1 101去1L ，102去2L，103去三楼
#           2 201一楼有人按上，202二楼有人按上，203三楼有人按上
#           3 302二楼有人按下，303三楼有人按下，304四楼有人按下

lock = threading.Lock()

class Link_to_qt(QObject):  #连接到qt的一个信号机制
    sendMsg = pyqtSignal(str)

    def __init__(self):
        super().__init__()


#信号机制
class Msg:
    def __init__(self, type, value):
        self.type = type
        self.value = value

#信息队列
exitFlag_1 =[]
exitFlag_2 =[]
exitFlag_3 =[]
exitFlag_4 =[]
exitFlag_5 =[]
exitFlag = [exitFlag_1,exitFlag_2,exitFlag_3,exitFlag_4,exitFlag_5]
MsgQueue_1=[]
MsgQueue_2=[]
MsgQueue_3=[]
MsgQueue_4=[]
MsgQueue_5=[]
MsgQueue = [MsgQueue_1,MsgQueue_2,MsgQueue_3,MsgQueue_4,MsgQueue_5]


#电梯类
class Elevator(object):
    state=1 #门状态
    floor=1 #楼层
    dir=0   #方向
    def __init__(self,id):
        self.id=id

    #上楼函数
    def up(self):
        if self.floor<20:
            self.floor+=1
        else:
            print('超过20层')

    def down(self):
        if self.floor>1:
            self.floor-=1
        else:
            print('低于1')

    def get_floor(self):
        print(self.floor)

elevators=[]
for i in range(5):
    elevators.append(Elevator(i))


send = Link_to_qt()
floor_send = Link_to_qt()#楼层消息，传递给lcd显示屏
opendoor_send = Link_to_qt()#开门信息，传递button信息
closedoor_send = Link_to_qt()#关门信息，传递button信息


class Example(QWidget):#UI

    global elevators
    def __init__(self):
        super().__init__()
        self.lcd = []#有五个显示屏
        self.elebtn = []#先实现一部电梯的按钮
        self.initUI()

    def initUI(self):

        global MsgQueue, exitFlag
        grid = QGridLayout()
        self.setLayout(grid)

        names = ['', 'down_20',
                 'up_19', 'down_19',
                 'up_18', 'down_18',
                 'up_17', 'down_17',
                 'up_16', 'down_16',
                 'up_15', 'down_15',
                 'up_14', 'down_14',
                 'up_13', 'down_13',
                 'up_12', 'down_12',
                 'up_11', 'down_11',
                 'up_10', 'down_10',
                 'up_09', 'down_09',
                 'up_08', 'down_08',
                 'up_07', 'down_07',
                 'up_06', 'down_06',
                 'up_05', 'down_05',
                 'up_04', 'down_04',
                 'up_03', 'down_03',
                 'up_02', 'down_02',
                 'up_01', '',
        ]

        cmd_names = ['oprn_1', 'close_1',
                     'open_2', 'close_2',
                     'open_3', 'close_3',
                     'open_4', 'close_4',
                     'open_5', 'close_5',
                     ]
        #整体布局
        positions = [(i, j) for i in range(1,23) for j in range(1,9)]
        lift_pos = [(i, j) for i in range(1,21) for j in range(4,9)]
        open_pos = [(i,j) for i in range(21,23) for j in range(4,9)]

        #增加lcd显示屏
        for i in range(5):
            self.lcd.append(QLCDNumber(self))
            self.lcd[i].setDigitCount(2)
            self.lcd[i].display(1)
            grid.addWidget(self.lcd[i], *(23,i+4))
        floor_send.sendMsg.connect(self.slot_hand)

        for position in positions:
            if position[1]<3 and position[0]<21:
                pos = position[1]-1 + (position[0]-1)*2
                btn = QPushButton(names[pos])
                btn.clicked.connect(self.up_down_button_clicked)
                grid.addWidget(btn,*position)

            if position[1]==3:
                continue

            if position[1]>3 and position[0]<21:
                floor_btn = QPushButton(str(position[1]-3)+str(21-position[0]))
                #floor_btn.setStyleSheet("color: blue")
                floor_btn.clicked.connect(self.floor_clicked)
                self.elebtn.append(floor_btn)
                grid.addWidget(floor_btn, *position)

            if position in open_pos:
                o_pos = (position[1]-4)*2+position[0]-21
                btn=QPushButton(cmd_names[o_pos])
                grid.addWidget(btn,*position)
        opendoor_send.sendMsg.connect(self.opendoor)#接收开门信息
        closedoor_send.sendMsg.connect(self.closedoor)#接收关门信息

        self.move(300, 150)
        self.setWindowTitle('Calculator')
        self.show()

    def opendoor(self,msg):#开门，将按钮设为绿色
        id = int(msg[0])
        floor_value = 1
        if int(msg) < 100:  # 10层一下
            floor_value = int(msg) % 10
        else:
            floor_value = int(msg) % 100
        num=(20-floor_value)*5+id
        self.elebtn[num].setStyleSheet("background-color:green")

    def closedoor(self,msg):#关门，将按钮设为原来颜色

        id = int(msg[0])
        floor_value = 1
        if int(msg) < 100:  # 10层一下
            floor_value = int(msg) % 10
        else:
            floor_value = int(msg) % 100
        floor_num = (20 - floor_value) * 5 + id
        self.elebtn[floor_num].setStyleSheet('')

    def slot_hand(self,msg):    #回调函数，收到消息之后将显示屏上的值更改
        id = int(msg[0])
        floor_value=1
        if int(msg)<100:#10层一下
            floor_value=int(msg)%10
        else:
            floor_value=int(msg)%100

        self.lcd[id].display(floor_value)

    def up_down_button_clicked(self):   #上下楼按钮槽函数
        sender = self.sender()
        txt=sender.text()
        if txt == '':
            print('this is not allowed')
            return
        type=0
        value=0
        if txt[0]=='u':
            type = 2
            value = int(txt[3] + txt[4])
        elif txt[0]=='d':
            type= 3
            value = int(txt[5] + txt[6])
        m = Msg(type, value)
        for i  in range(5):
            MsgQueue[i].append(m)
        print("产生消息编码:" + str([m.type, m.value]))

    def floor_clicked(self):        #电梯内部槽函数
        sender = self.sender()
        txt = sender.text()
        id=int(txt[0])-1
        value=1
        if int(txt)<100:
            value=int(txt)%10
        else:
            value=int(txt)%100
        m = Msg(1, value)
        MsgQueue[id].append(m)


def closed(state, cur, d,id):

    if d == 1:
        if startup(cur,d,id):
            state = 2
        else:
            d = 0
            if startup(cur,d,id):
                state = 3
            else:
                return state,cur,d
    else:
        if startup(cur,d,id):
            state = 3
        else:
            d = 1
            if startup(cur,d,id):
                state = 2
            else:
                return state,cur,d
    return state,cur,d


def up(state,cur,d,id):
    while True:
        state = state
        if stop(cur,d,id):
            state = 1
            print("当前状态:%s,当前楼层:%d,运行方向：%s" % (STATE[state], cur, DIR[d]))
            break
        cur +=1
        print("正在前往第%d层..." % cur)
        floor_send.sendMsg.emit(str(id)+str(cur))
        time.sleep(2)
    return state,cur,d


def down(state,cur,d,id):
    while True:
        state = state
        if stop(cur,d):
            state = 1
            print("当前状态:%s,当前楼层:%d,运行方向：%s" % (STATE[state], cur, DIR[d]))
            break
        cur -=1
        print("正在前往第%d层..." % cur)
        floor_send.sendMsg.emit(str(id)+str(cur))
        time.sleep(2)
    return state, cur, d


def startup(cur,d,id):
    global MsgQueue
    tmp = False
    if d == 1:
        for m in MsgQueue[id]:
            if m.type == 1 and m.value > cur:
                tmp = True
            if m.type == 2 and m.value > cur:
                tmp = True
            if m.type == 3 and m.value > cur:
                tmp = True
    if d == 0:
        for m in MsgQueue[id]:
            if m.type == 1 and m.value < cur:
                tmp = True
            if m.type == 2 and m.value < cur:
                tmp = True
            if m.type == 3 and m.value < cur:
                tmp = True

    return tmp


def stop(cur,d,id):
    global MsgQueue
    tmp = False
    if d == 1 or d==0:
        if cur == TOP:
            tmp = True
        tmplist = MsgQueue[id][:]
        for m in MsgQueue[id]:
            if m.type == 1 and m.value == cur:
                tmp = True
                tmplist.remove(m)
            if m.type == 2 and m.value == cur:
                tmp = True
                tmplist.remove(m)
            if m.type == 3 and m.value == cur:
                tmp = True
                tmplist.remove(m)
        MsgQueue[id]= tmplist[:]
    if d == 0:
        if cur == BOTTOM:
            tmp = True
        tmplist = MsgQueue[id][:]
        for m in MsgQueue[id]:
            if m.type == 1 and m.value == cur:
                tmp = True
                tmplist.remove(m)
            if m.type == 2 and m.value == cur:
                tmp = True
                tmplist.remove(m)
            if m.type == 3 and m.value == cur:
                tmp = True
                tmplist.remove(m)
        MsgQueue[id] = tmplist[:]
    return tmp


def closeThread(arg):
    global exitFlag
    print("正在关门...")
    if exitFlag[arg] != [1]:
        print("关门终止")
    time.sleep(1)
    print("已关门")



def closedoor(id):

    t = threading.Thread(target=closeThread,args=(id,))
    t.start()
    t.join()



def openThread(arg):
    global exitFlag
    print("正在开门...")
    if exitFlag[arg] != [1]:
       print("开门终止")
    time.sleep(1)
    print("已开门")


def opendoor(id):

    t = threading.Thread(target=openThread,args=(id,))
    t.start()
    t.join()

def statemachine(arg):
    global MsgQueue,exitFlag
    id=arg #电梯id
    print(id)
    while True:
        time.sleep(0.3)
        print("当前状态:%s,当前楼层:%d,运行方向：%s" % (elevators[id].state, elevators[id].floor, elevators[id].dir))
        if MsgQueue[id] == [] and elevators[id].state == 1:
            continue
        if exitFlag[id] != []:
            tmplist = MsgQueue[id][:]
            for m in tmplist:
                if m.type == 0 and m.value == 0:#00表示关门
                    if elevators[id].state == 0:
                        elevators[id].state = 1
                        closedoor(id)
                        closedoor_send.sendMsg.emit(str(id)+str(elevators[id].floor))
                    exitFlag[id].pop(0)
                    tmplist.remove(m)
                if m.type == 0 and m.value == 1:#01表示开门
                    if elevators[id].state == 1 or elevators[id].state == 0:
                        elevators[id].state = 0
                        opendoor(id)
                        opendoor_send.sendMsg.emit(str(id)+str(elevators[id].floor))
                    exitFlag[id].pop(0)
                    tmplist.remove(m)
                if m.type == 0 and m.value == 2:#02表示有人进门，并且把们关上
                    if elevators[id].state == 1:
                        elevators[id].state = 0
                        opendoor(id)
                        opendoor_send.sendMsg.emit(str(id)+str(elevators[id].floor))
                    exitFlag[id].pop(0)
                    tmplist.remove(m)
            MsgQueue[id] = tmplist[:]
            continue

        if elevators[id].state == 0:#门停开着
            counter = 2
            while counter:
                if exitFlag[id] != []:
                    print("超时终止")
                    break
                time.sleep(1)
                counter -= 1
            if counter == 0:
                print("超时")
                exitFlag[id].append(1)
                closedoor(id)
                closedoor_send.sendMsg.emit(str(id)+str(elevators[id].floor))
                exitFlag[id].pop(0)
                elevators[id].state = 1
            continue
        if elevators[id].state == 1:#门停关着
            if MsgQueue[id] == []:
                continue
            elevators[id].state, elevators[id].floor, elevators[id].dir= closed(elevators[id].state,
                                                                             elevators[id].floor, elevators[id].dir,id)
            continue
        if elevators[id].state == 2:#电梯上升
            if MsgQueue[id] == []:
                continue
            elevators[id].state, elevators[id].floor, elevators[id].dir = up(elevators[id].state,
                                                                              elevators[id].floor, elevators[id].dir,id)
            if elevators[id].state == 1:
                exitFlag[id].append(1)
                opendoor(id)
                opendoor_send.sendMsg.emit(str(id)+str(elevators[id].floor))
                exitFlag[id].pop(0)
                elevators[id].state = 0
            continue
        if elevators[id].state == 3:#电梯下降
            if MsgQueue[id] == []:
                continue
            elevators[id].state, elevators[id].floor, elevators[id].dir = down(elevators[id].state,
                                                                          elevators[id].floor, elevators[id].dir,id)

            if elevators[id].state == 1:
                exitFlag[id].append(1)
                opendoor(id)
                opendoor_send.sendMsg.emit(str(id)+str(elevators[id].floor))
                exitFlag[id].pop(0)
                elevators[id].state = 0
            continue


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    for i in range(5):
        thread1 = threading.Thread(target=statemachine,args=(i,))
        thread1.start()
    sys.exit(app.exec_())
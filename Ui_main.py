import sys
from PyQt5.QtWidgets import QApplication, QWidget,QToolTip,QPushButton,QMessageBox,QDesktopWidget,QMainWindow
from PyQt5.QtCore import QCoreApplication,QTimer
import serial 
import serial.tools.list_ports
from Ui_SerialUI import Ui_MainWindow
import datetime
import matplotlib.pyplot as plt


class Py_Serial(QMainWindow,Ui_MainWindow):
    def __init__(self, parent=None):
        super(Py_Serial, self).__init__(parent)
        
        self.setupUi(self)
        self.com= None
        self.spin_time = 1
        self.timeshow = True
        self.send_show =True
        self.wrap = True

        self.bytes = 1
        self.draw_num = 1
        self.draw =False
        self.x_list=[0]
        self.y_list = [0]
        self.add_byte = 1
        
        self.send_hex=False
        self.receive_hex=False

        self.tx_num = 0
        self.rx_num = 0
        self.port = None
        self.initUI()
    
    def initUI(self):
        self.timer = QTimer(self)
        self.send_timer  = QTimer(self)
        self.info_timer = QTimer(self)

        self.info_timer.start(1)
        #self.Serial_Choose()
        #初次自动读取可用串口
        self.refresh_com() 
        #串口读取
        self.timer.timeout.connect(self.Serial_Read)
        #发送按钮
        self.send_button.clicked.connect(self.click_send_button)
        #串口选择
        self.com_choose_button.clicked.connect(self.com_choose)
        #串口刷新
        self.com_find_button.clicked.connect(self.refresh_com)
        
        #是否显示时间
        self.time_checkBox.clicked.connect(self.timeshow_check)

        #HEX
        self.receive_hex_checkBox.clicked.connect(self.receive_hex_check)
        self.send_hex_checkBox.clicked.connect(self.send_hex_check)
        #自动换行
        self.wrap_checkBox.clicked.connect(self.wrap_check)
        #自动发送
        self.auto_send_checkBox.clicked.connect(self.send_setting)
        self.send_timer.timeout.connect(self.click_send_button)
        #显示发送
        self.sendshow_checkBox.clicked.connect(self.sendshow_check)
        #画图
        self.draw_checkBox.clicked.connect(self.draw_check)

        #信息刷新
        self.info_timer.timeout.connect(self.info_refresh)



        self.bps_choose_box.addItem('115200')
        self.bps_choose_box.addItem('57600')
        self.bps_choose_box.addItem('56000')
        self.bps_choose_box.addItem('38400')
        self.bps_choose_box.addItem('19200')
        self.bps_choose_box.addItem('14400')
        self.bps_choose_box.addItem('9600')
        self.bps_choose_box.addItem('4800')
        self.bps_choose_box.addItem('2400')
        self.bps_choose_box.addItem('1200')

        #数据位控件
        self.num_choose_box.addItem('8')
        self.num_choose_box.addItem('7')
        self.num_choose_box.addItem('6')
        self.num_choose_box.addItem('5')

        #停止位控件
        self.stop_choose_box.addItem('1')
        self.stop_choose_box.addItem('1.5')
        self.stop_choose_box.addItem('2')

        #校验位控件
        self.check_choose_box.addItem('NONE')
        self.check_choose_box.addItem('ODD')
        self.check_choose_box.addItem('EVEN')
    
    def draw_check(self):
        if(self.draw_checkBox.checkState()):
            self.draw = True
            self.bytes = int(self.spinBox_2.value())
        else:
            self.draw = False

        plt.ion() #开启interactive mode 成功的关键函数
        plt.figure(1)

    def info_refresh(self):
        self.info_label.setText(str(self.port)+"  "+ "Opened")
        self.rx_label.setText("RX"+" : "+str(self.rx_num) +" Bytes")
        self.tx_label.setText("TX"+" : "+str(self.tx_num) +" Bytes")

        if self.draw:
            add_x = self.x_list[-1]
            add_y = self.y_list[-1]
            tmp = self.add_byte
            if(self.add_byte==self.bytes):
                plt.plot(add_x,add_y,'.')
                plt.draw()
                plt.pause(1e-15)
            elif self.add_byte>self.bytes:
                while(self.add_byte>=self.bytes):

                    if(self.add_byte>tmp):
                        return
                    show_y = int(add_y/(10**(abs(self.add_byte-self.bytes))))
                    add_y = add_y - show_y * (10**abs(self.add_byte-self.bytes))

                    self.add_byte=self.add_byte -1
                    tmp = self.add_byte
                    plt.plot(add_x,show_y,'.')
                    add_x = add_x + 1

                    plt.draw()
                    plt.pause(1e-15)
                


    #是否显示发送
    def receive_hex_check(self):
        if(self.receive_hex_checkBox.checkState()):
            self.receive_hex = True
        else:
            self.receive_hex = False

    #是否显示发送
    def send_hex_check(self):
        if(self.send_hex_checkBox.checkState()):
            self.send_hex = True
        else:
            self.send_hex = False

    #是否显示发送
    def sendshow_check(self):
        if(self.sendshow_checkBox.checkState()):
            self.send_show = True
        else:
            self.send_show = False

    #是否换行
    def wrap_check(self):
        if(self.wrap_checkBox.checkState()):
            self.wrap = True
        else:
            self.wrap = False

    #是否显示时间
    def timeshow_check(self):
        print(self.time_checkBox.checkState())
        if(self.time_checkBox.checkState()):
            
            self.timeshow = True
        else:
            self.timeshow = False

    # 定时器接收数据
    def send_setting(self):
        if(self.auto_send_checkBox.checkState()):
            self.spin_time= int(self.spinBox.value())
            self.send_timer.start(self.spin_time)
        else:
            self.send_timer.stop()
    
    #串口选择，按打开
    def com_choose(self):
        port = self.com_choose_box.currentText()
        bps = self.bps_choose_box.currentText()

        try:
            if(self.com!=None):
                self.timer.stop()
                self.com.close()
            
            self.com=serial.Serial(port , bps,timeout = 1, rtscts=False)
            self.timer.start(1)
            self.port=port
        except:
            print("打不开此串口，请检查")

    #串口刷新
    def refresh_com(self):
        self.com_choose_box.clear()
        port_list = list(serial.tools.list_ports.comports())#获取可用串口
        if len(port_list) == 0:
            self.com_choose_box.addItem("无可用串口")
            print('无可用串口')
            return None
        else:
            print("可用串口：")
            for i in range(0,len(port_list)):
                print("---",port_list[i])
                self.com_choose_box.addItem(port_list[i].device)


    #发送按键
    def click_send_button(self):
        if self.com!=None and self.com.isOpen():
            try:
                text= self.write_text.toPlainText()
                self.tx_num = self.tx_num + len(str(text))
                
                if self.send_hex:
                    self.com.write(bytes.fromhex(text))
                else:
                    self.com.write(text.encode("gbk"))

                if self.send_show:
                    if self.timeshow:
                        text = " [发送] "+str(datetime.datetime.now().strftime("%H:%M:%S")) + " -> " + text
                    else:
                        text = " [发送] "+ ":" + text
                    if self.wrap:
                        self.receive_text.append(text)
                    else:
                        self.receive_text.insertPlainText(text)
            except:
                return
    
    #读取串口
    def Serial_Read(self):
        if self.com!=None and self.com.isOpen():
            try:
                num = self.com.inWaiting()
                data = self.com.read(num)

                if self.receive_hex:
                    data = ''.join('%02x ' % t for t in data)
                else:
                    data=data.decode('gbk')
                read_byte =len(str(data))
                self.rx_num = self.rx_num + read_byte 
                data = str(data)

                if data != '':
                    if self.timeshow:
                        read_txt = " [收到] "+str(datetime.datetime.now().strftime("%H:%M:%S")) + " -> " + data
                    else:
                        read_txt = " [收到] "+ data
                    if self.wrap:
                        self.receive_text.append(read_txt)
                    else:
                        self.receive_text.insertPlainText(read_txt)
                    
                    if self.draw:
                        self.x_list.append(self.draw_num+1)
                        self.draw_num= self.draw_num + read_byte
                        self.add_byte = read_byte
                        
                        self.y_list.append(int(data))
            except:
                return
                
    #选择串口，调试用
    def Serial_Choose(self):
        port_list = list(serial.tools.list_ports.comports())#获取可用串口
        if len(port_list) == 0:
            print('无可用串口')
            return None
        else:
            print("可用串口：")
            for i in range(0,len(port_list)):
                print(port_list[i])
            while True:
                port = input("请输入所选串口")
                for i in range(0,len(port_list)):
                    if port == port_list[i].device:
                        bps=115200
                        self.com=serial.Serial(port , bps,timeout = 1, rtscts=False)
                        self.timer.start(2)
                        return 
            print("请选择正确的串口")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    MainWindow = Py_Serial()
    MainWindow.show()
    sys.exit(app.exec_())
## Serial_Tool
串口调试助手，基于pyqt5与pyserial，练手
昨天晚上初步学了一下Pyqt，顺手写一个串口调试助手联手，本想融合常规串口助手的收发功能与匿名科创的实时画图功能。
花费了下午&&晚上，基本功能有了，暂时没有更多的时间去调试细节与一些已知Bug，以后有空再说~

## 基本界面

与常规串口调试功能类似

Bug: Hex发送转码需要一些改进

![show](https://github.com/C-ZiHao/Serial_Tool/blob/main/serial.png)


## 画图功能

选择指定字节的数字进行画图，Byte在右下角文本框指定，暂时只支持画收到的一条曲线，多线太麻烦暂时没时间~

Bug: 串口发送速度快漏数据
     
![draw](https://github.com/C-ZiHao/Serial_Tool/blob/main/draw.png)

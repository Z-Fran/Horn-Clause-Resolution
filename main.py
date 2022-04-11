"""
模块名:   main
功能：    定义了mainWindow类，实现各种功能
         定义了主函数
"""
#导入相关包
import sys
import traceback
from PyQt5.QtWidgets import QMainWindow,QWidget
from PyQt5.QtWidgets import QApplication,QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer,QRect,Qt
from PyQt5.QtGui import QPainter,QColor
#导入项目的其他模块
import HornResolution
from mainUI import *

"""
函数名: swapString
参数：  i，j：两个字符的位置
       string：字符串 
功能： 交换字符串中的两个字符
"""
def swapString(string,i,j):
    temp = string[j]
    trailer = string[j+1:] if j + 1 < len(string) else ''
    string = string[0:j] + string[i] + trailer
    string = string[0:i] + temp + string[i+1:]
    return string

"""
类：显示树的窗口
"""
class TreeWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.tree = []#树的结构
        self.treexy= []
        self.X=1000#默认宽度
        self.Y=1000#默认高度
        self.high = 0
        self.isDraw=False#是否开始绘制树
        self.initUI()#初始化函数
    def initUI(self):
        self.setMinimumSize(self.X, self.Y) 
        
    """
    方法名: paintEvent
    参数：  e：事件
    功能： 执行绘制事件
    """
    def paintEvent(self, e):
        if self.isDraw:
            qp = QPainter()#定义绘制指针
            qp.begin(self)
            self.X = 800
            self.Y = len(self.tree) * 180
            nodew = 200
            nodeh = 30
            self.treexy=[]
            xy = [[30+50+nodew,30],[30,30]]
            self.treexy.append(xy)
            for i in range(1,len(self.tree)):
                if i % 2 == 0:
                    xy = [[self.treexy[i-1][0][0]+nodew/2+25,self.treexy[i-1][0][1]+150],
                          [self.treexy[i-1][0][0]+nodew/2+25-nodew-50,self.treexy[i-1][0][1]+150]]
                else:
                    xy = [[self.treexy[i - 1][1][0] + nodew / 2 + 25, self.treexy[i - 1][0][1] + 150],
                          [self.treexy[i - 1][1][0] + nodew / 2 + 25 + nodew + 50, self.treexy[i - 1][0][1] + 150]]
                self.treexy.append(xy)
            self.setMinimumSize(self.X, self.Y)#设置窗口大小
            self.drawNode(qp)#绘制树
            qp.end()
    
    #绘制树节点
    def drawNode(self,qp):
        nodew = 200
        nodeh = 30
        for i in range(len(self.treexy)):
            str = ""
            for s in self.tree[i - 1][-1]:
                str+=' '+s
            for j in range(len(self.treexy[i])):
                qp.drawText(self.treexy[i][j][0]+20, self.treexy[i][j][1]+20, self.tree[i][j])
                qp.drawRect(self.treexy[i][j][0], self.treexy[i][j][1], nodew, nodeh)
            qp.drawText(self.treexy[i][0][0] + nodew / 2 + 20, self.treexy[i][0][1] - 10, str)
        for i in range(1,len(self.treexy)):
            qp.drawLine(self.treexy[i][0][0]+nodew/2,self.treexy[i][0][1],
                self.treexy[i-1][0][0]+nodew/2,self.treexy[i-1][0][1]+nodeh)
            qp.drawLine(self.treexy[i][0][0] + nodew / 2, self.treexy[i][0][1],
                self.treexy[i - 1][1][0] + nodew / 2, self.treexy[i - 1][1][1] + nodeh)
        xy = [(self.treexy[-1][0][0]+self.treexy[-1][1][0])/2 + 25, self.treexy[-1][0][1] + 150]
        qp.drawLine(xy[0] + nodew / 2, xy[1],self.treexy[-1][0][0] + nodew / 2, self.treexy[-1][0][1] + nodeh)
        qp.drawLine(xy[0] + nodew / 2, xy[1],self.treexy[-1][1][0] + nodew / 2, self.treexy[-1][1][1] + nodeh)
        qp.drawText(xy[0] + 20, xy[1] + 20, "NIL")
        qp.drawRect(xy[0], xy[1], nodew, nodeh)
        str=""
        for s in self.tree[-1][-1]:
            str += ' ' + s
        qp.drawText(xy[0] + nodew / 2 + 20, xy[1] - 10, str)

"""
类：主窗口
"""          
class mainWindow(QMainWindow,mainUI):#主窗口继承自QMainWindow和mainUI
    """
    构造函数
    """   
    def __init__(self,parent=None):
        super(mainWindow, self).__init__(parent)
        self.setupUi(self)#初始化UI界面
        self.clause=""
        #绘制树的滚动窗口
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setGeometry(QRect(500, 0, 700, 700))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.treewindow=TreeWindow()
        self.scrollArea.setWidget(self.treewindow)
        self.vBar = self.scrollArea.verticalScrollBar()
        self.hBar = self.scrollArea.horizontalScrollBar()

        self.readfile.clicked.connect(self.ReadFile)
        self.AddButton.clicked.connect(self.AddClause)
        self.DelButton.clicked.connect(self.DelClause)
        self.reset.clicked.connect(self.Reset)
        self.run.clicked.connect(self.Run)
        self.btn.clicked.connect(self.dialog.close)
        self.show()

    # 读取文件内容
    def ReadFile(self):
        input = open("input.txt", "r")
        str = input.readlines()
        for i in str:
            self.clause+=i
        print(self.clause)
        self.ClauseText.setPlainText(self.clause)

    #添加子句
    def AddClause(self):
        text = self.ClauseEdit.text()
        if text == "":
            return
        self.ClauseEdit.clear()
        if self.clause == "":
            self.clause+=text
        else:
            self.clause+='\n'+text
        self.ClauseText.setPlainText(self.clause)
    #删除子句
    def DelClause(self):
        index = self.clause.rfind('\n')
        if index == -1:
            self.clause = ""
        else:
            self.clause = self.clause[0:index]
        self.ClauseText.setPlainText(self.clause)
    """
    方法名: reset
    参数：  
    功能：  重置程序
    """
    def Reset(self):
        self.clause=""
        self.ClauseText.setPlainText(self.clause)
        self.ClauseEdit.clear()
        self.ClauseResult.clear()
            
    """
    方法名: Run
    参数：
    功能：  开始运行
    """
    def Run(self):
        try:
            #显示运行弹出框
            self.dialog.show()
            #执行完毕之后使“继续”按钮生效
            self.btn.setEnabled(True)
            flag,self.treewindow.tree = HornResolution.Run(self.clause,self.ClauseResult.text())
            if flag == False:
                self.treewindow.isDraw=False
                self.label_run.setText("归结失败！")
            #目标可达的情况
            else:
                self.label_run.setText("归结成功！")
                self.treewindow.isDraw=True
        #运行出错
        except:
            self.label_run.setText("运 行 出 错")
            print(traceback.format_exc())  #输出异常信息
            pass

#主函数                
if __name__ == '__main__':
    app = QApplication(sys.argv)#获取命令行参数
    myWin = mainWindow()#实例化窗口
    myWin.show()
    sys.exit(app.exec_())
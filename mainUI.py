"""
模块名:   mainUI
功能：    定义了mainUI类，用于绘制 UI 界面
"""
#导入相关包
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication,QStyleFactory

#定义类：mainUI
class mainUI(object):
    #界面初始化函数
    def setupUi(self, mainUI):
        #设置主窗口大小、标题、风格等
        mainUI.setObjectName("mainUI")
        mainUI.setFixedSize(1200, 720)
        mainUI.setWindowTitle('子句归结实验')
        QApplication.setStyle(QStyleFactory.create("Fusion"))
        
        """
        设置弹出输入框和对话框
        """
        #弹出输入框
        self.inputDialog=QtWidgets.QInputDialog()
        #弹出对话框
        self.dialog=QtWidgets.QWidget()
        self.dialog.setFixedSize(400, 200)
        self.dialog.setWindowModality(Qt.ApplicationModal)
        self.dialog.setWindowFlags(Qt.FramelessWindowHint)
        self.dialog.setObjectName("dialog") 
        self.dialog.setStyleSheet("#dialog{background-color: #6495ED}")
        self.dialog.setWindowOpacity(0.8)
        self.label_run=QtWidgets.QLabel(self.dialog) 
        #设置字体
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(24)
        #弹出对话框中得文字和按钮
        self.label_run.setGeometry(QtCore.QRect(50, 20, 300, 100))
        self.label_run.setFont(font)
        self.label_run.setAlignment(QtCore.Qt.AlignCenter)
        self.label_run.setText("运 * 行 * 中")
        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(14)
        self.btn=QtWidgets.QPushButton(self.dialog)
        self.btn.setGeometry(QtCore.QRect(150, 130, 100, 50))
        self.btn.setFont(font)
        self.btn.setText("  继  续  ")
        self.btn.setEnabled(False)
        

        font = QtGui.QFont()
        font.setFamily("楷体")
        font.setPointSize(16)
        self.initText = QtWidgets.QLabel(mainUI)
        self.initText.setGeometry(QtCore.QRect(50, 10, 300, 30))
        self.initText.setFont(font)
        self.initText.setText("子 * 句 * 归 * 结")
        #读取文件
        self.readfile=QtWidgets.QPushButton(mainUI)
        self.readfile.setGeometry(QtCore.QRect(320, 10, 140, 30))
        self.readfile.setText("读入谋杀者实例")
        self.readfile.setObjectName("readfile")

        #输入框
        self.ClauseEdit=QtWidgets.QLineEdit(mainUI)
        self.ClauseEdit.setGeometry(QtCore.QRect(50, 50, 300, 30))
        reg = QtCore.QRegExp("^[a-zA-Z()|&~@,]+$")
        pValidator = QtGui.QRegExpValidator(mainUI)
        pValidator.setRegExp(reg)
        self.ClauseEdit.setValidator(pValidator)
        
        #添加子句
        self.AddButton=QtWidgets.QPushButton(mainUI)
        self.AddButton.setGeometry(QtCore.QRect(360, 50, 100, 30))
        self.AddButton.setText("添加子句")
        self.AddButton.setObjectName("AddButton")   
        
        #子句列表
        self.ClauseText=QtWidgets.QTextBrowser(mainUI)
        self.ClauseText.setGeometry(QtCore.QRect(50, 90, 410, 210))
        
        #重置
        self.reset = QtWidgets.QPushButton(mainUI)
        self.reset.setGeometry(QtCore.QRect(50, 310, 200, 30))
        self.reset.setText("重  置")
        self.reset.setObjectName("reset")

        #删除子句
        self.DelButton=QtWidgets.QPushButton(mainUI)
        self.DelButton.setGeometry(QtCore.QRect(260, 310, 200, 30))
        self.DelButton.setText("删除子句")
        self.DelButton.setObjectName(u"DelButton")   

        #结论
        font.setPointSize(12)
        self.label_r = QtWidgets.QLabel(mainUI)
        self.label_r.setGeometry(QtCore.QRect(50, 350, 150, 30))
        self.label_r.setFont(font)
        self.label_r.setText("输入结论")
        self.ClauseResult=QtWidgets.QLineEdit(mainUI)
        self.ClauseResult.setGeometry(QtCore.QRect(140, 350, 200, 30))
        self.ClauseResult.setValidator(pValidator)

        #开始归结
        self.run = QtWidgets.QPushButton(mainUI)
        self.run.setGeometry(QtCore.QRect(350, 350, 110, 30))
        self.run.setText("开始归结")
        self.run.setObjectName("run")

        #输入提示
        self.label_tip = QtWidgets.QLabel(mainUI)
        self.label_tip.setGeometry(QtCore.QRect(50, 400, 410, 30))
        self.label_tip.setFont(font)
        self.label_tip.setAlignment(QtCore.Qt.AlignCenter)
        self.label_tip.setText("输 * 入 * 提 * 示")
        self.TipText=QtWidgets.QTextBrowser(mainUI)
        self.TipText.setFontPointSize(16)
        self.TipText.setGeometry(QtCore.QRect(50, 440, 410, 210))
        self.TipText.setPlainText("常量 ----- 大写字母\n变量 ----- 小写字母\n函数 ----- @Fx\n"
                                  +"∨ ----- |\n∧ ----- &\n￢ ----- ~")
        #将信号与槽连接
        QtCore.QMetaObject.connectSlotsByName(mainUI)
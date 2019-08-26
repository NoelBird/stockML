import sys
import datetime

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *


class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("mainwindow.ui")
        self.time_start = 0
        self.time_end = 0
        self.upperLimit = 0
        self.lowerLimit = 0

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")

        # 함수 바인딩 부분
        self.ui.btnStart.clicked.connect(self.start) # 인공지능 투자 실행
        self.ui.btnEnd.clicked.connect(self.end) # 인공지능 투자 종료

        self.ui.btnSellPriceApply.clicked.connect(self.sellPriceApply)
        self.ui.btnSellPriceCancel.clicked.connect(self.sellPriceCancel)

        self.ui.actionLogIn.triggered.connect(self.login)
        self.ui.actionLogOut.triggered.connect(self.logout)
        self.ui.actionLogState.triggered.connect(self.logState)

        self.ui.show()
        # self.ui.previewSmall.setPixmap(QPixmap('cat04_256.png'))
    
    def start(self):
        data = self.getData() # 데이터 얻어오기
        result = self.analysis() # 분석(LSTM)
        self.buy() # 매입 요청
        self.monitoring() # TODO: 멀티쓰레딩으로 구현하기. 적정 주가 매도
    
    def end(self):
        # TODO: monitoring을 종료시키기
        pass
    
    def getData(self):
        pass

    def analysis(self): #TODO: 기본적으로 LSTM
        pass #TODO: 내일하기
    
    def buy(self):
        pass
    
    def monitoring(self):
        pass
    
    def sellPriceApply(self):
        self.upperLimit = self.ui.txtUpperLimit.text()
        self.lowerLimit = self.ui.txtLowerLimit.text()
        QMessageBox.about(self, "판매가 설정", "적용되었습니다.")
    
    def sellPriceCancel(self):
        self.ui.txtUpperLimit.setText('')
        self.ui.txtLowerLimit.setText('')
    
    def login(self):
        # self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
    
    def logout(self):
        pass
    
    def logState(self):
        ret = self.kiwoom.dynamicCall("GetConnectState()")
        _logState = "로그인 되어 있습니다." if ret else "로그인 되어 있지 않습니다."
        QMessageBox.about(self, "로그인 상태", _logState)




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())
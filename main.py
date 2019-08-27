# import open source
import sys
import datetime
import time

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import QThread, pyqtSignal
from threading import Thread

from pandas import DataFrame

# import own source
from Kiwoom import Kiwoom


# 키움증권은 1초에 5번의 전송만 됨 1초에 딱 5번을 위해 설정값
TR_REQ_TIME_INTERVAL = 0.2




class Form(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.ui = uic.loadUi("mainwindow.ui")
        self.time_start = 0
        self.time_end = 0
        self.upperLimit = 0
        self.lowerLimit = 0

        self.kiwoom = Kiwoom()

        # 함수 바인딩 부분
        self.ui.btnStart.clicked.connect(self.start) # 인공지능 투자 실행
        self.ui.btnEnd.clicked.connect(self.end) # 인공지능 투자 종료

        self.ui.btnSellPriceApply.clicked.connect(self.sellPriceApply)
        self.ui.btnSellPriceCancel.clicked.connect(self.sellPriceCancel)

        self.ui.actionLogIn.triggered.connect(self.login)
        self.ui.actionLogOut.triggered.connect(self.logout)
        self.ui.actionLogState.triggered.connect(self.logState)

        self.ui.show()

        self.ui.tblWgtTable.setItem(0 , 0, QTableWidgetItem("text1"))
        # self.ui.previewSmall.setPixmap(QPixmap('cat04_256.png'))
    
    def start(self):
        data = self.getData("005930","20190826") # 데이터 얻어오기
        print(data)
        print('Done')
        result = self.analysis() # 분석(LSTM)
        self.buy() # 매입 요청
        self.monitoring() # TODO: 멀티쓰레딩으로 구현하기. 적정 주가 매도
    
    def end(self):
        # TODO: monitoring을 종료시키기
        self.ui.lblRunningTime.setText('0:00:00')
    
    def getData(self, code, start):
        self.kiwoom.ohlcv ={'date': [], 'open': [],'high': [],'low': [],'close': [],'volume': []}

        
        self.kiwoom.set_input_value("종목코드", code) # 가져오고자 하는 종목에 대한 종목코드
        self.kiwoom.set_input_value("기준일자", start) # 가자오고자 하는 종목의 일자
        self.kiwoom.set_input_value("수정주가부분", 1)
        self.kiwoom.comm_rq_data("opt10081_req", "opt10081", 0, "0101")
        time.sleep(0.2) #tr요청시 0.2초 간격을 주기 위해 사용
         

        df = DataFrame(self.kiwoom.ohlcv, columns=['open','high','low','close','volume'],
            index=self.kiwoom.ohlcv['date'])

        return df

    def analysis(self): #TODO: 기본적으로 LSTM
        pass #TODO: 내일하기
    
    def buy(self):
        res = self.kiwoom.dynamicCall("GetLoginInfo(\"USER_NAME\")")
        print(res)
        # pass
    
    def monitoring(self):
        self.monitoringThread = MonitoringThread() # 쓰레드 생성
        self.ui.btnEnd.clicked.connect(self.monitoringThread.terminate)
        self.monitoringThread.sigUpdate.connect(self.updated)
        self.monitoringThread.start() # 쓰레드 시작
    
    def updated(self, duringTime):
        self.ui.lblRunningTime.setText("%s" % datetime.timedelta(seconds=duringTime))
    
    def sellPriceApply(self):
        self.upperLimit = self.ui.txtUpperLimit.text()
        self.lowerLimit = self.ui.txtLowerLimit.text()
        QMessageBox.about(self, "판매가 설정", "적용되었습니다.")
    
    def sellPriceCancel(self):
        self.ui.txtUpperLimit.setText('')
        self.ui.txtLowerLimit.setText('')
    
    def login(self):
        # self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.comm_connect()
    
    def logout(self):
        pass
    
    def logState(self):
        ret = self.kiwoom.dynamicCall("GetConnectState()")
        _logState = "로그인 되어 있습니다." if ret else "로그인 되어 있지 않습니다."
        QMessageBox.about(self, "로그인 상태", _logState)




class MonitoringThread(QThread):

    sigUpdate = pyqtSignal(int)
    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        i = 1
        while True:
            time.sleep(1)
            self.sigUpdate.emit(i)
            i += 1




if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = Form()
    sys.exit(app.exec())
import sys
import datetime
import time

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QIcon, QPixmap

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *

from pandas import DataFrame

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import pandas as pd


# 키움증권은 1초에 5번의 전송만 됨 1초에 딱 5번을 위해 설정값
TR_REQ_TIME_INTERVAL = 0.2

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        self.OnReceiveChejanData.connect(self._receive_chejan_data)

    def comm_connect(self):
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def _event_connect(self, err_code):
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    # 종목코드 추출 - 거래소별 0: 코스피, 10: 코스닥
    def get_code_list_by_market(self, market):
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    # 종목한글명 추출
    def get_master_code_name(self, code):
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    # 입력인자 설정
    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    # TR 요청
    def comm_rq_data(self, rqname, trcode, next, screen_no):
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    # 데이터 수신
    def _comm_get_data(self, code, real_type, field_name, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString",
                               code, real_type, field_name, index, item_name)
        return ret.strip()

    # 자료수
    def _get_repeat_cnt(self, trcode, rqname):
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    # TR 수신 - TR 추가시 수정
    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        ##  패키지마다 다름

        if rqname == "opt10001_req":         # 주식 기본정보
            self._opt10001(rqname, trcode)


        elif rqname == "opt10009_req":         # 주식기관요청 (기관/외국인 순매매)
            self._opt10009(rqname, trcode)


        elif rqname == "opt10038_req":         # 증권사별 매매상위쵸엉(메릴린치수량)
            self._opt10038(rqname, trcode)

        elif rqname == "opt10045_req":          # 종목별 기관매매추이요청(평단가)
            self._opt10038(rqname, trcode)

        elif rqname == "opt10080_req":          # 주식분봉차트조회요청
            self._opt10080(rqname, trcode)

        elif rqname == "opt10081_req":        # 주식일봉차트조회요청
            self._opt10081(rqname, trcode)

        elif rqname == "opw00001_req":        # 예수금 상세현황 요청
            self._opw00001(rqname, trcode)

        elif rqname == "opw00018_req":        # 계좌평가잔고내역요청
            print('ttt')
            self._opw00018(rqname, trcode)


        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    # 주문
    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                         [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])

    # 체결잔고
    def get_chejan_data(self, fid):
        ret = self.dynamicCall("GetChejanData(int)", fid)
        return ret

    #체결잔고수신
    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        print(gubun)
        print(self.get_chejan_data(9203))
        print(self.get_chejan_data(302))
        print(self.get_chejan_data(900))
        print(self.get_chejan_data(901))

    def get_login_info(self, tag):
        ret = self.dynamicCall("GetLoginInfo(QString)", tag)
        return ret

    @staticmethod
    def change_format(data):
        strip_data = data.lstrip('-0')
        if strip_data == '':
            strip_data = '0'

        format_data = format(int(strip_data), ',d')
        if data.startswith('-'):
            format_data = '-' + format_data

        return format_data

    @staticmethod
    def change_format2(data):
        strip_data = data.lstrip('-0')

        if strip_data == '':
            strip_data = '0'

        if strip_data.startswith('.'):
            strip_data = '0' + strip_data

        if data.startswith('-'):
            strip_data = '-' + strip_data

        return strip_data


    def get_server_gubun(self):
        ret = self.dynamicCall("KOA_Functions(QString, QString)", "GetServerGubun", "")
        return ret

    # 주식 기본정보
    def _opt10001(self, rqname, trcode):
        신용비율 = self._comm_get_data(trcode, "", rqname, 0, "신용비율")

    #
    def _opw00001(self, rqname, trcode):
        d2_deposit = self._comm_get_data(trcode, "", rqname, 0, "d+2추정예수금")
        self.d2_deposit = Kiwoom.change_format(d2_deposit)

    #
    def _opw00018(self, rqname, trcode):
        total_purchase_price = self._comm_get_data(trcode, "", rqname, 0, "총매입금액")
        total_eval_price     = self._comm_get_data(trcode, "", rqname, 0, "총평가금액")
        total_eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, 0, "총평가손익금액")
        total_earning_rate = self._comm_get_data(trcode, "", rqname, 0, "총수익률(%)")
        estimated_deposit  = self._comm_get_data(trcode, "", rqname, 0, "추정예탁자산")

        if self.get_server_gubun():
            total_earning_rate = float(total_earning_rate) / 100
            total_earning_rate = str(total_earning_rate)

        self.opw00018_output['single'].append(Kiwoom.change_format(total_purchase_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_eval_profit_loss_price))
        self.opw00018_output['single'].append(Kiwoom.change_format(total_earning_rate))
        self.opw00018_output['single'].append(Kiwoom.change_format(estimated_deposit))

        # multi data
        rows = self._get_repeat_cnt(trcode, rqname)
        for i in range(rows):
            name     = self._comm_get_data(trcode, "", rqname, i, "종목명")
            quantity = self._comm_get_data(trcode, "", rqname, i, "보유수량")
            purchase_price = self._comm_get_data(trcode, "", rqname, i, "매입가")
            current_price  = self._comm_get_data(trcode, "", rqname, i, "현재가")
            eval_profit_loss_price = self._comm_get_data(trcode, "", rqname, i, "평가손익")
            earning_rate           = self._comm_get_data(trcode, "", rqname, i, "수익률(%)")

            quantity = Kiwoom.change_format(quantity)
            purchase_price = Kiwoom.change_format(purchase_price)
            current_price = Kiwoom.change_format(current_price)
            eval_profit_loss_price = Kiwoom.change_format(eval_profit_loss_price)
            earning_rate = Kiwoom.change_format2(earning_rate)

            self.opw00018_output['multi'].append([name, quantity, purchase_price, current_price,
                                                  eval_profit_loss_price, earning_rate])

            print(name, quantity, purchase_price, current_price, eval_profit_loss_price, earning_rate)

    #
    def reset_opw00018_output(self):
        self.opw00018_output = {'single': [], 'multi': []}


    # opt10080 TR 요청 -> 분봉 데이터 요청
    def _opt10080(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)
        print('tt2---222')

        for i in range(data_cnt):
            date   = self._comm_get_data(trcode, "", rqname, i, "체결시간")
            open   = self._comm_get_data(trcode, "", rqname, i, "시가")
            high   = self._comm_get_data(trcode, "", rqname, i, "고가")
            low    = self._comm_get_data(trcode, "", rqname, i, "저가")
            close  = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))


    # opt10080 TR 요청 -> 일봉 데이터 요청
    def _opt10081(self, rqname, trcode):
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date   = self._comm_get_data(trcode, "", rqname, i, "일자")
            open   = self._comm_get_data(trcode, "", rqname, i, "시가")
            high   = self._comm_get_data(trcode, "", rqname, i, "고가")
            low    = self._comm_get_data(trcode, "", rqname, i, "저가")
            close  = self._comm_get_data(trcode, "", rqname, i, "현재가")
            volume = self._comm_get_data(trcode, "", rqname, i, "거래량")

            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))


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
        # self.ui.previewSmall.setPixmap(QPixmap('cat04_256.png'))
    
    def start(self):
        data = self.getData("005930","20190826") # 데이터 얻어오기
        print(data)
        print('Done')
        # result = self.analysis() # 분석(LSTM)
        # self.buy() # 매입 요청
        # self.monitoring() # TODO: 멀티쓰레딩으로 구현하기. 적정 주가 매도
    
    def end(self):
        # TODO: monitoring을 종료시키기
        pass
    
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
    
    def buy(self, result):
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
        self.kiwoom.comm_connect()
    
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
import sys

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import *

from PySide6.QtCore import QTimer

class TennisScheduleWindow(QWidget):
    def __init__(self, tennis_schedule):
        super().__init__()
        self.tennis_schedule = tennis_schedule
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.table = QTableWidget(self)
        self.table.horizontalHeader().setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.load_data_into_table()
        self.layout.addWidget(self.table)
        self.adjust_frame_size(len(self.tennis_schedule))

    def adjust_frame_size(self, size):
        self.table.adjustSize()
        self.adjustSize()
        self.resize(18 * size, 300)

    def load_data_into_table(self):
        # 테이블 사이즈 조절

        # 코트별로 데이터 분리
        courts = {}
        for key, value in self.tennis_schedule.items():
            court_name = value["fcltNm"]
            if court_name not in courts:
                courts[court_name] = []
            courts[court_name].append(
                (value["useBeginHm"] + "-" + value["useEndHm"], value["reserveYn"])
            )

        # 각 코트별로 시간대 정렬
        for court in courts:
            courts[court].sort()

        # 테이블 구성
        self.table.setColumnCount(len(courts))
        self.table.setRowCount(len(courts[list(courts.keys())[0]]))
        self.table.setHorizontalHeaderLabels(list(courts.keys()))

        # 데이터 삽입
        for col, court in enumerate(courts.keys()):
            for row, (time, status) in enumerate(courts[court]):
                item = QTableWidgetItem(time)
                if status == "Y":
                    item.setBackground(QColor(0, 0, 255))  # 파란색
                    item.setForeground(QBrush(Qt.GlobalColor.white))
                else:
                    item.setBackground(QColor(255, 0, 0))  # 빨간색
                    item.setForeground(QBrush(Qt.GlobalColor.white))
                self.table.setItem(row, col, item)

        # 테이블 헤더 크기 조절
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # 프레임 크기 조절
        self.adjustSize()


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        # 앱 타이틀
        # self.setWindowTitle(f"세종시 통합예약 시스템 도우미 v{current_version}")
        self.setWindowModality(Qt.NonModal)

        ##################################################
        # UI 시작
        ##################################################
        self.resize(485, 861)
        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.titleLbl = QLabel(self.centralwidget)
        self.titleLbl.setObjectName("titleLbl")
        self.titleLbl.setGeometry(QRect(20, 10, 351, 41))
        font = QFont()
        font.setPointSize(18)
        self.titleLbl.setFont(font)
        self.accountGb = QGroupBox(self.centralwidget)
        self.accountGb.setObjectName("accountGb")
        self.accountGb.setGeometry(QRect(30, 60, 431, 71))
        font1 = QFont()
        font1.setPointSize(13)
        self.accountGb.setFont(font1)
        self.idLbl = QLabel(self.accountGb)
        self.idLbl.setObjectName("idLbl")
        self.idLbl.setGeometry(QRect(30, 30, 60, 31))
        self.idLbl.setFont(font1)
        self.idCb = QComboBox(self.accountGb)
        self.idCb.setObjectName("idCb")
        self.idCb.setGeometry(QRect(110, 30, 171, 31))
        self.addAccountBtn = QPushButton(self.accountGb)
        self.addAccountBtn.setObjectName("addAccountBtn")
        self.addAccountBtn.setGeometry(QRect(290, 30, 61, 31))
        font2 = QFont()
        font2.setPointSize(8)
        self.addAccountBtn.setFont(font2)
        self.deleteAccountBtn = QPushButton(self.accountGb)
        self.deleteAccountBtn.setObjectName("deleteAccountBtn")
        self.deleteAccountBtn.setGeometry(QRect(360, 30, 61, 31))
        self.deleteAccountBtn.setFont(font2)
        self.label_3 = QLabel(self.centralwidget)
        self.label_3.setObjectName("label_3")
        self.label_3.setGeometry(QRect(260, 150, 60, 16))
        self.reserve1Gb = QGroupBox(self.centralwidget)
        self.reserve1Gb.setObjectName("reserve1Gb")
        self.reserve1Gb.setGeometry(QRect(30, 130, 431, 181))
        self.reserve1Gb.setFont(font1)
        self.date1Lbl = QLabel(self.reserve1Gb)
        self.date1Lbl.setObjectName("date1Lbl")
        self.date1Lbl.setGeometry(QRect(30, 55, 60, 30))
        self.date1Lbl.setFont(font1)
        self.time1Lbl = QLabel(self.reserve1Gb)
        self.time1Lbl.setObjectName("time1Lbl")
        self.time1Lbl.setGeometry(QRect(30, 85, 60, 30))
        self.time1Lbl.setFont(font1)
        self.tennisPlace1Lbl = QLabel(self.reserve1Gb)
        self.tennisPlace1Lbl.setObjectName("tennisPlace1Lbl")
        self.tennisPlace1Lbl.setGeometry(QRect(30, 120, 81, 20))
        self.tennisPlace1Lbl.setFont(font1)
        self.date1Cb = QComboBox(self.reserve1Gb)
        self.date1Cb.setObjectName("date1Cb")
        self.date1Cb.setGeometry(QRect(160, 60, 231, 26))
        self.time1Cb = QComboBox(self.reserve1Gb)
        self.time1Cb.setObjectName("time1Cb")
        self.time1Cb.setGeometry(QRect(160, 90, 231, 26))
        self.tennisPlace1Cb = QComboBox(self.reserve1Gb)
        self.tennisPlace1Cb.setObjectName("tennisPlace1Cb")
        self.tennisPlace1Cb.setGeometry(QRect(160, 120, 231, 26))
        self.reserveYNLbl1 = QLabel(self.reserve1Gb)
        self.reserveYNLbl1.setObjectName("reserveYNLbl1")
        self.reserveYNLbl1.setGeometry(QRect(30, 150, 141, 21))
        self.reserveChkBtn1 = QPushButton(self.reserve1Gb)
        self.reserveChkBtn1.setObjectName("reserveChkBtn1")
        self.reserveChkBtn1.setGeometry(QRect(30, 28, 361, 23))
        font3 = QFont()
        font3.setPointSize(9)
        self.reserveChkBtn1.setFont(font3)
        self.reserveMsgLbl1 = QLabel(self.reserve1Gb)
        self.reserveMsgLbl1.setObjectName("reserveMsgLbl1")
        self.reserveMsgLbl1.setGeometry(QRect(160, 150, 221, 16))
        self.reserve2Gb = QGroupBox(self.centralwidget)
        self.reserve2Gb.setObjectName("reserve2Gb")
        self.reserve2Gb.setGeometry(QRect(30, 320, 431, 181))
        self.reserve2Gb.setFont(font1)
        self.date2Lbl = QLabel(self.reserve2Gb)
        self.date2Lbl.setObjectName("date2Lbl")
        self.date2Lbl.setGeometry(QRect(30, 60, 60, 20))
        self.date2Lbl.setFont(font1)
        self.time2Lbl = QLabel(self.reserve2Gb)
        self.time2Lbl.setObjectName("time2Lbl")
        self.time2Lbl.setGeometry(QRect(30, 90, 60, 20))
        self.time2Lbl.setFont(font1)
        self.tennisPlace2Lbl = QLabel(self.reserve2Gb)
        self.tennisPlace2Lbl.setObjectName("tennisPlace2Lbl")
        self.tennisPlace2Lbl.setGeometry(QRect(30, 120, 81, 20))
        self.tennisPlace2Lbl.setFont(font1)
        self.date2Cb = QComboBox(self.reserve2Gb)
        self.date2Cb.setObjectName("date2Cb")
        self.date2Cb.setGeometry(QRect(160, 60, 231, 26))
        self.time2Cb = QComboBox(self.reserve2Gb)
        self.time2Cb.setObjectName("time2Cb")
        self.time2Cb.setGeometry(QRect(160, 90, 231, 26))
        self.tennisPlace2Cb = QComboBox(self.reserve2Gb)
        self.tennisPlace2Cb.setObjectName("tennisPlace2Cb")
        self.tennisPlace2Cb.setGeometry(QRect(160, 120, 231, 26))
        self.reserveChbox2 = QCheckBox(self.reserve2Gb)
        self.reserveChbox2.setObjectName("reserveChbox2")
        self.reserveChbox2.setGeometry(QRect(100, 2, 21, 16))
        self.reserveYNLbl2 = QLabel(self.reserve2Gb)
        self.reserveYNLbl2.setObjectName("reserveYNLbl2")
        self.reserveYNLbl2.setGeometry(QRect(30, 150, 141, 21))
        self.reserveChkBtn2 = QPushButton(self.reserve2Gb)
        self.reserveChkBtn2.setObjectName("reserveChkBtn2")
        self.reserveChkBtn2.setGeometry(QRect(30, 30, 361, 23))
        self.reserveChkBtn2.setFont(font3)
        self.reserveMsgLbl2 = QLabel(self.reserve2Gb)
        self.reserveMsgLbl2.setObjectName("reserveMsgLbl2")
        self.reserveMsgLbl2.setGeometry(QRect(170, 152, 221, 16))
        self.noticeGb = QGroupBox(self.centralwidget)
        self.noticeGb.setObjectName("noticeGb")
        self.noticeGb.setGeometry(QRect(30, 530, 431, 161))
        self.noticeGb.setFont(font1)
        self.noticeLbl4 = QLabel(self.noticeGb)
        self.noticeLbl4.setObjectName("noticeLbl4")
        self.noticeLbl4.setGeometry(QRect(10, 50, 411, 16))
        self.noticeLbl4.setFont(font3)
        self.noticeLbl1 = QLabel(self.noticeGb)
        self.noticeLbl1.setObjectName("noticeLbl1")
        self.noticeLbl1.setGeometry(QRect(10, 27, 391, 20))
        self.noticeLbl1.setFont(font3)
        self.noticeLbl5 = QLabel(self.noticeGb)
        self.noticeLbl5.setObjectName("noticeLbl5")
        self.noticeLbl5.setGeometry(QRect(10, 70, 411, 16))
        self.noticeLbl5.setFont(font3)
        self.noticeLbl6 = QLabel(self.noticeGb)
        self.noticeLbl6.setObjectName("noticeLbl6")
        self.noticeLbl6.setGeometry(QRect(10, 90, 411, 16))
        self.noticeLbl6.setFont(font3)
        self.noticeLbl8_2 = QLabel(self.noticeGb)
        self.noticeLbl8_2.setObjectName("noticeLbl8_2")
        self.noticeLbl8_2.setGeometry(QRect(10, 110, 411, 16))
        self.noticeLbl8_2.setFont(font3)
        self.noticeLbl8_3 = QLabel(self.noticeGb)
        self.noticeLbl8_3.setObjectName("noticeLbl8_3")
        self.noticeLbl8_3.setGeometry(QRect(10, 130, 411, 16))
        self.noticeLbl8_3.setFont(font3)
        self.coutionLbl = QLabel(self.centralwidget)
        self.coutionLbl.setObjectName("coutionLbl")
        self.coutionLbl.setGeometry(QRect(190, 815, 261, 20))
        font4 = QFont()
        font4.setPointSize(7)
        font4.setBold(False)
        font4.setItalic(True)
        font4.setKerning(True)
        self.coutionLbl.setFont(font4)
        self.line2 = QFrame(self.centralwidget)
        self.line2.setObjectName("line2")
        self.line2.setGeometry(QRect(30, 795, 421, 20))
        self.line2.setFrameShape(QFrame.HLine)
        self.line2.setFrameShadow(QFrame.Sunken)
        self.loginBtn = QPushButton(self.centralwidget)
        self.loginBtn.setObjectName("loginBtn")
        self.loginBtn.setGeometry(QRect(40, 705, 181, 41))
        self.loginBtn.setFont(font1)
        self.autoReserveBtn = QPushButton(self.centralwidget)
        self.autoReserveBtn.setObjectName("autoReserveBtn")
        self.autoReserveBtn.setGeometry(QRect(250, 750, 91, 41))
        self.autoReserveBtn.setFont(font3)
        self.selfReserveBtn = QPushButton(self.centralwidget)
        self.selfReserveBtn.setObjectName("selfReserveBtn")
        self.selfReserveBtn.setGeometry(QRect(250, 705, 181, 41))
        self.selfReserveBtn.setFont(font1)
        self.timeEdit = QTimeEdit(self.centralwidget)
        self.timeEdit.setObjectName("timeEdit")
        self.timeEdit.setGeometry(QRect(100, 760, 118, 24))
        self.timeSetLbl = QLabel(self.centralwidget)
        self.timeSetLbl.setObjectName("timeSetLbl")
        self.timeSetLbl.setGeometry(QRect(30, 763, 71, 16))
        self.currentTimeLbl = QLabel(self.centralwidget)
        self.currentTimeLbl.setObjectName("currentTimeLbl")
        self.currentTimeLbl.setGeometry(QRect(30, 815, 131, 16))
        self.stopAutoReserveBtn = QPushButton(self.centralwidget)
        self.stopAutoReserveBtn.setObjectName("stopAutoReserveBtn")
        self.stopAutoReserveBtn.setGeometry(QRect(340, 750, 91, 41))
        self.stopAutoReserveBtn.setFont(font3)
        self.darkModeChBox = QCheckBox(self.centralwidget)
        self.darkModeChBox.setObjectName("darkModeChBox")
        self.darkModeChBox.setGeometry(QRect(380, 25, 81, 16))
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi(self)

        QMetaObject.connectSlotsByName(self)
        # setupUi

    def retranslateUi(self, MainWindow):
        self.setWindowTitle(
            QCoreApplication.translate(
                "MainWindow",
                "\uc138\uc885\uc2dc \ud1b5\ud569 \uc608\uc57d \uc2dc\uc2a4\ud15c \ub3c4\uc6b0\ubbf8 ",
                None,
            )
        )
        self.titleLbl.setText(
            QCoreApplication.translate(
                "MainWindow",
                "\uc138\uc885\uc2dc \ud1b5\ud569 \uc608\uc57d \uc2dc\uc2a4\ud15c \ub3c4\uc6b0\ubbf8",
                None,
            )
        )
        self.accountGb.setTitle(
            QCoreApplication.translate("MainWindow", "\uacc4\uc815\uc815\ubcf4", None)
        )
        self.idLbl.setText(
            QCoreApplication.translate("MainWindow", "\uc544\uc774\ub514 : ", None)
        )
        self.addAccountBtn.setText(
            QCoreApplication.translate("MainWindow", "\uacc4\uc815\ub4f1\ub85d", None)
        )
        self.deleteAccountBtn.setText(
            QCoreApplication.translate("MainWindow", "\uacc4\uc815\uc0ad\uc81c", None)
        )
        self.label_3.setText("")
        self.reserve1Gb.setTitle(
            QCoreApplication.translate("MainWindow", "\uc608\uc57d\uc815\ubcf4 1", None)
        )
        self.date1Lbl.setText(
            QCoreApplication.translate("MainWindow", "\ub0a0 \uc9dc : ", None)
        )
        self.time1Lbl.setText(
            QCoreApplication.translate("MainWindow", "\uc2dc \uac04 : ", None)
        )
        self.tennisPlace1Lbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\ud14c\ub2c8\uc2a4\uc7a5 : ", None
            )
        )
        self.reserveYNLbl1.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80  : ", None
            )
        )
        self.reserveChkBtn1.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80 \ud655\uc778", None
            )
        )
        self.reserveMsgLbl1.setText("")
        self.reserve2Gb.setTitle(
            QCoreApplication.translate("MainWindow", "\uc608\uc57d\uc815\ubcf4 2", None)
        )
        self.date2Lbl.setText(
            QCoreApplication.translate("MainWindow", "\ub0a0 \uc9dc : ", None)
        )
        self.time2Lbl.setText(
            QCoreApplication.translate("MainWindow", "\uc2dc \uac04 : ", None)
        )
        self.tennisPlace2Lbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\ud14c\ub2c8\uc2a4\uc7a5 : ", None
            )
        )
        self.reserveChbox2.setText("")
        self.reserveYNLbl2.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80  : ", None
            )
        )
        self.reserveChkBtn2.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uac00\ub2a5 \uc5ec\ubd80 \ud655\uc778", None
            )
        )
        self.reserveMsgLbl2.setText("")
        self.noticeGb.setTitle(
            QCoreApplication.translate("MainWindow", "\uc774\uc6a9\uc548\ub0b4", None)
        )
        self.noticeLbl4.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ud55c\uac1c \uc608\uc57d\uc2dc, \uc608\uc57d\uc815\ubcf4 1\ub9cc \uc124\uc815,\ub450\uac1c \uc608\uc57d\uc2dc, \uc608\uc57d\uc815\ubcf41,2 \ubaa8\ub450 \uc791\uc131",
                None,
            )
        )
        self.noticeLbl1.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ucd08\uae30 \ud504\ub85c\uadf8\ub7a8 \uc2e4\ud589 \uc2dc, \uacc4\uc815\ub4f1\ub85d \ud6c4 \ub85c\uadf8\uc778 \ubc0f \uc608\uc57d\ud558\uae30 \uc9c4\ud589",
                None,
            )
        )
        self.noticeLbl5.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ub85c\uadf8\uc778 \ubc84\ud2bc\uc744 \ud074\ub9ad\ud558\uc5ec \ub85c\uadf8\uc778 \ud6c4, \uc608\uc57d\ud558\uae30 \ubc84\ud2bc\uc744 \ub20c\ub7ec\uc11c \uc608\uc57d",
                None,
            )
        )
        self.noticeLbl6.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \uc608\uc57d\uc2dc\uac04 \uc124\uc815 \ud6c4, \uc790\ub3d9\uc608\uc57d\ud558\uae30 \ud074\ub9ad\uc2dc \uc124\uc815\ub41c \uc2dc\uac04\uc5d0 \uc790\ub3d9\uc73c\ub85c \uc608\uc57d",
                None,
            )
        )
        self.noticeLbl8_2.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- data.dat, data.dat.hash, key.key \ud30c\uc77c \ubcc0\uacbd \ubc0f  \uc0ad\uc81c \uc2dc \uacc4\uc815 \uc7ac\ub4f1\ub85d \ud544\uc694",
                None,
            )
        )
        self.noticeLbl8_3.setText(
            QCoreApplication.translate(
                "MainWindow",
                "- \ub2e4\uc815\ub3d9\uacfc \uc804\uc758\uc0dd\ud65c\uacf5\uc6d0\uc758 \uacbd\uc6b0, \uc2dc\uac04\uc774 \ub2e4\ub978 \uad6c\uc7a5\uacfc \ub2e4\ub984 \uc608\uc57d\uc2dc \uc720\uc758",
                None,
            )
        )
        self.coutionLbl.setText(
            QCoreApplication.translate(
                "MainWindow",
                "* \ubd80\uc815 \uc608\uc57d(\ub9e4\ud06c\ub85c)\uc73c\ub85c \uc778\ud55c \ubd88\uc774\uc775 \ubc1c\uc0dd\uc2dc \ucc45\uc784\uc9c0\uc9c0 \uc54a\uc2b5\ub2c8\ub2e4.",
                None,
            )
        )
        self.loginBtn.setText(
            QCoreApplication.translate("MainWindow", "\ub85c\uadf8\uc778", None)
        )
        self.autoReserveBtn.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc790\ub3d9\uc608\uc57d\uc2dc\uc791", None
            )
        )
        self.selfReserveBtn.setText(
            QCoreApplication.translate("MainWindow", "\uc608\uc57d\ud558\uae30", None)
        )
        self.timeSetLbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc608\uc57d\uc2dc\uac04 : ", None
            )
        )
        self.currentTimeLbl.setText(
            QCoreApplication.translate(
                "MainWindow", "\ud604\uc7ac\uc2dc\uac04 : ", None
            )
        )
        self.stopAutoReserveBtn.setText(
            QCoreApplication.translate(
                "MainWindow", "\uc790\ub3d9\uc608\uc57d\uc911\uc9c0", None
            )
        )
        self.darkModeChBox.setText(
            QCoreApplication.translate("MainWindow", "\ub2e4\ud06c\ubaa8\ub4dc", None)
        )

        # retranslateUi

app = QApplication(sys.argv)


window = MainWindow()
window.show()

# 이벤트 루프 시작
app.exec()
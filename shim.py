# -*- coding:utf-8 -*-
import sys,os
import time
import math,random
import threading
import itertools
import Image

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PIL.ImageQt import ImageQt

class Window(QMainWindow):
    is_done = pyqtSignal()
    def __init__(self,parent=None):
        super(Window,self).__init__(parent)
        
        self.setAcceptDrops(True)
        self.showFullScreen()
        self.width = self.width()
        self.height = self.height()
        
        #create a shimeji
        self.label = Shimeji(self,self.width,self.height,100,100)
        self.label.show()
        self.label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.label.customContextMenuRequested.connect(self.menu)
        
        #create a message label
        self.label_two = AlertMessage(self,self.label)
        self.label.is_moved.connect(self.label_two.follow)
        
        self.is_done.connect(self.play_song)        
        self.process = threading.Thread()
        self.stop_parent_event = threading.Event()
        
        #get a path of current file
        self.path = ''
        for i in os.path.dirname(os.path.realpath(__file__)):
            if i!='\\':
                self.path +=i
            else:
                self.path+='/'
        
    def dragEnterEvent(self, event):
        event.accept()
        
    def menu(self):
        position = QCursor.pos()
        self.menu = Menu(self)
        self.menu.exec_(position)
        
    def timer(self,dict,bool):
        while not self.stop_parent_event.is_set() :
            for q in (w for w in dict if self.stop_parent_event.is_set()==False):
                time.sleep(dict[q][1]*3600+dict[q][2]*60)
                self.label_two.setText(u'Ты сделала \n %s' % dict[q][0])
                self.label_two.show()
                self.is_done.emit()
                time.sleep(4)
                self.label_two.hide()                
            self.timer(dict,True)
    
    def play_song(self):
        m = QSound("%s/files/2.wav" % self.path)
        m.play()

class Shimeji(QLabel):
    is_moved = pyqtSignal(int,int)
    def __init__(self,parent,w,h,x,y):
        super(Shimeji,self).__init__(parent)
        self.w = w
        self.h = h
        self.x = x
        self.y = y
        self.setAcceptDrops(True)
        self.setGeometry(self.x,self.y,50,50)
        
        self.t = QTimer()
        self.time = 25
        self.t.timeout.connect(self.moving)
        self.t.start(self.time)
        
        self.need_x_coord = random.randint(0,self.w-80)
        self.stop = random.randrange(0,10000,25)
        self.timeout = self.stop
        
        #get a path
        self.path = ''
        for i in os.path.dirname(os.path.realpath(__file__)):
            if i!='\\':
                self.path +=i
            else:
                self.path+='/'
        
        self.image = Image.open("%s/img/sprites.png" %self.path)
        self.run_sprites = [self.image.crop((i*50,0,i*50+50,50)) for i in range(1,4)]
        self.cycled_sprites = itertools.cycle(self.run_sprites)
        self.fall_sprite = self.image.crop((300,0,350,50))
        self.setPixmap(QPixmap.fromImage(ImageQt(self.fall_sprite)))
    
    def moving(self):
        if self.y < self.h-90:
            self.y += 1
            self.move(self.x,self.y)
            self.setPixmap(QPixmap.fromImage(ImageQt(self.fall_sprite)))
        elif self.y == self.h-90:
            if self.x != self.need_x_coord:
                direction = math.copysign(1,self.need_x_coord-self.x)
                if direction == 1:
                    self.setPixmap(QPixmap.fromImage(ImageQt(next(self.cycled_sprites))))
                else:
                    self.setPixmap(QPixmap.fromImage(ImageQt(next(self.cycled_sprites).transpose(Image.FLIP_LEFT_RIGHT))))
                self.x = self.x + direction
                self.move(self.x,self.y)
            else:
                self.timeout -= 25
                if self.timeout == 0:
                    self.need_x_coord = random.randint(0,self.w-50)
                    self.stop = random.randrange(0,1000,25)
                    self.timeout = self.stop
        else:
            self.y = self.h-90
            self.move(self.x,self.y)
        self.is_moved.emit(self.x,self.y)
                    
    def dragEnterEvent(self, event):
        event.accept()
        
    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.LeftButton:
            return
        mimeData = QMimeData()
        drag = QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos()-self.rect().topLeft())
        dropAction = drag.start(Qt.MoveAction)
        cursor = QCursor()
        position = cursor.pos()
        coord = [position.x(),position.y()]
        self.move(coord[0],coord[1])
        self.y = coord[1]
        self.x = coord[0]
        if dropAction == Qt.MoveAction:
            self.close  
            
    def dropEvent(self,event):
        event.setDropAction(Qt.MoveAction)
        event.accept()

class AlertMessage(QLabel):
    def __init__(self,parent,frame):
        super(AlertMessage,self).__init__(parent)
        self.setGeometry(frame.x-100,frame.y-60,100,60)
        self.setStyleSheet('background-color: red')
        self.setAlignment(Qt.AlignCenter)
        
    def follow(self,pos_x,pos_y):
        self.move(pos_x-100,pos_y-60)
                
class Menu(QMenu):
    def __init__(self,parent):
        self.parent = parent
        super(Menu,self).__init__(parent)
        self.options = ["new_tab","exit"]
        self.conect = ["new_tab","exit"]
        
        for i in range(0,len(self.options)):
            self.action = QAction(self.options[i],self)
            self.act = self.addAction(self.action)
            method_to_call = getattr(self,self.conect[i])
            self.action.triggered.connect(method_to_call)        
        self.palette = QPalette()
        self.palette.setBrush(QPalette.Background,QBrush(QPixmap("pink.jpg")))
        
    def new_tab(self):
        timer_w = TimerWindow(self.parent)
        timer_w.show()

    def exit(self):
        sys.exit()

class TimerWindow(QMainWindow):
    def __init__(self,parent):
        self.parent = parent
        super(TimerWindow,self).__init__(parent)
        self.layout()
        self.stop_event = threading.Event()        
        
    def layout(self):
        self.win=QWidget(self)
        self.setFixedSize(600,350)
        self.title_text = QLabel(u"Задание")
        self.time_text = QLabel(u"Время")
        self.hours = QLabel(u'часы')
        self.minutes = QLabel(u'минуты')
        self.all_texts ={j:[QLineEdit(),QLineEdit(),QLineEdit()] for j in range(5)}
        self.start_button = QPushButton(u'Старт')
        self.start_button.clicked.connect(self.loop_timer)
        self.error_message = QLabel(u'Ошибка')
        self.stop_button = QPushButton(u'Стоп')
        self.stop_button.clicked.connect(self.stop)
        
        self.grid = QGridLayout()
        self.grid.setSpacing(10)
        
        self.grid.addWidget(self.title_text,1,0,1,3)
        self.grid.addWidget(self.time_text,1,4,1,1)
        
        #create a grid for all lineedits
        for i in range(2,7):
            self.grid.addWidget(self.all_texts[i-2][0],i,0,i,3)
            self.grid.addWidget(self.all_texts[i-2][1],i,4,i,1)
            self.grid.addWidget(self.hours,i,5,i,1)
            self.grid.addWidget(self.all_texts[i-2][2],i,6,i,1)
            self.grid.addWidget(self.minutes,i,7,i,1)
            
        self.grid.addWidget(self.error_message,7,1,7,1)
        self.error_message.hide()
        self.grid.addWidget(self.stop_button,7,4,7,1)
        self.grid.addWidget(self.start_button,7,6,7,1)
        self.setCentralWidget(self.win)
        self.win.setLayout(self.grid)
        self.show()
        
    def loop_timer(self):
        try:
            self.stop()
            self.parentr.stop_parent_event.clear()
            self.all_time = {}
            self.error_message.hide()
            for i in range(5):
                if unicode(self.all_texts[i][0].text()) != u"":
                    self.all_time[i]=[unicode(self.all_texts[i][0].text())] +\
                    [int(self.all_texts[i][j+1].text()) if self.all_texts[i][j+1].text()!='' else int(0) for j in range(2)]
            self.parent.process = threading.Thread(target = self.parent.timer,args = (self.all_time,True))
            self.parent.process.start()
        except ValueError:
            self.error_message.show()
            
    def stop(self):
        self.parent.stop_parent_event.set()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
    window.setAttribute(Qt.WA_NoSystemBackground,True)
    window.setAttribute(Qt.WA_TranslucentBackground, True) 
    window.show()
    sys.exit(app.exec_())   
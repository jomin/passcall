#coding=utf-8
import sys,threading
from PyQt4 import QtGui, QtCore, uic
from PyQt4.QtCore import  QStringList
from evdev import InputDevice, categorize, ecodes
from select import select
import virtkey,time
from kptool.keepassdb import keepassdb

keyboard_dev = InputDevice('/dev/input/event5')
mouse_dev = InputDevice('/dev/input/event6')
password = raw_input('请输入密码：',)

hot_key_down = 0
ctrl_key_value = 0
def put_key(key):
    v = virtkey.virtkey()
    for i in str(key):
        v.press_unicode(ord(i))
        v.release_unicode(ord(i))
    #v.press_keysym(65363)
    #v.release_keysym(65363)
def hot_ctrl_key():
    
    global ctrl_key_value
    while True:
        r,w,x = select([keyboard_dev],[],[])
        for event in keyboard_dev.read():
            if event.type == ecodes.EV_KEY and event.code == 29:
                ctrl_key_value = event.value
class MyWindow( QtGui.QWidget ):
    def __init__( self ):
        super( MyWindow, self ).__init__()
        self.setWindowTitle( "hello" )
        self.resize( 300, 200 )
        
        t = threading.Thread(target=hot_ctrl_key,args=())
        t.start()
        t1 = threading.Thread(target=self.HotKey)
        t1.start()
        self.monitor_action()
        gridlayout = QtGui.QGridLayout()
        self.button = QtGui.QPushButton( u"打开密码框" )
        gridlayout.addWidget( self.button )
        self.setLayout( gridlayout )
         
        self.connect( self.button, QtCore.SIGNAL( 'clicked()' ), self.creat_menu)
        self.timer = QtCore.QTimer()
        self.connect(self.timer,QtCore.SIGNAL("timeout()"), self.monitor_action)
        self.timer.start(100)
         
            
    def monitor_action(self):
        global hot_key_down
        if hot_key_down == 1 :
            self.creat_menu()
            hot_key_down = 0
    def creat_menu(self):
        self.menu = {}
        level = {
           0:0,
           1:0,
           2:0,
           #level : last_parent_id
           }
        self.user_action={}
        self.pass_action={}
        menuBar = QtGui.QMenuBar()
        self.menu[0] = QtGui.QMenu('1',menuBar)
        old_level = 0
        k = keepassdb.KeepassDBv1(r"/home/jing/文档/x-y-t.kdb", password)
        for g in k.get_groups():
            self.menu[g['group_id']] = QtGui.QMenu(g['title'])
            self.get_userandpass(k,g['group_id'])
            if g['level'] == old_level :
                #print level[g['level']],g['group_id']
                #menu[level[g['level']]].add(g['group_id'])
                self.menu[level[g['level']]].addMenu(self.menu[g['group_id']])
                #last_parent_id = g['group_id']
                level[g['level']+1] = g['group_id']
                old_level = g['level']
            elif g['level'] > old_level:
                #print level[g['level']],g['group_id']
                self.menu[level[g['level']]].addMenu(self.menu[g['group_id']])
                #menu[level[g['level']]].add(g['group_id'])
                old_level = g['level']
                #level[g['level']+1]=g['group_id']
            else :
                #print level[g['level']],g['group_id']
                self.menu[level[g['level']]].addMenu(self.menu[g['group_id']])
                level[g['level']+1] = g['group_id']
    #             menu[level[g['level']-1]].add(g['group_id'])
                old_level = g['level']
        point=QtCore.QPoint()
        point=QtGui.QCursor.pos()
        self.menu[0].exec_(point)


    def get_userandpass(self,k,groupid):
        user_action = {}
        pass_action = {}
        for e in k.get_entries_from_groupid(groupid):
            if e['id'] != '00000000000000000000000000000000':
                self.menu[e['id']] = QtGui.QMenu(e['title'])
                self.menu[e['group_id']].addMenu(self.menu[e['id']])
                self.user_action[e['id']] = self.menu[e['id']].addAction(e['username'])
                self.pass_action[e['id']] = self.menu[e['id']].addAction(e['password'])
                #txt = e['id']
                self.user_action[e['id']].triggered.connect(self.do_stuff_caller(e['username']))
                self.pass_action[e['id']].triggered.connect(self.do_stuff_caller(e['password']))



    def doStuff(self, item):
        put_key(item)
    def do_stuff_caller(self,item):
        return lambda: self.doStuff(item)
        
    def HotKey(self):
        global hot_key_down
        while True:
            r,w,x = select([mouse_dev],[],[])
            for event in mouse_dev.read():
                if ctrl_key_value != 0:
                    if event.type == ecodes.EV_KEY and event.value == 1 and event.code == 272:
                        hot_key_down = 1

app = QtGui.QApplication( sys.argv )
demo = MyWindow()
demo.show()
app.exec_()

from PyQt4 import QtGui
from PyQt4 import QtCore

import ESP_Module, sys
import SMS_Bot, sys
import sys
import serial
import serial.tools.list_ports
import time
import re

c=''
send_flag = 0
baud_rate = 115200
com_port = None
open_button = 0
portOpen = False
ESP_port = serial.Serial()
Console_Data = ''
ScriptData = ''
wifi_select=''
port_no = ''
read_serial=''
SSID_Name=''
ssid_password=''
check_b=''
Server_add=''
port=''
chat=''
TCP_Msg_len =0
POP_UP=''
local_var_ip = ''
server_Port_No=''
connection_no_to_close=''
chatbox_yesno=''
co_number=''
HTTP_Msg_len=''
get_http_host=''
get_directory = ''


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s


class DialogClass(QtGui.QDialog, SMS_Bot.Ui_Dialog):
    def __init__(self, parent=None):
        super(DialogClass, self).__init__(parent)
        self.setupUi(self)
        QtCore.QObject.connect(self.TCPUDP_Message, QtCore.SIGNAL(_fromUtf8("textChanged()")), self.TCP_Message_Length)
        QtCore.QObject.connect(self.SEND_DATA, QtCore.SIGNAL(_fromUtf8("clicked()")), self.send_message)
        QtCore.QObject.connect(self.Close_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Terminate_POP_UP)
        QtCore.QObject.connect(self.Connection_no_Chat, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.Connection_number)

    def TCP_Message_Length(self):
        global TCP_Msg_len
        TCP_Msg_len = len(self.TCPUDP_Message.toPlainText())

    def send_message(self):
        global chatbox_yesno
        global POP_UP
        global TCP_Msg_len
        global co_number
        if POP_UP:
           ESP_port.write('AT+CIPSEND=' + str(TCP_Msg_len) + "\r\n")
           time.sleep(1)
           ESP_port.write(str(self.TCPUDP_Message.toPlainText()) + "\r\n")
           self.TCPUDP_Message.setPlainText('')
        elif chatbox_yesno:

                ESP_port.write('AT+CIPSEND=' +str(co_number)+','+ str(TCP_Msg_len) + "\r\n")
                time.sleep(1)
                ESP_port.write(str(self.TCPUDP_Message.toPlainText()) + "\r\n")
                self.TCPUDP_Message.setPlainText('')

    def Connection_number(self,local_var):
         global co_number
         co_number=local_var

    def Terminate_POP_UP(self):
        app.Server_Chat_checkBox.setChecked(False)
        app.POP_up_checkBox.setChecked(False)
        self.close()


class MainGUIClass(QtGui.QMainWindow, ESP_Module.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainGUIClass, self).__init__(parent)
        self.setupUi(self)
        self.Thread1 = WorkThread()
        QtCore.QObject.connect(self.findButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.port_update)
        QtCore.QObject.connect(self.portComboBox, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.port_select)
        QtCore.QObject.connect(self.baudcomboBox, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.baud_select)
        QtCore.QObject.connect(self.connectButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.connect_disconnect)
        QtCore.QObject.connect(self.ClearLog, QtCore.SIGNAL(_fromUtf8("clicked()")), self.clear_log)
        QtCore.QObject.connect(self.Thread1, QtCore.SIGNAL(_fromUtf8("SERIAL_DATA")), self.serial_data)
        QtCore.QObject.connect(self.Thread1, QtCore.SIGNAL(_fromUtf8("SERIAL_DATA")), self.server_chat)
        QtCore.QObject.connect(self.Thread1, QtCore.SIGNAL(_fromUtf8("SERIAL_DATA")), self.tabcolour)
        QtCore.QObject.connect(self.Thread1, QtCore.SIGNAL(_fromUtf8("SERIAL_DATA")), self.show_IP_address)
        QtCore.QObject.connect(self.Thread1, QtCore.SIGNAL(_fromUtf8("SERIAL_DATA")), self.on_off)


        QtCore.QObject.connect(self.SendButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.send_script)
        QtCore.QObject.connect(self.ScriptLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.ScriptText)
        QtCore.QObject.connect(self.wifi_pass, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.ssid_pass)
        QtCore.QObject.connect(self.WirelessSelection, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.Selection)
        QtCore.QObject.connect(self.Wifi_Search, QtCore.SIGNAL(_fromUtf8("clicked()")), self.wifi_list)
        QtCore.QObject.connect(self.Refresh, QtCore.SIGNAL(_fromUtf8("clicked()")), self.wifi_refresh)
        QtCore.QObject.connect(self.SaveLog, QtCore.SIGNAL(_fromUtf8("clicked()")), self.log2txt)
        QtCore.QObject.connect(self.WifiCombobox, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.wifi_ssid)
        QtCore.QObject.connect(self.wifi_connect, QtCore.SIGNAL(_fromUtf8("clicked()")), self.get_wifi)
        QtCore.QObject.connect(self.checkBox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.yesno)
        QtCore.QObject.connect(self.Disconnect, QtCore.SIGNAL(_fromUtf8("clicked()")), self.wifi_disconnect)
        QtCore.QObject.connect(self.Default_wifi, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.default_wifi)
        QtCore.QObject.connect(self.SelectionCombobox, QtCore.SIGNAL(_fromUtf8("activated(QString)")), self.tcp_udp)
        QtCore.QObject.connect(self.ServerLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.Server_IP)
        QtCore.QObject.connect(self.PortLineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.Server_port)
        QtCore.QObject.connect(self.Connect_TCPUDP, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Connection)
        QtCore.QObject.connect(self.Clear_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Clear_TCPUDP)
        QtCore.QObject.connect(self.Disconnect_TCPUDP, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Termination)
        QtCore.QObject.connect(self.POP_up_checkBox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.POPUP_CHAT)
        QtCore.QObject.connect(self.Server_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Connect_to_Client)
        QtCore.QObject.connect(self.ServerClose_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Close_server)
        QtCore.QObject.connect(self.Server_PortlineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.Server_port_no)
        QtCore.QObject.connect(self.Connection_lineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.Connection_No)
        QtCore.QObject.connect(self.Clear_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Clear_Server_Data)
        QtCore.QObject.connect(self.Server_Chat_checkBox, QtCore.SIGNAL(_fromUtf8("stateChanged(int)")), self.server_chat_open)
        QtCore.QObject.connect(self.http_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.Configure_http)
        QtCore.QObject.connect(self.HTTPplainTextEdit, QtCore.SIGNAL(_fromUtf8("textChanged()")), self.COUNT_http_msg_len)
        QtCore.QObject.connect(self. http_clearpushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.http_clear)
        QtCore.QObject.connect(self.http_lineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.get_host_name)
        QtCore.QObject.connect(self.http_close, QtCore.SIGNAL(_fromUtf8("clicked()")), self.terminate_http)
        QtCore.QObject.connect(self.http_getpushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.get_button)
        QtCore.QObject.connect(self.http_Send_pushButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.HTTP_push_button)
        QtCore.QObject.connect(self.lineEdit, QtCore.SIGNAL(_fromUtf8("textChanged(QString)")), self.http_get_directory)


    def port_update(self):
        try:
            self.portComboBox.clear()
            ports = list(serial.tools.list_ports.comports())
            num_port = len(ports)
            for i in range(num_port):
                self.portComboBox.addItem("")
                # for i in range(num_port):
                self.portComboBox.setItemText(i, ports[i][0])
            self.port_select(ports[0][0])
        except:
            self.SerialConsole.setPlainText('Port Not Found')

    def port_select(self, port):
        ESP_port.close
        global portOpen
        portOpen = False
        ESP_port.port = port

    def baud_select(self, baud):
        ESP_port.close
        global portOpen
        portOpen = False
        ESP_port.baudrate = baud

    def connect_disconnect(self):
        global Console_Data

        try:

            global portOpen
            if (portOpen):

                ESP_port.close()
                portOpen = False
                self.connectButton.setText("Connect")
                Console_Data = 'Port Closed'
                self.SerialConsole.setPlainText(str(Console_Data))
            else:

                ESP_port.open()
                portOpen = True
                self.connectButton.setText("Disconnect")
                Console_Data = 'Port Opened'
                ESP_port.write("AT" + "\r\n")
                self.SerialConsole.setPlainText(str(Console_Data))


        except:
            self.SerialConsole.setPlainText('Port May be Used By Another Application')

    def serial_data(self):
        global Console_Data
        global read_serial
        self.SerialConsole.setPlainText(Console_Data)
        with open('temp.txt', 'w') as FileHandle :
                FileHandle.write(read_serial)
        self.SerialConsole.verticalScrollBar().setSliderPosition(self.SerialConsole.verticalScrollBar().maximum());

    def ScriptText(self, data):
        global ScriptData
        ScriptData = data

    def send_script(self):
      global portOpen
      if portOpen:
        global ScriptData
        ESP_port.write(str(ScriptData) + "\r\n")
        self.ScriptLineEdit.setText('')
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def clear_log(self):
        global Console_Data
        Console_Data = ''
        self.SerialConsole.setPlainText(str(Console_Data))

    def log2txt(self):
        with open('log.txt', 'w') as logtext :
           logtext.write(str(self.SerialConsole.toPlainText()))


    def Selection(self,local):
        global wifi_select
        global read_serial
        wifi_select=local
        
        if wifi_select == 'HOTSPOT+WIFI':
              self.Selection_pushButton.setText('HOTSPOT+WIFI MODE')
              ESP_port.write('AT+CWMODE_CUR=3'+ "\r\n")
              time.sleep(1)
              ESP_port.write('AT+CWLAP' + "\r\n")
              time.sleep(1)
        elif wifi_select == 'WIFI':
              self.Selection_pushButton.setText('WIFI MODE')
              ESP_port.write('AT+CWMODE_CUR=1'+ "\r\n")
              time.sleep(1)
              ESP_port.write('AT+CWLAP' + "\r\n")
              time.sleep(1)
        elif wifi_select == 'HOTSPOT':
              self.Selection_pushButton.setText('HOTSPOT MODE')
              ESP_port.write('AT+CWMODE_CUR=2'+ "\r\n")




    def wifi_list(self):
      global portOpen
      if portOpen:
        global read_serial
        local_var2='Select\n'
        count=0
        with open("temp.txt","r") as f:

            for line in f:
                if line.startswith('+CWLAP:('):
                    local_var=(re.search(r'"(.*?)"', line).group(1))
                    local_var2+=(local_var+"\n")
        with open('temp.txt', 'w') as logtext :
           logtext.write(local_var2)
        List = open("temp.txt").readlines()
        local_var1=len(List)
        # List=List.rstrip()
        for i in range(local_var1):
            self.WifiCombobox.addItem("")
            self.WifiCombobox.setItemText(i, List[i])
        read_serial=''
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def wifi_ssid(self,local_var5):
        global SSID_Name
        SSID_Name=local_var5

    def ssid_pass(self,local_var6):
        global wifi_select
        global ssid_password

        ssid_password=local_var6
        if SSID_Name == 'Select' or ssid_password == '':
            self.wifi_connect.setEnabled(False)
        else:
            self.wifi_connect.setEnabled(True)


    def yesno(self,yes):
        if yes:
            self.wifi_pass.setEchoMode(QtGui.QLineEdit.Normal)
        else:
            self.wifi_pass.setEchoMode(QtGui.QLineEdit.Password)


    def wifi_refresh(self):

        global portOpen
        if portOpen:
           ESP_port.write('AT+CWLAP' + "\r\n")
        else:
            self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def get_wifi(self):
      global portOpen
      if portOpen:
        global ssid_password
        global SSID_Name
        global check_b
        if check_b:
            ESP_port.write('AT+CWJAP_DEF="'+(str(SSID_Name)).strip()+'"'+','+'"'+str(ssid_password)+'"' + "\r\n")

        else:
            ESP_port.write('AT+CWJAP_CUR="'+(str(SSID_Name)).strip()+'"'+','+'"'+str(ssid_password)+'"'+ "\r\n")
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def tabcolour(self):
        global Console_Data
        global read_serial
        global co_number
        global POP_UP
        a1 = 0
        a2 = 0
        b1 = 0
        a1 = read_serial.rfind('CONNECT')
        a2 = read_serial.rfind('OK')
        a1 = a1 + 11
        b1 = read_serial.rfind('CLOSED')
        a=0
        b=0
        a=Console_Data.rfind('WIFI DISCONNECT')
        b=Console_Data.rfind('WIFI CONNECTED')
        if a>=0 or b>=0:
            if a>b:
               self.ConnectionStatus.setText("Disconnected")
               self.ConnectionStatus.setStyleSheet(_fromUtf8("background-color: rgb(170, 0, 0);"))

            elif b>a:
                self.ConnectionStatus.setText("Connected")
                self.ConnectionStatus.setStyleSheet(_fromUtf8("background-color: rgb(0, 85, 0);"))

            else:
                self.ConnectionStatus.setText("Disconnected")
                self.ConnectionStatus.setStyleSheet(_fromUtf8("background-color: rgb(170, 0, 0);"))

        if a1 > 0 or b1 > 0:
            if self.POP_up_checkBox.isChecked():
                  if a1 > b1 and a1 == a2:
                       app2.pushButton.setText('Server Status : Active')
                       app2.pushButton.setStyleSheet(_fromUtf8("background-color: rgb(0, 85, 0);"))
                       a1 = 0
                       read_serial=''
                  elif b1 > a1:
                        app2.pushButton.setText('Server Status : Inactive')
                        app2.pushButton.setStyleSheet(_fromUtf8("background-color: rgb(170, 0, 0);"))
                        b1 = 0
                        read_serial=''
            elif self.Server_Chat_checkBox.isChecked():
                if a1 > b1 and a1 == a2:
                    app3.pushButton.setText('Client Status : Active')
                    app3.pushButton.setStyleSheet(_fromUtf8("background-color: rgb(0, 85, 0);"))
                    a1 = 0
                    read_serial=''
                elif b1 > a1:
                    app3.pushButton.setText('Client Status : Inactive')
                    app3.pushButton.setStyleSheet(_fromUtf8("background-color: rgb(170, 0, 0);"))
                    b1 = 0
                    read_serial=''

    def default_wifi(self,Default):
        global check_b
        check_b=Default
        # ESP_port.write(' AT + CWAUTOCONN = 1' + "\r\n")

    def wifi_disconnect(self):
        global portOpen
        if portOpen:
           ESP_port.write('AT+CWQAP' + "\r\n")
        else:
            self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def tcp_udp(self,local_var11):
        global tcp_udp_selection
        tcp_udp_selection=local_var11
        if tcp_udp_selection == 'TCP':
            self.Connect_TCPUDP.setText("Connect TCP")
            self.Disconnect_TCPUDP.setText("Disconnect TCP")
        elif tcp_udp_selection == 'UDP':
            self.Connect_TCPUDP.setText("Connect UDP")
            self.Disconnect_TCPUDP.setText("Disconnect UDP")
        elif tcp_udp_selection == 'Select':
            self.Connect_TCPUDP.setText("Connect")
            self.Disconnect_TCPUDP.setText("Disconnect")

    def Server_IP(self,local_var8):
        global Server_add
        Server_add=local_var8

    def Server_port(self,local_var9):
        global port
        port=local_var9

    def Connection(self):
      global portOpen
      if portOpen:
        global Server_add
        global port
        global tcp_udp_selection
        if tcp_udp_selection == 'TCP':
            ESP_port.write('AT+CIPSTART="TCP",'+'"'+str(Server_add)+'"'+','+str(port)+"\r\n")
        elif tcp_udp_selection == 'UDP':
            ESP_port.write('AT+CIPSTART="UDP",'+'"'+str(Server_add)+'"'+','+str(port)+"\r\n")
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

          # local_var11=local_var10.split(':')
             # print local_var11
        # self.Client_PlaintextEdit.setPlainText(local_var11[1])
    #
    def server_chat(self):

                global read_serial
                global local_var_ip
                global POP_UP
                global chatbox_yesno
                # app2 = DialogClass()
                with open('temp.txt', 'w') as FileHandle:
                    FileHandle.write(read_serial)

                with open("temp.txt", "r") as f:
                    for line in f:
                        if line.startswith('+IPD'):
                            local_var_ip = line.split(':')
                            if self.POP_up_checkBox.isChecked():
                               app2.Server_PlaintextEdit.setPlainText(str(local_var_ip[1]))
                               read_serial = ''
                            elif self.Server_Chat_checkBox.isChecked():
                                app3.Server_PlaintextEdit.setPlainText(str(local_var_ip[1]))
                                read_serial = ''




    def POPUP_CHAT(self,showme_pop_up):
      global portOpen
      if portOpen:
        global POP_UP
        POP_UP=showme_pop_up
        if POP_UP:
            self.Server_Chat_checkBox.setChecked(False)
            app3.close()
            app2.show()
            app2.exec_()
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')


    def Termination(self):
        global portOpen
        if portOpen:
          ESP_port.write('AT+CIPCLOSE'+"\r\n")
        else:
            self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def Clear_TCPUDP(self):
        global Server_add
        global port
        global tcp_udp_selection
        Server_add=''
        port=''
        tcp_udp_selection='Select'
        self.ServerLineEdit.setText('')
        self.PortLineEdit.setText('')

    def Server_port_no(self,local1):
        global server_Port_No
        server_Port_No=local1

    def Connection_No(self,local2):
        global connection_no_to_close
        connection_no_to_close=local2

    def Connect_to_Client(self):
      global portOpen
      if portOpen:
        global server_Port_No
        ESP_port.write('AT+CIPMUX=1' + "\r\n")
        time.sleep(1)
        ESP_port.write('AT+CIPSERVER=1,'+str(server_Port_No) + "\r\n")
        time.sleep(1)
        ESP_port.write('AT+CIFSR' + "\r\n")
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def show_IP_address(self):
        global read_serial
        global local_var_ip
        x1=0
        x2=''
        with open('temp.txt', 'w') as FileHandle:
            FileHandle.write(read_serial)

        with open("temp.txt", "r") as f:
            for line in f:
                if line.startswith('+CIFSR:'):
                    local_var_ip = line.split(',')
                    self.Server_IPlineEdit.setText(str(local_var_ip[1]))
                    read_serial = ''
                    break
                if line.startswith('Content-Type:'):
                     x1=read_serial.rfind('Content-Type:')
                     x2=x1+27
                     # x2=read_serial.rfind('Ramakanta')
                     if x1>0:
                          self.HTTPplainTextEdit.setPlainText(read_serial[x1+27:-8].replace('<br/>','\n'))
                          read_serial=''

    def Clear_Server_Data(self):
        global connection_no_to_close
        global server_Port_No
        server_Port_No=''
        connection_no_to_close=''
        self.Connection_lineEdit.setText('')
        self.Server_PortlineEdit.setText('')

    def server_chat_open(self,yes):
      global portOpen
      if portOpen:
        global chatbox_yesno
        chatbox_yesno=yes
        if chatbox_yesno:
            self.POP_up_checkBox.setChecked(False)
            app2.close()
            # self.Server_Chat_checkBox.setChecked(False)
            app3.show()
            app3.exec_()
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def Close_server(self):
        global portOpen
        if portOpen:
           global connection_no_to_close
           ESP_port.write('AT+CIPCLOSE='+str(connection_no_to_close) + "\r\n")
        else:
            self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')


    def Configure_http(self):
      global portOpen
      if portOpen:
        global read_serial
        global get_http_host
        ESP_port.write('AT+CIPSTART="TCP",'+'"'+str(str(get_http_host).strip('http://')).rstrip('/')+'",80' + "\r\n")
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def COUNT_http_msg_len(self):
         global HTTP_Msg_len
         HTTP_Msg_len = len(self.HTTPplainTextEdit.toPlainText())

    def get_host_name(self,local):
        global get_http_host
        get_http_host=local
    def http_get_directory(self,locall):
        global get_directory
        get_directory = locall

    def get_button(self):
      global portOpen
      if portOpen:
        a = 0
        b = 0
        c = 0
        # global HTTP_Msg_len
        global get_http_host
        get_http_host = str(str(get_http_host).strip('http://')).rstrip('/')
        global get_directory
        c=len(get_directory)
        a=len(get_http_host)
        b=a+c+26
        ESP_port.write('AT+CIPSEND=' + str(b) + "\r\n")
        time.sleep(1)
        ESP_port.write('GET /'+str(get_directory)+' HTTP/1.1\r\nHost: '+str(get_http_host)+'\r\n\r\n')
        time.sleep(10)
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')


    def HTTP_push_button(self):
      global portOpen
      if portOpen:
        global HTTP_Msg_len
        global get_directory
        global get_http_host
        get_http_host = str(str(get_http_host).strip('http://')).rstrip('/')
        a=0
        b=0
        c=0
        d=0
        c = len(get_directory)
        a = len(get_http_host)
        # d = len(HTTP_Msg_len)
        # HTTP_Msg_len = len(self.HTTPplainTextEdit.toPlainText())
        # d = len(HTTP_Msg_len)
        b=c+a+2+HTTP_Msg_len+94
        print str(HTTP_Msg_len)
        ESP_port.write('AT+CIPSEND=' + str(b) + "\r\n")
        time.sleep(1)
        ESP_port.write('POST /'+str(get_directory)+' HTTP/1.1\r\nHost: '+str(get_http_host)+'\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: '+str(HTTP_Msg_len)+'\r\n\r\n'+str(self.HTTPplainTextEdit.toPlainText())+'\r\n\r\n')
        time.sleep(10)
      else:
          self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def terminate_http(self):
       global portOpen
       if portOpen:
         ESP_port.write('AT+CIPCLOSE=0'+ "\r\n")
         time.sleep(1)
         ESP_port.write('AT+RST'+ "\r\n")
       else:
           self.SerialConsole.setPlainText('Please Connect The Hardware.\n 1) Findport->select port.\n 2)select baud rate according to ur hardware->Connect')

    def http_clear(self):
        global get_http_host
        get_http_host=''
        self.http_lineEdit.setText('')
        self.HTTPplainTextEdit.setPlainText('')
        self.lineEdit.setText('')


class WorkThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        global portOpen
        global read_serial
        global chat
        global app2

        while True:
            while portOpen:
                global c
                d = ESP_port.read()
                global Console_Data
                Console_Data += d
                read_serial+=d
                chat+=d
                self.emit(QtCore.SIGNAL("SERIAL_DATA"))


if __name__ == '__main__':
    a = QtGui.QApplication(sys.argv)
    app = MainGUIClass()
    app2=DialogClass()
    app3=DialogClass()
    app.show()
    app.Thread1.start()
    sys.exit(a.exec_())

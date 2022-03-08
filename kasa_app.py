import asyncio
import sys
from qasync import QEventLoop
from kasa import Discover, SmartDevice
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot

class KasaObject():
    
    def __init__(self, devices):
        self.devices = devices
        
    def get_devices(self):
        return self.devices
        

class KasaWorker(QObject):
    signal_back = pyqtSignal(KasaObject)
    signal_button_change = pyqtSignal(bool)
    #set_num_signal = pyqtSignal(int)

    def __init__(self, loop: asyncio.AbstractEventLoop, parent=None):
        super(KasaWorker, self).__init__(parent)
        self.loop = loop
        self.counter = 0
        self.device = ""
        
    @pyqtSlot(SmartDevice)           
    def set_device(self, device):
        print("in set_device")
        print(device)
        self.device = device
        asyncio.ensure_future(self.toggle_device(), loop=self.loop)
        #toggle_device()
    
    async def toggle_device(self):
        if self.device.is_off:
            await self.device.turn_on()
        else:
            await self.device.turn_off()
        #await asyncio.sleep(1.0)
    
    
    
    async def countup(self):
        while True:
            self.counter += 1
            self.set_num_signal.emit(self.counter)
            await asyncio.sleep(1.0)
        

    async def discover_devices(self):
        print("in discover_devices")
        devices = await Discover.discover()
        wrapped_devices = KasaObject(devices)
        self.signal_back.emit(wrapped_devices)
    
    def work(self):
        #asyncio.ensure_future(self.toggle_device(), loop=self.loop)
        asyncio.ensure_future(self.discover_devices(),  loop=self.loop)
        #self.loop.run_forever()
        


class MainWindow(QMainWindow):
    set_device_signal = pyqtSignal(SmartDevice)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kasa Devices")
        self.layout = QVBoxLayout()
        widget = QWidget()
        widget.setLayout(self.layout)
        self.setCentralWidget(widget)
        #self.button = QPushButton("transmit!")
        #self.button.clicked.connect(self.emitter)
        #self.layout.addWidget(self.button)
        self.start_task()

    def start_task(self):
        loop = asyncio.get_event_loop()
        self.kasa_worker = KasaWorker(loop)
                       
        self.set_device_signal.connect(self.kasa_worker.set_device)
        self.kasa_worker.signal_back.connect(self.discover_devices)
        #self.asynciothread.set_num_signal.connect(self.output_num)
        self.kasa_worker.work()
    
    #@pyqtSlot(int)
    #def output_num(self, int):
        #print(str(int))
       
    def emitter(self):
        print("emiting string")
        self.set_device_signal.emit("recieved!!")
        
    #def toggle_device(self, device):
        #print("emiting device")
        #self.set_device_signal.emit(device)
    
        
    @pyqtSlot(KasaObject)
    def discover_devices(self, devices):
        print("received kasaObject")
        print(devices.get_devices())
        self.build_device_buttons(devices) 
    
    def build_device_buttons(self, devices):
        for device in devices.get_devices().values():
            self.btn = QPushButton(device.alias)
            self.btn.clicked.connect(lambda:asyncio.ensure_future(self.toggle_device(device), loop=asyncio.get_event_loop()))
            self.btn.setCheckable(True)
            if self.btn.isChecked() != device.is_off:
                self.btn.toggle()
            self.layout.addWidget(self.btn)

    async def toggle_device(self, device):
        if device.is_off:
            await device.turn_on()
        else:
            await device.turn_off()
        


def main():
    app = QApplication(sys.argv)
    #ui = MainWindow()
    #ui.show()
    #sys.exit(app.exec_())
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    with loop:
        window = MainWindow()
        window.show()
        loop.run_forever()
    
if __name__ == "__main__":
    main()

#app = App(title="Kasa GUI", width=300, height=200, layout="grid")
#devices = discover_devices()
#device_dropdown = build_combo(devices)
#selected_device_text = Text(app, text=device_dropdown.value, grid=[0,1], align="left")
#selected_device = devices.
#device_button = PushButton(app, command=
#app.display()

#devices = discover_devices()
#for name, device in devices.items():
    #print(name)
    #print(device.alias)
    #print(device.is_on)
    #print(device.is_off)

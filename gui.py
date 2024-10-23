import sys
import os
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QPushButton, QFileDialog
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer
from pynput import keyboard, mouse
from PIL import ImageGrab

class InputMonitor(QObject):
    event_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.running = False
        self.event_list = []

    """
    # 在 InputMonitor 类的 on_key_press、on_mouse_click 和 on_mouse_scroll 方法中添加当前时间
class InputMonitor(QObject):
    # ...

    def on_key_press(self, key):
        try:
            key_char = key.char
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.event_list.append(f'[{current_time}] 按下按键: {key_char}\n')
        except AttributeError:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.event_list.append(f'[{current_time}] 按下特殊按键: {key}\n')

    def on_mouse_click(self, x, y, button, pressed):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if pressed:
            self.event_list.append(f'[{current_time}] 鼠标按键按下: {button}\n')
        else:
            self.event_list.append(f'[{current_time}] 鼠标按键释放: {button}\n')

    def on_mouse_scroll(self, x, y, dx, dy):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.event_list.append(f'[{current_time}] 鼠标滚轮滚动: ({dx}, {dy})\n')

    # ...

    """

    def start_listeners(self, save_path):
        self.save_path = save_path
        self.log_dir = ""
        self.log_file_path = ""

        current_date = datetime.datetime.now().strftime("%Y%m%d")
        self.log_dir = os.path.join(self.save_path, current_date)
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file_path = os.path.join(self.log_dir, "log.log")

        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll)

        self.keyboard_listener.start()
        self.mouse_listener.start()

        self.running = True

    def stop_listeners(self):
        if self.running:
            self.keyboard_listener.stop()
            self.mouse_listener.stop()
            self.running = False

    def on_key_press(self, key):
        try:
            key_char = key.char
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.event_list.append(f'[{current_time}] 按下按键: {key_char}\n')
        except AttributeError:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.event_list.append(f'[{current_time}] 按下特殊按键: {key}\n')

    def on_mouse_click(self, x, y, button, pressed):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if pressed:
            self.event_list.append(f'[{current_time}] 鼠标按键按下: {button}\n')
        else:
            self.event_list.append(f'[{current_time}] 鼠标按键释放: {button}\n')

    def on_mouse_scroll(self, x, y, dx, dy):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.event_list.append(f'[{current_time}] 鼠标滚轮滚动: ({dx}, {dy})\n')

    def save_to_file(self):
        if not self.log_file_path:
            return
        with open(self.log_file_path, 'a') as file:
            for event_text in self.event_list:
                file.write(event_text)
        self.event_list.clear()

    def capture_screen(self):
        try:
            if not self.log_dir:
                return

            # 获取当前时间的秒级事件戳
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            # 拼接图像文件的路径
            image_file_path = os.path.join(self.log_dir, f"{timestamp}.png")

            # 截取屏幕并保存为图片
            screenshot = ImageGrab.grab()
            screenshot.save(image_file_path, "PNG")
        except Exception:
            pass


class InputMonitorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_text_box)
        self.screen_capture_timer = QTimer(self)
        self.screen_capture_timer.timeout.connect(self.capture_screen)

    def init_ui(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('输入监控窗口')

        self.text_box = QTextEdit(self)
        self.text_box.setReadOnly(True)
        self.text_box.setGeometry(50, 50, 700, 400)

        self.select_path_button = QPushButton('选择保存路径', self)
        self.select_path_button.setGeometry(50, 500, 150, 30)
        self.select_path_button.clicked.connect(self.select_save_path)

        self.close_button = QPushButton('关闭窗口', self)
        self.close_button.setGeometry(250, 500, 150, 30)
        self.close_button.clicked.connect(self.close_window)

        self.monitor = InputMonitor()
        self.worker = None

    def select_save_path(self):
        save_path = QFileDialog.getExistingDirectory(None, "选择保存路径")
        if save_path:
            self.monitor.start_listeners(save_path)
            self.timer.start(1000)  # 每秒刷新一次界面
            self.select_path_button.setDisabled(True)
            self.screen_capture_timer.start(180000)  # 每隔180秒截图一次
            self.select_path_button.setDisabled(True)

    def capture_screen(self):
        self.monitor.capture_screen()

    def update_text_box(self):
        if self.monitor.running:
            event_text = "".join(self.monitor.event_list)
            self.text_box.insertPlainText(event_text)
            self.monitor.save_to_file()
            self.monitor.event_list.clear()


    def close_window(self):
        if self.worker and self.worker.monitor.running:
            self.worker.monitor.stop_listeners()
            self.worker.wait()
        self.close()

def main():
    app = QApplication(sys.argv)
    window = InputMonitorWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

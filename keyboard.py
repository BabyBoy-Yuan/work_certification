import os
import tkinter as tk
from tkinter import filedialog
from pynput import keyboard, mouse
import datetime

class InputMonitor:
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        self.root.title("输入监控窗口")

        # 创建文本框用于显示输入行为
        self.text_box = tk.Text(self.root, height=10, width=40)
        self.text_box.pack()

        # 创建选择保存路径的按钮
        select_path_button = tk.Button(self.root, text="选择保存路径", command=self.select_save_path)
        select_path_button.pack()

        # 创建关闭窗口的按钮
        close_button = tk.Button(self.root, text="关闭窗口", command=self.close_window)
        close_button.pack()

        # 创建键盘监听器和鼠标监听器
        self.keyboard_listener = keyboard.Listener(on_press=self.on_key_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click, on_scroll=self.on_mouse_scroll)

        # 保存路径变量
        self.save_path = ""
        self.log_dir = ""
        self.log_file_path = ""

    def select_save_path(self):
        # 打开文件对话框以选择保存路径
        self.save_path = filedialog.askdirectory()
        if not self.save_path:
            tk.messagebox.showerror("错误", "请选择保存路径")
        else:
            # 根据当前日期创建子目录和日志文件
            current_date = datetime.datetime.now().strftime("%Y%m%d")
            self.log_dir = os.path.join(self.save_path, current_date)
            os.makedirs(self.log_dir, exist_ok=True)
            self.log_file_path = os.path.join(self.log_dir, "log.log")
            self.root.protocol("WM_DELETE_WINDOW", self.close_window)
            self.run()

    def run(self):
        # 启动监听器
        self.keyboard_listener.start()
        self.mouse_listener.start()

        # 运行主循环
        self.root.mainloop()

    def on_key_press(self, key):
        try:
            # 获取按下的按键
            key_char = key.char
            self.text_box.insert(tk.END, f'按下按键: {key_char}\n')
            self.save_to_file()
        except AttributeError:
            # 如果按下的是特殊按键，打印键的名称
            self.text_box.insert(tk.END, f'按下特殊按键: {key}\n')
            self.save_to_file()

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            # 鼠标按键按下事件
            self.text_box.insert(tk.END, f'鼠标按键按下: {button}\n')
            self.save_to_file()
        else:
            # 鼠标按键释放事件
            self.text_box.insert(tk.END, f'鼠标按键释放: {button}\n')
            self.save_to_file()

    def on_mouse_scroll(self, x, y, dx, dy):
        # 滚轮滚动事件
        self.text_box.insert(tk.END, f'鼠标滚轮滚动: ({dx}, {dy})\n')
        self.save_to_file()

    def save_to_file(self):
        if not self.log_file_path:
            return

        # 获取文本框中的内容
        text_content = self.text_box.get("1.0", tk.END)

        # 将内容保存到日志文件
        with open(self.log_file_path, 'a') as file:
            file.write(text_content)

        # 清空文本框
        self.text_box.delete("1.0", tk.END)

    def close_window(self):
        # 停止监听器并关闭窗口
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.save_to_file()  # 保存文件
        self.root.destroy()

if __name__ == "__main__":
    # 创建输入监控对象
    monitor = InputMonitor()
    # 运行监控程序
    monitor.run()







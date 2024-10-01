import tkinter as tk
from tkinter import ttk
import pygetwindow as gw
import keyboard
import mouse
import threading
import time

# Основной класс автокликера с GUI
class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.active_window = None
        self.root.title("Автокликер слона")
        
        # Установка иконки приложения
        self.root.iconbitmap("C:/Users/NoLuck/Desktop/SCRIPTS/slon3.ico")  # Замените на путь к вашему файлу иконки

        # Поле для ввода последовательности нажатий
        self.label_sequence = ttk.Label(root, text="Введите последовательность клавиш (через запятую):")
        self.label_sequence.grid(row=0, column=0, padx=10, pady=5)

        self.entry_sequence = ttk.Entry(root, width=30)
        self.entry_sequence.grid(row=0, column=1, padx=10, pady=5)
        self.entry_sequence.bind("<KeyRelease>", self.check_sequence)

        # Поле для ввода количества кликов
        self.label_clicks = ttk.Label(root, text="Количество повторений (или 0 для бесконечности):")
        self.label_clicks.grid(row=1, column=0, padx=10, pady=5)

        self.entry_clicks = ttk.Entry(root, width=10)
        self.entry_clicks.grid(row=1, column=1, padx=10, pady=5)
        self.entry_clicks.bind("<KeyRelease>", self.check_clicks)

        # Поле для ввода интервала
        self.label_interval = ttk.Label(root, text="Интервал между кликами (в секундах):")
        self.label_interval.grid(row=2, column=0, padx=10, pady=5)

        self.entry_interval = ttk.Entry(root, width=10)
        self.entry_interval.grid(row=2, column=1, padx=10, pady=5)

        # Поле для ввода времени начала
        self.label_start_time = ttk.Label(root, text="Время задержки перед стартом (в секундах):")
        self.label_start_time.grid(row=3, column=0, padx=10, pady=5)

        self.entry_start_time = ttk.Entry(root, width=10)
        self.entry_start_time.grid(row=3, column=1, padx=10, pady=5)

        # Поле для ввода времени завершения
        self.label_end_time = ttk.Label(root, text="Время работы (в секундах) или 0 для бесконечности:")
        self.label_end_time.grid(row=4, column=0, padx=10, pady=5)

        self.entry_end_time = ttk.Entry(root, width=10)
        self.entry_end_time.grid(row=4, column=1, padx=10, pady=5)

        # Поле для выбора клавиш, которые нужно зажимать
        self.label_hold_keys = ttk.Label(root, text="Клавиши для зажатия (через запятую):")
        self.label_hold_keys.grid(row=5, column=0, padx=10, pady=5)

        self.entry_hold_keys = ttk.Entry(root, width=30)
        self.entry_hold_keys.grid(row=5, column=1, padx=10, pady=5)

        # Поле для настройки горячей клавиши запуска
        self.label_start_hotkey = ttk.Label(root, text="Горячая клавиша для запуска: (Alt + A)")
        self.label_start_hotkey.grid(row=6, column=0, padx=10, pady=5)

        # Поле для настройки горячей клавиши остановки
        self.label_stop_hotkey = ttk.Label(root, text="Горячая клавиша для остановки: (Alt + S)")
        self.label_stop_hotkey.grid(row=7, column=0, padx=10, pady=5)

        # Кнопки запуска и остановки
        self.start_button = ttk.Button(root, text="Начать", command=self.start_clicking)
        self.start_button.grid(row=8, column=0, padx=10, pady=10)

        self.stop_button = ttk.Button(root, text="Остановить", command=self.stop_clicking)
        self.stop_button.grid(row=8, column=1, padx=10, pady=10)

        # Поле для вывода сообщений
        self.output_text = tk.Text(root, width=60, height=10, state='disabled')
        self.output_text.grid(row=9, column=0, columnspan=2, padx=10, pady=10)

        # Флаг для остановки кликов
        self.running = False

        # Устанавливаем горячие клавиши для запуска и остановки
        keyboard.add_hotkey('alt+a', self.start_clicking)
        keyboard.add_hotkey('alt+s', self.stop_clicking)

    def check_sequence(self, event):
        if self.entry_sequence.get().strip():
            self.entry_sequence.config({"background": "lightgreen"})
        else:
            self.entry_sequence.config({"background": "lightcoral"})

    def check_clicks(self, event):
        if self.entry_clicks.get().strip():
            self.entry_clicks.config({"background": "lightgreen"})
        else:
            self.entry_clicks.config({"background": "lightcoral"})

    def append_output(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.config(state='disabled')
        self.output_text.yview(tk.END)  # Прокручиваем вниз

    def start_clicking(self):
        self.active_window = gw.getActiveWindow()
        # Получаем значения из полей ввода
        sequence = self.entry_sequence.get().split(',')
        self.append_output(f"Последовательность нажатий: {sequence}")
        hold_keys = self.entry_hold_keys.get().split(',')
        try:
            clicks = int(self.entry_clicks.get())
            interval = float(self.entry_interval.get())
            start_time = float(self.entry_start_time.get())
            end_time = float(self.entry_end_time.get())
        except ValueError as e:
            self.append_output(f"Ошибка ввода: {e}")
            return

        # Устанавливаем флаг, что процесс запущен
        self.running = True
        self.append_output("Кликер запущен.")

        # Запускаем кликер в отдельном потоке с задержкой
        threading.Thread(target=self.clicker_loop, args=(sequence, hold_keys, clicks, interval, start_time, end_time)).start()

    def stop_clicking(self):
        # Останавливаем цикл кликов
        self.running = False
        self.append_output("Нажатия клавиш и мыши остановлены")

    def clicker_loop(self, sequence, hold_keys, clicks, interval, start_time, end_time):
        # Задержка перед началом
        self.append_output(f"Ожидание {start_time} секунд перед запуском...")
        time.sleep(start_time)

        start_time_actual = time.time()

        current_window = gw.getActiveWindow()
            
            # Проверяем, совпадает ли текущее активное окно с окном, в котором запущен кликер
        

        # Зажимаем указанные клавиши, только если они введены
        if hold_keys and any(key.strip() for key in hold_keys):
            for key in hold_keys:
                key = key.strip().lower()
                if key == 'mouse_left':
                    mouse.press(button='left')
                    self.append_output(f"Зажата левая кнопка мыши")
                elif key == 'mouse_right':
                    mouse.press(button='right')
                    self.append_output(f"Зажата правая кнопка мыши")
                else:
                    keyboard.press(key)
                    self.append_output(f"Зажата клавиша: {key}")

        i = 0
        while self.running:

            if current_window != self.active_window:
                self.append_output("Активное окно изменилось, кликер приостановлен.")
                time.sleep(0.1)
                continue  # Ждем, пока активное окно не вернется к нужному

            for action in sequence:
                if not self.running:
                    break

            # Если указано количество кликов (не бесконечность)
            if clicks > 0 and i >= clicks:
                self.append_output("Достигнуто максимальное количество кликов.")
                break

            # Если указано время завершения
            if end_time > 0 and (time.time() - start_time_actual) >= end_time:
                self.append_output("Достигнуто время завершения.")
                break

            # Выполняем последовательность нажатий
            for action in sequence:
                if not self.running:
                    break
                action = action.strip().lower()

                self.append_output(f"Текущее нажатие: {action}")

                if action == 'mouse_left':
                    mouse.click(button='left')
                    self.append_output("Клик левой кнопкой мыши.")
                elif action == 'mouse_right':
                    mouse.click(button='right')
                    self.append_output("Клик правой кнопкой мыши.")
                else:
                    keyboard.press(action)
                    time.sleep(0.05)
                    keyboard.release(action)
                    self.append_output(f"Нажата клавиша: {action}")
                time.sleep(0.05)
                time.sleep(interval)    

            i += 1

        # Отпускаем клавиши, только если они были зажаты
        for key in hold_keys:
            key = key.strip().lower()
            if key == 'mouse_left':
                mouse.release(button='left')
                self.append_output(f"Отжата левая кнопка мыши")
            elif key == 'mouse_right':
                mouse.release(button='right')
                self.append_output(f"Отжата правая кнопка мыши")
            elif key:
                keyboard.release(key)
                self.append_output(f"Отжата клавиша: {key}")

# Создаем окно приложения
root = tk.Tk()
app = AutoClickerApp(root)

# Запуск главного цикла приложения
root.mainloop()

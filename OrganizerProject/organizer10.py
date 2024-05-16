from tkinter import *
from tkinter import messagebox
import calendar
import datetime
import locale
import sqlite3

# Создаем подключение к базе данных
conn = sqlite3.connect('tasks.db')
cursor = conn.cursor()

# Создаем таблицу tasks
cursor.execute('''
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER,
    month INTEGER,
    day INTEGER,
    time TEXT,  -- Новое поле для времени
    task TEXT,
    delayed INTEGER,
    completed INTEGER,
    not_completed INTEGER
)
''')

# Сохраняем изменения и закрываем подключение
conn.commit()
conn.close()

def show_task_dialog(day):
    def save_task_wrapper():
        save_task(dialog, year, month, day, time_entry.get(), text_area.get("1.0", END).strip(), delayed_var, completed_var, not_completed_var)

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    task_data = None
    cursor.execute('''
    SELECT time, task, delayed, completed, not_completed 
    FROM tasks 
    WHERE year = ? AND month = ? AND day = ?
    ''', (year, month, day))
    task_data = cursor.fetchone()
    conn.close()

    if task_data:
        time, task, is_delayed, is_completed, is_not_completed = task_data
    else:
        time = ""
        task = ""
        is_delayed = False
        is_completed = False
        is_not_completed = False

    dialog = Toplevel(root)
    dialog.title(f"Задача для {day} числа")

    time_label = Label(dialog, text="Время:") #поле для добавления времени
    time_label.pack(padx=10, pady=5)
    time_entry = Entry(dialog, width=20)
    time_entry.pack(padx=10, pady=5)
    time_entry.insert(0, time)

    text_area = Text(dialog, height=10, width=50)   #????
    text_area.pack(padx=10, pady=10)
    text_area.insert(END, task)
    
    completed_var = IntVar(value=is_completed)
    completed_checkbox = Radiobutton(dialog, text="Выполнено", variable=completed_var, value=1)
    completed_checkbox.pack(padx=10, pady=5)

    delayed_var = IntVar(value=is_delayed)
    delayed_checkbox = Radiobutton(dialog, text="Задержано", variable=delayed_var, value=1)
    delayed_checkbox.pack(padx=10, pady=5)

    not_completed_var = IntVar(value=is_not_completed)
    not_completed_checkbox = Radiobutton(dialog, text="Не выполнено", variable=not_completed_var, value=1)
    not_completed_checkbox.pack(padx=10, pady=5)

    # Функция для снятия отметок с RadioButton
    def clear_radio_buttons():
        completed_var.set(0)
        delayed_var.set(0)
        not_completed_var.set(0)

    # Привязываем функцию к кнопке для снятия отметок
    clear_button = Button(dialog, text="Очистить галочки", command=clear_radio_buttons)
    clear_button.pack(padx=10, pady=5)

    button_ok = Button(dialog, text="OK", command=save_task_wrapper)
    button_ok.pack(padx=10, pady=5)

    button_delete = Button(dialog, text="Удалить", command=lambda: delete_task(dialog, year, month, day))
    button_delete.pack(padx=10, pady=5)

    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    # Остальная часть кода для диалогового окна остается без изменений

def save_task(dialog, year, month, day, time, task, delayed_var, completed_var, not_completed_var):
    if not task.strip():                                                #ДВЕ ПРОВЕРКИ НА ПРАВИЛЬНОСТЬ ЗАПОЛЕНЕНИЯ ФОРМЫ
        messagebox.showerror("Ошибка", "Запись не может быть пустой!")
        return

    if delayed_var.get() + completed_var.get() + not_completed_var.get() > 1:
        messagebox.showerror("Ошибка", "Выберите только один статус для задачи!")
        return

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute('''
    SELECT id FROM tasks WHERE year = ? AND month = ? AND day = ?
    ''', (year, month, day))
    existing_task = cursor.fetchone()

    if existing_task:
        task_id = existing_task[0]
        cursor.execute('''
        UPDATE tasks 
        SET time=?, task=?, delayed=?, completed=?, not_completed=?
        WHERE id=?
        ''', (time, task, delayed_var.get(), completed_var.get(), not_completed_var.get(), task_id))
    else:
        cursor.execute('''
        INSERT INTO tasks (year, month, day, time, task, delayed, completed, not_completed) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (year, month, day, time, task, delayed_var.get(), completed_var.get(), not_completed_var.get()))
    print('{time}')
    conn.commit()
    conn.close()
    fill()  # Обновляем календарь после сохранения задачи
    dialog.destroy()
    print("Time of the entry:", time)

    now = datetime.now()
    print("Current date and time:", now)

def back():
    global month, year
    month -= 1
    if month == 0:
        month = 12
        year -= 1
    fill()

def next():
    global month, year
    month += 1
    if month == 13:
        month = 1
        year += 1
    fill()

def delete_task(dialog, year, month, day):
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM tasks 
    WHERE year = ? AND month = ? AND day = ?
    ''', (year, month, day))
    print(year, month, day)
    conn.commit()
    cursor.close()
    conn.close()  # Закрываем соединение перед вызовом функции fill()
    print('time')
    fill() # Обновляем календарь после удаления задачи
    dialog.destroy()


def show_entries():                     #СПИСОК ЗАДАЧ ОКНО
    entries_window = Toplevel(root)
    entries_window.title('Список записей и состояний')
    entries_window.geometry("655x500")
    
    entries_window.grid_columnconfigure(0, weight=1)
    entries_window.grid_rowconfigure(0, weight=1)

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT day, time, task, delayed, completed, not_completed 
    FROM tasks 
    WHERE month = ? AND year = ?
    ''', (month, year))

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        no_entries_label = Label(entries_window, text="Записи отсутствуют", font=("Roboto", 14))
        no_entries_label.pack(expand=True)
        return          #код заканчивается если записей нет

    canvas = Canvas(entries_window)   #СКРОЛЛ БАР
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = Scrollbar(entries_window, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    entries_frame = Frame(canvas)
    canvas.create_window((0, 0), window=entries_frame, anchor="nw")

    for row in rows:
        day, time, task, is_delayed, is_completed, is_not_completed = row

        entry_frame = Frame(entries_frame, bg='#ffffff', width=500, height=100)
        entry_frame.pack(fill="both", expand=True)

        # Дополнительные надписи
        before_date_text = "Дата: "
        after_date_text = " "
        before_time_text = "Время: "
        after_time_text = " "

        if time:                                                                            #РЕДАКТИРОВАТЬ НАДПИСИ СЮДА
            date_text = f"{before_date_text}{day}.{month}.{year}{after_date_text}"
            time_text = f"{before_time_text}{time}{after_time_text}"
        else:
            date_text = f"{before_date_text}{day}.{month}.{year}{after_date_text}"
            time_text = ""

        date_label = Label(entry_frame, text=date_text, font=("Roboto", 18), fg='white', bg='#00BFFF', width=30)        #РАЗМЕЩЕНИЕ ????
        date_label.pack(side="top", fill="x")

        if time_text:                                                                                                    #ЕСЛИ ВРЕМЯ НЕ УКАЗАНО
            time_label = Label(entry_frame, text=time_text, font=("Roboto", 20), fg='white', bg='#00BFFF', width=30)
            time_label.pack(side="top", fill="x")

        status_label = Label(entry_frame, text="", font=("Roboto", 15), fg="black", bg='#FFFFFF')
        if is_completed:
            status_label["text"] = "Выполнено"
        elif is_delayed:
            status_label["text"] = "Задержано"
        elif is_not_completed:
            status_label["text"] = "Не выполнено"
        else:
            status_label["text"] = "В работе"
        status_label.pack(side="bottom", fill="x")

        entry_text = Text(entry_frame, wrap="word", height=2, width=50, font=("Roboto", 18), bg='#FFFFFF')
        entry_text.insert("1.0", task)
        entry_text.config(state="disabled")
        entry_text.pack(fill="both", expand=True)

    entries_window.mainloop()
    
from datetime import datetime

def check_due_tasks():
    now = datetime.now()

    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()

    cursor.execute('''  
    SELECT year, month, day, time, task
    FROM tasks 
    WHERE year = ? AND month = ? AND day = ?
    ''', (now.year, now.month, now.day))

    tasks = cursor.fetchall()

    conn.close()

    for task in tasks:
        year, month, day, time, task_description = task
        if not time.strip():        #ПРОВЕРКА НА СЛУЧАЙ ЕСЛИ ВРЕМЯ НЕ БЫЛО УКАЗАНО
            continue

        # Преобразование времени записи в формат 'часы:минуты'
        formatted_time = datetime.strptime(time, '%H:%M').strftime('%H:%M')

        # Преобразование даты записи в формат 'год-месяц-день'
        date_str = f"{year} {month} {day}"                  #ПРЕОБРАЗОВАНИЕ ИНФОРМАЦИИ О ДАТЕ В СТРИНГ
        date_obj = datetime.strptime(date_str, '%Y %m %d')
        formatted_date = date_obj.strftime('%Y-%m-%d')
        if formatted_time == now.strftime('%H:%M') and formatted_date == now.strftime('%Y-%m-%d'):
            print("Reminder:", f"Task scheduled for {formatted_time}: {task_description}")
            messagebox.showinfo("Reminder", f"Task scheduled for {formatted_time}: {task_description}")
        
    root.after(30000, check_due_tasks)  # ПЕРВЫЙ ТАЙМЕР И ЕСТЬ ВТОРОЙ ИХ НУЖНО ДВА ПОЧЕМУ ТО
        
def fill():
    for day_button in days:         #ОЧИСТКА КАЛЕНДАРЯ ПЕРЕД ЕГО ЗАПОЛНЕНИЕМ
        day_button.destroy()
    days.clear()

    global month, year
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')  # Установка русской локали

    info_label['text'] = calendar.month_name[month] + ', ' + str(year)
    month_days = calendar.monthrange(year, month)[1]
    if month == 1:
        back_month_days = calendar.monthrange(year - 1, 12)[1]
    else:
        back_month_days = calendar.monthrange(year, month - 1)[1]
    week_day = calendar.monthrange(year, month)[0]

    russian_weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']  # Список русских дней недели

    for n in range(7):
        lbl = Label(root, text=russian_weekdays[n], width=1, height=1, font='Roboto 12', fg='black', bg='#00BFFF') #СТилизация дней недели
        lbl.grid(row=1, column=n, sticky=NSEW)

    for row in range(6):                                                                            #Я не понимаю это
        for col in range(7):
            day_button = Button(root, text='0', width=4, height=2, font='Roboto 16', bg='blue')
            day_button.grid(row=row + 2, column=col, sticky=NSEW)
            days.append(day_button)

    for n in range(month_days):
        day_button = days[n + week_day]     #ЗАПОЛНЕНИЕ ДНЕЙ КАЛЕНДАРЯ???
        day_button['text'] = n + 1
        day_button['fg'] = 'black'
        day_button['command'] = lambda d=n+1: show_task_dialog(d)  # Привязываем функцию к кнопке

        conn = sqlite3.connect('tasks.db')
        cursor = conn.cursor()

        cursor.execute('''
        SELECT delayed, completed, not_completed 
        FROM tasks 
        WHERE year = ? AND month = ? AND day = ?
        ''', (year, month, n + 1))

        task_data = cursor.fetchone()

        conn.close()

        if task_data:
            is_delayed, is_completed, is_not_completed = task_data

            if is_completed:
                day_button['bg'] = '#2E8B57' #выполнено ЗЕЛЕНЫЙ
            elif is_delayed:
                day_button['bg'] = '#FFD700' #Задержано ЖЕЛТЫЙ
            elif is_not_completed:
                day_button['bg'] = '#DC143C' #Невополнено КРАСНЫЙ
            else:
                day_button['bg'] = 'lightblue' #Сегодняшний день СВЕТЛОЗЕЛЕНЫЙ

            day_button['text'] = f"{n + 1}\n*"
        else:
            day_button['bg'] = '#F0F8FF'
            day_button['text'] = n + 1

        if year == now.year and month == now.month and n + 1 == now.day:
            day_button['bg'] = 'lightgreen'

    for n in range(week_day):
        days[week_day - n - 1]['text'] = back_month_days - n
        days[week_day - n - 1]['fg'] = 'lightgrey'
        days[week_day - n - 1]['bg'] = '#f3f3f3'

    for n in range(6 * 7 - month_days - week_day):
        days[week_day + month_days + n]['text'] = n + 1
        days[week_day + month_days + n]['fg'] = 'lightgrey'
        days[week_day + month_days + n]['bg'] = '#f3f3f3'

root = Tk()
root.title('Календарь')
days = []
now = datetime.now()
year = now.year
month = now.month

back_button = Button(root, text='<', command=back, font=('Roboto', 15,'bold'))          #РАСПОЛОЖЕНИЕ КНОПОК И ЕЕ СТИЛИЗАЦИЯ
back_button.grid(row=0, column=0, sticky=NSEW)
next_button = Button(root, text='>', command=next, font=('Roboto', 15,'bold'))
next_button.grid(row=0, column=6, sticky=NSEW)
info_label = Label(root, text='0', width=1, height=1, font=('Roboto', 20, 'bold'), fg='#00BFFF')
info_label.grid(row=0, column=1, columnspan=5, sticky=NSEW)

show_entries_button = Button(root, text='Записи', command=show_entries, fg='black', bg='#00BFFF', font=('Roboto', 12))
show_entries_button.grid(row=0, column=7, sticky=NSEW)

fill()

for i in range(8):                              #МАСШТАБИРОВАНИЕ ПО СЕТКЕ GRID ПОТОМУ ЧТО????
    root.grid_columnconfigure(i, weight=1)
for i in range(9):                              #?????
    root.grid_rowconfigure(i, weight=1)

root.after(30000, check_due_tasks)  # Таймер, НЕ УДАЛЯТЬ НУЖНО ДВА ТАЙМЕРА ПОЧЕМУ ТО

root.mainloop()
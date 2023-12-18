import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from .user_window import SeancesForm
from .moderator_window import ModeratorForm
from .db_connect import register_user, login_user, get_user_role
from init_db.database_init import db_init
from init_db.database_init.roles import UserRoles


class LoginForm(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title('Форма входа')

    def clear_frame(self):
        # Удаление всех текущих виджетов
        for widgets in self.winfo_children():
            widgets.destroy()

    def draw_widgets(self):
        self.name_label = tk.Label(self, text="Имя пользователя:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.password_label = tk.Label(self, text="Пароль:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.pack()

        self.login_btn = tk.Button(self, text="Войти", command=self.authenticate)
        self.login_btn.pack()

    def authenticate(self):
        user_name = self.name_entry.get()
        password = self.password_entry.get()
        if user_name != "" and password != "":
            pass_hash = hashlib.md5(password.encode()).hexdigest()
            is_login_successfully = login_user(user_name, pass_hash)
            if is_login_successfully:
                if get_user_role(user_name) == UserRoles.cinema_goer.name:
                    self.open_seances_form(user_name)
                else:
                    self.open_moderator_form(user_name)
            else:
                tk.messagebox.showwarning('Ошибка', 'Такого пользователя не существует или введен неправильный пароль.')
        else:
            tk.messagebox.showwarning('Ошибка', 'Необходимо заполнить все поля')

    def open_seances_form(self, user_name):
        self.clear_frame()
        self.destroy()  # закрывает текущее окно
        SeancesForm(user_name).mainloop()  # и открывает окно выбора сеансов

    def open_moderator_form(self, user_name):
        self.clear_frame()
        self.destroy()  # закрывает текущее окно
        ModeratorForm(user_name).mainloop()  # и открывает окно выбора сеансов


class RegisterForm(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.title('Форма регистрации')

    def clear_frame(self):
        # Удаление всех текущих виджетов
        for widgets in self.winfo_children():
            widgets.destroy()

    def draw_widgets(self):
        self.name_label = tk.Label(self, text="Username:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self)
        self.name_entry.pack()

        self.password_label = tk.Label(self, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self, show='*')
        self.password_entry.pack()

        self.register_btn = tk.Button(self, text='Register', command=self.register_user)
        self.register_btn.pack()

        self.role_var = tk.StringVar(self)
        self.roles = ttk.Combobox(self, textvariable=self.role_var, values=[item.name for item in list(UserRoles)])
        self.roles.pack(padx=10, pady=10)

    def register_user(self):
        user_name = self.name_entry.get()
        password = self.password_entry.get()
        role = self.roles.get()
        if user_name != "" and password != "" and role != "":
            pass_hash = hashlib.md5(password.encode()).hexdigest()
            is_registered_successfully = register_user(user_name, pass_hash, role)
            if is_registered_successfully:
                if role == "cinema_goer":
                    self.open_seances_form(user_name)
                else:
                    self.open_moderator_form(user_name)
            else:
                tk.messagebox.showwarning('Ошибка', 'Пользователь с таким именем уже существует!')
        else:
            tk.messagebox.showwarning('Ошибка', 'Необходимо заполнить все поля')

    def open_seances_form(self, user_name):
        self.clear_frame()
        self.destroy()  # закрывает текущее окно
        SeancesForm(user_name).mainloop()  # и открывает окно выбора сеансов

    def open_moderator_form(self, user_name):
        self.clear_frame()
        self.destroy()  # закрывает текущее окно
        ModeratorForm(user_name).mainloop()  # и открывает окно выбора сеансов


class MainForm(tk.Tk):

    def __init__(self):
        super().__init__()

        self.title("Главная страница")
        self.init_login_form()

    def init_login_form(self):
        if db_init.is_db_exists():
            self.init_login_forms()
        else:
            self.init_db_button = tk.Button(self, text='Инициализировать БД', command=self.init_db)
            self.init_db_button.pack(pady=5)

    def init_db(self):
        db_init.init_db()
        db_init.init_structure()
        self.init_db_button.pack_forget()
        self.init_login_forms()

    def init_login_forms(self):
        self.login_btn = tk.Button(self, text='Вход', command=self.open_login)
        self.login_btn.pack(pady=5)
        self.register_btn = tk.Button(self, text='Регистрация', command=self.open_register)
        self.register_btn.pack(pady=5)

    def open_login(self):
        form = LoginForm(self)
        form.draw_widgets()

    def open_register(self):
        form = RegisterForm(self)
        form.draw_widgets()


def init_tkinter():
    main_form = MainForm()
    main_form.config(bg='white')
    main_form.mainloop()

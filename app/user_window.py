import tkinter as tk
from tkinter import ttk
from .db_connect import get_available_sessions, buy_ticket, get_tickets


class SeancesForm(tk.Tk):

    @property
    def sessions(self):
        return get_available_sessions()

    def __init__(self, user):
        super().__init__()
        self.user = user

        self.title("Выбор сеанса")
        self.geometry("400x300")

        self.comboBox_frame = tk.Frame(self)
        self.seancesInfo_frame = tk.Frame(self)
        self.controls_frame = tk.Frame(self)
        self.tickets_frame = tk.Frame(self)

        self.comboBox_frame.pack()
        self.seancesInfo_frame.pack()
        self.controls_frame.pack()
        self.tickets_frame.pack()

        self.seance_var = tk.StringVar(self.comboBox_frame)
        self.combobox = ttk.Combobox(self.comboBox_frame, textvariable=self.seance_var,
                                     values=list(self.sessions.keys()))
        self.combobox.bind('<<ComboboxSelected>>', self.seance_selected)
        self.combobox.pack()
        self.cost_label = tk.Label(self.seancesInfo_frame, text="", bg='lightgrey', fg='black')
        self.cost_label.pack()

        self.genre_label = tk.Label(self.seancesInfo_frame, text="", bg='lightgrey', fg='black')
        self.genre_label.pack()

        self.start_time_label = tk.Label(self.seancesInfo_frame, text="", bg='lightgrey', fg='black')
        self.start_time_label.pack()

        self.actors_label = tk.Label(self.seancesInfo_frame, text="", bg='lightgrey', fg='black')
        self.actors_label.pack()

        self.hall_name_label = tk.Label(self.seancesInfo_frame, text="", bg='lightgrey', fg='black')
        self.hall_name_label.pack()

        self.buy_button = tk.Button(self.controls_frame, text="Забронировать билет", command=self.buy_ticket)
        self.buy_button.pack(padx=10, pady=10)

        self.tickets_button = tk.Button(self.tickets_frame, text="Посмотреть мои билеты", command=self.show_tickets)
        self.tickets_button.pack(padx=10, pady=10)

    def seance_selected(self, event):
        selected_movie = self.sessions[self.seance_var.get()]
        self.cost_label['text'] = f"Стоимость: {str(selected_movie[3])}"
        self.genre_label['text'] = f"Жанр: {selected_movie[2]}"
        self.start_time_label['text'] = f'Время начала: {selected_movie[4]}'
        self.actors_label['text'] = f"В главных ролях: {', '.join(selected_movie[5])}"
        self.hall_name_label['text'] = f"Зал: {selected_movie[1]}"

    def buy_ticket(self):
        movie_name = self.seance_var.get()
        if not movie_name:
            tk.messagebox.showwarning('Невалидное значение', f'Поле с именем фильма не заполнено!')
            return
        session_id_selected_movie = self.sessions[self.seance_var.get()][0]
        buy_ticket(session_id_selected_movie, self.user)
        tk.messagebox.showinfo('Бронирование билета', f'Билет на фильм успешно куплен!')

        self.combobox.pack_forget()
        self.combobox = ttk.Combobox(self.comboBox_frame, textvariable=self.seance_var,
                                     values=list(self.sessions.keys()))
        self.combobox.bind('<<ComboboxSelected>>', self.seance_selected)
        self.combobox.pack()
        self.seance_var.set('')

    def show_tickets(self):
        self.destroy()
        TicketsForm(self.user)  # открываем новую форму для просмотра билетов


class TicketsForm(tk.Tk):

    @property
    def tickets(self):
        return get_tickets(self.user)

    def __init__(self, user):
        super().__init__()
        self.user = user

        self.title("Мои билеты")
        self.geometry("400x300")

        text_template = ("Название фильма: {movie_name}\n"
                         "Жанр:{genre}\n"
                         "Актеры: {actors}\n"
                         "Стоимость билета: {cost}\n"
                         "Время начала: {start_time}\n"
                         "Зал: {hall}\n")
        for ticket in self.tickets:
            tk.Label(self, text=text_template.format(movie_name=ticket[2], genre=ticket[3],
                                                     actors=', '.join(ticket[6]), cost=str(ticket[4]),
                                                     start_time=str(ticket[5]), hall=ticket[1])).pack(padx=10, pady=10)

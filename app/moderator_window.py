import time
import sys
import tkinter as tk
import datetime
from tkmacosx import Button
from tkinter import ttk
import threading
from .db_connect import get_genres, get_actors, add_film, add_actor, add_genre, add_new_hall, add_new_session, \
    get_bought_tickets_today, get_movies, drop_db, delete_movie, update_movie, truncate_tables, get_halls, \
    truncate_movies


class ModeratorForm(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user

        self.title("Панель модератора")
        self.geometry("400x300")

        self.add_film_button = tk.Button(self, text="Добавить новый фильм", command=self.add_film)
        self.add_film_button.pack(padx=10, pady=10)

        self.update_film_button = tk.Button(self, text="Изменить существующий фильм", command=self.update_film)
        self.update_film_button.pack(padx=10, pady=10)

        self.add_actor_button = tk.Button(self, text="Добавить новых актеров", command=self.add_actor)
        self.add_actor_button.pack(padx=10, pady=10)

        self.add_genre_button = tk.Button(self, text="Добавить новые жанры", command=self.add_genre)
        self.add_genre_button.pack(padx=10, pady=10)

        self.add_hall_button = tk.Button(self, text="Добавить новые залы", command=self.add_hall)
        self.add_hall_button.pack(padx=10, pady=10)

        self.add_seance_button = tk.Button(self, text="Добавить новые сеансы", command=self.add_session)
        self.add_seance_button.pack(padx=10, pady=10)

        self.tickets_booked_label = tk.Label(self, width=25)
        self.tickets_booked_label.pack(anchor="w", side="bottom")
        self.update_tickets_booked()

        self.drop_db_button = Button(self, bg='red', text="Дропнуть базу", command=self.drop_db_action)
        self.drop_db_button.pack(anchor="e", side="bottom")

        self.truncate_movies_button = Button(self, bg='red', text="Очистить фильмы",
                                             command=self.truncate_movies_action)
        self.truncate_movies_button.pack(anchor="e", side="bottom")

        self.truncate_all_tables_button = Button(self, bg='red', text="Очистить все таблицы",
                                                 command=self.truncate_all_tables_action)
        self.truncate_all_tables_button.pack(anchor="e", side="bottom")

    def truncate_movies_action(self):
        result = truncate_movies()
        if result:
            tk.messagebox.showinfo('Удалить фильмы', f'Фильмы успешно удалены!')
        else:
            tk.messagebox.showwarning('Удалить фильмы',
                                      'Невозможно удалить фильмы, так как уже существуют сеансы!')
        self.clean_fields()

    def truncate_all_tables_action(self):
        self.kill_event.set()
        truncate_tables()
        sys.exit(0)

    def drop_db_action(self):
        self.kill_event.set()
        tk.messagebox.showwarning('Удаление базы!',
                                  'Для удаления базы нужно ввести пароль от пользователя БД в консоли!')
        drop_db()
        sys.exit(0)

    @property
    def halls(self):
        return get_halls()

    @property
    def genres(self):
        return get_genres()

    @property
    def movies(self):
        return get_movies()

    @property
    def actors(self):
        return {f"{first_name} {last_name}": id_ for (first_name, last_name), id_ in get_actors().items()}

    def update_tickets_booked(self):

        def autoupdate(kill_event):
            while True and not kill_event.is_set():
                tickets_booked = get_bought_tickets_today()
                if tickets_booked:
                    self.tickets_booked_label["text"] = f"билетов забронировано сегодня: {tickets_booked}"
                time.sleep(10)

        self.kill_event = threading.Event()
        thread = threading.Thread(target=autoupdate, args=(self.kill_event,))
        thread.start()

    def update_film(self):

        def callback(event):
            selected_movie = self.movies_var.get()
            self.selected_movie_id, release_year = self.movies[selected_movie]
            movie_genre = list(get_genres(self.selected_movie_id).keys())[0]
            movie_actors = get_actors(self.selected_movie_id)
            self.clean_fields()
            self.set_description_widgets()
            self.release_year_entry.delete(0, tk.END)
            self.release_year_entry.insert(0, str(release_year))
            self.genre_combobox.set(movie_genre)
            for actor, id_ in movie_actors.items():
                self.actor_listbox.select_set(id_ - 1)
            self.update_button = tk.Button(self, text="Изменить фильм", command=self.update_film_action)
            self.update_button.pack()
            self.delete_button = tk.Button(self, text="Удалить фильм", command=self.delete_film_action)
            self.delete_button.pack()

        self.clean_fields()
        self.set_title_label()
        self.movies_var = tk.StringVar(self)
        self.movies_combobox = ttk.Combobox(self, textvariable=self.movies_var, values=list(self.movies.keys()))
        self.movies_combobox.bind("<<ComboboxSelected>>", callback)
        self.movies_combobox.pack()

    def update_film_action(self):

        release_year = self.release_year_entry.get()
        genre = self.genre_var.get()
        selected_actor_indexes = self.actor_listbox.curselection()
        selected_actors = [self.actor_listbox.get(i) for i in selected_actor_indexes]

        if not (release_year and selected_actors and genre):
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Все поля должны быть заполнены.")
            return
        try:
            release_year = int(release_year)
        except Exception as e:
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Введено не правильное значение, поле должно быть годом выхода фильма.")
            return

        update_movie(self.selected_movie_id, release_year, self.genres.get(genre),
                     [self.actors.get(actor) for actor in selected_actors])
        tk.messagebox.showinfo('Изменить фильм', f'Фильм успешно изменен!')
        self.clean_fields()

    def delete_film_action(self):
        result = delete_movie(self.selected_movie_id)
        if result:
            tk.messagebox.showinfo('Удалить фильм', f'Фильм успешно удален!')
        else:
            tk.messagebox.showwarning('Удалить фильм',
                                      'Невозможно удалить фильм, так как уже существуют сеансы с его показом!')
        self.clean_fields()

    def set_title_label(self):
        self.title_label = tk.Label(self, text="Название фильма")
        self.title_label.pack()

    def set_description_widgets(self):
        self.release_year_label = tk.Label(self, text="Год выхода фильма")
        self.release_year_label.pack()

        self.release_year_entry = tk.Entry(self)
        self.release_year_entry.pack()

        self.genre_label = tk.Label(self, text="Жанр")
        self.genre_label.pack()

        self.genre_var = tk.StringVar(self)
        self.genre_combobox = ttk.Combobox(self, textvariable=self.genre_var,
                                           values=list(self.genres.keys()))
        self.genre_combobox.pack()

        self.actors_label = tk.Label(self, text="Актеры")
        self.actors_label.pack()

        self.actor_listbox = tk.Listbox(self, selectmode="multiple")
        for actor, id_ in self.actors.items():
            self.actor_listbox.insert(id_, actor)
        self.actor_listbox.pack()

    def add_film(self):
        self.clean_fields()
        self.set_title_label()
        self.film_entry = tk.Entry(self)
        self.film_entry.pack()
        self.set_description_widgets()
        self.add_button = tk.Button(self, text="Добавить", command=self.add_film_action)
        self.add_button.pack()

    def clean_field(self, field_name: str):
        if hasattr(self, field_name):
            getattr(self, field_name).pack_forget()

    def clean_fields(self):
        fields = ["title_label", "actors_label", "genre_label", "release_year_label", "release_year_label",
                  "film_entry", "release_year_entry", "genre_combobox", "actor_listbox", "add_button", "genre_entry",
                  "genre_button",
                  "actor_first_name_entry", "actor_last_name_entry", "actor_button", "genre_label",
                  "actor_first_name_label", "actor_last_name_label", "hall_name_label", "hall_name_entry",
                  "hall_seats_count_label",
                  "hall_seats_count_entry", "hall_button", "hall_name_label", "session_movie_label",
                  "session_movie_entry", "session_movie_start_time_entry", "session_movie_start_time_label",
                  "session_movie_hall_label", "session_movie_hall_combobox", "session_movie_price_label",
                  "session_movie_price_entry", "session_button", "movies_combobox", "update_button", "delete_button"]

        for field in fields:
            self.clean_field(field)

    def add_film_action(self):
        film_name = self.film_entry.get()
        release_year = self.release_year_entry.get()
        genre = self.genre_var.get()
        selected_actor_indexes = self.actor_listbox.curselection()
        selected_actors = [self.actor_listbox.get(i) for i in selected_actor_indexes]
        if not (film_name and release_year and selected_actors and genre):
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Все поля должны быть заполнены.")
            return
        try:
            release_year = int(release_year)
        except Exception as e:
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Введено не правильное значение, поле должно быть годом выхода фильма.")
            return
        result = add_film(film_name, release_year, self.genres.get(genre),
                          [self.actors.get(actor) for actor in selected_actors])
        if result:
            tk.messagebox.showinfo('Добавить фильм', f'Фильм {film_name} успешно добавлен!')
        else:
            tk.messagebox.showwarning('Дубликат фильма', "Фильм с таким названием уже существует!")

        self.clean_fields()

    def add_actor(self):
        self.clean_fields()

        self.actor_first_name_label = tk.Label(self, text="Имя актера")
        self.actor_first_name_label.pack()

        self.actor_first_name_entry = tk.Entry(self)
        self.actor_first_name_entry.pack()

        self.actor_last_name_label = tk.Label(self, text="Фамилия актера")
        self.actor_last_name_label.pack()

        self.actor_last_name_entry = tk.Entry(self)
        self.actor_last_name_entry.pack()

        self.actor_button = tk.Button(self, text="Добавить актера", command=self.add_actor_action)
        self.actor_button.pack()

    def add_actor_action(self):
        first_name = self.actor_first_name_entry.get()
        last_name = self.actor_last_name_entry.get()

        if not (first_name and last_name):
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Поля с именем и фамилием актера должны быть заполнены.")
            return
        result = add_actor(first_name, last_name)
        if result:
            tk.messagebox.showinfo('Добавить актера', f'Актер {first_name} {last_name} успешно добавлен!')
        else:
            tk.messagebox.showwarning('Дубликат актера', "Актер с таким именем уже существует!")
        self.clean_fields()

    def add_genre(self):
        self.clean_fields()
        self.genre_label = tk.Label(self, text="Жанр")
        self.genre_label.pack()
        self.genre_entry = tk.Entry(self)
        self.genre_entry.pack()
        self.genre_button = tk.Button(self, text="Добавить жанр", command=self.add_genre_action)
        self.genre_button.pack()

    def add_genre_action(self):
        genre = self.genre_entry.get()
        if not genre:
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Поле с жанром должно быть не пустым.")
            return
        result = add_genre(genre)
        if result:
            tk.messagebox.showinfo('Добавить жанр', f'Жанр {genre} успешно добавлен!')
        else:
            tk.messagebox.showwarning('Дубликат жанра', "Жанр с таким названием уже существует!")
        self.clean_fields()

    def add_hall(self):
        self.clean_fields()
        self.hall_name_label = tk.Label(self, text="Имя зала")
        self.hall_name_label.pack()
        self.hall_name_entry = tk.Entry(self)
        self.hall_name_entry.pack()

        self.hall_seats_count_label = tk.Label(self, text="Количество мест")
        self.hall_seats_count_label.pack()
        self.hall_seats_count_entry = tk.Entry(self)
        self.hall_seats_count_entry.pack()
        self.hall_button = tk.Button(self, text="Добавить зал", command=self.add_hall_action)
        self.hall_button.pack()

    def add_hall_action(self):
        hall_name = self.hall_name_entry.get()
        seats_count = self.hall_seats_count_entry.get()
        if not (hall_name and seats_count):
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Поля с именем зала и количеством мест должны быть заполнены.")
            return
        try:
            seats_count = int(seats_count)
        except Exception:
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Поля с количеством мест должно быть целым числом.")
            return

        result = add_new_hall(hall_name, seats_count)
        if result:
            tk.messagebox.showinfo('Добавить зал', f'Зал {hall_name} успешно добавлен!')
        else:
            tk.messagebox.showwarning('Дубликат зала', "Зал с таким названием уже существует!")
        self.clean_fields()

    def add_session(self):
        self.clean_fields()
        self.session_movie_label = tk.Label(self, text="Имя фильма")
        self.session_movie_label.pack()
        self.movies_var = tk.StringVar(self)
        self.movies_combobox = ttk.Combobox(self, textvariable=self.movies_var, values=list(self.movies.keys()))
        self.movies_combobox.pack()

        self.session_movie_start_time_label = tk.Label(self, text="Время начала (ISO)")
        self.session_movie_start_time_label.pack()
        self.session_movie_start_time_entry = tk.Entry(self)
        self.session_movie_start_time_entry.pack()

        self.session_movie_hall_label = tk.Label(self, text="Имя зала")
        self.session_movie_hall_label.pack()
        self.session_var = tk.StringVar(self)
        self.session_movie_hall_combobox = ttk.Combobox(self, textvariable=self.session_var,
                                                        values=list(self.halls))
        self.session_movie_hall_combobox.pack()

        self.session_movie_price_label = tk.Label(self, text="Цена билета")
        self.session_movie_price_label.pack()
        self.session_movie_price_entry = tk.Entry(self)
        self.session_movie_price_entry.pack()

        self.session_button = tk.Button(self, text="Добавить сеанс", command=self.add_session_action)
        self.session_button.pack()

    def add_session_action(self):
        movie_name = self.movies_var.get()
        start_time = self.session_movie_start_time_entry.get()
        hall_name = self.session_var.get()
        price = self.session_movie_price_entry.get()

        if not (movie_name and start_time and hall_name and price):
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Все поля должны быть заполнены.")
            return
        try:
            price = float(price)
        except Exception:
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Цена должна быть числом с плавающей точкой.")
            return

        try:
            start_time = datetime.datetime.fromisoformat(start_time)
        except Exception:
            tk.messagebox.showwarning('Некорректный ввод',
                                      "Время начала должно быть в ISO формате.")
            return

        result = add_new_session(movie_name, start_time, hall_name, price)
        if result:
            tk.messagebox.showinfo('Добавить сеанс',
                                   f'Сеанс успешно добавлен! Все билеты для сеанса были успешно сгенерированы.')
        else:
            tk.messagebox.showwarning('Несуществующий фильм',
                                      "Невозможно добавить сеанс, так как такого фильма или зала не существует!")
        self.clean_fields()

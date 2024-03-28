import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection_engine import Database
from database.tables import *


class MembersInterface:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.root.title("Система профкому")
        Session = sessionmaker(bind=self.database.engine)
        self.session = Session()
        style = ttk.Style()
        style.configure('Green.TButton', background='DeepSkyBlue')  # Колір тексту та кнопок

        self.load_data()
        self.table_label = ttk.Label(root, text="Члени профкому")
        self.table_label.grid(row=0, column=0, pady=10)

        self.options_label = ttk.Label(root, text="Меню")
        self.options_label.grid(row=0, column=1, columnspan=3, pady=10)

        self.role_combobox = ttk.Combobox(root, values=self.role_options, style="Green.TButton")
        self.role_combobox.grid(row=1, column=2, padx=5, pady=5)
        self.role_combobox.current(0)
        self.role_combobox.bind("<<ComboboxSelected>>", self.update_table)

        self.faculty_combobox = ttk.Combobox(root, values=self.faculties_options, style="Green.TButton")
        self.faculty_combobox.grid(row=2, column=2, padx=5, pady=5)
        self.faculty_combobox.current(0)
        self.faculty_combobox.bind("<<ComboboxSelected>>", self.update_table)

        self.delete_button = ttk.Button(root, text="Видалити", command=self.delete_member, style="Green.TButton")
        self.delete_button.grid(row=1, column=3, padx=5, pady=5)

        self.add_button = ttk.Button(root, text="Додати", command=self.add_member, style="Green.TButton")
        self.add_button.grid(row=2, column=3, padx=5, pady=5)

        self.display_table(self.members_df)

    def load_data(self):
        self.roles_df = pd.read_sql_table('roles', con=self.database.engine)
        self.faculties_df = pd.read_sql_table('faculties', con=self.database.engine)
        self.members_df = pd.read_sql_table('members', con=self.database.engine)
        self.members_df = self.members_df.merge(self.roles_df, how='left', left_on='role', right_on='id')
        self.members_df = self.members_df.merge(self.faculties_df, how='left', left_on='faculty', right_on='id')
        self.role_options = ['Усі ролі'] + list(self.roles_df['title'])
        self.faculties_options = ['Усі факультети'] + list(self.faculties_df['title'])

    def update_table(self, event=None):
        selected_role = self.role_combobox.get()
        if selected_role == 'Усі ролі':
            filtered_df = self.members_df
        else:
            print(self.members_df)
            filtered_df = self.members_df[self.members_df['title_x'] == selected_role]
        selected_faculty = self.faculty_combobox.get()

        if selected_faculty == "Усі факультети":
            filtered_fc = self.faculties_df
        else:
            filtered_fc = self.faculties_df[self.members_df["title_y"] == selected_faculty]

        # Одночасне фільтрування за ролями та факультетами
        # Одночасне фільтрування за ролями та факультетами
        filtered_data = pd.merge(filtered_df, filtered_fc, how='inner', left_on='faculty', right_on='id',
                                 suffixes=('_left', '_right'))

        self.table_frame.grid_forget()
        self.display_table(filtered_data)

    def display_table(self, data):
        self.table_frame = ttk.Frame(self.root, style="Green.TButton")
        self.table_frame.grid(row=1, column=0, columnspan=1, sticky="nsew", rowspan=10)
        self.tree = ttk.Treeview(self.table_frame, columns=['Name', 'Surname', 'Role', 'Faculty'], show="headings",
                                 selectmode="browse")

        # Нові назви стовпців
        self.tree.heading('Name', text='Ім\'я')
        self.tree.heading('Surname', text='Прізвище')
        self.tree.heading('Role', text='Роль')
        self.tree.heading('Faculty', text='Факультет')

        for index, row in data.iterrows():
            # Отримання назви ролі за її id з датафрейму self.roles_df
            role_id = row['role']
            role_title = self.roles_df[self.roles_df['id'] == role_id]['title'].iloc[0]

            # Отримання назви факультету за її id з датафрейму self.faculties_df
            faculty_title = row['title_y']

            # Вставка рядка в таблицю з відповідними значеннями
            self.tree.insert("", "end", values=[row['name'], row['surname'], role_title, faculty_title])

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def delete_member(self):
        selected_item = self.tree.focus()
        if selected_item:
            result = messagebox.askyesno("Видалення", "Ви дійсно бажаєте видалити обраного члена?")
            if result:
                with self.session as session:
                    member_id = self.tree.item(selected_item, "values")[0]
                    query = members.delete().where(members.c.id == member_id)
                    session.execute(query)
                    session.commit()
                    messagebox.showinfo("Успішно", "Член був успішно видалений")
                    self.load_data()
                    self.update_table()

    def add_member(self):
        # Створення нового вікна для введення даних нового члена
        add_window = tk.Toplevel(self.root)
        add_window.title("Додати нового члена")

        # Написи та поля для введення даних
        tk.Label(add_window, text="Ім'я:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Прізвище:").grid(row=1, column=0, padx=10, pady=5)
        surname_entry = tk.Entry(add_window)
        surname_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Роль:").grid(row=2, column=0, padx=10, pady=5)
        role_combobox = ttk.Combobox(add_window, values=self.role_options)
        role_combobox.grid(row=2, column=1, padx=10, pady=5)
        role_combobox.current(0)

        tk.Label(add_window, text="Факультет:").grid(row=3, column=0, padx=10, pady=5)
        faculty_combobox = ttk.Combobox(add_window, values=self.faculties_options)
        faculty_combobox.grid(row=3, column=1, padx=10, pady=5)
        faculty_combobox.current(0)

        def save_member():
            new_member = {
                'name': name_entry.get(),
                'surname': surname_entry.get(),
                'role': self.roles_df[self.roles_df['title'] == role_combobox.get()]['id'].iloc[0],
                'faculty': self.faculties_df[self.faculties_df['title'] == faculty_combobox.get()]['id'].iloc[0]
            }
            self.session.execute(members.insert().values(name=new_member["name"],
                                                         surname=new_member["surname"],
                                                         role=new_member["role"],
                                                         faculty=new_member["faculty"]))
            self.session.commit()
            messagebox.showinfo("Успішно", "Новий член був успішно доданий")
            add_window.destroy()
            self.load_data()
            self.update_table()

        # Кнопка для збереження нового члена
        save_button = ttk.Button(add_window, text="Зберегти", command=save_member)
        save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)



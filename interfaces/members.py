import tkinter as tk
from customtkinter import *
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection_engine import Database
from database.tables import *


class MembersInterface:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.root.title("Члени профкому")
        Session = sessionmaker(bind=self.database.engine)
        self.session = Session()
        style = ttk.Style()
        style.configure('Green.TButton', background='DeepSkyBlue')  # Колір тексту та кнопок

        self.load_data()

        style = ttk.Style()
        style.configure('Custom.Treeview', font=('Arial', 11), highlightthickness=0)  # Зміна стилю таблиці
        style.layout('Custom.Treeview',
                     [('Custom.Treeview.treearea', {'sticky': 'nswe'})])  # Визначення області таблиці
        style.layout('Custom.Treeview.Item',
                     [('Custom.Treeview.padding', {'sticky': 'nswe'})])  # Визначення розміщення елементів в таблиці

        self.edit_button = CTkButton(root, text="Редагувати", command=self.edit_member)
        self.edit_button.grid(row=2, column=4, padx=5, pady=5)

        self.role_combobox = CTkComboBox(root, values=self.role_options, command=self.update_table)
        self.role_combobox.grid(row=1, column=3, padx=5, pady=5)

        self.faculty_combobox = CTkComboBox(root, values=self.faculties_options, command=self.update_table)
        self.faculty_combobox.grid(row=1, column=1, padx=5, pady=5)

        self.delete_button = CTkButton(root, text="Видалити", command=self.delete_member,)
        self.delete_button.grid(row=2, column=3, padx=5, pady=5)

        self.add_button = CTkButton(root, text="Додати", command=self.add_member, )
        self.add_button.grid(row=3, column=3, padx=5, pady=5)

        self.search_entry = CTkEntry(root, width=300)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)

        self.search_button = CTkButton(root, text="Пошук", command=self.search_member)
        self.search_button.grid(row=0, column=1, padx=5, pady=5)

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

        filtered_data = pd.merge(filtered_df, filtered_fc, how='inner', left_on='faculty', right_on='id',
                                 suffixes=('_left', '_right'))

        self.table_frame.grid_forget()
        self.display_table(filtered_data)

    def display_table(self, data):
        self.table_frame = CTkFrame(self.root)
        self.table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", rowspan=10)
        self.tree = ttk.Treeview(self.table_frame, columns=['ID', 'Name', 'Surname', 'Role', 'Faculty'], show="headings",
                                 selectmode="browse", style='Custom.Treeview')

        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Ім\'я')
        self.tree.heading('Surname', text='Прізвище')
        self.tree.heading('Role', text='Роль')
        self.tree.heading('Faculty', text='Факультет')

        for index, row in data.iterrows():
            member_id = row["id_x"]
            role_id = row['role']
            role_title = self.roles_df[self.roles_df['id'] == role_id]['title'].iloc[0]

            # Отримання назви факультету за її id з датафрейму self.faculties_df
            faculty_title = row['title_y']

            # Вставка рядка в таблицю з відповідними значеннями
            self.tree.insert("", "end", values=[member_id, row['name'], row['surname'], role_title, faculty_title])

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
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

    def edit_member(self):
        selected_item = self.tree.focus()
        if selected_item:
            member_id = int(self.tree.item(selected_item, "values")[0])
            selected_member = self.members_df[self.members_df['id_x'] == member_id].iloc[0]
            edit_window = CTkToplevel(self.root)
            edit_window.title("Редагувати дані члена")

            CTkLabel(edit_window, text="Ім'я:").grid(row=0, column=0, padx=10, pady=5)
            name_entry = CTkEntry(edit_window)
            name_entry.grid(row=0, column=1, padx=10, pady=5)
            name_entry.insert(0, selected_member['name'])

            CTkLabel(edit_window, text="Прізвище:").grid(row=1, column=0, padx=10, pady=5)
            surname_entry = CTkEntry(edit_window)
            surname_entry.grid(row=1, column=1, padx=10, pady=5)
            surname_entry.insert(0, selected_member['surname'])

            CTkLabel(edit_window, text="Роль:").grid(row=2, column=0, padx=10, pady=5)
            role_combobox = CTkComboBox(edit_window, values=self.role_options)
            role_combobox.grid(row=2, column=1, padx=10, pady=5)
            role_combobox.set(selected_member['title_x'])

            CTkLabel(edit_window, text="Факультет:").grid(row=3, column=0, padx=10, pady=5)
            faculty_combobox = CTkComboBox(edit_window, values=self.faculties_options)
            faculty_combobox.grid(row=3, column=1, padx=10, pady=5)
            faculty_combobox.set(selected_member['title_y'])

            def save_changes():
                new_name = name_entry.get()
                new_surname = surname_entry.get()

                if any(char.isdigit() for char in new_name) or any(char.isdigit() for char in new_surname):
                    messagebox.showerror("Помилка", "Ім'я та прізвище не повинні містити цифр.")
                    return

                updated_data = {
                    'name': new_name,
                    'surname': new_surname,
                    'role': self.roles_df[self.roles_df['title'] == role_combobox.get()]['id'].iloc[0],
                    'faculty': self.faculties_df[self.faculties_df['title'] == faculty_combobox.get()]['id'].iloc[0]
                }

                self.session.execute(members.update().values(name=updated_data["name"],
                                                             surname=updated_data["surname"],
                                                             role=updated_data["role"],
                                                             faculty=updated_data["faculty"]).where(
                    members.c.id == member_id))
                self.session.commit()
                messagebox.showinfo("Успішно", "Дані члена були успішно оновлені")
                edit_window.destroy()
                self.load_data()
                self.update_table()

            save_button = CTkButton(edit_window, text="Зберегти", command=save_changes)
            save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def add_member(self):
        # Створення нового вікна для введення даних нового члена
        add_window = CTkToplevel(self.root)
        add_window.title("Додати нового члена")

        # Написи та поля для введення даних
        CTkLabel(add_window, text="Ім'я:").grid(row=0, column=0, padx=10, pady=5)
        name_entry = CTkEntry(add_window)
        name_entry.grid(row=0, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Прізвище:").grid(row=1, column=0, padx=10, pady=5)
        surname_entry = CTkEntry(add_window)
        surname_entry.grid(row=1, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Роль:").grid(row=2, column=0, padx=10, pady=5)
        role_combobox = CTkComboBox(add_window, values=self.role_options,)
        role_combobox.grid(row=2, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Факультет:").grid(row=3, column=0, padx=10, pady=5)
        faculty_combobox = CTkComboBox(add_window, values=self.faculties_options)
        faculty_combobox.grid(row=3, column=1, padx=10, pady=5)

        def save_member():
            new_name = name_entry.get()
            new_surname = surname_entry.get()

            # Перевірка, чи ім'я та прізвище не містять цифр
            if any(char.isdigit() for char in new_name) or any(char.isdigit() for char in new_surname):
                messagebox.showerror("Помилка", "Ім'я та прізвище не повинні містити цифр.")
                return

            new_member = {
                'name': new_name,
                'surname': new_surname,
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

        save_button = CTkButton(add_window, text="Зберегти", command=save_member)
        save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def search_member(self):
        search_query = self.search_entry.get().strip()
        if search_query:
            filtered_data = self.members_df[self.members_df['name'].str.contains(search_query, case=False) |
                                            self.members_df['surname'].str.contains(search_query, case=False) |
                                            self.members_df["title_x"].str.contains(search_query, case=False) |
                                            self.members_df["title_y"].str.contains(search_query, case=False)
                                            ]

            self.table_frame.grid_forget()
            self.display_table(filtered_data)
        else:
            self.table_frame.grid_forget()
            self.display_table(self.members_df)



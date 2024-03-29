import tkinter as tk
from customtkinter import *
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection_engine import Database
from database.tables import *


class LeasureParticipantsInterface:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.root.title("Учасники заходів відпочинку")
        Session = sessionmaker(bind=self.database.engine)
        self.session = Session()

        self.load_data()

        style = ttk.Style()
        style.configure('Custom.Treeview', font=('Arial', 11), highlightthickness=0)
        style.layout('Custom.Treeview',
                     [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.layout('Custom.Treeview.Item',
                     [('Custom.Treeview.padding', {'sticky': 'nswe'})])

        self.delete_button = CTkButton(root, text="Видалити", command=self.delete_leasure_participant)
        self.delete_button.grid(row=2, column=4, padx=5, pady=5)

        self.add_button = CTkButton(root, text="Додати", command=self.add_leasure_participant)
        self.add_button.grid(row=2, column=3, padx=5, pady=5)

        self.add_leasure_button = CTkButton(root, text="Додати дозвілля", command=self.add_leasure)
        self.add_leasure_button.grid(row=3, column=3, padx=5, pady=5)

        self.search_entry = CTkEntry(root, width=300)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)

        self.search_button = CTkButton(root, text="Пошук", command=self.search_leasure_participant)
        self.search_button.grid(row=0, column=1, padx=5, pady=5)

        self.display_table(self.leasure_participants_df)

    def load_data(self):
        self.leasure_participants_df = pd.read_sql_table('leasure_participants', con=self.database.engine)
        self.leasure_df = pd.read_sql_table('leasure', con=self.database.engine)
        self.members_df = pd.read_sql_table('members', con=self.database.engine)

        self.leasure_participants_df = self.leasure_participants_df.merge(self.leasure_df, how='left',
                                                                          left_on='leasure_id', right_on='id')
        self.leasure_participants_df = self.leasure_participants_df.merge(self.members_df, how='left',
                                                                          left_on='participant_id', right_on='id')

    def display_table(self, data):
        self.table_frame = CTkFrame(self.root)
        self.table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", rowspan=10)
        self.tree = ttk.Treeview(self.table_frame, columns=['ID', 'Leasure', 'Participant', 'Year'], show="headings",
                                 selectmode="browse", style='Custom.Treeview')

        self.tree.heading('ID', text='ID')
        self.tree.heading('Leasure', text='Назва заходу')
        self.tree.heading('Participant', text='Учасник')
        self.tree.heading('Year', text='Рік')

        for index, row in data.iterrows():
            self.tree.insert("", "end", values=[row['id_x'], row['title'], f"{row['name']} {row['surname']}", row["year"]])

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = CTkScrollbar(self.table_frame, orientation="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def delete_leasure_participant(self):
        selected_item = self.tree.focus()
        if selected_item:
            result = messagebox.askyesno("Видалення", "Ви дійсно бажаєте видалити обраного учасника?")
            if result:
                with self.session as session:
                    leasure_participant_id = self.tree.item(selected_item, "values")[0]
                    query = leasure_participants.delete().where(leasure_participants.c.id == leasure_participant_id)
                    session.execute(query)
                    session.commit()
                    messagebox.showinfo("Успішно", "Учасника було успішно видалено")
                    self.load_data()
                    self.display_table(self.leasure_participants_df)

    def add_leasure_participant(self):
        add_window = CTkToplevel(self.root)
        add_window.title("Додати нового учасника заходу")

        CTkLabel(add_window, text="Назва заходу:").grid(row=0, column=0, padx=10, pady=5)
        leasure_combobox = CTkComboBox(add_window, values=self.leasure_df['title'])
        leasure_combobox.grid(row=0, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Учасник:").grid(row=1, column=0, padx=10, pady=5)
        participant_combobox = CTkComboBox(add_window, values=self.members_df.apply(lambda row: f"{row['name']} {row['surname']}", axis=1))
        participant_combobox.grid(row=1, column=1, padx=10, pady=5)

        def save_leasure_participant():
            selected_leasure = leasure_combobox.get()
            selected_participant = participant_combobox.get()

            leasure_id = self.leasure_df[self.leasure_df['title'] == selected_leasure]['id'].iloc[0]
            participant_id = self.members_df[self.members_df.apply(lambda row: f"{row['name']} {row['surname']}", axis=1) == selected_participant]['id'].iloc[0]

            with self.session as session:
                session.execute(leasure_participants.insert().values(leasure_id=leasure_id, participant_id=participant_id))
                session.commit()
                messagebox.showinfo("Успішно", "Нового учасника було успішно додано")
                add_window.destroy()
                self.load_data()
                self.display_table(self.leasure_participants_df)

        save_button = CTkButton(add_window, text="Зберегти", command=save_leasure_participant)
        save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    def search_leasure_participant(self):
        search_query = self.search_entry.get().strip()
        if search_query:
            filtered_data = self.leasure_participants_df[
                self.leasure_participants_df['title'].str.contains(search_query, case=False) |
                self.leasure_participants_df['name'].str.contains(search_query, case=False) |
                self.leasure_participants_df['surname'].str.contains(search_query, case=False)]
            self.table_frame.grid_forget()
            self.display_table(filtered_data)
        else:
            self.table_frame.grid_forget()
            self.display_table(self.leasure_participants_df)

    def add_leasure(self):
        add_leasure_window = CTkToplevel(self.root)
        add_leasure_window.title("Додати нове дозвілля")

        CTkLabel(add_leasure_window, text="Назва заходу:").grid(row=0, column=0, padx=10, pady=5)
        leasure_title_entry = CTkEntry(add_leasure_window)
        leasure_title_entry.grid(row=0, column=1, padx=10, pady=5)

        CTkLabel(add_leasure_window, text="Рік:").grid(row=1, column=0, padx=10, pady=5)
        leasure_year_entry = CTkEntry(add_leasure_window)
        leasure_year_entry.grid(row=1, column=1, padx=10, pady=5)

        def save_leasure():
            new_leasure = {
                'title': leasure_title_entry.get(),
                'year': leasure_year_entry.get()
            }

            with self.session as session:
                session.execute(leasure.insert().values(title=new_leasure["title"], year=new_leasure["year"]))
                session.commit()
                messagebox.showinfo("Успішно", "Нове дозвілля було успішно додано")
                add_leasure_window.destroy()
                self.load_data()

        save_button = CTkButton(add_leasure_window, text="Зберегти", command=save_leasure)
        save_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)


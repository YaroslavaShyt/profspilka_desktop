import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy import create_engine, engine
from database.connection_engine import Database


class MembersInterface:
    def __init__(self, root=tk.Tk(), database=Database()):
        self.root = root
        self.database = database
        self.root.title("Відображення членів")

        self.load_data()

        self.role_combobox = ttk.Combobox(root, values=self.role_options)
        self.role_combobox.grid(row=0, column=0, padx=10, pady=10)
        self.role_combobox.current(0)
        self.role_combobox.bind("<<ComboboxSelected>>", self.update_table)

        self.delete_button = ttk.Button(root, text="Видалити", command=self.delete_member)
        self.delete_button.grid(row=0, column=1, padx=10, pady=10)

        self.display_table(self.members_df)

    def load_data(self):
        self.roles_df = pd.read_sql_table('roles', con=self.database.engine)
        self.members_df = pd.read_sql_table('members', con=self.database.engine)
        self.members_df = self.members_df.merge(self.roles_df, how='left', left_on='role', right_on='id')
        self.role_options = ['Усі ролі'] + list(self.roles_df['title'])

    def update_table(self, event=None):
        selected_role = self.role_combobox.get()
        if selected_role == 'Усі ролі':
            filtered_df = self.members_df
        else:
            filtered_df = self.members_df[self.members_df['title'] == selected_role]
        self.table_frame.grid_forget()
        self.display_table(filtered_df)

    def display_table(self, data):
        self.table_frame = ttk.Frame(self.root)
        self.table_frame.grid(row=1, column=0, padx=10, pady=10)
        self.tree = ttk.Treeview(self.table_frame, columns=list(data.columns), show="headings", selectmode="browse")
        for column in data.columns:
            self.tree.heading(column, text=column)
            self.tree.column(column, anchor="center")
        for index, row in data.iterrows():
            self.tree.insert("", "end", values=list(row))
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def delete_member(self):
        selected_item = self.tree.focus()
        if selected_item:
            result = messagebox.askyesno("Видалення", "Ви дійсно бажаєте видалити обраного члена?")
            if result:
                member_id = self.tree.item(selected_item, "values")[0]
                query = f"DELETE FROM members WHERE id={member_id}"
                self.database.execute(query)
                self.load_data()
                self.update_table()


root = tk.Tk()
app = MembersInterface(root)
root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from customtkinter import *
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection_engine import Database
from database.tables import *
import matplotlib.pyplot as plt
import os


class ExpensesInterface:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.root.title("Витрати профкому")
        Session = sessionmaker(bind=self.database.engine)
        self.session = Session()
        # self.root.configure(bg='#0d1d1f')
        style = ttk.Style()
        style.configure('Green.TButton', background='DeepSkyBlue')

        self.load_data()

        self.sort_combobox = CTkComboBox(root, values=['Рік', 'Сума'], command=self.sort_table)
        self.sort_combobox.grid(row=1, column=3, padx=5, pady=5)

        style = ttk.Style()
        style.configure('Custom.Treeview.Heading', font=('Arial', 12, 'bold'))  # Зміна стилю заголовків
        style.configure('Custom.Treeview', font=('Arial', 11), highlightthickness=0)  # Зміна стилю таблиці
        style.layout('Custom.Treeview',
                     [('Custom.Treeview.treearea', {'sticky': 'nswe'})])  # Визначення області таблиці
        style.layout('Custom.Treeview.Item',
                     [('Custom.Treeview.padding', {'sticky': 'nswe'})])  # Визначення розміщення елементів в таблиці

        self.delete_button = CTkButton(root, text="Видалити", command=self.delete_expense, )
        self.delete_button.grid(row=2, column=4, padx=5, pady=5)

        self.add_button = CTkButton(root, text="Додати", command=self.add_expense, )
        self.add_button.grid(row=2, column=3, padx=5, pady=5)

        self.search_entry = CTkEntry(root, width=300)
        self.search_entry.grid(row=0, column=0, padx=5, pady=5)

        self.search_button = CTkButton(root, text="Пошук", command=self.search_expense)
        self.search_button.grid(row=0, column=1, padx=5, pady=5)

        self.edit_button = CTkButton(root, text="Редагувати", command=self.edit_expense)
        self.edit_button.grid(row=3, column=4, padx=5, pady=5)

        self.display_table(self.expenses_df)

        self.plot_button = CTkButton(root, text="Побудувати графік", command=self.generate_plot, )
        self.plot_button.grid(row=3, column=3, padx=10, pady=10)

    def load_data(self):
        self.expenses_df = pd.read_sql_table('expenses', con=self.database.engine)
        self.members_df = pd.read_sql_table('members', con=self.database.engine)
        self.faculties_df = pd.read_sql_table('faculties', con=self.database.engine)
        self.members_df = self.members_df.merge(self.faculties_df, how='left', left_on='faculty', right_on='id')
        self.expenses_df = self.expenses_df.merge(self.members_df, how='left', left_on='id_member', right_on='id_x')

    def sort_table(self, event=None):
        sort_option = self.sort_combobox.get()
        if sort_option == 'Рік':
            self.expenses_df = self.expenses_df.sort_values(by='year', ascending=False)
        elif sort_option == 'Сума':
            self.expenses_df = self.expenses_df.sort_values(by='amount', ascending=False)
        self.display_table(self.expenses_df)

    def display_table(self, data):
        self.table_frame = CTkFrame(self.root, width=50, corner_radius=100)
        self.table_frame.grid(row=1, column=0, columnspan=2, rowspan=10, sticky="nsew")
        self.tree = ttk.Treeview(self.table_frame, style='Custom.Treeview',
                                 columns=['Expense ID', 'Name', 'Surname', 'Faculty', 'Amount', 'Purpose', 'Year'],
                                 show="headings")
        self.tree.heading('Expense ID', text='Expense ID')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Surname', text='Surname')
        self.tree.heading('Faculty', text='Faculty')
        self.tree.heading('Amount', text='Amount')
        self.tree.heading('Purpose', text='Purpose')
        self.tree.heading('Year', text='Year')

        self.tree.column('Expense ID', minwidth=50, width=100)
        self.tree.column('Name', minwidth=50, width=100)
        self.tree.column('Surname', minwidth=50, width=100)
        self.tree.column('Faculty', minwidth=50, width=100)
        self.tree.column('Amount', minwidth=50, width=100)
        self.tree.column('Purpose', minwidth=50, width=100)
        self.tree.column('Year', minwidth=50, width=100)

        for index, row in data.iterrows():
            name = row['name']
            surname = row['surname']
            faculty = row['title']
            self.tree.insert("", "end",
                             values=[row['id'], name, surname, faculty, row['amount'], row['purpose'], row['year']])

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(self.table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

    def delete_expense(self):
        selected_item = self.tree.focus()
        if selected_item:
            result = messagebox.askyesno("Видалення", "Ви дійсно бажаєте видалити обрану витрату?")
            if result:
                with self.session as session:
                    expense_id = self.tree.item(selected_item, "values")[0]
                    query = expenses.delete().where(expenses.c.id == expense_id)
                    session.execute(query)
                    session.commit()
                    messagebox.showinfo("Успішно", "Витрата була успішно видалена")
                    self.load_data()
                    self.display_table(self.expenses_df)

    def add_expense(self):
        add_window = CTkToplevel(self.root)
        add_window.title("Додати витрати")

        CTkLabel(add_window, text="Член:").grid(row=0, column=0, padx=10, pady=5)

        # Заповнення комбобоксу іменами та прізвищами членів
        members_names = self.members_df['name'] + ' ' + self.members_df['surname']
        member_combobox = CTkComboBox(add_window, values=members_names)
        member_combobox.grid(row=0, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Сума:").grid(row=1, column=0, padx=10, pady=5)
        amount_entry = CTkEntry(add_window)
        amount_entry.grid(row=1, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Призначення:").grid(row=2, column=0, padx=10, pady=5)
        purpose_entry = CTkEntry(add_window)
        purpose_entry.grid(row=2, column=1, padx=10, pady=5)

        CTkLabel(add_window, text="Рік:").grid(row=3, column=0, padx=10, pady=5)
        year_entry = CTkEntry(add_window)
        year_entry.grid(row=3, column=1, padx=10, pady=5)

        def save_expense():
            selected_name = member_combobox.get()

            id_member = self.members_df[(self.members_df['name'] == selected_name.split()[0]) &
                                        (self.members_df['surname'] == selected_name.split()[1])]['id_x'][0]

            self.session.execute(expenses.insert().values(id_member=id_member,
                                                          amount=float(amount_entry.get()),
                                                          purpose=purpose_entry.get(),
                                                          year=int(year_entry.get())))

            self.session.commit()
            messagebox.showinfo("Успішно", "Нові витрати були успішно додані")
            add_window.destroy()
            self.load_data()
            self.display_table(self.expenses_df)

        save_button = CTkButton(add_window, text="Зберегти", command=save_expense)
        save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def edit_expense(self):
        selected_item = self.tree.focus()
        if selected_item:
            edit_window = CTkToplevel(self.root)
            edit_window.title("Редагувати витрати")

            expense_id = int(self.tree.item(selected_item, "values")[0])
            selected_expense = self.expenses_df[self.expenses_df['id'] == expense_id].iloc[0]

            CTkLabel(edit_window, text="ID Member:").grid(row=0, column=0, padx=10, pady=5)
            id_member_entry = CTkEntry(edit_window)
            id_member_entry.grid(row=0, column=1, padx=10, pady=5)
            id_member_entry.insert(0, str(selected_expense['id_member']))

            CTkLabel(edit_window, text="Amount:").grid(row=1, column=0, padx=10, pady=5)
            amount_entry = CTkEntry(edit_window)
            amount_entry.grid(row=1, column=1, padx=10, pady=5)
            amount_entry.insert(0, str(selected_expense['amount']))

            CTkLabel(edit_window, text="Purpose:").grid(row=2, column=0, padx=10, pady=5)
            purpose_entry = CTkEntry(edit_window)
            purpose_entry.grid(row=2, column=1, padx=10, pady=5)
            purpose_entry.insert(0, selected_expense['purpose'])

            CTkLabel(edit_window, text="Year:").grid(row=3, column=0, padx=10, pady=5)
            year_entry = CTkEntry(edit_window)
            year_entry.grid(row=3, column=1, padx=10, pady=5)
            year_entry.insert(0, str(selected_expense['year']))

            def save_changes():
                self.session.execute(expenses.update().values(id_member=int(id_member_entry.get()),
                                                              amount=float(amount_entry.get()),
                                                              purpose=purpose_entry.get(),
                                                              year=int(year_entry.get())).where(
                    expenses.c.id == expense_id))
                self.session.commit()
                messagebox.showinfo("Успішно", "Зміни були успішно збережені")
                edit_window.destroy()
                self.load_data()
                self.display_table(self.expenses_df)

            save_button = CTkButton(edit_window, text="Зберегти", command=save_changes)
            save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def generate_plot(self):
        grouped_data = self.expenses_df.groupby('year')['amount'].sum()
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.bar(grouped_data.index.astype(str), grouped_data.values)
        plt.xlabel('Рік')
        plt.ylabel('Загальні витрати')
        plt.title('Загальні витрати за роками')

        categories_data = self.expenses_df.groupby('purpose')['amount'].sum()
        plt.subplot(1, 2, 2)
        plt.pie(categories_data.values, labels=categories_data.index, autopct='%1.1f%%')
        plt.axis('equal')
        plt.title('Витрати за категоріями')
        plt.tight_layout()

        directory = "../plots"
        if not os.path.exists(directory):
            os.makedirs(directory)
        plt.savefig(os.path.join(directory, "expenses_plot.png"))

        messagebox.showinfo("Успіх", "Графік успішно згенеровано та збережено у папці 'plots'!")

    def search_expense(self):
        search_query = self.search_entry.get().strip()

        if search_query:

            filtered_data = self.expenses_df[self.expenses_df['purpose'].str.contains(search_query, case=False) |
                                             self.expenses_df['name'].str.contains(search_query, case=False) |
                                             self.expenses_df['surname'].str.contains(search_query, case=False) |
                                             self.expenses_df['title'].str.contains(search_query, case=False)
                                             ]
            self.table_frame.grid_forget()
            self.display_table(filtered_data)
        else:
            self.table_frame.grid_forget()
            self.display_table(self.expenses_df)

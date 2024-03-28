import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from sqlalchemy.orm import sessionmaker
from database.connection_engine import Database
from database.tables import *
import matplotlib.pyplot as plt


class ExpensesInterface:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.root.title("Витрати профкому")
        Session = sessionmaker(bind=self.database.engine)
        self.session = Session()
       # self.root.configure(bg='#0d1d1f')
        style = ttk.Style()
        style.configure('Green.TButton', background='DeepSkyBlue')  # Колір тексту та кнопок

        self.load_data()
        self.table_label = ttk.Label(root, text="Витрати")
        self.table_label.grid(row=0, column=0, pady=10)

        self.options_label = ttk.Label(root, text="Меню")
        self.options_label.grid(row=0, column=1, pady=10)

        self.sort_combobox = ttk.Combobox(root, values=['Рік', 'Сума'], style="Green.TButton")
        self.sort_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.sort_combobox.current(0)
        self.sort_combobox.bind("<<ComboboxSelected>>", self.sort_table)

        self.delete_button = ttk.Button(root, text="Видалити", command=self.delete_expense, style="Green.TButton")
        self.delete_button.grid(row=2, column=1, padx=5, pady=5)

        self.add_button = ttk.Button(root, text="Додати", command=self.add_expense, style="Green.TButton")
        self.add_button.grid(row=1, column=2, padx=5, pady=5)

        self.display_table(self.expenses_df)

        self.plot_button = ttk.Button(root, text="Побудувати графік", command=self.generate_plot, style="Green.TButton")
        self.plot_button.grid(row=2, column=2, columnspan=4, padx=10, pady=10)

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
        self.table_frame = ttk.Frame(self.root, width=50, style="Green.TButton")
        self.table_frame.grid(row=1, column=0, columnspan=1, rowspan=10, sticky="nsew")
        self.tree = ttk.Treeview(self.table_frame,
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
        print(self.members_df)
        for index, row in data.iterrows():
            member_data = self.members_df[self.members_df['id_x'] == row['id_member']].iloc[0]
            name = member_data['name']
            surname = member_data['surname']
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
        add_window = tk.Toplevel(self.root)
        add_window.title("Додати витрати")

        tk.Label(add_window, text="ID Member:").grid(row=0, column=0, padx=10, pady=5)
        id_member_entry = tk.Entry(add_window)
        id_member_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Amount:").grid(row=1, column=0, padx=10, pady=5)
        amount_entry = tk.Entry(add_window)
        amount_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Purpose:").grid(row=2, column=0, padx=10, pady=5)
        purpose_entry = tk.Entry(add_window)
        purpose_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(add_window, text="Year:").grid(row=3, column=0, padx=10, pady=5)
        year_entry = tk.Entry(add_window)
        year_entry.grid(row=3, column=1, padx=10, pady=5)

        def save_expense():
            self.session.execute(expenses.insert().values(id_member=int(id_member_entry.get()),
                                   amount=float(amount_entry.get()),
                                   purpose=purpose_entry.get(),
                                   year=int(year_entry.get())))

            self.session.commit()
            messagebox.showinfo("Успішно", "Нові витрати були успішно додані")
            add_window.destroy()
            self.load_data()
            self.display_table(self.expenses_df)

        save_button = ttk.Button(add_window, text="Зберегти", command=save_expense)
        save_button.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

    def generate_plot(self):
        grouped_data = self.expenses_df.groupby('year')['amount'].sum()
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.bar(grouped_data.index.astype(str), grouped_data.values)
        plt.xlabel('Рік')
        plt.ylabel('Загальні витрати')
        plt.title('Загальні витрати за роками')

        # Графік витрат за категоріями
        categories_data = self.expenses_df.groupby('purpose')['amount'].sum()
        plt.subplot(1, 2, 2)
        plt.pie(categories_data.values, labels=categories_data.index, autopct='%1.1f%%')
        plt.axis('equal')
        plt.title('Витрати за категоріями')

        plt.tight_layout()
        plt.show()



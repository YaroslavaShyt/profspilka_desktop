from members import *
from expenses import ExpensesInterface
from leasure_participants import LeasureParticipantsInterface


class HomePage:
    def __init__(self, root, database):
        self.root = root
        self.database = database
        self.root.title("Меню")

        self.label = CTkLabel(root, text="Профспілкова система", font=("Lucida Console", 14,), padx=20)
        self.label.pack(pady=20)
        self.label = CTkLabel(root, text="<<НТУУ КПІ>>", font=("Lucida Console", 12,),)
        self.label.pack(pady=10)

        self.members_button = CTkButton(root, text="Члени профспілки", command=self.open_members_page)
        self.members_button.pack(pady=20)

        self.expenses_button = CTkButton(root, text="Витрати профспілки", command=self.open_expenses_page)
        self.expenses_button.pack(pady=20)

        self.leasure_button = CTkButton(root, text="Дозвілля профспілки", command=self.open_leasure_participants_page)
        self.leasure_button.pack(pady=20)

    def open_members_page(self):
        members_page = CTkToplevel(self.root)
        members_page.title("Члени профспілки")
        app = MembersInterface(members_page, self.database)

    def open_expenses_page(self):
        expenses_page = CTkToplevel(self.root)
        expenses_page.title("Витрати профспілки")
        app = ExpensesInterface(expenses_page, self.database)

    def open_leasure_participants_page(self):
        expenses_page = CTkToplevel(self.root)
        expenses_page.title("Дозвілля профспілки")
        app = LeasureParticipantsInterface(expenses_page, self.database)


if __name__ == "__main__":
    root = CTk()
    database = Database()
    app = HomePage(root, database)
    root.mainloop()

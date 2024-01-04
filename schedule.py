import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import pandas as pd

class ToDoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ToDo App")
        self.root.geometry("1800x900")
        self.root.resizable(True, True)

        # Initialize data
        self.load_data()

        # Create UI elements
        self.create_tabs()
        self.create_date_label()
        self.create_tables()
        self.create_context_menu()
        self.create_buttons()

    def load_data(self):
        try:
            self.df = pd.read_csv("tasks.csv")
        except FileNotFoundError:
            self.df = pd.DataFrame(columns=["ID", "Name", "Date Created", "Description", "Due Date", "Status"])

    def save_data(self):
        self.df.to_csv("tasks.csv", index=False)

    def create_tabs(self):
        self.tabs = ttk.Notebook(self.root)

        self.daily_tab = ttk.Frame(self.tabs)
        self.weekly_tab = ttk.Frame(self.tabs)

        self.tabs.add(self.daily_tab, text="Daily To-Do")
        self.tabs.add(self.weekly_tab, text="Weekly To-Do")

        self.tabs.pack(expand=1, fill="both")

    def create_date_label(self):
        # Date label
        date_label = tk.Label(self.daily_tab, text=datetime.now().strftime("%A, %B %d, %Y"), font=("Helvetica", 14, "bold"))
        date_label.pack(pady=10, anchor="center")

    def create_tables(self):
        # Create three separate Treeview widgets for each column
        self.to_do_table = ttk.Treeview(self.daily_tab, columns=("Name",), show="headings")
        self.in_progress_table = ttk.Treeview(self.daily_tab, columns=("Description",), show="headings")
        self.finished_table = ttk.Treeview(self.daily_tab, columns=("Due Date",), show="headings")

        # Set column headings
        self.to_do_table.heading("Name", text="To-Do")
        self.in_progress_table.heading("Description", text="In Progress")
        self.finished_table.heading("Due Date", text="Finished")

        # Bind events to tables
        self.to_do_table.bind("<Double-1>", self.show_task_details)
        self.to_do_table.bind("<Button-3>", self.show_context_menu)
        self.in_progress_table.bind("<Double-1>", self.show_task_details)
        self.in_progress_table.bind("<Button-3>", self.show_context_menu)
        self.finished_table.bind("<Double-1>", self.show_task_details)
        self.finished_table.bind("<Button-3>", self.show_context_menu)

        # Pack tables to the left and right
        self.to_do_table.pack(side="left", expand=1, fill="both", padx=(0, 1))
        self.in_progress_table.pack(side="left", expand=1, fill="both", padx=(0, 1))
        self.finished_table.pack(side="left", expand=1, fill="both")

        # Load tasks into the tables
        self.load_tasks()

    def load_tasks(self):
        # Clear existing data in tables
        for table in [self.to_do_table, self.in_progress_table, self.finished_table]:
            table.delete(*table.get_children())

        # Load tasks into the respective tables
        for index, row in self.df.iterrows():
            if row["Status"] == "To-Do":
                self.to_do_table.insert("", "end", values=(row["Name"],))
            elif row["Status"] == "In Progress":
                self.in_progress_table.insert("", "end", values=(row["Name"],))
            elif row["Status"] == "Finished":
                self.finished_table.insert("", "end", values=(row["Name"],))

    def add_task(self, name, description, due_date, status):
        current_date = datetime.now().strftime("%m/%d/%Y")
        new_task = {"ID": len(self.df) + 1, "Name": name, "Date Created": current_date,
                    "Description": description, "Due Date": due_date, "Status": status}
        self.df = pd.concat([self.df, pd.DataFrame([new_task])], ignore_index=True)
        self.save_data()
        self.load_tasks()

    def remove_task(self, task_id):
        self.df = self.df[self.df["ID"] != task_id]
        self.save_data()
        self.load_tasks()

    def move_task(self, task_id, new_status):
        self.df.loc[self.df["ID"] == task_id, "Status"] = new_status
        self.save_data()
        self.load_tasks()

    def show_task_details(self, event):
        table = event.widget
        item = table.selection()[0]
        if table == self.to_do_table:
            status = "To-Do"
        elif table == self.in_progress_table:
            status = "In Progress"
        elif table == self.finished_table:
            status = "Finished"

        task_name = table.item(item, "values")[0]
        task_details = self.df[(self.df["Name"] == task_name) & (self.df["Status"] == status)].iloc[0]
        details_str = f"Name: {task_details['Name']}\n" \
                      f"Description: {task_details['Description']}\n" \
                      f"Date Created: {task_details['Date Created']}\n" \
                      f"Due Date: {task_details['Due Date']}"    
        messagebox.showinfo("Task Details", details_str)

    def show_context_menu(self, event):
        table = event.widget
        item = table.selection()[0]
        if table == self.to_do_table:
            status = "To-Do"
        elif table == self.in_progress_table:
            status = "In Progress"
        elif table == self.finished_table:
            status = "Finished"

        task_name = table.item(item, "values")[0]

        # Clear the context menu before adding new commands
        self.context_menu.delete(0, "end")

        def move_to_todo():
            task_id = self.df[(self.df["Name"] == task_name) & (self.df["Status"] == status)]["ID"].values[0]
            self.move_task(task_id, "To-Do")
        
        def move_to_in_progress():
            task_id = self.df[(self.df["Name"] == task_name) & (self.df["Status"] == status)]["ID"].values[0]
            self.move_task(task_id, "In Progress")

        def move_to_finished():
            tasks = self.df[(self.df["Name"] == task_name) & (self.df["Status"] == status)]
            if not tasks.empty:
                task_id = tasks["ID"].values[0]
                self.move_task(task_id, "Finished")

        self.context_menu.add_command(label="Set to To-Do", command=move_to_todo)
        self.context_menu.add_command(label="Move to In Progress", command=move_to_in_progress)
        self.context_menu.add_command(label="Move to Finished", command=move_to_finished)

        # Post the context menu
        self.context_menu.post(event.x_root, event.y_root)

    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)

    def create_buttons(self):
        add_button = tk.Button(self.root, text="Add Task", command=self.add_task_dialog)
        add_button.pack(side="left", padx=5)

        remove_button = tk.Button(self.root, text="Remove Task", command=self.remove_task_button)
        remove_button.pack(side="left", padx=5)

    def add_task_dialog(self):
        dialog = AddTaskDialog(self.root)
        if dialog.result:
            # Determine the initial status based on the selected tab
            current_tab = self.tabs.index(self.tabs.select())
            if current_tab == 0:
                status = "To-Do"
            else:
                # You can customize the behavior for other tabs if needed
                status = "To-Do"

            self.add_task(dialog.name, dialog.description, dialog.due_date, status)

    def remove_task_button(self):
        selected_item = None
        current_tab = self.tabs.index(self.tabs.select())
        if current_tab == 0:
            selected_item = self.to_do_table.selection()
        elif current_tab == 1:
            selected_item = self.in_progress_table.selection()
        elif current_tab == 2:
            selected_item = self.finished_table.selection()

        if selected_item:
            task_name = None
            if current_tab == 0:
                task_name = self.to_do_table.item(selected_item, "values")[0]
            elif current_tab == 1:
                task_name = self.in_progress_table.item(selected_item, "values")[0]
            elif current_tab == 2:
                task_name = self.finished_table.item(selected_item, "values")[0]

            task_id = self.df[(self.df["Name"] == task_name) & (self.df["Status"] == self.get_current_status())]["ID"].values[0]
            confirm = messagebox.askyesno("Confirmation", f"Are you sure you want to remove {task_name}?")
            if confirm:
                self.remove_task(task_id)

    def get_current_status(self):
        current_tab = self.tabs.index(self.tabs.select())
        if current_tab == 0:
            return "To-Do"
        elif current_tab == 1:
            return "In Progress"
        elif current_tab == 2:
            return "Finished"


class AddTaskDialog(tk.simpledialog.Dialog):
    def body(self, master):
        tk.Label(master, text="Task Name:").grid(row=0, sticky="w")
        tk.Label(master, text="Description:").grid(row=1, sticky="w")
        tk.Label(master, text="Due Date (MM/DD/YYYY):").grid(row=2, sticky="w")

        self.name_entry = tk.Entry(master)
        self.description_entry = tk.Entry(master)
        self.due_date_entry = tk.Entry(master)

        self.name_entry.grid(row=0, column=1, sticky="w")
        self.description_entry.grid(row=1, column=1, sticky="w")
        self.due_date_entry.grid(row=2, column=1, sticky="w")

        # Set default due date to current date
        self.due_date_entry.insert(0, datetime.now().strftime("%m/%d/%Y"))

        return self.name_entry  # Focus on the name entry field

    def apply(self):
        self.result = True
        self.name = self.name_entry.get()
        self.description = self.description_entry.get()
        self.due_date = self.due_date_entry.get()


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()

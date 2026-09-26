import tkinter as tk
from tkinter import messagebox, ttk

import main


class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pass Manager")
        self.root.geometry("820x560")
        self.root.minsize(700, 480)
        self.master_password = None
        self.logins = []
        self.password_visible = False

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Title.TLabel", font=("Segoe UI", 24, "bold"))
        style.configure("Subtitle.TLabel", foreground="#5b6472")
        style.configure("Treeview", rowheight=32, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

        self.build_unlock_view()

    def build_unlock_view(self):
        self.unlock_frame = ttk.Frame(self.root, padding=48)
        self.unlock_frame.pack(expand=True)
        ttk.Label(self.unlock_frame, text="Pass Manager", style="Title.TLabel").pack(pady=(0, 8))
        ttk.Label(self.unlock_frame, text="Unlock your encrypted login vault", style="Subtitle.TLabel").pack(pady=(0, 28))
        ttk.Label(self.unlock_frame, text="Master password").pack(anchor="w")
        self.master_entry = ttk.Entry(self.unlock_frame, show="*", width=34)
        self.master_entry.pack(fill="x", pady=(6, 14))
        self.master_entry.bind("<Return>", lambda event: self.unlock())
        ttk.Button(self.unlock_frame, text="Unlock vault", command=self.unlock).pack(fill="x")
        self.unlock_status = ttk.Label(self.unlock_frame, style="Subtitle.TLabel")
        self.unlock_status.pack(pady=(14, 0))
        self.master_entry.focus_set()

    def unlock(self):
        password = self.master_entry.get()
        if not password:
            self.unlock_status.configure(text="Enter your master password.")
            return
        try:
            self.logins = main.get_all_logins(password)
        except (ValueError, KeyError, TypeError) as error:
            self.unlock_status.configure(text=str(error))
            return
        self.master_password = password
        self.unlock_frame.destroy()
        self.build_vault_view()

    def build_vault_view(self):
        frame = ttk.Frame(self.root, padding=24)
        frame.pack(fill="both", expand=True)
        header = ttk.Frame(frame)
        header.pack(fill="x", pady=(0, 18))
        ttk.Label(header, text="Your vault", style="Title.TLabel").pack(side="left")
        ttk.Button(header, text="Change master password", command=self.change_master_password).pack(side="right")

        content = ttk.Panedwindow(frame, orient="horizontal")
        content.pack(fill="both", expand=True)
        list_frame = ttk.Frame(content, padding=(0, 0, 16, 0))
        details = ttk.LabelFrame(content, text="Login details", padding=18)
        content.add(list_frame, weight=3)
        content.add(details, weight=2)

        self.login_table = ttk.Treeview(list_frame, columns=("username",), show="headings", selectmode="browse")
        self.login_table.heading("username", text="Username")
        self.login_table.column("username", anchor="w", width=260)
        self.login_table.pack(fill="both", expand=True)
        self.login_table.bind("<<TreeviewSelect>>", self.show_selected_login)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.login_table.yview)
        scrollbar.place(relx=1, rely=0, relheight=1, anchor="ne")
        self.login_table.configure(yscrollcommand=scrollbar.set)

        ttk.Label(details, text="Username").pack(anchor="w")
        self.username_entry = ttk.Entry(details)
        self.username_entry.pack(fill="x", pady=(5, 14))
        ttk.Label(details, text="Password").pack(anchor="w")
        password_row = ttk.Frame(details)
        password_row.pack(fill="x", pady=(5, 18))
        self.password_entry = ttk.Entry(password_row, show="*")
        self.password_entry.pack(side="left", fill="x", expand=True)
        ttk.Button(password_row, text="Show", command=self.toggle_password).pack(side="left", padx=(8, 0))
        ttk.Button(password_row, text="Copy", command=self.copy_password).pack(side="left", padx=(8, 0))

        ttk.Separator(details).pack(fill="x", pady=(0, 18))
        ttk.Label(details, text="Add a login", font=("Segoe UI", 11, "bold")).pack(anchor="w")
        self.new_username = ttk.Entry(details)
        self.new_username.pack(fill="x", pady=(10, 6))
        self.new_password = ttk.Entry(details, show="*")
        self.new_password.pack(fill="x", pady=(0, 8))
        buttons = ttk.Frame(details)
        buttons.pack(fill="x")
        ttk.Button(buttons, text="Generate", command=self.generate_password).pack(side="left")
        ttk.Button(buttons, text="Save login", command=self.save_login).pack(side="right")
        ttk.Button(details, text="Delete selected login", command=self.delete_selected_login).pack(fill="x", side="bottom", pady=(18, 0))
        self.refresh_table()

    def refresh_table(self):
        for item in self.login_table.get_children():
            self.login_table.delete(item)
        for index, login in enumerate(self.logins):
            self.login_table.insert("", "end", iid=str(index), values=(login["username"],))

    def show_selected_login(self, event=None):
        selection = self.login_table.selection()
        if not selection:
            return
        login = self.logins[int(selection[0])]
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, login["username"])
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, login["password"])
        self.password_entry.configure(show="" if self.password_visible else "*")

    def toggle_password(self):
        self.password_visible = not self.password_visible
        self.password_entry.configure(show="" if self.password_visible else "*")

    def copy_password(self):
        password = self.password_entry.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)

    def generate_password(self):
        self.new_password.delete(0, "end")
        self.new_password.insert(0, main.generate_password())

    def save_login(self):
        username = self.new_username.get().strip()
        password = self.new_password.get()
        if not username or not password:
            messagebox.showwarning("Missing details", "Enter both a username and password.")
            return
        try:
            main.store_login_info(username, password, self.master_password)
            self.logins = main.get_all_logins(self.master_password)
        except (ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Could not save login", str(error))
            return
        self.new_username.delete(0, "end")
        self.new_password.delete(0, "end")
        self.refresh_table()

    def delete_selected_login(self):
        selection = self.login_table.selection()
        if not selection:
            return
        username = self.logins[int(selection[0])]["username"]
        if not messagebox.askyesno("Delete login", f"Delete the login for {username}?"):
            return
        try:
            main.delete_login_info(username, self.master_password)
            self.logins = main.get_all_logins(self.master_password)
        except (ValueError, KeyError, TypeError) as error:
            messagebox.showerror("Could not delete login", str(error))
            return
        self.refresh_table()
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")

    def change_master_password(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Change master password")
        dialog.transient(self.root)
        dialog.grab_set()
        form = ttk.Frame(dialog, padding=20)
        form.pack()
        ttk.Label(form, text="New master password").pack(anchor="w")
        new_password = ttk.Entry(form, show="*", width=32)
        new_password.pack(pady=(6, 14))
        ttk.Label(form, text="Confirm new password").pack(anchor="w")
        confirmation = ttk.Entry(form, show="*", width=32)
        confirmation.pack(pady=(6, 18))

        def submit():
            password = new_password.get()
            if not password or password != confirmation.get():
                messagebox.showwarning("Invalid password", "Enter matching, non-empty passwords.", parent=dialog)
                return
            try:
                main.change_master_password(self.master_password, password)
            except (ValueError, KeyError, TypeError) as error:
                messagebox.showerror("Could not change password", str(error), parent=dialog)
                return
            self.master_password = password
            dialog.destroy()

        ttk.Button(form, text="Change password", command=submit).pack(fill="x")


root = tk.Tk()
PasswordManagerGUI(root)
root.mainloop()

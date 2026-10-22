import sqlite3
import customtkinter as ctk


# ==========================================
# 1. Database Manager
# ==========================================
class DatabaseManager:

    def __init__(self, db_name="bank.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    account_type TEXT NOT NULL
                )
            """
            )
            conn.commit()

    def add_account(self, name: str, account_type: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO accounts (name, account_type) VALUES (?, ?)",
                (name, account_type),
            )
            conn.commit()

    def get_all_accounts(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, account_type FROM accounts")
            return cursor.fetchall()

    def update_account(self, acc_id: int, name: str, account_type: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE accounts SET name = ?, account_type = ? WHERE id = ?",
                (name, account_type, acc_id),
            )
            conn.commit()

    def delete_account(self, acc_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM accounts WHERE id = ?", (acc_id,))
            conn.commit()


# ==========================================
# 2. Main Application Window
# ==========================================
class BankApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.db = DatabaseManager()

        self.title("Bank Management System")
        self.geometry("600x480")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Tabview Setup
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.tab_add = self.tabview.add("Add Account")
        self.tab_view = self.tabview.add("View Accounts")

        self.setup_add_tab()
        self.setup_view_tab()

    # ------------------------------------------
    # Tab 1 Layout: Add Account
    # ------------------------------------------
    def setup_add_tab(self):
        self.tab_add.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            self.tab_add,
            text="Create New Account",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        title.pack(pady=20)

        self.name_entry = ctk.CTkEntry(
            self.tab_add, placeholder_text="Account Holder Name", width=300
        )
        self.name_entry.pack(pady=10)

        self.type_menu = ctk.CTkOptionMenu(
            self.tab_add, values=["Normal", "VIP"], width=300
        )
        self.type_menu.pack(pady=10)

        add_btn = ctk.CTkButton(
            self.tab_add,
            text="Save Account",
            command=self.handle_add_account,
            width=300,
        )
        add_btn.pack(pady=20)

        self.status_label = ctk.CTkLabel(self.tab_add, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

    def handle_add_account(self):
        name = self.name_entry.get().strip()
        acc_type = self.type_menu.get()

        if not name:
            self.status_label.configure(
                text="Please enter a name!", text_color="red"
            )
            return

        self.db.add_account(name, acc_type)
        self.status_label.configure(
            text=f"✓ Account created for {name}!", text_color="green"
        )
        self.name_entry.delete(0, ctk.END)

        # Automatically refresh table on Tab 2
        self.refresh_table()

    # ------------------------------------------
    # Tab 2 Layout: View & Manage Accounts
    # ------------------------------------------
    def setup_view_tab(self):
        self.tab_view.grid_columnconfigure(0, weight=1)
        self.tab_view.grid_rowconfigure(1, weight=1)

        # Header controls
        top_bar = ctk.CTkFrame(self.tab_view, fg_color="transparent")
        top_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        refresh_btn = ctk.CTkButton(
            top_bar, text="🔄 Refresh Table", command=self.refresh_table, width=120
        )
        refresh_btn.pack(side="right")

        # Scrollable container for rows
        self.scroll_frame = ctk.CTkScrollableFrame(self.tab_view)
        self.scroll_frame.grid(
            row=1, column=0, padx=10, pady=(0, 10), sticky="nsew"
        )
        self.scroll_frame.grid_columnconfigure(1, weight=1)

        # Load initial data
        self.refresh_table()

    def refresh_table(self):
        # Clear existing row widgets inside scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        accounts = self.db.get_all_accounts()

        # Render Table Header
        headers = ["ID", "Name", "Type", "Actions"]
        for col_idx, header in enumerate(headers):
            lbl = ctk.CTkLabel(
                self.scroll_frame,
                text=header,
                font=ctk.CTkFont(size=12, weight="bold"),
            )
            lbl.grid(row=0, column=col_idx, padx=10, pady=5, sticky="w")

        # Render Account Rows
        for row_idx, (acc_id, name, acc_type) in enumerate(
            accounts, start=1
        ):
            # ID
            ctk.CTkLabel(self.scroll_frame, text=str(acc_id)).grid(
                row=row_idx, column=0, padx=10, pady=5, sticky="w"
            )

            # Name
            ctk.CTkLabel(self.scroll_frame, text=name).grid(
                row=row_idx, column=1, padx=10, pady=5, sticky="w"
            )

            # Type
            ctk.CTkLabel(self.scroll_frame, text=acc_type).grid(
                row=row_idx, column=2, padx=10, pady=5, sticky="w"
            )

            # Action Buttons Frame
            btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            btn_frame.grid(row=row_idx, column=3, padx=10, pady=5)

            # Modify Button
            mod_btn = ctk.CTkButton(
                btn_frame,
                text="Edit",
                width=60,
                fg_color="#1f538d",
                command=lambda i=acc_id, n=name, t=acc_type: self.open_edit_dialog(
                    i, n, t
                ),
            )
            mod_btn.pack(side="left", padx=2)

            # Delete Button
            del_btn = ctk.CTkButton(
                btn_frame,
                text="Delete",
                width=60,
                fg_color="#942323",
                hover_color="#6e1a1a",
                command=lambda i=acc_id: self.handle_delete(i),
            )
            del_btn.pack(side="left", padx=2)

    # ------------------------------------------
    # Actions: Edit & Delete
    # ------------------------------------------
    def handle_delete(self, acc_id: int):
        self.db.delete_account(acc_id)
        self.refresh_table()

    def open_edit_dialog(self, acc_id: int, current_name: str, current_type: str):
        # Create a pop-up window (CTkToplevel)
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Edit Account #{acc_id}")
        dialog.geometry("350x250")
        dialog.grab_set()  # Focus pop-up window

        dialog.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            dialog,
            text=f"Modify Account #{acc_id}",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        title.pack(pady=15)

        entry_name = ctk.CTkEntry(dialog, width=250)
        entry_name.insert(0, current_name)
        entry_name.pack(pady=10)

        type_menu = ctk.CTkOptionMenu(
            dialog, values=["Normal", "VIP"], width=250
        )
        type_menu.set(current_type)
        type_menu.pack(pady=10)

        def save_changes():
            new_name = entry_name.get().strip()
            new_type = type_menu.get()
            if new_name:
                self.db.update_account(acc_id, new_name, new_type)
                self.refresh_table()
                dialog.destroy()

        save_btn = ctk.CTkButton(dialog, text="Save Changes", command=save_changes)
        save_btn.pack(pady=15)


if __name__ == "__main__":
    app = BankApp()
    app.mainloop()
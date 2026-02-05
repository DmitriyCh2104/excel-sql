import os
import shutil
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime

class MiniApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pro File & Data Utility")
        self.root.geometry("500x450")

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(expand=1, fill="both")

        # --- Tab 1: File Manager ---
        self.file_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.file_tab, text="File Cleanup")
        
        tk.Label(self.file_tab, text="Select Directory:", font=('Arial', 10, 'bold')).pack(pady=5)
        self.dir_path = tk.StringVar()
        tk.Entry(self.file_tab, textvariable=self.dir_path, width=50).pack()
        tk.Button(self.file_tab, text="Browse Folder", command=self.browse_dir).pack(pady=5)

        tk.Label(self.file_tab, text="Date Threshold (YYYY-MM-DD):").pack(pady=5)
        self.date_entry = tk.Entry(self.file_tab)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack()

        self.action = tk.StringVar(value="move")
        tk.Radiobutton(self.file_tab, text="Move to 'Archived'", variable=self.action, value="move").pack()
        tk.Radiobutton(self.file_tab, text="Delete Permanently", variable=self.action, value="delete").pack()

        tk.Button(self.file_tab, text="Run Cleanup", bg="#ff9999", command=self.run_cleanup).pack(pady=20)

        # --- Tab 2: Converter ---
        self.conv_tab = ttk.Frame(self.tabs)
        self.tabs.add(self.conv_tab, text="Excel <-> SQL")

        tk.Label(self.conv_tab, text="Data Conversion Tools", font=('Arial', 10, 'bold')).pack(pady=20)
        
        tk.Button(self.conv_tab, text="✨ Excel to SQL Script", width=25, height=2, 
                  command=self.excel_to_sql, bg="#e1f5fe").pack(pady=10)
        
        tk.Button(self.conv_tab, text="📊 SQL to Excel (CSV-based)", width=25, height=2, 
                  command=self.sql_to_excel, bg="#e1f5fe").pack(pady=10)

    # --- Logic for File Cleanup ---
    def browse_dir(self):
        path = filedialog.askdirectory()
        if path: self.dir_path.set(path)

    def run_cleanup(self):
        path = self.dir_path.get()
        if not path: return
        
        try:
            threshold_date = datetime.strptime(self.date_entry.get(), "%Y-%m-%d").timestamp()
        except ValueError:
            messagebox.showerror("Error", "Use YYYY-MM-DD format!")
            return

        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        count = 0

        for f in files:
            full_path = os.path.join(path, f)
            if os.path.getmtime(full_path) > threshold_date:
                if self.action.get() == "delete":
                    os.remove(full_path)
                else:
                    dest = os.path.join(path, "Archived")
                    os.makedirs(dest, exist_ok=True)
                    shutil.move(full_path, os.path.join(dest, f))
                count += 1
        
        messagebox.showinfo("Done", f"Success! {count} files processed.")

    # --- Logic for Conversion ---
    def excel_to_sql(self):
        # 1. Select Source
        file_path = filedialog.askopenfilename(title="Select Excel File", 
                                              filetypes=[("Excel files", "*.xlsx *.xls")])
        if not file_path: return

        # 2. Select Destination
        save_path = filedialog.asksaveasfilename(defaultextension=".sql",
                                                initialfile="output.sql",
                                                filetypes=[("SQL Script", "*.sql")])
        if not save_path: return

        try:
            df = pd.read_excel(file_path)
            table_name = os.path.basename(file_path).rsplit('.', 1)[0].replace(" ", "_")
            
            with open(save_path, 'w', encoding='utf-8') as f:
                for _, row in df.iterrows():
                    columns = ", ".join([f"`{col}`" for col in df.columns])
                    values = []
                    for val in row:
                        if pd.isna(val):
                            values.append("NULL")
                        elif isinstance(val, (int, float)):
                            values.append(str(val))
                        else:
                            # Escape single quotes for SQL safety
                            safe_val = str(val).replace("'", "''")
                            values.append(f"'{safe_val}'")
                    
                    f.write(f"INSERT INTO `{table_name}` ({columns}) VALUES ({', '.join(values)});\n")
            
            messagebox.showinfo("Success", f"SQL script saved to:\n{save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to convert: {str(e)}")

    def sql_to_excel(self):
        messagebox.showinfo("Info", "Note: This works best for simple SQL dumps. For complex DBs, connect via Python's sqlite3.")
        file_path = filedialog.askopenfilename(filetypes=[("SQL files", "*.sql")])
        if not file_path: return
        
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                filetypes=[("Excel File", "*.xlsx")])
        if save_path:
            # Placeholder for complex logic, but you can use regex or simple line parsing here
            messagebox.showwarning("Incomplete", "SQL parsing requires a specific DB dialect. Check documentation for your SQL flavor.")

if __name__ == "__main__":
    root = tk.Tk()
    app = MiniApp(root)
    root.mainloop()

# drl_config_window.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from drl_config import DRLConfiguration

class DRLConfigWindow:
    def __init__(self, parent):
        self.drl_config = DRLConfiguration()
        self.window = tk.Toplevel(parent)
        self.window.title("DRL Configuration")
        self.window.geometry("800x600")
        
        # Create main frame
        main_frame = ttk.Frame(self.window, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Protocol List Frame (Left Side)
        list_frame = ttk.LabelFrame(main_frame, text="Protocols", padding="5")
        list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # Protocol listbox with scrollbar
        self.protocol_list = tk.Listbox(list_frame, width=30, height=20)
        self.protocol_list.pack(side=tk.LEFT, fill=tk.Y)
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.protocol_list.yview)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.protocol_list.config(yscrollcommand=list_scrollbar.set)
        self.protocol_list.bind('<<ListboxSelect>>', self.on_protocol_select)
        
        # Protocol Control Buttons
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Add", command=self.add_protocol).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self.delete_protocol).pack(side=tk.LEFT, padx=2)
        
        # Configuration Frame (Right Side)
        config_frame = ttk.LabelFrame(main_frame, text="Protocol Configuration", padding="5")
        config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Protocol Name
        ttk.Label(config_frame, text="Protocol Name:").pack(anchor=tk.W, pady=2)
        self.protocol_name = ttk.Entry(config_frame)
        self.protocol_name.pack(fill=tk.X, pady=2)
        
        # Protocol Match Patterns
        ttk.Label(config_frame, text="Match Patterns (comma separated):").pack(anchor=tk.W, pady=2)
        self.match_patterns = ttk.Entry(config_frame)
        self.match_patterns.pack(fill=tk.X, pady=2)
        
        # Adult DRL Values
        adult_frame = ttk.LabelFrame(config_frame, text="Adult DRL Values", padding="5")
        adult_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(adult_frame, text="DLP:").grid(row=0, column=0, padx=5)
        self.adult_dlp = ttk.Entry(adult_frame, width=10)
        self.adult_dlp.grid(row=0, column=1, padx=5)
        
        ttk.Label(adult_frame, text="CTDIvol:").grid(row=0, column=2, padx=5)
        self.adult_ctdi = ttk.Entry(adult_frame, width=10)
        self.adult_ctdi.grid(row=0, column=3, padx=5)
        
        # Children DRL Values
        child_frame = ttk.LabelFrame(config_frame, text="Children DRL Values", padding="5")
        child_frame.pack(fill=tk.X, pady=5)
        
        age_ranges = ["0-1", "1-5", "5-10", "10-15"]
        self.child_entries = {}
        
        for i, age_range in enumerate(age_ranges):
            ttk.Label(child_frame, text=f"Age {age_range}:").grid(row=i, column=0, padx=5, pady=2)
            
            ttk.Label(child_frame, text="DLP:").grid(row=i, column=1, padx=5)
            dlp_entry = ttk.Entry(child_frame, width=10)
            dlp_entry.grid(row=i, column=2, padx=5)
            
            ttk.Label(child_frame, text="CTDIvol:").grid(row=i, column=3, padx=5)
            ctdi_entry = ttk.Entry(child_frame, width=10)
            ctdi_entry.grid(row=i, column=4, padx=5)
            
            self.child_entries[age_range] = {"DLP": dlp_entry, "CTDIvol": ctdi_entry}
        
        # Bottom Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Save Changes", command=self.save_changes).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Import from Excel", command=self.import_excel).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export to Excel", command=self.export_excel).pack(side=tk.LEFT, padx=5)
        
        # Load existing protocols
        self.load_protocols()
            
    def load_protocols(self):
        self.protocol_list.delete(0, tk.END)
        for protocol in self.drl_config.get_all_protocols():
            self.protocol_list.insert(tk.END, protocol)
            
    def save_changes(self):
        protocol_name = self.protocol_name.get().strip()
        if not protocol_name:
            messagebox.showerror("Error", "Protocol name is required")
            return
            
        try:
            data = {
                'protocol_match': [x.strip() for x in self.match_patterns.get().split(',')],
                'adult': {
                    'DLP': float(self.adult_dlp.get()),
                    'CTDIvol': float(self.adult_ctdi.get())
                },
                'child': {}
            }
            
            for age_range, entries in self.child_entries.items():
                if entries['DLP'].get() and entries['CTDIvol'].get():
                    data['child'][age_range] = {
                        'DLP': float(entries['DLP'].get()),
                        'CTDIvol': float(entries['CTDIvol'].get())
                    }
                    
            self.drl_config.add_protocol(protocol_name, data)
            self.load_protocols()
            messagebox.showinfo("Success", "Protocol saved successfully")
            
        except ValueError as e:
            messagebox.showerror("Error", "Invalid numeric value entered")
            
    def import_excel(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            success, message = self.drl_config.import_from_excel(file_path)
            if success:
                self.load_protocols()
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
                
    def export_excel(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
        if file_path:
            success, message = self.drl_config.export_to_excel(file_path)
            if success:
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
                
    def add_protocol(self):
        self.clear_form()
        
    def delete_protocol(self):
        selection = self.protocol_list.curselection()
        if selection:
            protocol = self.protocol_list.get(selection[0])
            if messagebox.askyesno("Confirm Delete", f"Delete protocol {protocol}?"):
                self.drl_config.delete_protocol(protocol)
                self.load_protocols()
                self.clear_form()
                
    def clear_form(self):
        self.protocol_name.delete(0, tk.END)
        self.match_patterns.delete(0, tk.END)
        self.adult_dlp.delete(0, tk.END)
        self.adult_ctdi.delete(0, tk.END)
        for entries in self.child_entries.values():
            entries['DLP'].delete(0, tk.END)
            entries['CTDIvol'].delete(0, tk.END)
            
    def on_protocol_select(self, event):
        selection = self.protocol_list.curselection()
        if selection:
            protocol = self.protocol_list.get(selection[0])
            data = self.drl_config.get_protocol(protocol)
            if data:
                self.clear_form()
                self.protocol_name.insert(0, protocol)
                self.match_patterns.insert(0, ','.join(data['protocol_match']))
                self.adult_dlp.insert(0, str(data['adult']['DLP']))
                self.adult_ctdi.insert(0, str(data['adult']['CTDIvol']))
                
                for age_range, values in data['child'].items():
                    if age_range in self.child_entries:
                        self.child_entries[age_range]['DLP'].insert(0, str(values['DLP']))
                        self.child_entries[age_range]['CTDIvol'].insert(0, str(values['CTDIvol']))
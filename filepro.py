import os
import shutil
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import tkinter.font as font
import ctypes
import threading
import sys

# Check Python version
if sys.version_info < (3, 6):
    raise Exception("This script requires Python 3.6 or higher")

# Constants
IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".yaml"]

if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    os.chdir(exe_dir)

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    pass

class FolderProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Folder Processor")
        self.root.configure(bg='#F0F0F0')  # Light grey background

        # Use a modern, clean font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family='Roboto', size=12)

        self.selected_directory = ""
        self.new_folder_name = "Chapter 1"
        self.frame = tk.Frame(root, bg='#F0F0F0')  # Light grey background
        self.frame.pack(padx=10, pady=10)

        self.directory_label = tk.Label(self.frame, text="Select Directory:", bg="#F0F0F0", fg="black")
        self.directory_label.grid(row=0, column=0)

        self.directory_var = tk.StringVar()
        self.directory_entry = tk.Entry(self.frame, textvariable=self.directory_var, width=50)
        self.directory_entry.grid(row=0, column=1)

        self.browse_button = tk.Button(self.frame, text="Browse", command=self.browse_directory, bg="skyblue", fg="black")
        self.browse_button.grid(row=0, column=2)

        self.folder_name_label = tk.Label(self.frame, text="New Folder Name:", bg="#F0F0F0", fg="black")
        self.folder_name_label.grid(row=1, column=0)

        self.folder_name_entry = tk.Entry(self.frame, textvariable=tk.StringVar(value=self.new_folder_name), width=50)
        self.folder_name_entry.grid(row=1, column=1)

        self.update_button = tk.Button(self.frame, text="Update Folder Name", command=self.update_folder_name, bg="green", fg="black")
        self.update_button.grid(row=1, column=2)

        self.process_button = tk.Button(self.frame, text="Process Folders", command=self.process_folders, bg="orange", fg="black")
        self.process_button.grid(row=2, columnspan=3, pady=10)

        self.progress_bar = ttk.Progressbar(self.frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(row=3, columnspan=3, pady=10)

        self.cancel_button = tk.Button(self.frame, text="Cancel", command=self.cancel_processing, bg="red", fg="black")
        self.cancel_button.grid(row=4, columnspan=3, pady=10)
        self.cancel_button.config(state=tk.DISABLED)
        self.process_thread = None

        # Add checkboxes for extensions
        self.extensions_label = tk.Label(self.frame, text="Extensions:", bg="#F0F0F0", fg="black")
        self.extensions_label.grid(row=5, column=0)

        self.extension_vars = {ext: tk.BooleanVar(value=True) for ext in IMAGE_EXTENSIONS}
        for i, ext in enumerate(IMAGE_EXTENSIONS):
            cb = tk.Checkbutton(self.frame, text=ext, variable=self.extension_vars[ext], bg="#F0F0F0", fg="black", selectcolor="white")
            cb.grid(row=5+i, column=1)

        self.add_extension_entry = tk.Entry(self.frame, bg="#F0F0F0", fg="black")
        self.add_extension_entry.insert(0, "Add extension here")
        self.add_extension_entry.grid(row=6+len(IMAGE_EXTENSIONS), column=1)

        self.add_extension_button = tk.Button(self.frame, text="Add Extension", command=self.add_extension, bg="green", fg="black")
        self.add_extension_button.grid(row=6+len(IMAGE_EXTENSIONS), column=2)

        self.remove_extension_button = tk.Button(self.frame, text="Remove Selected Extension", command=self.remove_extension, bg="red", fg="black")
        self.remove_extension_button.grid(row=7+len(IMAGE_EXTENSIONS), column=2)

    def browse_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.selected_directory = directory_path
            self.directory_var.set(directory_path)

    def update_folder_name(self):
        self.new_folder_name = self.folder_name_entry.get()

    def process_folders(self):
        if not self.selected_directory:
            messagebox.showerror("Error", "Please select a directory")
            return
        self.process_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.process_thread = threading.Thread(target=self.process_folders_thread)
        self.process_thread.start()

    def process_folders_thread(self):
        global IMAGE_EXTENSIONS
        IMAGE_EXTENSIONS = [ext for ext, var in self.extension_vars.items() if var.get()]
        try:
            directory_contents = os.listdir(self.selected_directory)
            num_folders = sum(1 for item in directory_contents if os.path.isdir(os.path.join(self.selected_directory, item)))
            self.progress_bar["maximum"] = num_folders
            for item in directory_contents:
                item_path = os.path.join(self.selected_directory, item)
                if not os.path.isdir(item_path):
                    continue
                files = os.listdir(item_path)
                folder = os.path.join(item_path, self.new_folder_name)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                self.process_files_in_folder(files, folder, item_path, item)
                self.progress_bar["value"] += 1
                self.root.update()
            self.process_button.config(state=tk.NORMAL)
            self.browse_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during processing: {str(e)}")

    def process_files_in_folder(self, files, folder, item_path, item):
        try:
            for file in files:
                if os.path.splitext(file)[1] in IMAGE_EXTENSIONS:
                    file_path = os.path.join(item_path, file)
                    shutil.copy(file_path, os.path.join(folder, "cover.jpg"))
                    break
            else:
                raise ValueError(f"No image files found in folder {item}")
        except Exception as e:
            messagebox.showerror("Error", f"Error copying cover image: {str(e)}")
        for file in files:
            if os.path.splitext(file)[1] in IMAGE_EXTENSIONS:
                file_path = os.path.join(item_path, file)
                shutil.move(file_path, folder)

    def add_extension(self):
        new_extension = self.add_extension_entry.get()
        if new_extension:
            self.extension_vars[new_extension] = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self.frame, text=new_extension, variable=self.extension_vars[new_extension], bg="#F0F0F0", fg="black", selectcolor="blue")
            cb.grid(row=5+len(self.extension_vars)-1, column=1)
            self.add_extension_entry.delete(0, tk.END)

    def remove_extension(self):
        for ext, var in list(self.extension_vars.items()):
            if var.get():
                del self.extension_vars[ext]
                for widget in self.frame.grid_slaves():
                    if widget.cget("text") == ext:
                        widget.destroy()

    def cancel_processing(self):
        if self.process_thread and self.process_thread.is_alive():
            self.process_thread.join()
            messagebox.showinfo("Info", "Processing canceled")

if __name__ == "__main__":
    root = tk.Tk()
    app = FolderProcessorApp(root)
    root.mainloop()

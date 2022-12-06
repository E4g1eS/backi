import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import os.path
import os
import shutil
import time

class Backuper:
    __root : tk.Tk
    __source_path_label : tk.Label
    __source_path : str
    __destination_path_label : tk.Label
    __destination_path : str

    __backup_progress_label : tk.Label
    __backup_progress_bar : ttk.Progressbar

    __warned : bool
    __failed : bool

    def __init__(self):
        self.__source_path = ""
        self.__destination_path = ""
        self.__warned = False
        self.__failed = False

        self.__root = tk.Tk()
        self.__root.title("Backuper")
        self.__root.geometry("400x200")
        self.__init_ui()
        self.__root.mainloop()

    def __init_ui(self) -> None:
   
        # Source:

        source_frame = tk.Frame(self.__root)
        source_frame.pack()

        source_button = tk.Button(source_frame, text="Set source", command=lambda : self.__set_path("source"))
        source_button.pack(side="left")

        self.__source_path_label = tk.Label(source_frame, text="Set source!")
        self.__source_path_label.pack(side="right")

        # Destination:

        destination_frame = tk.Frame(self.__root)
        destination_frame.pack()

        destination_button = tk.Button(destination_frame, text="Set destination", command=lambda : self.__set_path("destination"))
        destination_button.pack(side="left")

        self.__destination_path_label = tk.Label(destination_frame, text="Set destination!")
        self.__destination_path_label.pack(side="right")

        # Run:

        backup_frame = tk.Frame(self.__root)
        backup_frame.pack()

        backup_button = tk.Button(backup_frame, text="Run backup", command=self.__start_backup)
        backup_button.pack()

        backup_progress_frame = tk.Frame(backup_frame)
        backup_progress_frame.pack()

        self.__backup_progress_label = tk.Label(backup_progress_frame, text="0/0")
        self.__backup_progress_label.pack(side="left")

        self.__backup_progress_bar = ttk.Progressbar(backup_progress_frame)
        self.__backup_progress_bar.pack(side="right")

    def __set_path(self, which : str) -> None:
        directory = filedialog.askdirectory(mustexist=True)

        if directory == "":
            return

        if which == "source":
            self.__source_path = directory
            self.__source_path_label.configure(text=directory)

        elif which == "destination":
            self.__destination_path = directory
            self.__destination_path_label.configure(text=directory)

        else: raise SyntaxError("Wrong 'which' argument!")

    def __start_backup(self):
        self.__warned = False
        self.__failed = False

        if (os.path.isdir(self.__source_path)) != True:
            messagebox.showerror("Error", "Source directory does not exist!")
            return

        if (os.path.isdir(self.__destination_path)) != True:
            messagebox.showerror("Error", "Destination directory does not exist!")
            return

        # Counting:

        total_file_count = 0
        for dir_root, dirs, files in os.walk(self.__source_path):
            for file in files:
                total_file_count += 1

        # Processing:

        file_being_done = 0
        os.chdir(self.__source_path)
        for dir_root, dirs, files in os.walk("."):

            dir_root = dir_root[1:]
            dir_root = dir_root.replace("\\", "/")
            dir_root = dir_root + "/"

            for file in files:

                file_being_done += 1
                self.__backup_progress_label.configure(text=(str(file_being_done) + "/" + str(total_file_count)))
                self.__backup_progress_bar["value"] = (file_being_done / total_file_count) * 100.0
                self.__root.update()

                source_file_path = self.__source_path + dir_root + file
                destination_file_path = self.__destination_path + dir_root + file

                print("\nCopy '" + source_file_path + "' -----> " + destination_file_path + "'.", end=" ")

                if not os.path.isdir(self.__destination_path + dir_root):
                    os.makedirs(self.__destination_path + dir_root)

                if os.path.isfile(destination_file_path):
                    source_time = os.path.getmtime(source_file_path)
                    destination_time = os.path.getmtime(destination_file_path)

                    if source_time == destination_time: # Same file, no need to copy
                        print("Not copying, file modification dates are the same.", end=" ")
                        continue

                    elif destination_time > source_time:
                        if not self.__warned:
                            messagebox.showwarning("Warning", "Destination directory contains newer files than source directory!")
                            self.__warned = True
                        print("Not copying, file in the destinaton directory is newer!", end=" ")
                        continue

                try:
                    shutil.copy2(source_file_path, destination_file_path)
                except:
                    print("Could not copy file.", end=" ")
                    self.__failed = True
                else:
                    print("Copied.", end=" ")

        self.__backup_progress_bar["value"] = 0.0
        print("######################################")

        if self.__failed:
            self.__backup_progress_label.configure(text="Done with errors!")
            print("DONE WITH ERRORS")
        else:
            self.__backup_progress_label.configure(text="All done!")
            print("DONE")

        print('\a')


if __name__ == "__main__":
    backuper = Backuper()

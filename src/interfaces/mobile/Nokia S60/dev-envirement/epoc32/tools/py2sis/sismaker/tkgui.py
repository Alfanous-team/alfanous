# Copyright (c) 2005 Nokia Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import Tkinter as tk
import tkFileDialog, tkMessageBox

import sismaker.utils as utils

class SISMakerApp(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.view_main()

    def clear(self):
        for c in self.slaves():
            c.destroy()
        self.pack(padx=12,pady=12)

    def view_main(self):
        self.clear()
        file_button = tk.Button(
            self, text="Script -> SIS",
            command=self.view_wrap_file, width=15).pack(
                side="top", padx=5, pady=5)
        dir_button = tk.Button(
            self, text="Dir -> SIS",
            command=self.view_wrap_dir, width=15).pack(
                side="top", padx=5, pady=5)

    def view_wrap_dir(self):
        self.clear()
        self.select_widget("Choose dir", self.choose_dir)
        self.common_widgets()

    def view_wrap_file(self):
        self.clear()
        self.select_widget("Choose file", self.choose_file)
        self.common_widgets()

    def select_widget(self, label, callback):
        self.selected_src = tk.StringVar()
        dir_label = tk.Label(
            self, text=label).grid(
            row=0, padx=2, pady=2, sticky=tk.W)
        dir_button = tk.Button(
            self, text="...", command=callback).grid(
            row=0, column=2, padx=2, pady=2)
        dir_entry = tk.Entry(
            self, textvariable=self.selected_src, width=20).grid(
            row=0, column=1, padx=2, pady=2, sticky=tk.W)        

    def common_widgets(self):
        self.selected_uid = tk.StringVar()
        self.selected_uid.set("0x00000001")
        uid_label = tk.Label(
            self, text="UID").grid(
            row=1, column=0, padx=2, pady=2, sticky=tk.W)
        uid_entry = tk.Entry(
            self, textvariable=self.selected_uid, width=20).grid(
            row=1, column=1, padx=2, pady=2, sticky=tk.W)

        self.selected_appname = tk.StringVar()
        app_label = tk.Label(
            self, text="App. Name").grid(
            row=2, column=0, padx=2, pady=2, sticky=tk.W)
        app_entry = tk.Entry(
            self, textvariable=self.selected_appname, width=20).grid(
            row=2, column=1, padx=2, pady=2, sticky=tk.W)

        self.selected_sisname = tk.StringVar()
        sis_label = tk.Label(
            self, text="SIS File").grid(
            row=3, column=0, padx=2, pady=2, sticky=tk.W)        
        sis_entry = tk.Entry(
            self, textvariable=self.selected_sisname, width=20).grid(
            row=3, column=1, padx=2, pady=2, sticky=tk.W)
        sis_button = tk.Button(
            self, text="...", command=self.choose_sis).grid(
            row=3, column=2, padx=2, pady=2)
        

        make_button = tk.Button(
            self, text="Make SIS", command=self.makesis).grid(
            row=4, columnspan=2, padx=2, pady=2, sticky=tk.E)

    def makesis(self):
        import sismaker
        sisname = self.selected_sisname.get()
        uid = self.selected_uid.get()
        appname = self.selected_appname.get()
        if not sisname:
            self.error("SIS file not specified", "Please select the location where to save the resulting SIS file")
            return
        s = sismaker.SISMaker()
        try:
            output = s.make_sis(self.selected_src.get(), sisname, uid=uid, appname=appname)
        except Exception, msg:
            self.error("Make SIS failed!", msg)
        else:
            self.info("Finished", "SIS file created succesfully")

    def error(self, title, msg):
        tkMessageBox.showerror(title=title, message=msg, parent=self)

    def info(self, title, msg):
        tkMessageBox.showinfo(title=title, message=msg, parent=self)
    
    def choose_dir(self):
        dir = tkFileDialog.askdirectory(parent=self, title="Choose a directory", initialdir="C:\\")
        self.process_src(dir)

    def choose_file(self):
        file = tkFileDialog.askopenfilename(parent=self, title="Choose a script", initialdir="C:\\")
        self.process_src(file)

    def choose_sis(self):
        file = tkFileDialog.asksaveasfilename(parent=self, title="Choose a path for resulting SIS file", initialdir="C:\\")
        self.selected_sisname.set(file)

    def process_src(self, src):
        if not src:
            return
        try:
            main = utils.find_main_script(src)
        except ValueError, msg:
            self.error("Invalid Directory", msg)
            return
        try:
            script = open(main).read()
        except IOError, msg:
            self.error("I/O Error", "Could not read default.py: %s" % msg)
        self.selected_src.set(src)
        uid = utils.find_uid(script)
        if uid is not None:
            self.selected_uid.set(uid)
        if not self.selected_appname.get():
            self.selected_appname.set(utils.get_appname(src).title())


def main():
    root = tk.Tk()
    root.title("SIS Maker")
    app = SISMakerApp(root)
    app.mainloop()

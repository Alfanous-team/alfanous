# Copyright (c) 2009 Nokia Corporation
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

import os
import sys
import subprocess
import webbrowser
import tkFileDialog
import tkFont
import tkMessageBox
from tkSimpleDialog import *
from Tkinter import *

color = "#%02x%02x%02x" % (192, 192, 192)
expand_tip = "Show advanced options"
hide_tip = "Hide advanced options"
compatibility_tip = "Select PyS60 module over Python core module when " +\
                    "conflicting module names exist.For example, " +\
                    "the calendar module."
create_tip = "Enter application source and then click, to create SIS in " +\
             "the same directory as the script."
additional_options_tip = "View the options available in ensymble"
file_radiobutton_tip = "Select this to browse for a single script file"
dir_radiobutton_tip = "Select this to browse for a directory"
help_tip = "View detailed description of packager elements"
heap_size_tip = "Application heap size, min. and/or max. ('4k,1M' by default)"
profile_tip = "Select the environment in which the packaged Python script " +\
              "is run. 'S60UI' by default."
clear_all_tip = "Restore default values."
install_tip = "Install the SIS to the phone. The phone should " +\
              "be connected to PC through Nokia PCSuite."
open_folder_tip = "Open the folder containing the SIS."
byte_code_tip = "Package as : Bytecode(Module import is faster, source " +\
                "code not visible in traceback) or Source code(Module " +\
                "import is slower, source code visible in traceback). " +\
                "Bytecode by default."
ignore_missing_deps_tip = "Ignore missing dependencies and continue with " +\
                          "sis generation"


class ToolTip:
    """Defining a class ToolTip used to display tool tips. Basically it
       binds the events to widgets based on mouse pointer entering or
       leaving the widget."""

    def __init__(self, master, text):
        self.master = master
        self.tooltip_widget = None
        self.text = text
        self.widget_id = None
        # Defining bindings for these events
        self.master.bind("<Enter>", self.enter_widget)
        self.master.bind("<Leave>", self.leave_widget)
        self.master.bind("<ButtonPress>", self.leave_widget)

    def enter_widget(self, event=None):
        self.clear_other_tips()
        self.widget_id = self.master.after(500, self.show_tooltip)

    def leave_widget(self, event=None):
        self.clear_other_tips()
        current_tooltip = self.tooltip_widget
        self.tooltip_widget = None
        if current_tooltip:
            current_tooltip.destroy()

    def clear_other_tips(self):
        # Clear the other tool tips if they are not cleared
        alarm_id = self.widget_id
        self.widget_id = None
        if alarm_id:
            self.master.after_cancel(alarm_id)

    def show_tooltip(self):
        # Obtain the coordinates and display the required tooltip
        if not self.tooltip_widget:
            self.tooltip_widget = Toplevel(self.master)
            current_tooltip = self.tooltip_widget
            current_tooltip.overrideredirect(1)
            Label(self.tooltip_widget, anchor='center', bd=1, fg="black",
                  bg="white", justify='left', relief='solid',
                  text=self.text, wraplength=200).pack()
            current_tooltip.update_idletasks()
            x, y = self.get_coordinates()
            current_tooltip.geometry("+%d+%d" % (x, y))

    def get_coordinates(self):
        # Get the required coordinates for displaying tooltip
        current_tooltip = self.tooltip_widget
        widget_width = current_tooltip.winfo_reqwidth()
        widget_height = current_tooltip.winfo_reqheight()
        screen_width = current_tooltip.winfo_screenwidth()
        screen_height = current_tooltip.winfo_screenheight()

        y = self.master.winfo_rooty() + self.master.winfo_height()
        if y + widget_height > screen_height:
            y = self.master.winfo_rooty() - widget_height

        x = self.master.winfo_rootx() + self.master.winfo_width() - 40
        if x + widget_width > screen_width:
            x = self.master.winfo_rootx() - widget_width + 40
        return x, y


class EnsymbleOutputDialog(Dialog):

    '''Class to display dialogs.
       This inherits the tkSimpleDialog.Dialog class.
    '''

    def __init__(self,parent, ensymble_output, ret, sis_path=None,
                 sis_filename=None):
        '''Initialize a dialog.
           Override the init() of the base class so as to enable display of
           titlebar icon and call ensymble output specific dialogs.
        '''
        Toplevel.__init__(self, parent)
        Toplevel.iconbitmap(self, 'pycon.ico')
        # If the master is not viewable, don't make the child transient,
        # or else it would be opened withdrawn.
        if parent.winfo_viewable():
            self.transient(parent)

        self.normalfont = tkFont.Font(family="MS Sans Serif", size=10,
                                 weight="normal")
        self.specialfont = tkFont.Font(family="MS Sans Serif", size=10,
                                 weight="bold")
        self.ensymble_output = ensymble_output
        self.sis_path = sis_path
        self.sis_filename = sis_filename
        self.parent = parent
        self.initial_focus = None

        if ret != 0:
            self.failuredialog()
        else:
            self.successdialog()

        if not self.initial_focus:
            self.initial_focus = self

        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx()+250,
                                      parent.winfo_rooty()+200))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def failuredialog(self):
        # Dialog displayed when generation of sis fails
        box = Frame(self)
        Label(box, anchor='center', fg='red', font=self.specialfont,
              text="Failure!").pack()
        Label(box, anchor='center', justify='left', font=self.normalfont,
              text=self.ensymble_output).pack()
        w = Button(box, text="Ok", font=self.specialfont, borderwidth=3,
                   width=10, command=self.ok)
        w.pack(padx=5, pady=5, anchor=CENTER)
        box.pack()

    def successdialog(self):
        # Dialog displayed when sis generation successful
        box = Frame(self)
        Label(box, anchor='center', fg='blue', font=self.specialfont,
              text="Success!").pack()
        Label(box, anchor='center', justify='left', font=self.normalfont,
              text=self.ensymble_output).pack()
        button_frame = Frame(box)
        install_button = Button(button_frame, text="Install",
            font=self.specialfont, borderwidth=3, width=10,
            command=self.install)
        ToolTip(install_button, install_tip)
        install_button.pack(side=LEFT, padx=50, pady=5)
        open_folder_button = Button(button_frame, text="Open Folder",
            font=self.specialfont, borderwidth=3, width=10,
            command=self.folder)
        ToolTip(open_folder_button, open_folder_tip)
        open_folder_button.pack(side=LEFT, pady=5)
        button_frame.pack()
        box.pack()

    def folder(self, event=None):
        # Call DOS explorer command to open the folder containing the sis file
        if sys.platform == 'win32':
            os.popen("explorer /select, " + self.sis_path + self.sis_filename)

    def install(self, event=None):
        # Invoke the Nokia PC Suite Software installer
        prev_dir = os.getcwd()
        os.chdir(self.sis_path)
        if sys.platform == 'win32':
            os.popen(self.sis_filename)
        os.chdir(prev_dir)


class GUI():
    """This class contains the GUI specification"""

    def __init__(self):

        self.root = Tk()
        self.root.config(bg=color)
        # Defining font style for our GUI
        self.normalfont = tkFont.Font(family="MS Sans Serif", size=10,
                                 weight="normal")
        self.specialfont = tkFont.Font(family="Helvetica", size=10,
                                 weight="bold")
        # Defining the variables used in the GUI
        self.state = 0
        self.initial_dir = ""
        self.display = StringVar()
        self.version = StringVar()
        self.uid = StringVar()
        self.passphrase = StringVar()
        self.filename = StringVar()
        self.additional_arguments = StringVar()
        self.heap_min = StringVar()
        self.heap_max = StringVar()
        self.public_key = StringVar()
        self.private_key = StringVar()
        self.set_profile = IntVar()
        self.file_or_dir = IntVar()
        self.pys60_environment = IntVar()
        self.source_or_byte_code = IntVar()
        self.ignore_missing_deps = IntVar()
        self.img = PhotoImage(file='python_logo.gif')
        self.entryframe = Frame(self.root, bg=color)

        self.labelname = ["Application title", "Version", "UID", "Certificate",
                          "Private key", "Pass phrase", "Additional options"]
        self.entryname = [self.display, self.version, self.uid,
                          self.public_key, self.private_key, self.passphrase,
                          self.additional_arguments]

        # Associate callbacks to the variables to be traced
        for fields in self.entryname:
            fields.trace_variable('w', self.clear_button_callback)
        self.filename.trace_variable('w', self.create_button_callback)
        self.heap_min.trace_variable('w', self.clear_button_callback)
        self.heap_max.trace_variable('w', self.clear_button_callback)
        self.pys60_environment.trace_variable('w', self.clear_button_callback)
        self.set_profile.trace_variable('w', self.clear_button_callback)
        self.file_or_dir.trace_variable('w', self.file_or_dir_callback)
        self.source_or_byte_code.trace_variable('w',
            self.continue_warnings_callback)
        self.ignore_missing_deps.trace_variable('w',
            self.continue_warnings_callback)

        self.mandatory_frame = Frame(self.entryframe, bg=color)
        self.source_frame = Frame(self.mandatory_frame, borderwidth=1,
                                  relief=GROOVE, bg=color)
        Label(self.source_frame, bg=color, text="Application source:",
              font=self.specialfont).grid(column=0, sticky='w', padx=5)
        file_radiobutton = Radiobutton(self.source_frame, bg=color,
            text="Script file", value=0, variable=self.file_or_dir,
            font=self.normalfont, cursor="hand2")
        file_radiobutton.grid(row=1, sticky='w', padx=5)
        ToolTip(file_radiobutton, file_radiobutton_tip)
        dir_radiobutton = Radiobutton(self.source_frame, bg=color,
            text="Script directory", value=1, variable=self.file_or_dir,
            font=self.normalfont, cursor="hand2")
        dir_radiobutton.grid(row=1, column=0, columnspan=2, sticky='e')
        ToolTip(dir_radiobutton, dir_radiobutton_tip)
        Entry(self.source_frame, textvariable=self.filename, width=35,
              font=self.normalfont).grid(row=2, columnspan=2, pady=9,
              sticky='w', padx=7)
        self.browse_button = Button(self.source_frame, text="Browse",
                                    width=7, font=self.specialfont,
                                    borderwidth=3, relief=RAISED,
                                    command=self.browse_script).grid(row=3,
                                    columnspan=2, padx=8, pady=3)
        # Embed the image and "Python for S60" label in a separate frame
        self.image_frame = Frame(self.mandatory_frame, bg=color)
        pys60widget = Label(self.image_frame, bg=color, image=self.img)
        pys60widget.grid(row=0, column=2, rowspan=3, columnspan=3)
        Label(self.image_frame, text="Python for S60", bg=color,
              font=self.specialfont).grid(row=3, column=2)
        warnings_checkbutton = Checkbutton(self.mandatory_frame, bg=color,
            text="Continue with missing dependencies",
            variable=self.ignore_missing_deps, font=self.specialfont)
        ToolTip(warnings_checkbutton, ignore_missing_deps_tip)
        # The final frame contains buttons "Create", "Help" and
        # "More/Less"
        self.final_frame = Frame(self.entryframe, bg=color)
        self.create_button = Button(self.final_frame, text="Create", width=6,
                                    relief="raised", font=self.specialfont,
                                    borderwidth=3, command=self.create_sis,
                                    state=DISABLED)
        ToolTip(self.create_button, create_tip)
        self.create_button.grid(row=2, column=0)
        help_button = Button(self.final_frame, text="Help", relief="raised",
                             width=6, font=self.specialfont, borderwidth=3,
                             command=self.showhtml)
        help_button.grid(row=2, column=1, padx=25)
        self.expand_button = Button(self.final_frame, width=6,
            text="More ▼", font=self.specialfont, borderwidth=3,
            relief=RAISED, command=self.show_frame)
        ToolTip(self.expand_button, expand_tip)
        self.expand_button.grid(row=2, column=2, sticky='e', pady=6)
        ToolTip(help_button, help_tip)

        # Display the frames
        self.source_frame.grid(row=0, column=0, columnspan=2,
                                  pady=10, padx=5)
        self.image_frame.grid(row=0, column=2, rowspan=3, columnspan=3,
                         pady=10, padx=5)
        warnings_checkbutton.grid(row=1, column=0)
        self.mandatory_frame.grid()
        self.entryframe.grid(row=0, pady=2)
        self.final_frame.grid(pady=5, column=0, columnspan=2)

        # Launching a subprocess without a console window
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.startupinfo = startupinfo

    def show_frame(self):
        self.state = 1
        self.expand_button.configure(text="Less ▲",
                                     command=self.hide_frame)
        ToolTip(self.expand_button, hide_tip)
        # The optional frame contains the fields displayed when the
        # "More ▼" button is clicked
        self.optional_frame = Frame(self.entryframe, bg=color)
        i = 5
        for name, entry in zip(self.labelname, self.entryname):
            templabel = Label(self.optional_frame, bg=color, text=name,
                font=self.normalfont).grid(row=i, sticky=E, pady=5, ipadx=5)
            if name != "Pass phrase":
                tempentry = Entry(self.optional_frame, textvariable=entry,
                    font=self.normalfont).grid(row=i, column=1, pady=5)
            else:
                tempentry = Entry(self.optional_frame, textvariable=entry,
                    font=self.normalfont, show="*").grid(row=i,
                                                         column=1, pady=5)
            if name == "Certificate":
                Button(self.optional_frame, text="Browse", width=7,
                       font=self.specialfont, relief=RAISED, borderwidth=3,
                       command=self.browse_cert).grid(row=i,
                                                      column=2, pady=3)
            if name == "Additional options":
                options_button = Button(self.optional_frame, text="Options",
                                        width=7, font=self.specialfont,
                                        relief=RAISED, borderwidth=3,
                                        command=self.show_options)
                options_button.grid(row=i, column=2, pady=3)
                ToolTip(options_button, additional_options_tip)
            i = i + 1

        self.profile_and_heap_layout = Frame(self.optional_frame, bg=color)
        self.profile_frame = Frame(self.profile_and_heap_layout, bg=color,
                                   borderwidth=2, relief=GROOVE)
        self.profile_label = Label(self.profile_frame, bg=color,
                                   text="Profile", font=self.specialfont,
                                   padx=25)
        self.profile_label.grid(row=0, column=0)
        ToolTip(self.profile_label, profile_tip)
        Radiobutton(self.profile_frame, bg=color, text="S60UI",
                    variable=self.set_profile,
                    value=0, cursor="hand2", font=self.normalfont).grid(row=1,
                    column=0, sticky=W, ipadx=35)
        Radiobutton(self.profile_frame, bg=color, text="Console",
                    variable=self.set_profile,
                    value=1, cursor="hand2", font=self.normalfont).grid(row=2,
                    column=0, sticky=W, ipadx=35)
        self.heapsize_frame = Frame(self.profile_and_heap_layout, bg=color,
                                    borderwidth=2, relief=GROOVE)
        self.heap_label = Label(self.heapsize_frame, bg=color,
                                text="Heap Size", font=self.specialfont)
        self.heap_label.grid(row=0, column=1, ipady=2)
        ToolTip(self.heap_label, heap_size_tip)
        Label(self.heapsize_frame, bg=color, text="Min",
              font=self.normalfont).grid(row=1, column=0)
        Entry(self.heapsize_frame, textvariable=self.heap_min,
              width=6).grid(row=2, column=0, pady=4, padx=2)
        Label(self.heapsize_frame, bg=color, text="Max",
              font=self.normalfont).grid(row=1, column=2)
        Entry(self.heapsize_frame, textvariable=self.heap_max,
              width=6).grid(row=2, column=2, pady=4, padx=2)

        self.checkbutton_frame = Frame(self.optional_frame, bg=color)
        self.clear_all_button = Button(self.checkbutton_frame,
                                       text=" Reset ", width=7, relief=RAISED,
                                       font=self.specialfont, borderwidth=3,
                                       command=self.clear_all)
        self.clear_all_button.grid(row=0, column=0, padx=60)
        ToolTip(self.clear_all_button, clear_all_tip)
        self.check_state_and_configure()
        self.byte_and_source_frame = Frame(self.profile_and_heap_layout,
            bg=color, borderwidth=2, relief=GROOVE)
        self.byte_and_source_label = Label(self.byte_and_source_frame, bg=color,
            text="Package As :", font=self.specialfont)
        self.byte_and_source_label.grid(row=0, columnspan=2)
        ToolTip(self.byte_and_source_label, byte_code_tip)
        Radiobutton(self.byte_and_source_frame, bg=color, text="Bytecode",
                    variable=self.source_or_byte_code,
                    value=0, cursor="hand2", font=self.normalfont).grid(row=1,
                    column=0, sticky=W)
        Radiobutton(self.byte_and_source_frame, bg=color, text="Source code",
                    variable=self.source_or_byte_code,
                    value=1, cursor="hand2", font=self.normalfont).grid(row=1,
                    column=1, sticky=W)

        mode_checkbutton = Checkbutton(self.checkbutton_frame, bg=color,
            text="1.4.x compatibility mode", variable=self.pys60_environment,
            font=self.specialfont)
        mode_checkbutton.grid(row=0, column=2)
        ToolTip(mode_checkbutton, compatibility_tip)
        self.profile_frame.grid(row=1, column=0, padx=5)
        self.heapsize_frame.grid(row=1, column=2, padx=10, pady=5)
        self.byte_and_source_frame.grid(row=2, columnspan=3, padx=10, pady=5)
        self.profile_and_heap_layout.grid(padx=2, pady=5, columnspan=3)
        self.checkbutton_frame.grid(pady=5, columnspan=3)
        self.optional_frame.grid(row=5)

    def check_state_and_configure(self):
        if self.state:
            if (self.display.get() == "" and self.version.get() == "" and \
                self.uid.get() == "" and self.public_key.get() == "" and \
                self.private_key.get() == "" and self.passphrase.get() == "" \
                and self.additional_arguments.get() == "" and \
                self.filename.get() == "" and self.heap_min.get() == "" and \
                self.heap_max.get() == "" and self.set_profile.get() == 0 and \
                self.pys60_environment.get() == 0 and \
                self.file_or_dir.get() == 0 and \
                self.source_or_byte_code.get() == 0 and \
                self.ignore_missing_deps.get() == 0):
                self.clear_all_button.configure(state=DISABLED)
            else:
                self.clear_all_button.configure(state=NORMAL)

    def clear_all(self):
        for field in self.entryname:
            field.set("")
        self.filename.set("")
        self.heap_min.set("")
        self.heap_max.set("")
        self.file_or_dir.set(0)
        self.set_profile.set(0)
        self.source_or_byte_code.set(0)
        self.ignore_missing_deps.set(0)
        self.pys60_environment.set(0)
        self.clear_all_button.configure(state=DISABLED)

    def hide_frame(self):
        self.state = 0
        self.optional_frame.destroy()
        self.expand_button.configure(text="More ▼",
                                     command=self.show_frame)
        ToolTip(self.expand_button, expand_tip)

    def showhtml(self):
        """ Displays the html documentation"""
        webbrowser.open("ensymble_ui_help.html")

    def show_options(self):
        """ Shows the options of ensymble in a text scrollbar window"""
        output_log = open("help.txt", "w")
        ret = subprocess.call("python ensymble.py py2sis --help",
            stdout=output_log, stderr=output_log, startupinfo=self.startupinfo)
        output_log.close()
        output_log = open("help.txt", "r")
        help_text = ''.join(output_log.readlines())
        output_log.close()
        os.remove("help.txt")
        newtop = Tk()
        newtop.iconbitmap('pycon.ico')
        newtop.title('Ensymble Options')
        textwidget = Text(newtop, height = 50)
        scrollbar = Scrollbar(newtop)
        textwidget.insert(END, help_text)
        textwidget.configure(state=DISABLED)
        scrollbar.config(command=textwidget.yview)
        textwidget.config(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        textwidget.pack(expand=YES)
        newtop.mainloop()

    def continue_warnings_callback(self, name, index, mode):
        self.check_state_and_configure()

    def clear_button_callback(self, name, index, mode):
        varValue = self.root.globalgetvar(name)
        if varValue != "":
            self.clear_all_button.configure(state=NORMAL)
        self.check_state_and_configure()

    def file_or_dir_callback(self, name, index, mode):
        varValue = self.root.globalgetvar(name)
        if varValue == 0:
            self.create_button.configure(state=NORMAL)
        else:
            self.create_button.configure(state=DISABLED)
        self.check_state_and_configure()
        self.filename.set("")

    def create_button_callback(self, name, index, mode):
        varValue = self.root.globalgetvar(name)
        if varValue != "":
            self.create_button.configure(state=NORMAL)
        else:
            self.create_button.configure(state=DISABLED)
        self.check_state_and_configure()

    def browse_script(self):
        """ Opens the file browser window"""
        file_name = self.filename.get()
        file_or_dir_name = ""
        if file_name != "":
            if os.path.exists(file_name):
                self.initial_dir = file_name
            else:
                tkMessageBox.showerror("Failure",
                                       "File\Directory " + '"' + file_name +\
                                       '"' + " does not exist")
                return
        if self.file_or_dir.get() == 1:
            file_or_dir_name =\
            tkFileDialog.askdirectory(initialdir=self.initial_dir)
        else:
            file_or_dir_name =\
            tkFileDialog.askopenfilename(title="Open",
                             initialdir=self.initial_dir,
                             filetypes=[("Python Files", ".py")])
        if file_or_dir_name:
            self.filename.set(file_or_dir_name)

    def browse_cert(self):
        cert_name =\
            tkFileDialog.askopenfilename(filetypes=[("Certificate", ".crt")])
        if cert_name:
            self.public_key.set(cert_name)
            private_key = str(cert_name)
            private_key = private_key.replace('.crt', '.key')
            if os.path.exists(private_key):
                self.private_key.set(private_key)

    def create_sis(self):
        """Creates sis for the file or directory specified"""
        appname = self.display.get()
        uid = self.uid.get()
        version = self.version.get()
        cert = self.public_key.get()
        key = self.private_key.get()
        filename = self.filename.get()
        cmd_args = self.additional_arguments.get()
        heap_min = self.heap_min.get()
        heap_max = self.heap_max.get()
        passphrase = self.passphrase.get()
        self.sis_path = ''
        args = ['python', 'ensymble.py', 'py2sis']
        if appname:
            for item in ['--appname', appname]:
                args.append(item)
        if version:
            for item in ['--version', version]:
                args.append(item)
        if cert:
            for item in ['--cert', cert, '--privkey', key]:
                args.append(item)
        if not passphrase:
            passphrase = ''
        for item in ['--passphrase', passphrase]:
            args.append(item)
        if uid:
            for item in ['--uid', uid]:
                args.append(item)
        if self.source_or_byte_code.get():
            args.append("--sourcecode")
        if self.ignore_missing_deps.get():
            args.append("--ignore-missing-deps")
        if cmd_args:
            cmd_args = cmd_args.split(' ')
            for item in cmd_args:
                if item.find('--') == -1:
                    self.sis_path = item
                    continue
                args.append(item)
        if self.set_profile.get():
            args.append("--profile=" + "console")
        if heap_min or heap_max:
            args.append("--heapsize")
            if heap_max and not heap_min:
                args.append(heap_max)
            elif heap_min and not heap_max:
                args.append(heap_min)
            else:
                args.append(heap_min + ',' + heap_max)
        if self.pys60_environment.get():
            args.append("--mode=" + "pys60")
        if filename:
            args.append(filename)
        if not self.sis_path:
            # When output path is not specified place the sis in script
            # directory
            self.sis_path = os.path.split(os.path.abspath(filename))[0]
        args.append(self.sis_path)
        self.output_log = open("log.txt", "w")
        ret = subprocess.call(args, stdout=self.output_log,
                         stderr=self.output_log, startupinfo=self.startupinfo)
        self.output_log.close()
        self.output_log = open("log.txt", "r")
        ensymble_output = ''.join(self.output_log.readlines())
        self.output_log.close()
        if ret != 0:
            display_text = "Ensymble output:\n" + ensymble_output
            EnsymbleOutputDialog(self.root, display_text, ret)
        else:
            sis_filename = None
            latest_timestamp = 0
            prev_dir = os.getcwd()
            os.chdir(self.sis_path)
            sis_files = [item for item in os.listdir(self.sis_path)
                         if item.endswith(".sis")]
            for file_name in sis_files:
                creation_time = os.stat(file_name).st_atime
                if creation_time > latest_timestamp:
                    latest_timestamp = creation_time
                    sis_filename = file_name
            if not self.sis_path.endswith('\\'):
                self.sis_path += '\\'
            os.chdir(prev_dir)
            display_text = "SIS file successfully created.\n" +\
                           "Ensymble output:\n" + ensymble_output
            EnsymbleOutputDialog(self.root, display_text,
                                 ret, self.sis_path, sis_filename)
        self.initial_dir = os.path.split(os.path.abspath(filename))[0]
        os.remove("log.txt")


if __name__ == "__main__":
    ensymblegui = GUI()
    ensymblegui.root.resizable(0, 0)
    ensymblegui.root.title('PyS60 application packager')
    ensymblegui.root.iconbitmap('pycon.ico')
    ensymblegui.root.mainloop()

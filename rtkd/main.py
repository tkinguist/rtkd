import tkinter as tk
from tkinter import ttk
from tkreform import Window
from tkreform.declarative import M, W, Packer, MenuBinder
from tkreform.menu import MenuCascade, MenuCommand, MenuSeparator
from tkreform.events import LMB, RMB, X2

win = Window(tk.Tk())

win.title = "RTKD"
win.size = 1000, 600

TK_WIDGETS = [
    "Button", "Checkbutton", "Entry", "Frame", "Label", "LabelFrame",
    "Listbox", "Message", "PanedWindow", "Radiobutton", "Scale", "Scrollbar",
    "Spinbox", "Text"
]

TTK_WIDGETS = [
    "Button", "Checkbutton", "Entry", "Frame", "Label", "LabelFrame",
    "Menubutton", "PanedWindow", "Radiobutton", "Scale", "Scrollbar",
    "Spinbox", "Combobox", "Notebook", "Progressbar", "Separator", "Sizegrip",
    "Treeview"
]

win /= (
    W(tk.Menu) * MenuBinder(win) / (
        M(MenuCascade(label="File"), tearoff=False) / (
            MenuCommand(label="New", accelerator="Ctrl+N"),
            MenuCommand(label="Open", accelerator="Ctrl+O"),
            MenuCommand(label="Save", accelerator="Ctrl+S"),
            MenuSeparator(),
            MenuCommand(label="Exit", command=win.destroy, accelerator="Alt+F4")
        ),
        M(MenuCascade(label="Edit"), tearoff=False),
        M(MenuCascade(label="View"), tearoff=False),
        M(MenuCascade(label="Tool"), tearoff=False),
        M(MenuCascade(label="Help"), tearoff=False)
    ),
    W(tk.PanedWindow, showhandle=True) * Packer(fill="both", expand=True) / (
        W(tk.LabelFrame, text="Widgets", labelanchor="nw", width=150) / (
            W(tk.LabelFrame, text="Widget Library", labelanchor="nw", height=50) * Packer(fill="both") / (
                W(ttk.Combobox, width=15, value=("tk", "ttk")) * Packer(fill="both"),
            ),
            W(tk.Frame) * Packer(fill="both", expand=True) / (
                W(tk.Listbox, width=15) * Packer(side="left", fill="both", expand=True),
                W(tk.Scrollbar) * Packer(side="right", fill="y")
            )
        ),
        W(tk.LabelFrame, text="tk"),
        W(tk.LabelFrame, text="Attributes", labelanchor="nw", width=150)
    ),
)


@win[1].on("<Configure>")
def global_update(event):
    win[1].base.paneconfig(win[1][1].base, width=event.width - win[1][0].width - win[1][2].width - 16)
    win[1].sync()


@win[1][0][0][0].on("<<ComboboxSelected>>")
def update_widgets(event):
    lib = win[1][0][0][0].base.get()
    if lib in ("tk", "ttk"):
        win[1][0][1][0].base.delete(0, len(TK_WIDGETS if lib == "tk" else TTK_WIDGETS) + 5)
        for x in (TK_WIDGETS if lib == "tk" else TTK_WIDGETS):
            win[1][0][1][0].base.insert("end", x)


@win[1][0][1][0].on(str(LMB - X2))
def widget_add(event):
    lib, target = win[1][0][0][0].base.get(), event.widget.get(event.widget.curselection())
    if lib in ("tk", "ttk"):
        w = win[1][1].add_widget(getattr(tk if lib == "tk" else ttk, target))
        w.place(in_=win[1][1].base)

        if isinstance(w.base, (tk.Frame, ttk.Frame)):
            w.width, w.height = 50, 50

        if isinstance(w.base, (tk.Label, ttk.Label)):
            w.width, w.height = 10, 5
            w.base["relief"] = "raised"

        widget_menu = win.add_widget(tk.Menu, tearoff=False)
        widget_menu /= (
            MenuCommand(label="Resize"),
            MenuCommand(label="Delete", command=w.base.destroy)
        )
        
        @w.on(str(-RMB))
        def _edit(event):
            widget_menu.base.post(event.x_root, event.y_root)

        @win[1][1].on("<Button>")
        def _unpost(event):
            widget_menu.base.unpost()

        x, y, tx, ty = 0, 0, 0, 0

        @w.on(str(LMB))
        def _hold(event):
            nonlocal tx, ty
            tx, ty = event.x, event.y

        @w.on("<B1-Motion>")
        def _move(event):
            nonlocal x, y
            x, y = event.x + x - tx, event.y + y - ty
            w.place(x=x, y=y)


win[1][0][0][0].base.current(0)
win[1][0][1][1].base.config(command=win[1][0][1][0].base.yview)
win[1][0][1][0].base.config(yscrollcommand=win[1][0][1][1].base.set)

update_widgets(None)

win.loop()

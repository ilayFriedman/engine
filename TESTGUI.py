import tkinter as tk
import tkinter.ttk as ttk

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.tree = ttk.Treeview()
        self.tree.pack()
        for i in range(10):
            self.tree.insert("", "end", text="Item %s" % i)
        self.tree.bind("<Double-1>", self.OnDoubleClick)
        self.root.mainloop()


    def OnDoubleClick(self, event):
        item = self.tree.identify('item',event.x,event.y)
        print (self.tree.item(item,"text"))
        print("you clicked on", self.tree.item(item,"text"))
        print()


if __name__ == "__main__":
    app = App()
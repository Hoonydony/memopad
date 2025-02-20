import tkinter as tk
from tkinter import filedialog, messagebox, font, simpledialog
from tkinter import ttk

class Notepad:
    def __init__(self, root):
        self.root = root
        self.root.title("Look_at_me")
        self.root.geometry("800x600")

        # 메뉴 바 생성
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        # 사용자 정의 메뉴 추가
        self.custom_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.custom_menu.add_command(label="About Look_at_me", command=self.show_about)
        self.custom_menu.add_command(label="Save Tab", command=self.save_file)
        self.custom_menu.add_command(label="Add Tab", command=self.new_tab)
        self.menu_bar.add_cascade(label="Look_at_me", menu=self.custom_menu)

        # 툴바 생성
        self.toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        font_size_button = tk.Button(self.toolbar, text="Font Size", command=self.change_font_size)
        font_size_button.pack(side=tk.LEFT, padx=2, pady=2)

        bold_button = tk.Button(self.toolbar, text="Bold", command=self.toggle_bold)
        bold_button.pack(side=tk.LEFT, padx=2, pady=2)

        underline_button = tk.Button(self.toolbar, text="Underline", command=self.toggle_underline)
        underline_button.pack(side=tk.LEFT, padx=2, pady=2)

        copy_all_button = tk.Button(self.toolbar, text="Copy All", command=self.copy_all)
        copy_all_button.pack(side=tk.RIGHT, padx=2, pady=2)

        save_button = tk.Button(self.toolbar, text="Save", command=self.save_file)
        save_button.pack(side=tk.RIGHT, padx=2, pady=2)

        # 탭 추가 버튼 툴바에 추가
        add_tab_button = tk.Button(self.toolbar, text="+", command=self.new_tab)
        add_tab_button.pack(side=tk.RIGHT, padx=2, pady=2)

        # 탭 프레임 생성
        self.tab_frame = tk.Frame(self.root)
        self.tab_frame.pack(side=tk.TOP, fill=tk.X)

        self.notebook = ttk.Notebook(self.tab_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.notebook.bind("<Double-Button-1>", self.rename_tab)

        # 메인 프레임 생성
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        self.current_font = font.Font(family="Cambria Math", size=25)
        self.new_tab()

        # 단축키 설정
        self.root.bind("<Command-z>", self.undo)
        self.root.bind("<Command-a>", self.select_all)
        self.root.bind("<Command-b>", self.toggle_bold)
        self.root.bind("<Command-u>", self.toggle_underline)

    def new_tab(self):
        title = simpledialog.askstring("New Tab", "Enter tab title:")
        if not title:
            return

        tab = ttk.Frame(self.notebook)
        text_area = tk.Text(tab, wrap=tk.WORD, font=self.current_font, undo=True)
        text_area.pack(expand=True, fill=tk.BOTH)

        # Initialize tags
        text_area.tag_configure("bold", font=(self.current_font.actual("family"), self.current_font.actual("size"), "bold"))
        text_area.tag_configure("underline", underline=True)

        self.notebook.add(tab, text=title)
        self.tabs[tab] = {"text_area": text_area, "filename": None}
        self.notebook.select(tab)


    def rename_tab(self, event):
        selected_tab = self.notebook.select()
        if not selected_tab:
            return
        
        index = self.notebook.index(selected_tab)
        current_title = self.notebook.tab(selected_tab, "text")

        entry = tk.Entry(self.notebook)
        entry.insert(0, current_title)
        entry.select_range(0, tk.END)
        entry.focus_set()

        def set_new_title(event):
            new_title = entry.get()
            if new_title:
                self.notebook.tab(selected_tab, text=new_title)
            entry.destroy()

        entry.bind("<Return>", set_new_title)
        entry.bind("<FocusOut>", lambda e: entry.destroy())
        
        self.notebook.tab(selected_tab, text=current_title)
        entry.place(in_=self.notebook, relx=0.5, rely=0.1, anchor="center")

    def save_file(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        if self.tabs[current_tab]["filename"]:
            self._save_to_file(self.tabs[current_tab]["text_area"], self.tabs[current_tab]["filename"])
        else:
            self.save_file_as()

    def save_file_as(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        filename = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if filename:
            self.tabs[current_tab]["filename"] = filename
            self._save_to_file(self.tabs[current_tab]["text_area"], filename)

    def _save_to_file(self, text_area, filename):
        try:
            content = text_area.get(1.0, tk.END)
            with open(filename, 'w') as file:
                file.write(content)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {e}")

    def copy_all(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        text_area = self.tabs[current_tab]["text_area"]
        self.root.clipboard_clear()
        self.root.clipboard_append(text_area.get(1.0, tk.END))
        self.root.update()

    def change_font_size(self):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        text_area = self.tabs[current_tab]["text_area"]
        new_size = simpledialog.askinteger("Font Size", "Enter new font size:")

        if new_size:
            # 선택된 텍스트가 있을 경우, 해당 텍스트에만 폰트 크기 적용
            if text_area.tag_ranges(tk.SEL):
                start, end = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
                text_area.tag_configure(f"size_{new_size}", font=(self.current_font.actual("family"), new_size))
                text_area.tag_add(f"size_{new_size}", start, end)
            else:
                # 선택된 텍스트가 없을 경우, 탭 전체 폰트 크기 변경
                self.current_font.configure(size=new_size)

    def _toggle_style(self, style):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        text_area = self.tabs[current_tab]["text_area"]

        if text_area.tag_ranges(tk.SEL):
            sel_first, sel_last = text_area.index(tk.SEL_FIRST), text_area.index(tk.SEL_LAST)
            if style in text_area.tag_names(sel_first):
                text_area.tag_remove(style, sel_first, sel_last)
            else:
                text_area.tag_add(style, sel_first, sel_last)


    def toggle_bold(self, event=None):
        self._toggle_style("bold")

    def toggle_underline(self, event=None):
        self._toggle_style("underline")


    def undo(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        text_area = self.tabs[current_tab]["text_area"]
        text_area.edit_undo()

    def select_all(self, event):
        current_tab = self.notebook.nametowidget(self.notebook.select())
        text_area = self.tabs[current_tab]["text_area"]
        text_area.tag_add("sel", "1.0", "end")

    def show_about(self):
        messagebox.showinfo("About", "Look_at_me version 0.2 by Hoonydony")

if __name__ == "__main__":
    root = tk.Tk()
    app = Notepad(root)
    root.createcommand('tk::mac::ShowAbout', lambda: messagebox.showinfo("About", "Look_at_me 0.2 by Hoonydony"))
    root.mainloop()
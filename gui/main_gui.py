import os
import sys
import json
import tkinter as tk
from tkinter import ttk
from tkinter import font as tkfont
from base.Model import Product
import threading


# --- Utility to get resource path for PyInstaller ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temporary folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Load JSON config ---
config_path = resource_path("configs.json")
with open(config_path, "r", encoding="utf-8") as f:
    config_data = json.load(f)

# --- Output folder ---
if getattr(sys, 'frozen', False):
    # running as exe
    root_dir = os.path.dirname(sys.executable)
else:
    # running as python script
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

output_dir = os.path.join(root_dir, "result")
os.makedirs(output_dir, exist_ok=True)

# --- Color palette (user provided) ---
PRIMARY = "#0eb693"
ACCENT = "#0d2c40"
BG = "#f6f8f8"
CARD = "#ffffff"
TEXT = ACCENT

# --- Main Wizard Class ---
class PriceUpdater(tk.Tk):
    def __init__(self):
        super().__init__()

        # set icon...
        try:
            self.iconbitmap(resource_path("icon.ico"))
        except Exception:
            try:
                img = tk.PhotoImage(file=resource_path("icon.png"))
                self.wm_iconphoto(True, img)
            except Exception:
                pass

        self.title("Price Crawler")
        # initial geometry
        w, h = 620, 480
        self.geometry(f"{w}x{h}")

        # set a minimum size (safe variant)
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        min_w = min(w, max(200, screen_w - 100))
        min_h = min(h, max(150, screen_h - 100))
        self.minsize(min_w, min_h)

        self.resizable(True, True)
        self.configure(bg=BG)

        # center window on screen (use final w/h)
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

        # fonts (reverted to a neutral/system font)
        self.header_font = tkfont.Font(family="Segoe UI", size=16, weight="bold")
        self.normal_font = tkfont.Font(family="Segoe UI", size=11)
        self.small_font = tkfont.Font(family="Segoe UI", size=9)

        # ttk style
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure("TFrame", background=BG)
        style.configure("Card.TFrame", background=CARD, relief="flat")
        # Header label: background = BG so it appears without card background
        style.configure("Header.TLabel", background=BG, foreground=TEXT, font=self.header_font, anchor="e", justify="right")
        style.configure("Title.TLabel", background=CARD, foreground=TEXT, font=self.normal_font, anchor="e", justify="right")
        style.configure("TLabel", background=BG, foreground=TEXT, font=self.normal_font, anchor="e", justify="right")

        # Button styles
        style.configure("Primary.TButton",
                        background=PRIMARY,
                        foreground="white",
                        relief="flat",
                        padding=8,
                        font=self.normal_font)
        style.map("Primary.TButton",
                  background=[("active", PRIMARY), ("disabled", "#bfbfbf")])

        style.configure("Ghost.TButton",
                        background=CARD,
                        foreground=TEXT,
                        relief="flat",
                        padding=6,
                        font=self.normal_font)
        style.map("Ghost.TButton",
                  background=[("active", "#f0f0f0")])

        # Progressbar style
        style.layout("Green.Horizontal.TProgressbar",
                     [('Horizontal.Progressbar.trough',
                       {'children': [('Horizontal.Progressbar.pbar', {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'we'})])
        style.configure("Green.Horizontal.TProgressbar",
                        troughcolor=CARD,
                        background=PRIMARY,
                        thickness=12)

        # special remaining label style: use card background so it appears "no separate bg"
        style.configure("Remaining.TLabel", background=CARD, foreground=ACCENT, font=self.small_font, anchor="w", justify="left")

        # state
        self.category = None
        self.selected_products = []

        self.frames = {}
        for F in (CategoryPage, ProductPage, ProgressPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            # place each page centered in main window
            frame.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.98, relheight=0.96)

        self.show_frame("CategoryPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

# --- Thin minimal scrollbar (Canvas-based, no arrows) ---
class ThinScrollbar(tk.Canvas):
    """
    Minimal, thin vertical scrollbar implemented with Canvas.
    - Acts like a scrollbar: accepts a command (e.g., canvas.yview).
    - Exposes .set(first, last) to update thumb position from the scrolled widget.
    - No arrows, narrow width, minimal look (like modern Windows overlay scrollbar).
    """
    def __init__(self, parent, command=None, width=8, track_color="#eef3f3",
                 thumb_color="#cfdeda", thumb_active="#0eb693", **kw):

        # مقدار bg رو امن بگیر
        bg_color = kw.pop("bg", CARD)

        super().__init__(parent, width=width, highlightthickness=0,
                         bg=bg_color, bd=0, **kw)

        self.command = command
        self.width_px = width
        self.track_color = track_color
        self.thumb_color = thumb_color
        self.thumb_active = thumb_active

        # draw track and thumb placeholders
        self._track = self.create_rectangle(0, 0, width, 0, fill=self.track_color, outline="")
        self._thumb = self.create_rectangle(0, 0, width, 0, fill=self.thumb_color, outline="", tags="thumb")

        # state for dragging
        self._dragging = False
        self._drag_offset = 0  # pixel offset inside thumb where user clicked

        # bindings
        self.tag_bind("thumb", "<Button-1>", self._on_thumb_press)
        self.tag_bind("thumb", "<B1-Motion>", self._on_thumb_drag)
        self.bind("<Button-1>", self._on_track_click)
        self.bind("<Configure>", self._on_configure)
        # change thumb color on enter/leave for subtle hover feedback
        self.tag_bind("thumb", "<Enter>", lambda e: self.itemconfig(self._thumb, fill=self.thumb_active))
        self.tag_bind("thumb", "<Leave>", lambda e: self.itemconfig(self._thumb, fill=self.thumb_color))

    def _on_configure(self, event=None):
        # redraw track full height and ensure thumb positioned
        h = int(self.winfo_height())
        w = int(self.width_px)
        self.coords(self._track, 0, 0, w, h)
        # if thumb currently has coords, keep them but ensure inside bounds
        # otherwise set thumb full (will be resized by .set)
        # no-op here; actual thumb size set by .set()

    def set(self, first, last):
        """
        Called by the scrolled widget to update the thumb.
        first, last are floats (or strings) in [0..1] indicating the visible fraction.
        """
        try:
            f = float(first)
            l = float(last)
        except Exception:
            return
        h = max(1, int(self.winfo_height()))
        w = int(self.width_px)
        # when content fits entirely, show nothing (thumb covers full area but make it inactive)
        if l - f >= 0.9999:
            self.coords(self._thumb, 0, 0, w, h)
            self.itemconfigure(self._thumb, state="hidden")
            return
        else:
            self.itemconfigure(self._thumb, state="normal")

        thumb_top = int(f * h)
        thumb_bottom = int(l * h)
        # set a minimum thumb size for usability
        min_h = 24
        if (thumb_bottom - thumb_top) < min_h:
            center = int((thumb_top + thumb_bottom) / 2)
            thumb_top = max(0, center - min_h // 2)
            thumb_bottom = min(h, center + min_h // 2)
        self.coords(self._thumb, 0, thumb_top, w, thumb_bottom)

    def _on_thumb_press(self, event):
        self._dragging = True
        # compute where inside thumb the click occurred
        x1, y1, x2, y2 = self.coords(self._thumb)
        self._drag_offset = event.y - y1
        # visually indicate active
        self.itemconfig(self._thumb, fill=self.thumb_active)

    def _on_thumb_drag(self, event):
        if not self._dragging:
            return
        h = max(1, int(self.winfo_height()))
        x1, y1, x2, y2 = self.coords(self._thumb)
        thumb_h = int(y2 - y1)
        # compute new top coordinate so that pointer stays at same offset
        new_top = event.y - self._drag_offset
        # clamp
        new_top = max(0, min(new_top, h - thumb_h))
        # set coords
        self.coords(self._thumb, 0, new_top, self.width_px, new_top + thumb_h)
        # compute fraction and call command
        if callable(self.command):
            fraction = new_top / max(1, (h - thumb_h))
            # command expects something like widget.yview_moveto
            try:
                self.command("moveto", fraction)
            except Exception:
                # many widgets expect a function that accepts ("moveto", fraction)
                try:
                    self.command(fraction)
                except Exception:
                    pass

    def _on_track_click(self, event):
        # if click outside thumb, move page up/down: center thumb around clicked point
        h = max(1, int(self.winfo_height()))
        x1, y1, x2, y2 = self.coords(self._thumb)
        thumb_h = int(y2 - y1)
        if event.y < y1:
            # page up
            target_top = max(0, event.y - thumb_h // 2)
        elif event.y > y2:
            # page down
            target_top = min(h - thumb_h, event.y - thumb_h // 2)
        else:
            # clicked on thumb already handled by thumb binding
            return
        # set coords and call command
        self.coords(self._thumb, 0, target_top, self.width_px, target_top + thumb_h)
        if callable(self.command):
            fraction = target_top / max(1, (h - thumb_h))
            try:
                self.command("moveto", fraction)
            except Exception:
                try:
                    self.command(fraction)
                except Exception:
                    pass

# --- Helper: scrollable area with canvas (uses ThinScrollbar) ---
class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, bg=CARD, *args, **kwargs):
        super().__init__(parent, style="Card.TFrame")
        # canvas for content
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0, bg=bg)
        # minimal thin scrollbar on the right
        self.scrollbar = ThinScrollbar(self, command=self._yview, width=8, bg=CARD,
                                    track_color="#eef3f3", thumb_color="#d7eae1", thumb_active=PRIMARY)

        # inner frame to put widgets
        self.inner = tk.Frame(self.canvas, bg=bg)

        self.inner_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        # pack: canvas fills, scrollbar on right
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # configure canvas scroll
        self.canvas.configure(yscrollcommand=self._on_canvas_scroll)

        # resize handling
        self.inner.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        # allow mousewheel on the canvas (Windows)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _yview(self, *args):
        """
        Acts as the command for the scrollbar to control the canvas yview.
        Accepts same args as canvas.yview (e.g., 'moveto', fraction) or ('scroll', n, 'units')
        """
        try:
            self.canvas.yview(*args)
        except Exception:
            # fallback: if command called with a single float, try moveto
            if len(args) == 1:
                try:
                    frac = float(args[0])
                    self.canvas.yview_moveto(frac)
                except Exception:
                    pass

    def _on_canvas_scroll(self, first, last):
        # canvas -> scrollbar update; forward normalized fractions
        self.scrollbar.set(first, last)

    def _on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # keep inner width same as canvas
        canvas_width = event.width
        self.canvas.itemconfig(self.inner_id, width=canvas_width)

    def _on_mousewheel(self, event):
        # windows default: delta multiples of 120
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

# --- Category Page ---
class CategoryPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.selected_category = None
        self.item_widgets = {}  # name -> (frame, label)

        header = ttk.Label(self, text="انتخاب دسته‌بندی", style="Header.TLabel")
        header.pack(padx=18, pady=(18, 6), anchor="e")

        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        # scrollable list area
        self.scroll_area = ScrollableFrame(container, bg=CARD)
        self.scroll_area.pack(fill="both", expand=True, padx=6, pady=6)

        btn_frame = tk.Frame(container, bg=CARD)
        btn_frame.pack(padx=18, pady=(6, 18), fill="x")

        next_btn = ttk.Button(btn_frame, text="بعدی", style="Primary.TButton", command=self.next_page)
        next_btn.pack(side="right")

        self.build_items()

    def build_items(self):
        # clear existing
        for w in self.scroll_area.inner.winfo_children():
            w.destroy()
        self.item_widgets.clear()
        for idx, cat in enumerate(config_data.keys()):
            item_frame = tk.Frame(self.scroll_area.inner, bg=CARD)
            item_frame.pack(fill="x")
            # label aligned to right
            lbl = tk.Label(item_frame, text=cat, bg=CARD, fg=TEXT, font=self.controller.normal_font,
                           anchor="e", justify="right", cursor="hand2")
            lbl.pack(fill="both", padx=12, pady=12, anchor="e")
            # bind click
            lbl.bind("<Button-1>", lambda e, name=cat: self.on_click(name))
            # minimal separator
            sep = tk.Frame(self.scroll_area.inner, height=1, bg="#e9eef0")
            sep.pack(fill="x", padx=8)
            self.item_widgets[cat] = (item_frame, lbl)

    def on_click(self, name):
        # single-select behavior
        if self.selected_category == name:
            return
        # unselect previous
        if self.selected_category and self.selected_category in self.item_widgets:
            prev_frame, prev_lbl = self.item_widgets[self.selected_category]
            prev_frame.configure(bg=CARD)
            prev_lbl.configure(bg=CARD, fg=TEXT)
        # select new
        frame, lbl = self.item_widgets[name]
        frame.configure(bg=PRIMARY)
        lbl.configure(bg=PRIMARY, fg="white")
        self.selected_category = name

    def next_page(self):
        if not self.selected_category:
            return
        self.controller.category = self.selected_category
        self.controller.show_frame("ProductPage")

# --- Product Page ---
class ProductPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller
        self.selected_products_set = set()
        self.item_widgets = {}  # name -> (frame, lbl)

        header = ttk.Label(self, text="انتخاب محصولات", style="Header.TLabel")
        header.pack(padx=18, pady=(18, 6), anchor="e")

        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        self.scroll_area = ScrollableFrame(container, bg=CARD)
        self.scroll_area.pack(fill="both", expand=True, padx=6, pady=6)

        btn_frame = tk.Frame(container, bg=CARD)
        btn_frame.pack(padx=18, pady=(6, 18), fill="x")

        # جای دکمه‌ها برعکس شد: بازگشت سمت چپ، اجرا سمت راست
        back_btn = ttk.Button(btn_frame, text="بازگشت", style="Ghost.TButton",
                              command=lambda: controller.show_frame("CategoryPage"))
        back_btn.pack(side="left")

        run_btn = ttk.Button(btn_frame, text="اجرا", style="Primary.TButton", command=self.run_products)
        run_btn.pack(side="right")

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        # rebuild product list for selected category
        self.build_items()

    def build_items(self):
        # clear existing
        for w in self.scroll_area.inner.winfo_children():
            w.destroy()
        self.item_widgets.clear()
        self.selected_products_set.clear()

        category = self.controller.category
        products = list(config_data.get(category, {}).keys())
        for prod in products:
            item_frame = tk.Frame(self.scroll_area.inner, bg=CARD)
            item_frame.pack(fill="x")
            lbl = tk.Label(item_frame, text=prod, bg=CARD, fg=TEXT, font=self.controller.normal_font,
                           anchor="e", justify="right", cursor="hand2")
            lbl.pack(fill="both", padx=12, pady=12, anchor="e")
            # bind click (toggle)
            lbl.bind("<Button-1>", lambda e, name=prod: self.on_toggle(name))
            sep = tk.Frame(self.scroll_area.inner, height=1, bg="#e9eef0")
            sep.pack(fill="x", padx=8)
            self.item_widgets[prod] = (item_frame, lbl)

    def on_toggle(self, name):
        # toggle selection (multi-select)
        frame, lbl = self.item_widgets[name]
        if name in self.selected_products_set:
            # unselect
            self.selected_products_set.remove(name)
            frame.configure(bg=CARD)
            lbl.configure(bg=CARD, fg=TEXT)
        else:
            # select
            self.selected_products_set.add(name)
            frame.configure(bg=PRIMARY)
            lbl.configure(bg=PRIMARY, fg="white")

    def run_products(self):
        if not self.selected_products_set:
            return
        self.controller.selected_products = list(self.selected_products_set)
        self.controller.show_frame("ProgressPage")
        self.controller.frames["ProgressPage"].start_processing()

# --- Progress Page ---
class ProgressPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg=BG)
        self.controller = controller

        # header label kept as attribute so we can change it after processing
        self.header_label = ttk.Label(self, text="درحال به‌روز‌رسانی قیمت‌ها", style="Header.TLabel")
        self.header_label.pack(padx=18, pady=(14, 6), anchor="e")

        container = ttk.Frame(self, style="Card.TFrame")
        container.pack(fill="both", expand=True, padx=12, pady=(6, 12))

        # ---------- Use ScrollableFrame here ----------
        # create a scrollable area (uses your ScrollableFrame implementation)
        self.scroll_area = ScrollableFrame(container, bg=CARD)
        self.scroll_area.pack(fill="both", expand=True, padx=6, pady=6)

        # the inner frame where we'll add progress items
        # NOTE: your ScrollableFrame exposes the inner frame as `inner`
        self.progress_frame = self.scroll_area.inner

        # back button (kept but not packed immediately)
        self.back_btn = ttk.Button(container, text="بازگشت به دسته‌ها", style="Ghost.TButton",
                                   command=self.go_back)
        self.progress_items = []

    def start_processing(self):
        try:
            self.back_btn.pack_forget()
        except Exception:
            pass

        # clear existing items from the scrollable inner frame
        for widget in self.progress_frame.winfo_children():
            widget.destroy()
        self.progress_items.clear()

        category = self.controller.category
        for product_name in self.controller.selected_products:
            frame_item = tk.Frame(self.progress_frame, bg=CARD)
            frame_item.pack(fill="x", pady=8, padx=8)

            label_frame = tk.Frame(frame_item, bg=CARD)
            label_frame.pack(fill="x")

            # نام محصول راست‌چین
            label_name = ttk.Label(label_frame, text=product_name, style="Title.TLabel")
            label_name.pack(side="right", anchor="e")

            # remaining به زبان انگلیسی -- بدون پس‌زمینه جداگانه (هم‌رنگ کارت)
            label_remaining = ttk.Label(label_frame, text="0/0 remaining", style="Remaining.TLabel")
            label_remaining.pack(side="left", anchor="w")

            bar = ttk.Progressbar(frame_item, style="Green.Horizontal.TProgressbar",
                                  length=480, mode="determinate", maximum=100)
            bar.pack(fill="x", pady=(8, 4))

            self.progress_items.append({
                "bar": bar,
                "label_remaining": label_remaining,
                "label_name": label_name,
                "name": product_name,
                "category": category,
            })

        # ensure header reset to in-progress text when starting
        self.header_label.config(text="درحال به‌روز‌رسانی قیمت‌ها")
        self.update_idletasks()
        threading.Thread(target=self.process_products_thread, daemon=True).start()

    def process_products_thread(self):
        category = self.controller.category
        for item in self.progress_items:
            product_name = item["name"]
            bar = item["bar"]
            label_remaining = item["label_remaining"]

            config = config_data[category][product_name]
            p = Product(name=product_name, category=category, config=config, output_location=output_dir)
            total = p.get_total_combinations()
            if total <= 0:
                self.after(0, lambda lb=label_remaining, b=bar: self.update_bar(b, lb, total, total, 100))
                continue

            def progress_callback(done, total, lb=label_remaining, b=bar):
                percent = (done / total) * 100 if total else 100
                self.after(0, lambda: self.update_bar(b, lb, done, total, percent))

            try:
                p.calculate_prices(progress_callback=progress_callback)
            except Exception as e:
                self.after(0, lambda lb=label_remaining: lb.config(text="Error"))
            finally:
                self.after(0, lambda lb=label_remaining, b=bar: (lb.config(text="Finished"), b.config(value=100)))

        # all done: change header text, and show back button
        self.after(0, lambda: self.header_label.config(text="پایان به‌روز‌رسانی"))
        self.after(0, self.show_back_button)

    def update_bar(self, bar, label, done, total, percent):
        bar["value"] = percent
        if total and done >= total:
            label.config(text="Finished")
        else:
            label.config(text=f"{done}/{total} remaining")
        self.update_idletasks()

    def show_back_button(self):
        if not self.back_btn.winfo_ismapped():
            # pack the back button into the same container (it was created earlier)
            self.back_btn.pack(side="bottom", pady=12)

    def go_back(self):
        self.controller.selected_products = []
        self.controller.show_frame("CategoryPage")


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        try:
            import ctypes
            myappid = "pricecrawler"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception:
            pass

    app = PriceUpdater()
    app.mainloop()
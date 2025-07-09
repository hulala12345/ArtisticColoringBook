# Artistic Coloring Book application implemented using tkinter.
# Features include gallery, coloring workspace with palette, zoom, textures, and saving.
# Note: advanced image saving with effects requires Pillow; if unavailable, saving uses PostScript.

import tkinter as tk
from tkinter import colorchooser, filedialog, messagebox
import io

try:
    from PIL import Image, ImageTk, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

class ColoringPage(tk.Canvas):
    def __init__(self, master, width=800, height=600, **kwargs):
        super().__init__(master, width=width, height=height, bg='white', **kwargs)
        self.bind('<B1-Motion>', self.paint)
        self.bind('<ButtonPress-1>', self.start_paint)
        self.color = 'black'
        self.brush_size = 5
        self.drawing = []  # store drawing actions
        self.scale_factor = 1.0
        self.texture = None

    def start_paint(self, event):
        self.last_x, self.last_y = event.x, event.y

    def paint(self, event):
        x, y = event.x, event.y
        line = self.create_line(self.last_x, self.last_y, x, y,
                                fill=self.color, width=self.brush_size,
                                capstyle=tk.ROUND, smooth=True)
        self.drawing.append(('line', self.last_x, self.last_y, x, y,
                            self.color, self.brush_size))
        self.last_x, self.last_y = x, y

    def set_brush_color(self, color):
        self.color = color

    def set_brush_size(self, size):
        self.brush_size = size

    def apply_texture(self, texture):
        self.texture = texture
        # Simple texture application: overlay pattern lines
        if texture == 'crosshatch':
            step = 10
            for i in range(0, int(self['width']), step):
                self.create_line(i, 0, i, int(self['height']), fill='grey', dash=(2, 2))
            for j in range(0, int(self['height']), step):
                self.create_line(0, j, int(self['width']), j, fill='grey', dash=(2, 2))
        # Additional patterns can be added here

    def zoom(self, factor):
        if factor < 0.5 or factor > 2.0:
            return
        self.scale('all', 0, 0, factor / self.scale_factor, factor / self.scale_factor)
        self.scale_factor = factor

    def save_image(self, path, fmt='PNG'):
        if PIL_AVAILABLE:
            # Use Pillow to create an image from the canvas
            self.update()
            ps = self.postscript(colormode='color')
            img = Image.open(io.BytesIO(ps.encode('utf-8')))
            img.save(path, fmt)
        else:
            # Fallback to PostScript
            ps_path = path + '.ps'
            self.postscript(file=ps_path, colormode='color')
            messagebox.showinfo('Save', f'Image saved as {ps_path}. Convert to {fmt} using external tools.')

class Gallery(tk.Frame):
    def __init__(self, master, on_select):
        super().__init__(master)
        self.on_select = on_select
        self.create_gallery()

    def create_gallery(self):
        categories = ['Nature', 'Animals', 'Fantasy']
        for idx, cat in enumerate(categories):
            btn = tk.Button(self, text=cat, command=lambda c=cat: self.select_category(c))
            btn.grid(row=0, column=idx, padx=10, pady=10)
        self.thumb_frame = tk.Frame(self)
        self.thumb_frame.grid(row=1, column=0, columnspan=3)
        self.load_thumbnails('Nature')

    def select_category(self, category):
        for widget in self.thumb_frame.winfo_children():
            widget.destroy()
        self.load_thumbnails(category)

    def load_thumbnails(self, category):
        for i in range(3):
            lbl = tk.Label(self.thumb_frame, text=f'{category} {i+1}', bg='lightgrey', width=20, height=10)
            lbl.bind('<Button-1>', lambda e, c=category, idx=i: self.on_select(c, idx))
            lbl.grid(row=0, column=i, padx=5, pady=5)

class ColoringApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Artistic Coloring Book')
        self.geometry('1000x700')
        self.gallery = Gallery(self, self.start_coloring)
        self.gallery.pack(fill='both', expand=True)
        self.workspace = None

    def start_coloring(self, category, index):
        if self.workspace:
            self.workspace.destroy()
        self.gallery.pack_forget()
        self.workspace = tk.Frame(self)
        self.workspace.pack(fill='both', expand=True)
        self.page = ColoringPage(self.workspace)
        self.page.pack(side='left', fill='both', expand=True)
        toolbar = tk.Frame(self.workspace)
        toolbar.pack(side='right', fill='y')
        palette_btn = tk.Button(toolbar, text='Pick Color', command=self.choose_color)
        palette_btn.pack(pady=5)
        size_scale = tk.Scale(toolbar, from_=1, to=20, orient='horizontal',
                              label='Brush Size', command=lambda v: self.page.set_brush_size(int(v)))
        size_scale.set(5)
        size_scale.pack(pady=5)
        zoom_scale = tk.Scale(toolbar, from_=50, to=200, orient='horizontal',
                              label='Zoom %', command=lambda v: self.page.zoom(int(v)/100))
        zoom_scale.set(100)
        zoom_scale.pack(pady=5)
        texture_btn = tk.Button(toolbar, text='Apply Crosshatch',
                                command=lambda: self.page.apply_texture('crosshatch'))
        texture_btn.pack(pady=5)
        save_btn = tk.Button(toolbar, text='Save', command=self.save_art)
        save_btn.pack(pady=5)

    def choose_color(self):
        color = colorchooser.askcolor(title='Choose color')
        if color[1]:
            self.page.set_brush_color(color[1])

    def save_art(self):
        path = filedialog.asksaveasfilename(defaultextension='.png',
                                            filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg')])
        if path:
            fmt = 'PNG' if path.lower().endswith('.png') else 'JPEG'
            self.page.save_image(path, fmt)

if __name__ == '__main__':
    app = ColoringApp()
    app.mainloop()

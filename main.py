import tkinter as tk
import customtkinter as ctk
import tkinter as tk
import customtkinter as ctk
import os
import sys
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk

# Import Mixins
from simpleedit import SimpleEditMixin
from processing import ProcessingMixin
from colors import ColorsMixin
from ai_tools import AiToolsMixin

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

class Application(ctk.CTk, SimpleEditMixin, ProcessingMixin, ColorsMixin, AiToolsMixin):
    def __init__(self):
        super().__init__()
        self.title("Imagine Penguin")
        self.geometry("1400x900")
        
        # Set App Icon
        try:
            # Resize icon to avoid X11 BadLength error for large images
            icon_path = self.resource_path("icon.png")
            icon_img = Image.open(icon_path)
            icon_img = icon_img.resize((128, 128), Image.Resampling.LANCZOS)
            self.iconphoto(False, ImageTk.PhotoImage(icon_img))
        except Exception as e:
            print(f"Warning: Could not load icon: {e}")

        # Colors
        self.bg_color = "#000000"
        self.sidebar_color = "#111111"
        self.header_color = "#111111"
        self.text_color = "#FFFFFF"
        self.accent_color = "#E91E63" # Pinkish Red
        self.hover_color = "#222222"

        # Alterar o fundo para preto
        self.configure(bg=self.bg_color)

        # Definir a fonte padrão
        self.default_font = ctk.CTkFont(family="Comic Sans MS", size=14, weight="bold")

        self.create_menu()
        self.create_layout()

        self.image_history = [] # Stack to store previous image states
        self.sidebar_visible = True

        self.image_label = None
        self.original_image = None # Keep original for reset if needed
        self.processed_image = None # Current state of image
        self.display_image = None # Image ready for display (resized)

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def save_state(self):
        if self.processed_image:
             self.image_history.append(self.processed_image.copy())

    def undo(self):
        if self.edit_menu_visible:
             self.toggle_edit_menu() # Hide menu after selection
        if self.image_history:
             self.processed_image = self.image_history.pop()
             self.update_image_display()
        else:
             messagebox.showinfo("Info", "Nothing to undo")

    def styled_button(self, parent, text, command, fg_color="transparent", text_color="white", hover_color=None, width=None, anchor="w"):
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            corner_radius=0,
            height=36,
            width=width if width else 200,
            fg_color=fg_color,
            hover_color=hover_color if hover_color else self.hover_color,
            text_color=text_color,
            anchor=anchor,
            font=self.default_font
        )

    def section_header(self, parent, text):
        return ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=12, weight="bold"), text_color="#666666", anchor="w")

    def create_menu(self):
        # Using custom header instead of OS menu
        # Keeping empty or minimal if needed, but for now we build the header manually
        pass

    def create_layout(self):
        # Main Container
        main_container = ctk.CTkFrame(self, fg_color=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Top Bar
        self.top_bar = ctk.CTkFrame(main_container, height=50, fg_color=self.header_color, corner_radius=0)
        self.top_bar.pack(side=tk.TOP, fill=tk.X)

        # Decoration: Hamburger Icon (text for now)
        ctk.CTkButton(self.top_bar, text="☰", width=40, fg_color="transparent", hover_color=self.hover_color, font=("Comic Sans MS", 20), command=self.toggle_sidebar).pack(side=tk.LEFT, padx=(10, 5))
        

        # Pseudo Menu Buttons
        self.styled_button(self.top_bar, "File", command=self.load_image, width=50, fg_color="#333333", text_color="white").pack(side=tk.LEFT, padx=5, pady=8)
        self.edit_btn = self.styled_button(self.top_bar, "Edit", command=self.toggle_edit_menu, width=50)
        self.edit_btn.pack(side=tk.LEFT, padx=5, pady=8)

        # Export Button
        # Export Button
        self.styled_button(self.top_bar, text="Export", command=self.save_image, fg_color=self.accent_color, hover_color="#C2185B", width=80, anchor="center").pack(side=tk.RIGHT, padx=15, pady=8)

        # Content Container (Sidebar + Main)
        content_container = ctk.CTkFrame(main_container, fg_color="transparent")
        content_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

        # Sidebar (Left)
        self.sidebar = ctk.CTkFrame(content_container, width=250, corner_radius=0, fg_color=self.sidebar_color)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Tools Section
        self.section_header(self.sidebar, "TOOLS").pack(padx=20, pady=(20, 10))
        
        self.simple_edit_btn = self.styled_button(self.sidebar, text="✂ Simple Edit", command=self.show_simple_edit_tools)
        self.simple_edit_btn.pack(fill=tk.X, pady=2, padx=10)
        
        self.processing_btn = self.styled_button(self.sidebar, text="🪄 Processing", command=self.show_processing_tools)
        self.processing_btn.pack(fill=tk.X, pady=2, padx=10)
        
        self.colors_btn = self.styled_button(self.sidebar, text="🎨 Colors", command=self.show_colors_tools)
        self.colors_btn.pack(fill=tk.X, pady=2, padx=10)

        self.ai_btn = self.styled_button(self.sidebar, text="🤖 AI Tools", command=self.show_ai_tools)
        self.ai_btn.pack(fill=tk.X, pady=2, padx=10)

        # Container for sub-tools (hidden initially)
        self.edit_tools_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")

        # Content Area (Right)
        self.content_area = ctk.CTkFrame(content_container, fg_color=self.bg_color)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Main Image Area
        self.image_display_label = ctk.CTkLabel(self.content_area, text="")
        # Pack is handled in update_display
        
        # Empty State
        self.empty_state_frame = ctk.CTkFrame(self.content_area, fg_color="transparent", border_width=1, border_color="#333333")
        self.empty_state_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.4, relheight=0.4)
        
        ctk.CTkLabel(self.empty_state_frame, text="⬆", font=("Comic Sans MS", 48), text_color="#444444").pack(pady=(40, 10))
        ctk.CTkLabel(self.empty_state_frame, text="No Image Loaded", font=("Comic Sans MS", 18, "bold"), text_color="white").pack(pady=5)
        ctk.CTkLabel(self.empty_state_frame, text="Drag and drop an image here, or click to upload", font=("Comic Sans MS", 12), text_color="#888888").pack(pady=5)
        
        self.styled_button(self.empty_state_frame, text="Browse Files", command=self.load_image, fg_color="#333333", hover_color=self.hover_color, anchor="center").pack(pady=20)

        # Loading Indicator (Initially hidden)
        self.loading_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        self.loading_label = ctk.CTkLabel(self.loading_frame, text="Processing...", font=ctk.CTkFont(size=18, weight="bold"))
        self.loading_label.pack(pady=10)
        self.progress_bar = ctk.CTkProgressBar(self.loading_frame, orientation="horizontal", mode="indeterminate", progress_color=self.accent_color)
        self.progress_bar.pack()

        # Custom Edit Dropdown Menu (Hidden initially)
        self.edit_menu_frame = ctk.CTkFrame(self, width=150, height=40, fg_color=self.header_color, corner_radius=0, border_width=1, border_color="#333333")
        self.styled_button(self.edit_menu_frame, "Undo", self.undo, width=140, anchor="w").pack(padx=5, pady=5)
        self.edit_menu_visible = False

    def toggle_edit_menu(self):
        if self.edit_menu_visible:
            self.edit_menu_frame.place_forget()
            self.edit_menu_visible = False
        else:
            # Position relative to edit button
            x = self.edit_btn.winfo_rootx() - self.winfo_rootx()
            y = self.edit_btn.winfo_rooty() - self.winfo_rooty() + self.edit_btn.winfo_height() + 5
            self.edit_menu_frame.place(x=x, y=y)
            self.edit_menu_frame.lift() # Ensure it's on top
            self.edit_menu_visible = True

    def show_loading(self):
        self.image_display_label.pack_forget()
        self.empty_state_frame.place_forget()
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        self.progress_bar.start()

    def hide_loading(self):
        self.loading_frame.place_forget()
        self.progress_bar.stop()
        if self.processed_image:
           self.image_display_label.pack(expand=True)
        else:
           self.empty_state_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.4, relheight=0.4)

    def hide_sub_tools(self):
        self.edit_tools_frame.pack_forget()
        self.simple_edit_btn.pack(fill=tk.X, pady=2, padx=10)
        self.processing_btn.pack(fill=tk.X, pady=2, padx=10)
        self.processing_btn.pack(fill=tk.X, pady=2, padx=10)
        self.colors_btn.pack(fill=tk.X, pady=2, padx=10)
        self.ai_btn.pack(fill=tk.X, pady=2, padx=10)

    def load_image(self):
        # Determine initial directory
        initial_dir = os.getcwd()
        home = os.path.expanduser("~")
        potential_dirs = ["Imagens", "Images"]
        for d in potential_dirs:
            p = os.path.join(home, d)
            if os.path.exists(p):
                initial_dir = p
                break

        file_path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        
        if file_path:
            try:
                self.original_image = Image.open(file_path)
                self.processed_image = self.original_image.copy()
                self.image_history = [] # Clear history on new load
                self.update_image_display()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load image: {e}")

    def save_image(self):
        if self.processed_image:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")]
            )
            if file_path:
                try:
                    self.processed_image.save(file_path)
                    messagebox.showinfo("Success", "Image saved successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save image: {e}")
        else:
            messagebox.showwarning("Warning", "No image to save.")

    def update_image_display(self):
        if self.processed_image:
            # Resize image to fit content area while maintaining aspect ratio
            display_width = 800
            display_height = 600
            
            img_copy = self.processed_image.copy()
            img_copy.thumbnail((display_width, display_height))
            
            self.display_image = ctk.CTkImage(light_image=img_copy, dark_image=img_copy, size=img_copy.size)
            self.image_display_label.configure(image=self.display_image, text="")
            self.image_display_label.pack(expand=True)
            self.empty_state_frame.place_forget()
        else:
             self.image_display_label.pack_forget()
             self.image_display_label.configure(image=None)
             self.empty_state_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER, relwidth=0.4, relheight=0.4)

    def show_edit_menu(self):
        # Deprecated: Replaced by custom toggle_edit_menu
        pass

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, before=self.content_area)
            self.sidebar_visible = True

if __name__ == "__main__":
    app = Application()
    app.mainloop()

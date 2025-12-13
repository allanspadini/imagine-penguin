import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

class SimpleEditMixin:
    def show_simple_edit_tools(self):
        # Hide standard menu options
        self.processing_btn.pack_forget()
        # self.option3_btn.pack_forget() # option3 removed check design
        self.colors_btn.pack_forget()

        # Clear existing tools in frame if any (optional if we want to toggle back and forth)
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()
            
        self.edit_tools_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(self.edit_tools_frame, text="Edit Options", font=ctk.CTkFont(size=14, slant="italic", family="Comic Sans MS"), text_color="white").pack(pady=(5, 5))
        
        self.styled_button(self.edit_tools_frame, text="Rotate Left 90°", command=lambda: self.rotate_image(90)).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Rotate Right 90°", command=lambda: self.rotate_image(-90)).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Horizontal Flip", command=self.flip_horizontal).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Vertical Flip", command=self.flip_vertical).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Crop", command=self.show_crop_options).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Back", command=self.hide_simple_edit_tools).pack(fill=tk.X, pady=5, padx=30)

    def hide_simple_edit_tools(self):
        self.edit_tools_frame.pack_forget()
        self.simple_edit_btn.pack(fill=tk.X, pady=2, padx=10)
        self.processing_btn.pack(fill=tk.X, pady=2, padx=10)
        self.colors_btn.pack(fill=tk.X, pady=2, padx=10)
    
    def rotate_image(self, angle):
        if self.processed_image:
            self.save_state()
            self.processed_image = self.processed_image.rotate(angle, expand=True)
            self.update_image_display()
        else:
            messagebox.showwarning("Warning", "No image loaded to rotate.")

    def flip_horizontal(self):
        if self.processed_image:
            self.save_state()
            self.processed_image = self.processed_image.transpose(Image.FLIP_LEFT_RIGHT)
            self.update_image_display()
        else:
            messagebox.showwarning("Warning", "No image loaded to flip.")

    def flip_vertical(self):
        if self.processed_image:
            self.save_state()
            self.processed_image = self.processed_image.transpose(Image.FLIP_TOP_BOTTOM)
            self.update_image_display()
        else:
            messagebox.showwarning("Warning", "No image loaded to flip.")

    def show_crop_options(self):
        # Clear existing tools
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.edit_tools_frame, text="Crop Options", font=ctk.CTkFont(size=14, slant="italic", family="Comic Sans MS"), text_color="white").pack(pady=(5, 5))

        # Input for pixels
        self.crop_entry = ctk.CTkEntry(self.edit_tools_frame, placeholder_text="Pixels")
        self.crop_entry.pack(fill=tk.X, pady=5, padx=30)
        
        # Grid layout for directional buttons
        crop_controls = ctk.CTkFrame(self.edit_tools_frame, fg_color="transparent")
        crop_controls.pack(fill=tk.X, padx=30)
        
        # UP
        self.styled_button(crop_controls, text="Top", command=lambda: self.apply_crop("top"), width=60).pack(pady=2)
        
        # Left/Right container
        lr_frame = ctk.CTkFrame(crop_controls, fg_color="transparent")
        lr_frame.pack(pady=2)
        self.styled_button(lr_frame, text="Left", command=lambda: self.apply_crop("left"), width=60).pack(side=tk.LEFT, padx=2)
        self.styled_button(lr_frame, text="Right", command=lambda: self.apply_crop("right"), width=60).pack(side=tk.LEFT, padx=2)
        
        # Down
        self.styled_button(crop_controls, text="Bottom", command=lambda: self.apply_crop("bottom"), width=60).pack(pady=2)

        self.styled_button(self.edit_tools_frame, text="Back", command=self.show_simple_edit_tools).pack(fill=tk.X, pady=10, padx=30)

    def apply_crop(self, side):
        if self.processed_image:
            try:
                pixels = int(self.crop_entry.get())
                if pixels <= 0:
                     raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid positive integer number of pixels.")
                return

            width, height = self.processed_image.size
            left, top, right, bottom = 0, 0, width, height
            
            if side == "left":
                left += pixels
            elif side == "right":
                right -= pixels
            elif side == "top":
                top += pixels
            elif side == "bottom":
                bottom -= pixels
            
            # Validation
            if left >= right or top >= bottom:
                 messagebox.showerror("Error", "Crop too large, resulting image would be empty.")
                 return

            self.save_state()
            self.processed_image = self.processed_image.crop((left, top, right, bottom))
            self.update_image_display()
        else:
            messagebox.showwarning("Warning", "No image loaded to crop.")

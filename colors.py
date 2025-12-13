import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageOps, ImageEnhance

class ColorsMixin:
    def show_colors_tools(self):
        # Hide standard menu options
        self.processing_btn.pack_forget()
        self.simple_edit_btn.pack_forget()
        self.colors_btn.pack_forget()

        # Clear existing tools
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()

        self.edit_tools_frame.pack(fill=tk.X, pady=10)

        ctk.CTkLabel(self.edit_tools_frame, text="Colors", font=ctk.CTkFont(size=14, slant="italic", family="Comic Sans MS"), text_color="white").pack(pady=(5, 5))

        self.styled_button(self.edit_tools_frame, text="Grayscale", command=self.apply_grayscale).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Invert Colors", command=self.apply_invert).pack(fill=tk.X, pady=2, padx=30)
        
        ctk.CTkLabel(self.edit_tools_frame, text="Brightness", text_color="white", font=ctk.CTkFont(size=12, family="Comic Sans MS")).pack(pady=(10, 2))
        self.brightness_slider = ctk.CTkSlider(self.edit_tools_frame, from_=0.1, to=2.0, number_of_steps=19, command=self.adjust_brightness)
        self.brightness_slider.set(1.0)
        self.brightness_slider.pack(fill=tk.X, padx=30)
        
        ctk.CTkLabel(self.edit_tools_frame, text="Contrast", text_color="white", font=ctk.CTkFont(size=12, family="Comic Sans MS")).pack(pady=(10, 2))
        self.contrast_slider = ctk.CTkSlider(self.edit_tools_frame, from_=0.1, to=2.0, number_of_steps=19, command=self.adjust_contrast)
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X, padx=30)
        
        ctk.CTkButton(self.edit_tools_frame,corner_radius=0, text="Apply Adjustments", command=self.apply_adjustments, fg_color=self.accent_color, hover_color="#C2185B", height=30).pack(fill=tk.X, pady=10, padx=30)

        self.styled_button(self.edit_tools_frame, text="Back", command=self.hide_simple_edit_tools).pack(fill=tk.X, pady=5, padx=30)

    def apply_grayscale(self):
        if self.processed_image:
            self.save_state()
            self.processed_image = ImageOps.grayscale(self.processed_image)
            # Grayscale converts to 'L' mode, but ctk image might want RGB.
            # Convert back to RGB for consistency in display and further processing
            self.processed_image = self.processed_image.convert("RGB")
            self.update_image_display()
        else:
             messagebox.showwarning("Warning", "No image loaded.")

    def apply_invert(self):
        if self.processed_image:
            self.save_state()
            # Invert requires RGB or L usually, ensure it is.
            if self.processed_image.mode == 'RGBA':
                 # Separate alpha, invert rgb, recombine
                 r, g, b, a = self.processed_image.split()
                 rgb_image = Image.merge('RGB', (r, g, b))
                 inverted_image = ImageOps.invert(rgb_image)
                 r2, g2, b2 = inverted_image.split()
                 self.processed_image = Image.merge('RGBA', (r2, g2, b2, a))
            else:
                 self.processed_image = ImageOps.invert(self.processed_image)
            self.update_image_display()
        else:
             messagebox.showwarning("Warning", "No image loaded.")
             
    def adjust_brightness(self, value):
        pass 
        
    def adjust_contrast(self, value):
        pass

    def apply_adjustments(self):
        if self.processed_image:
            self.save_state()
            
            # Apply Brightness
            enhancer = ImageEnhance.Brightness(self.processed_image)
            self.processed_image = enhancer.enhance(self.brightness_slider.get())
            
            # Apply Contrast
            enhancer = ImageEnhance.Contrast(self.processed_image)
            self.processed_image = enhancer.enhance(self.contrast_slider.get())
            
            self.update_image_display()
            
            # Reset sliders to 1.0 (neutral) after apply? Or keep them?
            # Keeping them might apply 2x effect if clicked again. Resetting is safer.
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
        else:
             messagebox.showwarning("Warning", "No image loaded.")

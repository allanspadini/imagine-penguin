import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageFilter, ImageEnhance
import cv2
import numpy as np
import threading

class ProcessingMixin:
    def show_processing_tools(self):
        # Hide standard menu options
        self.processing_btn.pack_forget()
        # self.option3_btn.pack_forget()
        self.simple_edit_btn.pack_forget()
        self.colors_btn.pack_forget()

        # Clear existing tools
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()
            
        self.edit_tools_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(self.edit_tools_frame, text="Processing", font=ctk.CTkFont(size=14, slant="italic", family="Comic Sans MS"), text_color="white").pack(pady=(5, 5))

        self.styled_button(self.edit_tools_frame, text="Remove Background", command=self.remove_background).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Blur Background", command=self.blur_background).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Sharpen", command=self.apply_sharpen).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Upscale 2x", command=self.apply_upscale).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Back", command=self.hide_simple_edit_tools).pack(fill=tk.X, pady=5, padx=30)

    def show_loading(self):
        self.image_display_label.pack_forget()
        self.empty_state_frame.place_forget()
        self.loading_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    def hide_loading(self):
        self.loading_frame.place_forget()
        self.image_display_label.pack(expand=True)
    
    def remove_background(self):
        if self.processed_image:
            self.save_state()
            self.show_loading()
            # Run in a separate thread to keep UI responsive
            threading.Thread(target=self._remove_background_cv_thread, daemon=True).start()
        else:
             messagebox.showwarning("Warning", "No image loaded.")

    def _remove_background_cv_thread(self):
        try:
             # Convert PIL image to OpenCV format
            img_np = np.array(self.processed_image)
            
            # Handle RGBA images by converting to RGB for grabCut
            if img_np.shape[2] == 4:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
            else:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
            
            # Initial mask
            mask = np.zeros(img_bgr.shape[:2], np.uint8)
            
            # Arrays needed for grabCut
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            
            # Define a rectangle for initialization (margin of 10 pixels seems safe)
            height, width = img_bgr.shape[:2]
            rect = (10, 10, width - 20, height - 20)
            
            # Run grapCut
            cv2.grabCut(img_bgr, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)
            
            # Modify mask where 0 and 2 are background, 1 and 3 are foreground
            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype("uint8")
            
            # Apply mask to image
            img_bgr = img_bgr * mask2[:, :, np.newaxis]
            
            # Create alpha channel from mask
            alpha = (mask2 * 255).astype("uint8")
            
            # Merge RGB and Alpha
            b, g, r = cv2.split(img_bgr)
            rgba = [b, g, r, alpha]
            result = cv2.merge(rgba, 4)
            
            # Convert back to PIL Image (RGB mode)
            result = cv2.cvtColor(result, cv2.COLOR_BGRA2RGBA)
            result_image = Image.fromarray(result)
            
            # Update UI on main thread
            self.after(0, self._finish_background_removal, result_image)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to remove background: {e}"))
            self.after(0, self.hide_loading)

    def _finish_background_removal(self, result_image):
        self.processed_image = result_image
        self.update_image_display()
        self.hide_loading()
        # No message box as requested

    def blur_background(self):
        if self.processed_image:
            self.save_state()
            self.show_loading()
            threading.Thread(target=self._blur_background_thread, daemon=True).start()
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def _blur_background_thread(self):
        try:
            # Convert PIL image to OpenCV format
            img_np = np.array(self.processed_image)
             # Handle RGBA images by converting to RGB for grabCut
            if img_np.shape[2] == 4:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGBA2BGR)
            else:
                img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

            # Initialize mask and bg/fg models
            mask = np.zeros(img_bgr.shape[:2], np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)

            # Simply define a rectangle leaving a small border
            height, width = img_bgr.shape[:2]
            rect = (10, 10, width - 20, height - 20)

            # Run GrabCut
            cv2.grabCut(img_bgr, mask, rect, bgdModel, fgdModel, 5, cv2.GC_INIT_WITH_RECT)

            # Create mask where 0 and 2 are background (0), 1 and 3 are foreground (1)
            # We want to blur background, so we need a mask for the background
            mask2 = np.where((mask == 2) | (mask == 0), 1, 0).astype("uint8") # 1 where bg, 0 where fg
            
            # --- Processing using PIL ---
            # Create a blurred version of the original image
            original_pil = self.processed_image.convert("RGB")
            blurred_pil = original_pil.filter(ImageFilter.GaussianBlur(radius=10))
            
            # Convert mask to PIL Image (L mode)
            mask_pil = Image.fromarray(mask2 * 255).convert("L")
            
            # Composite: Paste blurred image onto original using the background mask
            result_image = Image.composite(blurred_pil, original_pil, mask_pil)
            
            # Update UI on main thread
            self.after(0, self._finish_background_removal, result_image) # reuse finish callback

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Failed to blur background: {e}"))
            self.after(0, self.hide_loading)

    def apply_sharpen(self):
        if self.processed_image:
            self.save_state()
            self.show_loading()
            threading.Thread(target=self._apply_sharpen_thread, daemon=True).start()
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def _apply_sharpen_thread(self):
        try:
            enhancer = ImageEnhance.Sharpness(self.processed_image)
            # Default factor 2.0 for visible sharpening
            result_image = enhancer.enhance(2.0)
            self.after(0, self._finish_processing, result_image)
        except Exception as e:
             self.after(0, lambda: messagebox.showerror("Error", f"Failed to sharpen: {e}"))
             self.after(0, self.hide_loading)

    def apply_upscale(self, scale=2.0):
        if self.processed_image:
            self.save_state()
            self.show_loading()
            threading.Thread(target=self._apply_upscale_thread, args=(scale,), daemon=True).start()
        else:
            messagebox.showwarning("Warning", "No image loaded.")

    def _apply_upscale_thread(self, scale):
        try:
            # PIL -> OpenCV (RGB -> BGR)
            # Handle RGBA images by converting to RGB first
            img_pil = self.processed_image.convert("RGB")
            img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

            h, w = img.shape[:2]
            new_size = (int(w * scale), int(h * scale))

            # Upscale with Lanczos
            img = cv2.resize(img, new_size, interpolation=cv2.INTER_LANCZOS4)

            # Apply Unsharp Mask
            img = self._unsharp_mask_cv2(img, amount=1.0, radius=1.2)

            # OpenCV -> PIL (BGR -> RGB)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            result_image = Image.fromarray(img)

            self.after(0, self._finish_processing, result_image)
        except Exception as e:
             self.after(0, lambda: messagebox.showerror("Error", f"Failed to upscale: {e}"))
             self.after(0, self.hide_loading)
            
    def _finish_processing(self, result_image):
        self.processed_image = result_image
        self.update_image_display()
        self.hide_loading()

    def _unsharp_mask_cv2(self, image, amount=1.2, radius=1.0):
        blurred = cv2.GaussianBlur(image, (0, 0), radius)
        sharpened = cv2.addWeighted(image, 1 + amount, blurred, -amount, 0)
        return sharpened

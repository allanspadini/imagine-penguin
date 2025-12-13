import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import threading
import base64
from io import BytesIO
from openai import OpenAI
import json
import requests
from PIL import Image

class AiToolsMixin:
    def show_ai_tools(self):
        # Hide other menu options
        self.processing_btn.pack_forget()
        self.simple_edit_btn.pack_forget()
        self.colors_btn.pack_forget()
        if hasattr(self, 'ai_btn'):
             self.ai_btn.pack_forget()

        # Clear existing tools
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()
            
        self.edit_tools_frame.pack(fill=tk.X, pady=10)
        
        ctk.CTkLabel(self.edit_tools_frame, text="AI Tools", font=ctk.CTkFont(size=14, slant="italic", family="Comic Sans MS"), text_color="white").pack(pady=(5, 5))

        self.styled_button(self.edit_tools_frame, text="Imagine to Json", command=self.show_imagine_to_json).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Image Generation", command=self.show_image_generation).pack(fill=tk.X, pady=2, padx=30)
        self.styled_button(self.edit_tools_frame, text="Back", command=self.hide_ai_tools).pack(fill=tk.X, pady=5, padx=30)

    def hide_ai_tools(self):
        self.edit_tools_frame.pack_forget()
        self.simple_edit_btn.pack(fill=tk.X, pady=2, padx=10)
        self.processing_btn.pack(fill=tk.X, pady=2, padx=10)
        self.colors_btn.pack(fill=tk.X, pady=2, padx=10)
        if hasattr(self, 'ai_btn'):
            self.ai_btn.pack(fill=tk.X, pady=2, padx=10)

    def show_imagine_to_json(self):
        # Clear existing tools to show the form
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.edit_tools_frame, text="Imagine to Json", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(pady=5)

        # API Key Input
        ctk.CTkLabel(self.edit_tools_frame, text="OpenRouter API Key:", font=ctk.CTkFont(size=10)).pack(pady=(5,0), padx=20, anchor="w")
        self.api_key_entry = ctk.CTkEntry(self.edit_tools_frame, show="*", placeholder_text="sk-or-...")
        self.api_key_entry.pack(fill=tk.X, padx=20, pady=5)

        # Model Selection
        ctk.CTkLabel(self.edit_tools_frame, text="Model:", font=ctk.CTkFont(size=10)).pack(pady=(5,0), padx=20, anchor="w")
        self.model_var = ctk.StringVar(value="nvidia/nemotron-nano-12b-v2-vl:free")
        models = [
            "https://openrouter.ai/openai/gpt-5.2-pro",
            "nvidia/nemotron-nano-12b-v2-vl:free",
            "anthropic/claude-haiku-4.5",
            "google/gemini-3-pro-preview",
            "z-ai/glm-4.6v",
            "openai/gpt-5.2-pro"
        ]
        self.model_dropdown = ctk.CTkOptionMenu(self.edit_tools_frame, variable=self.model_var, values=models)
        self.model_dropdown.pack(fill=tk.X, padx=20, pady=5)

        # Generate Button
        self.styled_button(self.edit_tools_frame, text="Generate JSON", command=self.start_generation, fg_color="#2196F3", hover_color="#1976D2").pack(fill=tk.X, pady=10, padx=20)
        
        # Output Area (Textbox)
        self.json_output = ctk.CTkTextbox(self.edit_tools_frame, height=200, font=("Consolas", 10))
        self.json_output.pack(fill=tk.X, padx=10, pady=5)

        self.styled_button(self.edit_tools_frame, text="Copy JSON", command=self.copy_to_clipboard, fg_color="#333333").pack(fill=tk.X, pady=2, padx=20)
        self.styled_button(self.edit_tools_frame, text="Back", command=self.show_ai_tools).pack(fill=tk.X, pady=5, padx=30)

    def copy_to_clipboard(self):
        text = self.json_output.get("1.0", tk.END).strip()
        if text:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.update() # Required to finalize clipboard update
            messagebox.showinfo("Copied", "JSON copied to clipboard!")
        else:
            messagebox.showwarning("Empty", "Nothing to copy.")

    def start_generation(self):
        if not self.processed_image:
            messagebox.showwarning("Warning", "No image loaded.")
            return

        api_key = self.api_key_entry.get().strip()
        if not api_key:
             messagebox.showwarning("Warning", "Please enter your OpenRouter API Key.")
             return

        self.show_loading()
        threading.Thread(target=self._generate_description_thread, args=(api_key,), daemon=True).start()

    def _generate_description_thread(self, api_key):
        try:
            # Encode image to base64
            buffered = BytesIO()
            # Convert to RGB if needed (JPEG doesn't support RGBA)
            img_to_send = self.processed_image.convert("RGB")
            img_to_send.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            base64_image = f"data:image/jpeg;base64,{img_str}"

            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )

            completion = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://imagine-penguin.app", # Placeholder
                    "X-Title": "Imagine Penguin",
                },
                extra_body={},
                model=self.model_var.get(),
                messages=[
                    {
                    "role": "user",
                    "content": [
                        {
                        "type": "text",
                        "text": "Analyze this image and provide a detailed description in JSON format. The JSON should have keys like 'subject', 'colors', 'mood', 'details'."
                        },
                        {
                        "type": "image_url",
                        "image_url": {
                            "url": base64_image
                        }
                        }
                    ]
                    }
                ]
            )
            
            result = completion.choices[0].message.content
            self.after(0, self._display_result, result)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"AI Generation failed: {e}"))
            self.after(0, self.hide_loading)

    def _display_result(self, result):
        self.json_output.delete("1.0", tk.END)
        self.json_output.insert("1.0", result)
        self.hide_loading()

    def show_image_generation(self):
        # Clear existing tools
        for widget in self.edit_tools_frame.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.edit_tools_frame, text="Image Generation", font=ctk.CTkFont(size=12, weight="bold"), text_color="white").pack(pady=5)

        # API Key Input
        ctk.CTkLabel(self.edit_tools_frame, text="OpenRouter API Key:", font=ctk.CTkFont(size=10)).pack(pady=(5,0), padx=20, anchor="w")
        self.api_key_entry = ctk.CTkEntry(self.edit_tools_frame, show="*", placeholder_text="sk-or-...")
        self.api_key_entry.pack(fill=tk.X, padx=20, pady=5)

        # Model Selection
        ctk.CTkLabel(self.edit_tools_frame, text="Model:", font=ctk.CTkFont(size=10)).pack(pady=(5,0), padx=20, anchor="w")
        self.model_var = ctk.StringVar(value="black-forest-labs/flux.2-pro")
        models = [
            "black-forest-labs/flux.2-pro",
            "black-forest-labs/flux.2-flex",
            "google/gemini-3-pro-image-preview",
            "openai/gpt-5-image",
            "google/gemini-2.5-flash-image"
        ]
        self.model_dropdown = ctk.CTkOptionMenu(self.edit_tools_frame, variable=self.model_var, values=models)
        self.model_dropdown.pack(fill=tk.X, padx=20, pady=5)

        # Prompt Input
        ctk.CTkLabel(self.edit_tools_frame, text="Prompt:", font=ctk.CTkFont(size=10)).pack(pady=(5,0), padx=20, anchor="w")
        self.prompt_entry = ctk.CTkTextbox(self.edit_tools_frame, height=100, font=("Consolas", 10))
        self.prompt_entry.pack(fill=tk.X, padx=20, pady=5)

        # Generate Button
        self.styled_button(self.edit_tools_frame, text="Generate Image", command=self.start_image_generation, fg_color="#E91E63", hover_color="#C2185B").pack(fill=tk.X, pady=10, padx=20)
        
        self.styled_button(self.edit_tools_frame, text="Back", command=self.show_ai_tools).pack(fill=tk.X, pady=5, padx=30)

    def start_image_generation(self):
        api_key = self.api_key_entry.get().strip()
        prompt = self.prompt_entry.get("1.0", tk.END).strip()

        if not api_key:
             messagebox.showwarning("Warning", "Please enter your OpenRouter API Key.")
             return
        
        if not prompt:
             messagebox.showwarning("Warning", "Please enter a prompt.")
             return

        self.show_loading()
        threading.Thread(target=self._generate_image_thread, args=(api_key, prompt), daemon=True).start()

    def _generate_image_thread(self, api_key, prompt):
        try:
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )

            # OpenRouter uses chat/completions for image generation models
            response = client.chat.completions.create(
                model=self.model_var.get(),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                extra_headers={
                    "HTTP-Referer": "https://imagine-penguin.app",
                    "X-Title": "Imagine Penguin",
                },
                # Some models/endpoints might require this, or just benefit from it
                # extra_body={"modalities": ["image"]} 
            )
            
            # The URL is returned in the content of the message
            image_url = response.choices[0].message.content
            
            # Basic cleanup if it returns markdown
            if image_url.startswith("![") and "](" in image_url:
                 # Extract URL from markdown image syntax ![alt](url)
                 image_url = image_url.split("](")[1][:-1]
            
            # Ensure we have a valid URL string (sometimes it might be extra text, but for Flux usually just URL)
            # If it contains spaces or newlines, take the first token that looks like a URL?
            # For now, assume it's clean or standard markdown.
            
            # Download the image
            img_data = requests.get(image_url).content
            img = Image.open(BytesIO(img_data))
            
            self.after(0, self._finish_image_generation, img)

        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Image Generation failed: {e}"))
            self.after(0, self.hide_loading)

    def _finish_image_generation(self, img):
        self.processed_image = img
        self.save_state() # Save for undo
        self.update_image_display()
        self.hide_loading()

# 🐧 Imagine Penguin

<p align="center">
  <img src="icon.png" alt="Imagine Penguin Icon" width="200"/>
</p>

**Imagine Penguin** is a powerful and intuitive image editing application built with Python and CustomTkinter. It combines classic image processing tools with advanced AI capabilities to help you create, edit, and analyze images with ease.

## ✨ Features

### 🛠️ Classic Processing
- **Remove Background**: Intelligent background removal using computer vision (GrabCut).
- **Blur Background**: Apply aesthetic blur to the background while keeping the subject in focus.
- **Upscale 2x**: High-quality resolution upscale (Lanczos + Unsharp Mask) without AI artifacts.
- **Sharpening**: Instantly improve detail sharpness.

### 🤖 AI Tools (Via OpenRouter)
- **Imagine to JSON**: Get detailed descriptions of your images (subject, mood, colors) in JSON format.
- **Image Generation**: Create amazing images from text using models like **Flux**, **Gemini**, and **GPT-5**.

### 🎨 Simple Edit & Colors
- Basic adjustment tools and color manipulation.

## 🚀 How to Use

### Prerequisites
- Python 3.11+
- `uv` package manager

### Installation

```bash
# Clone the repository
git clone https://github.com/allanspadini/imagine-penguin.git
cd imagine-penguin

# Install dependencies
uv sync
```

### Running

```bash
uv run main.py
```

## 🛠️ Technologies
- **CustomTkinter**: Modern and responsive interface.
- **OpenCV & PIL**: Image processing engines.
- **OpenAI SDK**: Integration with OpenRouter for AI features.

import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import fitz  # PyMuPDF
import threading
import os
import re
import base64
import json
from datetime import datetime
import warnings
from io import BytesIO
from PIL import Image, ImageTk

# --- COMPLIANCE FIX: REMOVED REQUESTS/OPENROUTER ---
# We now use the official Groq client for EVERYTHING.
from groq import Groq 

# Hide deprecation warnings
warnings.filterwarnings("ignore")

class SmartPDFAnalyzer:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart PDF Analyzer - COMPETITION EDITION (GROQ NATIVE)")
        self.root.geometry("1400x900")
        
        # Data storage
        self.pdf_data = []
        self.current_pdf = None
        self.current_page = 0
        self.total_pages = 0
        self.all_text = ""
        self.images_data = []  
        self.current_image_index = 0
        self.image_descriptions = {} 
        
        # --- API CONFIGURATION (COMPLIANT) ---
        # 1. We removed OpenRouter Key (Banned)
        # 2. We allow setting Groq Key via Environment Variable or GUI
        self.groq_api_key = os.getenv("GROQ_API_KEY", "") 
        
        # Initialize APIs
        self.groq_client = None
        
        # --- COMPLIANCE FIX: ALLOWED MODELS ONLY ---
        # Removed GPT-4o, Claude, Qwen (via OpenRouter).
        # Added ONLY Groq-hosted Vision models.
        self.image_models = [
            "llama-3.2-11b-vision-preview", # Native Groq Vision
            "llama-3.2-90b-vision-preview"  # Native Groq Vision (High Res)
        ]
        self.selected_image_model = tk.StringVar(value=self.image_models[0])
        
        # Colors
        self.colors = {
            'bg': '#1e1e1e', 'fg': '#ffffff', 'accent': '#4CAF50',
            'secondary': '#2196F3', 'warning': '#FF9800', 'card_bg': '#2d2d2d',
            'text_bg': '#252525', 'highlight': '#3e3e42', 'image_bg': '#1a1a2e',
            'scrollbar_bg': '#3e3e42', 'scrollbar_trough': '#2d2d2d'
        }
        
        self.root.configure(bg=self.colors['bg'])
        self.create_gui()
        
        # Try auto-connect if env var exists
        if self.groq_api_key:
            self.setup_groq()
    
    def setup_groq(self):
        """Setup Groq API (Native Client)"""
        try:
            if not self.groq_api_key:
                # If key is empty, try to get from user input if available
                if hasattr(self, 'api_key_entry'):
                    self.groq_api_key = self.api_key_entry.get().strip()
                
            if not self.groq_api_key:
                print("⚠️ Groq API key not set.")
                self.groq_status = "Not configured"
                self.update_groq_status()
                return False
            
            self.groq_client = Groq(api_key=self.groq_api_key)
            
            # Quick test
            test_response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            
            if test_response:
                print("✅ Groq API configured successfully!")
                self.groq_status = "Connected"
                self.update_groq_status()
                return True
                
        except Exception as e:
            print(f"⚠️ Groq setup failed: {e}")
            self.groq_status = "Connection Failed"
            self.update_groq_status()
            return False
        
        return False
    
    def create_gui(self):
        # ... (GUI Layout code remains mostly the same, simplified for brevity) ...
        # [Keeping your exact layout logic to ensure UI doesn't break]
        
        self.main_container = tk.Frame(self.root, bg=self.colors['bg'])
        self.main_container.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(self.main_container, bg=self.colors['bg'], highlightthickness=0)
        self.canvas.pack(side='left', fill='both', expand=True)
        
        self.scrollbar = tk.Scrollbar(self.main_container, orient='vertical', command=self.canvas.yview, bg=self.colors['scrollbar_bg'])
        self.scrollbar.pack(side='right', fill='y')
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw', width=1380)
        
        self.scrollable_frame.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame, width=e.width))
        
        content_container = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
        content_container.pack(fill='both', expand=True, padx=15, pady=10)
        
        # LEFT PANEL
        left_panel = tk.Frame(content_container, bg=self.colors['bg'], width=320)
        left_panel.pack(side='left', fill='y')
        left_panel.pack_propagate(False)
        
        # Title
        tk.Label(left_panel, text="🚀 PDF ANALYZER PRO", font=('Arial', 16, 'bold'), bg=self.colors['bg'], fg=self.colors['accent']).pack(pady=(0,5))
        
        # API Key Input (New: For safety during demo)
        api_frame = tk.LabelFrame(left_panel, text="🔑 API CONFIG", bg=self.colors['card_bg'], fg=self.colors['fg'])
        api_frame.pack(fill='x', pady=5)
        self.api_key_entry = tk.Entry(api_frame, show="*", bg=self.colors['text_bg'], fg='white')
        self.api_key_entry.pack(fill='x', padx=5, pady=5)
        if self.groq_api_key: self.api_key_entry.insert(0, self.groq_api_key)
        tk.Button(api_frame, text="Update Key", command=self.setup_groq, bg=self.colors['accent'], fg='white').pack(pady=5)

        # File Selection
        file_frame = tk.LabelFrame(left_panel, text="📂 PDF", bg=self.colors['card_bg'], fg=self.colors['fg'])
        file_frame.pack(fill='x', pady=5)
        self.pdf_label = tk.Label(file_frame, text="No PDF", bg=self.colors['card_bg'], fg=self.colors['warning'])
        self.pdf_label.pack(pady=5)
        tk.Button(file_frame, text="Browse", command=self.browse_pdf, bg=self.colors['secondary'], fg='white').pack(pady=5)
        
        # Image Analysis
        img_frame = tk.LabelFrame(left_panel, text="🖼️ VISION AI", bg=self.colors['card_bg'], fg=self.colors['fg'])
        img_frame.pack(fill='x', pady=5)
        
        tk.Label(img_frame, text="Groq Vision Model:", bg=self.colors['card_bg'], fg='white').pack(anchor='w', padx=5)
        self.image_model_dropdown = ttk.Combobox(img_frame, textvariable=self.selected_image_model, values=self.image_models, state="readonly")
        self.image_model_dropdown.pack(fill='x', padx=5, pady=5)
        
        self.analyze_images_btn = tk.Button(img_frame, text="Analyze Images", command=self.analyze_images, bg=self.colors['accent'], fg='white', state='disabled')
        self.analyze_images_btn.pack(fill='x', padx=5, pady=5)
        
        # AI Mode
        ai_frame = tk.LabelFrame(left_panel, text="🤖 MODE", bg=self.colors['card_bg'], fg=self.colors['fg'])
        ai_frame.pack(fill='x', pady=5)
        self.ai_mode = tk.StringVar(value="smart")
        tk.Radiobutton(ai_frame, text="Smart (Groq)", variable=self.ai_mode, value="smart", bg=self.colors['card_bg'], fg='white', selectcolor=self.colors['bg']).pack(anchor='w')
        tk.Radiobutton(ai_frame, text="Fast (Rules)", variable=self.ai_mode, value="fast", bg=self.colors['card_bg'], fg='white', selectcolor=self.colors['bg']).pack(anchor='w')
        self.groq_status_label = tk.Label(ai_frame, text="Groq: Checking...", bg=self.colors['card_bg'], fg='white')
        self.groq_status_label.pack()

        # Processing
        tk.Button(left_panel, text="▶ START ANALYSIS", command=self.start_analysis, bg=self.colors['accent'], fg='white', font=('Arial', 10, 'bold')).pack(pady=10, fill='x')
        
        # Progress
        self.status_label = tk.Label(left_panel, text="Ready", bg=self.colors['bg'], fg='white')
        self.status_label.pack()
        self.progress = ttk.Progressbar(left_panel)
        self.progress.pack(fill='x', pady=5)

        # RIGHT PANEL
        right_panel = tk.Frame(content_container, bg=self.colors['bg'])
        right_panel.pack(side='right', fill='both', expand=True)
        
        # Navigation
        nav_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        nav_frame.pack(fill='x')
        self.prev_btn = tk.Button(nav_frame, text="◀", command=self.prev_page, state='disabled')
        self.prev_btn.pack(side='left')
        self.page_label = tk.Label(nav_frame, text="Page 0/0", bg=self.colors['bg'], fg='white', font=('Arial', 12))
        self.page_label.pack(side='left', padx=20)
        self.next_btn = tk.Button(nav_frame, text="▶", command=self.next_page, state='disabled')
        self.next_btn.pack(side='left')
        
        # Content Split
        split_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        split_frame.pack(fill='both', expand=True, pady=5)
        
        # Text
        text_f = tk.LabelFrame(split_frame, text="Text", bg=self.colors['card_bg'], fg='white')
        text_f.pack(side='left', fill='both', expand=True)
        self.text_display = scrolledtext.ScrolledText(text_f, height=15, bg=self.colors['text_bg'], fg='white')
        self.text_display.pack(fill='both', expand=True)
        
        # Image
        img_f = tk.LabelFrame(split_frame, text="Image", bg=self.colors['card_bg'], fg='white')
        img_f.pack(side='right', fill='both', expand=True)
        self.image_canvas = tk.Canvas(img_f, bg=self.colors['image_bg'])
        self.image_canvas.pack(fill='both', expand=True)
        
        # Analysis Text Boxes
        data_frame = tk.Frame(right_panel, bg=self.colors['bg'])
        data_frame.pack(fill='x', pady=5)
        
        self.entity_text = scrolledtext.ScrolledText(data_frame, height=5, bg=self.colors['text_bg'], fg='white')
        self.entity_text.pack(side='left', fill='both', expand=True, padx=2)
        self.keyword_text = scrolledtext.ScrolledText(data_frame, height=5, bg=self.colors['text_bg'], fg='white')
        self.keyword_text.pack(side='left', fill='both', expand=True, padx=2)
        
        # Q&A
        qa_frame = tk.LabelFrame(right_panel, text="❓ ASK GROQ", bg=self.colors['card_bg'], fg='white')
        qa_frame.pack(fill='x', pady=5)
        
        q_input = tk.Frame(qa_frame, bg=self.colors['card_bg'])
        q_input.pack(fill='x')
        self.search_entry = tk.Entry(q_input, bg=self.colors['text_bg'], fg='white')
        self.search_entry.pack(side='left', fill='x', expand=True)
        self.search_entry.bind('<Return>', lambda e: self.ask_question())
        tk.Button(q_input, text="ASK", command=self.ask_question, bg=self.colors['accent'], fg='white').pack(side='right')
        
        self.answer_text = scrolledtext.ScrolledText(qa_frame, height=8, bg=self.colors['text_bg'], fg='white')
        self.answer_text.pack(fill='x')

        self.root.after(100, self.update_groq_status)

    # --- CORE FUNCTIONS ---

    def browse_pdf(self):
        filepath = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
        if filepath:
            self.current_pdf = filepath
            self.pdf_label.config(text=os.path.basename(filepath))
            self.analyze_images_btn.config(state='normal')
            
            doc = fitz.open(filepath)
            self.total_pages = len(doc)
            doc.close()
            self.page_label.config(text=f"Page 1/{self.total_pages}")
            self.extract_images_from_pdf(filepath)

    def extract_images_from_pdf(self, pdf_path):
        self.images_data = []
        try:
            doc = fitz.open(pdf_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    pil_image = Image.open(BytesIO(base_image["image"]))
                    if pil_image.mode != 'RGB': pil_image = pil_image.convert('RGB')
                    
                    self.images_data.append({
                        'page': page_num + 1, 'image': pil_image, 'description': None
                    })
            doc.close()
            self.status_label.config(text=f"Images Found: {len(self.images_data)}")
            if self.images_data: self.show_current_image()
        except Exception as e:
            print(f"Img Error: {e}")

    def analyze_images(self):
        if not self.images_data: return
        self.status_label.config(text="Analyzing Images via Groq Vision...")
        self.progress['value'] = 0
        self.analyze_images_btn.config(state='disabled')
        threading.Thread(target=self.analyze_images_thread, daemon=True).start()

    def analyze_images_thread(self):
        total = len(self.images_data)
        for idx, img_data in enumerate(self.images_data):
            # --- COMPLIANCE FIX: USING GROQ NATIVE VISION ---
            desc = self.analyze_single_image_groq(img_data['image'])
            self.images_data[idx]['description'] = desc
            self.root.after(0, self.update_progress, ((idx+1)/total)*100, f"Analyzed Image {idx+1}/{total}")
        
        self.root.after(0, self.analysis_complete_img)

    def analyze_single_image_groq(self, pil_image):
        """
        COMPLIANCE: Uses self.groq_client (Groq) with Llama 3.2 Vision.
        NO OpenRouter. NO Requests.
        """
        if not self.groq_client: return "Groq not connected."
        
        try:
            # Encode image
            buffered = BytesIO()
            pil_image.save(buffered, format="JPEG")
            base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            # Call Groq API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Describe this image in detail for a forensic report."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                },
                            },
                        ],
                    }
                ],
                model=self.selected_image_model.get(),
                temperature=0.1,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Groq Vision Error: {e}"

    def start_analysis(self):
        if not self.current_pdf: return
        self.status_label.config(text="Extracting Text...")
        self.progress['value'] = 0
        threading.Thread(target=self.analyze_pdf_thread, daemon=True).start()

    def analyze_pdf_thread(self):
        doc = fitz.open(self.current_pdf)
        self.pdf_data = []
        self.all_text = ""
        
        for i in range(len(doc)):
            page = doc.load_page(i)
            text = page.get_text()
            self.all_text += f"\nPAGE {i+1}:\n{text}"
            
            # Analyze text with Groq (Llama 3)
            analysis = self.analyze_text_groq(text)
            self.pdf_data.append({'page': i+1, 'text': text, 'analysis': analysis})
            
            self.root.after(0, self.update_progress, ((i+1)/len(doc))*100, f"Read Page {i+1}")
            
        doc.close()
        self.root.after(0, self.load_page, 0)
        self.root.after(0, lambda: self.status_label.config(text="PDF Text Analysis Complete"))

    def analyze_text_groq(self, text):
        if not self.groq_client: return {"entities": [], "keywords": []}
        try:
            # Simplified prompt for speed
            resp = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "Return JSON: {entities: [], keywords: []}"},
                    {"role": "user", "content": f"Analyze:\n{text[:2000]}"}
                ],
                response_format={"type": "json_object"} # Groq JSON mode
            )
            return json.loads(resp.choices[0].message.content)
        except:
            return {"entities": [], "keywords": []}

    def ask_question(self):
        q = self.search_entry.get()
        if not q or not self.groq_client: return
        
        self.answer_text.delete('1.0', tk.END)
        self.answer_text.insert('1.0', "Thinking...")
        
        try:
            # Combine Text + Image Desc
            context = self.all_text[:10000]
            for img in self.images_data:
                if img['description']:
                    context += f"\n[IMAGE on Page {img['page']}]: {img['description']}"
            
            resp = self.groq_client.chat.completions.create(
                model="llama-3.1-70b-versatile", # Stronger model for Q&A
                messages=[
                    {"role": "system", "content": "You are a forensic document analyst. Answer based on the text and images provided."},
                    {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {q}"}
                ]
            )
            self.answer_text.delete('1.0', tk.END)
            self.answer_text.insert('1.0', resp.choices[0].message.content)
        except Exception as e:
            self.answer_text.insert('1.0', f"Error: {e}")

    # --- UTILS ---
    def update_progress(self, val, txt):
        self.progress['value'] = val
        self.status_label.config(text=txt)
    
    def update_groq_status(self):
        txt = "✅ Connected" if self.groq_client else "❌ Disconnected"
        self.groq_status_label.config(text=f"Groq: {txt}")

    def analysis_complete_img(self):
        self.status_label.config(text="Vision Analysis Complete")
        self.analyze_images_btn.config(state='normal')
        if self.images_data: self.show_current_image()

    def show_current_image(self):
        if not self.images_data: return
        img_data = self.images_data[self.current_image_index]
        
        # Resize for canvas
        cw, ch = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        if cw < 10: cw, ch = 300, 300
        
        img = img_data['image'].copy()
        img.thumbnail((cw, ch))
        self.tk_img = ImageTk.PhotoImage(img) # Keep ref
        
        self.image_canvas.delete("all")
        self.image_canvas.create_image(cw//2, ch//2, image=self.tk_img, anchor='center')
        
        # Show description in Q&A area temporarily or dedicated area
        if img_data['description']:
            self.answer_text.delete('1.0', tk.END)
            self.answer_text.insert('1.0', f"IMAGE {self.current_image_index+1} ANALYSIS:\n{img_data['description']}")

    def load_page(self, idx):
        if not self.pdf_data: return
        data = self.pdf_data[idx]
        self.text_display.delete('1.0', tk.END)
        self.text_display.insert('1.0', data['text'])
        
        self.entity_text.delete('1.0', tk.END)
        self.entity_text.insert('1.0', str(data['analysis'].get('entities', '')))
        
        self.keyword_text.delete('1.0', tk.END)
        self.keyword_text.insert('1.0', str(data['analysis'].get('keywords', '')))
        
        self.page_label.config(text=f"Page {idx+1}/{len(self.pdf_data)}")
        self.prev_btn.config(state='normal' if idx > 0 else 'disabled')
        self.next_btn.config(state='normal' if idx < len(self.pdf_data)-1 else 'disabled')
        self.current_page = idx

    def prev_page(self): self.load_page(self.current_page - 1)
    def next_page(self): self.load_page(self.current_page + 1)

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartPDFAnalyzer(root)
    root.mainloop()
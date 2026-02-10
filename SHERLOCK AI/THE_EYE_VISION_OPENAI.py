import os
import fitz  # PyMuPDF
import base64
from io import BytesIO
from PIL import Image
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class VisionAnalyzer:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = None
        if self.api_key:
            try:
                self.client = Groq(api_key=self.api_key)
            except: pass
        
        # Groq's Native Vision Model
        self.model = "llama-3.2-11b-vision-preview"

    def encode_image(self, pil_image):
        """Converts PIL image to Base64"""
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def analyze_visual(self, pil_image, context="generic"):
        """
        Sends image to Groq Vision. 
        Uses 'context' to tell the AI what to look for.
        """
        if not self.client: return "❌ Groq API Not Connected"

        base64_img = self.encode_image(pil_image)
        
        # --- PROMPT LOGIC ---
        # We tailor the instruction based on what we think the image is
        base_instruction = "Analyze this image for a forensic investigation. Output purely factual data."
        
        if context == "handwriting":
            specific_instruction = "This is likely a HANDWRITTEN NOTE or SCANNED DOCUMENT. Transcribe the text exactly. Ignore paper texture."
        elif context == "embedded":
            specific_instruction = "This is an EVIDENCE PHOTO embedded in a file. Describe details, people, background, and anomalies."
        else:
            specific_instruction = "If text: transcribe. If photo: describe details. If blurry: mark uncertain parts as [?]."

        final_prompt = f"{base_instruction}\n\nSPECIFIC TASK: {specific_instruction}"

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": final_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_img}"}}
                    ]
                }],
                temperature=0.1
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"⚠️ Vision Error: {e}"

    def process_file(self, file_path, file_type):
        """
        Master function to handle Images AND PDFs.
        """
        results = ""
        
        # --- IMAGE HANDLER ---
        if file_type in ["jpg", "jpeg", "png"]:
            try:
                img = Image.open(file_path)
                desc = self.analyze_visual(img, context="generic")
                results += f"\n[IMAGE ANALYSIS]:\n{desc}\n"
            except Exception as e:
                results += f"❌ Error opening image: {e}"

        # --- PDF HANDLER (Deep Scan) ---
        elif file_type == "pdf":
            try:
                doc = fitz.open(file_path)
                results += f"\n[PDF DOSSIER - {len(doc)} Pages]\n"
                
                for page_num, page in enumerate(doc):
                    # 1. Try Digital Text Extraction
                    text = page.get_text()
                    
                    # 2. Check for Handwriting/Scanned Page
                    if len(text.strip()) < 50: 
                        pix = page.get_pixmap()
                        img = Image.open(BytesIO(pix.tobytes()))
                        # Tell AI this is handwriting
                        vision_text = self.analyze_visual(img, context="handwriting")
                        results += f"\n--- PAGE {page_num+1} (Handwriting/Scan) ---\n{vision_text}\n"
                    else:
                        results += f"\n--- PAGE {page_num+1} (Digital Text) ---\n{text}\n"
                    
                    # 3. Extract Embedded Images
                    images = page.get_images()
                    for i, img_info in enumerate(images):
                        xref = img_info[0]
                        base_image = doc.extract_image(xref)
                        pil_img = Image.open(BytesIO(base_image["image"]))
                        
                        # Filter out tiny icons
                        if pil_img.width > 100 and pil_img.height > 100:
                            # Tell AI this is an evidence photo
                            img_desc = self.analyze_visual(pil_img, context="embedded")
                            results += f"\n[EMBEDDED IMAGE P{page_num+1}-{i+1}]: {img_desc}\n"
                            
            except Exception as e:
                results += f"❌ PDF Error: {e}"
                
        return results

# Adapter for Dashboard
def analyze_image(path):
    engine = VisionAnalyzer()
    ext = path.split(".")[-1].lower()
    return engine.process_file(path, ext)
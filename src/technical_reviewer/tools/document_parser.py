from crewai.tools import tool
import pdfplumber
from pdf2image import convert_from_path
import os
import tempfile
import base64
from openai import OpenAI

@tool
def parse_document(file_path: str) -> str:
    """Extract and visually analyze architecture from PDF or image"""
    
    client = OpenAI()
    text_results = []

    def analyze_image(img_path):
        with open(img_path, "rb") as img_file:
            base64_image = base64.b64encode(img_file.read()).decode('utf-8')
        
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this architecture document or diagram. Detail all components, relationships, databases, and technologies shown."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ],
                }
            ],
            max_tokens=1500,
        )
        return response.choices[0].message.content

    if file_path.lower().endswith(".pdf"):
        # First get raw text just in case
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_results.append(extracted)
        except Exception:
            pass
        
        # Now get images and analyze with vision
        with tempfile.TemporaryDirectory() as temp_dir:
            images = convert_from_path(file_path, output_folder=temp_dir)
            for i, image in enumerate(images):
                img_path = os.path.join(temp_dir, f"page_{i}.jpg")
                image.save(img_path, 'JPEG')
                vision_analysis = analyze_image(img_path)
                text_results.append(f"--- Page {i+1} Visual Analysis ---\n{vision_analysis}")

    elif file_path.lower().endswith((".png", ".jpg", ".jpeg")):
        vision_analysis = analyze_image(file_path)
        text_results.append(vision_analysis)

    else:
        return "Unsupported file format"

    return "\n\n".join(text_results)
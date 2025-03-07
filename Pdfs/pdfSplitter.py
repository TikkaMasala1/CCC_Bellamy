import fitz
import re
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
import sys
import os


def ocr_page(page):
    try:
        # Convert PDF page to  image
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))

        # Preprocess image to enhance OCR accuracy
        img_np = np.array(img)
        # Convert to grayscale for better thresholding
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        # Apply binary thresholding to create high-contrast image
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        img_processed = Image.fromarray(thresh)

        # Perform OCR using Tesseract with default settings
        text = pytesseract.image_to_string(img_processed)
        return text.strip()
    except Exception as e:
        print(f"OCR failed on page {page.number}: {e}")
        return ""


def split_pdf_by_chapters(pdf_path, output_text_files=False):
    try:
        doc = fitz.open(pdf_path)
        chapters = []
        pattern = re.compile(r"^\s*Domain\s+\d+:.*", re.IGNORECASE)

        # Identify chapter start pages
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text().strip()

            # Fallback to OCR if no text detected in PDF
            if not text:
                text = ocr_page(page)

            # Check each line for chapter heading pattern
            lines = text.split('\n')
            for line in lines:
                line_clean = line.strip()
                if pattern.match(line_clean):
                    # Store chapter info with sanitized filename
                    chapters.append({
                        'title': re.sub(r'\W+', '_', line_clean),  # Safe filename
                        'start_page': page_num
                    })
                    break  # Process next page after first match

        # Create output directories if needed
        if not os.path.exists("chapters"):
            os.makedirs("chapters")
        if output_text_files and not os.path.exists("chapter_texts"):
            os.makedirs("chapter_texts")

        # Process identified chapters
        for i, chapter in enumerate(chapters):
            # Determine page range for current chapter
            start = chapter['start_page']
            end = chapters[i + 1]['start_page'] - 1 if i < len(chapters) - 1 else len(doc) - 1

            # Generate PDF output filename
            output_filename = f"chapters/{chapter['title']}.pdf"

            # Extract and save chapter pages as new PDF
            output = fitz.open()
            output.insert_pdf(doc, from_page=start, to_page=end)
            output.save(output_filename)
            output.close()
            print(f"Saved: {output_filename}")

            # Optional text file generation
            if output_text_files:
                chapter_text = ""
                # Extract text from all chapter pages
                for page_num in range(start, end + 1):
                    page = doc.load_page(page_num)
                    text = page.get_text().strip()
                    # Use OCR if no text detected
                    if not text:
                        text = ocr_page(page)
                    chapter_text += text + "\n\n"

                # Save combined text content
                text_filename = f"chapter_texts/{chapter['title']}.txt"
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(chapter_text)
                print(f"Saved: {text_filename}")

        doc.close()
    except Exception as e:
        print(f"Critical error processing PDF: {e}")
        sys.exit(1)


split_pdf_by_chapters(
    "CCSK Study Guide.pdf",
    output_text_files=True)

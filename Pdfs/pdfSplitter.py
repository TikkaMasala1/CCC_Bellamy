import fitz
import re
import pytesseract
from PIL import Image
import io
import cv2
import numpy as np
import sys
import os

pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def ocr_page(page):
    """
    Performs OCR on a given page of a PDF.

    Args:
        page (fitz.Page): The page object from PyMuPDF.

    Returns:
        str: The extracted text from the page, or an empty string if OCR fails.
    """
    try:
        # Convert PDF page to image
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        img_np = np.array(img)

        # Convert image to grayscale and apply thresholding for better OCR
        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        img_processed = Image.fromarray(thresh)

        # Perform OCR using Tesseract
        text = pytesseract.image_to_string(img_processed)
        return text.strip()
    except Exception as e:
        print(f"OCR failed on page {page.number}: {e}")
        return ""


def split_pdf_by_chapters(pdf_path, output_text_files=False):
    """
    Splits a PDF into separate chapter PDFs and optionally extracts chapter text.

    Args:
        pdf_path (str): Path to the input PDF file.
        output_text_files (bool, optional): Whether to generate text files for each chapter. Defaults to False.
    """
    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)
        chapters = []  # List to store chapter information
        # Regular expression to match chapter headings (e.g., "Domain 1: Chapter Title")
        pattern = re.compile(

            r"^Domain\s+\d+:\s*([A-Z][\w\s\-,&]+)(?:\n\s*([A-Z][\w\s\-,&]+))*",

            re.MULTILINE | re.IGNORECASE

        )

        # Iterate through each page of the PDF
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_blocks = page.get_text("blocks")  # Extract text blocks from the page

            # Check only the top 20% of the page for chapter headings
            top_region = page.rect.height * 0.2
            chapter_candidates = []

            # Extract potential chapter headings from the top region
            for block in text_blocks:
                x0, y0, x1, y1, text, _, _ = block
                if y0 < top_region:
                    chapter_candidates.extend(text.split('\n'))

            # Fallback to OCR if no text is found in the top region
            if not chapter_candidates:
                text = ocr_page(page)
                chapter_candidates = text.split('\n')[:3]  # Check the first 3 lines from OCR

            # Check if any of the candidate lines match the chapter heading pattern
            match_found = False
            for line in chapter_candidates:
                clean_line = line.strip()
                if pattern.fullmatch(clean_line):
                    # Sanitize the chapter title for use as a filename
                    sanitized = re.sub(r'\W+', '_', clean_line)
                    chapters.append({
                        'title': sanitized,
                        'start_page': page_num
                    })
                    match_found = True
                    break

        # Validate chapter sequence to ensure chapters are in increasing page order.
        valid_structure = True
        for i in range(1, len(chapters)):
            if chapters[i]['start_page'] <= chapters[i - 1]['start_page']:
                valid_structure = False
        if not valid_structure:
            raise ValueError("Invalid chapter sequence detected")

        # Create output directories if they don't exist
        os.makedirs("chapters", exist_ok=True)
        if output_text_files:
            os.makedirs("chapter_texts", exist_ok=True)

        # Iterate through the identified chapters and create separate PDF files
        for i, ch in enumerate(chapters):
            start = ch['start_page']
            end = chapters[i + 1]['start_page'] - 1 if i < len(chapters) - 1 else len(doc) - 1

            # Validate minimum chapter length (skip if chapter is too short)
            if end - start < 1:
                continue

            # Create a new PDF document for the chapter
            output = fitz.open()
            output.insert_pdf(doc, from_page=start, to_page=end)
            output.save(f"chapters/{ch['title']}.pdf")

            # Optionally, generate text files for each chapter
            if output_text_files:
                chapter_text = ""
                # Extract text from each page of the chapter
                for page_num in range(start, end + 1):
                    page = doc.load_page(page_num)
                    text = page.get_text().strip()
                    if not text:
                        text = ocr_page(page)  # Fallback to OCR if no text is found
                    chapter_text += text + "\n\n"

                # Save the extracted text to a file
                text_filename = f"chapter_texts/{ch['title']}.txt"
                with open(text_filename, 'w', encoding='utf-8') as f:
                    f.write(chapter_text)

        doc.close()  # Close the input PDF document
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)  # Exit the program if an error occurs


if __name__ == "__main__":
    split_pdf_by_chapters("Documents/CCSK Study Guide.pdf", output_text_files=True)

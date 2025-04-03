import sys
import re
import fitz
import os

DOCUMENT_INSTRUCTIONS = {
    'CCSK': {
        'skip_pages': 7,
        'regex_pattern': r'^Domain\s+[IVXLCDM\d]+:\s*[^.]+(?=\n\s*[A-Z0-9]|\Z)',
        'flags': re.MULTILINE,
        'footer_margin': 75,
        'subchapter_regex_pattern': r'^\s*(\d+\.)+\d+\s+[A-Z][A-Za-z. &-]+',
        'subchapter_flags': re.MULTILINE
    },

    'Zero Trust Planning': {
        'skip_pages': 9,
        'regex_pattern': r'^\d+\s+(?!.*\(\d{4}[^)]*\))(?!.*Retrieved\s+\d{4})[A-Z].+',
        'flags': re.MULTILINE,
        'footer_margin': 75,
        'subchapter_regex_pattern': r'^\s*(\d+\.)+\d+\s+[A-Z][A-Za-z. &-]+',
        'subchapter_flags': re.MULTILINE
    },

    'Zero Trust Strategy': {
        'skip_pages': 9,
        'regex_pattern': r'^\d+\s+(?!.*(?:Note:|See|Pg\.|In some|To learn|Learn more|is (?:designed to|United States legislation)|\(\w+\)|they\b|have created|as many|familiarize))[A-Z][A-Za-z, &-]+(?<!\.)$',
        'flags': re.MULTILINE,
        'footer_margin': 75,
        'subchapter_regex_pattern': r'^\s*(\d+\.)+\d+\s+[A-Z][A-Za-z. &-]+',
        'subchapter_flags': re.MULTILINE
    },

    'Zero Trust Implementation': {
        'skip_pages': 8,
        'regex_pattern': r'^\d+\s+(?!.*(?:\(\d{4}[^)]*\)|Retrieved\s+\d{4}|Learn\s+more|Note:|https?://))[A-Z][A-Za-z].+',
        'flags': re.MULTILINE,
        'footer_margin': 75,
        'subchapter_regex_pattern': r'^\s*(\d+\.)+\d+\s+[A-Z][A-Za-z. &-]+',
        'subchapter_flags': re.MULTILINE
    }
}


def process_pdf(pdf_path, instruction_key):
    """
    Processes a PDF, extracts text, and splits it into chapters using regex.

    Args:
        pdf_path (str): Path to the PDF file.
        instruction_key (str): Key to the document instructions.
    """
    instructions = DOCUMENT_INSTRUCTIONS.get(instruction_key)
    if not instructions:
        raise ValueError(f"No instructions found for key: {instruction_key}")

    # Simplified chapter pattern
    chapter_pattern = re.compile(
        instructions['regex_pattern'],
        flags=instructions.get('flags', 0)
    )

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Error opening PDF: {e}")

    # Extract text from PDF with minimal preprocessing
    full_text = ""
    footer_margin = instructions['footer_margin']  # Get the footer margin

    for page_num in range(instructions['skip_pages'], doc.page_count):
        page = doc[page_num]
        # Define the area to clip (excluding footer)
        page_rect = page.rect
        clip_rect = fitz.Rect(0, 0, page_rect.width, page_rect.height - footer_margin)
        # Extract text from the clipped area
        text = page.get_text("text", clip=clip_rect)
        full_text += text + "\n"

    # Improved chapter splitting
    chapters = []
    last_pos = 0
    for match in chapter_pattern.finditer(full_text):
        start = match.start()
        if start > last_pos:
            chapters.append(full_text[last_pos:start])
        last_pos = start
    chapters.append(full_text[last_pos:])

    # Process chapters
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join("Output", base_filename)
    os.makedirs(output_dir, exist_ok=True)

    subchapter_pattern = re.compile(
        instructions.get('subchapter_regex_pattern', r'^$'),
        flags=instructions.get('subchapter_flags', 0)
    )

    for idx, chapter_text in enumerate(chapters, 1):
        # Split subchapters
        subchapters = []
        last_sub_pos = 0
        for match in subchapter_pattern.finditer(chapter_text):
            start = match.start()
            if start > last_sub_pos:
                subchapters.append(chapter_text[last_sub_pos:start])
            last_sub_pos = start
        subchapters.append(chapter_text[last_sub_pos:])

        # Save subchapters
        chapter_dir = os.path.join(output_dir, f"chapter_{idx}")
        os.makedirs(chapter_dir, exist_ok=True)

        for sub_idx, sub_text in enumerate(subchapters, 1):
            # Extract the first line of sub_text to use as file name
            stripped_text = sub_text.strip()
            first_line = stripped_text.splitlines()[0] if stripped_text else ""
            # Sanitize the first line to remove invalid filename characters
            safe_name = re.sub(r'[\\/*?:"<>|]', "", first_line)
            # Fallback if the sanitized first line is empty
            if not safe_name:
                safe_name = f"subchapter_{sub_idx}"
            # Save the file using the sanitized first line as the file name
            with open(os.path.join(chapter_dir, f"{safe_name}.txt"), 'w', encoding='utf-8') as f:
                f.write(sub_text.strip())


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./pdfSplitter.py <pdf-file> <instruction-key>")
        sys.exit(1)

    try:
        process_pdf(sys.argv[1], sys.argv[2])
        print("Successfully split PDF into chapters and subchapters")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

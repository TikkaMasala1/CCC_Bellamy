import sys
import re
import fitz
import os

# Hardcoded document instructions
DOCUMENT_INSTRUCTIONS = {
    'CCSK': {
        'skip_pages': 7,
        'regex_pattern': r'^Domain\s+[IVXLCDM\d]+:\s*[^.]+(?=\n\s*[A-Z0-9]|\Z)',
        'flags': re.MULTILINE
    },

    'Zero Trust Planning': {
        'skip_pages': 8,
        'regex_pattern': r'^\d+\s+(?!.*\(\d{4}[^)]*\))(?!.*Retrieved\s+\d{4})[A-Z].+',
        'flags': re.MULTILINE
    },

    'Zero Trust Strategy': {
        'skip_pages': 8,
        'regex_pattern': r'^\d+\s+(?!.*(?:Note:|See|Pg\.|In some|To learn|Learn more|is (?:designed to|United States legislation)|\(\w+\)|they\b|have created|as many|familiarize))[A-Z][A-Za-z, &-]+(?<!\.)$',
        'flags': re.MULTILINE
    },

    'Zero Trust Implementation': {
        'skip_pages': 8,
        'regex_pattern': r'^\d+\s+(?!.*(?:\(\d{4}[^)]*\)|Retrieved\s+\d{4}|Learn\s+more|Note:|https?://))[A-Z][A-Za-z].+',
        'flags': re.MULTILINE
    }
}


def process_pdf(pdf_path, instruction_key):
    """
    Processes a PDF, extracts text, and splits it into chapters using regex.

    Args:
        pdf_path (str): Path to the PDF file.
        instruction_key (str): Key to the document instructions.
    """

    # Get document-specific instructions
    instructions = DOCUMENT_INSTRUCTIONS.get(instruction_key)
    if not instructions:
        raise ValueError(f"No instructions found for key: {instruction_key}")

    # Compile regex pattern
    pattern = re.compile(
        instructions['regex_pattern'],
        flags=instructions.get('flags', 0)
    )

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise ValueError(f"Error opening PDF: {e}")

    # Extract text from PDF
    full_text = ""
    for page_num in range(instructions['skip_pages'], doc.page_count):
        page = doc[page_num]
        full_text += page.get_text("text") + "\n"  # add newline for proper multiline regex.

    doc.close()

    # Split text into chapters using regex
    matches = list(pattern.finditer(full_text))
    if not matches:
        raise ValueError("No chapter matches found in the text")

    chapters = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i < len(matches) - 1 else len(full_text)
        chapters.append(full_text[start:end])

    # Write chapters to files
    base_filename = os.path.splitext(os.path.basename(pdf_path))[0]  # Get filename without extension

    os.makedirs(f"Output/{base_filename}", exist_ok=True)

    for idx, chapter in enumerate(chapters, 1):
        with open(f"Output/{base_filename}/chapter_{idx}.txt", 'w', encoding="utf-8") as f:  # added encoding
            f.write(chapter)


if __name__ == "__main__":
    process_pdf("Documents/Zero_Trust_Implementation_Study_Guide.pdf", "Zero Trust Implementation")
    # if len(sys.argv) != 3:
    #     print("Usage: ./pdfSplitter.py <pdf-file> <instruction-key>")
    #     sys.exit(1)
    #
    # try:
    #     process_pdf(sys.argv[1], sys.argv[2])
    #     print("Successfully split PDF into chapters")
    # except Exception as e:
    #     print(f"Error: {str(e)}")
    #     sys.exit(1)

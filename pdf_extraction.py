import fitz  # PyMuPDF
import nltk
from pathlib import Path
import os
import re

def is_footnote(text: str, y_position: float, page_height: float) -> bool:
        """Identify footnotes based on content and position."""
        footnote_patterns = [
            r'^\[\d+\]',
            r'^\d+\.',
            r'^\d+',
            r'^[*†‡§]'
        ]

        text = text.strip()
        is_footnote_format = any(re.match(pattern, text) for pattern in footnote_patterns)
        is_bottom_position = y_position > (page_height * 0.84)
        return is_footnote_format and is_bottom_position and len(text) < 256


def extract_text_blocks_from_pdf(pdf_path, start_page=0, end_page=-1):
    extracted_text_blocks = []
    footnote_text_blocks = []
    doc = fitz.open(pdf_path)

    # Ensure the page range is valid
    start_page = max(0, start_page)  # Page numbers start from 0
    if end_page < 0: end_page = len(doc) + end_page
    end_page = min(end_page, len(doc) - 1)
    
    for page_num in range(start_page, end_page + 1):
        page = doc[page_num]
        blocks = page.get_text("blocks", sort=True)
        
        for block in blocks:
            text = block[4]  # The text is the fifth element in the block tuple
            y_position = block[1]

            # Skip empty blocks and page numbers
            if not text.strip() or text.strip().isdigit(): 
                 continue 
            
            # Footnotes to be stored separately
            elif is_footnote(text.strip(), y_position, page.rect.height):
                footnote_text_blocks.append((page_num +1, text.strip()))

            # Text blocks
            else:
                extracted_text_blocks.append(text.strip())

    return (extracted_text_blocks, footnote_text_blocks)

def is_sentence_end(text):
    text = text.strip()
    pattern = r'[.!?][\"\'\)]?$'
    return bool(re.search(pattern, text))


def get_paragraph_blocks(text_blocks):
    complete_para_blocks = []
    continuing_block = ""
    
    for i, block in enumerate(text_blocks):
        
        if not block.strip():
            continue

        # First block
        if not continuing_block:
            continuing_block = block
            continue

        # Check if previous block is incomplete and current block starts with lowercase
        if not is_sentence_end(continuing_block) and block.strip()[0].islower():
            continuing_block = f"{continuing_block.strip()} {block.strip()}"
        else:
            # Add the continuing block to list and start a new one
            complete_para_blocks.append(continuing_block.strip())
            continuing_block = block

    # Add the last paragraph
    if continuing_block:
        complete_para_blocks.append(continuing_block.strip())
    
    return complete_para_blocks
   


# if __name__ == "__main__":
#     input_pdf_path = "docs/seer_En.pdf"
#     extracted_text_blocks, footnote_text_blocks = extract_text_blocks_from_pdf(input_pdf_path)
#     complete_paragraph_blocks = get_paragraph_blocks(extracted_text_blocks)

#     for block in complete_paragraph_blocks:

#         print(block)
#         print('-' * 80)
#         print()
#     print("====Footnotes====")
#     for block in footnote_text_blocks:

#         print("Page num: ", block[0])
#         print(block[1])
    
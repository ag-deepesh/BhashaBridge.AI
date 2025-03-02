import pdfplumber
import re
from typing import List, Dict, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFTextExtractor:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.page_number_patterns = [
            r'^\d+$',
            r'^Page\s*\d+$',
            r'^\d+\s*of\s*\d+$'
        ]
        self.footnote_patterns = [
            r'^\[\d+\]',
            r'^\d+\.',
            r'^[*†‡§]'
        ]
        # Title page patterns
        self.title_patterns = [
            r'^(CHAPTER|Chapter)\s+\d+',
            r'^(SECTION|Section)\s+\d+',
            r'^(ABSTRACT|Abstract)',
            r'^(CONTENTS|Contents)',
            r'^(INTRODUCTION|Introduction)'
        ]
        
    def is_page_number(self, text: str) -> bool:
        """Check if the text is likely a page number."""
        text = text.strip()
        return any(re.match(pattern, text) for pattern in self.page_number_patterns)
    
    def is_footnote(self, text: str, y_position: float, page_height: float) -> bool:
        """Check if the text is likely a footnote based on content and position."""
        text = text.strip()
        is_footnote_format = any(re.match(pattern, text) for pattern in self.footnote_patterns)
        is_bottom_position = y_position > (page_height * 0.9)
        return is_footnote_format or is_bottom_position

    def is_title_block(self, text: str, font_size: float = None, y_position: float = None, 
                      page_height: float = None) -> bool:
        """
        Detect if text block is likely a title based on content, font size, and position.
        """
        text = text.strip()
        
        # Check for title patterns
        is_title_pattern = any(re.match(pattern, text) for pattern in self.title_patterns)
        
        # Title characteristics
        is_large_font = font_size and font_size > 12  # Assuming standard font size is 12
        is_top_position = y_position and page_height and (y_position < (page_height * 0.2))
        is_all_caps = text.isupper() and len(text) > 3
        
        return (is_title_pattern or 
                (is_large_font and is_top_position) or 
                (is_all_caps and is_top_position))

    def should_merge_blocks(self, block1: Dict, block2: Dict) -> bool:
        """Determine if two text blocks should be merged."""
        if not block1 or not block2:
            return False
            
        text1 = block1['text'].strip()
        text2 = block2['text'].strip()
        
        # Don't merge if either block is a title
        if (self.is_title_block(text1, block1.get('font_size'), 
                              block1.get('y_position'), block1.get('page_height')) or
            self.is_title_block(text2, block2.get('font_size'), 
                              block2.get('y_position'), block2.get('page_height'))):
            return False
            
        # Don't merge blocks from different pages
        if block1['page_number'] != block2['page_number']:
            return False
        
        # Check for incomplete sentence endings
        incomplete_endings = [
            lambda x: not x.endswith('.'),
            lambda x: x.endswith(','),
            lambda x: x.endswith(':'),
            lambda x: x.endswith(';'),
            lambda x: x.endswith('-'),
            lambda x: any(x.endswith(word) for word in ['and', 'or', 'the', 'a', 'an'])
        ]
        
        # Check if block2 starts with lowercase
        starts_lowercase = text2[0].islower() if text2 else False
        
        return any(ending(text1) for ending in incomplete_endings) or starts_lowercase

    def clean_text_block(self, text: str) -> str:
        """Clean and normalize text block."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\S\n]+', ' ', text)
        text = re.sub(r'-\s+', '', text)
        return text.strip()

    def extract_blocks(self) -> List[Dict]:
        """Extract and merge text blocks from PDF."""
        blocks = []
        current_block = None
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_blocks = page.extract_words(
                        keep_blank_chars=True,
                        #x_tolerance=3,
                        #y_tolerance=3
                    )
                    
                    for block in page_blocks:
                        text = block.get('text', '').strip()
                        if not text:
                            continue
                            
                        # Skip page numbers and footnotes
                        if self.is_page_number(text) or \
                           self.is_footnote(text, block['bottom'], page.height):
                            continue
                        
                        # Create block with metadata
                        new_block = {
                            'text': self.clean_text_block(text),
                            'page_number': page_num,
                            'font_size': block.get('size', 0),
                            'y_position': block.get('top', 0),
                            'page_height': page.height
                        }
                        
                        if current_block and self.should_merge_blocks(current_block, new_block):
                            # Merge with previous block
                            current_block['text'] = f"{current_block['text']} {new_block['text']}"
                        else:
                            # Start new block
                            if current_block:
                                blocks.append(current_block)
                            current_block = new_block
                    
            # Add the last block
            if current_block:
                blocks.append(current_block)
                
            return blocks
            
        except Exception as e:
            logger.error(f"Error processing PDF: {str(e)}")
            raise

def main():
    pdf_path = "docs/seer_En.pdf"
    
    try:
        extractor = PDFTextExtractor(pdf_path)
        text_blocks = extractor.extract_blocks()
        
        print(f"\nExtracted {len(text_blocks)} text blocks:")
        for i, block in enumerate(text_blocks, 1):
            print(f"\nBlock {i} (Page {block['page_number']}):")
            print(block['text'])
            print("-" * 80)
            
    except Exception as e:
        logger.error(f"Failed to process PDF: {str(e)}")

if __name__ == "__main__":
    main()
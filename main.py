# from translate_text import *
from translate_api import *
from pdf_extraction import *
from save_output import *
from translation_eval import *
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import re

def get_glossary(excel_file_path):
    try:
        # Read the Excel file
        df = pd.read_excel(excel_file_path)
        # Ensure the required columns exist
        required_columns = ['English', 'Hindi', 'Transliteration']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Excel file must contain 'English', 'Hindi', and 'Transliteration' columns")
        
        # Select only the required columns and remove any rows with missing values
        glossary_df = df[required_columns].dropna()
        glossary_df['English'] = glossary_df['English'].str.lower()
        glossary_df['Transliteration'] = glossary_df['Transliteration'].str.lower()
        return glossary_df
    
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        return None


def get_glossary_transformed_block(block, glossary_df):
    try:
        # Create dictionaries for English and Transliteration mappings
        eng_to_hindi = dict(zip(glossary_df['English'], glossary_df['Hindi']))
        trans_to_hindi = dict(zip(glossary_df['Transliteration'], glossary_df['Hindi']))

        # Combine all words/phrases to search for
        search_terms = list(eng_to_hindi.keys()) + list(trans_to_hindi.keys())
        
        # Create regex pattern - word boundaries to match whole words only
        # Sort by length in descending order to match longer phrases first
        pattern = '|'.join(r'\b' + re.escape(term) + r'\b' 
                          for term in sorted(search_terms, key=len, reverse=True))
        
        # Define replacement function
        def replace_match(match):
            term = match.group(0)
            return eng_to_hindi.get(term) or trans_to_hindi.get(term)

        # Single pass replacement using regex substitution
        transformed_block = re.sub(pattern, replace_match, block.lower())
        return transformed_block
        
    except Exception as e:
        print(f"Error transforming block: {str(e)}")
        return block


def translate_document(input_pdf_path, output_path, glossary_df=None, src_lang='English', tgt_lang=None):
    """
    Main function to handle the translation pipeline
    """
    try:
        
        # 1. Parse pdf and extract text blocks
        extracted_text_blocks, footnote_text_blocks = extract_text_blocks_from_pdf(input_pdf_path)
        complete_paragraph_blocks = get_paragraph_blocks(extracted_text_blocks)
        
        print("Text block extraction done!")
        
        # 2. Translate text blocks
        translated_text_paragraphs = []
        for block in tqdm(complete_paragraph_blocks):
            block = block.strip()
            translated_block = translate_text_gpt(block, tgt_lang)
            translated_text_paragraphs.append(translated_block)
        
        print('\n\n\n')
        print("========Footnotes========")
        for block in tqdm(footnote_text_blocks):
            translated_block = translate_text_gpt(block[1], tgt_lang)
            translated_text_paragraphs.append(f"Page num: {block[0]}\n")
            translated_text_paragraphs.append(translated_block)
            print()

        
        # 3. Save the translated text to output file
        result = save_output_text(translated_text_paragraphs, output_path)
        #return (paragraphs, translated_paragraphs, output_path) if os.path.exists(output_path) else result
        
    except Exception as e:
        print("Error: ", e)
        return f"Error in translation process: {str(e)}"

if __name__== "__main__":

    input_pdf_path = "docs/seer_En.pdf"
    glossary_excel_path = "docs/glossary-en-hi-heartfulness.xlsx"
    input_ground_truth_pdf_path = "docs/seer_hindi.pdf"
    src_lang, tgt_lang =  "English", "Hindi"
    glossary_df = get_glossary(glossary_excel_path)

    # Create output directory if it doesn't exist
    output_dir = "translated_docs"
    os.makedirs(output_dir, exist_ok=True)
    
    # Create output file
    input_filename = Path(input_pdf_path).stem
    output_path = os.path.join(output_dir, f"translated_{input_filename}_GPT4o_{tgt_lang}_2.txt")
    
    translate_document(input_pdf_path, output_path, glossary_df, src_lang=src_lang, tgt_lang=tgt_lang)

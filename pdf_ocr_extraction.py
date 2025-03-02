import easyocr
from pdf2image import convert_from_path
import os
import numpy as np


def extract_text_with_easyocr(pdf_path):

    reader = easyocr.Reader(['en'])

    #create output filename using pdf file name
    pdf_filename = os.path.basename(pdf_path)
    pdf_name = ps.path.splitext(pdf_filename)[0]
    output_file = f"{pdf_name}.txt"
    print("output file: ", output_file)

    #Covert PDF to images
    print("Converting PDF to images...")
    images = convert_from_path(pdf_path)

    #Open file for writing
    with open(output_file, 'w', encoding='utf-8') as f:
        #Process each page
        for i, image in enumerate(images):
            print(f"Processing page {i+1}...")

            #Extract text
            result = reader.readtext(np.arracy(image))

            #combine text from the page
            page_text = '\n'.join([text[1] for text in result])
            translated_page_text = translate_text(page_text)

            f.write(f"\n\n== Page {i+1} ==\n\n")

            #Flush the buffer to ensure writing
            f.flush()

    print("text has been written to: {output file}")
    return output_file


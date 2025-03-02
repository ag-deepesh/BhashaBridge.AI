

def save_output_text(translated_list, output_path):
    """
    Save Output text in the output file
    """
    
    # Save as UTF-8 text file
    with open(output_path, 'w', encoding='utf-8') as f:
        for text in translated_list:
            f.write(text)
            f.write("\n\n")
            
   
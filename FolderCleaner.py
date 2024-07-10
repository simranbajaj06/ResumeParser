import os
import PyPDF2

def folder_cleaner(folder_path):
    for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                
                pdf_path = os.path.join(folder_path, filename)
            
                try:
                    with open(pdf_path, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        text=''
                        for page_num in range(len(reader.pages)):
                            page = reader.pages[page_num]
                            text += page.extract_text()
                            
                        text=text.strip()
                        if len(text)==0:
                            os.remove(pdf_path)
                except :
                    os.remove(pdf_path)
                    continue
      
    
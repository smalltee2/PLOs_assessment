import PyPDF2
import io

class PDFExtractor:
    def extract_text(self, file) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += f"\n--- หน้า {page_num + 1} ---\n"
                text += page.extract_text()
            
            return text
        except Exception as e:
            raise Exception(f"ไม่สามารถอ่านไฟล์ PDF: {str(e)}")

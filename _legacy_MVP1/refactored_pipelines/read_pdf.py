import pypdf
import sys

def extract_text_from_pdf(pdf_path):
    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

if __name__ == "__main__":
    pdf_path = "/Users/sml/Downloads/AI 기반 뉴스 자동화 시스템 기술 리서치.pdf"
    content = extract_text_from_pdf(pdf_path)
    print(content)

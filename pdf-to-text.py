import base64
import io
import logging
import sys
from typing import Any
import PyPDF2
import pdfplumber
import pytesseract
from PIL import Image
import functions_framework


@functions_framework.http
def convert_pdf_to_text(request):
    """
    Receives a base64 encoded PDF file, decodes it, extracts the text,
    and returns the text.
    """
    # Extract base64 encoded PDF from request
    request_json = request.get_json(silent=True)
    encoded_pdf = request_json.get("pdf_base64") if request_json else None
    if not encoded_pdf:
        return "Base64 encoded PDF is required.", 400

    try:
        # Decode the base64 PDF
        pdf_bytes = base64.b64decode(encoded_pdf)
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))

        # Extract text from each page
        text = ""
        for page_number, page in enumerate(reader.pages):
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
                else:
                    logging.info(
                        "No text found on page %d, attempting OCR.", page_number + 1
                    )
                    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                        page = pdf.pages[page_number]
                        pil_image = page.to_image(resolution=300).original
                        ocr_text = pytesseract.image_to_string(pil_image)
                        if ocr_text.strip():
                            text += ocr_text + "\n"
                        else:
                            logging.info(
                                "OCR did not find any text on page %d.", page_number + 1
                            )
            except Exception as e:
                logging.error(
                    "Error extracting text from page %d: %s", page_number + 1, str(e)
                )
                continue

        logging.info("Text extracted from PDF: %s", text)
        return text

    except Exception as e:
        logging.error("Error processing PDF: %s", str(e))
        return "An error occurred while processing the PDF.", 500


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_text.py <path_to_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    extracted_text = convert_pdf_to_text(pdf_path)
    print(extracted_text)

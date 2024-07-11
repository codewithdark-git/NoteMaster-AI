import pytesseract
import easyocr

# def image_to_text(image):
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#     text = pytesseract.image_to_string(image)
#     return text

def image_to_text(image):
    reader = easyocr.Reader(['ch_sim', 'en'])  # this needs to run only once to load the model into memory
    result = reader.readtext(image, detail=0)
    return result



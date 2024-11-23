import pytesseract
import easyocr
import numpy as np

def image_to_text(image):
    try:
        # Initialize EasyOCR reader
        reader = easyocr.Reader(['en'])
        
        # Ensure image is in the correct format
        if not isinstance(image, np.ndarray):
            raise ValueError(f"Input must be a numpy array, got {type(image)}")
            
        # Get OCR results
        result = reader.readtext(image, detail=0)
        
        # Process results
        if not result:
            return ""
            
        if isinstance(result, list):
            text = ' '.join(str(r) for r in result)
            return text
        
        return str(result)
        
    except Exception as e:
        raise Exception(f"OCR processing error: {str(e)}")

import base64

def utf8_to_base64(text:str):
    """
    Converts a UTF-8 text to a base64 text.
    """
    encoded_bytes = text.encode('utf-8')
    base64_bytes = base64.b64encode(encoded_bytes)
    base64_text = base64_bytes.decode('utf-8')
    return base64_text


def base64_to_utf8(base10_text:str):
    """
    Converts a base64 text to a UTF-8 text.
    \nIf the decoding fails, return the input text
    """
    try:
        base64_bytes = base10_text.encode('utf-8')
        decoded_bytes = base64.b64decode(base64_bytes)
        utf8_text = decoded_bytes.decode('utf-8')
        return utf8_text
    except:
        # if the decoding fails, return the input text
        return base10_text
    

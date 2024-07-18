import base64

def utf8_to_base32(utf8_text: str) -> str:
    """
    Converts a UTF-8 text to a base32 text.
    """
    # Encode the UTF-8 text to bytes, then encode it to Base32 and decode back to UTF-8 for the string representation
    return base64.b32encode(utf8_text.encode('utf-8')).decode('utf-8')

def base32_to_utf8(base32_text: str) -> str:
    """
    Converts a base32 text to a UTF-8 text.
    If the decoding fails, return the input text
    """
    try:
        # Decode the Base32 encoded text to bytes, then decode it to UTF-8
        return base64.b32decode(base32_text.encode('utf-8')).decode('utf-8')
    except Exception:
        # Return the input text if decoding fails
        return base32_text
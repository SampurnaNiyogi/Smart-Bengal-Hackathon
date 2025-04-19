import base64
from pathlib import Path


def get_base64_encoded_image(image_path: str) -> str:
    """
    Convert image to base64 string
    :param image_path: The path to the image file
    :return: The image converted to base64 string
    """
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded}"


def load_css(css_filename: str) -> str:
    """
    Reads css from a .css file
    :param css_filename: The path to the css
    :return: The contents of the file
    """
    css_pathobj = Path('.') / 'css' / css_filename
    return css_pathobj.read_text()

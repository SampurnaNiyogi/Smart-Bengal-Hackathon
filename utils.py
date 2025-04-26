from streamlit import cache_data
import base64
from pathlib import Path


def get_base64_encoded_image(image_path: str) -> str:
    """
    Converts image to base64 string. This enables loading images in HTML in a Streamlit application
    :param image_path: The path to the image file
    :return: The image converted to base64 string
    """
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        return f"data:image/jpeg;base64,{encoded}"


@cache_data
def load_css(css_filename: str) -> str:
    """
    Reads CSS from a .css file
    :param css_filename: The name of the CSS file
    :return: HTML tag with the contents of the CSS file
    """
    css_pathobj = Path('.') / 'css' / css_filename
    css = css_pathobj.read_text()
    return f'<style>{css}</style>'


@cache_data
def load_svg(filename: str) -> str:
    """
    Loads SVG from a .svg file
    :param filename: The name of the SVG
    :return: The contents of the SVG
    """
    nice = Path('.') / 'assets' / filename
    return nice.read_text()

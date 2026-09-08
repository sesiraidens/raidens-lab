import numpy as np
import cv2


def rgb_to_hsv(r, g, b):
    """
    Converte RGB para HSV.
    
    Args:
        r: Vermelho (0-255)
        g: Verde (0-255)
        b: Azul (0-255)
        
    Returns:
        tuple: (h, s, v) - Hue (0-179), Saturation (0-255), Value (0-255)
    """
    pixel = np.uint8([[[b, g, r]]])
    hsv = cv2.cvtColor(pixel, cv2.COLOR_BGR2HSV)
    return tuple(hsv[0][0].tolist())


def rgb_to_lab(r, g, b):
    """
    Converte RGB para LAB.
    
    Args:
        r: Vermelho (0-255)
        g: Verde (0-255)
        b: Azul (0-255)
        
    Returns:
        tuple: (l, a, b) - Lightness (0-255), Green-Red (0-255), Blue-Yellow (0-255)
    """
    pixel = np.uint8([[[b, g, r]]])
    lab = cv2.cvtColor(pixel, cv2.COLOR_BGR2LAB)
    return tuple(lab[0][0].tolist())


def hsv_to_rgb(h, s, v):
    """
    Converte HSV para RGB.
    
    Args:
        h: Hue (0-179)
        s: Saturation (0-255)
        v: Value (0-255)
        
    Returns:
        tuple: (r, g, b) - Vermelho, Verde, Azul (0-255)
    """
    pixel = np.uint8([[[h, s, v]]])
    bgr = cv2.cvtColor(pixel, cv2.COLOR_HSV2BGR)
    return tuple(bgr[0][0][::-1].tolist())


def lab_to_rgb(l, a, b):
    """
    Converte LAB para RGB.
    
    Args:
        l: Lightness (0-255)
        a: Green-Red (0-255)
        b: Blue-Yellow (0-255)
        
    Returns:
        tuple: (r, g, b) - Vermelho, Verde, Azul (0-255)
    """
    pixel = np.uint8([[[l, a, b]]])
    bgr = cv2.cvtColor(pixel, cv2.COLOR_LAB2BGR)
    return tuple(bgr[0][0][::-1].tolist())


def hex_to_rgb(hex_color):
    """
    Converte hexadecimal para RGB.
    
    Args:
        hex_color: Cor em formato hexadecimal (ex: "#FF0000" ou "FF0000")
        
    Returns:
        tuple: (r, g, b)
    """
    hex_color = hex_color.lstrip("#")
    
    if len(hex_color) != 6:
        raise ValueError("Hex deve ter 6 caracteres")
        
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return (r, g, b)


def rgb_to_hex(r, g, b):
    """
    Converte RGB para hexadecimal.
    
    Args:
        r: Vermelho (0-255)
        g: Verde (0-255)
        b: Azul (0-255)
        
    Returns:
        str: Cor em hexadecimal (ex: "#FF0000")
    """
    return f"#{r:02x}{g:02x}{b:02x}"


def hsv_to_lab(h, s, v):
    """
    Converte HSV para LAB.
    
    Args:
        h: Hue (0-179)
        s: Saturation (0-255)
        v: Value (0-255)
        
    Returns:
        tuple: (l, a, b)
    """
    r, g, b = hsv_to_rgb(h, s, v)
    return rgb_to_lab(r, g, b)


def lab_to_hsv(l, a, b):
    """
    Converte LAB para HSV.
    
    Args:
        l: Lightness (0-255)
        a: Green-Red (0-255)
        b: Blue-Yellow (0-255)
        
    Returns:
        tuple: (h, s, v)
    """
    r, g, b_val = lab_to_rgb(l, a, b)
    return rgb_to_hsv(r, g, b_val)


def get_color_name(h, s, v):
    """
    Retorna nome aproximado da cor baseado no Hue.
    
    Args:
        h: Hue (0-179)
        s: Saturation (0-255)
        v: Value (0-255)
        
    Returns:
        str: Nome da cor
    """
    if s < 30:
        if v < 50:
            return "preto"
        elif v > 200:
            return "branco"
        else:
            return "cinza"
    
    if h < 10 or h > 160:
        return "vermelho"
    elif h < 22:
        return "laranja"
    elif h < 33:
        return "amarelo"
    elif h < 78:
        return "verde"
    elif h < 130:
        return "azul"
    elif h < 160:
        return "roxo"
    
    return "desconhecido"


def get_color_ranges():
    """
    Retorna ranges pre-definidos para cores comuns em HSV.
    
    Returns:
        dict: Dicionario com ranges de cada cor
    """
    return {
        "vermelho": {
            "lower1": [0, 120, 70],
            "upper1": [10, 255, 255],
            "lower2": [170, 120, 70],
            "upper2": [180, 255, 255]
        },
        "verde": {
            "lower": [35, 100, 100],
            "upper": [85, 255, 255]
        },
        "azul": {
            "lower": [100, 100, 100],
            "upper": [130, 255, 255]
        },
        "amarelo": {
            "lower": [20, 100, 100],
            "upper": [35, 255, 255]
        },
        "laranja": {
            "lower": [10, 100, 100],
            "upper": [20, 255, 255]
        },
        "roxo": {
            "lower": [130, 100, 100],
            "upper": [160, 255, 255]
        }
    }


def compare_colors(color1, color2, color_space="HSV"):
    """
    Calcula distancia entre duas cores.
    
    Args:
        color1: Primeira cor como tupla
        color2: Segunda cor como tupla
        color_space: Espaco de cor ("HSV" ou "LAB")
        
    Returns:
        float: Distancia euclidiana entre as cores
    """
    c1 = np.array(color1, dtype=np.float32)
    c2 = np.array(color2, dtype=np.float32)
    
    if color_space == "HSV":
        h_diff = min(abs(c1[0] - c2[0]), 180 - abs(c1[0] - c2[0]))
        s_diff = abs(c1[1] - c2[1])
        v_diff = abs(c1[2] - c2[2])
        
        return np.sqrt(h_diff**2 + s_diff**2 + v_diff**2)
    
    return np.sqrt(np.sum((c1 - c2)**2))


def filter_image_by_color(image, lower, upper, color_space="HSV"):
    """
    Filtra imagem por faixa de cor.
    
    Args:
        image: Imagem BGR
        lower: Limite inferior
        upper: Limite superior
        color_space: Espaco de cor
        
    Returns:
        numpy.ndarray: Mascara binaria
    """
    if color_space == "HSV":
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    elif color_space == "LAB":
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    else:
        converted = image
        
    lower_array = np.array(lower)
    upper_array = np.array(upper)
    
    mask = cv2.inRange(converted, lower_array, upper_array)
    
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask

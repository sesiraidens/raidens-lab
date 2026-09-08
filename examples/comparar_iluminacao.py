"""
Exemplo de comparacao de ranges em diferentes iluminacoes.

Carrega um range e testa em multiplos niveis de brilho.
"""
import sys
import os
import cv2
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.range_validator import validate_range
from utils.color_converter import load_range


def adjust_brightness(image, factor):
    """
    Ajusta brilho da imagem.
    
    Args:
        image: Imagem BGR
        factor: Fator de brilho (1.0 = original)
        
    Returns:
        numpy.ndarray: Imagem ajustada
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 2] = np.clip(hsv[:, :, 2] * factor, 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Comparar ranges sob diferentes iluminacoes")
    parser.add_argument("--image", type=str, required=True, help="Caminho da imagem")
    parser.add_argument("--config", type=str, required=True, help="Caminho do YAML")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("COMPARACAO DE ILUMINACAO - RAIDENS LAB")
    print("=" * 50)
    print()
    
    image = cv2.imread(args.image)
    if image is None:
        print(f"Erro: Imagem nao encontrada: {args.image}")
        return
        
    data = load_range(args.config)
    lower = data["lower"]
    upper = data["upper"]
    color_space = data.get("color_space", "HSV")
    color_name = data.get("color", "N/A")
    
    print(f"Cor: {color_name}")
    print(f"Espaco: {color_space}")
    print(f"Range: {lower} - {upper}")
    print()
    
    brightness_levels = [0.5, 0.75, 1.0, 1.25, 1.5]
    
    print(f"{'Nivel':<10} {'Pixels %':<12} {'Valido':<8}")
    print("-" * 35)
    
    for factor in brightness_levels:
        adjusted = adjust_brightness(image, factor)
        result = validate_range(adjusted, lower, upper, color_space)
        
        status = "SIM" if result["valid"] else "NAO"
        print(f"{factor:<10.2f} {result['percentage']:<12.1f} {status:<8}")
        
    print()
    print("Niveis de brilho testados:")
    print("  0.5 = metade do brilho (escuro)")
    print("  0.75 = um pouco mais escuro")
    print("  1.0 = original")
    print("  1.25 = um pouco mais claro")
    print("  1.5 = mais claro")


if __name__ == "__main__":
    main()

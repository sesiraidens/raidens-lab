import cv2
import numpy as np
from .color_converter import rgb_to_hsv, rgb_to_lab


def auto_calibrate_hsv(image_path, click_point, region_size=50, margin=2.0):
    """
    Calibracao automatica HSV a partir de um clique na imagem.
    
    Args:
        image_path: Caminho da imagem
        click_point: Tupla (x, y) do ponto clicado
        region_size: Tamanho da regiao de amostragem
        margin: Margem de tolerancia em desvios padrao
        
    Returns:
        dict: Range calibrado com lower e upper
    """
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
        
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    x, y = click_point
    
    y1 = max(0, y - region_size)
    y2 = min(image.shape[0], y + region_size)
    x1 = max(0, x - region_size)
    x2 = min(image.shape[1], x + region_size)
    
    region = hsv[y1:y2, x1:x2]
    
    mean_h = np.mean(region[:, :, 0])
    mean_s = np.mean(region[:, :, 1])
    mean_v = np.mean(region[:, :, 2])
    
    std_h = np.std(region[:, :, 0])
    std_s = np.std(region[:, :, 1])
    std_v = np.std(region[:, :, 2])
    
    lower = [
        max(0, int(mean_h - margin * std_h)),
        max(0, int(mean_s - margin * std_s)),
        max(0, int(mean_v - margin * std_v))
    ]
    
    upper = [
        min(179, int(mean_h + margin * std_h)),
        min(255, int(mean_s + margin * std_s)),
        min(255, int(mean_v + margin * std_v))
    ]
    
    return {"lower": lower, "upper": upper}


def auto_calibrate_lab(image_path, click_point, region_size=50, margin=2.0):
    """
    Calibracao automatica LAB a partir de um clique.
    
    Args:
        image_path: Caminho da imagem
        click_point: Tupla (x, y)
        region_size: Tamanho da regiao
        margin: Margem em desvios padrao
        
    Returns:
        dict: Range calibrado
    """
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
        
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    
    x, y = click_point
    
    y1 = max(0, y - region_size)
    y2 = min(image.shape[0], y + region_size)
    x1 = max(0, x - region_size)
    x2 = min(image.shape[1], x + region_size)
    
    region = lab[y1:y2, x1:x2]
    
    mean_l = np.mean(region[:, :, 0])
    mean_a = np.mean(region[:, :, 1])
    mean_b = np.mean(region[:, :, 2])
    
    std_l = np.std(region[:, :, 0])
    std_a = np.std(region[:, :, 1])
    std_b = np.std(region[:, :, 2])
    
    lower = [
        max(0, int(mean_l - margin * std_l)),
        max(0, int(mean_a - margin * std_a)),
        max(0, int(mean_b - margin * std_b))
    ]
    
    upper = [
        min(255, int(mean_l + margin * std_l)),
        min(255, int(mean_a + margin * std_a)),
        min(255, int(mean_b + margin * std_b))
    ]
    
    return {"lower": lower, "upper": upper}


def auto_calibrate_interactive(image_path, color_space="HSV"):
    """
    Calibracao interativa com selecao de pontos na imagem.
    
    Abre a imagem e permite clicar em multiplos pontos
    para calibrar uma cor.
    
    Args:
        image_path: Caminho da imagem
        color_space: Espaco de cor ("HSV" ou "LAB")
        
    Returns:
        dict: Range calibrado
    """
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
        
    points = []
    
    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            points.append((x, y))
            cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
            cv2.imshow("Selecionar pontos", image)
    
    cv2.imshow("Selecionar pontos", image)
    cv2.setMouseCallback("Selecionar pontos", mouse_callback)
    
    print("Clique nos pontos da cor desejada.")
    print("Pressione qualquer tecla para confirmar.")
    
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    if not points:
        return None
        
    if color_space == "HSV":
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    else:
        converted = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
    all_pixels = []
    
    for x, y in points:
        y1 = max(0, y - 20)
        y2 = min(image.shape[0], y + 20)
        x1 = max(0, x - 20)
        x2 = min(image.shape[1], x + 20)
        
        region = converted[y1:y2, x1:x2]
        pixels = region.reshape(-1, 3)
        all_pixels.append(pixels)
        
    all_pixels = np.vstack(all_pixels)
    
    mean = np.mean(all_pixels, axis=0)
    std = np.std(all_pixels, axis=0)
    
    margin = 2.0
    
    lower = [max(0, int(mean[i] - margin * std[i])) for i in range(3)]
    upper = [min(255 if color_space == "LAB" else [255, 255, 255][i], 
                  int(mean[i] + margin * std[i])) for i in range(3)]
    
    if color_space == "HSV":
        upper[0] = min(179, upper[0])
        
    return {"lower": lower, "upper": upper}


def find_dominant_colors(image_path, n_colors=3, region_size=None):
    """
    Encontra as cores dominantes em uma imagem.
    
    Args:
        image_path: Caminho da imagem
        n_colors: Numero de cores para encontrar
        region_size: Se especificado, analisa apenas uma regiao
        
    Returns:
        list: Lista de cores dominantes em HSV
    """
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
        
    if region_size:
        h, w = image.shape[:2]
        y1 = h // 2 - region_size // 2
        y2 = h // 2 + region_size // 2
        x1 = w // 2 - region_size // 2
        x2 = w // 2 + region_size // 2
        image = image[y1:y2, x1:x2]
        
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    pixels = hsv.reshape(-1, 3).astype(np.float32)
    
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
    _, labels, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, 
                                     cv2.KMEANS_RANDOM_CENTERS)
    
    counts = np.bincount(labels.flatten())
    sorted_indices = np.argsort(-counts)
    
    colors = []
    for idx in sorted_indices:
        center = centers[idx].astype(int)
        percentage = counts[idx] / len(pixels) * 100
        
        colors.append({
            "hsv": center.tolist(),
            "percentage": percentage
        })
        
    return colors

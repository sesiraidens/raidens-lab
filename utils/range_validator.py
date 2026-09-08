import cv2
import numpy as np
import yaml
from .color_converter import filter_image_by_color


def validate_range(image, lower, upper, color_space="HSV", min_percentage=10.0):
    """
    Valida range de cor contra uma imagem.
    
    Args:
        image: Imagem BGR para testar
        lower: Limite inferior
        upper: Limite superior
        color_space: Espaco de cor
        min_percentage: Percentual minimo de pixels detectados
        
    Returns:
        dict: Resultado da validacao
    """
    mask = filter_image_by_color(image, lower, upper, color_space)
    
    total_pixels = mask.shape[0] * mask.shape[1]
    detected_pixels = cv2.countNonZero(mask)
    percentage = (detected_pixels / total_pixels) * 100
    
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    valid = percentage >= min_percentage
    
    return {
        "valid": valid,
        "percentage": percentage,
        "detected_pixels": detected_pixels,
        "total_pixels": total_pixels,
        "num_contours": len(contours),
        "threshold": min_percentage
    }


def validate_range_from_file(image_path, range_path, min_percentage=10.0):
    """
    Valida range a partir de arquivo de imagem e arquivo YAML.
    
    Args:
        image_path: Caminho da imagem
        range_path: Caminho do arquivo YAML com o range
        min_percentage: Percentual minimo aceitavel
        
    Returns:
        dict: Resultado da validacao
    """
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
        
    with open(range_path, "r") as f:
        data = yaml.safe_load(f)
        
    lower = data["lower"]
    upper = data["upper"]
    color_space = data.get("color_space", "HSV")
    
    return validate_range(image, lower, upper, color_space, min_percentage)


def test_range_on_camera(range_path, camera_index=0, duration=5):
    """
    Testa range em tempo real usando camera.
    
    Args:
        range_path: Caminho do arquivo YAML
        camera_index: Indice da camera
        duration: Duracao do teste em segundos
    """
    with open(range_path, "r") as f:
        data = yaml.safe_load(f)
        
    lower = data["lower"]
    upper = data["upper"]
    color_space = data.get("color_space", "HSV")
    color_name = data.get("color", "N/A")
    
    cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("Erro: Camera nao disponivel.")
        return
        
    print(f"Testando range: {color_name}")
    print(f"Espaco: {color_space}")
    print(f"Lower: {lower}")
    print(f"Upper: {upper}")
    print(f"Duracao: {duration}s")
    print("Pressione Q para sair antecipadamente.")
    
    import time
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
            
        mask = filter_image_by_color(frame, lower, upper, color_space)
        masked = cv2.bitwise_and(frame, frame, mask=mask)
        
        total = mask.shape[0] * mask.shape[1]
        detected = cv2.countNonZero(mask)
        pct = (detected / total) * 100
        
        cv2.putText(frame, f"Detectado: {pct:.1f}%", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        cv2.putText(frame, f"Cor: {color_name}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        display = np.hstack([frame, masked])
        cv2.imshow("Range Test", display)
        
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
            
        elapsed = time.time() - start_time
        if elapsed >= duration:
            break
            
    cap.release()
    cv2.destroyAllWindows()
    
    print("Teste finalizado.")


def batch_validate(image_dir, config_dir="configs"):
    """
    Valida todos os ranges contra todas as imagens de um diretorio.
    
    Args:
        image_dir: Diretorio com imagens de teste
        config_dir: Diretorio com arquivos YAML de ranges
        
    Returns:
        list: Lista de resultados
    """
    import os
    
    results = []
    
    config_files = [f for f in os.listdir(config_dir) if f.endswith(".yaml")]
    image_files = [f for f in os.listdir(image_dir) 
                   if f.lower().endswith((".png", ".jpg", ".jpeg"))]
    
    for config_file in config_files:
        config_path = os.path.join(config_dir, config_file)
        
        with open(config_path, "r") as f:
            data = yaml.safe_load(f)
            
        lower = data["lower"]
        upper = data["upper"]
        color_space = data.get("color_space", "HSV")
        color_name = data.get("color", "unknown")
        
        for image_file in image_files:
            image_path = os.path.join(image_dir, image_file)
            
            try:
                image = cv2.imread(image_path)
                
                if image is None:
                    continue
                    
                result = validate_range(image, lower, upper, color_space)
                result["config"] = config_file
                result["image"] = image_file
                result["color"] = color_name
                
                results.append(result)
                
            except Exception as e:
                print(f"Erro ao validar {image_file} com {config_file}: {e}")
                
    return results


def print_validation_report(results):
    """
    Imprime relatorio de validacao.
    
    Args:
        results: Lista de resultados de validacao
    """
    print("\n" + "=" * 60)
    print("RELATORIO DE VALIDACAO DE RANGES")
    print("=" * 60)
    
    valid_count = sum(1 for r in results if r["valid"])
    total_count = len(results)
    
    print(f"\nTotal de testes: {total_count}")
    print(f"Validos: {valid_count}")
    print(f"Invalidos: {total_count - valid_count}")
    print(f"Taxa de sucesso: {(valid_count / total_count * 100):.1f}%")
    
    print("\nDetalhes:")
    print("-" * 60)
    
    for r in results:
        status = "OK" if r["valid"] else "FALHOU"
        print(f"[{status}] {r['config']} vs {r['image']}")
        print(f"         Cor: {r['color']} | Pixels: {r['percentage']:.1f}%")
        
    print("\n" + "=" * 60)

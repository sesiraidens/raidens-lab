import yaml
import os
from datetime import datetime


def generate_yaml(color_name, lower, upper, color_space="HSV", output_dir="configs"):
    """
    Gera arquivo YAML com range de cor.
    
    Args:
        color_name: Nome da cor
        lower: Limite inferior
        upper: Limite superior
        color_space: Espaco de cor (HSV ou LAB)
        output_dir: Diretorio de saida
        
    Returns:
        str: Caminho do arquivo criado
    """
    os.makedirs(output_dir, exist_ok=True)
    
    prefix = color_space.lower()
    filepath = os.path.join(output_dir, f"{prefix}_{color_name}.yaml")
    
    data = {
        "color": color_name,
        "color_space": color_space,
        "lower": list(lower),
        "upper": list(upper),
        "generated_at": datetime.now().isoformat()
    }
    
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
    print(f"Arquivo gerado: {filepath}")
    return filepath


def generate_multi_range_yaml(color_name, ranges, color_space="HSV", output_dir="configs"):
    """
    Gera arquivo YAML com multiplos ranges para uma cor.
    
    Util para cores como vermelho que cobrem faixas distintas no HSV.
    
    Args:
        color_name: Nome da cor
        ranges: Lista de dicionarios com lower e upper
        color_space: Espaco de cor
        output_dir: Diretorio de saida
        
    Returns:
        str: Caminho do arquivo criado
    """
    os.makedirs(output_dir, exist_ok=True)
    
    prefix = color_space.lower()
    filepath = os.path.join(output_dir, f"{prefix}_{color_name}.yaml")
    
    data = {
        "color": color_name,
        "color_space": color_space,
        "ranges": ranges,
        "generated_at": datetime.now().isoformat()
    }
    
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
    print(f"Arquivo gerado: {filepath}")
    return filepath


def merge_ranges(range1, range2):
    """
    Combina dois ranges em um so.
    
    Util quando uma cor tem duas faixas (ex: vermelho em HSV).
    
    Args:
        range1: Primeiro range {"lower": [...], "upper": [...]}
        range2: Segundo range {"lower": [...], "upper": [...]}
        
    Returns:
        dict: Range combinado
    """
    lower = [
        min(range1["lower"][0], range2["lower"][0]),
        min(range1["lower"][1], range2["lower"][1]),
        min(range1["lower"][2], range2["lower"][2])
    ]
    
    upper = [
        max(range1["upper"][0], range2["upper"][0]),
        max(range1["upper"][1], range2["upper"][1]),
        max(range1["upper"][2], range2["upper"][2])
    ]
    
    return {"lower": lower, "upper": upper}


def load_range(filepath):
    """
    Carrega range de cor de arquivo YAML.
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        dict: Range carregado
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
        
    return data


def list_ranges(config_dir="configs"):
    """
    Lista todos os ranges disponiveis em um diretorio.
    
    Args:
        config_dir: Diretorio com arquivos YAML
        
    Returns:
        list: Lista de dicionarios com informacoes dos ranges
    """
    ranges = []
    
    if not os.path.exists(config_dir):
        return ranges
        
    for filename in os.listdir(config_dir):
        if filename.endswith(".yaml"):
            filepath = os.path.join(config_dir, filename)
            try:
                data = load_range(filepath)
                ranges.append({
                    "file": filename,
                    "color": data.get("color", "unknown"),
                    "color_space": data.get("color_space", "unknown")
                })
            except Exception as e:
                print(f"Erro ao ler {filename}: {e}")
                
    return ranges


def format_range_for_display(data):
    """
    Formata range para exibicao no terminal.
    
    Args:
        data: Dicionario com dados do range
        
    Returns:
        str: Range formatado
    """
    color = data.get("color", "N/A")
    color_space = data.get("color_space", "N/A")
    
    if "ranges" in data:
        ranges = data["ranges"]
        parts = []
        for i, r in enumerate(ranges, 1):
            parts.append(f"  Range {i}: {r['lower']} - {r['upper']}")
        ranges_str = "\n".join(parts)
    else:
        lower = data.get("lower", [])
        upper = data.get("upper", [])
        ranges_str = f"  Lower: {lower}\n  Upper: {upper}"
        
    return f"""
Cor: {color}
Espaco: {color_space}
Ranges:
{ranges_str}
"""

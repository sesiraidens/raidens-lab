"""
Exemplo de teste de range de cor em tempo real.

Uso:
    python testar_range.py --config configs/hsv_verde.yaml
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.range_validator import test_range_on_camera


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Testar range de cor")
    parser.add_argument("--config", type=str, required=True, help="Caminho do YAML")
    parser.add_argument("--camera", type=int, default=0, help="Indice da camera")
    parser.add_argument("--duration", type=int, default=10, help="Duracao em segundos")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("TESTE DE RANGE - RAIDENS LAB")
    print("=" * 50)
    print()
    
    if not os.path.exists(args.config):
        print(f"Erro: Arquivo nao encontrado: {args.config}")
        return
        
    test_range_on_camera(args.config, args.camera, args.duration)
    
    print("Teste finalizado.")


if __name__ == "__main__":
    main()

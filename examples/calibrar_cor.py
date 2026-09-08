"""
Exemplo de calibracao HSV interativa.

Uso:
    python calibrar_cor.py --color vermelho --camera 0
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from calibrators.hsv_calibrator import HSVCalibrator


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Calibrar cor HSV")
    parser.add_argument("--camera", type=int, default=0, help="Indice da camera")
    parser.add_argument("--color", type=str, default="vermelho", help="Nome da cor")
    
    args = parser.parse_args()
    
    print("=" * 50)
    print("CALIBRADOR HSV - RAIDENS LAB")
    print("=" * 50)
    print()
    print(f"Cor: {args.color}")
    print(f"Camera: {args.camera}")
    print()
    print("Controles:")
    print("  Ajuste as trackbars para isolar a cor")
    print("  S = Salvar range")
    print("  R = Resetar valores")
    print("  Q = Sair")
    print()
    
    calibrator = HSVCalibrator(camera_index=args.camera)
    calibrator.set_color_name(args.color)
    calibrator.run()
    
    print("Calibracao finalizada.")


if __name__ == "__main__":
    main()

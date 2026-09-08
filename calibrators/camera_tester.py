import cv2
import numpy as np
import yaml
import os
from utils.color_converter import filter_image_by_color, get_color_name


class CameraTester:
    """
    Testador de ranges de cor em tempo real.
    
    Carrega ranges de cor de arquivos YAML e testa
    em captura de camera ao vivo.
    """
    
    def __init__(self, camera_index=0):
        """
        Inicializa o testador.
        
        Args:
            camera_index: Indice da camera
        """
        self.camera_index = camera_index
        self.cap = None
        self.ranges = {}
        
    def load_range(self, filepath):
        """
        Carrega range de cor de arquivo YAML.
        
        Args:
            filepath: Caminho do arquivo
        """
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
            
        color_name = data.get("color", "unknown")
        self.ranges[color_name] = {
            "lower": data["lower"],
            "upper": data["upper"],
            "color_space": data.get("color_space", "HSV")
        }
        
        print(f"Range carregado: {color_name} ({filepath})")
        
    def load_all_ranges(self, config_dir="configs"):
        """
        Carrega todos os ranges de um diretorio.
        
        Args:
            config_dir: Diretorio com arquivos YAML
        """
        if not os.path.exists(config_dir):
            print(f"Diretorio nao encontrado: {config_dir}")
            return
            
        for filename in os.listdir(config_dir):
            if filename.endswith(".yaml"):
                filepath = os.path.join(config_dir, filename)
                try:
                    self.load_range(filepath)
                except Exception as e:
                    print(f"Erro ao carregar {filename}: {e}")
                    
    def run(self):
        """
        Inicia teste em tempo real.
        
        Exibe janela com deteccao de cores.
        Pressione Q para sair.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Erro: Camera nao disponivel.")
            return
            
        print(f"Ranges carregados: {len(self.ranges)}")
        print("Pressione Q para sair.")
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
                
            display = frame.copy()
            
            colors = list(self.ranges.keys())
            y_offset = 30
            
            for color_name in colors:
                color_data = self.ranges[color_name]
                lower = color_data["lower"]
                upper = color_data["upper"]
                color_space = color_data["color_space"]
                
                mask = filter_image_by_color(frame, lower, upper, color_space)
                
                total = mask.shape[0] * mask.shape[1]
                detected = cv2.countNonZero(mask)
                pct = (detected / total) * 100
                
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, 
                                                cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if area > 500:
                        x, y, w, h = cv2.boundingRect(contour)
                        cv2.rectangle(display, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        M = cv2.moments(contour)
                        if M["m00"] != 0:
                            cx = int(M["m10"] / M["m00"])
                            cy = int(M["m01"] / M["m00"])
                            cv2.putText(display, color_name, (cx-20, cy),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                text = f"{color_name}: {pct:.1f}% ({len(contours)} obj)"
                cv2.putText(display, text, (10, y_offset),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                y_offset += 25
                
            cv2.imshow("Camera Tester", display)
            
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
                
        self.cap.release()
        cv2.destroyAllWindows()
        
    def test_single_frame(self, frame):
        """
        Testa ranges em um unico frame.
        
        Args:
            frame: Frame BGR
            
        Returns:
            dict: Resultados por cor
        """
        results = {}
        
        for color_name, color_data in self.ranges.items():
            lower = color_data["lower"]
            upper = color_data["upper"]
            color_space = color_data["color_space"]
            
            mask = filter_image_by_color(frame, lower, upper, color_space)
            
            total = mask.shape[0] * mask.shape[1]
            detected = cv2.countNonZero(mask)
            pct = (detected / total) * 100
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                            cv2.CHAIN_APPROX_SIMPLE)
            
            objects = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 500:
                    x, y, w, h = cv2.boundingRect(contour)
                    M = cv2.moments(contour)
                    if M["m00"] != 0:
                        cx = int(M["m10"] / M["m00"])
                        cy = int(M["m01"] / M["m00"])
                    else:
                        cx, cy = x + w//2, y + h//2
                        
                    objects.append({
                        "area": area,
                        "center": (cx, cy),
                        "bbox": (x, y, w, h)
                    })
                    
            results[color_name] = {
                "percentage": pct,
                "num_objects": len(objects),
                "objects": objects
            }
            
        return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Testador de ranges de cor")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--config-dir", type=str, default="configs")
    
    args = parser.parse_args()
    
    tester = CameraTester(camera_index=args.camera)
    tester.load_all_ranges(args.config_dir)
    tester.run()

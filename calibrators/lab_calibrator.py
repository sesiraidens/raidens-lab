import cv2
import numpy as np
import yaml
import os
from datetime import datetime


class LABCalibrator:
    """
    Calibrador interativo de cores no espaco LAB.
    
    LAB separa luminancia (L) de crominancia (A, B),
    sendo mais robusto a variacoes de iluminacao que HSV.
    
    Uso:
        calibrator = LABCalibrator(camera_index=0)
        calibrator.run()
    """
    
    def __init__(self, camera_index=0, window_name="LAB Calibrator"):
        """
        Inicializa o calibrador.
        
        Args:
            camera_index: Indice da camera
            window_name: Nome da janela
        """
        self.camera_index = camera_index
        self.window_name = window_name
        self.cap = None
        
        self.l_min = 0
        self.l_max = 255
        self.a_min = 0
        self.a_max = 255
        self.b_min = 0
        self.b_max = 255
        
        self.current_color_name = "cor_lab"
        
    def _create_trackbars(self):
        """Cria trackbars para os canais L, A e B."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 800, 400)
        
        cv2.createTrackbar("L Min", self.window_name, self.l_min, 255, lambda x: None)
        cv2.createTrackbar("L Max", self.window_name, self.l_max, 255, lambda x: None)
        cv2.createTrackbar("A Min", self.window_name, self.a_min, 255, lambda x: None)
        cv2.createTrackbar("A Max", self.window_name, self.a_max, 255, lambda x: None)
        cv2.createTrackbar("B Min", self.window_name, self.b_min, 255, lambda x: None)
        cv2.createTrackbar("B Max", self.window_name, self.b_max, 255, lambda x: None)
        
    def _get_trackbar_values(self):
        """Le valores das trackbars."""
        self.l_min = cv2.getTrackbarPos("L Min", self.window_name)
        self.l_max = cv2.getTrackbarPos("L Max", self.window_name)
        self.a_min = cv2.getTrackbarPos("A Min", self.window_name)
        self.a_max = cv2.getTrackbarPos("A Max", self.window_name)
        self.b_min = cv2.getTrackbarPos("B Min", self.window_name)
        self.b_max = cv2.getTrackbarPos("B Max", self.window_name)
        
    def _apply_mask(self, frame):
        """
        Aplica mascara no espaco LAB.
        
        Args:
            frame: Frame BGR
            
        Returns:
            tuple: (mascara, frame_mascarado)
        """
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        
        lower = np.array([self.l_min, self.a_min, self.b_min])
        upper = np.array([self.l_max, self.a_max, self.b_max])
        
        mask = cv2.inRange(lab, lower, upper)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        masked = cv2.bitwise_and(frame, frame, mask=mask)
        
        return mask, masked
    
    def _draw_info(self, frame, mask):
        """Desenha informacoes na janela."""
        h, w = mask.shape
        total_pixels = h * w
        white_pixels = cv2.countNonZero(mask)
        percentage = (white_pixels / total_pixels) * 100
        
        info_text = f"Pixels detectados: {percentage:.1f}%"
        cv2.putText(frame, info_text, (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        range_text = f"Range: L[{self.l_min}-{self.l_max}] A[{self.a_min}-{self.a_max}] B[{self.b_min}-{self.b_max}]"
        cv2.putText(frame, range_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        controls = "S=Save | Q=Quit | R=Reset"
        cv2.putText(frame, controls, (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    def _save_range(self, filepath=None):
        """Salva range em arquivo YAML."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"lab_{self.current_color_name}_{timestamp}.yaml"
            
        data = {
            "color": self.current_color_name,
            "color_space": "LAB",
            "lower": [self.l_min, self.a_min, self.b_min],
            "upper": [self.l_max, self.a_max, self.b_max],
            "calibrated_at": datetime.now().isoformat()
        }
        
        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
            
        print(f"Range salvo em: {filepath}")
        
    def _reset_values(self):
        """Reseta trackbars."""
        cv2.setTrackbarPos("L Min", self.window_name, 0)
        cv2.setTrackbarPos("L Max", self.window_name, 255)
        cv2.setTrackbarPos("A Min", self.window_name, 0)
        cv2.setTrackbarPos("A Max", self.window_name, 255)
        cv2.setTrackbarPos("B Min", self.window_name, 0)
        cv2.setTrackbarPos("B Max", self.window_name, 255)
        
    def set_color_name(self, name):
        """Define nome da cor."""
        self.current_color_name = name
        
    def run(self):
        """
        Inicia loop principal do calibrador.
        
        Controles:
            S: Salvar
            Q: Sair
            R: Resetar
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Erro: Camera nao disponivel.")
            return
            
        self._create_trackbars()
        
        print(f"Calibrador LAB iniciado.")
        print(f"Cor: {self.current_color_name}")
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                break
                
            self._get_trackbar_values()
            mask, masked = self._apply_mask(frame)
            self._draw_info(frame, mask)
            
            display = np.hstack([frame, masked])
            cv2.imshow(self.window_name, display)
            
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord("q"):
                break
            elif key == ord("s"):
                self._save_range()
            elif key == ord("r"):
                self._reset_values()
                
        self.cap.release()
        cv2.destroyAllWindows()
        
    def calibrate_from_image(self, image_path, click_point):
        """
        Calibracao automatica a partir de clique na imagem.
        
        Args:
            image_path: Caminho da imagem
            click_point: Tupla (x, y)
            
        Returns:
            dict: Range calibrado
        """
        image = cv2.imread(image_path)
        
        if image is None:
            raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
            
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        x, y = click_point
        region_size = 50
        
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
        
        margin = 2
        
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
        
        self.l_min, self.a_min, self.b_min = lower
        self.l_max, self.a_max, self.b_max = upper
        
        return {"lower": lower, "upper": upper}


def load_lab_ranges(filepath):
    """
    Carrega ranges LAB de arquivo YAML.
    
    Args:
        filepath: Caminho do arquivo
        
    Returns:
        dict: Lower e upper bounds
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
        
    return {
        "lower": data["lower"],
        "upper": data["upper"]
    }


def save_lab_range(color_name, lower, upper, output_dir="configs"):
    """
    Salva range LAB em arquivo YAML.
    
    Args:
        color_name: Nome da cor
        lower: Limite inferior [L, A, B]
        upper: Limite superior [L, A, B]
        output_dir: Diretorio de saida
    """
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, f"lab_{color_name}.yaml")
    
    data = {
        "color": color_name,
        "color_space": "LAB",
        "lower": lower,
        "upper": upper
    }
    
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
        
    print(f"Range salvo: {filepath}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Calibrador LAB de cores")
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--color", type=str, default="cor_lab")
    
    args = parser.parse_args()
    
    calibrator = LABCalibrator(camera_index=args.camera)
    calibrator.set_color_name(args.color)
    calibrator.run()

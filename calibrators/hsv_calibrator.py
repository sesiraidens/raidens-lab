import cv2
import numpy as np
import yaml
import os
from datetime import datetime


class HSVCalibrator:
    """
    Calibrador interativo de cores no espaco HSV.
    
    Abre janela com captura de camera e trackbars para ajuste
    de ranges de cor. Permite salvar ranges em arquivo YAML.
    
    Uso:
        calibrator = HSVCalibrator(camera_index=0)
        calibrator.run()
    """
    
    def __init__(self, camera_index=0, window_name="HSV Calibrator"):
        """
        Inicializa o calibrador.
        
        Args:
            camera_index: Indice da camera (0 para webcam padrao)
            window_name: Nome da janela de exibicao
        """
        self.camera_index = camera_index
        self.window_name = window_name
        self.cap = None
        
        self.h_min = 0
        self.h_max = 179
        self.s_min = 0
        self.s_max = 255
        self.v_min = 0
        self.v_max = 255
        
        self.current_color_name = "cor_calibrada"
        
    def _create_trackbars(self):
        """Cria as trackbars na janela."""
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, 800, 400)
        
        cv2.createTrackbar("H Min", self.window_name, self.h_min, 179, lambda x: None)
        cv2.createTrackbar("H Max", self.window_name, self.h_max, 179, lambda x: None)
        cv2.createTrackbar("S Min", self.window_name, self.s_min, 255, lambda x: None)
        cv2.createTrackbar("S Max", self.window_name, self.s_max, 255, lambda x: None)
        cv2.createTrackbar("V Min", self.window_name, self.v_min, 255, lambda x: None)
        cv2.createTrackbar("V Max", self.window_name, self.v_max, 255, lambda x: None)
        
    def _get_trackbar_values(self):
        """Le valores atuais das trackbars."""
        self.h_min = cv2.getTrackbarPos("H Min", self.window_name)
        self.h_max = cv2.getTrackbarPos("H Max", self.window_name)
        self.s_min = cv2.getTrackbarPos("S Min", self.window_name)
        self.s_max = cv2.getTrackbarPos("S Max", self.window_name)
        self.v_min = cv2.getTrackbarPos("V Min", self.window_name)
        self.v_max = cv2.getTrackbarPos("V Max", self.window_name)
        
    def _apply_mask(self, frame):
        """
        Aplica mascara HSV no frame.
        
        Args:
            frame: Frame BGR da camera
            
        Returns:
            tuple: (mascara, frame_mascarado)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower = np.array([self.h_min, self.s_min, self.v_min])
        upper = np.array([self.h_max, self.s_max, self.v_max])
        
        mask = cv2.inRange(hsv, lower, upper)
        
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        
        masked = cv2.bitwise_and(frame, frame, mask=mask)
        
        return mask, masked
    
    def _draw_info(self, frame, mask):
        """
        Desenha informacoes na janela.
        
        Args:
            frame: Frame original
            mask: Mascara resultante
        """
        h, w = mask.shape
        total_pixels = h * w
        white_pixels = cv2.countNonZero(mask)
        percentage = (white_pixels / total_pixels) * 100
        
        info_text = f"Pixels detectados: {percentage:.1f}%"
        cv2.putText(frame, info_text, (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        range_text = f"Range: H[{self.h_min}-{self.h_max}] S[{self.s_min}-{self.s_max}] V[{self.v_min}-{self.v_max}]"
        cv2.putText(frame, range_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        controls = "S=Save | Q=Quit | R=Reset"
        cv2.putText(frame, controls, (10, h - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    def _get_limits(self):
        """Retorna limites atuais como dicionario."""
        return {
            "lower": [self.h_min, self.s_min, self.v_min],
            "upper": [self.h_max, self.s_max, self.v_max]
        }
        
    def _save_range(self, filepath=None):
        """
        Salva range atual em arquivo YAML.
        
        Args:
            filepath: Caminho do arquivo. Se None, gera automatico.
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"hsv_{self.current_color_name}_{timestamp}.yaml"
            
        data = {
            "color": self.current_color_name,
            "color_space": "HSV",
            "lower": self._get_limits()["lower"],
            "upper": self._get_limits()["upper"],
            "calibrated_at": datetime.now().isoformat()
        }
        
        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
            
        print(f"Range salvo em: {filepath}")
        
    def _reset_values(self):
        """Reseta trackbars para valores padrao."""
        cv2.setTrackbarPos("H Min", self.window_name, 0)
        cv2.setTrackbarPos("H Max", self.window_name, 179)
        cv2.setTrackbarPos("S Min", self.window_name, 0)
        cv2.setTrackbarPos("S Max", self.window_name, 255)
        cv2.setTrackbarPos("V Min", self.window_name, 0)
        cv2.setTrackbarPos("V Max", self.window_name, 255)
        
    def set_color_name(self, name):
        """
        Define nome da cor para salvar.
        
        Args:
            name: Nome da cor (ex: "vermelho", "verde")
        """
        self.current_color_name = name
        
    def run(self):
        """
        Inicia o loop principal do calibrador.
        
        Controles:
            S: Salvar range atual
            Q: Sair
            R: Resetar valores
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        
        if not self.cap.isOpened():
            print("Erro: Nao foi possivel abrir a camera.")
            return
            
        self._create_trackbars()
        
        print(f"Calibrador HSV iniciado.")
        print(f"Cor: {self.current_color_name}")
        print(f"Pressione S para salvar, Q para sair, R para resetar.")
        
        while True:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Erro ao ler frame da camera.")
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
        Calibracao automatica a partir de um clique na imagem.
        
        Args:
            image_path: Caminho da imagem
            click_point: Tupla (x, y) do ponto clicado
            
        Returns:
            dict: Range calibrado
        """
        image = cv2.imread(image_path)
        
        if image is None:
            raise FileNotFoundError(f"Imagem nao encontrada: {image_path}")
            
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        x, y = click_point
        region_size = 50
        
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
        
        margin = 2
        
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
        
        self.h_min, self.s_min, self.v_min = lower
        self.h_max, self.s_max, self.v_max = upper
        
        return {"lower": lower, "upper": upper}


def load_hsv_ranges(filepath):
    """
    Carrega ranges HSV de arquivo YAML.
    
    Args:
        filepath: Caminho do arquivo YAML
        
    Returns:
        dict: Dicionario com lower e upper bounds
    """
    with open(filepath, "r") as f:
        data = yaml.safe_load(f)
        
    return {
        "lower": data["lower"],
        "upper": data["upper"]
    }


def save_hsv_range(color_name, lower, upper, output_dir="configs"):
    """
    Salva range HSV em arquivo YAML.
    
    Args:
        color_name: Nome da cor
        lower: Limite inferior [H, S, V]
        upper: Limite superior [H, S, V]
        output_dir: Diretorio de saida
    """
    os.makedirs(output_dir, exist_ok=True)
    
    filepath = os.path.join(output_dir, f"hsv_{color_name}.yaml")
    
    data = {
        "color": color_name,
        "color_space": "HSV",
        "lower": lower,
        "upper": upper
    }
    
    with open(filepath, "w") as f:
        yaml.dump(data, f, default_flow_style=False)
        
    print(f"Range salvo: {filepath}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Calibrador HSV de cores")
    parser.add_argument("--camera", type=int, default=0, help="Indice da camera")
    parser.add_argument("--color", type=str, default="cor_calibrada", help="Nome da cor")
    
    args = parser.parse_args()
    
    calibrator = HSVCalibrator(camera_index=args.camera)
    calibrator.set_color_name(args.color)
    calibrator.run()

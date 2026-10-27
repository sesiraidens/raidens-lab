<div align="center">

<img src="https://sesiraidens.github.io/portifolio/assets/logo_color-aNRVU26Y.png" alt="Logo RAIDENS" width="140">

# raidens-lab

**Calibração de cores em HSV e LAB para visão computacional confiável em qualquer iluminação**

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![YAML](https://img.shields.io/badge/Configs-YAML-CB171E?style=flat-square&logo=yaml&logoColor=white)
![Licença MIT](https://img.shields.io/badge/Licen%C3%A7a-MIT-D9333B?style=flat-square)

[Sobre](#sobre) · [Instalação](#instalação) · [Início rápido](#início-rápido) · [Ferramentas](#ferramentas) · [Dicas](#dicas-de-calibração)

</div>

---

## Sobre

Uma cor que o robô reconhece perfeitamente no laboratório pode sumir na arena da competição. Iluminação, ângulo da câmera, sombras e reflexos mudam os valores que a câmera enxerga. O **raidens-lab** existe para resolver isso: ele ajuda a encontrar os ranges certos *no local da prova* e os salva em YAML para que o código do robô só precise carregá-los.

### HSV ou LAB?

| Espaço | Quando usar |
|---|---|
| **HSV** | Ambientes com luz estável. É intuitivo de ajustar pelo matiz (H). |
| **LAB** | Ambientes com sombras ou luz variável. Separa a luminosidade (L) da cor (A e B), então é mais robusto. |

## Instalação

```bash
git clone https://github.com/sesiraidens/raidens-lab.git
cd raidens-lab
pip install "opencv-python>=4.5" "numpy>=1.19" "pyyaml>=5.0"
```

## Início rápido

**1. Calibre a cor com a câmera**

```bash
python calibrators/hsv_calibrator.py --camera 0 --color vermelho
```

Ajuste as seis barras (H, S e V mínimos e máximos) até a máscara mostrar só a cor desejada.

| Tecla | Ação |
|---|---|
| `S` | Salvar o range em `configs/` |
| `R` | Resetar as barras |
| `Q` | Sair |

**2. Teste o range em tempo real**

```bash
python examples/testar_range.py --config configs/hsv_verde.yaml --camera 0 --duration 10
```

**3. Verifique a robustez a mudanças de luz**

```bash
python examples/comparar_iluminacao.py --image foto.jpg --config configs/hsv_vermelho.yaml
```

## Ferramentas

### Calibradores interativos

| Classe | O que faz |
|---|---|
| `HSVCalibrator` | Barras deslizantes em HSV sobre a imagem da câmera |
| `LABCalibrator` | O mesmo fluxo no espaço LAB |
| `CameraTester` | Carrega todos os YAML de `configs/` e mostra contornos, centróides e percentual detectado de cada cor |

```python
from calibrators.hsv_calibrator import HSVCalibrator
from calibrators.camera_tester import CameraTester

calibrador = HSVCalibrator(camera_index=0)
calibrador.set_color_name("verde")
calibrador.run()

tester = CameraTester(camera_index=0)
tester.load_all_ranges("configs")
tester.run()
```

### Utilitários

| Módulo | Funções |
|---|---|
| `utils/color_converter.py` | Conversões entre RGB, HSV, LAB e hexadecimal; `get_color_name`, `compare_colors`, `filter_image_by_color` |
| `utils/range_generator.py` | `generate_yaml`, `generate_multi_range_yaml`, `merge_ranges`, `load_range`, `list_ranges` |
| `utils/range_validator.py` | `validate_range`, `validate_range_from_file`, `test_range_on_camera`, `batch_validate`, `print_validation_report` |
| `utils/auto_calibrator.py` | `auto_calibrate_hsv` e `auto_calibrate_lab` a partir de um clique, `auto_calibrate_interactive`, `find_dominant_colors` (k-means) |

### Faixas de valores no OpenCV

| Espaço | Canal | Faixa |
|---|---|---|
| HSV | H (matiz) | 0 a 179 |
| HSV | S (saturação) e V (valor) | 0 a 255 |
| LAB | L (luminosidade), A (verde ↔ vermelho) e B (azul ↔ amarelo) | 0 a 255 |

## Ranges pré-definidos

| Arquivo | Cor | Espaço |
|---|---|---|
| `hsv_vermelho.yaml` | Vermelho | HSV, faixa baixa (0 a 10) |
| `hsv_vermelho_2.yaml` | Vermelho | HSV, faixa alta (170 a 179) |
| `hsv_verde.yaml` | Verde | HSV (35 a 85) |
| `hsv_azul.yaml` | Azul | HSV (100 a 130) |
| `hsv_amarelo.yaml` | Amarelo | HSV (20 a 35) |
| `lab_vermelho.yaml` | Vermelho | LAB |
| `lab_verde.yaml` | Verde | LAB |

## Dicas de calibração

1. **Calibre onde vai competir.** A luz da arena raramente é igual à do laboratório.
2. **Mantenha o ângulo da câmera** igual na calibração e no uso.
3. **Deixe margem.** Cerca de dois desvios-padrão em torno da média cobre as variações normais.
4. **O vermelho precisa de dois ranges em HSV**, porque o matiz "dá a volta" entre 179 e 0.
5. **Muita sombra? Prefira LAB.**

## Estrutura

```text
raidens-lab/
├── calibrators/   # Ferramentas interativas com câmera
├── utils/         # Conversão, geração, validação e calibração automática
├── configs/       # Ranges prontos em YAML
└── examples/      # Scripts de linha de comando
```

## Ecossistema RAIDENS

Este repositório faz parte de um conjunto de bibliotecas da equipe. Elas usam os mesmos nomes de classes e convenções, então o que você aprende em uma serve nas outras.

| Repositório | Para quê |
|---|---|
| [`raidens-python`](https://github.com/sesiraidens/raidens-python) | Biblioteca principal em Python: sensores, motores e robôs prontos (seguidor, parede, resgate) |
| [`raidens-arduino`](https://github.com/sesiraidens/raidens-arduino) | As mesmas abstrações em C++ para rodar direto no Arduino |
| [`raidens-sensores`](https://github.com/sesiraidens/raidens-sensores) | Catálogo completo de sensores com calibração e filtragem |
| [`raidens-motores`](https://github.com/sesiraidens/raidens-motores) | Motores DC, servo, passo, driver L298N e rodas mecanum |
| [`raidens-pid`](https://github.com/sesiraidens/raidens-pid) | Controladores PID, PID avançado, cascata e sintonia Ziegler-Nichols |
| [`raidens-opencv`](https://github.com/sesiraidens/raidens-opencv) | Visão computacional: cores, linhas e navegação por câmera |
| [`raidens-obr`](https://github.com/sesiraidens/raidens-obr) | Robô completo para a OBR, integrando sensores, motores e missões |
| [`raidens-electronics`](https://github.com/sesiraidens/raidens-electronics) | Cálculos e modelos de componentes eletrônicos |
| [`raidens-3d`](https://github.com/sesiraidens/raidens-3d) | Peças 3D paramétricas geradas em OpenSCAD |
| [`raidens-ros`](https://github.com/sesiraidens/raidens-ros) | Estrutura de nodes e tópicos ROS 2 |
| [`raidens-snippets`](https://github.com/sesiraidens/raidens-snippets) | Trechos de código prontos para copiar e colar |

---

<div align="center">

<img src="https://sesiraidens.github.io/portifolio/assets/logo_color-aNRVU26Y.png" alt="Logo RAIDENS" width="56">

**Equipe RAIDENS** · SESI 192 Alumínio/SP

[![Email](https://img.shields.io/badge/Email-sesiraidens%40gmail.com-D14836?style=flat-square&logo=gmail&logoColor=white)](mailto:sesiraidens@gmail.com)
[![Linktree](https://img.shields.io/badge/Linktree-sesiraidens-39E06B?style=flat-square&logo=linktree&logoColor=white)](https://linktr.ee/sesiraidens)
[![GitHub](https://img.shields.io/badge/GitHub-sesiraidens-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/sesiraidens)

<sub>Desenvolvido pela equipe RAIDENS para fins educacionais. Licenciado sob MIT.</sub>

</div>


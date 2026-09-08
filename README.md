<div align="center">

<img src="https://sesiraidens.github.io/portifolio/assets/logo_color-aNRVU26Y.png" width="80">

# raidens-lab

Ferramentas de calibracao de cores nos espacos LAB e HSV para visao computacional.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-d9333b?style=flat)
![Status](https://img.shields.io/badge/Status-Active-2ea043?style=flat)

</div>

---

## Sobre

O **raidens-lab** reune ferramentas para calibracao de cores utilizadas em projetos de visao computacional da equipe RAIDENS. A calibracao e essencial para que o robo identifique cores de forma confiavel em diferentes condicoes de iluminacao.

### Por que calibrar?

Sensores de cor (TCS3200, TCS34725) e cameras dependem de ranges de cor para identificar objetos. Esses ranges variam conforme:
- Iluminacao do ambiente (interna vs externa)
- Angulo da camera em relacao ao objeto
- Cor do objeto (tons diferentes de vermelho)
- Presenca de sombras ou reflexos

O raidens-lab oferece ferramentas interativas para encontrar ranges otimos e salva-los em formato YAML para reutilizacao.

---

## Estrutura

`
raidens-lab/
├── calibrators/
│   ├── hsv_calibrator.py      # Calibrador interativo HSV
│   ├── lab_calibrator.py      # Calibrador interativo LAB
│   ├── camera_tester.py       # Teste de ranges em tempo real
│   └── __init__.py
├── utils/
│   ├── color_converter.py     # Conversao RGB/HSV/LAB
│   ├── range_generator.py     # Gerador de ranges YAML
│   ├── range_validator.py     # Validador de ranges
│   ├── auto_calibrator.py     # Calibracao automatica
│   └── __init__.py
├── configs/
│   ├── hsv_vermelho.yaml      # Range HSV vermelho
│   ├── hsv_vermelho_2.yaml    # Range HSV vermelho (faixa alta)
│   ├── hsv_verde.yaml         # Range HSV verde
│   ├── hsv_azul.yaml          # Range HSV azul
│   ├── hsv_amarelo.yaml       # Range HSV amarelo
│   ├── lab_vermelho.yaml      # Range LAB vermelho
│   └── lab_verde.yaml         # Range LAB verde
├── examples/
│   ├── calibrar_cor.py        # Exemplo de calibracao
│   ├── testar_range.py        # Exemplo de teste
│   └── comparar_iluminacao.py # Teste de robustez
└── README.md
`

---

## Modulos

### calibrators/hsv_calibrator.py

Calibrador interativo de cores no espaco HSV.

**Como funciona:**
1. Abre janela com captura de camera em tempo real
2. Exibe seis trackbars (H_min, H_max, S_min, S_max, V_min, V_max)
3. Usuario ajusta ate a mascara cobrir apenas a cor desejada
4. Pressiona S para salvar em YAML

**Controles:**
- S: Salvar range atual
- R: Resetar trackbars
- Q: Sair

**Uso via terminal:**
`ash
python calibrators/hsv_calibrator.py --camera 0 --color vermelho
`

**Uso como modulo:**
`python
from calibrators.hsv_calibrator import HSVCalibrator

calibrator = HSVCalibrator(camera_index=0)
calibrator.set_color_name("verde")
calibrator.run()
`

### calibrators/lab_calibrator.py

Calibrador interativo no espaco LAB.

**Vantagem do LAB sobre HSV:**
- LAB separa luminancia (L) de crominancia (A, B)
- Mais robusto a variacoes de iluminacao
- Melhor para ambientes com sombras

**Uso:**
`python
from calibrators.lab_calibrator import LABCalibrator

calibrator = LABCalibrator()
calibrator.set_color_name("vermelho")
calibrator.run()
`

### calibrators/camera_tester.py

Teste de ranges em tempo real.

**Funcionalidades:**
- Carrega multiplos ranges de diretorio configs/
- Exibe deteccao de cores com contornos e centroides
- Mostra percentual de pixels detectados por cor

**Uso:**
`python
from calibrators.camera_tester import CameraTester

tester = CameraTester(camera_index=0)
tester.load_all_ranges("configs")
tester.run()
`

### utils/color_converter.py

Conversao entre espacos de cor e funcoes auxiliares.

**Funcoes principais:**
- gb_to_hsv(r, g, b) - Converte RGB para HSV
- gb_to_lab(r, g, b) - Converte RGB para LAB
- hsv_to_rgb(h, s, v) - Converte HSV para RGB
- hex_to_rgb(hex_color) - Converte hexadecimal para RGB
- get_color_name(h, s, v) - Retorna nome aproximado da cor
- get_color_ranges() - Retorna ranges pre-definidos para cores comuns
- compare_colors(c1, c2) - Calcula distancia entre duas cores
- ilter_image_by_color(image, lower, upper) - Filtra imagem por cor

**Faixas de valores:**

| Espaco | Canal | Min | Max |
|---|---|---|---|
| HSV | H (Hue) | 0 | 179 |
| HSV | S (Saturation) | 0 | 255 |
| HSV | V (Value) | 0 | 255 |
| LAB | L (Lightness) | 0 | 255 |
| LAB | A (Green-Red) | 0 | 255 |
| LAB | B (Blue-Yellow) | 0 | 255 |

### utils/range_generator.py

Gerador de arquivos YAML com ranges de cor.

**Funcoes:**
- generate_yaml(color_name, lower, upper) - Gera arquivo YAML
- generate_multi_range_yaml(color_name, ranges) - Gera com multiplos ranges
- merge_ranges(range1, range2) - Combina dois ranges
- load_range(filepath) - Carrega range de arquivo
- list_ranges(config_dir) - Lista ranges disponiveis

### utils/range_validator.py

Validador de ranges contra imagens e camera.

**Funcoes:**
- alidate_range(image, lower, upper) - Valida range contra imagem
- alidate_range_from_file(image_path, range_path) - Valida a partir de arquivos
- 	est_range_on_camera(range_path) - Testa em tempo real
- atch_validate(image_dir, config_dir) - Valida multiplos ranges
- print_validation_report(results) - Imprime relatorio

### utils/auto_calibrator.py

Calibracao automatica por amostragem de pixels.

**Funcoes:**
- uto_calibrate_hsv(image_path, click_point) - Calibracao HSV automatica
- uto_calibrate_lab(image_path, click_point) - Calibracao LAB automatica
- uto_calibrate_interactive(image_path) - Calibracao com multiplos cliques
- ind_dominant_colors(image_path, n_colors) - Encontra cores dominantes via kmeans

---

## Dependencias

`
opencv-python>=4.5.0
numpy>=1.19.0
pyyaml>=5.0
`

**Instalacao:**
`ash
pip install opencv-python numpy pyyaml
`

---

## Como Usar

### Calibracao basica

1. Rode o calibrador HSV:
`ash
python calibrators/hsv_calibrator.py --color vermelho
`

2. Ajuste as trackbars para isolar a cor desejada
3. Pressione S para salvar
4. O arquivo YAML sera gerado em configs/

### Teste de range

1. Rode o testador:
`ash
python examples/testar_range.py --config configs/hsv_verde.yaml
`

2. Aponte a camera para o objeto
3. Verifique o percentual de deteccao

### Comparacao de iluminacao

1. Rode o comparador:
`ash
python examples/comparar_iluminacao.py --image foto.jpg --config configs/hsv_vermelho.yaml
`

2. Verifique se o range funciona em diferentes niveis de brilho

---

## Configs Pre-Definidos

| Arquivo | Cor | Espaco |
|---|---|---|
| hsv_vermelho.yaml | Vermelho | HSV (0-10) |
| hsv_vermelho_2.yaml | Vermelho | HSV (170-179) |
| hsv_verde.yaml | Verde | HSV (35-85) |
| hsv_azul.yaml | Azul | HSV (100-130) |
| hsv_amarelo.yaml | Amarelo | HSV (20-35) |
| lab_vermelho.yaml | Vermelho | LAB |
| lab_verde.yaml | Verde | LAB |

---

## Dicas de Calibracao

1. **Iluminacao constante:** Calibre na mesma iluminacao que usara na competicao
2. **Angulo consistente:** Mantenha a camera no mesmo angulo durante calibracao e uso
3. **Margem de seguranca:** Use margem de 2 desvios padrao para cobrir variacoes
4. **Vermelho em HSV:** Precisa de dois ranges (0-10 e 170-179) por causa da divisao do Hue
5. **LAB para sombras:** Se o ambiente tem muitas sombras, prefira LAB

---

## Equipe

**RAIDENS - SESI Aluminio 192**

Desenvolvido para uso interno da equipe. Licenciado sob MIT.
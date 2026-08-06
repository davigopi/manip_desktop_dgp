# manip_desktop_dgp

Biblioteca Python para automação desktop.

A biblioteca reúne diversas funções utilizadas em automações Windows, como:

- Captura de tela utilizando MSS
- Localização de imagens via OpenCV
- Localização de imagens via PyAutoGUI
- OCR utilizando Tesseract
- Clique automático do mouse
- Abertura e fechamento de programas
- Utilitários para manipulação de tela

---

# Tutorial de Instalação

## 1. Criar o repositório

Crie um repositório no GitHub.

Exemplo:

https://github.com/davigopi/manip_desktop_dgp

Depois envie todos os arquivos do projeto.

---

## 2. Estrutura do projeto

A estrutura recomendada é:

```

manip_desktop_dgp/

├── manip_desktop_dgp.py
├── pyproject.toml
├── README.md
├── LICENSE
└── img/
├── capturadas/
└── ...

```

---

## 3. Criar o arquivo pyproject.toml

Exemplo:

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "manip_desktop_dgp"
version = "0.1.0"

dependencies = [
    "numpy",
    "opencv-python",
    "pyautogui",
    "psutil",
    "mss",
    "pytesseract",
    "Pillow"
]

[tool.setuptools]
py-modules = ["manip_desktop_dgp"]
```

---

# 4. Publicar no GitHub

Após criar o projeto:

```
git init

git add .

git commit -m "Primeira versão"

git branch -M main

git remote add origin https://github.com/davigopi/manip_desktop_dgp.git

git push -u origin main
```

---

# 5. Instalar em qualquer computador

Execute:


```
pip install git+https://github.com/davigopi/manip_desktop_dgp.git
```

---

# 6. Atualizar para a última versão

Sempre que fizer alterações:

```
git add .

git commit -m "Nova versão"

git push
```

Nos computadores que utilizam a biblioteca:

```
pip install --upgrade git+https://github.com/davigopi/manip_desktop_dgp.git
```

---

# 7. Importando no projeto

```python
from manip_desktop_dgp import ImageManip
from manip_desktop_dgp import ProgramManip
from manip_desktop_dgp import Palvclker
```

---

# 8. Exemplo de utilização

## Localizar uma imagem

```python
from manip_desktop_dgp import ImageManip

img = ImageManip()

xy = img.find_img("gmail.png")

if xy:
    print(xy)
```

---

## Clicar na imagem localizada

```python
from manip_desktop_dgp import clk_x_y

clk_x_y(x, y)
```

---

## Abrir um programa

```python
from manip_desktop_dgp import ProgramManip

program = ProgramManip("chrome.exe")

program.open(r"C:\Program Files\Google\Chrome\Application\chrome.exe")
```

---

## Fechar um programa

```python
program.close()
```

---

## OCR da tela

```python
from manip_desktop_dgp import Palvclker

ocr = Palvclker()

dados = ocr.get_todos_dados()

print(dados)
```

---

# Dependências

```
numpy
opencv-python
pyautogui
mss
psutil
pytesseract
Pillow
```

---

# Tesseract OCR

Para utilizar OCR é necessário instalar o Tesseract.

Download:

https://github.com/UB-Mannheim/tesseract/wiki

ou

https://github.com/tesseract-ocr/tesseract

Caso esteja instalado no caminho padrão:

```
C:\Program Files\Tesseract-OCR
```

a biblioteca fará a detecção automaticamente.

Também é possível distribuir a pasta **tesseract** junto ao projeto.

---

# Funcionalidades

✔ Localização de imagens

✔ Captura de tela

✔ OCR

✔ Clique automático

✔ Gerenciamento de programas

✔ Compatível com múltiplos monitores

✔ Suporte ao PyInstaller

---

# Autor

Davi Pinheiro

GitHub

https://github.com/davigopi

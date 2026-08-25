TUTORIAL: CRIAR E CENTRALIZAR A BIBLIOTECA E COMANDO CLI (manip_desktop_dgp)
===============================================================================
---------------------------------------------------------
## 1. ESTRUTURA DA PASTA DO PROJETO LOCAL
---------------------------------------------------------
Crie uma pasta com o nome manip_desktop_dgp e coloque os dois arquivos dentro dela:
```
manip_desktop_dgp/
    ├── manip_desktop_dgp.py
    ├── pyproject.toml
    ├── README.md
    ├── LICENSE (Opcional)
    ├── .gitignore
    ├── .editorconfig
    ├── requirements-dev.txt
    └── CHANGELOG.md
```
---------------------------------------------------------
## 2. PUBLICAR NO GITHUB
---------------------------------------------------------
Repositório público ou privado no GitHub com o nome manip_desktop_dgp.

URL do repositório: https://github.com/davigopi/manip_desktop_dgp

---------------------------------------------------------
## 3. INSTALAR E ATUALIZAÇÕES
---------------------------------------------------------

Abra o terminal do seu computador, ative o ambiente virtual e, no diretório do repositório manip_desktop_dgp, execute

### A) INSTALAR A FERRAMENTA NO COMPUTADOR
```bash
pip install git+https://github.com/davigopi/manip_desktop_dgp.git
```

### B) ATUALIZAR A FERRAMENTA NO FUTURO

Alterado a version em pyproject.toml:
```bash
pip install --upgrade git+https://github.com/davigopi/manip_desktop_dgp.git
```
Força a atualização:
```bash
pip install --force-reinstall git+https://github.com/davigopi/manip_desktop_dgp.git
```
```bash
pip install --upgrade --no-cache-dir git+https://github.com/davigopi/manip_desktop_dgp.git
```

### C) INSTALAR REQUIREMENTS

```bash
pip install -r venv\Lib\site-packages\manip_desktop_dgp\requirements.txt
```
---------------------------------------------------------

## 4. COMO USAR NOS SEUS PROJETOS
---------------------------------------------------------
- Via importação dentro de scripts Python futuros:
```python
from manip_desktop_dgp import ImageManip, Palvclker
```
```python
import manip_desktop_dgp
```
- Via terminal (em qualquer pasta de projeto React Native, Python, etc.):
  Basta abrir o terminal na pasta desejada e digitar:
```bash
python -m manip_desktop_dgp
```
---------------------------------------------------------
---------------------------------------------------------

Por favor, analise o código Python que vou colar abaixo e crie exclusivamente o conteúdo para preencher a seção "5. EXEMPLOS DE CÓDIGO DE COMO UTILIZAR" do meu README.md.

SISTEMA DE SUBSTITUIÇÃO DE SÍMBOLOS MARKDOWN:
Para evitar qualquer formatação automática ou caixas escuras na interface do chat, NUNCA utilize os caracteres originais de Markdown. Em vez disso, substitua os símbolos seguindo a regra: [quantidade]_[nome_do_caracter]

- Para ``` use: 3_crase
- Para ### use: 3_cerquilha
- Para ## use: 2_cerquilha
- Para # (comentários) use: 1_cerquilha

REGRA CRÍTICA PARA EVITAR CAIXA ESCURA:
- NUNCA adicione 4 espaços ou TABs no início de NENHUMA linha. Escreva TODO o código encostado na margem esquerda (sem indentação nenhuma). O usuário reindentará depois ou ajustará no editor.

Formate a resposta estritamente seguindo esta estrutura:

---------------------------------------------------------
2_cerquilha 5. EXEMPLOS DE CÓDIGO DE COMO UTILIZAR
---------------------------------------------------------

3_cerquilha A) Exemplo Básico (Inicialização e Verificação Simples)
3_crase python
1_cerquilha Exemplo basico sem indentacao
from selenium import webdriver
from fast_modal_checker import Checker_Site_DGP
driver = webdriver.Chrome()
try:
checker = Checker_Site_DGP(driver)
driver.get("[https://exemplo.com](https://exemplo.com)")
finally:
driver.quit()
3_crase

3_cerquilha B) Exemplo Avançado (Tratamento de Modais, Loading e Exceções)
3_crase python
1_cerquilha [Crie o exemplo avançado sem indentacao na margem esquerda]
3_crase

3_cerquilha C) Exemplo de Execução CLI / Teste Integrado
3_crase bash
[Comandos de terminal sem indentacao]
3_crase

---

Segue o meu código Python para análise:

[COLE SEU CÓDIGO PYTHON AQUI]
=======
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


# 1. Instalar em qualquer computador


```
pip install git+https://github.com/davigopi/manip_desktop_dgp.git
```

---

# 2. Atualizar para a última versão


```
pip install --force-reinstall git+https://github.com/davigopi/manip_desktop_dgp.git
ou
pip install --upgrade --no-cache-dir git+https://github.com/davigopi/manip_desktop_dgp.git

```

---

# 3. Importando no projeto

```python
from manip_desktop_dgp import ImageManip
from manip_desktop_dgp import ProgramManip
from manip_desktop_dgp import Palvclker
```

---

# 4. Exemplo de utilização

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

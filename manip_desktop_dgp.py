# flake8: noqa
# pyright: # type: ignore

import numpy as np
import pyautogui
from PIL import ImageGrab
import cv2
from mss import MSS
import os
import sys
import time
import pytesseract
from time import sleep
from pathlib import Path

salvar_imagens = False
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

def print_padao(texto_1=None, texto_2=None, titulo=None, rodape=None):
    global salvar_imagens
    if salvar_imagens:
        if texto_1 and "_|" in texto_1:
            palv_1, palv_2 = texto_1.split("_|")
            texto_1 = f'\n{palv_1:.<14} | {palv_2:.<23}'
        if titulo:
            print(f'\n{50*"#"}\n{titulo} \n{50*"_"}')
        elif rodape:
            print(f'{50*"="}')
        elif texto_2:
            print(f"{texto_1:.<40} | {texto_2}")
        else:
            print(f"{texto_1:.<40}")

def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        path_sys = Path(sys._MEIPASS)
    else:
        path_sys = Path.cwd()
    return path_sys / relative_path

def salve_img(img, nome_arq):
    global salvar_imagens
    if salvar_imagens and img is not None and img.size > 0 and nome_arq:
        arq_sist = nome_arq + '.png'
        arq = os.path.join('img', 'capturadas', arq_sist)
        path_img = resource_path(arq)
        os.makedirs(os.path.dirname(path_img), exist_ok=True)
        cv2.imwrite(path_img, img)

def clk_x_y(x, y):
    pyautogui.click(x, y)

def setup_tesseract():
    # 1. Define os caminhos prioritários (pasta local do projeto)
    tesseract_exe = resource_path( Path("tesseract") / "tesseract.exe" )
    tessdata_dir = resource_path( Path("tesseract") / "tessdata" )
    # 2. Fallback: Se não existir na pasta do projeto, busca na instalação padrão do Windows
    if not tesseract_exe.exists():
        tesseract_exe = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
        tessdata_dir = Path(r"C:\Program Files\Tesseract-OCR\tessdata")
    if not tesseract_exe.exists():
        raise Exception(f"Tesseract não encontrado no caminho:\n{tesseract_exe}")
    pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
    os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)
    global salvar_imagens
    if salvar_imagens:
        print_padao(titulo="Configurando Tesseract OCR...")
        print_padao(texto_1=f"Tesseract: {tesseract_exe}")
        print_padao(texto_1=f"Tessdata: {tessdata_dir}")
        print_padao(texto_1=f"Versão do Tesseract: {pytesseract.get_tesseract_version()}")
        print_padao(rodape=True)

def get_monitor(width=None, height=None, index_nonitor=1):
    target_monitor = get_monitor_by_size(width, height) if width and height else get_monitor_by_index(index_nonitor)
    region = {
        "left": int(target_monitor["left"]),                                                                                    # X
        "top": int(target_monitor["top"]) + int(target_monitor["height"] * 0.16),                                               # Y
        "width": int(target_monitor["width"]) - 4,                                                                              # largura
        "height": int(target_monitor["height"]) - int(target_monitor["height"] * 0.16) - int(target_monitor["height"] * 0.06)   # altura
    }
    region["list"] = [int(region["left"]), int(region["top"]), int(region["width"]), int(region["height"])]
    return region

def get_monitor_by_size(width, height):
  # with garante que os instância do capturador de img da biblioteca MSS sejam liberados de forma correta ao finalizar o bloco.
  with MSS() as sct:
    monitores = sct.monitors[1:]
    for monitor in monitores:
      if monitor["width"] == width and monitor["height"] == height:
        return monitor
    if len(monitores) > 1:
      return monitores[1]
    return monitores[0]

def get_monitor_by_index(index_nonitor):
    with MSS() as sct:
        if 1 <= index_nonitor < len(sct.monitors):
            return sct.monitors[index_nonitor]
        return sct.monitors[1]

def get_img_mss(region):
    # Captura a região da img via MSS e padroniza a conversão para BGR.
    with MSS() as sct:
        region = region if region else sct.monitors[1]
        sct_img = sct.grab(region)
        img = np.array(sct_img)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        # img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        return img_bgr
    raise Exception("Não existe img")

def get_img_pil(region):
    # sct_img = pyautogui.screenshot(region=region['list'])
    # img = np.array(sct_img)
    # img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    # return img_bgr

    # 1. Converte a região (left, top, width, height) para a bounding box (left, top, right, bottom)
    left = region["left"]
    top = region["top"]
    right = left + region["width"]
    bottom = top + region["height"]

    # 2. Captura a tela usando o Pillow com suporte a múltiplos monitores (coordenadas negativas)
    sct_img = ImageGrab.grab(bbox=(left, top, right, bottom), all_screens=True)

    # 3. Converte para array NumPy e ajusta a cor de RGB para BGR (OpenCV)
    img = np.array(sct_img)
    img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    return img_bgr

#     return dict_arqs
# def get_all_img(region):
#     dict_arqs = {}
#     # Captura e conversão inicial
#     if region['get_img'] == 'pil':
#         dict_arqs['img'] = get_img_pil(region)
#         dict_arqs['img_cv'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_RGB2BGR)
#         dict_arqs['gray'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_RGB2GRAY)
#     else:
#         dict_arqs['img'] = get_img_mss(region)
#         dict_arqs['img_cv'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_BGRA2BGR)
#         dict_arqs['gray'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_BGRA2GRAY)
#     scale = region.get('scale', 2)
#     dict_arqs['grayClr'] = cv2.resize(dict_arqs['gray'], None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
#     # 1. Otsu Thresholding Direto (Excelente para texto limpo em tela)
#     _, dict_arqs['threshOtsu'] = cv2.threshold(dict_arqs['grayClr'], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     _, dict_arqs['threshOtsuInv'] = cv2.threshold(dict_arqs['grayClr'], 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
#     # 2. Morfologia: Engrossa levemente as letras para não quebrar a haste do 'p' nem fechar o 'a'
#     kernel = np.ones((2, 2), np.uint8)
#     dict_arqs['threshMorph'] = cv2.morphologyEx(dict_arqs['threshOtsuInv'], cv2.MORPH_CLOSE, kernel)
#     # 3. CLAHE com Adaptive Threshold Ajustado (BlockSize maior: 21 em vez de 11)
#     clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
#     dict_arqs['grayClahe'] = clahe.apply(dict_arqs['grayClr'])
#     dict_arqs['threshAdapt'] = cv2.adaptiveThreshold(
#         dict_arqs['grayClahe'], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 5
#     )
#     # # 4. Inversões e Contraste Suave
#     # dict_arqs['grayEsc'] = cv2.equalizeHist(dict_arqs['grayClr'])
#     # dict_arqs['grayClrInv'] = cv2.bitwise_not(dict_arqs['grayClr'])
#     # for contraste in range(2, 6, 1):
#     #     c_esc = cv2.addWeighted(dict_arqs['grayClrInv'], contraste, np.zeros(dict_arqs['grayClrInv'].shape, dict_arqs['grayClrInv'].dtype), 0, 0)
#     #     dict_arqs['contrClr'+str(contraste)] = cv2.GaussianBlur(c_esc, (3, 3), 0)
#     # return dict_arqs
#     # 4. Inversões e Contraste Unificado (Gera contrClr e contrEsc no mesmo loop)
#     dict_arqs['grayEsc'] = cv2.equalizeHist(dict_arqs['grayClr'])
#     dict_arqs['grayClrInv'] = cv2.bitwise_not(dict_arqs['grayClr'])
#     dict_arqs['grayEscInv'] = cv2.bitwise_not(dict_arqs['grayEsc'])

#     for contraste in range(2, 8, 1):
#         # Processa imagem cinza normal (contrClr)
#         c_clr = cv2.addWeighted(dict_arqs['grayClrInv'], contraste, np.zeros(dict_arqs['grayClrInv'].shape, dict_arqs['grayClrInv'].dtype), 0, 0)
#         dict_arqs['contrClr' + str(contraste)] = cv2.GaussianBlur(c_clr, (3, 3), 0)

#         # Processa imagem equalizada (contrEsc) -> Onde o 'dme' é detectado
#         c_esc = cv2.addWeighted(dict_arqs['grayEscInv'], contraste, np.zeros(dict_arqs['grayEscInv'].shape, dict_arqs['grayEscInv'].dtype), 0, 0)
#         dict_arqs['contrEsc' + str(contraste)] = cv2.GaussianBlur(c_esc, (3, 3), 0)

#     return dict_arqs
def get_all_img(region):
    dict_arqs = {}

    # 1. Captura e conversão inicial (BGR/Cinza)
    if region['get_img'] == 'pil':
        dict_arqs['img'] = get_img_pil(region)
        dict_arqs['img_cv'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_RGB2BGR)
        dict_arqs['gray'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_RGB2GRAY)
    else:
        dict_arqs['img'] = get_img_mss(region)
        dict_arqs['img_cv'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_BGRA2BGR)
        dict_arqs['gray'] = cv2.cvtColor(dict_arqs['img'], cv2.COLOR_BGRA2GRAY)

    # 2. Redimensionamento (Zoom)
    scale = region.get('scale', 2)
    dict_arqs['grayClr'] = cv2.resize(dict_arqs['gray'], None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)

    # 3. Equalização e Suavização (EXATAMENTE COMO NO ANTERIOR)
    dict_arqs['grayEsc'] = cv2.equalizeHist(dict_arqs['grayClr'])
    dict_arqs['grayEsc'] = cv2.GaussianBlur(dict_arqs['grayEsc'], (3, 3), 0)

    # 4. Inversão base para contrastes
    dict_arqs['grayClrInv'] = cv2.bitwise_not(dict_arqs['grayClr'])
    dict_arqs['grayEscInv'] = cv2.bitwise_not(dict_arqs['grayEsc'])

    # 5. Loop dinâmico de contraste (Gera contrEsc4 identico ao anterior)
    for contraste in range(2, 11, 2):
        c_clr = cv2.addWeighted(dict_arqs['grayClrInv'], contraste, np.zeros(dict_arqs['grayClrInv'].shape, dict_arqs['grayClrInv'].dtype), 0, 0)
        c_esc = cv2.addWeighted(dict_arqs['grayEscInv'], contraste, np.zeros(dict_arqs['grayEscInv'].shape, dict_arqs['grayEscInv'].dtype), 0, 0)

        dict_arqs['contrClr' + str(contraste)] = cv2.GaussianBlur(c_clr, (3, 3), 0)
        dict_arqs['contrEsc' + str(contraste)] = cv2.GaussianBlur(c_esc, (3, 3), 0)
        _, dict_arqs['mask' + str(contraste)] = cv2.threshold(dict_arqs['contrClr' + str(contraste)], 150, 255, cv2.THRESH_BINARY)

    # 6. CLAHE e Binarização Adaptativa (EXATAMENTE COMO NO ANTERIOR)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    dict_arqs['grayClahe'] = clahe.apply(dict_arqs['grayClr'])
    dict_arqs['threshAdapt'] = cv2.adaptiveThreshold(
        dict_arqs['grayClahe'], 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 7. Adicionais do código novo (Otsu e Morfologia) sem alterar os anteriores
    _, dict_arqs['threshOtsu'] = cv2.threshold(dict_arqs['grayClr'], 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    _, dict_arqs['threshOtsuInv'] = cv2.threshold(dict_arqs['grayClr'], 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    kernel = np.ones((2, 2), np.uint8)
    dict_arqs['threshMorph'] = cv2.morphologyEx(dict_arqs['threshOtsuInv'], cv2.MORPH_CLOSE, kernel)

    return dict_arqs

def get_dict_img(region):
    dict_arqs = {}
    dict_arqs['img_bgr'] = get_img_mss(region)
    dict_arqs['img_gray'] = cv2.cvtColor(dict_arqs['img_bgr'], cv2.COLOR_BGR2GRAY)
    return dict_arqs

def find_dif_size_img(palv, fator, porcentagem) :
    dict_arqs_find = {}
    arq = resource_path(os.path.join('img', palv))
    img_find = cv2.imread(arq, cv2.IMREAD_GRAYSCALE)
    if img_find is None or img_find.size == 0:
        print_padao(texto_1=f"Erro ao carregar img: {img}")
        raise Exception("Não existe imagem para procurar")
    list_zoom = [1]
    for i in range(fator, porcentagem+1, fator):
        list_zoom.extend([round(1+i/100, 2), round(1-i/100, 2)])
    for zoom in list_zoom:
        altura, largura = img_find.shape[:2]
        dict_arqs_find[f'img_find_{zoom}'] = cv2.resize(img_find, (int(largura * zoom), int(altura * zoom)), interpolation=cv2.INTER_AREA)
    return dict_arqs_find

class ImageManip:
    def locate_x_y(self, palv, reduce_confidence=0.05, metodo="mss_image", width=None, height=None, index_nonitor=1):
        setup_tesseract()
        confidence = 0.95
        confidence_print = 1
        confidence_minima = 0.65
        count = 1
        n_tentativas = 2
        region = get_monitor(width, height, index_nonitor)
        if not palv:
            raise Exception(f'Não informado palavra da imagem {palv}.')
        while True:
            try:
                if metodo == "mss_image":
                    dict_arqs = get_dict_img(region)
                    for nome_arq in dict_arqs:
                        salve_img(dict_arqs[nome_arq], nome_arq)
                    dict_arqs_find = find_dif_size_img(palv, 2, 30)
                    for palv, arq_find in dict_arqs_find.items():
                        # Evita erro caso a imagem procurada seja maior que a região da img
                        if arq_find.shape[0] > dict_arqs['img_gray'].shape[0] or \
                        arq_find.shape[1] > dict_arqs['img_gray'].shape[1]:
                            continue
                        res = cv2.matchTemplate(dict_arqs['img_gray'], arq_find, cv2.TM_CCOEFF_NORMED)
                        locais = np.where(res >= confidence)
                        if len(locais[0]) > 0:
                            x, y = locais[1][0], locais[0][0]
                            h, w = arq_find.shape[:2]
                            x_img = int(region["left"] + x + w // 2)
                            y_img = int(region["top"] + y + h // 2)
                            print_padao(texto_1=f'Imagem {palv} encontra na img {palv} valores X: {x_img} e Y:{y_img}')
                            return x_img, y_img
                        salve_img(arq_find, palv+'_nao_encontrado')
                    chave, valor = next(iter(dict_arqs_find.items()))
                    salve_img(valor, chave+'_nao_encontrado')
                elif metodo == "pyautogui":
                    arq = resource_path(os.path.join('img', palv))
                    box = list(pyautogui.locateAllOnScreen(arq, confidence=confidence, region=region["list"]))
                    if box:
                        ponto = pyautogui.center(box[0])
                        return ponto.x, ponto.y
                else:
                    raise Exception(f'Valor inválido do método {metodo}.')
                # --- FLUXO DE FALHA DE BUSCA (Roda se não deu return no if acima) ---
                confidence -= reduce_confidence
                confidence = round(confidence, 2)
                if confidence <= confidence_print:
                    print(f'\rImg: {palv} | Confid: {confidence}', end='')
                    confidence_print -= 0.1
                if confidence <= confidence_minima:
                    if count >= n_tentativas:
                        return None, None
                    count += 1
                    confidence = 0.95
                    confidence_print = 1
                sleep(0.05)     # Pausa no fluxo normal para liberar CPU
            except NameError as e:
                print(f'\rImg: {palv} não existe | Erro: ({type(e).__name__}).', end='')
                return None, None
            except Exception as e:
                print(f'\nErro inesperado: {type(e).__name__} - {e}')
                return None, None


class Palvclker:
    def get_todos_dados(self, list_psm=[3, 6, 11, 12], opcao='all', conf_min=0, limit_caracter=2, scale=2, width=None, height=None, index_nonitor=1, get_img='MSS'):
        setup_tesseract()
        region = get_monitor(width, height, index_nonitor)
        region['scale'] = scale
        region['get_img'] = get_img
        dict_arqs = get_all_img(region)
        for nome_arq in dict_arqs:
            salve_img(dict_arqs[nome_arq], nome_arq)
        dict_imgs_verification = {opcao: dict_arqs[opcao]} if opcao in dict_arqs else dict_arqs
        dict_dados = {}
        for nome_img, img_tst in dict_imgs_verification.items():
            print(f'{nome_img}:', end=' ')
            for psm in list_psm:
                print(f'{psm}', end='.')
                # Adicione `-c tessedit_char_whitelist=...` nas configurações do pytesseract
                config_tess = f'--oem 3 --psm {psm} -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
                dados = pytesseract.image_to_data(img_tst, config=config_tess, output_type=pytesseract.Output.DICT)
                # dados = pytesseract.image_to_data(img_tst, config=f'--oem 3 --psm {psm}', output_type=pytesseract.Output.DICT)
                for i, palv in enumerate(dados['text']):
                    try:
                        conf = int(dados['conf'][i])
                    except:
                        continue
                    if conf < conf_min:
                        continue
                    if len(palv) < limit_caracter:
                        continue
                    palv = palv.lower().strip()
                    if not palv:
                        continue
                    x = dados['left'][i]
                    y = dados['top'][i]
                    w = dados['width'][i]
                    h = dados['height'][i]
                    if nome_img not in ['img', 'img_cv', 'gray']:
                        x = int(x / region['scale'])
                        y = int(y / region['scale'])
                        w = int(w / region['scale'])
                        h = int(h / region['scale'])
                    # somar com o limite enviado para posicao correta n oregion
                    if region:
                        x += region['left']
                        y += region['top']
                    # Calcula o centro da palavra (ideal para o PyAutoGUI clicar)
                    center_x = x + int(w / 2)
                    center_y = y + int(h / 2)
                    key_palv = palv+'_|'+nome_img+'.'+str(psm)+'.'
                    for cont in range(100):
                        fk_key = f"{key_palv}{cont}"
                        if fk_key not in dict_dados:
                            dict_dados[fk_key] = {
                                "x": center_x,
                                "y": center_y,
                                "box_left": x,
                                "box_top": y,
                                "w": w,
                                "h": h,
                            }
                        break
            print('', end=' | ')
        return dict_dados if dict_dados else None

if __name__ == '__main__':
    # dafini e vai salvar as imagens em img\capturada
    salvar_imagens = True

    # procurar imagem
    palv = 'gmail.png'
    print_padao(titulo=f'Pasta local: {palv}')
    imageManip = ImageManip()

    # imageManip.palv = palv
    # imageManip.reduce_confidence = 0.1
    x, y = imageManip.locate_x_y(palv=palv, reduce_confidence=0.1, width=1360, height=768)
    if not x or not y:
        print_padao(texto_1='x e y não existe')
    else:                                 # <--- RETORNA FALSE SE NÃO ACHAR
        print_padao(texto_1=f'X: {x} e Y: {y}')
        clk_x_y(x, y)
    print_padao(rodape=True)

    # procurar palavra
    palvclker = Palvclker()
    palv = 'dme'
    print_padao(titulo=f'Palavra a porcura: {palv}')
    dados = palvclker.get_todos_dados(list_psm=[6, 11], opcao='all', width=1360, height=768, get_img='pil', limit_caracter=2)
    list_palv = []
    encontrado = False
    for key_1, value_2 in dados.items():
        try:
            key_palavra, _ = key_1.split("_|")
        except ValueError:
            continue
        if key_palavra not in list_palv:
            list_palv.append(key_palavra)
        if '_|' in palv:
            palv_1, palv_2 = palv.split("_|")
            if palv_1 in key_1 and palv_2 in key_1:
                print_padao(texto_1=key_1, texto_2=value_2)
                encontrado = True
        else:
            if palv in key_1:
                print_padao(texto_1=key_1, texto_2=value_2)
                encontrado = True
    if not encontrado:
        print_padao(texto_1=f'\nNão encontrada, lista:\n{list_palv}.')
    print_padao(rodape=True)

    # palavra perto da posição do mouse
    time.sleep(3)
    x, y = pyautogui.position()
    print_padao(titulo=f'Possição do mouse : X: {x}, Y: {y}. Palavra(s) próxima(s) a direitra do mouse:')
    for key_1, value_2 in dados.items():
        if not value_2['x']  <= x + 100:
            continue
        if not value_2['x']  >= x:
            continue
        if not value_2['y']  <= y + 10:
            continue
        if not value_2['y']  >= y - 10:
            continue
        print_padao(texto_1=key_1, texto_2=value_2)
    print_padao(rodape=True)

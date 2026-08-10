# flake8: noqa
# pyright: # type: ignore

import numpy as np
import pyautogui
import psutil
import cv2
import mss
from mss import MSS
import os
import sys
import pytesseract
import signal  # interface gerenciador do sistema operacional
from time import sleep
# from PIL import Image  # pip install Pillow
from pathlib import Path

salvar_imagens = False
pyautogui.PAUSE = 0
pyautogui.FAILSAFE = True

# from src.exceptions import BlockExecution, ContinueFindSpecification, EndFindSpecification
# pip install Pillow
# import pyscreeze

''' obs: o python 3.14 da erro no pacote ainda nao funciona 11/2025 
pip install numpy==1.26.4
pip install pyautogui opencv-python numpy
pip install pyautogui opencv-python pillow numpy
pip install psutil
pip install mss
pip install pytesseract

pip install opencv-python ->em alguns programa usa confidencialidade
pip install opencv-python==4.8.1.78


'''
def print_padao(texto_1=None, texto_2=None, titulo=None, rodape=None): 
    global salvar_imagens
    if salvar_imagens:    
        if texto_1 and "_|" in texto_1:
            palv_1, palv_2 = texto_1.split("_|")
            texto_1 = f'{palv_1:.<14} | {palv_2:.<23}' 
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
    # try:
    #     path_sys = sys._MEIPASS
    # except Exception:
    #     path_sys = os.getcwd()
    # return os.path.join(path_sys, str(relative_path))

def salve_tela(tela, nome_arq):
    global salvar_imagens
    if salvar_imagens and tela is not None and tela.size > 0 and nome_arq:
        arq_sist = nome_arq + '.png'
        arq = os.path.join('img', 'capturadas', arq_sist)
        path_tela = resource_path(arq)
        os.makedirs(os.path.dirname(path_tela), exist_ok=True)
        cv2.imwrite(path_tela, tela)

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

def define_region():
    target_monitor = get_monitor(width=1360, height=768)
    left = target_monitor["left"]
    top = target_monitor["top"]
    width = target_monitor["width"]
    height = target_monitor["height"]
    top_offset = int(height * 0.16)
    bottom_offset = int(height * 0.06)
    region = {
        "left": left,                                   # X
        "top": top + top_offset,                        # Y
        "width": width - 4,                             # largura
        "height": height - top_offset - bottom_offset   # altura
    }
    region_list = [region["left"], region["top"], region["width"], region["height"]]
    return region, region_list

def get_monitor(width=1360, height=768):
  # with garante que os instância do capturador de tela da biblioteca mss sejam liberados de forma correta ao finalizar o bloco.
  with MSS() as sct:
    monitores = sct.monitors[1:]
    for monitor in monitores:
      if monitor["width"] == width and monitor["height"] == height:
        return monitor
    if len(monitores) > 1:
      return monitores[1]
    return monitores[0]

def get_tela(region):
    # Captura a região da tela via MSS e padroniza a conversão para BGR.
    with MSS() as sct:
        region = region if region else sct.regions[1]
        sct_img = sct.grab(region)
        tela = np.array(sct_img)
        tela_bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
        return tela_bgr
    raise Exception("Não existe Tela")
    
def get_tela_all(scale, region):
    dict_arqs = {}
    dict_arqs['tela'] = get_tela(region)
    dict_arqs['tela_cv'] = cv2.cvtColor(dict_arqs['tela'], cv2.COLOR_BGRA2BGR)       
    dict_arqs['gray'] = cv2.cvtColor(dict_arqs['tela'], cv2.COLOR_BGRA2GRAY)
    dict_arqs['grayClr'] = cv2.resize(dict_arqs['gray'], None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    dict_arqs['grayEsc'] = cv2.equalizeHist(dict_arqs['grayClr'])
    dict_arqs['grayEsc'] = cv2.GaussianBlur(dict_arqs['grayEsc'], (3, 3), 0)
    img_inv = cv2.bitwise_not(dict_arqs['grayClr'])
    dict_arqs['contrClr'] = cv2.addWeighted(img_inv, 1.5, np.zeros(img_inv.shape, img_inv.dtype), 0, 0)
    dict_arqs['contrClr3'] = cv2.addWeighted(img_inv, 3.0, np.zeros(img_inv.shape, img_inv.dtype), 0, 0)
    dict_arqs['contrClr6'] = cv2.addWeighted(img_inv, 6.0, np.zeros(img_inv.shape, img_inv.dtype), 0, 0)
    img_inv = cv2.bitwise_not(dict_arqs['grayEsc'])
    dict_arqs['contrEsc'] = cv2.addWeighted(img_inv, 1.5, np.zeros(img_inv.shape, img_inv.dtype), 0, 0)
    dict_arqs['contrEsc3'] = cv2.addWeighted(img_inv, 3.0, np.zeros(img_inv.shape, img_inv.dtype), 0, 0)
    dict_arqs['contrEsc6'] = cv2.addWeighted(img_inv, 6.0, np.zeros(img_inv.shape, img_inv.dtype), 0, 0)
    _, dict_arqs['threshClr'] = cv2.threshold(dict_arqs['grayClr'], 150, 255, cv2.THRESH_BINARY)
    _, dict_arqs['threshEsc'] = cv2.threshold(dict_arqs['grayEsc'], 150, 255, cv2.THRESH_BINARY)
    dict_arqs['threshInvClr'] = cv2.bitwise_not(dict_arqs['threshClr'])
    dict_arqs['threshInvEsc'] = cv2.bitwise_not(dict_arqs['threshEsc'])
    _, dict_arqs['mask'] = cv2.threshold(dict_arqs['contrClr3'], 150, 255, cv2.THRESH_BINARY)
    return dict_arqs
    
def get_tela_img(region):
    dict_arqs = {}
    dict_arqs['img_tela_bgr'] = get_tela(region)
    dict_arqs['img_tela_gray'] = cv2.cvtColor(dict_arqs['img_tela_bgr'], cv2.COLOR_BGR2GRAY)
    return dict_arqs
   
def set_imgs_find(name_arq, fator, porcentagem) :  
    dict_arqs_find = {} 
    arq = resource_path(os.path.join('img', name_arq))
    img_find = cv2.imread(arq, cv2.IMREAD_GRAYSCALE)
    if img_find is None or img_find.size == 0:
        print_padao(texto_1=f"Erro ao carregar tela: {img}")
        raise Exception("Não existe imagem para procurar")
    list_zoom = [1]
    for i in range(fator, porcentagem+1, fator):
        list_zoom.extend([round(1+i/100, 2), round(1-i/100, 2)])
    for zoom in list_zoom:
        altura, largura = img_find.shape[:2]
        dict_arqs_find[f'img_find_{zoom}'] = cv2.resize(img_find, (int(largura * zoom), int(altura * zoom)), interpolation=cv2.INTER_AREA)
    return dict_arqs_find
    
class ImageManip:
    def __init__(self, *args, **kwargs) -> None:
        # self.arq = kwargs.get("path_img")
        self.name_arq = kwargs.get("name_arq")
        self.reduce_confidence = kwargs.get("reduce_confidence", 0.05)
        self.metodo = "mss_image"
        setup_tesseract()

    @property
    def locate_x_y(self):
        confidence = 0.95
        confidence_print = 1
        confidence_minima = 0.65
        count = 1
        n_tentativas = 2
        region, region_list = define_region()
        while True:
            try:
                if self.metodo == "mss_image":
                    dict_arqs = get_tela_img(region)
                    for nome_arq in dict_arqs:
                        salve_tela(dict_arqs[nome_arq], nome_arq)
                    dict_arqs_find = set_imgs_find(self.name_arq, 2, 30)
                    for name_arq, arq_find in dict_arqs_find.items():
                        # Evita erro caso a imagem procurada seja maior que a região da tela
                        if arq_find.shape[0] > dict_arqs['img_tela_gray'].shape[0] or \
                        arq_find.shape[1] > dict_arqs['img_tela_gray'].shape[1]:
                            continue
                        res = cv2.matchTemplate(dict_arqs['img_tela_gray'], arq_find, cv2.TM_CCOEFF_NORMED)
                        locais = np.where(res >= confidence)
                        if len(locais[0]) > 0:
                            x, y = locais[1][0], locais[0][0]
                            h, w = arq_find.shape[:2]
                            x_img = int(region["left"] + x + w // 2)
                            y_img = int(region["top"] + y + h // 2)
                            print_padao(texto_1=f'Imagem {self.name_arq} encontra na tela {name_arq} valores X: {x_img} e Y:{y_img}')
                            return x_img, y_img
                        salve_tela(arq_find, name_arq+'_nao_encontrado')
                    chave, valor = next(iter(dict_arqs_find.items()))
                    salve_tela(valor, chave+'_nao_encontrado')
                elif self.metodo == "pyautogui":
                    arq = resource_path(os.path.join('img', self.name_arq))
                    box = list(pyautogui.locateAllOnScreen(arq, confidence=confidence, region=region_list))
                    if box:
                        ponto = pyautogui.center(box[0])
                        return ponto.x, ponto.y
                else:
                    raise Exception(f'Valor inválido do método {self.metodo}.')
                # --- FLUXO DE FALHA DE BUSCA (Roda se não deu return no if acima) ---
                confidence -= self.reduce_confidence
                confidence = round(confidence, 2)

                if confidence <= confidence_print:
                    print(f'\rImg: {self.name_arq} | Confid: {confidence}', end='')
                    confidence_print -= 0.1

                if confidence <= confidence_minima:
                    if count >= n_tentativas:
                        return None, None
                    count += 1
                    confidence = 0.95
                    confidence_print = 1

                sleep(0.05)  # Pausa no fluxo normal para liberar CPU

            except NameError as e:
                print(f'\rImg: {self.name_arq} não existe | Erro: ({type(e).__name__}).', end='')
                return None, None

            except Exception as e:
                print(f'\nErro inesperado: {type(e).__name__} - {e}')
                return None, None
            #     print_padao(texto_1=f'Imagem {self.name_arq} não encontrada {self.metodo}')
            # except NameError as e:
            #     print(f'\rImg: {self.name_arq} não existe | Erro: ({type(e).__name__}).', end='')
            #     return None, None

            # except Exception as e:
            #     confidence -= self.reduce_confidence
            #     confidence = round(confidence, 2)
            #     if confidence <= confidence_print:
            #         # arq = resource_path(os.path.join('img', self.name_arq))
            #         print(f'\rImg: {self.name_arq} | Confid: {confidence} | Erro: ({type(e).__name__}).', end='')
            #         confidence_print -= 0.1
            #     if confidence <= confidence_minima:
            #         if count >= n_tentativas:
            #             # input(f'A imagem não foi encontrada {self.arq}')
            #             return None, None
            #         count += 1
            #         confidence = 1
            #     sleep(0.05)

        

class Palvclker:
    def get_todos_dados(self, list_psm=[3, 6, 11, 12],  opcao='all', conf_min=0, limit_caracter=2, scale=2):
        setup_tesseract()
        region, region_list = define_region()
        dict_arqs = get_tela_all(scale, region)
        for nome_arq in dict_arqs:
            salve_tela(dict_arqs[nome_arq], nome_arq)
        dict_imgs_verification = {opcao: dict_arqs[opcao]} if opcao in dict_arqs else dict_arqs
        dict_dados = {}
        for nome_img, img_tst in dict_imgs_verification.items():
            print(f'{nome_img}:', end=' ')
            for psm in list_psm:
                print(f'{psm}', end='.')
                dados = pytesseract.image_to_data(img_tst, config=f'--oem 3 --psm {psm}', output_type=pytesseract.Output.DICT)
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
                    if nome_img != "img" and nome_img != "img_cv":
                        x = int(x / scale)
                        y = int(y / scale)
                        w = int(w / scale)
                        h = int(h / scale)
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
    palv = 'pacotes'
    name_arq = 'fogo.png'
    list_psm = [11]
    confidence = 0.1
    salvar_imagens = True

    region, region_list = define_region()

    imageManip = ImageManip()
    print_padao(titulo=f'Pasta local: {name_arq}')
    imageManip.name_arq = name_arq
    imageManip.reduce_confidence = confidence
    x, y = imageManip.locate_x_y
    if not x or not y:
        print_padao(texto_1='x e y não existe')
    else:                                 # <--- RETORNA FALSE SE NÃO ACHAR
        print_padao(texto_1=f'X: {x} e Y: {y}')
        print_padao(rodape=True)
        print(x, y)
        clk_x_y(x, y)

    palvclker = Palvclker()
    dados = palvclker.get_todos_dados(list_psm=list_psm, opcao='all', limit_caracter=2)
    print_padao(titulo=f'Palavra que sera porcurado é: {palv}')
    list_palv = []
    encontrado = False
    for key_1, value_2 in dados.items():
        # print("", key_1, value_2)
        key_palavra, _ = key_1.split("_|")
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
        print_padao(texto_1=f'\nPalavra {palv} não encontrada na tela, lista: {list_palv}.')
    print_padao(rodape=True)

    x, y = pyautogui.position()
    print_padao(titulo=f'Possição do mouse : X: {x}, Y: {y}. Palavra(s) próxima(s):')
    for key_1, value_2 in dados.items():
        if not value_2['x']  <= x + 30:
            continue
        if not value_2['x']  >= x - 30:
            continue
        if not value_2['y']  <= y + 50:
            continue
        if not value_2['y']  >= y - 50:
            continue
        print_padao(texto_1=key_1, texto_2=value_2)
    print_padao(rodape=True)



# class ProgramManip():
#     def __init__(self, program) -> None:
#         self.program = program
#         self.name_program =  os.path.splitext(self.program.lower())[0]

#     def close(self):
#         # programaAberto = self.program in (i.name() for i in psutil.process_iter())
#         programaAberto = any(self.name_program in (p.name() or "").lower() for p in psutil.process_iter(['name']))
#         if not programaAberto:
#             print("Programa não está aberto:", self.program)
#             return

#         '''# listar de dicionarios dos processos aberto no S.O.'''
#         list_pid_name = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if self.name_program in (p.info['name'] or "").lower()]
#         if not list_pid_name:
#             print("Nenhum processo encontrado para fechar:", self.program)
#             return
        
#         for dicionarioPidName in list_pid_name:
#             pid = dicionarioPidName['pid']  # seleciona apenas os pid
#             os.kill(pid, signal.SIGTERM)  # fecha prog atravez do seu pid,

#     def open(self, what):
#         for _ in range(3):
#             os.startfile(what)
#             print(f'Tentar abrir o programa: {self.name_program}')
#             for _ in range(3):
#                 # programaAberto = self.program in (i.name() for i in psutil.process_iter())
#                 programaAberto = any(self.name_program in (p.name() or "").lower() for p in psutil.process_iter(['name']))
#                 if programaAberto:
#                     return True
#                 print(f"Nenhum processo {self.program} encontrado, repetir para tentar abrir. \n")
#                 sleep(1)
#         for p in psutil.process_iter(['name']):
#             print(p.name())
#         return False

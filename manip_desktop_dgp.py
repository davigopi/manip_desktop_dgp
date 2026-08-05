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

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        # base_path = os.path.abspath(".")
        base_path = os.getcwd()
    return os.path.join(base_path, str(relative_path))

def get_monitor_por_resolucao(width=1360, height=768):
  with MSS() as sct:
    monitores = sct.monitors[1:]
    for monitor in monitores:
      if monitor["width"] == width and monitor["height"] == height:
        return monitor
    if len(monitores) > 1:
      return monitores[1]
    return monitores[0]

def print_padao(texto_1=None, texto_2=None, titulo=None, rodape=None):     
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

def define_region():
    target_monitor = get_monitor_por_resolucao(width=1360, height=768)
    left = target_monitor["left"]
    top = target_monitor["top"]
    width = target_monitor["width"]
    height = target_monitor["height"]
    top_offset = int(height * 0.16)
    bottom_offset = int(height * 0.06)
    dict_region = {
        "left": left,                                   # X
        "top": top + top_offset,                        # Y
        "width": width - 4,                             # largura
        "height": height - top_offset - bottom_offset   # altura
    }
    list_region = [dict_region["left"], dict_region["top"], dict_region["width"], dict_region["height"]]
    return dict_region, list_region

def capturar_regiao(dict_region, caminho_salvar=None):
    """
    Captura a região da tela via MSS e padroniza a conversão para BGR.
    Se um caminho for informado, salva o arquivo PNG em disco via cv2.imwrite.
    """
    with MSS() as sct:
        sct_img = sct.grab(dict_region)
        tela = np.array(sct_img)
        tela_bgr = cv2.cvtColor(tela, cv2.COLOR_BGRA2BGR)
        
        if caminho_salvar:
            os.makedirs(os.path.dirname(caminho_salvar), exist_ok=True)
            cv2.imwrite(caminho_salvar, tela_bgr)
            
        return tela_bgr
    
def localizar_imagem(img, dict_region, list_region=None, metodo='mss', confidence=0.8):
    if metodo == "pyautogui":
        box = list(pyautogui.locateAllOnScreen(img, confidence=confidence, region=list_region))
        return pyautogui.center(box[0]) if box else False

    elif metodo == "mss":
        template = cv2.imread(img, cv2.IMREAD_COLOR)
        if template is None:
            return False
        h, w = template.shape[:2]
        # Define caminho de debug caso precise salvar (opcional)
        path_debug = resource_path(os.path.join('img', 'capturadas', 'img_sist_capturado.png'))
        # Chama a mesma função de captura utilizada pelo get_img_capturador
        tela_bgr = capturar_regiao(dict_region, caminho_salvar=path_debug if salvar_imagens else None)
        # Opcional: Para usar em cinza mantendo a mesma matriz capturada
        tela_gray = cv2.cvtColor(tela_bgr, cv2.COLOR_BGR2GRAY)
        template_gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
        res = cv2.matchTemplate(tela_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        locais = np.where(res >= confidence)
        for x, y in zip(*locais[::-1]):
            x_coord = int(dict_region["left"] + x + w // 2)
            y_coord = int(dict_region["top"] + y + h // 2)
            return x_coord, y_coord
        return False
    else:
        raise ValueError("Método inválido.")
    
def get_img_capturador(dict_region):
    path_img = resource_path(os.path.join('img', 'capturadas', 'img_sist_capturado.png'))
    os.makedirs(os.path.dirname(path_img), exist_ok=True)
    if salvar_imagens:
        print_padao(titulo='Regiao do monitor capturada')
        print_padao(texto_1=f'Região: {dict_region}')
        print_padao(texto_1=f'Caminho: {path_img}')
        print_padao(rodape=True)
    # Usa a função unificada e salva o arquivo em disco
    capturar_regiao(dict_region, caminho_salvar=path_img)
    return path_img

def clk_x_y(x, y):
    pyautogui.click(x, y)


class ImageManip:
    def __init__(self, *args, **kwargs) -> None:
        self.img = kwargs.get("img")
        self.reduce_confidence = kwargs.get("reduce_confidence", 0.05)
        # if getattr(sys, "frozen", False):
        #     self.path_sys = Path(sys._MEIPASS)
        # else:
        #     self.path_sys = Path(__file__).resolve().parent

    @property
    def locate_x_y(self):
        if not self.img or not os.path.exists(self.img):
            print_padao(texto_1=f"Imagem nao encontrada: {self.img}")
            return False
        confidence = 0.95
        confidence_print = 1
        confidence_minima = 0.65
        count = 1
        n_tentativas = 2
        
        dict_region, list_region = define_region()
        if salvar_imagens:
            get_img_capturador(dict_region)
        while True:
            try:
                xy = localizar_imagem(self.img, dict_region, list_region, metodo='mss', confidence=confidence)
                if xy:
                    # input(f'A imagem foi encontrada {xy}')
                    return xy
                raise Exception('Imagem não encontrada')
            except Exception as e:
                confidence -= self.reduce_confidence
                confidence = round(confidence, 2)
                if confidence <= confidence_print:
                    name_img = os.path.basename(self.img)
                    print(f'\rImg: {name_img} | Confid: {confidence} | Erro: ({e}).', end='')
                    confidence_print -= 0.1
                if confidence <= confidence_minima:
                    if count >= n_tentativas:
                        # input(f'A imagem não foi encontrada {self.img}')
                        return False
                    count += 1
                    confidence = 1
                sleep(0.05)


    def find_img(self, name):
        path_img = resource_path(os.path.join('img', name))
        print_padao(titulo=f'Pasta local: {path_img}')
        self.img = path_img
        self.reduce_confidence = 0.1
        xy = self.locate_x_y
        if not xy:
            print_padao(texto_1='não existe x e y')
            return False                                    # <--- RETORNA FALSE SE NÃO ACHAR
        print_padao(texto_1=f'X: e Y encontrado: {xy}')
        print_padao(rodape=True)
        return xy
        

class ProgramManip():
    def __init__(self, program) -> None:
        self.program = program
        self.name_program =  os.path.splitext(self.program.lower())[0]

    def close(self):
        # programaAberto = self.program in (i.name() for i in psutil.process_iter())
        programaAberto = any(self.name_program in (p.name() or "").lower() for p in psutil.process_iter(['name']))
        if not programaAberto:
            print("Programa não está aberto:", self.program)
            return

        '''# listar de dicionarios dos processos aberto no S.O.'''
        list_pid_name = [p.info for p in psutil.process_iter(attrs=['pid', 'name']) if self.name_program in (p.info['name'] or "").lower()]
        if not list_pid_name:
            print("Nenhum processo encontrado para fechar:", self.program)
            return
        
        for dicionarioPidName in list_pid_name:
            pid = dicionarioPidName['pid']  # seleciona apenas os pid
            os.kill(pid, signal.SIGTERM)  # fecha prog atravez do seu pid,

    def open(self, what):
        for _ in range(3):
            os.startfile(what)
            print(f'Tentar abrir o programa: {self.name_program}')
            for _ in range(3):
                # programaAberto = self.program in (i.name() for i in psutil.process_iter())
                programaAberto = any(self.name_program in (p.name() or "").lower() for p in psutil.process_iter(['name']))
                if programaAberto:
                    return True
                print(f"Nenhum processo {self.program} encontrado, repetir para tentar abrir. \n")
                sleep(1)
        for p in psutil.process_iter(['name']):
            print(p.name())
        return False


class Palvclker:
    def __init__(self):
        pyautogui.PAUSE = 0
        pyautogui.FAILSAFE = True

    # def setup_tesseract(self):
    #     if getattr(sys, 'frozen', False):
    #             path_sys = Path(sys._MEIPASS)
    #         else:
    #             path_sys = Path.cwd()  # Usa o diretório de onde o comando é chamado

    #         tesseract_exe = path_sys / "tesseract" / "tesseract.exe"
    #         tessdata_dir = path_sys / "tesseract" / "tessdata"
    #     # Procura a pasta tesseract empacotada no --add-data
    #     tesseract_exe = os.path.join(base_dir, "tesseract", "tesseract.exe")
    #     tessdata_dir = os.path.join(base_dir, "tesseract", "tessdata")
    #     if os.path.exists(tesseract_exe):
    #         pytesseract.pytesseract.tesseract_cmd = tesseract_exe
    #         os.environ["TESSDATA_PREFIX"] = tessdata_dir
    #     else:
    #         # Fallback local se não estiver rodando pelo pacote do PyInstaller
    #         pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    def setup_tesseract(self):
        # 1. Define o diretório base (PyInstaller ou Diretório de Execução Atual)
        if getattr(sys, 'frozen', False):
            path_sys = Path(sys._MEIPASS)
        else:
            path_sys = Path.cwd()  # Usa a raiz de execução do terminal
        # 2. Define os caminhos prioritários (pasta local do projeto)
        tesseract_exe = path_sys / "tesseract" / "tesseract.exe"
        tessdata_dir = path_sys / "tesseract" / "tessdata"
        # 3. Fallback: Se não existir na pasta do projeto, busca na instalação padrão do Windows
        if not tesseract_exe.exists():
            tesseract_exe = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")
            tessdata_dir = Path(r"C:\Program Files\Tesseract-OCR\tessdata")
        # 4. Validação final
        if not tesseract_exe.exists():
            raise Exception(f"Tesseract não encontrado no caminho:\n{tesseract_exe}")
        # 5. Configuração
        pytesseract.pytesseract.tesseract_cmd = str(tesseract_exe)
        os.environ["TESSDATA_PREFIX"] = str(tessdata_dir)
        # Logs
        if salvar_imagens:
            print_padao(titulo="Configurando Tesseract OCR...")
            print_padao(texto_1=f"Tesseract: {tesseract_exe}")
            print_padao(texto_1=f"Tessdata: {tessdata_dir}")
            print_padao(texto_1=f"Versão do Tesseract: {pytesseract.get_tesseract_version()}")
            print_padao(rodape=True)
        return path_sys

    def capturar_all_img(self, scale, region):
        dict_imgs = {}
        with MSS() as sct:
            if region:
                screenshot = sct.grab(region)
            else:
                region = sct.regions[1] 
                screenshot = sct.grab(region)
            # print(f'\n\n################## screenshot: {screenshot} ##################\n\n')
            dict_imgs['img'] = np.array(screenshot)
        # img_cv = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        dict_imgs['img_cv'] = cv2.cvtColor(dict_imgs['img'], cv2.COLOR_BGRA2BGR)       
        # dict_imgs['gray'] = cv2.cvtColor(dict_imgs['img_cv'], cv2.COLOR_BGR2GRAY)
        dict_imgs['gray'] = cv2.cvtColor(dict_imgs['img'], cv2.COLOR_BGRA2GRAY)
        dict_imgs['grayClr'] = cv2.resize(dict_imgs['gray'], None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        dict_imgs['grayEsc'] = cv2.equalizeHist(dict_imgs['grayClr'])
        dict_imgs['grayEsc'] = cv2.GaussianBlur(dict_imgs['grayEsc'], (3, 3), 0)
        dict_imgs['inv'] = cv2.bitwise_not(dict_imgs['grayClr'])
        dict_imgs['contrClr'] = cv2.addWeighted(dict_imgs['inv'], 1.5, np.zeros(dict_imgs['inv'].shape, dict_imgs['inv'].dtype), 0, 0)
        dict_imgs['contrClrFort'] = cv2.addWeighted(dict_imgs['inv'], 3.0, np.zeros(dict_imgs['inv'].shape, dict_imgs['inv'].dtype), 0, 0)
        dict_imgs['contrClrFortMuito'] = cv2.addWeighted(dict_imgs['inv'], 6.0, np.zeros(dict_imgs['inv'].shape, dict_imgs['inv'].dtype), 0, 0)
        dict_imgs['inv'] = cv2.bitwise_not(dict_imgs['grayEsc'])
        dict_imgs['contrEsc'] = cv2.addWeighted(dict_imgs['inv'], 1.5, np.zeros(dict_imgs['inv'].shape, dict_imgs['inv'].dtype), 0, 0)
        dict_imgs['contrEscFort'] = cv2.addWeighted(dict_imgs['inv'], 3.0, np.zeros(dict_imgs['inv'].shape, dict_imgs['inv'].dtype), 0, 0)
        _, dict_imgs['threshClr'] = cv2.threshold(dict_imgs['grayClr'], 150, 255, cv2.THRESH_BINARY)
        _, dict_imgs['threshEsc'] = cv2.threshold(dict_imgs['grayEsc'], 150, 255, cv2.THRESH_BINARY)
        dict_imgs['threshInvClr'] = cv2.bitwise_not(dict_imgs['threshClr'])
        dict_imgs['threshInvEsc'] = cv2.bitwise_not(dict_imgs['threshEsc'])
        # mask = cv2.inRange(contrClrFort, 200, 255)
        _, dict_imgs['mask'] = cv2.threshold(dict_imgs['contrClrFort'], 150, 255, cv2.THRESH_BINARY)
        return dict_imgs

    def salve_imgs(self, dict_imgs, path_sys):
        path_img_original = os.path.join(path_sys, 'img', 'capturadas', 'grayEsc.png')
        path_img_grayClr = os.path.join(path_sys, 'img', 'capturadas', 'grayClr.png')
        path_img_grayEsc = os.path.join(path_sys, 'img', 'capturadas', 'grayEsc.png')
        path_img_contrasCLaro = os.path.join(path_sys, 'img', 'capturadas', 'contrClr.png')
        path_img_contrClrFort = os.path.join(path_sys, 'img', 'capturadas', 'contrClrFort.png')
        path_img_contrClrFortMuito = os.path.join(path_sys, 'img', 'capturadas', 'contrClrFortMuito.png')
        path_img_contrasEscuro = os.path.join(path_sys, 'img', 'capturadas', 'contrEsc.png')
        path_img_contrasEscuroForte = os.path.join(path_sys, 'img', 'capturadas', 'contrEscFort.png')
        path_img_threshClr = os.path.join(path_sys, 'img', 'capturadas', 'threshClr.png')
        path_img_threshEsc = os.path.join(path_sys, 'img', 'capturadas', 'threshEsc.png')
        path_img_threshInvClr = os.path.join(path_sys, 'img', 'capturadas', 'threshInvClr.png')
        path_img_threshInvEsc = os.path.join(path_sys, 'img', 'capturadas', 'threshInvEsc.png')
        path_img_mask = os.path.join(path_sys, 'img', 'capturadas', 'mask.png')
        cv2.imwrite(path_img_original, dict_imgs['img_cv'])
        cv2.imwrite(path_img_grayClr, dict_imgs['grayClr'])
        cv2.imwrite(path_img_grayEsc, dict_imgs['grayEsc'])
        cv2.imwrite(path_img_contrasCLaro, dict_imgs['contrClr'])
        cv2.imwrite(path_img_contrClrFort, dict_imgs['contrClrFort'])
        cv2.imwrite(path_img_contrClrFortMuito, dict_imgs['contrClrFortMuito'])
        cv2.imwrite(path_img_contrasEscuro, dict_imgs['contrEsc'])
        cv2.imwrite(path_img_contrasEscuroForte, dict_imgs['contrEscFort'])
        cv2.imwrite(path_img_threshClr, dict_imgs['threshClr'])
        cv2.imwrite(path_img_threshEsc, dict_imgs['threshEsc'])
        cv2.imwrite(path_img_threshInvClr, dict_imgs['threshInvClr'])
        cv2.imwrite(path_img_threshInvEsc, dict_imgs['threshInvEsc'])
        cv2.imwrite(path_img_mask, dict_imgs['mask'])

    def creat_dict_imgs_verification(self, opcao, dict_imgs):
        list_nome = ['img', 'grayClr', 'grayEsc', 'contrClr', 'contrClrFort', 'contrClrFortMuito', 'contrEsc','contrEscFort', 'threshClr', 'threshEsc', 'threshInvClr', 'threshInvEsc', 'mask']
        dict_imgs_verification={}
        if opcao in list_nome:
            dict_imgs_verification[opcao] = dict_imgs[opcao]
        else:
            for nome in list_nome:
                dict_imgs_verification[nome] = dict_imgs[nome]
        return dict_imgs_verification
        
    def get_todos_dados(self, list_psm=[3, 6, 11, 12],  opcao='all', conf_min=0, limit_caracter=2, scale=2):
        path_sys = self.setup_tesseract()
        dict_region, list_region = define_region()
        dict_imgs = self.capturar_all_img(scale, dict_region)
        if salvar_imagens:
            self.salve_imgs(dict_imgs, path_sys)
        dict_imgs_verification = self.creat_dict_imgs_verification(opcao, dict_imgs)
        dict_dados = {}
        for nome_img, img_tst in dict_imgs_verification.items():
            # nome_img = list_nome[index_img]
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
                    if dict_region:
                        x += dict_region['left']
                        y += dict_region['top']
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
    palv = 'gmail'
    salvar_imagens = True
    imageManip = ImageManip()
    dict_region, list_region = define_region()
    xy=imageManip.find_img('gmail.png')
    print(xy)
    if xy:
        clk_x_y(xy[0], xy[1])
    list_psm = [11]
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


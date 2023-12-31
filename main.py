from PIL import Image, ImageWin, ImageDraw, ImageFont
import re
import win32com.client
import win32ui
from datetime import datetime

# Ścieżki należy dostosować do urządzenia. Unikać 'relative path' bo to powoduje problemy z VBA.
LOGO_NANOTECH_PATH = r"C:\Development\Python\naklejki_pcb\assets\logo_nanotech_chrome.png"
GENERATED_STICKERS_PATH = r"C:\Development\Python\naklejki_pcb\wygenerowane_naklejki"
FONT_PATH = r"C:\Development\Python\naklejki_pcb\Fonts\Ubuntu-Medium.ttf"
PCB_NAME_FILE_PATH = r"C:\Development\Python\naklejki_pcb\pcb_name.txt"

# Nazwa drukarki
PRINTER_NAME = "Godex DT2x"

def clean_pcb_name(text, kod):
    """ Funkcja używająca wyrażenia regularnego do znalezienia i usunięcia treści w nawiasach { } jeżeli PCB jest na sprzedaż. 
    Jeżeli Montaż - zwraca kod Nanotech zamiast nazwy PCB"""
    pattern = r'\{wysyłamy na montaż\}'
    if re.search(pattern, text):
        cleaned_text = kod
    else:
        cleaned_text = re.sub(r'\{.*?\}', '', text)
    return cleaned_text

def clean_order_num(text):
    """ Funkcja używająca wyrażenia regularnego do wyodrebnienia pierwszych 4 znakow """
    cleaned_text = text[0:4]
    return cleaned_text

def generate_sticker(pcb_name:str, order_num:str, qty:str):
    """ Funkcja generująca naklejkę na płytki PCB na etykiecie o rozmiarze '50x30' 
        Zwraca ścieżkę do naklejki"""

    # Utwórz pustą naklejkę
    sticker = Image.new(mode='RGBA', size=(390,260), color='white')
    sticker_width = sticker.size[0]

    # Utwórz 'ołówek'
    pencil = ImageDraw.Draw(sticker)

    # Załaduj logo
    logo = Image.open(LOGO_NANOTECH_PATH).convert("RGBA")

    # Tu można łatwo dostosować rozmiar loga zmieniając parametr 'percent_of_increase'
    original_logo_w, original_logo_h = (340, 83)
    percent_of_increase = -0.2

    new_logo_w = int(original_logo_w + original_logo_w * percent_of_increase)
    new_logo_h = int(original_logo_h + original_logo_h * percent_of_increase)

    logo = logo.resize((new_logo_w, new_logo_h))

    # Dodaj logo do tła
    sticker.paste(logo, ((sticker_width - new_logo_w) // 2 ,20), logo)
    
    # Załaduj czcionki
    pcb_name_font_size = 30
    pcb_name_font = ImageFont.truetype(font=FONT_PATH, size=pcb_name_font_size)
    qty_font = ImageFont.truetype(font=FONT_PATH, size=25)
    order_num_font = ImageFont.truetype(font=FONT_PATH, size=21)
    
    # Oblicz długość linijki z tekstem
    text_lenght = pencil.textlength(text=pcb_name, font=pcb_name_font)

    # Jeśli tekst jest zbyt długi zmniejsz czcionkę
    while (text_lenght + 20) >= sticker_width:
        pcb_name_font_size -= 1
        pcb_name_font = ImageFont.truetype(font=FONT_PATH, size=pcb_name_font_size)
        text_lenght = pencil.textlength(text=pcb_name, font=pcb_name_font)

    # Dodaj napis z nazwą PCB
    print(f"Dodaję nazwę PCB w rozmiarze czcionki {pcb_name_font_size}")
    pcb_name_coords = ((sticker_width - text_lenght) // 2, 100)
    pencil.text(pcb_name_coords, pcb_name, font=pcb_name_font, fill=(0, 0, 0, 255))

    # Dodaj napis 'Ilość: {qty}'
    qty_text = f"{qty} szt."
    qty_text_lenght = pencil.textlength(text=qty_text, font=qty_font)
    qty_coords = ((sticker_width - qty_text_lenght) // 2, 155)
    pencil.text(qty_coords , qty_text, font=qty_font, fill=(0, 0, 0, 255))

    # Dodaj napis z Order Number
    order_num_text = f"# {order_num}   /   {datetime.now().date()}"
    order_num_text_lenght = pencil.textlength(text=order_num_text, font=order_num_font)
    order_num_coords = ((sticker_width - order_num_text_lenght) // 2, 200)
    pencil.text(order_num_coords, order_num_text, font=order_num_font, fill=(0, 0, 0, 255))
    
    sticker_path = f"{GENERATED_STICKERS_PATH}\\the_sticker.png"
    sticker.save(f"{sticker_path}")
    #sticker.show(f"{sticker_path}")

    return sticker_path

def print_sticker(sticker_path, printer_name):
    """ Funkcja drukująca naklejkę o na etykiecie o wymiarach '50x30' """

    # Inicjalizacja obiektu kontekstu urządzenia (Device Context - hDC)
    hDC = win32ui.CreateDC()

    # Utworzenie kontekstu urządzenia związanego z drukarką o określonej nazwie
    hDC.CreatePrinterDC(printer_name)

    # Otwarcie pliku z obrazkiem etykiety
    bmp = Image.open(sticker_path)

    # Rozpoczęcie drukowania - inicjacja dokumentu i strony
    hDC.StartDoc(sticker_path)
    hDC.StartPage()

    # Utworzenie obiektu Dib na podstawie obrazka
    dib = ImageWin.Dib(bmp)

    # Narysowanie obrazka na kontekście urządzenia
    dib.draw(hDC.GetHandleOutput(), (0, 0, 390, 260))

    # Zakończenie bieżącej strony i dokumentu drukowania
    hDC.EndPage()
    hDC.EndDoc()

    # Usunięcie obiektu kontekstu urządzenia
    hDC.DeleteDC()


def get_data_from_file():
    """ Funkcja pobierająca dane z pliku .txt i zwracająca 'nazwę pcb' """

    with open(PCB_NAME_FILE_PATH, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        pcb_name = lines[0].strip() 
        order_num = lines[1].strip()
        kod = lines[2].strip()

    return pcb_name, order_num, kod

# Główna pętla programu
pcb_name, order_num, kod = get_data_from_file()
print(f"Drukowanie naklejek dla PCB: '{pcb_name}'")
qty = input("Podaj ilości dla każdej naklejki oddzielone spacjami np. '25 25 25 15 50 40'\n")
for _ in qty.split():
    sticker_path = generate_sticker(pcb_name=clean_pcb_name(pcb_name, kod), order_num=clean_order_num(order_num), qty=_)
    #print_sticker(sticker_path=sticker_path, printer_name=PRINTER_NAME)


# generate_sticker(clean_pcb_name("MTV.048  .647556 {Mati znowu będzie się tłumaczył klientowi}"), "5017", "525")


from PIL import Image, ImageWin, ImageDraw, ImageFont
import re
import sys
import win32com.client
import win32ui


LOGO_NANOTECH_PATH = r"assets\nanotech_logo.png"
GENERATED_STICKERS_PATH = r"wygenerowane_naklejki"
FONT_PATH = r"Fonts\Ubuntu-Medium.ttf"

number = 1


def clean_pcb_name(text):
    """ Funkcja używająca wyrażenia regularnego do znalezienia i usunięcia treści w nawiasach { } """
    cleaned_text = re.sub(r'\{.*?\}', '', text)
    return cleaned_text

def generate_sticker(pcb_name:str, qty:str):
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
    percent_of_increase = 0.1

    new_logo_w = int(original_logo_w + original_logo_w * percent_of_increase)
    new_logo_h = int(original_logo_h + original_logo_h * percent_of_increase)

    logo = logo.resize((new_logo_w, new_logo_h))

    # Dodaj logo do tła
    sticker.paste(logo, ((sticker_width - new_logo_w) // 2 ,20), logo)
    
    # Załaduj czcionkę
    font_size = 30
    pcb_name_font = ImageFont.truetype(font=FONT_PATH, size=font_size)

    # Oblicz długość linijki z tekstem
    text_lenght = pencil.textlength(text=pcb_name, font=pcb_name_font)

    # Jeśli tekst jest zbyt długi zmniejsz czcionkę
    while (text_lenght + 20) >= sticker_width:
        font_size -= 1
        pcb_name_font = ImageFont.truetype(font=FONT_PATH, size=font_size)
        text_lenght = pencil.textlength(text=pcb_name, font=pcb_name_font)
        print(f"Zmniejszam czcionkę do: {font_size}")

    # Oblicz koordynaty dla nazwy PCB
    pcb_name_coords = ((sticker_width - text_lenght) // 2, 130)

    # Dodaj napis z nazwą PCB
    pencil.text(pcb_name_coords, pcb_name, font=pcb_name_font, fill=(0, 0, 0, 255))

    # Dodaj napis 'Ilość:'
    qty_text = f"Ilość:  {qty}"
    qty_name_font = ImageFont.truetype(font=FONT_PATH, size=18)
    qty_text_lenght = pencil.textlength(text=qty_text, font=qty_name_font)
    pencil.text(((sticker_width - qty_text_lenght) // 2, 200) , qty_text, font=qty_name_font, fill=(0, 0, 0, 255))
    
    sticker_path = sticker.save(f"{GENERATED_STICKERS_PATH}\\the_sticker{number}.png")
    sticker.show(f"{sticker_path}")

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


def get_data_from_excel():
    """ Funkcja przyjmująca dane z excela i zwracająca 'nazwę pcb' """

    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = 1

    # Odczytaj ścieżkę do pliku tymczasowego z argumentów linii poleceń
    temp_file_path = sys.argv[1]

    # Odczytaj wartość z pliku tymczasowego
    with open(temp_file_path, 'r') as file:
        pcb_name = file.read()
        
    return pcb_name


# Główna pętla programu
pcb_name = get_data_from_excel()
print(f"Drukowanie naklejek dla PCB: '{pcb_name}'\n")
qty = input("Podaj ilości dla każdej naklejki oddzielone spacjami np. '25 25 25 15 50 40'\n")
for _ in qty.split():
    sticker_path = generate_sticker(pcb_name=pcb_name, qty=qty)
    print_sticker(sticker_path=sticker_path, printer_name="Godex DT2x")



# generate_sticker(clean_pcb_name("MTV.048.647556 {Mati znowu będzie się tłumaczył klientowi}"), "525")

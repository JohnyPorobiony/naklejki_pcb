from PIL import Image, ImageWin, ImageDraw, ImageFont
import re

LOGO_NANOTECH_PATH = r"assets\nanotech_logo.png"
GENERATED_STICKERS_PATH = r"wygenerowane_naklejki"
FONT_PATH = r"Fonts\Ubuntu-Medium.ttf"

number = 1


def clean_pcb_name(text):
    """ Funkcja używająca wyrażenia regularnego do znalezienia i usunięcia treści w nawiasach { } """
    cleaned_text = re.sub(r'\{.*?\}', '', text)
    return cleaned_text

def generate_sticker(sticker_size:str, pcb_name:str, qty:str):
    """ Funkcja generująca naklejkę na płytki PCB """

    if sticker_size == "50x30":

        # Utwórz pustą naklejkę
        sticker = Image.new(mode='RGBA', size=(390,260), color='white')
        sticker_width = sticker.size[0]

        # Utwórz 'ołówek'
        pencil = ImageDraw.Draw(sticker)

        # Załaduj logo
        logo = Image.open(LOGO_NANOTECH_PATH).convert("RGBA")

        # Tu można łatwo dostosować rozmiar loga zmieniając parametr 'percent_of_increase'
        original_logo_w, original_logo_h = (340, 83)
        percent_of_increase = -0.05

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
        
        sticker.save(f"{GENERATED_STICKERS_PATH}\\the_sticker{number}.png")
        sticker.show(f"{GENERATED_STICKERS_PATH}\\the_sticker.png")





generate_sticker("50x30", clean_pcb_name("MTV.048.647556 {Mati znowu będzie się tłumaczył klientowi}"), "525")

# name = input("Podaj nazwę PCB: \n")
# qty = input("Podaj ilości PCB oddzielone spacjami np. '25 25 25 15 50 40'\n")

# for _ in qty.split():
#     generate_sticker("50x30", clean_pcb_name(name), _)
#     number += 1
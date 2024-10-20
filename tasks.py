from robocorp.tasks import task
from RPA.Excel.Files import Files

# Heikki työskentelyalue
# Kyhäsin tämän kaltaisen. Eli, eli, funktio avaa sen taulun ja tutkii for looppia käyttäen pylvästä, komponentti ja hinta. 
# Se aloittaa 2. riviltä, koska ensimmäinen rivi on tarkoitettu nimikategorioille. Jos hinta rivillä ei ole mitään, niin se ottaa komponentin nimen sille varatulta solulta ja puskee sen components nimiseen listaan, jatkaen tätä toimintaa siihen asti kunnes komponentteja ei enää löydy. Tämän jälkeen se sulkee excelin ja palauttaa listan globaaliin käyttöön.
# Käytin tätä kirjastoo ja dokumentointia https://sema4.ai/docs/automation/libraries/rpa-framework/rpa-excel-files/
def read_components():
    excel = Files()
    components = []
    
    try:
        excel.open_workbook("Komponenttitaulukko.xlsx")
        total_rows = excel.find_empty_row() - 1

        for row in range(2, total_rows +1):
            component = excel.get_cell_value( column=1, row=row)
            price = excel.get_cell_value(column=2, row=row)

            if not component:
                break

            if not price:
                components.append(component)
    finally:
        excel.close_workbook()

    return components





# /Heikki Työskentelyalue



# /Jasper Työskentelyalue
components = read_components()
@task
def minimal_task():
    message = "Hello"
    message = message + " World!"
    print(components)







# /Kauri työskentelyalue

# Lukee (toistaiseksi taulukkoon kovakoodattua) dataa ja
# tuuttaa sen excel-tiedostoon. Tällä hetkellä aika kämänen ratkaisu,
# mutta sentään jotain pohjaa. Periaattessa tämän häntäpäähän voisi lisätä toisen toiminnon, joka
# kopioi komponenttien nimet ja kirjoittaa ne uudelleen A-sarakkeen tyhjiin kohtiin, niin lista uusiutuu.
def write_to_excel():
    excel = Files()
    excel.open_workbook("taulukkotesti.xlsx")
    
    # debug-taulukko
    # tähän sitten joku elegantimpi ratkaisu, kun saadaan revittyä tietoa netistä
    table = {
        "price": [600, 700, 350],
        "shop": ["Verkkokauppa", "Datatronic", "Proshop"]
    }

    prices = table["price"]
    shops = table["shop"]

    # ekat tyhjät rivit
    empty_row = find_next_empty_row(excel)

    # kirjoittaa taulukkoon saatujen rivinumeroiden perusteella
    for i in range(len(prices)):
        current_row = empty_row + i
        excel.set_cell_value(current_row, "B", prices[i])
        excel.set_cell_value(current_row, "C", shops[i])

    
    excel.save_workbook()



# Etsii tyhjiä rivejä rivi nro 2:sta alkaen
# Tämä EI varmaan ole pomminvarma. Varmaankin hajoaa jos esim. hintatietoa ei löydy

def find_next_empty_row(excel):
    row = 2 
    while True:
        value_in_b = excel.get_cell_value(row, "B") #prices
        value_in_c = excel.get_cell_value(row, "C")# shops
        
        # jos tyhjiä, palauta tämä
        if not value_in_b and not value_in_c:
            return row
        row += 1


#def send_email():
    # funktio, joka etsii dataa excelistä ja lähettää sen sähköpostiin menee tänne
    # todennäköisesti tarvii robocorp vault -kirjaston sähköpostitilille pääsyyn
    # get_worksheet_value(row: int, column: Union[str, int], name: Optional[str] = None)


# /Kauri työskentelyalue
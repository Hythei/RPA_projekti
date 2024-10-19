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

# /Kauri työskentelyalue

# /Jasper Työskentelyalue
components = read_components()
@task
def minimal_task():
    message = "Hello"
    message = message + " World!"
    print(components)


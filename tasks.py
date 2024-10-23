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
            price1 = excel.get_cell_value(column=2, row=row)
            price2 = excel.get_cell_value(column=3, row=row)

            if not component:
                break

            if not price1 or price2 :
                components.append(component)
    finally:
        excel.close_workbook()

    return components

components = read_components()




# /Heikki Työskentelyalue



# /Jasper Työskentelyalue
# Olin käyttänyt Seleniumia webscraping tekemiseen.
# Pistin sen niin, että se jatkaa 15 sivuun asti, koska muuten siinä menee liian kauan, kun se käy läpi kaikki sivut. Lisäksi jos kone menee lepotilaan niin se lakkaa toimimasta.
# Se nyt lukee ensimmäiseksi Verkkokaupasta komponentin nimet ja hinnat, jonka jälkeen se menee suoraan proshoppiin, josta se jatkaa scrapeemista.
# Koodin loppussa olin lisännyt että se tekee xlsl file johon se listaa komponentit, vain sitä varten että näen sen toimintaa.
# En ole varma pitäisikö lisätä Datatronic, kun siellä komponenttit lajiteltu erikseen.
# HUOM!!!! Koodia pitää vielä sovittaa teidän koodiin.

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time

# Set up the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# URL for Verkkokauppa and Proshop
urls = {
    'Verkkokauppa': "https://www.verkkokauppa.com/fi/catalog/tietokoneiden-komponentit/products",
    'Proshop': "https://www.proshop.fi/Komponentit-ja-oheislaitteet"
}

# Maximum number of pages to scrape from each website
max_pages = 15

# Lists to hold data for both websites
all_product_names = []
all_product_details = []
all_sources = []

def scrape_verkkokauppa():
    current_page = 1
    while current_page <= max_pages:
        time.sleep(5)
        print(f"Verkkokauppa: Page {current_page} loaded. Extracting products...")

        products = driver.find_elements(by="xpath", value='//li[contains(@class, "iIZx")]')
        print(f"Found {len(products)} products on this page.")

        for product in products:
            try:
                name = product.find_element(by="xpath", value='.//span[contains(@class, "qEFQO")]').text
                details = product.find_element(by="xpath", value='.//span[contains(@class, "SowTR")]').text

                all_product_names.append(name)
                all_product_details.append(details)
                all_sources.append('Verkkokauppa')
                print(f"Extracted from Verkkokauppa: {name}, {details}")
            except Exception as e:
                print(f"Error extracting data for a product on Verkkokauppa: {e}")

        try:
            next_button = driver.find_element(by="xpath", value='//a[contains(@class, "eKuPQo")]')
            if next_button and current_page < max_pages:
                print(f"Navigating to Verkkokauppa page {current_page + 1}...")
                next_button.click()
                current_page += 1
                time.sleep(3)
            else:
                break
        except Exception as e:
            print("No more pages or error clicking the next button on Verkkokauppa:", e)
            break

def scrape_proshop():
    current_page = 1
    while current_page <= max_pages:
        time.sleep(5)
        
        # Navigate to the correct page by modifying the URL (e.g., ?pn=2, ?pn=3, etc.)
        proshop_url = f"https://www.proshop.fi/Komponentit-ja-oheislaitteet?pn={current_page}"
        print(f"Proshop: Navigating to {proshop_url}")
        driver.get(proshop_url)
        
        print(f"Proshop: Page {current_page} loaded. Extracting products...")

        products = driver.find_elements(by="xpath", value='//li[contains(@class, "row toggle")]')
        print(f"Found {len(products)} products on this page.")

        for product in products:
            try:
                name = product.find_element(by="xpath", value='.//h2[contains(@class, "truncate-overflow")]').text
                details = product.find_element(by="xpath", value='.//span[contains(@class, "site-currency-lg")]').text

                all_product_names.append(name)
                all_product_details.append(details)
                all_sources.append('Proshop')
                print(f"Extracted from Proshop: {name}, {details}")
            except Exception as e:
                print(f"Error extracting data for a product on Proshop: {e}")

        current_page += 1
        if current_page > max_pages:
            break

try:
    # Scrape Verkkokauppa
    driver.get(urls['Verkkokauppa'])
    scrape_verkkokauppa()

    # Scrape Proshop
    scrape_proshop()

    # Create a DataFrame with all scraped data
    df = pd.DataFrame({
        'Product Name': all_product_names,
        'Product Details': all_product_details,
        'Source': all_sources
    })

    # Save the DataFrame to an Excel file
    output_file = 'computer_components.xlsx'
    df.to_excel(output_file, index=False)

    print(f"Data has been written to {output_file}")

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    driver.quit()


























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

"""
Ensin haetaan tuote lista saksalaiselta nettisivusta komponentti tuotelista, josta voidaan lukea tuotekoodi. 
Ensimmäinen haku on tuotekatekorian mukaan ja seuraavat haut on sen jälkeen sivu numeroilla. 
Sivu numeroita voidaan muokkaa muuttamalla "max-page" määrä.
Lopuksi tekee csv listan.
Sen jälkeen kun se on saanut tuotekoodi listan niin se alkaa webscrapee tuotteet menemällä sivun kauppaan
ja kirjoittaa hakuu tuotekoodin.
Jos se löytää tuotteen molemmista kaupoista se listaa sen csv ja exceliin,
mutta jos jommassa kummassa kaupassa ei löydy tuotetta niin se ei listaa sitä.

Se tallentaa csv ja exceli tiedostoon tuotteet, jotka löytyy molemmista kaupoista.

Tiedostossa tuotteet listautuu:

Product Name    Product Number      Proshop Price   Verkkokauppa Price      Halvin(kauppa)



Kun tuotteet on listattu excelissä se tekee lopuksi hintavertailu, jonka se kertoo kummassa kaupassa on halvempi hinta.

"""
from robocorp.tasks import task
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up the WebDriver
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))



import csv
#import chromedriver_autoinstaller
#from selenium import webdriver
from selenium.webdriver.common.by import By



# Automaattinen ChromeDriverin haku ja asennus
#chromedriver_autoinstaller.install()

# Luo selaininstanssi
driver = webdriver.Chrome()
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def lue_excel():

    file_name = "product_prices.xlsx"
    data = pd.read_excel(file_name,
              header=0,
                index_col=False,
                #chunksize=10000,
                keep_default_na=True
                )
    return data

def hintavertailu(df):
    
    # Määrittele ehdot ja valinnat
    conditions = [

        (df["Proshop Price"] < df["Verkkokauppa Price"]),

        (df["Proshop Price"] > df["Verkkokauppa Price"]),

        (df["Proshop Price"] == df["Verkkokauppa Price"])

    ]

    choices = ["Proshop", "Verkkokauppa", "Sama hinta"]

    # Lisää uusi sarake ehtojen perusteella
    df["Halvempi"] = np.select(conditions, choices, default="Ei hintaa")

    return df

def fetch_https(url):
    # Aseta verkkosivun URL
    # Tee GET-pyyntö sivulle
    response = requests.get(url)
    response.raise_for_status()  # Tarkistaa, että sivu latautui oikein

    # Analysoi sivun HTML-rakenne
    soup = BeautifulSoup(response.text, 'html.parser')

    return soup

def next_page(page, product_codes):

    url = f"https://geizhals.eu/?cat=gra16_512&v=e&hloc=pl&hloc=uk&sort=t&pg={page}#productlist"
    soup=fetch_https(url)

    for item in soup.find_all('div', class_='productlist__mpn'):  # Muuta class oikeaksi
        code = item.get_text(strip=True)
        product_codes.append(code)

    return product_codes

def Tuotelista():

    url = "https://geizhals.eu/?cat=gra16_512&asuch=&bpmin=&bpmax=&v=e&hloc=pl&hloc=uk&plz=&dist=&mail=&sort=t&bl1_id=30&togglecountry=set"
    soup=fetch_https(url)

    # Etsi HTML-elementit, joissa on tuotekoodeja
    product_codes = []

    #<div class="productlist__mpn">GV-N408SWF3V2-16GD</div>
    for item in soup.find_all('div', class_='productlist__mpn'):  # Muuta class oikeaksi
        code = item.get_text(strip=True)
        product_codes.append(code)

    # Lue next page
    page=1
    max_page=3  # Anna max sivujen määrä

    while page < (max_page +1):
        page += 1
        product_codes = next_page(page,product_codes)


    """
    url = f"https://geizhals.eu/?cat=gra16_512&v=e&hloc=pl&hloc=uk&sort=t&pg={page}#productlist"
    soup=fetch_https(url)

    for item in soup.find_all('div', class_='productlist__mpn'):  # Muuta class oikeaksi
        code = item.get_text(strip=True)
        product_codes.append(code)
    """

    df=pd.DataFrame(product_codes,columns=["Product Code"])
    print(df)

    # Tallenna tulokset CSV-tiedostoon
    with open('product_codes2.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Product Code"])
        for code in product_codes:
            writer.writerow([code])

    print("Tuotekoodit tallennettu tiedostoon.")

    return


def save_excel(df, file_name):
    # Optionally, save to Excel
    df.to_excel(f'{file_name}.xlsx', index=False)
    print("Talletettu exceliin.")
    return

def save_csv(df, file_name):
    df.to_csv(f'{file_name}.csv', index=False)
    print("Talletettu CSV -tiedostoon.")
    return

# Funktio hinnan hakemiseen Proshopista
def get_price_from_proshop(product_code):
    url = f"https://www.proshop.fi/?s={product_code}"
    driver.get(url)
    
    time.sleep(5)  # Odota, että sivu latautuu

    try:
        # Odota, että hintaelementti latautuu
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'site-currency-lg'))
        )
        # Etsi hinta-elementti
        #price_element = driver.find_element(By.CLASS_NAME, 'site-currency-lg')

        # etsi nimi-elementti
        name_element = driver.find_element(by="xpath", value='.//h2[contains(@class, "truncate-overflow")]').text
        
        # Poista mahdolliset ylimääräiset merkit ja korvaa pilkku pisteellä
        price_text = price_element.text.replace(",", ".").replace("€", "").strip()

        return float(price_text), name_element  # Palauta hinta float-tyyppinä vertailua varten

        #return price_element.text
    except Exception as e:
        #print(f"Hintaa ei löytynyt Proshopista tuotteelle {product_code}: {e}")
        print(f"Hintaa ei löytynyt Proshopista tuotteelle {product_code}:")
        return 0, None # None

# Funktio hinnan hakemiseen Verkkokauppa.comista

def get_price_from_verkkokauppa(product_code):
    url = f"https://www.verkkokauppa.com/fi/search?query={product_code}"
    driver.get(url)

    try:
        # Odota, että hintaelementti latautuu
        price_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(@class, 'sc-fxwrCY') and contains(text(), 'Hinta')]"))
        )

        # Poista "Hinta" ja korvaa pilkku pisteellä
        price_text = price_element.text.replace("Hinta", "").strip().replace("€.", "").strip()
        if price_text == "": price_text = 0
        return float(price_text)  # Palauta hinta float-tyyppinä vertailua varten

        # Palauta hinta, jos se löytyy
        #return price_element.text if "€" in price_element.text else None

    except Exception as e:
        #print(f"Hintaa ei löytynyt Verkkokauppa.comista tuotteelle {product_code}: {e}")
        print(f"Hintaa ei löytynyt Verkkokauppa.comista tuotteelle {product_code}:")
        return 0 #None



def Tuote_hinnat():
    # Lue CSV-tiedoston tuotekoodit
    product_codes = []
    with open('product_codes.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            product_codes.append(row['Product Code'])




    # Testikoodi tuotteille
    """
    product_codes = ["ZT-D40720H-10M", "RX 7800 XT 16G-L/OC", "11330-02-20G"]  # Lisää tuotteita tähän
    product_codes = ["RX 7800 XT 16G-L/OC","11330-02-20G", "ZT-D40720H-10M"]  # Lisää tuotteita tähän
    for product_code in product_codes:
        proshop_price = get_price_from_proshop(product_code)
        verkkokauppa_price = get_price_from_verkkokauppa(product_code)
        print(f"Tuotekoodi: {product_code}, Proshop hinta: {proshop_price}, Verkkokauppa hinta: {verkkokauppa_price}")
    #"""


    # Käy läpi tuotekoodit ja hae hinnat
    product_prices = []
    for product_code in product_codes:
        print(f"\nHakemassa hintoja tuotteelle: {product_code}")
        proshop_price, product_name = get_price_from_proshop(product_code)
        verkkokauppa_price = get_price_from_verkkokauppa(product_code)
        
        # Tulosta tai tallenna tiedot
        product_prices.append({
            "Product Name": product_name,
            "Product Code": product_code,
            "Proshop Price": proshop_price,
            "Verkkokauppa Price": verkkokauppa_price
        })

        # Lisää viive pyyntöjen välille (kuorman keventämiseksi)
        time.sleep(1)

    df = pd.DataFrame(product_prices, columns=["Product Name","Product Code", "Proshop Price", "Verkkokauppa Price"])
    # Poista rivit, joissa jompikumpi sarakkeista ("Proshop Price" tai "Verkkokauppa Price") on 0.00
    df = df[(df["Proshop Price"] != 0.00) & (df["Verkkokauppa Price"] != 0.00)]

    print("TUOTTEET.. \n",df)
    file_name="product_prices"
    save_excel(df, file_name)
    save_csv(df, file_name)
    """
    # Tallenna tulokset CSV-tiedostoon
    with open('data/product_prices.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["Product Code", "Proshop Price", "Verkkokauppa Price"])
        writer.writeheader()
        for product in product_prices:
            writer.writerow(product)
    #"""
    print("Hinnat tallennettu tiedostoon.")


    # Sulje selainohjain lopuksi
    driver.quit()
    return df

@task
def main_scrape():

    Tuotelista()

    df = Tuote_hinnat()
    #if df.empty:
        #df = lue_excel()
    df = hintavertailu(df)
    print(df)

    file_name="compared_product"
    save_excel(df, file_name)

#main_scrape()

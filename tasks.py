from robocorp.tasks import task

# Heikki työskentelyalue
components = ["AMD Radeon RX 7900XTX", "Nvidia RTX 4060"]

# components arrayta voidaan käsitellä luonnollisesti käyttäen for -looppia tässä tapauksessa, 
# Voidaan esim käsittelyvaiheess luoda "process_component" -function, joka käy ne läpi yksitellen
    # def process_component(components):
        # print(f"Processing component: {component}")

# /Heikki Työskentelyalue
@task
def minimal_task():
    message = "Hello"
    message = message + " World!"

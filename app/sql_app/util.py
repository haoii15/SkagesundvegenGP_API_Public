
non_hub = ["Skagehrain GP", "Saudisund GP", "Simola GP", "Skaustralia GP", "Stakkelona GP", "Smonaco GP", "Stazerbadsjan GP"]

hub = ["Ska GP", "Zandesund GP", "Stonkza GP", "Community GP", "Singasund GP", "Staxico GP", "Uland GP", "Stakkelagos GP", "Stakke Dhabi GP"]


def insert2022(self):
    for gp in non_hub:
        self.insert_laps(gp, 0)
    for gp in hub:
        self.insert_laps(gp, 1)
    
    self.active("Uland GP")

def setup(self):
    self.drop_all()
    self.create_all()
    self.insert2022()

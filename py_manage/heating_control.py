
class heating_system():
    def __init__(self, status: bool):
        self.heating_status = status
        self.heating_off()
        

    def heating_on(self):
        print("Heating system is ON")
        self.heating_status = 1
        # Also set the RP GPIO


    def heating_off(self):
        print("Heating system is OFF")
        self.heating_status = 0


    def get_heating_status(self):
        return self.heating_status
        # Also clear the RP GPIO

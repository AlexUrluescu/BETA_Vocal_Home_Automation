from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider
import sys
from PyQt5.QtCore import Qt
import requests
import json
from PyQt5.QtCore import QTimer
from senzor import dht_sensor
from guiFlow import GuiFlow
from check_internet_connection import internet_checker
import heating_control
import logging
from check_internet_connection import internet_checker

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = QApplication(sys.argv)

oneHourInMls = 3600000

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # // DEV
        # self.url = "https://beta-vocal-home-automation-1.onrender.com"

        # LOCAL
        self.url = "http://localhost:3001"

        self.setWindowTitle("Exemplu PyQt5")
        self.setGeometry(100, 100, 1000, 600)

        self.status = ""
        self.treshlod = 0
        self.id_treshold = ""
        self.temperature = "0"
        self.hysteresis = 0.5
        self.humidity = "0"
        self.text_alert = "Temperatura a fost actualizata"
        self.text_error_hardware = "Check your hardware"
        self.val = 30
        self.button_status = True
        self.id_status = ""

        # this variable stop the main timer when the treshold is changing
        self.change_treshold = 0

        self.senzor = dht_sensor()
        self.GuiFlow = GuiFlow(self.url)
        self.internet_checker = internet_checker()
        self.heating_system = heating_control.heating_system(False)
        self.temp_senzor = ""
        self.hum_senzor = ""

        # this timer controls when the user is changing the treshold with the buttons +/-
        # when the timer is done, the function "active_alert" will be executed
        self.timer_alert = QTimer()
        self.timer_alert.setInterval(5000)
        self.timer_alert.setSingleShot(True)
        self.timer_alert.timeout.connect(self.activate_alert)

        self.timer10 = QTimer()
        self.timer10.setInterval(5000)
        self.timer10.setSingleShot(True)
        self.timer10.timeout.connect(self.hide_div)

        self.timer_checker_status = QTimer()
        self.timer_checker_status.setInterval(5000)

        self.timer_test = QTimer()
        self.timer_test.setInterval(5000)
        
        self.timer_checker_treshold = QTimer()
        self.timer_checker_treshold.setInterval(5000)

        # error counters
        self.error_senzor_counter = 0


        # style for the slider when is ON
        self.stil_on = """
            QSlider::groove:horizontal {
                background-color: #ddd;
                height: 35px;
                border-radius: 17px;
            }
            
                QSlider::handle:horizontal {
                    background-color: green;
                    width: 35px;
                    margin: -5px 0;
                    border-radius: 17px;
                }
            """
        # style for the slider when is OFF
        self.stil_off = """
            QSlider::groove:horizontal {
                background-color: #ddd;
                height: 35px;
                border-radius: 17px;
            }
            
                QSlider::handle:horizontal {
                    background-color: red;
                    width: 35px;
                    margin: -5px 0;
                    border-radius: 17px;
                }
            """

        treshold = ""
        temperature = "Temp"
        humidity = "Hum"
        text_alert = "Alert"
        text_error_hardware = "The hardware has an error"

        # --------------- SLIDER -------------------------------------------
        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(1)
        self.slider.setGeometry(460,70, 150, 20) 
        # self.slider.setValue(self.val)
        self.slider.setFixedSize(135, 60)
        self.slider.valueChanged.connect(self.slider_value_changed)

        # ------------------------- BUTTONS ----------------------------------------------------------------------
        self.button_plus = QPushButton('+', self)
        self.button_plus.setGeometry(605, 110, 80, 80)
        self.button_plus.setStyleSheet("QPushButton { width: 50px; height: 50px; border-radius: 40%; background-color: #D8D9DA; font-size: 45px; font-family: 'Poppins', sans-serif;}")
        self.button_plus.setEnabled(self.button_status)
        self.button_plus.clicked.connect(self.button_plus_clicked)

        self.button_minus = QPushButton('-', self)
        self.button_minus.setGeometry(605, 270, 80, 80)
        self.button_minus.setStyleSheet("QPushButton { width: 50px; height: 50px; border-radius: 40%; background-color: #D8D9DA; font-size: 45px; font-family: 'Poppins', sans-serif; }")
        self.button_minus.setEnabled(self.button_status)
        self.button_minus.clicked.connect(self.button_minus_clicked)

        # ------------------------ CONTAINERS ---------------------------------
        self.div_treshold = QWidget(self)
        self.div_treshold.setStyleSheet("QWidget { background-color: white; color: black; border-radius: 75%; font-family: 'Poppins', sans-serif; }")
        self.div_treshold.setFixedSize(150, 150)
        self.div_treshold.move(450, 150)

        self.div_home_temp = QWidget(self)
        self.div_home_temp.setStyleSheet("QWidget { background-color: white; color: black; border-radius: 75%; font-family: 'Poppins', sans-serif; }")
        self.div_home_temp.setFixedSize(150, 150)
        self.div_home_temp.move(160, 50)

        self.div_home_hum = QWidget(self)
        self.div_home_hum.setStyleSheet("QWidget { background-color: white; color: black; border-radius: 75%; font-family: 'Poppins', sans-serif; }")
        self.div_home_hum.setFixedSize(150, 150)
        self.div_home_hum.move(160, 230)

        self.div_text_alert = QWidget(self)
        self.div_text_alert.setStyleSheet("QWidget { background-color: green; border-radius: 20px; font-family: 'Poppins', sans-serif; font-size: 10px; }")
        self.div_text_alert.setFixedSize(350, 40)
        self.div_text_alert.move(400, 20)
        self.div_text_alert.hide()

        self.div_error_hardware = QWidget(self)
        self.div_error_hardware.setStyleSheet("QWidget { font-family: 'Poppins', sans-serif; }")
        self.div_error_hardware.setFixedSize(250, 40)
        self.div_error_hardware.move(110, 7)
        self.div_error_hardware.hide()


        # ------------------------- LAYOUT CONTAINERS -------------------------
        self.div_treshold_layout = QVBoxLayout(self.div_treshold)
        self.div_treshold.setLayout(self.div_treshold_layout)

        self.div_home_temp_layout = QVBoxLayout(self.div_home_temp)
        self.div_home_temp.setLayout(self.div_home_temp_layout)

        self.div_home_hum_layout = QVBoxLayout(self.div_home_hum)
        self.div_home_hum.setLayout(self.div_home_hum_layout)

        self.div_text_alert_layout = QVBoxLayout(self.div_text_alert)
        self.div_text_alert.setLayout(self.div_text_alert_layout)

        self.div_error_hardware_layout = QVBoxLayout(self.div_error_hardware)
        self.div_error_hardware.setLayout(self.div_error_hardware_layout)

        # -------------------------- LABELS -----------------------------------
        self.treshold_label = QLabel(treshold, self.div_treshold)
        self.treshold_label.setStyleSheet(" QLabel { font-size: 50px; border: none; }")
        self.treshold_label.setText(str(self.treshlod))

        self.home_temp_label = QLabel(temperature, self.div_home_temp)
        self.home_temp_label.setStyleSheet(" QLabel { font-size: 40px; }")
        self.home_temp_label.setText(f"{self.temperature} °C")
        
        self.home_hum_label = QLabel(humidity, self.div_home_hum)
        self.home_hum_label.setStyleSheet(" QLabel { font-size: 40px; }")
        self.home_hum_label.setText(f"{self.humidity} %")
        
        self.text_alert_label = QLabel(text_alert, self.div_text_alert)
        self.text_alert_label.setStyleSheet(" QLabel { font-size: 20px; color: white; }")
        self.text_alert_label.setText(f"{self.text_alert}")

        self.text_error_hardware_label = QLabel(text_error_hardware, self.div_error_hardware)
        self.text_error_hardware_label.setStyleSheet(" QLabel { color: red; font-family: 'Arial'; font-size: 15px;}")
        self.text_error_hardware_label.setText(f"{self.text_error_hardware}")

        # ------------------------ LAYOUT ADDS ------------------------------
        self.div_treshold_layout.addWidget(self.treshold_label)
        self.div_home_temp_layout.addWidget(self.home_temp_label)
        self.div_home_hum_layout.addWidget(self.home_hum_label)
        self.div_text_alert_layout.addWidget(self.text_alert_label)
        self.div_error_hardware_layout.addWidget(self.text_error_hardware_label)

        # ------------------------ CENTER THE LABELS ---------------------------
        self.div_treshold_layout.setAlignment(Qt.AlignCenter) 
        self.div_home_temp_layout.setAlignment(Qt.AlignCenter) 
        self.div_home_hum_layout.setAlignment(Qt.AlignCenter)  
        self.div_text_alert_layout.setAlignment(Qt.AlignCenter)  
        self.div_error_hardware_layout.setAlignment(Qt.AlignCenter)  


        self.initUI()
        self.init_timer_data_senzors()
        self.init_timer_checker_status()
        self.init_timer_checker_treshold()
        self.init_timer_test()
        

    # this function control the slider's value, when he is changing
    def slider_value_changed(self, value):
        if(value == 0):
            self.slider.setStyleSheet(self.stil_off)
            self.button_status = False
            self.button_plus.setEnabled(self.button_status)
            self.button_minus.setEnabled(self.button_status)

            payload = {'status': 0}
            json_payload = json.dumps(payload)
            url = f"{self.url}/update-status/{self.id_status}"
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, headers=headers, data=json_payload)
            
            if response.status_code == 200:
                self.status = 0

            else:
                logging.info(f"Error ({response.status_code}): {response.text}")

        
        else:
            self.slider.setStyleSheet(self.stil_on)
            self.button_status = True
            self.button_plus.setEnabled(self.button_status)
            self.button_minus.setEnabled(self.button_status)

            payload = {'status': 1}
            json_payload = json.dumps(payload)
            url = f"{self.url}/update-status/{self.id_status}"
            headers = {'Content-Type': 'application/json'}
            response = requests.put(url, headers=headers, data=json_payload)
            
            if response.status_code == 200:
                self.status = 1

            else:
                logging.info(f"Error ({response.status_code}): {response.text}")


    # when we fetch the status, we use this function to update the slider status
    def change_status_slider(self, value):
        if(value == 1):
            # the slider is ON
            self.slider.setStyleSheet(self.stil_on)
            self.slider.setValue(1)
            self.button_status = True
            self.button_plus.setEnabled(self.button_status)
            self.button_minus.setEnabled(self.button_status)
        
        elif(value == 0):
            # the slider is OFF
            self.slider.setValue(0)
            self.slider.setStyleSheet(self.stil_off)
            self.button_status = False
            self.button_plus.setEnabled(self.button_status)
            self.button_minus.setEnabled(self.button_status)


    # this function fetch the heating's status when the app opens
    def fetch_heating_status(self):
        internet: bool = self.internet_checker.check_internet_connection()

        if(internet):
            url = f"{self.url}/status"

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                status_value = int(data[0]["status"])
                self.status = status_value
                self.val = status_value
                self.id_status = data[0]["_id"]

                if self.status == 1:
                    self.button_status = True
                    self.change_status_slider(1)
                
                else:
                    self.button_status = False
                    self.change_status_slider(0)


            else:
                logging.info("Error to fetching the endpoint heatingstatus")

        else:
            self.status = 0
            self.button_status = False
            self.change_status_slider(0)
    

    # this function fecth the treshold value when the app opens
    def fetch_treshold(self):
        internet: bool = self.internet_checker.check_internet_connection()

        if(internet):
            url = f"{self.url}/treshold"
    
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                value = data[0]["temperature"]

                self.treshlod = value
                self.id_treshold = data[0]["_id"]
                self.treshold_label.setText(str(self.treshlod))

            else:
                logging.info("Error to fetching the endpoint heatingtemp")
        
        else:
            self.treshlod = 18
            self.treshold_label.setText(str(self.treshlod))



    def initUI(self):
        print("intra imagine")
        self.setStyleSheet("background-color: #F0F0F0;")

        # ------------------------ VARIABLES --------------------------------------------------------------------

        if(self.status == 1):
            self.slider.setValue(1)
            self.slider.setStyleSheet(self.stil_on)

        else:
            self.slider.setValue(0)
            self.slider.setStyleSheet(self.stil_off)

        # -------------------------- SLIDER -------------------------------------
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(1)
        slider.setValue(30)
        slider.setTickInterval(1)
        slider.setTickPosition(QSlider.TicksBelow)
        slider.setFixedSize(150, 100)
        slider.move(300, 300)


    def hide_div(self):
        self.div_text_alert.hide()


    # this function insert the treshold's value to Mongo DB
    def activate_alert(self):
        self.timer10.start()

        logging.debug("The function active_alert is running ...")
        self.div_text_alert.show()

        payload = {'temperature': self.treshlod}
        json_payload = json.dumps(payload)
        url = f"{self.url}/update-treshold/{self.id_treshold}"
        headers = {'Content-Type': 'application/json'}
        response = requests.put(url, headers=headers, data=json_payload)
        
        if response.status_code == 200:
            # this variable controls when the treshold is changing, to not have timers conflict
            self.change_treshold = 0

            logging.debug("The function active_alert is done successfully ...")

        else:
           logging.info(f"Error at activate_alert ({response.status_code}): {response.text}")       
        

    def button_plus_clicked(self):
        self.change_treshold = 1
  
        self.timer_alert.stop()
        self.timer_alert.start()

        self.treshlod = self.treshlod + 0.5
        self.treshold_label.setText(str(self.treshlod))


    def button_minus_clicked(self):
        self.change_treshold = 1

        self.timer_alert.stop()
        self.timer_alert.start()

        self.treshlod = self.treshlod - 0.5
        self.treshold_label.setText(str(self.treshlod))



    # this function get senzor's data from the API (remote) or senzor class (local)
    def get_data_senzors(self):
        # first we fetch what the senzor returns, if he returns 0 means that he doesn't fetch the temperature
        temp_senzor_return = self.senzor.get_t()

        if temp_senzor_return == 0:
            # increment the variable error_senzor_counter every time the senzor doesn't fetch the temperature
            self.error_senzor_counter = self.error_senzor_counter + 1

        # if the senzor fetch a real temperature we will update the value in the interface
        else:
            self.temp_senzor = temp_senzor_return
            self.home_temp_label.setText(f"{self.temp_senzor} °C")

            # reset the error_senzor_counter to 0, because he returned a correct value
            self.error_senzor_counter = 0


        # first we fetch what the senzor returns, if he returns 0 means that he doesn't fetch the humidity
        hum_senzor_return = self.senzor.get_h()

        if hum_senzor_return == 0:
            # increment the variable error_senzor_counter every time the senzor doesn't fetch the humidity
            self.error_senzor_counter: int = self.error_senzor_counter + 1


        # if the senzor fetch a real humidity we will update the value in the interface
        else:
            self.hum_senzor = hum_senzor_return
            self.home_hum_label.setText(f"{self.hum_senzor} %")

            # reset the error_senzor_counter to 0, because he returned a correct value
            self.error_senzor_counter: int = 0

        
        if self.error_senzor_counter >= 50:
            if(self.div_error_hardware.isVisible()):
                logging.info("The hardware error is already on screen")
            
            else:  
                self.div_error_hardware.show()

        if(temp_senzor_return != 0 and hum_senzor_return != 0):
            self.GuiFlow.sendSenzorTemperatureAndHumidity(temp_senzor_return, hum_senzor_return)

    
    def get_data_senzors_to_save_into_db(self):
        # first we fetch what the senzor returns, if he returns 0 means that he doesn't fetch the temperature
        temp_senzor_return = self.senzor.get_t()

        if temp_senzor_return == 0:
            # increment the variable error_senzor_counter every time the senzor doesn't fetch the temperature
            self.error_senzor_counter = self.error_senzor_counter + 1

        # if the senzor fetch a real temperature we will update the value in the interface
        else:
            self.temp_senzor = temp_senzor_return
            self.home_temp_label.setText(f"{self.temp_senzor} °C")

            # reset the error_senzor_counter to 0, because he returned a correct value
            self.error_senzor_counter = 0


        # first we fetch what the senzor returns, if he returns 0 means that he doesn't fetch the humidity
        hum_senzor_return = self.senzor.get_h()

        if hum_senzor_return == 0:
            # increment the variable error_senzor_counter every time the senzor doesn't fetch the humidity
            self.error_senzor_counter: int = self.error_senzor_counter + 1


        # if the senzor fetch a real humidity we will update the value in the interface
        else:
            self.hum_senzor = hum_senzor_return
            self.home_hum_label.setText(f"{self.hum_senzor} %")

            # reset the error_senzor_counter to 0, because he returned a correct value
            self.error_senzor_counter: int = 0

        
        if self.error_senzor_counter >= 50:
            if(self.div_error_hardware.isVisible()):
                logging.info("The hardware error is already on screen")
            
            else:  
                self.div_error_hardware.show()

        if(temp_senzor_return != 0 and hum_senzor_return != 0):
            self.GuiFlow.insertDataIntoDB(temp_senzor_return, hum_senzor_return)


        # BUG -------
        # if(self.hum_senzor != 0 and self.temp_senzor!=0):
        #     internet_connection: bool = self.internet_checker.check_internet_connection()
        #     if internet_connection:
        #         logging.info("exists connection")
        #     else:
        #         logging.info("doesn't exist connection")


        # Varianta cu luat date de la senzori direct de la API -----------------------
        # url = f"{self.url}/senzor"
        # print("iasa")

        # response = requests.get(url)

        # data = response.json()

        # print(f"Temp_Home: {data['temperature']}")
        # print(f"Hum_Home: {data['humidity']}")

        # self.temp_senzor = data['temperature']
        # self.home_temp_label.setText(f"{self.temp_senzor} °C")

        # self.hum_senzor = data['humidity']
        # self.home_hum_label.setText(f"{self.hum_senzor} %")
        if self.status == 0:
            # logging.info("Heating system is OFF")
            self.heating_system.heating_off()
            self.div_treshold.setStyleSheet("QWidget { background-color: white;color: black; border-radius: 75%; font-family: 'Poppins', sans-serif; border: none; }")    
        else:
            if(self.treshlod >= (int(self.temp_senzor) + self.hysteresis)):
                # logging.info("Heating system is ON")
                self.heating_system.heating_on()
                self.div_treshold.setStyleSheet("QWidget { background-color: white; color: black; border-radius: 75%; font-family: 'Poppins', sans-serif; border: 8px solid gold; }")
            else:
                # logging.info("Heating system is OFF")
                self.heating_system.heating_off()
                self.div_treshold.setStyleSheet("QWidget { background-color: white; color: black; border-radius: 75%; font-family: 'Poppins', sans-serif; border: none; }")


    # this timer calls every 5 sec the get_data_senzors function
    def init_timer_data_senzors(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_data_senzors)
        self.timer.start(10000)

    
    def init_timer_save_data_senzors_into_db(self):
        self.timer_save_data_senzors_into_db = QTimer()
        self.timer_save_data_senzors_into_db.timeout.connect(self.get_data_senzors_to_save_into_db)
        self.timer_save_data_senzors_into_db.start(oneHourInMls)


    def check_test(self):
        logging.info("test merge")


    def check_status(self):
        internet: bool = self.internet_checker.check_internet_connection()

        if(internet):
            url = f"{self.url}/status"

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                status_value = int(data[0]["status"])
    
                if status_value == self.status:
                    logging.info("Same status")

                else:
                    self.status = status_value
                    self.id_status = data[0]["_id"]

                    if self.status == 1:
                        self.button_status = True
                        self.change_status_slider(1)
                    
                    else:
                        self.button_status = False
                        self.change_status_slider(0)

            else:
                logging.info("Error to fetching the heatingstatus endpoint at check_status function")
        
        else:
            logging.info("No data for status, because is no internet")


    # this timer checks the slider status
    def init_timer_checker_status(self):
        self.timer_checker_status.timeout.connect(self.check_status)
        self.timer_checker_status.start()

    def init_timer_test(self):
        self.timer_test.timeout.connect(self.check_test)
        self.timer_test.start()


    def check_treshold(self):
        logging.debug("The function check_treshold is running ...")

        internet: bool = self.internet_checker.check_internet_connection()

        if(internet):
            url = f"{self.url}/treshold"
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                treshold_value = float(data[0]["temperature"])

                # if self.change_treshold is 1, means that the user is making changes with the +/- buttons
                if self.change_treshold == 1:
                    logging.debug("The treshold is changing now")

                
                else:
                    if treshold_value == self.treshlod:
                        logging.info("Same treshold")

                    else:
                        self.treshlod = treshold_value
        
                        self.treshold_label.setText(str(self.treshlod))


            else:
                logging.info("Error to fetching the heatingstemp endpoint at check_treshold function")

        else:
            logging.info("No info for treshold, no internet connection")


    # this timer check the treshold's value
    def init_timer_checker_treshold(self):
        logging.debug("check timer")
        self.timer_checker_treshold.timeout.connect(self.check_treshold)
        self.timer_checker_treshold.start()




if __name__ == '__main__':
    
    window = MainWindow()
    window.fetch_heating_status()
    window.fetch_treshold()
    window.initUI()
    window.show()

    sys.exit(app.exec_())
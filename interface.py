from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from datetime import datetime
from kivy.config import Config

import time 
import re

Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '480')
Config.set('graphics', 'resizable', False)



class CarDashboard(FloatLayout):
    accelerator_pedal = NumericProperty(0)
    soc = NumericProperty(90)
    cell_temperature = NumericProperty(25)
    current_time = StringProperty("")

    def read_spi():
        with open("spi_log.txt", "r") as log_file:
            lines = log_file.readlines()
            if lines:
                latest_line = lines[-1]  
                
                spi_data_int = re.findall(r'\[(\d+(?:,\s*\d+)*)\]', latest_line)
                if spi_data_int:
                    spi_data_int = list(map(int, spi_data_int))  
                global accelerator_pedal
                global soc
                global cell_temperature
                accelerator_pedal = NumericProperty(spi_data_int[0])
                soc = NumericProperty(spi_data_int[1])
                cell_temperature = NumericProperty(spi_data_int[2])
                        
            time.sleep(1) 


    def __init__(self, **kwargs):
        super(CarDashboard, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.read_spi()



class DesignApp(App):
    def build(self):
        return CarDashboard()

if __name__ == '__main__':
    DesignApp().run()

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from datetime import datetime
from kivy.config import Config
from kivy.core.window import Window

import time 
import re

Config.set('graphics', 'resizable', False)

class CarDashboard(FloatLayout):
    accelerator_pedal = NumericProperty(0)
    soc = NumericProperty(90)
    cell_temperature = NumericProperty(25)
    current_time = StringProperty("")

    def __init__(self, **kwargs):
        super(CarDashboard, self).__init__(**kwargs)
        Clock.schedule_interval(self.update_time, 1)

    def update_time(self, dt):
        self.current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class DesignApp(App):
    def build(self):
        Window.size = (Window.system_size[0], Window.system_size[1])
        Window.maximize()
        return CarDashboard()

if __name__ == '__main__':
    DesignApp().run()

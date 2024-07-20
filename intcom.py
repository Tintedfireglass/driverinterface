from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.image import Image
from math import cos, sin, pi
from kivy.core.window import Window
from datetime import datetime
import serial
import threading

class Speedometer(Label):
    value = NumericProperty(0)
    movement = NumericProperty(-180)
    soc = NumericProperty(36)

    def __init__(self, **kwargs):
        super(Speedometer, self).__init__(**kwargs)

    def draw_speedometer(self):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0.7, 1)
            Line(circle=(self.center_x, self.center_y, min(self.width, self.height) / 2 - 1), width=2)
            Color(1, 0.2, 0)
            angle = self.movement * pi / 180
            Line(points=[self.center_x, self.center_y,
                         self.center_x + (min(self.width, self.height) / 2 - 1) * 0.8 * cos(angle),
                         self.center_y + (min(self.width, self.height) / 2 - 1) * 0.8 * sin(angle)],
                 width=2)

            Label(text=str(int(self.value)), pos=(self.center_x - 10, self.center_y - 30), font_size=20)

class BatteryIndicator(FloatLayout):
    soc = NumericProperty(100)
    
    def __init__(self, **kwargs):
        super(BatteryIndicator, self).__init__(**kwargs)
        self.size = (100, 150) 
        self.pos = (50, self.height - 200)  
        self.label = Label(text=str(self.soc) + '%', font_size=20, pos=(self.center_x, self.top - 20))
        self.add_widget(self.label)
        self.update_battery()

    def update_battery(self):
        self.canvas.clear()
        with self.canvas:
            # Cell outline
            Color(0.5, 0.5, 0.5)  
            Rectangle(pos=self.pos, size=(self.width, self.height))

            # Cell positive terminal
            Color(0.5, 0.5, 0.5)
            terminal_height = 20
            terminal_width = 10
            terminal_pos = (self.pos[0] + (self.width - terminal_width) / 2, self.pos[1] + self.height - terminal_height + 10)
            Rectangle(pos=terminal_pos, size=(terminal_width, terminal_height))

            # Cell body
            Color(0.2, 0.2, 0.2)  
            Rectangle(pos=(self.pos[0] + 5, self.pos[1] + 10), size=(self.width - 10, self.height - 30))

            # SOC level
            Color(0, 1, 0)  
            soc_height = (self.height - 30) * (self.soc / 100.0)
            Rectangle(pos=(self.pos[0] + 5, self.pos[1] + 10), size=(self.width - 10, soc_height))

        
        self.label.text = str(self.soc) + '%'
        self.label.pos = (self.center_x - self.label.width / 2, self.top - 25)

    def on_soc(self, instance, value):
        self.update_battery()

class CarDashboard(FloatLayout):
    accelerator_pedal = NumericProperty(0)
    cell_temperature = NumericProperty(0)
    current_time = StringProperty("00:00")

    def __init__(self, **kwargs):
        super(CarDashboard, self).__init__(**kwargs)

        self.speedometer = Speedometer(font_size=80, size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.speedometer)

        # Battery Indicator (top-left)
        self.battery_indicator = BatteryIndicator(size_hint=(None, None), size=(150, 150), pos_hint={"left": 0.1, "top": 0.9})
        self.add_widget(self.battery_indicator)

        # Cell Temperature Label (top-right)
        self.cell_temperature_label = Label(text=str(self.cell_temperature) + '°C', font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"right": 0.95, "top": 0.95}, halign='right', valign='middle')
        self.add_widget(self.cell_temperature_label)

        # Time Label (bottom-left)
        self.time_label = Label(text=self.current_time, font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"left": 0.05, "bottom": 0.05}, halign='left', valign='middle')
        self.add_widget(self.time_label)

        # Replace the OJAS text label with an image
        self.logo_image = Image(source='logo.png', size_hint=(None, None), size=(200, 200), pos_hint={"right": 0.95, "bottom": 0.05})
        self.add_widget(self.logo_image)

        self.dummy_soc = 100  # Initial SOC value
        self.dummy_value = 0  # Initial speed value

        self.serial_port = None
        self.start_UART_thread()
        Clock.schedule_interval(self.update_speedometer, 0.1)
    
    def UARTRead(self):
        try:
            with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as self.serial_port:
                while True:
                    dataa = self.serial_port.readline().decode('utf-8').strip()
                    if dataa:
                        match = dataa.split()
                        if len(match) >= 2:
                            # Update data on main thread
                            self.update_data(match[0], match[1])
        except serial.SerialException as e:
            print(f"Serial Exception: {e}")

    def update_data(self, soc, value):
        # Schedule UI update on the main thread
        Clock.schedule_once(lambda dt: self.update_speedometer(soc, value))
        
    def update_speedometer(self, dt):
        

        self.speedometer.soc = int(self.soc)
        self.speedometer.value = int(self.value)
        maxim = 360
        self.speedometer.movement = -180 - (self.speedometer.value / maxim) * 360  
        self.speedometer.draw_speedometer()

        color_value = max(min((1 - self.speedometer.value / 100) * 2, 1), 0)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.5 + 0.5 * (1 - color_value), 0.5 * color_value, 0)
            Rectangle(pos=self.pos, size=self.size)

        self.battery_indicator.soc = self.speedometer.soc

        self.cell_temperature = 30  
        self.cell_temperature_label.text = str(self.cell_temperature) + '°C'

        self.current_time = self.get_current_time()
        self.time_label.text = self.current_time

    def get_current_time(self):
        now = datetime.now()
        return now.strftime("%H:%M:%S")

    def start_UART_thread(self):
        uart_thread = threading.Thread(target=self.UARTRead)
        uart_thread.daemon = True
        uart_thread.start()

class CarDashboardApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        return CarDashboard()

if __name__ == '__main__':
    CarDashboardApp().run()

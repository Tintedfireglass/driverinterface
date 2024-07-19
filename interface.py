from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from math import cos, sin, pi
from kivy.core.window import Window
from kivy.config import Config
from serial import Serial
import threading

#from comm import uart_read


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
            angle = (self.movement) * pi / 180
            Line(points=[self.center_x, self.center_y,
                         self.center_x + (min(self.width, self.height) / 2 - 1) * 0.8 * cos(angle),
                         self.center_y + (min(self.width, self.height) / 2 - 1) * 0.8 * sin(angle)],
                 width=2)


            #soc label
            Label(text='SOC: ' + str(self.soc) + '%',pos=(self.center_x - 350, self.center_y +200), valign='top', font_size=20)

            # Add text indicating movement
            Label(text=str(int(self.value)), pos=(self.center_x - 10, self.center_y - 30), font_size=20)

           


class CarDashboard(FloatLayout):
    accelerator_pedal = NumericProperty(0)
    cell_temperature = NumericProperty(0)
    current_time = StringProperty("00:00")
    uart_thread.start()

    def __init__(self, **kwargs):
        super(CarDashboard, self).__init__(**kwargs)

        self.speedometer = Speedometer(font_size=80, size_hint=(None, None), size=(400, 400), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self.add_widget(self.speedometer)

        # State of Charge Label (top-left)
        state_of_charge_label = Speedometer(font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"left": 0.3, "top": 0.95}, halign='left', valign='middle')
        self.add_widget(state_of_charge_label)

        # Cell Temperature Label (top-right)
        cell_temperature_label = Label(text=str(self.cell_temperature) + '°C', font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"right": 0.95, "top": 0.95}, halign='right', valign='middle')
        self.add_widget(cell_temperature_label)

        # Time Label (bottom-left)
        time_label = Label(text=self.current_time, font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"left": 0.05, "bottom": 0.05}, halign='left', valign='middle')
        self.add_widget(time_label)

        # OJAS Label (bottom-right)
        ojas_label = Label(text="OJAS", font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"right": 0.95, "bottom": 0.05}, halign='right', valign='middle')
        self.add_widget(ojas_label)

        Clock.schedule_interval(self.update_speedometer, 0.1)

    
    def UARTRead(self):
        while True:
            with Serial('/dev/ttyACM0', 115200) as serial:
                dataa = serial.readline()
                print(dataa)
                match = dataa.split()
                self.arrr = match

    def start_UART_thread(self):
        uart_thread = threading.Thread(target=self.UARTRead)
        uart_thread.daemon = True
        uart_thread.start()

    def update_speedometer(self, dt):
        if hasattr(self, 'arrr') and self.arrr:
            self.speedometer.soc = self.arrr[0]
            self.speedometer.value = int(self.arrr[1])
            if self.speedometer.value < 100:
                self.speedometer.movement -= 1
            else:
                self.speedometer.movement = -180
            self.speedometer.draw_speedometer()

            color_value = max(min((1 - self.speedometer.value / 100) * 2, 1), 0)
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0.5 + 0.5 * (1 - color_value), 0.5 * color_value, 0)
                Rectangle(pos=self.pos, size=self.size)
            

    

        
        

class CarDashboardApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        return CarDashboard()
    


if __name__ == '__main__':
    CarDashboardApp().run()

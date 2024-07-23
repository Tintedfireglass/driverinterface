from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle, PushMatrix, PopMatrix, Rotate
from kivy.uix.image import Image
from math import cos, sin, pi
from kivy.core.window import Window

class Speedometer(FloatLayout):
    value = NumericProperty(0)
    movement = NumericProperty(-180)
    soc = NumericProperty(36)

    def __init__(self, **kwargs):
        super(Speedometer, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 400)
        self.pos_hint = {'center_x': 0.5, 'center_y': 0.5}

        # Add background image
        self.bg_image = Image(source='speedometer.png', size=self.size, pos=self.pos)
        self.add_widget(self.bg_image)

        # Add speedometer label for value display
        self.speed_label = Label(font_size=20, pos=(self.center_x - 10, self.center_y - 30))
        self.add_widget(self.speed_label)

        self.bind(size=self.update_canvas, pos=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(1, 1, 1)
            Rectangle(texture=self.bg_image.texture, size=self.size, pos=self.pos)
        self.draw_speedometer()

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
            self.speed_label.text = str(int(self.value))
            self.speed_label.pos = (self.center_x - 10, self.center_y - 30)

class BatteryIndicator(FloatLayout):
    soc = NumericProperty(100)
    
    def __init__(self, **kwargs):
        super(BatteryIndicator, self).__init__(**kwargs)
        self.size = (100, 150)  # Adjust the size to accommodate text and bar
        self.pos = (50, self.height - 200)  # Adjust the position
        self.label = Label(text=str(self.soc) + '%', font_size=20, pos=(self.center_x, self.top - 20))
        self.add_widget(self.label)
        self.update_battery()

    def update_battery(self):
        self.canvas.clear()
        with self.canvas:
            # Battery outline
            Color(0.5, 0.5, 0.5)  
            Rectangle(pos=self.pos, size=(self.width, self.height))

            # Battery terminal
            Color(0.5, 0.5, 0.5)
            terminal_height = 20
            terminal_width = 10
            terminal_pos = (self.pos[0] + (self.width - terminal_width) / 2, self.pos[1] + self.height - terminal_height + 10)
            Rectangle(pos=terminal_pos, size=(terminal_width, terminal_height))

            # Battery body
            Color(0.2, 0.2, 0.2)  # Dark gray color
            Rectangle(pos=(self.pos[0] + 5, self.pos[1] + 10), size=(self.width - 10, self.height - 30))

            # SOC level
            if self.soc > 50:
                Color(0, 1, 0)  # Green color
            elif self.soc > 20:
                Color(1, 1, 0)  # Yellow color
            else:
                Color(1, 0, 0)  # Red color
            soc_height = (self.height - 30) * (self.soc / 100.0)
            Rectangle(pos=(self.pos[0] + 5, self.pos[1] + 10), size=(self.width - 10, soc_height))

        # Update the text label
        self.label.text = str(self.soc) + '%'
        self.label.pos = (self.center_x - self.label.width / 2, self.top - 25)

    def on_soc(self, instance, value):
        self.update_battery()

class CarDashboard(FloatLayout):
    accelerator_pedal = NumericProperty(0)
    cell_temperature = NumericProperty(0)
    error_message = StringProperty("")

    def __init__(self, **kwargs):
        super(CarDashboard, self).__init__(**kwargs)

        self.speedometer = Speedometer()
        self.add_widget(self.speedometer)

        # Battery Indicator (top-left)
        self.battery_indicator = BatteryIndicator(size_hint=(None, None), size=(150, 150), pos_hint={"left": 0.1, "top": 0.9})
        self.add_widget(self.battery_indicator)

        # Cell Temperature Label (top-right)
        self.cell_temperature_label = Label(text=str(self.cell_temperature) + '°C', font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"right": 0.95, "top": 0.95}, halign='right', valign='middle')
        self.add_widget(self.cell_temperature_label)

        # Error Message Label (bottom-left)
        self.error_message_label = Label(text=self.error_message, font_size=20, size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"left": 0.05, "bottom": 0.05}, halign='left', valign='middle')
        self.add_widget(self.error_message_label)

        # Ojas Image (bottom-right)
        self.logo_image = Image(source='logo.png', size_hint=(None, None), size=(200, 200), pos_hint={"right": 0.95, "bottom": 0.05})
        self.add_widget(self.logo_image)

        self.dummy_soc = 100  # Initial SOC value
        self.dummy_value = 0  # Initial speed value

        Clock.schedule_interval(self.update_speedometer, 0.1)

    def update_speedometer(self, dt):
        # Update dummy data
        self.dummy_soc = max(0, self.dummy_soc - 0.1)  
        self.dummy_value = min(100, self.dummy_value + 0.5)  

        self.speedometer.soc = int(self.dummy_soc)
        self.speedometer.value = int(self.dummy_value)
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

        # Update the error message
        self.error_message = self.get_error_message()
        self.error_message_label.text = 'Error: ' + self.error_message

    def get_error_message(self):
        self.errrr = "E5 Pedal Error!"
        return "       "+self.errrr

class CarDashboardApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        return CarDashboard()

if __name__ == '__main__':
    CarDashboardApp().run()

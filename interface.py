from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import NumericProperty, StringProperty
from kivy.clock import Clock
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.image import Image
from math import cos, sin, pi
from kivy.core.window import Window

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

            # Add text indicating movement
            Label(text=str(int(self.value)), pos=(self.center_x - 10, self.center_y - 30), font_size=20)

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
            # Draw battery outline
            Color(0.5, 0.5, 0.5)  # Gray color
            Rectangle(pos=self.pos, size=(self.width, self.height))

            # Draw battery terminal
            Color(0.5, 0.5, 0.5)
            terminal_height = 20
            terminal_width = 10
            terminal_pos = (self.pos[0] + (self.width - terminal_width) / 2, self.pos[1] + self.height - terminal_height + 10)
            Rectangle(pos=terminal_pos, size=(terminal_width, terminal_height))

            # Draw battery body
            Color(0.2, 0.2, 0.2)  # Dark gray color
            Rectangle(pos=(self.pos[0] + 5, self.pos[1] + 10), size=(self.width - 10, self.height - 30))

            # Draw SOC level
            Color(0, 1, 0)  # Green color
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

        Clock.schedule_interval(self.update_speedometer, 0.1)

    def update_speedometer(self, dt):
        # Update dummy data
        self.dummy_soc = max(0, self.dummy_soc - 0.1)  # Decrement SOC value
        self.dummy_value = min(100, self.dummy_value + 0.5)  # Increment speed value

        self.speedometer.soc = int(self.dummy_soc)
        self.speedometer.value = int(self.dummy_value)
        maxim = 360
        self.speedometer.movement = -180 - (self.speedometer.value / maxim) * 360  # Movement from -180 to 180 degrees
        self.speedometer.draw_speedometer()

        color_value = max(min((1 - self.speedometer.value / 100) * 2, 1), 0)
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.5 + 0.5 * (1 - color_value), 0.5 * color_value, 0)
            Rectangle(pos=self.pos, size=self.size)

        # Update the battery indicator
        self.battery_indicator.soc = self.speedometer.soc

        # Update the cell temperature (dummy value)
        self.cell_temperature = 30  # Constant value for demonstration
        self.cell_temperature_label.text = str(self.cell_temperature) + '°C'

        # Update the current time
        self.current_time = self.get_current_time()
        self.time_label.text = self.current_time

    def get_current_time(self):
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%H:%M:%S")

class CarDashboardApp(App):
    def build(self):
        Window.fullscreen = 'auto'
        return CarDashboard()

if __name__ == '__main__':
    CarDashboardApp().run()

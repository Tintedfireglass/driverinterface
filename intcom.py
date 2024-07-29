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

class Speedometer(FloatLayout):
    value = NumericProperty(0)
    movement = NumericProperty(-180)
    soc = NumericProperty(36)

    def __init__(self, **kwargs):
        super(Speedometer, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (400, 400)
        self.pos_hint = {'center_x': 0.3, 'center_y': 0.5}  # Adjusted for speedometer position

        # Background image
        self.bg_image = Image(source='speedometer.png', size=self.size, pos=self.pos)
        self.add_widget(self.bg_image)

        # Speedometer label for value display
        self.speed_label = Label(font_size=20, color=(1, 1, 1, 1))
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
        self.size_hint = (None, None)
        self.size = (100, 150) 
        self.pos_hint = {'x': 0.05, 'top': 0.95}  
        self.update_battery()
        self.bind(soc=self.update_battery)

    def update_battery(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Battery outline
            Color(0.5, 0.5, 0.5)  
            Rectangle(pos=self.pos, size=self.size)

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
            soc_height = (self.height - 30) * (self.soc / 100.0)
            if self.soc > 50:
                Color(0, 1, 0)  # Green color
            elif self.soc > 20:
                Color(1, 1, 0)  # Yellow color
            else:
                Color(1, 0, 0)  # Red color
            Rectangle(pos=(self.pos[0] + 5, self.pos[1] + 10), size=(self.width - 10, soc_height))

class HorizontalBar(FloatLayout):
    value = NumericProperty(0)
    label_text = StringProperty('')

    def __init__(self, **kwargs):
        super(HorizontalBar, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (300, 50)
        self.bind(value=self.update_canvas)

    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0.5, 0.5, 0.5)
            Rectangle(pos=self.pos, size=self.size)
            Color(0, 1, 0)
            Rectangle(pos=self.pos, size=(self.size[0] * (self.value / 100.0), self.size[1]))

class CarDashboard(FloatLayout):
    accelerator_pedal = NumericProperty(0)
    cell_temperature = NumericProperty(0)
    error_message = StringProperty("")

    def __init__(self, **kwargs):
        super(CarDashboard, self).__init__(**kwargs)

        self.speedometer = Speedometer()
        self.add_widget(self.speedometer)

        # RPM Meter (similar to Speedometer)
        self.rpm_meter = Speedometer()
        self.rpm_meter.pos_hint = {'center_x': 0.7, 'center_y': 0.5}  # Adjusted for RPM meter position
        self.add_widget(self.rpm_meter)

        # Battery Indicator (top-left)
        self.battery_indicator = BatteryIndicator(size_hint=(None, None), size=(150, 150), pos_hint={"x": 0.05, "top": 0.85})
        self.add_widget(self.battery_indicator)

        # Battery SOC Label
        self.battery_soc_label = Label(text="SOC: 100%", font_size=20, color=(1, 1, 1, 1), pos_hint={"x": -0.4225, "top": 1.4})
        self.add_widget(self.battery_soc_label)

        # Cell Temperature Label (top-right)
        self.cell_temperature_label = Label(text=str(self.cell_temperature) + '°C', font_size=20, color=(1, 1, 1, 1),
                                            size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"right": 0.95, "top": 0.95},
                                            halign='right', valign='middle')
        self.add_widget(self.cell_temperature_label)

        # Error Message Label (bottom-left)
        self.error_message_label = Label(text=self.error_message, font_size=20, color=(1, 1, 1, 1),
                                         size_hint=(None, None), size=(self.width / 2, 50), pos_hint={"left": 0.05, "bottom": 0.05},
                                         halign='left', valign='middle')
        self.add_widget(self.error_message_label)

        # Ojas Image (bottom-right)
        self.logo_image = Image(source='logo.png', size_hint=(None, None), size=(200, 200), pos_hint={"right": 0.95, "bottom": 0.05})
        self.add_widget(self.logo_image)

        # Power and Current Bars
        self.power_bar = HorizontalBar(pos_hint={"center_x": 0.4, "top": 0.85}, label_text='Power: ')
        self.current_bar = HorizontalBar(pos_hint={"center_x": 0.6, "top": 0.85}, label_text='Current: ')
        self.add_widget(self.power_bar)
        self.add_widget(self.current_bar)

        # Power Label
        self.power_label = Label(text="Power: 0", font_size=20, color=(1, 1, 1, 1), pos_hint={"center_x": 0.4, "top": 1.325})
        self.add_widget(self.power_label)

        # Current Label
        self.current_label = Label(text="Current: 0", font_size=20, color=(1, 1, 1, 1), pos_hint={"center_x": 0.6, "top": 1.325})
        self.add_widget(self.current_label)

        self.serial_port = None
        self.start_UART_thread()

        Clock.schedule_interval(self.update_dashboard, 0.1)

    def UARTRead(self):
        try:
            with serial.Serial('/dev/ttyACM0', 115200, timeout=1) as self.serial_port:
                while True:
                    data = self.serial_port.readline().decode('utf-8').strip()
                    if data:
                        values = data.split(',')
                        if len(values) >= 7:
                            self.update_data(values)
        except serial.SerialException as e:
            print(f"Error opening or communicating over serial port: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def start_UART_thread(self):
        uart_thread = threading.Thread(target=self.UARTRead)
        uart_thread.daemon = True
        uart_thread.start()

    def update_data(self, values):
        try:
            speed, rpm, power, current, soc, cell_temp, error = map(float, values[:6]) + [values[6]]
            self.speedometer.value = speed
            self.speedometer.movement = -180 + (speed / 300 * 180)
            self.rpm_meter.value = rpm
            self.rpm_meter.movement = -180 + (rpm / 10000 * 180)
            self.power_bar.value = power
            self.power_label.text = f"Power: {int(power)}"
            self.current_bar.value = current
            self.current_label.text = f"Current: {int(current)}"
            self.battery_indicator.soc = soc
            self.battery_soc_label.text = f"SOC: {int(soc)}%"
            self.cell_temperature = cell_temp
            self.cell_temperature_label.text = f"{int(cell_temp)}°C"
            self.error_message = error
            self.error_message_label.text = error
        except ValueError:
            print(f"Invalid value received: {values}")
        except Exception as e:
            print(f"Unexpected error: {e}")

    def update_dashboard(self, dt):
        self.dummy_soc -= 0.1
        if self.dummy_soc < 0:
            self.dummy_soc = 100

        self.dummy_value += 1
        if self.dummy_value > 300:
            self.dummy_value = 0

        self.dummy_rpm += 100
        if self.dummy_rpm > 10000:
            self.dummy_rpm = 0

        self.dummy_power = (self.dummy_value / 300) * 100
        self.dummy_current = (self.dummy_value / 300) * 100

        # self.speedometer.value = self.dummy_value
        # self.speedometer.movement = -180 + (self.dummy_value / 300 * 180)
        # self.rpm_meter.value = self.dummy_rpm
        # self.rpm_meter.movement = -180 + (self.dummy_rpm / 10000 * 180)
        # self.power_bar.value = self.dummy_power
        # self.power_label.text = f"Power: {int(self.dummy_power)}"
        # self.current_bar.value = self.dummy_current
        # self.current_label.text = f"Current: {int(self.dummy_current)}"
        # self.battery_indicator.soc = self.dummy_soc
        # self.battery_soc_label.text = f"SOC: {int(self.dummy_soc)}%"
        # self.cell_temperature_label.text = f"{int(self.cell_temperature)}°C"
        # self.error_message_label.text = self.error_message

class CarDashboardApp(App):
    def build(self):
        return CarDashboard()

if __name__ == '__main__':
    CarDashboardApp().run()

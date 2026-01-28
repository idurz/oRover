class Radar:
    def __init__(self, gpio, pin: int):
        self.gpio = gpio
        self.pin = pin
        gpio.setup(pin, gpio.OUT)

    def on(self):
        self.gpio.output(self.pin, self.gpio.HIGH)

    def off(self):
        self.gpio.output(self.pin, self.gpio.LOW)
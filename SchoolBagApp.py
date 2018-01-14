from kivy.app import App
from kivy.uix.button import Button


class SchoolBagApp(App):
    def build(self):
        return Button(text='Hello World')


SchoolBagApp().run()

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup


class Informer:
    @staticmethod
    def show_popup(title, text):
        Informer.__show_ok_pop(title, Label(text=text))

    @staticmethod
    def show_smiley_popup(title):
        Informer.__show_ok_pop(title, Image(source='icons/smiley.png'))

    @staticmethod
    def show_ok_pop(title, widget):
        button = Button(text='OK')
        box = BoxLayout(orientation='vertical')
        box.add_widget(widget)
        box.add_widget(button)
        popup = Popup(
            title=title, content=box,
            size_hint=(None, None), size=(600, 300))
        button.bind(on_press=popup.dismiss)
        popup.open()
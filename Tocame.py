from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.clock import Clock
import random
import json
import os
import pygame

TOUCH_ME = "puntajes.json"
try:
    pygame.mixer.init()
    pygame.mixer.music.load("mustoc.mp3")
    pygame.mixer.music.set_volume(1.0)  # volumen al 100%
    pygame.mixer.music.play(-1)  # Repite el sonido indefinidamente  
except Exception as e:
    print("Error cargando sonido:", e)
    
class PantallaInicio(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.label = Label(text="Ingresa tu nombre para comenzar:", font_size=25)
        self.input_nombre = TextInput(multiline=False, font_size=25, size_hint=(1, 0.2))
        boton_jugar = Button(text="INICIAR JUEGO", font_size=30, background_color=(1, 0.3, 0.3, 1), size_hint=(1, 0.3))
        boton_jugar.bind(on_press=self.ir_a_juego)

        layout.add_widget(self.label)
        layout.add_widget(self.input_nombre)
        layout.add_widget(boton_jugar)
        self.add_widget(layout)

    def ir_a_juego(self, instance):
        nombre = self.input_nombre.text.strip()
        if nombre:
            juego_screen = self.manager.get_screen("juego")
            juego_screen.nombre_jugador = nombre
            juego_screen.reiniciar_juego()
            self.manager.current = "juego"

class PantallaJuego(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.nombre_jugador = ""
        self.puntuacion = 0
        self.tiempo_restante = 30
        self.velocidad_boton = 0.7
        self.boton_opciones_mostradas = False

        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=20)
        self.label_puntuacion = Label(text="", font_size=30)
        self.label_tiempo = Label(text="", font_size=30)

        self.boton_juego = Button(
            text="¡TÓCAME!",
            size_hint=(None, None),
            size=(200, 200),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            font_size=25,
            background_color=(0.2, 0.8, 0.3, 1)
        )
        self.boton_juego.bind(on_press=self.sumar_punto)

        self.layout.add_widget(self.label_tiempo)
        self.layout.add_widget(self.label_puntuacion)
        self.layout.add_widget(self.boton_juego)
        self.add_widget(self.layout)

        # Solo se programan una vez
        Clock.schedule_interval(self.actualizar_tiempo, 1)
        Clock.schedule_interval(self.mover_boton, self.velocidad_boton)

    def reiniciar_juego(self):
        self.puntuacion = 0
        self.tiempo_restante = 30
        self.boton_opciones_mostradas = False

        self.label_puntuacion.text = f"Puntos: {self.puntuacion}"
        self.label_tiempo.text = f"Tiempo: {self.tiempo_restante}s"
        self.boton_juego.disabled = False

        # Limpieza de botones extra al reiniciar
        for widget in self.children[:]:
            if isinstance(widget, BoxLayout) and widget != self.layout:
                self.remove_widget(widget)

    def sumar_punto(self, instance):
        self.puntuacion += 1
        self.label_puntuacion.text = f"Puntos: {self.puntuacion}"

    def actualizar_tiempo(self, dt):
        if self.tiempo_restante > 0:
            self.tiempo_restante -= 1
            self.label_tiempo.text = f"Tiempo: {self.tiempo_restante}s"

        if self.tiempo_restante <= 0 and not self.boton_opciones_mostradas:
            self.boton_juego.disabled = True
            self.label_tiempo.text = "¡TIEMPO AGOTADO!"
            self.guardar_puntaje(self.nombre_jugador)
            self.mostrar_opciones_finales()
            self.boton_opciones_mostradas = True

    def mover_boton(self, dt):
        if self.boton_juego.disabled:
            return
        max_x = Window.width - self.boton_juego.width
        max_y = Window.height - self.boton_juego.height
        new_x = random.randint(0, int(max_x))
        new_y = random.randint(0, int(max_y))
        self.boton_juego.pos = (new_x, new_y)

    def mostrar_opciones_finales(self):
        layout_opciones = BoxLayout(
            orientation="horizontal",
            size_hint=(1, 0.2),
            spacing=20,
            padding=[50, 10]
        )

        boton_reiniciar = Button(text="JUGAR DE NUEVO", background_color=(0.1, 0.5, 0.8, 1), font_size=20)
        boton_reiniciar.bind(on_press=lambda x: self.reiniciar_juego())

        boton_top = Button(text="VER TOP", background_color=(1, 0.84, 0, 1), font_size=20)
        boton_top.bind(on_press=self.ver_top)

        boton_salir = Button(text="SALIR", background_color=(0.8, 0.2, 0.2, 1), font_size=20)
        boton_salir.bind(on_press=self.salir)

        layout_opciones.add_widget(boton_reiniciar)
        layout_opciones.add_widget(boton_top)
        layout_opciones.add_widget(boton_salir)
        self.add_widget(layout_opciones)

    def guardar_puntaje(self, nombre):
        puntajes = []
        if os.path.exists(TOUCH_ME):
            try:
                with open(TOUCH_ME, "r") as f:
                    puntajes = json.load(f)
            except json.JSONDecodeError:
                puntajes = []

        puntajes.append({"nombre": nombre, "puntos": self.puntuacion})
        puntajes = sorted(puntajes, key=lambda x: x["puntos"], reverse=True)

        with open(TOUCH_ME, "w") as f:
            json.dump(puntajes, f)

    def ver_top(self, instance):
        self.manager.get_screen("top").pantalla_origen = "juego"
        self.manager.get_screen("top").mostrar_top()
        self.manager.current = "top"

    def salir(self, instance):
        App.get_running_app().stop()

class PantallaTop(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pantalla_origen = "inicio"
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.label_titulo = Label(text="TOP 5 PUNTAJES", font_size=30)
        self.labels_puntajes = [Label(font_size=25) for _ in range(5)]

        self.boton_volver_inicio = Button(text="Volver al inicio",background_color=(0.4, 1, 0.8, 1), font_size=20) #
        self.boton_volver_inicio.bind(on_press=self.volver_inicio)

        self.boton_ir_tiempo_agotado = Button(text="Ir a pantalla de juego finalizado", font_size=20)
        self.boton_ir_tiempo_agotado.bind(on_press=self.ir_a_tiempo_agotado)

        self.layout.add_widget(self.label_titulo)
        for lbl in self.labels_puntajes:
            self.layout.add_widget(lbl)
        self.layout.add_widget(self.boton_ir_tiempo_agotado)
        self.layout.add_widget(self.boton_volver_inicio)
        self.add_widget(self.layout)

    def mostrar_top(self):
        if os.path.exists(TOUCH_ME):
            with open(TOUCH_ME, "r") as f:
                puntajes = json.load(f)

            top = sorted(puntajes, key=lambda x: x["puntos"], reverse=True)[:5]

            for i in range(5):
                if i < len(top):
                    entry = top[i]
                    self.labels_puntajes[i].text = f"{i+1}. {entry['nombre']} - {entry['puntos']} puntos"
                else:
                    self.labels_puntajes[i].text = ""
        else:
            for label in self.labels_puntajes:
                label.text = "Sin datos aún."

    def volver_inicio(self, instance):
        self.manager.current = "inicio"

    def ir_a_tiempo_agotado(self, instance):
        self.manager.current = "juego"
        juego = self.manager.get_screen("juego")
        juego.boton_juego.disabled = True
        juego.label_tiempo.text = "¡TIEMPO AGOTADO!"
        if not juego.boton_opciones_mostradas:
            juego.mostrar_opciones_finales()
            juego.boton_opciones_mostradas = True

class JuegoApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(PantallaInicio(name="inicio"))
        sm.add_widget(PantallaJuego(name="juego"))
        sm.add_widget(PantallaTop(name="top"))
        return sm

if __name__ == "__main__":
    JuegoApp().run()
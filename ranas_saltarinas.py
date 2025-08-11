import tkinter as tk
import time
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class JuegoRanas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ranas Saltarinas")
        self.geometry("800x350")
        self.resizable(False, False)

        # --- Cargar imagen externa ---
        try:
            image_path = resource_path(os.path.join('image', 'ranas.png'))
            self.imagen_rana_datos = tk.PhotoImage(file=image_path)
        except tk.TclError:
            self.imagen_rana_datos = None
            print(f"Advertencia: No se pudo cargar la imagen en {image_path}")

        # --- Configuración del Juego ---
        self.estado_inicial = ['G', 'G', 'G', '_', 'B', 'B', 'B']
        self.estado_ganador = ['B', 'B', 'B', '_', 'G', 'G', 'G']

        # --- Contenedores de Pantallas ---
        self.frame_inicio = tk.Frame(self)
        self.frame_juego = tk.Frame(self)

        self.crear_pantalla_inicio()
        self.crear_pantalla_juego()

        self.mostrar_pantalla_inicio()

    def mostrar_pantalla_inicio(self):
        if hasattr(self, 'temporizador_activo') and self.temporizador_activo:
            self.temporizador_activo = False
        self.frame_juego.pack_forget()
        self.frame_inicio.pack(expand=True, fill=tk.BOTH)

    def iniciar_juego(self):
        self.frame_inicio.pack_forget()
        self.frame_juego.pack(expand=True, fill=tk.BOTH)
        self.reiniciar_juego()

    def crear_pantalla_inicio(self):
        color_fondo = '#90EE90'
        self.frame_inicio.config(bg=color_fondo)

        titulo = tk.Label(self.frame_inicio, text="Ranas Saltarinas", font=("Arial", 40, "bold"), bg=color_fondo, fg='#005A00')
        titulo.pack(pady=(50, 10))

        descripcion = tk.Label(self.frame_inicio, text="El objetivo es mover todas las ranas verdes a la derecha y las marrones a la izquierda.", font=("Arial", 12), bg=color_fondo)
        descripcion.pack(pady=10)

        boton_inicio = tk.Button(self.frame_inicio, text="Iniciar Juego", font=("Arial", 20), command=self.iniciar_juego)
        boton_inicio.pack(pady=20)

        if self.imagen_rana_datos:
            img_label = tk.Label(self.frame_inicio, image=self.imagen_rana_datos, bg=color_fondo)
            img_label.place(relx=1.0, rely=1.0, anchor='se', x=-10, y=-10)

    def crear_pantalla_juego(self):
        color_fondo_juego = 'lightblue'
        self.frame_juego.config(bg=color_fondo_juego)
        control_frame = tk.Frame(self.frame_juego, bg=color_fondo_juego)
        control_frame.pack(pady=5)

        self.movimientos_label = tk.Label(control_frame, text="Movimientos: 0", font=("Arial", 14), bg=color_fondo_juego)
        self.movimientos_label.pack(side=tk.LEFT, padx=10)

        self.tiempo_label = tk.Label(control_frame, text="Tiempo: 0s", font=("Arial", 14), bg=color_fondo_juego)
        self.tiempo_label.pack(side=tk.LEFT, padx=10)

        self.boton_reinicio = tk.Button(control_frame, text="Reiniciar", font=("Arial", 12), command=self.reiniciar_juego)
        self.boton_reinicio.pack(side=tk.LEFT, padx=10)
        
        self.boton_menu = tk.Button(control_frame, text="Menú Principal", font=("Arial", 12), command=self.mostrar_pantalla_inicio)
        self.boton_menu.pack(side=tk.LEFT, padx=10)

        self.canvas = tk.Canvas(self.frame_juego, width=800, height=200, bg=color_fondo_juego, highlightthickness=0)
        self.canvas.pack()

        self.mensaje_final_label = tk.Label(self.frame_juego, text="", font=("Arial", 16, "bold"), bg=color_fondo_juego)
        self.mensaje_final_label.pack(pady=5)

    def reiniciar_juego(self):
        self.estado_actual = list(self.estado_inicial)
        self.posicion_vacia = self.estado_actual.index('_')
        self.movimientos = 0
        self.tiempo_inicio = None
        self.temporizador_activo = False
        self.movimientos_label.config(text="Movimientos: 0")
        self.tiempo_label.config(text="Tiempo: 0s")
        self.mensaje_final_label.config(text="")
        self.dibujar_tablero()

    def dibujar_tablero(self):
        self.canvas.delete("all")
        for i in range(len(self.estado_actual)):
            x0, y0 = i * 110 + 40, 75
            x1, y1 = x0 + 100, 125
            self.canvas.create_oval(x0, y0, x1, y1, fill='darkgreen', outline='black')
        for i, tipo_rana in enumerate(self.estado_actual):
            if tipo_rana != '_':
                x_centro, y_centro = i * 110 + 90, 100
                color = 'green' if tipo_rana == 'G' else '#8B4513'
                rana_id = self.canvas.create_oval(x_centro-40, y_centro-40, x_centro+40, y_centro+40, fill=color, outline='black')
                self.canvas.tag_bind(rana_id, "<Button-1>", lambda event, pos=i: self.click_rana(pos))

    def click_rana(self, posicion):
        if self.mensaje_final_label.cget("text") != "": return
        if not self.temporizador_activo:
            self.tiempo_inicio = time.time()
            self.temporizador_activo = True
            self.actualizar_temporizador()
        
        if self._es_movimiento_valido(posicion):
            self.movimientos += 1
            self.movimientos_label.config(text=f"Movimientos: {self.movimientos}")
            self.estado_actual[self.posicion_vacia], self.estado_actual[posicion] = self.estado_actual[posicion], self.estado_actual[self.posicion_vacia]
            self.posicion_vacia = posicion
            self.dibujar_tablero()
            self.verificar_estado_juego()

    def _es_movimiento_valido(self, pos, estado=None):
        if estado is None:
            estado = self.estado_actual
        
        posicion_vacia = estado.index('_')
        tipo_rana = estado[pos]
        if tipo_rana == '_': return False

        if tipo_rana == 'G':
            if pos + 1 == posicion_vacia: return True
            if pos + 2 == posicion_vacia and estado[pos + 1] == 'B': return True
        elif tipo_rana == 'B':
            if pos - 1 == posicion_vacia: return True
            if pos - 2 == posicion_vacia and estado[pos - 1] == 'G': return True
        return False

    def actualizar_temporizador(self):
        if self.temporizador_activo:
            tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
            self.tiempo_label.config(text=f"Tiempo: {tiempo_transcurrido}s")
            self.after(1000, self.actualizar_temporizador)

    def verificar_estado_juego(self):
        if self.estado_actual == self.estado_ganador:
            self.temporizador_activo = False
            tiempo_final = int(time.time() - self.tiempo_inicio)
            mensaje = f"¡Felicidades! Ganaste en {self.movimientos} movimientos y {tiempo_final}s"
            self.mensaje_final_label.config(text=mensaje, fg="blue")
            return

        # Verificar si hay movimientos posibles
        for i in range(len(self.estado_actual)):
            if self._es_movimiento_valido(i):
                return # Si se encuentra al menos un movimiento, el juego continúa
        
        # Si el bucle termina, no hay movimientos y no se ha ganado
        self.temporizador_activo = False
        self.mensaje_final_label.config(text="¡Te has quedado sin movimientos! Inténtalo de nuevo.", fg="red")

if __name__ == "__main__":
    juego = JuegoRanas()
    juego.mainloop()
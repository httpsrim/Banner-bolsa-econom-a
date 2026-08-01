import tkinter as tk
import yfinance as yf
import threading
import time

# Configuración de valores (Bolsa española usa sufijo .MC)
TICKERS = [
    # --- ÍNDICES MUNDIALES ---
    "^IBEX", "^GSPC", 
    # --- TECNOLOGÍA GLOBAL ---
    "AAPL", "MSFT", "NVDA", "TSLA", "AMZN", "GOOGL", "META", "NFLX",
    # --- GRANDES MARCAS INTERNACIONALES ---
    "KO", "MCD", "NKE", "DIS",
    # --- BOLSA ESPAÑOLA (IBEX 35) ---
    "SAN.MC", "BBVA.MC", "CABK.MC", "ITX.MC", "IBE.MC", "TEF.MC", 
    "REP.MC", "AENA.MC", "FER.MC", "AMS.MC", "CLNX.MC", "IND.MC"
]

def obtener_datos():
    resultados = []
    for t in TICKERS:
        try:
            ticker = yf.Ticker(t)
            datos = ticker.history(period="2d")
            
            precio_actual = datos['Close'].iloc[-1]
            precio_anterior = datos['Close'].iloc[-2]
            variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
            
            simbolo = t.replace(".MC", "")
            
            if t.startswith("^"):
                moneda = " pts"
            elif t.endswith(".MC"):
                moneda = "€" 
            else:
                moneda = "$"
            
            if variacion > 0.005:
                color = "#00FF00"  # Verde
                flecha = "▲"
            elif variacion < -0.005:
                color = "#FF0000"  # Rojo
                flecha = "▼"
            else:
                color = "#ffffff"  # Blanco
                flecha = "→"

            texto_cinta = f"{simbolo}: {precio_actual:.2f}{moneda} ({variacion:+.2f}%) {flecha}"

            resultados.append({
                "simbolo": simbolo,
                "precio": f"{precio_actual:.2f}{moneda}",
                "variacion": f"{variacion:+.2f}% {flecha}",
                "texto": texto_cinta,
                "color": color
            })
        except Exception:
            simbolo = t.replace(".MC", "")
            resultados.append({
                "simbolo": simbolo,
                "precio": "N/D",
                "variacion": "N/D",
                "texto": f"{simbolo}: Datos no disponibles",
                "color": "#008cff"
            })
            
    return resultados

# Configurar la ventana gráfica (Pantalla Completa)
root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()

root.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")
root.configure(bg="black")

# Variables globales para control de vista
canvas = None
frame_tabla = None
elementos_canvas = []
timer_movimiento = None
timer_cambio_vista = None
datos_iniciales = obtener_datos()

# -------------------------------------------------------------
# LÓGICA DE ACTUALIZACIÓN EN SEGUNDO PLANO
# -------------------------------------------------------------
def aplicar_actualizaciones(nuevos_datos):
    global datos_iniciales
    datos_iniciales = nuevos_datos
    if canvas:
        for i, dato in enumerate(nuevos_datos):
            if i < len(elementos_canvas):
                canvas.itemconfig(elementos_canvas[i], text=dato["texto"], fill=dato["color"])

def actualizar_en_segundo_plano():
    while True:
        time.sleep(300)  # Cada 5 minutos busca datos nuevos
        try:
            nuevo_texto = obtener_datos()
            root.after(0, aplicar_actualizaciones, nuevo_texto)
        except Exception:
            pass

# -------------------------------------------------------------
# VISTA 1: CINTA EN MOVIMIENTO (DURACIÓN: 60 SEGUNDOS)
# -------------------------------------------------------------
def desplazar_texto():
    global timer_movimiento
    if canvas:
        for id_txt in elementos_canvas:
            canvas.move(id_txt, -12, 0)
        
        for id_txt in elementos_canvas:
            bbox = canvas.bbox(id_txt)
            if bbox and bbox[2] < 0: 
                max_x = max(canvas.bbox(i)[2] for i in elementos_canvas)
                nuevo_x = max(max_x, ancho_pantalla) + 80
                canvas.coords(id_txt, nuevo_x, alto_pantalla // 2)

        timer_movimiento = root.after(20, desplazar_texto)

def iniciar_cinta():
    global canvas, elementos_canvas, frame_tabla
    
    # Si venimos de la vista de lista, destruimos su contenedor
    if frame_tabla:
        frame_tabla.destroy()
        frame_tabla = None

    canvas = tk.Canvas(root, bg="black", highlightthickness=0, height=alto_pantalla)
    canvas.pack(fill="both", expand=True)

    elementos_canvas = []
    pos_x = ancho_pantalla

    for dato in datos_iniciales:
        id_txt = canvas.create_text(
            pos_x, 
            alto_pantalla // 2, 
            text=dato["texto"], 
            font=("Consolas", 80, "bold"), 
            fill=dato["color"], 
            anchor="w"
        )
        elementos_canvas.append(id_txt)

        bbox = canvas.bbox(id_txt)
        pos_x = bbox[2] + 80

    desplazar_texto()

    # Programar cambio a la vista de lista a los 60 segundos (60,000 ms)
    root.after(60000, mostrar_lista_completa)

# -------------------------------------------------------------
# VISTA 2: LISTA GIGANTE A PANTALLA COMPLETA (DURACIÓN: 30 SEGUNDOS)
# -------------------------------------------------------------
def mostrar_lista_completa():
    global canvas, timer_movimiento, frame_tabla
    
    # Detener animación y destruir Canvas
    if timer_movimiento:
        root.after_cancel(timer_movimiento)
    if canvas:
        canvas.destroy()
        canvas = None

    frame_tabla = tk.Frame(root, bg="black")
    frame_tabla.pack(expand=True, fill="both")

    lbl_titulo = tk.Label(
        frame_tabla, 
        text="RESUMEN DEL MERCADO", 
        font=("Consolas", 42, "bold"), 
        fg="white", 
        bg="black"
    )
    lbl_titulo.pack(pady=(30, 10))

    grid_container = tk.Frame(frame_tabla, bg="black")
    grid_container.pack(expand=True, fill="both", padx=40, pady=20)

    # Configurar distribución uniforme de 2 bloques
    for col in range(8):
        grid_container.grid_columnconfigure(col, weight=1)

    headers = ["SÍMBOLO", "PRECIO", "VARIACIÓN"]
    num_columnas_pantalla = 2

    col_offset = 0
    for _ in range(num_columnas_pantalla):
        for idx, h in enumerate(headers):
            lbl = tk.Label(
                grid_container, 
                text=h, 
                font=("Consolas", 22, "bold"), 
                fg="#888888", 
                bg="black", 
                anchor="center"
            )
            lbl.grid(row=0, column=col_offset + idx, sticky="nsew", pady=10)
        col_offset += 4

    mitad = (len(datos_iniciales) + 1) // 2

    for row in range(1, mitad + 1):
        grid_container.grid_rowconfigure(row, weight=1)

    for i, dato in enumerate(datos_iniciales):
        bloque_col = 0 if i < mitad else 4
        fila = (i % mitad) + 1

        tk.Label(
            grid_container, 
            text=dato["simbolo"], 
            font=("Consolas", 26, "bold"), 
            fg="white", 
            bg="black", 
            anchor="center"
        ).grid(row=fila, column=bloque_col, sticky="nsew", padx=5, pady=2)
        
        tk.Label(
            grid_container, 
            text=dato["precio"], 
            font=("Consolas", 26), 
            fg="white", 
            bg="black", 
            anchor="center"
        ).grid(row=fila, column=bloque_col + 1, sticky="nsew", padx=5, pady=2)
        
        tk.Label(
            grid_container, 
            text=dato["variacion"], 
            font=("Consolas", 26, "bold"), 
            fg=dato["color"], 
            bg="black", 
            anchor="center"
        ).grid(row=fila, column=bloque_col + 2, sticky="nsew", padx=5, pady=2)

    # Programar el reinicio de la cinta tras 30 segundos (30,000 ms)
    root.after(30000, iniciar_cinta)

# -------------------------------------------------------------
# INICIALIZACIÓN
# -------------------------------------------------------------
hilo_actualizacion = threading.Thread(target=actualizar_en_segundo_plano, daemon=True)
hilo_actualizacion.start()

# Iniciar el primer ciclo
iniciar_cinta()

root.bind("<Escape>", lambda e: root.destroy())

root.after(120000, root.destroy)  
root.mainloop()
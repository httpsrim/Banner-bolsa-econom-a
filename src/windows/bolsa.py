import tkinter as tk
import yfinance as yf
import threading
import time

# Configuración de valores (Bolsa española, Índices y Tech de EE.UU.)
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
            
            # Selector inteligente de moneda/unidad para Windows
            if t.startswith("^"):
                moneda = " pts"
            elif t.endswith(".MC"):
                moneda = "€" 
            else:
                moneda = "$"
            
            # Lógica de colores según la variación
            if variacion > 0.005:
                color = "#00FF00"  # Verde
                texto = f"{simbolo}: {precio_actual:.2f}{moneda} (+{variacion:.2f}%) ▲"
            elif variacion < -0.005:
                color = "#FF0000"  # Rojo
                texto = f"{simbolo}: {precio_actual:.2f}{moneda} ({variacion:.2f}%) ▼"
            else:
                color = "#ffffff"  # Blanco
                texto = f"{simbolo}: {precio_actual:.2f}{moneda} ({variacion:.2f}%) →"
            resultados.append({"texto": texto, "color": color})
        except Exception:
            simbolo = t.replace(".MC", "")
            resultados.append({"texto": f"{simbolo}: Datos no disponibles", "color": "#008cff"})
            
    return resultados

# Configurar la ventana gráfica (Pantalla Completa Nativa en Windows)
root = tk.Tk()
root.attributes("-fullscreen", True) # Modo pantalla completa absoluto en Windows
root.attributes("-topmost", True)   # Siempre visible por encima de todo

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()
root.configure(bg="black")

# Preparar el lienzo (Canvas)
canvas = tk.Canvas(root, bg="black", highlightthickness=0, height=alto_pantalla)
canvas.pack(fill="both", expand=True)

elementos_canvas = []
datos_iniciales = obtener_datos()

# Empezamos a dibujar en el borde derecho
pos_x = ancho_pantalla

for dato in datos_iniciales:
    id_txt = canvas.create_text(pos_x, alto_pantalla // 2, text=dato["texto"], 
                              font=("Consolas", 200, "bold"), fill=dato["color"], anchor="w")
    elementos_canvas.append(id_txt)

    bbox = canvas.bbox(id_txt)
    pos_x = bbox[2] + 50  # Espacio de 50 píxeles entre acciones

# Función de desplazamiento continuo
def desplazar_texto():
    for id_txt in elementos_canvas:
        canvas.move(id_txt, -5, 0)
    
    for id_txt in elementos_canvas:
        bbox = canvas.bbox(id_txt)
        if bbox and bbox[2] < 0: 
            max_x = max(canvas.bbox(i)[2] for i in elementos_canvas)
            nuevo_x = max(max_x, ancho_pantalla) + 50  
            canvas.coords(id_txt, nuevo_x, alto_pantalla // 2)

    root.after(20, desplazar_texto)

# Aplicar las actualizaciones en la interfaz
def aplicar_actualizaciones(nuevos_datos):
    for i, dato in enumerate(nuevos_datos):
        if i < len(elementos_canvas):
            canvas.itemconfig(elementos_canvas[i], text=dato["texto"], fill=dato["color"])

# Hilo de actualización cada 5 minutos
def actualizar_en_segundo_plano():
    while True:
        time.sleep(300) 
        try:
            nuevo_texto = obtener_datos()
            # Corregido: Ahora apunta correctamente a aplicar_actualizaciones
            root.after(0, aplicar_actualizaciones, nuevo_texto)
        except Exception:
            pass 

# Iniciar el hilo
hilo_actualizacion = threading.Thread(target=actualizar_en_segundo_plano, daemon=True)
hilo_actualizacion.start()

desplazar_texto()

# Cierra el programa presionando la tecla Escape
root.bind("<Escape>", lambda e: root.destroy())

# SEGURIDAD WINDOWS: Se cierra solo al minuto para hacer pruebas sin quedarte atrapado. 
# (Quita la línea de abajo cuando verifiques que te funciona bien).
root.after(60000, root.destroy) 

root.mainloop()
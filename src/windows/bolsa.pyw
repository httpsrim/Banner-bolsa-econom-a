import sys
import subprocess

# =========================================================================
# Auto-instalador inteligente para entornos de Windows
# =========================================================================
try:
    import yfinance as yf
except ModuleNotFoundError:
    # Si el Python que ejecuta este archivo no tiene yfinance, se lo instala a sí mismo
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yfinance"])
    import yfinance as yf

import tkinter as tk
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
            
            if t.startswith("^"):
                moneda = " pts"
            elif t.endswith(".MC"):
                moneda = "€" 
            else:
                moneda = "$"
            
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

# --- CONFIGURAR VENTANA GRÁFICA INTERFAZ ---
root = tk.Tk()
root.attributes("-fullscreen", True) 
root.attributes("-topmost", True)   
root.configure(bg="black")

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()

canvas = tk.Canvas(root, bg="black", highlightthickness=0, height=alto_pantalla)
canvas.pack(fill="both", expand=True)

elementos_canvas = []
animacion_lista = False

def inicializar_cinta(datos_iniciales):
    global animacion_lista
    
    pos_x = ancho_pantalla
    for dato in datos_iniciales:
        id_txt = canvas.create_text(pos_x, alto_pantalla // 2, text=dato["texto"], 
                                  font=("Consolas", 200, "bold"), fill=dato["color"], anchor="w")
        elementos_canvas.append(id_txt)

        root.update_idletasks()
        bbox = canvas.bbox(id_txt)
        
        if bbox:
            pos_x = bbox[2] + 50  
        else:
            pos_x += 2000 

    animacion_lista = True
    desplazar_texto()

def desplazar_texto():
    if not animacion_lista:
        return
        
    for id_txt in elementos_canvas:
        canvas.move(id_txt, -20, 0)
    
    for id_txt in elementos_canvas:
        bbox = canvas.bbox(id_txt)
        if bbox and bbox[2] < 0: 
            max_x = max(canvas.bbox(i)[2] for i in elementos_canvas if canvas.bbox(i))
            nuevo_x = max(max_x, ancho_pantalla) + 50  
            canvas.coords(id_txt, nuevo_x, alto_pantalla // 2)

    root.after(20, desplazar_texto)

def aplicar_actualizaciones(nuevos_datos):
    for i, dato in enumerate(nuevos_datos):
        if i < len(elementos_canvas):
            canvas.itemconfig(elementos_canvas[i], text=dato["texto"], fill=dato["color"])

def ejecucion_segundo_plano():
    datos = obtener_datos()
    root.after(0, inicializar_cinta, datos)
    
    while True:
        time.sleep(300) 
        try:
            nuevo_texto = obtener_datos()
            root.after(0, aplicar_actualizaciones, nuevo_texto)
        except Exception:
            pass 

hilo_actualizacion = threading.Thread(target=ejecucion_segundo_plano, daemon=True)
hilo_actualizacion.start()

# Cierra el programa presionando la tecla Escape
root.bind("<Escape>", lambda e: root.destroy())

#  Se cerrará solo a los 60 segundos (1 minuto) de abrirse, esto es a la hora de hacer pruebas en PCs
#root.after(600000, root.destroy) 

root.mainloop()

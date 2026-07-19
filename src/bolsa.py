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
            # Descargamos el histórico de 2 días para comparar
            ticker = yf.Ticker(t)
            datos = ticker.history(period="2d")
            
            # Si hoy es festivo o fin de semana, toma los últimos datos disponibles
            precio_actual = datos['Close'].iloc[-1]
            precio_anterior = datos['Close'].iloc[-2]
            variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
            
            simbolo = t.replace(".MC", "")
            
            # Lógica de colores según la variación
            if variacion > 0.005:
                color = "#00FF00"  # Verde
                texto = f"{simbolo}: {precio_actual:.2f}€ (+{variacion:.2f}%) ▲"
            elif variacion < -0.005:
                color = "#FF0000"  # Rojo
                texto = f"{simbolo}: {precio_actual:.2f}€ ({variacion:.2f}%) ▼"
            else:
                color = "#ffffff"  # Blanco
                texto = f"{simbolo}: {precio_actual:.2f}€ ({variacion:.2f}%) →"
            resultados.append({"texto": texto, "color": color})
        except Exception:
            simbolo = t.replace(".MC", "")
            resultados.append({"texto": f"{simbolo}: Datos no disponibles", "color": "#008cff"})
            
    return resultados

# Configurar la ventana gráfica (Pantalla Completa)
root = tk.Tk()
root.overrideredirect(True) # Quita los bordes, barra superior y botones
root.attributes("-topmost", True) # Lo mantiene siempre por encima de otras ventanas

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()

# Posiciona la ventana ocupando el 100% de la pantalla (desde la coordenada 0,0)
root.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")
root.configure(bg="black")

# 3. Preparar el texto rodante (¡Aquí estaba la línea que faltaba!)
canvas = tk.Canvas(root, bg="black", highlightthickness=0, height=alto_pantalla)
canvas.pack(fill="both", expand=True)

elementos_canvas = []
datos_iniciales = obtener_datos()

# Empezamos a dibujar en el borde derecho de la pantalla
pos_x = ancho_pantalla

for dato in datos_iniciales:
    # Creamos un texto individual para esta accion con su color (usando pos_x)
    id_txt = canvas.create_text(pos_x, alto_pantalla // 2, text=dato["texto"], 
                              font=("Consolas", 200, "bold"), fill=dato["color"], anchor="w")
    elementos_canvas.append(id_txt)

    # Calculamos donde acaba la acción para colocar la siguiente
    bbox = canvas.bbox(id_txt)
    pos_x = bbox[2] + 50  # Añadimos un espacio de 50 píxeles entre acciones

# Función de desplazamiento continuo
def desplazar_texto():
    # Movemos todos los elementos x pixeles a la izquierda
    for id_txt in elementos_canvas:
        canvas.move(id_txt, -5, 0)
    
    # Comprobamos si alguno se ha salido de la pantalla por la izquierda
    for id_txt in elementos_canvas:
        bbox = canvas.bbox(id_txt) # Corregido 'canva' por 'canvas'
        if bbox and bbox[2] < 0: 
            # Buscamos el ultimo elemento que va en la cola
            max_x = max(canvas.bbox(i)[2] for i in elementos_canvas)
            nuevo_x = max(max_x, ancho_pantalla) + 50  # Añadimos un espacio de 50 píxeles

            # Lo movemos al final de la cola
            canvas.coords(id_txt, nuevo_x, alto_pantalla // 2)

    root.after(20, desplazar_texto)

# Actualizar en segundo plano (Linux)
def aplicar_actualizaciones(nuevos_datos):
    for i, dato in enumerate(nuevos_datos):
        if i < len(elementos_canvas):
            canvas.itemconfig(elementos_canvas[i], text=dato["texto"], fill=dato["color"])

# Se actualiza cada 5 minutos (Corregido el nombre de la función)
def actualizar_en_segundo_plano():
    while True:
        time.sleep(300) # Espera 300 segundos (5 minutos)
        try:
            nuevo_texto = obtener_datos()
            # Pedimos al sistema gráfico que haga los cambios
            root.after(0, aplicar_updates, nuevo_texto)
        except Exception:
            pass # Si falla internet, ignora el error y reintenta en 5 min

# Iniciamos el trabajador invisible en segundo plano
hilo_actualizacion = threading.Thread(target=actualizar_en_segundo_plano, daemon=True)
hilo_actualizacion.start()

# Activamos el movimiento de la cinta
desplazar_texto()

# Cierra el programa presionando la tecla Escape
root.bind("<Escape>", lambda e: root.destroy())
# SOLO PARA PROBAR EN PCs, se corta el programa a los 60 segundos (1 minuto) para no dejarlo abierto
root.after(60000, root.destroy) 

root.mainloop()
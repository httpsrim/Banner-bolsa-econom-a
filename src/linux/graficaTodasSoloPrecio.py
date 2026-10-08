import tkinter as tk
import yfinance as yf
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Lista de activos
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

# Configuración de la ventana a Pantalla Completa
root = tk.Tk()
root.title("Carrusel Financiero")
root.overrideredirect(True)
root.attributes("-topmost", True)

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()

root.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")
root.configure(bg="black")

frame_grafico = tk.Frame(root, bg="black")
frame_grafico.pack(expand=True, fill="both")

# Variables de control
indice_actual = 0
timer_rotacion = None
canvas_actual = None

def cargar_grafico(indice):
    global canvas_actual, timer_rotacion
    
    # Destruir el gráfico anterior
    if canvas_actual:
        canvas_actual.get_tk_widget().destroy()
        canvas_actual = None
        
    for widget in frame_grafico.winfo_children():
        widget.destroy()

    ticker_simbolo = TICKERS[indice]
    
    # --- DETERMINAR MONEDA / UNIDAD ---
    if ticker_simbolo.startswith("^"):
        moneda = "pts"
    elif ticker_simbolo.endswith(".MC"):
        moneda = "€"
    else:
        moneda = "$"

    try:
        # Descarga de datos
        df = yf.Ticker(ticker_simbolo).history(period="3mo")

        if df.empty:
            raise ValueError("Sin datos disponibles")

        simbolo_limpio = ticker_simbolo.replace(".MC", "")

        # Crear figura
        fig = Figure(figsize=(ancho_pantalla / 100, alto_pantalla / 100), dpi=100, facecolor='black')
        ax1 = fig.add_subplot(111, facecolor='black')

        # Colores: Verde (Alcista) y Rojo (Bajista)
        colores = ['#00FF00' if c >= o else '#FF0000' for o, c in zip(df['Open'], df['Close'])]
        indices = list(range(len(df)))

        # 1. Velas Japonesas
        ax1.vlines(indices, df['Low'], df['High'], color=colores, linewidth=1)
        cuerpos = (df['Close'] - df['Open']).abs()
        bases = df[['Open', 'Close']].min(axis=1)
        ax1.bar(indices, cuerpos, bottom=bases, color=colores, width=0.6)

        # -------------------------------------------------------------
        # CÁLCULO DE LA MEDIA MÓVIL EXPONENCIAL (EMA 15)
        # -------------------------------------------------------------
        df['EMA15'] = df['Close'].ewm(span=15, adjust=False).mean()
        ax1.plot(indices, df['EMA15'], color='#FF007F', linewidth=2, label="Media Exponencial (EMA 15d)")

        # Formato del panel principal
        ax1.set_title(f"[{indice + 1}/{len(TICKERS)}] ANÁLISIS TÉCNICO: {simbolo_limpio} ({ticker_simbolo})", 
                      fontsize=18, color='white', fontweight='bold', pad=15)
        ax1.set_ylabel(f"Precio ({moneda})", fontsize=12, color='white')
        ax1.tick_params(colors='white')
        ax1.grid(True, color='#222222', linestyle='--')
        ax1.legend(loc="upper left")

        # Fechas en eje X
        paso_fechas = max(1, len(df) // 6)
        ticks_x = indices[::paso_fechas]
        etiquetas_x = [df.index[i].strftime('%d/%m') for i in ticks_x]
        ax1.set_xticks(ticks_x)
        ax1.set_xticklabels(etiquetas_x, color='white', fontsize=10)

        fig.tight_layout()

        # Renderizar en interfaz
        canvas_actual = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas_actual.draw()
        canvas_actual.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        lbl_error = tk.Label(
            frame_grafico,
            text=f"[{indice + 1}/{len(TICKERS)}] {ticker_simbolo}\nError al cargar: {e}",
            font=("Consolas", 24),
            fg="#FF0000",
            bg="black"
        )
        lbl_error.pack(expand=True)

    # Rotación automática cada 10 segundos
    timer_rotacion = root.after(10000, siguiente_grafico)

def siguiente_grafico():
    global indice_actual, timer_rotacion
    if timer_rotacion:
        root.after_cancel(timer_rotacion)
    indice_actual = (indice_actual + 1) % len(TICKERS)
    cargar_grafico(indice_actual)

def anterior_grafico():
    global indice_actual, timer_rotacion
    if timer_rotacion:
        root.after_cancel(timer_rotacion)
    indice_actual = (indice_actual - 1) % len(TICKERS)
    cargar_grafico(indice_actual)

# Controles de teclado
root.bind("<Right>", lambda e: siguiente_grafico())
root.bind("<Left>", lambda e: anterior_grafico())
root.bind("<Escape>", lambda e: root.destroy())

cargar_grafico(0)
root.mainloop()

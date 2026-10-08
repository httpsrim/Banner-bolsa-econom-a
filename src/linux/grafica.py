import tkinter as tk
import yfinance as yf
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configuración de la ventana en Pantalla Completa
root = tk.Tk()
root.title("Gráfico Financiero")
root.overrideredirect(True)
root.attributes("-topmost", True)

ancho_pantalla = root.winfo_screenwidth()
alto_pantalla = root.winfo_screenheight()

root.geometry(f"{ancho_pantalla}x{alto_pantalla}+0+0")
root.configure(bg="black")

frame_grafico = tk.Frame(root, bg="black")
frame_grafico.pack(expand=True, fill="both")

def cargar_grafico(ticker_simbolo="^GSPC"):
    try:
        # Descarga de datos históricos (3 meses)
        df = yf.Ticker(ticker_simbolo).history(period="3mo")

        if df.empty:
            raise ValueError(f"No se encontraron datos para {ticker_simbolo}")

        # Creación de la figura
        fig = Figure(figsize=(ancho_pantalla / 100, alto_pantalla / 100), dpi=100, facecolor='black')
        ax1 = fig.add_subplot(211, facecolor='black')
        ax2 = fig.add_subplot(212, facecolor='black', sharex=ax1)

        # Colores de las velas: Verde (Alcista) y Rojo (Bajista)
        colores = ['#00FF00' if c >= o else '#FF0000' for o, c in zip(df['Open'], df['Close'])]
        indices = list(range(len(df)))

        # 1. Velas Japonesas (Mechas y Cuerpos)
        ax1.vlines(indices, df['Low'], df['High'], color=colores, linewidth=1)
        cuerpos = (df['Close'] - df['Open']).abs()
        bases = df[['Open', 'Close']].min(axis=1)
        ax1.bar(indices, cuerpos, bottom=bases, color=colores, width=0.6)

        # Media Móvil Simple de 15 días (SMA)
        df['SMA15'] = df['Close'].rolling(window=15).mean()
        ax1.plot(indices, df['SMA15'], color='#008cff', linewidth=2, label="Media Móvil (15d)")

        # Formato del panel superior (Precios)
        ax1.set_title(f"ANÁLISIS TÉCNICO: S&P 500 ({ticker_simbolo}) - ÚLTIMOS 3 MESES", 
                      fontsize=18, color='white', fontweight='bold', pad=15)
        ax1.set_ylabel("Precio ($)", fontsize=12, color='white')
        ax1.tick_params(colors='white')
        ax1.grid(True, color='#222222', linestyle='--')
        ax1.legend(loc="upper left")

        # 2. Panel inferior (Volumen)
        ax2.bar(indices, df['Volume'], color=colores, alpha=0.7)
        ax2.set_ylabel("Volumen", fontsize=12, color='white')
        ax2.tick_params(colors='white')
        ax2.grid(True, color='#222222', linestyle='--')

        # Formato de fechas en el eje X
        paso_fechas = max(1, len(df) // 6)
        ticks_x = indices[::paso_fechas]
        etiquetas_x = [df.index[i].strftime('%d/%m') for i in ticks_x]
        ax2.set_xticks(ticks_x)
        ax2.set_xticklabels(etiquetas_x, color='white', fontsize=10)

        fig.tight_layout()

        # Renderizar la gráfica dentro de la interfaz
        canvas = FigureCanvasTkAgg(fig, master=frame_grafico)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    except Exception as e:
        lbl_error = tk.Label(
            frame_grafico,
            text=f"Error al cargar el gráfico:\n{e}",
            font=("Consolas", 24),
            fg="#FF0000",
            bg="black"
        )
        lbl_error.pack(expand=True)

# Cargar el gráfico (puedes cambiar "^GSPC" por otro símbolo como "AAPL" o "SAN.MC")
cargar_grafico("^GSPC")

# Presionar la tecla ESCAPE para salir de la aplicación
root.bind("<Escape>", lambda e: root.destroy())

root.mainloop()

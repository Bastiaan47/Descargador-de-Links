#El fokin prodigio de bastiaanTR estubo aqui
import customtkinter as ctk
import tkinter.messagebox as tkmb
import yt_dlp
import threading
import os

# --- Configuracion Visual ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class YutuDownloader(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Batidescargador")
        self.geometry("500x480")
        self.resizable(False, False)

        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        #-Titulo
        self.label_titulo = ctk.CTkLabel(self.main_frame, text="Youtube Downloader", font=ctk.CTkFont(size=20, weight="bold"))
        self.label_titulo.pack(pady=(20, 5))

        self.label_subtitulo = ctk.CTkLabel(self.main_frame, text="Descargar links y listas de reproduccion de Yutu", text_color="gray70")
        self.label_subtitulo.pack(pady=(0, 20))

        #-Entrada de URL
        self.url_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Pega el enlace de YouTube aquí...", width=350, height=40)
        self.url_entry.pack(pady=10)

        #-Switch Playlist
        self.playlist_switch = ctk.CTkSwitch(self.main_frame, text="Descargar Playlist Completa (en una sola carpeta)", width=250)
        self.playlist_switch.pack(pady=10)

        #-Formato
        self.label_fmt = ctk.CTkLabel(self.main_frame, text="Formato de Salida:", anchor="w")
        self.label_fmt.pack(pady=(10, 0))

        self.opciones_formato = [
            "M4A (Mayor Calidad - Menor Tamaño)",
            "MP3 (Buena calidad - estandar)", 
            "WAV (Mayor Calidad - Mayor Tamaño y 0 perdidas)", 
            "FLAC (Calidad superior - no compatible con GTA)",
            "MP4 (Video)"
        ]
        self.formato_combo = ctk.CTkOptionMenu(self.main_frame, values=self.opciones_formato, width=250)
        self.formato_combo.pack(pady=5)

        #-Barra de carga
        self.progress_bar = ctk.CTkProgressBar(self.main_frame, width=350)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=(20, 5))

        self.status_label = ctk.CTkLabel(self.main_frame, text="Esperando...", text_color="gray60", font=ctk.CTkFont(size=13))
        self.status_label.pack(pady=(0, 10))

        #-Boton de descarga
        self.boton_descarga = ctk.CTkButton(self.main_frame, text="INICIAR DESCARGA", height=45, width=350, font=ctk.CTkFont(size=15, weight="bold"), command=self.iniciar_hilo_descarga)
        self.boton_descarga.pack(pady=10)

    # --- LOGICA DE INTERFAZ ---
    def actualizar_ui(self, valor, texto):
        self.progress_bar.set(valor)
        self.status_label.configure(text=texto)

    def hook_progreso(self, d):
        if d['status'] == 'downloading':
            p_str = d.get('_percent_str', '0%').replace('\x1b[0;94m', '').replace('\x1b[0m', '').strip()
            filename = os.path.basename(d.get('filename', 'Archivo'))
            nombre_corto = (filename[:20] + '..') if len(filename) > 20 else filename
            try:
                porcentaje_limpio = p_str.replace('%','')
                valor = float(porcentaje_limpio) / 100
                texto_nuevo = f"⏳ {p_str} | {nombre_corto}"
                self.after(0, lambda v=valor, t=texto_nuevo: self.actualizar_ui(v, t))
            except:
                pass
        elif d['status'] == 'finished':
            self.after(0, lambda: self.actualizar_ui(1.0, "⚙️ Finalizando y limpiando..."))

    def iniciar_hilo_descarga(self):
        url = self.url_entry.get()
        if not url:
            tkmb.showerror("Error", "¡Falta el link!")
            return
        self.boton_descarga.configure(state="disabled", text="Iniciando...")
        self.progress_bar.set(0)
        thread = threading.Thread(target=self.logica_descarga)
        thread.start()

    # --- LOGICA YT-DLP ---
    def logica_descarga(self):
        url = self.url_entry.get()
        formato_seleccionado = self.formato_combo.get()
        es_playlist = self.playlist_switch.get()
        carpeta_raiz = "Descargas"
        
        if "list=" in url and es_playlist:
            nombre_archivo = f"{carpeta_raiz}/%(playlist)s/%(title)s (%(artist)s).%(ext)s"
            noplaylist_option = False
        else:
            nombre_archivo = f"{carpeta_raiz}/%(title)s (%(artist)s).%(ext)s"
            noplaylist_option = True

        opciones = {
            'outtmpl': nombre_archivo,
            'noplaylist': noplaylist_option,
            'writethumbnail': False, 
            'progress_hooks': [self.hook_progreso],
            'quiet': True,
            'no_warnings': True,
            'ignoreerrors': True,
            'restrictfilenames': False,
        }

        #-Configuracion de Formatos
        if formato_seleccionado.startswith("WAV"):
            opciones.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'wav'},{'key': 'FFmpegMetadata'}],
            })
        elif formato_seleccionado.startswith("M4A"):
            opciones.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'm4a'},{'key': 'EmbedThumbnail'}, {'key': 'FFmpegMetadata'}],
            })
        elif formato_seleccionado.startswith("MP3"):
            opciones.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '320'},{'key': 'EmbedThumbnail'},{'key': 'FFmpegMetadata'}],
            })
        elif formato_seleccionado.startswith("FLAC"):
            opciones.update({
                'format': 'bestaudio/best',
                'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'flac'},{'key': 'EmbedThumbnail'},{'key': 'FFmpegMetadata'}],
            })
        elif formato_seleccionado.startswith("MP4"):
            opciones.update({
                'format': 'bestvideo+bestaudio/best',
                'merge_output_format': 'mp4',
                'postprocessors': [{'key': 'EmbedThumbnail'}, {'key': 'FFmpegMetadata'}],
            })

        try:
            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])
            self.after(0, lambda: self.finalizar_exito())
        except Exception as e:
            mensaje_error = str(e)
            self.after(0, lambda: self.finalizar_error(mensaje_error))

    def finalizar_exito(self):
        self.status_label.configure(text="¡Descarga Completada!")
        self.boton_descarga.configure(state="normal", text="INICIAR DESCARGA")
        self.progress_bar.set(0)
        tkmb.showinfo("Éxito", "Carpeta limpia: Solo música.")

    def finalizar_error(self, error_msg):
        self.status_label.configure(text="Error")
        self.boton_descarga.configure(state="normal", text="INICIAR DESCARGA")
        tkmb.showerror("Error", f"Fallo:\n{error_msg}")

if __name__ == "__main__":
    app = YutuDownloader()
    app.mainloop()

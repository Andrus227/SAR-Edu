import customtkinter as ctk
from app import RobixSupervisorio


if __name__ == "__main__":
    try:
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        app = RobixSupervisorio()
        app.mainloop()
    except Exception as e:
        print(f"[ERRO FATAL] Falha ao iniciar o supervisório: {e}")
import tkinter as tk

# color constants

violet = "#752d85"
dark_violet = "#2f1333"
white = "#ffffff"
green = "#12e659"

# text constants

main_title = "NotifAyy"
description = "Get informed when someone post an update anywhere, everywhere."

# font constants

title_font = ("Helvetica", "35", "bold")
info_font = ("Helvetica", "18")
button_font = ("Helvetica", "14", "bold")
login_font = ("Helvetica", "14")


window = tk.Tk()
window.title(main_title)
window.minsize(800, 600)

background_image = tk.PhotoImage(file="./tlo03.gif")
background_label = tk.Label(window, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

main_frame = tk.Frame(window, bg=violet, bd=15, relief="raised")
main_frame.place(in_=window, anchor="c", relx=0.5, rely=0.5)

info_frame = tk.Frame(main_frame, bg=violet)
info_frame.grid(row=0, column=0, sticky="w")

title = tk.Label(info_frame,
                 text=main_title,
                 font=title_font,
                 bg=violet,
                 fg=white)
info = tk.Label(info_frame,
                text=description,
                font=info_font,
                bg=violet,
                fg=white)

title.grid(row=0, column=0, sticky="w")
info.grid(row=1, column=0, sticky="w")

login_panel_frame = tk.Frame(main_frame, bg=violet)
login_panel_frame.grid(row=1, column=0, sticky="w")

login = tk.Entry(login_panel_frame,
                 width=25,
                 bg=dark_violet,
                 fg=white,
                 font=login_font)
password = tk.Entry(login_panel_frame,
                    width=25,
                    bg=dark_violet,
                    fg=white,
                    show="*",
                    font=login_font)
signup_button = tk.Button(login_panel_frame,
                          text="Sign up",
                          bg=green,
                          font=button_font)
login_button = tk.Button(login_panel_frame,
                         text="Log in",
                         bg=green,
                         font=button_font)

login.grid(row=0, column=0, sticky="w")
password.grid(row=0, column=1, sticky="w")
login_button.grid(row=0, column=2, sticky="w")
signup_button.grid(row=0, column=3, sticky="w")

window.mainloop()

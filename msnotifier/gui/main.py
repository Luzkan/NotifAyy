import tkinter as tk
from pathlib import Path

import msnotifier.gui.validator as validator
import msnotifier.gui.constants as const


def add_alert():
    alerts_list.insert(tk.END,
                       f"Alert: {alert_title.get()}, URL: {webpage_url.get()}")


def delete_alert(event):
    w = event.widget
    try:
        index = w.curselection()[0]
        alerts_list.delete(index)
    except IndexError:
        pass


def new_user_msg():
    user_exists_label.grid_forget()
    wrong_data_label.grid_forget()
    new_user_label.grid(row=2, column=0, sticky="w")


def user_exists_msg():
    wrong_data_label.grid_forget()
    new_user_label.grid_forget()
    user_exists_label.grid(row=2, column=0, sticky="w")


def wrong_data_msg():
    user_exists_label.grid_forget()
    new_user_label.grid_forget()
    wrong_data_label.grid(row=2, column=0, sticky="w")


def switch_to_main_frame():
    manager_frame.place_forget()
    user_exists_label.grid_forget()
    wrong_data_label.grid_forget()
    new_user_label.grid_forget()
    main_frame.place(in_=window, anchor="c", relx=0.5, rely=0.5)


def switch_to_manager_frame():
    main_frame.place_forget()
    manager_frame.place(in_=window, anchor="c", relx=0.5, rely=0.5)

    welcome_message = f"Hello, {login.get()}!"
    welcome_label = tk.Label(welcome_frame,
                             text=welcome_message,
                             font=const.welcome_font,
                             bg=const.violet,
                             fg=const.white)

    welcome_frame.grid(row=0, column=0, sticky="w")
    data_frame.grid(row=1, column=0, sticky="w")
    listbox_frame.grid(row=2, column=0, sticky="w")

    welcome_label.grid(row=0, column=0, sticky="w")
    logout_button.grid(row=0, column=1, sticky="e")
    welcome_info_label.grid(row=1, column=0, sticky="w")

    webpage_url_label.grid(row=2, column=0, sticky="w")
    webpage_url.grid(row=2, column=1, sticky="w")
    add_alert_button.grid(row=3, column=2, sticky="e")
    alert_title_label.grid(row=3, column=0, sticky="w")
    alert_title.grid(row=3, column=1, sticky="w")

    alerts_list.grid(row=0, column=0, sticky="w")


def check_sign_up():
    if not validator.user_exists(login.get()):
        validator.add_new_user(login.get(), password.get())
        new_user_msg()
    else:
        user_exists_msg()


def validate():
    if not validator.data_is_valid(login.get(), password.get()):
        wrong_data_msg()
    else:
        switch_to_manager_frame()


# main window
window = tk.Tk()
window.title(const.main_title)
window.minsize(800, 600)

# background image
background_image = tk.PhotoImage(file=Path("msnotifier")
                                 / ("gui") / ("tlo03.gif"))
background_label = tk.Label(window, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

# main frame - contains info_frame and login_panel_frame
main_frame = tk.Frame(window, bg=const.violet, bd=15, relief="raised")
main_frame.place(in_=window, anchor="c", relx=0.5, rely=0.5)

info_frame = tk.Frame(main_frame, bg=const.violet)
info_frame.grid(row=0, column=0, sticky="w")

# info_frame elements
title = tk.Label(info_frame,
                 text=const.main_title,
                 font=const.title_font,
                 bg=const.violet,
                 fg=const.white)
info = tk.Label(info_frame,
                text=const.description,
                font=const.info_font,
                bg=const.violet,
                fg=const.white)
wrong_data_label = tk.Label(info_frame,
                            text=const.wrong_data,
                            font=const.info_font,
                            bg=const.violet,
                            fg=const.red)
user_exists_label = tk.Label(info_frame,
                             text=const.user_exists_text,
                             font=const.info_font,
                             bg=const.violet,
                             fg=const.red)
new_user_label = tk.Label(info_frame,
                          text=const.user_added,
                          font=const.info_font,
                          bg=const.violet,
                          fg=const.standard_green)

title.grid(row=0, column=0, sticky="w")
info.grid(row=1, column=0, sticky="w")

login_panel_frame = tk.Frame(main_frame, bg=const.violet)
login_panel_frame.grid(row=1, column=0, sticky="w")

# login_panel_frame elements
login = tk.Entry(login_panel_frame,
                 width=25,
                 bg=const.dark_violet,
                 fg=const.white,
                 font=const.login_font)
password = tk.Entry(login_panel_frame,
                    width=25,
                    bg=const.dark_violet,
                    fg=const.white,
                    show="*",
                    font=const.login_font)
signup_button = tk.Button(login_panel_frame,
                          text=const.sign_up,
                          bg=const.green,
                          font=const.button_font,
                          command=check_sign_up)
login_button = tk.Button(login_panel_frame,
                         text=const.login_text,
                         bg=const.green,
                         font=const.button_font,
                         command=validate)

login.grid(row=0, column=0, sticky="w")
password.grid(row=0, column=1, sticky="w")
login_button.grid(row=0, column=2, sticky="w")
signup_button.grid(row=0, column=3, sticky="w")

manager_frame = tk.Frame(window,
                         bg=const.violet,
                         bd=15,
                         relief="raised")

welcome_frame = tk.Frame(manager_frame, bg=const.violet)

welcome_info_label = tk.Label(welcome_frame,
                              text=const.welcome_info,
                              font=const.welcome_info_font,
                              bg=const.violet,
                              fg=const.white)
logout_button = tk.Button(welcome_frame,
                          text=const.logout,
                          bg=const.green,
                          font=const.button_font,
                          command=switch_to_main_frame)

data_frame = tk.Frame(manager_frame, bg=const.violet)

webpage_url_label = tk.Label(data_frame,
                             text=const.webpage_url_text,
                             font=const.alerts_font,
                             bg=const.violet,
                             fg=const.white)
webpage_url = tk.Entry(data_frame,
                       width=25,
                       bg=const.dark_violet,
                       fg=const.white,
                       font=const.login_font)
alert_title = tk.Entry(data_frame,
                       width=25,
                       bg=const.dark_violet,
                       fg=const.white,
                       font=const.login_font)
alert_title_label = tk.Label(data_frame,
                             text=const.alert_title_text,
                             font=const.alerts_font,
                             bg=const.violet,
                             fg=const.white)
add_alert_button = tk.Button(data_frame,
                             text=const.add_alert,
                             bg=const.green,
                             font=const.alerts_font_bold,
                             command=add_alert)

listbox_frame = tk.Frame(manager_frame, bg=const.violet)

alerts_list = tk.Listbox(listbox_frame,
                         bg=const.dark_violet,
                         fg=const.white,
                         font=const.alerts_font)
alerts_list.bind('<<ListboxSelect>>', delete_alert)

window.mainloop()

import tkinter as tk
from pathlib import Path

import msnotifier.gui.manager as manager
import msnotifier.gui.constants as const


def get_alerts() -> None:
    alerts_list.delete(0, "end")
    for alert in manager.get_current_alerts(manager.current_user):
        alerts_list.insert(tk.END, alert)


def main_add_alert() -> None:
    alert_content = f"Alert: {alert_title.get()}, URL: {webpage_url.get()}"
    alerts_list.insert(tk.END, alert_content)
    manager.add_alert(manager.current_user, alert_content)


def delete_alert(event) -> None:
    w = event.widget
    try:
        index = w.curselection()[0]
        alerts_list.delete(index)
        manager.delete_alert(manager.current_user, index)
    except IndexError:
        pass


def new_user_msg() -> None:
    user_exists_label.grid_forget()
    wrong_data_label.grid_forget()
    new_user_label.grid(row=2, column=0, sticky="w")


def user_exists_msg() -> None:
    wrong_data_label.grid_forget()
    new_user_label.grid_forget()
    user_exists_label.grid(row=2, column=0, sticky="w")


def wrong_data_msg() -> None:
    user_exists_label.grid_forget()
    new_user_label.grid_forget()
    wrong_data_label.grid(row=2, column=0, sticky="w")


def switch_to_main_frame() -> None:
    manager.current_user = ""
    manager_frame.place_forget()
    user_exists_label.grid_forget()
    wrong_data_label.grid_forget()
    new_user_label.grid_forget()
    main_frame.place(in_=window, anchor="c", relx=0.5, rely=0.5)


def switch_to_manager_frame() -> None:
    main_frame.place_forget()
    manager_frame.place(in_=window, anchor="c", relx=0.5, rely=0.5)
    manager.current_user = login.get()
    welcome_message = f"Hello, {manager.current_user}!"
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
    webpage_url.delete(0, "end")
    add_alert_button.grid(row=3, column=2, sticky="e")
    alert_title_label.grid(row=3, column=0, sticky="w")
    alert_title.grid(row=3, column=1, sticky="w")
    alert_title.delete(0, "end")

    alerts_list.grid(row=0, column=0, sticky="w")
    get_alerts()


def check_sign_up() -> None:
    if not manager.user_exists(login.get()):
        manager.add_new_user(login.get(), password.get())
        new_user_msg()
    else:
        user_exists_msg()


def validate() -> None:
    if not manager.data_is_valid(login.get(), password.get()):
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

listbox_frame = tk.Frame(manager_frame, bg=const.violet)

alerts_list = tk.Listbox(listbox_frame,
                         bg=const.dark_violet,
                         fg=const.white,
                         font=const.alerts_font,
                         bd=5,
                         relief="raised",
                         width="65")
alerts_list.bind('<<ListboxSelect>>', delete_alert)

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
                             command=main_add_alert)

window.mainloop()

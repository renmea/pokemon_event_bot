import tkinter as tk
from tkinter import ttk
import webbrowser
from config import *


def open_url(url):
    webbrowser.open(url)


def show(results):

    root=tk.Tk()

    root.title(
        "Pokemon Championsイベント"
    )

    root.geometry(
        f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}"
    )

    notebook=ttk.Notebook(root)

    notebook.pack(
        fill="both",
        expand=True
    )


    for category,data in results.items():

        frame=tk.Frame(
            notebook
        )

        notebook.add(
            frame,
            text=f"{category} ({len(data)})"
        )


        canvas=tk.Canvas(
            frame
        )

        scrollbar=tk.Scrollbar(
            frame,
            orient="vertical",
            command=canvas.yview
        )

        content=tk.Frame(
            canvas
        )


        content.bind(
            "<Configure>",
            lambda e,c=canvas:
            c.configure(
                scrollregion=c.bbox("all")
            )
        )


        canvas.create_window(
            (0,0),
            window=content,
            anchor="nw"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )


        for title,url in data:

            # 外枠
            box=tk.Frame(
                content,
                relief="solid",
                borderwidth=1,
                padx=10,
                pady=10
            )

            box.pack(
                fill="x",
                padx=5,
                pady=5
            )


            # イベント名
            title_label=tk.Label(

                box,

                text=title,

                font=(
                    "Meiryo",
                    15,
                    "bold"
                ),

                justify="left",

                anchor="w",

                wraplength=1300
            )

            title_label.pack(
                fill="x",
                anchor="w"
            )


            # URL説明
            url_text=tk.Label(

                box,

                text="URL:",

                font=(
                    "Meiryo",
                    10,
                    "bold"
                ),

                anchor="w"
            )

            url_text.pack(
                anchor="w"
            )


            # URL本体だけクリック可能
            link=tk.Label(

                box,

                text=url,

                fg="blue",

                cursor="hand2",

                font=(
                    "Meiryo",
                    10,
                    "underline"
                ),

                justify="left",

                anchor="w"
            )

            link.pack(
                anchor="w"
            )


            link.bind(

                "<Button-1>",

                lambda e,u=url:
                open_url(u)

            )


    root.mainloop()
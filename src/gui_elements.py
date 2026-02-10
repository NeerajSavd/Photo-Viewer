import flet as ft
from search import on_this_day
from PIL import Image
import os
import io
from datetime import datetime

def create_image_card(img_path):
    def open_explorer():
        folder = os.path.dirname(os.path.abspath(img_path))
        if os.path.exists(folder):
            os.startfile(folder)
    def open_image():
        os.startfile(img_path)
    
    with Image.open(img_path) as img:
        img.thumbnail((250, 250))
        buf = io.BytesIO()
        try:
            img.save(buf, format="JPEG")
        except OSError:
            img = img.convert("RGB")
            img.save(buf, format="JPEG")
        img = buf.getvalue()

    image = ft.Image(
        src=img,
        width=200,
        height=200,
        fit="cover"
    )
    return ft.Container(
        content=
            ft.GestureDetector(
                content=image,
                on_tap=open_image,
                on_long_press=open_explorer,
                mouse_cursor=ft.MouseCursor.CLICK
            ),
        width=200,
        height=200,
    )

def create_otd_grid():
    images = on_this_day()
    main_view = ft.ListView(
        expand=1,
        spacing=15,
        padding=15,
    )
    for category in images:
        category_name = category[0]
        category_images = category[1]
        main_view.controls.append(
            ft.Row(
                controls=[ft.Text(value=category_name, size=30, weight=ft.FontWeight.BOLD)],
                alignment=ft.MainAxisAlignment.CENTER,
            )
        )
        images_row = ft.Row(
            wrap=True,
            spacing=10,
            run_spacing=10,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[]
        )
        for img in category_images:
            images_row.controls.append(create_image_card(img))
        main_view.controls.append(images_row)
    
    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(value="On This Day", size=50, weight=ft.FontWeight.BOLD),
                ft.Text(value=f"{datetime.now().strftime('%B %d %Y')}".replace(" 0", " "),
                    size=25, weight=ft.FontWeight.BOLD,
                ),
                main_view,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=1,
    )
    return container

def create_image_grid(images, page_number):
    main_view = ft.ListView(
        expand=1,
        spacing=15,
        padding=15,
    )
    images_row = ft.Row(
        wrap=True,
        spacing=10,
        run_spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        controls=[]
    )
    for img in images[page_number * IMAGES_PER_PAGE:(page_number + 1) * IMAGES_PER_PAGE]:
        images_row.controls.append(create_image_card(img))
    
    main_view.controls.append(images_row)
    container = ft.Container(
        content=ft.Column(
            controls=[
                ft.Text(value="Results", size=50, weight=ft.FontWeight.BOLD),
                main_view,
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=1,
    )
    return container

IMAGES_PER_PAGE = 20

def create_page_nav(page_number, prev_page, next_page, length):
    nav_bar = ft.Row()
    if page_number > 0:
        prev_button = ft.IconButton(
            icon=ft.Icons.ARROW_BACK,
            icon_color=ft.Colors.WHITE,
            tooltip="Previous Page",
            bgcolor=ft.Colors.BLACK,
            on_click=lambda _: prev_page(),
        )
        nav_bar.controls.append(prev_button)
    
    num_pages = (length + IMAGES_PER_PAGE - 1) // IMAGES_PER_PAGE
    nav_bar.controls.append(ft.Text(f"Page {page_number + 1} of {num_pages}"))

    if length > IMAGES_PER_PAGE * (page_number + 1):
        next_button = ft.IconButton(
            icon=ft.Icons.ARROW_FORWARD,
            icon_color=ft.Colors.WHITE,
            tooltip="Next Page",
            bgcolor=ft.Colors.BLACK,
            on_click=lambda _: next_page(),
        )
        nav_bar.controls.append(next_button)
    return nav_bar
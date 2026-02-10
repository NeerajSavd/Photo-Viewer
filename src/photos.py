import flet as ft
from gui_elements import create_otd_grid, create_image_grid, create_page_nav
from search import search
from image_tagging import run_analysis
import asyncio

class PhotoApp(ft.Container):
    def __init__(self, page, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pages = page
        self.pages.title = "Photos"
        self.pages.bgcolor = ft.Colors.BLACK
        
        self.query = ''
        self.pages.appbar = self.create_appbar()
        self.create_main_page()
        self.images = None
        self.page_number = 0

    def create_appbar(self):
        return ft.AppBar(
            title=ft.Text("Photos"),
            leading_width=40,
            center_title=False,
            bgcolor='#1e2a56',
            actions=[
                ft.PopupMenuButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=ft.Colors.WHITE
                ),
            ],
        )
    
    async def submit_search(self, e):
        self.query = e
        self.pages.clean()
        loading = ft.Row(
            controls=[
                ft.ProgressRing(
                color=ft.Colors.WHITE,
            )],
            alignment=ft.MainAxisAlignment.CENTER,
        )
        self.pages.add(loading)
        self.pages.update()
        await asyncio.sleep(0.1)
        self.images = search(self.query)
        self.create_search_page()

    def create_main_page(self):
        self.pages.clean()
        search_bar = ft.TextField(
            hint_text="Search your library...",
            prefix_icon=ft.Icons.SEARCH,
            border_radius=25,
            height=45,
            width=600,
            bgcolor='#333333',
            on_submit=self.submit_search,
        )
        search_container = ft.Container(
            content=ft.Row(
                controls=[search_bar],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.Padding.only(top=25, bottom=20),
        )
        self.pages.add(search_container)
        self.pages.add(create_otd_grid())

        sync_button = ft.Button(
            content=ft.Text(
                value="Sync Library",
                color=ft.Colors.WHITE,
            ),
            on_click=lambda _: run_analysis(),
            bgcolor='#1e2a56',
            icon=ft.Icons.SYNC,
        )
        self.pages.add(sync_button)
    
    def create_search_page(self):
        self.pages.clean()
        back_button = ft.Button(
            content=ft.Text(
                value="Back",
                color=ft.Colors.WHITE,
            ),
            tooltip="Back",
            bgcolor='#1e2a56',
            on_click=self.create_main_page,
        )
        self.pages.add(back_button)

        def prev_page():
            self.page_number -= 1
            self.create_search_page()
        def next_page():
            self.page_number += 1
            self.create_search_page()

        self.pages.add(create_image_grid(self.images, self.page_number))
        self.pages.add(create_page_nav(self.page_number, prev_page, next_page, len(self.images)))


def main(page: ft.Page):
    app = PhotoApp(page)
    page.add(app)

ft.run(main)
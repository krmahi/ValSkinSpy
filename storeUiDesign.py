import flet as ft

def main(page: ft.Page):
    page.add(
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=f"https://media.valorant-api.com//weaponskinlevels/ba42fe63-457a-78ce-4499-47950a698129//displayicon.png", 
                                fit=ft.ImageFit.CONTAIN
                            ),
                            # content=ft.Text("skin 1"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "white"),
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=f"c:\\Users\\Em\\Pictures\\Jinx\\LeagueofLegends_ArcaneJinx.jpg",
                                fit=ft.ImageFit.CONTAIN
                            ),
                            # content=ft.Text("skin 2"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "white"),
                            # bgcolor="blue",
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
        ft.Row(
            [
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=f"https://media.valorant-api.com//weaponskinlevels//3bc38af9-4068-164e-d42f-da844a259058/displayicon.png",
                                fit=ft.ImageFit.CONTAIN
                            ),
                            # content=ft.Text("skin 3"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "white"),
                            # bgcolor="green",
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
                ft.Column(
                    [
                        ft.Container(
                            content=ft.Image(
                                src=f"c:\\Users\\Em\\Pictures\\Jinx\\WhatsApp Image 2024-11-20 at 5.06.28 PM.jpeg",
                                fit=ft.ImageFit.CONTAIN
                            ),

                            # content=ft.Text("skin 4"),
                            alignment=ft.alignment.center,
                            border=ft.border.all(1, "white"),
                            # bgcolor="yellow",
                            expand=True,
                        )
                    ],
                    expand=True,
                ),
            ],
            expand=True,
        ),
    )


ft.app(main)

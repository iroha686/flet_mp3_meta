from mutagen.id3 import ID3, APIC
import flet as ft
import os

class Mp3App(ft.UserControl): #uiを構築
    def build(self): #主要なUI
        self.selected_mp3 = None
        self.selected_png = None
        self.mp3_name_t = ft.Text("未選択", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color="PINK500")
        self.png_name_t = ft.Text("未選択", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color="PINK500")
        self.cover_log = ft.Text(" ", size=16)

        self.main_content = ft.Column(
            controls=[
                ft.Text("タグの編集", theme_style=ft.TextThemeStyle.TITLE_LARGE),
            ]
        )

        self.cover_content = ft.Column(
            controls=[
                ft.Text("カバーの変更", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.FloatingActionButton(
                    "カバー(png)を選択",icon=ft.icons.FILE_UPLOAD,bgcolor="PINK50",
                    elevation=1,hover_elevation=3,highlight_elevation=4,
                    on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["png"]),
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "選択したカバー：",theme_style=ft.TextThemeStyle.TITLE_MEDIUM,color="BLACK87",
                        ),
                        self.png_name_t,
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.FloatingActionButton(
                            "カバー埋め込み", icon=ft.icons.SAVE_ALT, bgcolor="PINK50",
                            elevation=1, hover_elevation=3, highlight_elevation=4,
                            on_click=self.embed_cover,
                        ),
                        self.cover_log,
                    ]
                ),
            ]
        )

        self.filter = ft.Tabs( #タブの作成
            scrollable=False, #タブを水平方向にスクロールできるかどうか
            selected_index=0, #初期状態で選択されているタブ
            on_change=self.tabs_changed, #タブが変更されたときにself.tabs_changed呼び出し
            #タブを2つ作成
            tabs=[ft.Tab(text="メイン"), ft.Tab(text="カバー")],
        )

        self.content_display = ft.Column(controls=[self.main_content]) #起動時はメインタブ

        self.file_picker = ft.FilePicker(on_result=self.file_picker_result)# FilePickerの初期化        
        self.page.overlay.append(self.file_picker)# FilePickerをoverlayに追加

        return ft.Column( #画面の配置
            width=700, #全体の横幅
            controls=[
                ft.FloatingActionButton(
                    "曲(mp3)を選択",icon=ft.icons.UPLOAD_FILE,bgcolor="PINK50",
                    elevation=1,hover_elevation=3,highlight_elevation=4,
                    on_click=lambda _: self.file_picker.pick_files(allowed_extensions=["mp3"]),
                ),
                ft.Row(
                    controls=[
                        ft.Text(
                            "編集する曲：",theme_style=ft.TextThemeStyle.TITLE_MEDIUM,color="BLACK87",
                        ),
                        self.mp3_name_t,
                    ],
                ),
                ft.Column(
                    spacing=20, #Column内のコントロールの間隔
                    controls=[
                        self.filter, #タブの呼び出し
                        self.content_display,
                    ],
                ),
            ],
        )

    #ファイル処理
    async def file_picker_result(self, e: ft.FilePickerResultEvent):
        if e.files:
            selected_file = e.files[0] #ファイルを取得
            if selected_file.name.endswith('.mp3'):
                self.selected_mp3 = selected_file.path
                self.mp3_name_t.value = f"{selected_file.name}"
            elif selected_file.name.endswith('.png'):
                self.selected_png = selected_file.path
                self.png_name_t.value = f"{selected_file.name}"
        await self.update_async()

    #タブが変更されたときに呼び出し
    async def tabs_changed(self, e):
        c_tab_index = self.filter.tabs[self.filter.selected_index].text #現在のタブのテキスト取得
        if c_tab_index == "メイン": #タブのごとに処理を実行
            self.content_display.controls = [self.main_content]
        elif c_tab_index == "カバー":
            self.content_display.controls = [self.cover_content]
        await self.update_async()

    async def embed_cover(self, e): #カバー埋め込み
        if not self.selected_mp3:
            self.cover_log.value = "MP3ファイルが選択されていません。"
        elif not self.selected_png:
            self.cover_log.value = "PNGファイルが選択されていません。"
        else:
            tag = ID3(self.selected_mp3) #MP3ファイルのID3タグ取得

            tag.delall('APIC') #前のAPICフレームを削除

            # カバーアートを更新
            with open(self.selected_png, "rb") as img_f:
                new_cover_d = img_f.read()
                tag.add(APIC(mime="image/png", type=3, desc=u"Cover", data=new_cover_d))
                
                tag.save(self.selected_mp3) #MP3ファイルに保存

                self.cover_log.value = f"{self.mp3_name_t.value} のカバー変更しました。"
        await self.update_async()

    #GUIを更新するときに呼び出し
    async def update_async(self):
        await super().update_async() #更新

#GUIの構築
async def main(page: ft.Page):
    page.title = "mp3 tag"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    await page.add_async(Mp3App())


ft.app(main) # アプリケーション起動
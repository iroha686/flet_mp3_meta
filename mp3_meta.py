from mutagen.id3 import ID3, APIC, TIT2, TRCK
from mutagen.mp3 import MP3
import flet as ft
import os

class Mp3App(ft.UserControl): #uiを構築
    def build(self): #主要なUI
        self.selected_mp3 = None
        self.selected_png = None
        self.mp3_ti_t = ft.Text()
        self.mp3_tr_t = ft.Text()
        self.mp3_name_t = ft.Text("未選択", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color="PINK500")
        self.png_name_t = ft.Text("未選択", theme_style=ft.TextThemeStyle.TITLE_MEDIUM, color="PINK500")
        self.main_log = ft.Text(size=16)
        self.cover_log = ft.Text(size=16)

        self.edit_ti = ft.TextField(expand=True) #タイトルを入力する欄の作成
        self.edit_tr = ft.TextField(expand=True) #トラック番号

        self.main_content = ft.Column(
            controls=[
                ft.Text("タグの編集", theme_style=ft.TextThemeStyle.TITLE_LARGE),
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Text(
                            "タイトル",size=16,width=100
                        ),
                        self.edit_ti
                    ]
                ),
                ft.Row(
                    spacing=5,
                    controls=[
                        ft.Text(
                            "トラック番号",size=16,width=100
                        ),
                        self.edit_tr,
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.FloatingActionButton(
                            "タグを保存", icon=ft.icons.SAVE_ROUNDED, bgcolor="PINK50",
                            elevation=1, hover_elevation=3, highlight_elevation=4,
                            on_click=self.save_tags
                        ),
                        self.main_log,
                    ]
                ),
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

    #タグを保存するとき呼び出し
    async def save_tags(self, e):
        if not self.selected_mp3:
            self.main_log.value = "MP3ファイルが選択されていません"
            await self.update_async()
            return

        try:
            audio = MP3(self.selected_mp3, ID3=ID3)

            #タイトルを設定
            title = self.edit_ti.value
            if title:
                audio.tags["TIT2"] = TIT2(encoding=3, text=title)

            #トラック番号を設定
            track = self.edit_tr.value
            if track:
                audio.tags["TRCK"] = TRCK(encoding=3, text=track)

            audio.save()
            self.main_log.value = f"MP3タグを保存しました: {self.mp3_name_t.value}"

        except Exception as ex:
            self.main_log.value = f"エラーが発生しました: {ex}"
        await self.update_async()

    async def embed_cover(self, e): #カバー埋め込み
        if not self.selected_mp3:
            self.cover_log.value = "MP3ファイルが選択されていません。"
            await self.update_async()
            return
        elif not self.selected_png:
            self.cover_log.value = "PNGファイルが選択されていません。"
            await self.update_async()
            return
        
        try:
            tag = ID3(self.selected_mp3) #MP3ファイルのID3タグ取得

            tag.delall('APIC') #前のAPICフレームを削除

            # カバーアートを更新
            with open(self.selected_png, "rb") as img_f:
                new_cover_d = img_f.read()
                tag.add(APIC(mime="image/png", type=3, desc=u"Cover", data=new_cover_d))
                
                tag.save(self.selected_mp3) #MP3ファイルに保存

                self.cover_log.value = f"カバー変更しました: {self.mp3_name_t.value}"

        except Exception as ex:
            self.cover_log.value = f"エラーが発生しました: {ex}"
        await self.update_async()

#GUIの構築
async def main(page: ft.Page):
    page.title = "mp3 tag"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.ADAPTIVE

    await page.add_async(Mp3App())


ft.app(main) # アプリケーション起動
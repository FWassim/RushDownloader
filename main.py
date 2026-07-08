import flet as ft
import shutil
import config
import engine

#-----------------------------------
# Main Page config
#-----------------------------------
async def main(page: ft.Page):
    page.title = "Rush Downloader"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = config.BG
    page.window.width = 640
    page.window.height = 760
    page.window.min_width = 560
    page.window.min_height = 640
    page.padding = 0
    page.fonts = {
        "FiraCode" : "FiraCode-Medium.ttf"
    }
    page.theme = ft.Theme(font_family="FiraCode")

    folder_path = {"value": ""}
    rows_by_url = {}

    # ---------------------------------------------------------------
    # Header
    # ---------------------------------------------------------------
    header = ft.Container(
        content=ft.Row(
            [
                ft.Container(
                    content=ft.Icon(ft.Icons.DOWNLOAD, color=config.BG, size=24),
                    bgcolor=config.ACCENT_YELLOW,
                    padding=8,
                    border_radius=0,
                ),
                ft.Column(
                    [
                        ft.Text("YT Batch Downloader", size=22, color=config.ACCENT_YELLOW),
                        ft.Text("H.264 (MP4) encoding for Premiere Pro", size=11, color=config.ACCENT_CYAN),
                    ],
                    spacing=0,
                    tight=True,
                ),
            ],
            spacing=14,
        ),
        padding=ft.Padding(28, 26, 28, 18),
        border=ft.Border(bottom=ft.BorderSide(1, config.BORDER)),
    )
    # ---------------------------------------------------------------
    # Links input area (DYNAMIC ROWS)
    # ---------------------------------------------------------------
    link_rows_container = ft.Column(spacing=10)

    def add_link_row(e=None, pasted_url=""):
        url_field = ft.TextField(
            value=pasted_url,
            hint_text="> PASTE_URL_HERE",
            expand=True,
            bgcolor=config.SURFACE_ALT,
            border_color=config.BORDER,
            focused_border_color=config.ACCENT_CYAN,
            border_radius=0,
            text_style=ft.TextStyle(color=config.TEXT_PRIMARY, size=13),
            content_padding=12,
        )

        def on_url_change(e):
            val = e.control.value
            if "\n" in val:
                lines = [line.strip() for line in val.split("\n") if line.strip()]
                if lines:
                    e.control.value = lines[0]
                    e.control.update()
                    for line in lines[1:]:
                        if config.YOUTUBE_REGEX.match(line): 
                            add_link_row(pasted_url=line)
        
        url_field.on_change = on_url_change

        start_field = ft.TextField(
            hint_text="START (opt.)", 
            width=115, 
            bgcolor=config.SURFACE_ALT, 
            border_color=config.BORDER, 
            focused_border_color=config.ACCENT_CYAN, 
            border_radius=0, 
            text_style=ft.TextStyle(color="#FCEE0A", size=12),
            content_padding=12,
            on_blur=validate_time_field,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,2}(:[0-9]{0,2}){0,2}$", replacement_string="")
        )
        
        end_field = ft.TextField(
            hint_text="END (opt.)",
            width=115, 
            bgcolor=config.SURFACE_ALT, 
            border_color=config.BORDER, 
            focused_border_color=config.ACCENT_CYAN, 
            border_radius=0, 
            text_style=ft.TextStyle(color="#FCEE0A", size=12),
            content_padding=12,
            on_blur=validate_time_field,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]{0,2}(:[0-9]{0,2}){0,2}$", replacement_string="")
        )
        
        row = ft.Row([
            url_field, 
            start_field, 
            end_field,
            ft.IconButton(
                icon=ft.Icons.CLOSE, 
                icon_color="#FF003C",
                icon_size=18, 
                on_click=lambda e: remove_link_row(row)
            )
        ], spacing=8)
        
        row.data = {"url": url_field, "start": start_field, "end": end_field}
        link_rows_container.controls.append(row)
        page.update()

    def remove_link_row(row):
        if row in link_rows_container.controls:
            link_rows_container.controls.remove(row)
            page.update()

    def validate_time_field(e):
        val = e.control.value
        if not val: 
            e.control.border_color = config.BORDER
            e.control.update()
            return
        
        parts = val.split(':')
        for part in parts[1:]: 
            if part.isdigit() and int(part) >= 60:
                e.control.border_color = config.ACCENT_RED
                e.control.update()
                return
        e.control.border_color = config.BORDER
        e.control.update()
        
    add_link_row() 
    btn_add_link = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.ADD, size=16), ft.Text("ADD VIDEO LINK")], tight=True), 
        style=ft.ButtonStyle(color=config.ACCENT_CYAN), 
        on_click=add_link_row
    )

    def clear_all_links(e=None):
        link_rows_container.controls.clear()
        add_link_row()
        page.update()
    
    btn_clear_all = ft.TextButton(
        content=ft.Row([ft.Icon(ft.Icons.DELETE_SWEEP, size=16), ft.Text("CLEAR ALL")], tight=True), 
        style=ft.ButtonStyle(color=config.ACCENT_RED), 
        on_click=clear_all_links
    )

    links_card = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [ft.Text("VIDEO URLS", size=12, color=config.TEXT_MUTED), 
                     ft.Row([btn_clear_all, btn_add_link], spacing=10)], 
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Container(height=4),
                link_rows_container,
            ], 
            spacing=0
        ),
        bgcolor=config.SURFACE,
        border=ft.Border(
            top=ft.BorderSide(1, config.BORDER), 
            right=ft.BorderSide(1, config.BORDER), 
            bottom=ft.BorderSide(1, config.BORDER), 
            left=ft.BorderSide(1, config.BORDER)
        ),
        border_radius=0,
        padding=18, 
        margin=ft.Margin(28, 20, 28, 16),
    )

    # ---------------------------------------------------------------
    # Folder selector
    # ---------------------------------------------------------------
    folder_text = ft.Text("Output folder: not set", size=12, color=config.TEXT_MUTED, expand=True, no_wrap=True)

    async def choose_folder(_):
        path = await ft.FilePicker().get_directory_path(dialog_title="Select output folder")
        if path:
            folder_path["value"] = path
            display = path if len(path) < 46 else "…" + path[-45:]
            folder_text.value = f"Output folder: {display}"
            folder_text.color = config.ACCENT_YELLOW
            page.update()

    folder_card = ft.Container(
        content=ft.Row(
            [
                folder_text,
                ft.OutlinedButton(
                    "Browse",
                    icon=ft.Icons.FOLDER_OPEN,
                    style=ft.ButtonStyle(
                        color=config.ACCENT_CYAN,
                        side=ft.BorderSide(1, config.ACCENT_CYAN),
                        shape=ft.RoundedRectangleBorder(radius=0),
                    ),
                    on_click=choose_folder,
                ),
            ],
            spacing=10,
        ),
        bgcolor=config.SURFACE,
        border=ft.Border.all(1, config.BORDER),
        border_radius=0,
        padding=14,
        margin=ft.Margin(28, 0, 28, 20),
    )

    # ---------------------------------------------------------------
    # Action button + progress + status banner
    # ---------------------------------------------------------------
    progress_bar = ft.ProgressBar(
        value=0,
        bgcolor=config.SURFACE_ALT,
        color=config.ACCENT_CYAN,
        bar_height=4,
        border_radius=0,
        visible=False,
    )
    progress_label = ft.Text("", size=11, color=config.ACCENT_CYAN, visible=False)

    status_banner_text = ft.Text("", size=12, color=config.TEXT_MUTED, expand=True)
    status_banner = ft.Container(
        content=ft.Row([status_banner_text], spacing=8),
        bgcolor=config.SURFACE_ALT,
        border_radius=0,
        border=ft.Border(left=ft.BorderSide(4, config.BORDER)),
        padding=12,
        visible=False,
    )

    def set_banner(message: str, kind: str = "info"):
        colors = {
            "info": config.TEXT_MUTED,
            "warning": config.ACCENT_YELLOW,
            "error": config.ACCENT_RED,
            "success": config.ACCENT_CYAN,
        }
        color = colors.get(kind, colors["info"])
        status_banner_text.value = message
        status_banner_text.color = color
        status_banner.border = ft.Border(left=ft.BorderSide(4, color))
        status_banner.visible = True
        page.update()

    results_column = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO)
    results_container = ft.Container(
        content=results_column,
        bgcolor=config.SURFACE,
        border=ft.Border.all(1, config.BORDER),
        border_radius=0,
        padding=14,
        margin=ft.Margin(28, 12, 28, 0),
        visible=False,
        height=180,
    )
    # ---------------------------------------------------------------
    # FFmpeg Dependency verification
    # ---------------------------------------------------------------
    ffmpeg_installed = shutil.which("ffmpeg") is not None
    if not ffmpeg_installed:
        set_banner("FFmpeg NOT DETECTED IN SYSTEM PATH.", "error")
    #----------------------------------------------------------------
    # UI UPDATES
    #----------------------------------------------------------------
    def make_result_row(task_id: str, display_text: str) -> ft.Row:
        label = display_text if len(display_text) < 55 else display_text[:52] + "..."
        text = ft.Text(f"[ STANDBY ] {label}", size=11, color=config.TEXT_MUTED, expand=True, no_wrap=True)
        row = ft.Row([text], spacing=8)
        rows_by_url[task_id] = text
        return row

    def update_result_row(task_id: str, kind: str, display_text: str):
        text = rows_by_url[task_id]
        label = display_text if len(display_text) < 55 else display_text[:52] + "..."
        if kind == "running": text.value, text.color = f"[ EXTRACT ] {label}", config.ACCENT_CYAN
        elif kind == "success": text.value, text.color = f"[ SAVED ] {label}", config.TEXT_PRIMARY
        elif kind == "error": text.value, text.color = f"[ FAILURE ] {label}", config.ACCENT_RED
        page.update()

    def set_ui_locked(locked: bool):
        btn_start.disabled = locked
        btn_add_link.disabled = locked
        for row in link_rows_container.controls:
            for control in row.controls: control.disabled = locked
        for c in folder_card.content.controls: c.disabled = locked
        page.update()


    def start_download(e):
        tasks = []
        
        for i, row in enumerate(link_rows_container.controls):
            url = row.data["url"].value.strip()
            start_str = row.data["start"].value.strip()
            end_str = row.data["end"].value.strip()
            
            if config.YOUTUBE_REGEX.match(url):
                start_sec = engine.parse_timecode(start_str)
                end_sec = engine.parse_timecode(end_str)

                if start_sec == "ERROR" or end_sec == "ERROR":
                    set_banner(f"ERR_03: INVALID TIMECODE FORMAT AT ROW {i+1} (MAX 59s)", "error")
                    return
                
                tag = "[FULL_VERSION]"
                if start_sec is not None or end_sec is not None:
                                    s_tag = start_str if start_sec is not None else "00:00"
                                    e_tag = end_str if end_sec is not None else "END"
                                    tag = f"[{s_tag}-{e_tag}]"
                    
                tasks.append({
                    "id": f"task_{i}",
                    "url": url, 
                    "start": start_sec, 
                    "end": end_sec, 
                    "tag": tag
                })

        if not tasks:
            set_banner("No valid URLs entered.", "error")
            return

        if not folder_path["value"]:
            set_banner("No output folder selected.", "error")
            return

        results_column.controls.clear()
        rows_by_url.clear()
        
        for task in tasks:
            display_str = f"{task['tag']} {task['url']}"
            results_column.controls.append(make_result_row(task['id'], display_str))
            
        results_container.visible = True

        progress_bar.value = 0
        progress_bar.visible = True
        progress_label.visible = True
        progress_label.value = f"0 / {len(tasks)}"
        set_banner("VERIFYING CONNECTION...", "warning")
        page.update()
        
        if not engine.check_connection():
            set_banner("CRITICAL: NO DATALINK CONNECTION. ABORTING.", "error")
            return
        set_banner("Starting downloads...", "warning")
        set_ui_locked(True)
        page.update()
        
        page.run_thread(engine.execute_downloads, tasks, folder_path["value"],page,progress_bar,progress_label,update_result_row,set_banner,set_ui_locked)
    
    #----------------------------------------------------------
    # Action Button
    #----------------------------------------------------------

    btn_start = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.BOLT if ffmpeg_installed else ft.Icons.WARNING_AMBER_ROUNDED, color=config.BG, size=20), 
                    ft.Text("DOWNLOAD" if ffmpeg_installed else "MISSING DEPENDENCY", size=15)
                ], 
                alignment=ft.MainAxisAlignment.CENTER, 
                spacing=8
            ),
            on_click=start_download,
            disabled=not ffmpeg_installed,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: config.ACCENT_CYAN if ffmpeg_installed else config.SURFACE_ALT, ft.ControlState.HOVERED: config.ACCENT_CYAN}, 
                color=config.BG if ffmpeg_installed else config.TEXT_MUTED, 
                shape=ft.RoundedRectangleBorder(radius=0), 
                padding=ft.Padding(0, 18, 0, 18), 
                elevation=0
            ),
            width=700 - 56,
        )

    action_zone = ft.Container(
        content=ft.Column(
            [
                btn_start,
                ft.Container(height=10),
                progress_bar,
                ft.Container(height=4),
                progress_label,
                ft.Container(height=10),
                status_banner,
            ],
            spacing=0,
        ),
        margin=ft.Margin(28, 0, 28, 20),
    )

    # ---------------------------------------------------------------
    # Assembly
    # ---------------------------------------------------------------
    page.add(
        ft.Column(
            [
                header,
                links_card,
                folder_card,
                action_zone,
                results_container,
            ],
            spacing=0,
            scroll=ft.ScrollMode.AUTO,
        )
    )

if __name__ == "__main__":
    ft.app(target=main, assets_dir="assets")
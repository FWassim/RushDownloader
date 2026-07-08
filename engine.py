import os
import socket
import random
import time
import yt_dlp
import config
import re
from plyer import notification

#-------------------------------------------------------
# Checking network connection
#------------------------------------------------------
def check_connection():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3)
        return True
    except OSError:
        return False
    
#-------------------------------------------------------
# Send Notifications
#-------------------------------------------------------
def send_desktop_notification(title, message):
    notification.notify(
        title=title,
        message=message,
        app_name="YT Batch Downloader",
        timeout=10
    )
#-------------------------------------------------------
#Parsing timecode 
#-------------------------------------------------------
STRICT_TIME_REGEX = re.compile(r"^([0-9]{1,2}:)?[0-5]?[0-9]:[0-5]?[0-9]$|^[0-5]?[0-9]$")
def parse_timecode(t_str):
    if not t_str: return None
    t_str = t_str.strip()
    if not STRICT_TIME_REGEX.match(t_str):
        return "ERROR"
    try:
        parts = t_str.strip().split(':')
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return int(parts[0])
    except:
        return "ERROR"
#-------------------------------------------------------
#Executing downloads
#-------------------------------------------------------
def execute_downloads(tasks, directory, page, progress_bar, progress_label, update_row_cb, set_banner_cb, set_ui_locked_cb):
        total = len(tasks)
        done = 0
        failures = []
        last_update = [0.0]

        def progress_hook(d):
                    if d['status'] == 'downloading':
                        current_time = time.time()

                        if current_time - last_update[0] > 0.3:
                            progress_bar.value = None
                            raw_percent = d.get('_percent_str', '0%')
                            clean_percent = re.sub(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])', '', raw_percent).strip()
                            progress_label.value = f"BLOCK {done + 1}/{total} : {clean_percent} (DOWNLOADING...)"
                            page.update()
                            last_update[0] = current_time
                            
                    elif d['status'] == 'finished':
                        progress_bar.value = None 
                        progress_label.value = f"BLOCK {done + 1}/{total} : MULTIPLEXING DATA (FFmpeg)..."
                        page.update()
                
        for task in tasks:
            display_str = f"{task['tag']} {task['url']}"
            update_row_cb(task['id'], "running", display_str)
            options = {
                "format": "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]",
                "merge_output_format": "mp4",
                "outtmpl": os.path.join(directory, "%(title)s.%(ext)s"),
                "restrictfilenames": True,
                "noplaylist": True,
                "quiet": True,
                "no_warnings": True,
                "color": "no_color",
                "progress_hooks": [progress_hook],
                "postprocessors": [{
							    "key": "FFmpegVideoConvertor",
							    "preferedformat": "mp4"
                                }]
                        }
            if task['start'] is not None or task['end'] is not None:
                        safe_start = task['start'] if task['start'] is not None else 0
                        safe_end = task['end'] if task['end'] is not None else 999999
                        
                        options['download_ranges'] = yt_dlp.utils.download_range_func(None, [(safe_start, safe_end)])
                        options['force_keyframes_at_cuts'] = True

            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    ydl.download([task['url']])
                update_row_cb(task['id'], "success", display_str)
            except Exception as ex:
                update_row_cb(task['id'], "error", display_str)
                failures.append((task['url'], str(ex)))

            done += 1
            progress_bar.value = done / total
            progress_label.value = f"{done} / {total}"
            page.update()
            
            # Shadowban delay
            if done < total:
                delay = random.uniform(2.5, 5.5)
                progress_bar.color = config.ACCENT_YELLOW 
                progress_label.value = f"BLOCK {done}/{total} : [ BYPASSING SECURITY... WAIT {delay:.1f}s ]"
                page.update()
                time.sleep(delay)
                progress_bar.color = config.ACCENT_CYAN 
                page.update()

        if not failures:
            set_banner_cb("All downloads completed.", "success")
            send_desktop_notification("Download Complete", "All your YouTube clips have been saved.")
        elif len(failures) == total:
            set_banner_cb("All downloads failed.", "error")
        else:
            set_banner_cb(f"{len(failures)} of {total} downloads failed.", "warning")

        set_ui_locked_cb(False)
        progress_bar.value = 1
        page.update()
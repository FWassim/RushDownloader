# Rush Downloader

A desktop batch YouTube downloader built for video editors, designed to eliminate codec compatibility issues in Adobe Premiere Pro. Built with Python and [Flet](https://flet.dev/), powered by `yt-dlp` and FFmpeg.

The interface uses a dark, cyberpunk-inspired visual theme, but functionally this is a straightforward, reliable batch downloading tool.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flet](https://img.shields.io/badge/UI-Flet-informational)
![yt--dlp](https://img.shields.io/badge/Engine-yt--dlp-critical)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## Overview

Rush Downloader batch-downloads YouTube videos and guarantees output files that Adobe Premiere Pro can import without issues. It lets you queue multiple links at once, optionally trim each clip to a specific in/out timecode, and download the whole batch sequentially — with built-in pacing to avoid rate limiting or blocking.

## Problems This Solves

**1. AV1 codec import failures in Premiere Pro**
Modern YouTube videos are frequently served in AV1, a codec Premiere Pro often fails to decode properly. A common symptom is importing a video and getting only the audio track, with no video and no clear error message.

Rush Downloader avoids this entirely by forcing `yt-dlp` to select H.264 (`avc1`) video streams and merging them into a clean `.mp4` container via FFmpeg. The result is guaranteed to be Premiere-compatible.

**2. Rate limiting / paywalls on sequential downloads**
Downloading several videos back-to-back from some tools or services quickly triggers rate limits, blocks, or upsells to a paid tier.

Rush Downloader introduces a randomized delay between each download in the queue to simulate human-like pacing, avoiding detection while remaining completely free and unrestricted.

## Features

- **Forced H.264/MP4 output** for guaranteed Premiere Pro compatibility
- **Batch queue system** add any number of video links, each in its own row
- **Per-clip timecode trimming** optional START/END timecodes (`SS`, `MM:SS`, or `HH:MM:SS`) to download only a segment
- **Smart multi-line paste** paste a list of URLs at once; the app automatically splits them into separate rows
- **Anti-throttle pacing** randomized delay between downloads to avoid rate limits or bans
- **Connection pre-check** verifies network connectivity before starting a batch
- **FFmpeg detection on launch** disables the download button with a clear warning if FFmpeg isn't found in PATH
- **Live progress feed** per-file progress bar, download speed, and status (`STANDBY` → `EXTRACT` → `SAVED`/`FAILURE`)
- **Desktop notifications** native OS notification when the batch completes
- **Custom output folder** native OS folder picker
- **Cyberpunk-inspired UI** dark theme, neon accents, monospace font (Fira Code)

## Tech Stack

- **Language:** Python 3.10+
- **UI framework:** Flet (Flutter-based)
- **Download engine:** yt-dlp
- **Muxing/encoding:** FFmpeg (external dependency)
- **Notifications:** Plyer
- **Font:** Fira Code (Local Asset)

### Project Structure

```
assets/     Contains the Fira Code font file
            
Main.py     UI layer : page layout, dynamic link rows, folder picker,
            progress display, input validation, event wiring
engine.py   Core logic : connection check, timecode parsing,
            yt-dlp execution, throttle delay, desktop notifications
config.py   Design tokens : color palette, fonts, regex constants
```

The UI never touches the download logic directly; it delegates to `engine.py` through callbacks (`update_row_cb`, `set_banner_cb`, `set_ui_locked_cb`, `clear_ui_cb`), which run on a background thread (`page.run_thread`) so the interface stays responsive during large batches.

## Requirements

- Python ≥ 3.10
- [FFmpeg](https://ffmpeg.org/download.html) installed and available in your system PATH
  (the app detects its absence on launch and disables the download button until resolved)

### Python dependencies

```
flet
yt-dlp
plyer
```

## Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/rush-downloader.git
cd rush-downloader

# (Recommended) Create a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install flet yt-dlp plyer

# Verify FFmpeg is installed and in PATH
ffmpeg -version

# Run the app
python Main.py
```

## Usage

1. Paste a YouTube URL into the first input row. Pasting multiple links at once (one per line) automatically creates additional rows.
2. Optionally set a START and/or END timecode per video to download only a specific segment.
3. Click **Browse** to select your output folder.
4. Click **Download**.
5. Monitor progress through the live status feed:
   - `STANDBY` queued, not started
   - `EXTRACT` currently downloading/muxing
   - `SAVED` completed, ready to import into Premiere
   - `FAILURE` an error occurred (see status banner for details)
6. Receive a desktop notification once the batch is complete.

## Why H.264 Specifically?

`yt-dlp` is configured with the following format selector:

```python
"format": "bestvideo[ext=mp4][vcodec^=avc1]+bestaudio[ext=m4a]/best[ext=mp4]"
```

This targets H.264 (`avc1`) video streams and `m4a` audio specifically, merging them into `.mp4` via FFmpeg's `FFmpegVideoConvertor` postprocessor. This avoids AV1 entirely and produces footage that imports cleanly into Premiere Pro without re-encoding.

## Roadmap

- [ ] Playlist support (batch-expand a single playlist URL)
- [ ] Audio-only extraction mode
- [ ] Configurable resolution/bitrate presets
- [ ] Persistent download history / log export
- [ ] Cross-platform packaged builds (Windows `.exe` / macOS `.app`)

## Disclaimer

This tool is intended for downloading content you own the rights to, or that is otherwise permitted for offline use (e.g. royalty-free footage, your own uploads, Creative Commons content). Respect YouTube's Terms of Service and applicable copyright law in your jurisdiction.

## License

Distributed under the MIT License. See `LICENSE` for details.
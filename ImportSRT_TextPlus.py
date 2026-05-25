# -*- coding: utf-8 -*-
"""
DaVinci Resolve internal script: Import SRT as Text+ clips.

Run from Resolve:
  Workspace > Scripts > Edit > ImportSRT_TextPlus_v6

This version:
  - Reads an SRT file.
  - Inserts Text+ clips using Mark In/Out so each clip has the SRT duration.
  - Uses relative Mark In/Out frames for Resolve 20 timeline start offsets.
  - Tries Japanese-capable fonts to avoid tofu/square glyphs.

Tip:
  Before running, target/select the video track where you want the Text+ clips
  to be inserted. In Resolve, Text+ insertion follows the current edit target.
"""

from __future__ import print_function

import os
import re
import traceback


DEFAULT_SRT_PATH = ""

PREFERRED_FONTS = [
    "Yu Gothic",
    "Yu Gothic UI",
    "Meiryo",
    "MS Gothic",
    "Noto Sans CJK JP",
    "Noto Sans JP",
    "Source Han Sans JP",
]

SRT_TIME_RE = re.compile(
    r"^\s*(\d{1,2}):(\d{2}):(\d{2}),(\d{3})\s*-->\s*"
    r"(\d{1,2}):(\d{2}):(\d{2}),(\d{3})"
)


def desktop_path(filename):
    home = os.path.expanduser("~")
    desktop = os.path.join(home, "Desktop")
    if not os.path.isdir(desktop):
        desktop = home
    return os.path.join(desktop, filename)


LOG_PATH = desktop_path("resolve_srt_textplus_import_log.txt")


def log(message):
    try:
        with open(LOG_PATH, "a") as f:
            f.write(str(message) + "\n")
    except Exception:
        pass
    print(message)


def get_resolve():
    if "resolve" in globals():
        return globals()["resolve"]
    try:
        import DaVinciResolveScript as dvr_script
        return dvr_script.scriptapp("Resolve")
    except Exception as exc:
        log("DaVinciResolveScript import failed: {0}".format(exc))
        return None


def ask_file_path(resolve_app):
    if DEFAULT_SRT_PATH:
        return DEFAULT_SRT_PATH

    try:
        fusion = resolve_app.Fusion()
        if fusion:
            path = fusion.RequestFile(
                "Select SRT file",
                "",
                {
                    "FReqB_Saving": False,
                    "FReqB_SeqGather": False,
                    "FReqS_Filter": "SRT files (*.srt)|*.srt|All files (*.*)|*.*",
                },
            )
            if path:
                return path
    except Exception as exc:
        log("Resolve/Fusion file picker failed: {0}".format(exc))

    try:
        import Tkinter as tk
        import tkFileDialog as filedialog
    except Exception:
        try:
            import tkinter as tk
            from tkinter import filedialog
        except Exception as exc:
            log("Tk file picker unavailable: {0}".format(exc))
            return ""

    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        path = filedialog.askopenfilename(
            title="Select SRT file",
            filetypes=[("SRT subtitles", "*.srt"), ("All files", "*.*")],
        )
        root.destroy()
        return path
    except Exception as exc:
        log("Tk file picker failed: {0}".format(exc))
        return ""


def read_text_file(path):
    encodings = ["utf-8-sig", "utf-8", "cp932", "shift_jis"]
    last_error = None
    for encoding in encodings:
        try:
            with open(path, "r", encoding=encoding) as f:
                return f.read()
        except TypeError:
            try:
                import codecs
                with codecs.open(path, "r", encoding=encoding) as f:
                    return f.read()
            except Exception as exc:
                last_error = exc
        except Exception as exc:
            last_error = exc
    raise last_error


def srt_time_to_seconds(match, offset):
    return (
        int(match.group(offset + 0)) * 3600
        + int(match.group(offset + 1)) * 60
        + int(match.group(offset + 2))
        + int(match.group(offset + 3)) / 1000.0
    )


def parse_srt(data):
    data = data.replace("\r\n", "\n").replace("\r", "\n")
    blocks = re.split(r"\n\s*\n", data.strip())
    subtitles = []

    for block in blocks:
        lines = [line.strip("\ufeff") for line in block.split("\n")]
        lines = [line for line in lines if line.strip()]
        if not lines:
            continue

        time_match = None
        time_index = None
        for index, line in enumerate(lines):
            time_match = SRT_TIME_RE.match(line)
            if time_match:
                time_index = index
                break

        if time_index is None or time_match is None:
            continue

        text = "\n".join(lines[time_index + 1 :]).strip()
        if text:
            subtitles.append(
                {
                    "start": srt_time_to_seconds(time_match, 1),
                    "end": srt_time_to_seconds(time_match, 5),
                    "text": text,
                }
            )

    return subtitles


def seconds_to_frame(seconds, fps):
    return int(round(seconds * fps))


def frame_to_timecode(frame, fps):
    rounded_fps = int(round(fps)) or 24
    hours = frame // (rounded_fps * 3600)
    frame %= rounded_fps * 3600
    minutes = frame // (rounded_fps * 60)
    frame %= rounded_fps * 60
    seconds = frame // rounded_fps
    frames = frame % rounded_fps
    return "{0:02d}:{1:02d}:{2:02d}:{3:02d}".format(hours, minutes, seconds, frames)


def get_timeline_fps(timeline):
    fps = timeline.GetSetting("timelineFrameRate")
    try:
        return float(str(fps).replace(",", "."))
    except Exception:
        return 24.0


def set_mark_range(timeline, relative_start_frame, relative_end_frame):
    mark_out = max(relative_start_frame + 1, relative_end_frame - 1)

    try:
        result = timeline.SetMarkInOut(relative_start_frame, mark_out, "video")
        log("SetMarkInOut video relative {0}-{1}: {2}".format(relative_start_frame, mark_out, result))
        if result:
            return True
    except Exception as exc:
        log("SetMarkInOut video failed: {0}".format(exc))

    try:
        result = timeline.SetMarkInOut(relative_start_frame, mark_out)
        log("SetMarkInOut all relative {0}-{1}: {2}".format(relative_start_frame, mark_out, result))
        return bool(result)
    except Exception as exc:
        log("SetMarkInOut all failed: {0}".format(exc))
        return False


def clear_mark_range(timeline):
    for args in (("video",), tuple()):
        try:
            result = timeline.ClearMarkInOut(*args)
            log("ClearMarkInOut{0}: {1}".format(args, result))
            return
        except Exception:
            pass


def set_first_working_font(tool):
    for font_name in PREFERRED_FONTS:
        try:
            tool.SetInput("Font", font_name)
            log("Tried font: {0}".format(font_name))
            return font_name
        except Exception:
            pass
    return None


def set_text_plus_content(clip, text):
    try:
        comp = clip.GetFusionCompByIndex(1)
        if not comp:
            log("Fusion comp not found on created title.")
            return False

        tools = comp.GetToolList(False)
        for tool in tools.values():
            attrs = tool.GetAttrs()
            tool_id = attrs.get("TOOLS_RegID", "")
            if tool_id in ("TextPlus", "Text3D") or "Text" in str(tool_id):
                tool.SetInput("StyledText", text)
                font_name = set_first_working_font(tool)
                try:
                    tool.SetInput("Style", "Regular")
                except Exception:
                    pass
                try:
                    tool.SetInput("Size", 0.08)
                except Exception:
                    pass
                log("Set StyledText. Font request: {0}".format(font_name or "unchanged"))
                return True

        log("Text tool not found inside Fusion comp.")
    except Exception as exc:
        log("Setting Text+ content failed: {0}".format(exc))
    return False


def insert_text_plus_title(timeline, timeline_start_frame, rel_start, rel_end, fps, text):
    visible_timecode = frame_to_timecode(timeline_start_frame + rel_start, fps)

    try:
        timeline.SetCurrentTimecode(visible_timecode)
        log("Set playhead visible timecode: {0}".format(visible_timecode))
    except Exception as exc:
        log("SetCurrentTimecode failed: {0}".format(exc))

    set_mark_range(timeline, rel_start, rel_end)

    clip = None
    used_name = None
    for title_name in ("Text+", "Text Plus", "Text"):
        try:
            clip = timeline.InsertFusionTitleIntoTimeline(title_name)
            if clip:
                used_name = title_name
                break
        except Exception as exc:
            log("InsertFusionTitleIntoTimeline({0}) failed: {1}".format(title_name, exc))

    if not clip:
        log("Could not insert a Fusion title.")
        return False

    log("Inserted Fusion title: {0}".format(used_name))
    try:
        log("Created clip start/end/duration: {0}/{1}/{2}".format(
            clip.GetStart(), clip.GetEnd(), clip.GetDuration()
        ))
    except Exception as exc:
        log("Could not read created clip timing: {0}".format(exc))

    set_text_plus_content(clip, text)
    return True


def main():
    try:
        if os.path.exists(LOG_PATH):
            os.remove(LOG_PATH)
    except Exception:
        pass

    log("SRT Text+ import v6 started.")
    log("Log file: {0}".format(LOG_PATH))

    resolve_app = get_resolve()
    if not resolve_app:
        log("Resolve object was not found.")
        return

    project_manager = resolve_app.GetProjectManager()
    project = project_manager.GetCurrentProject() if project_manager else None
    if not project:
        log("No current project.")
        return

    timeline = project.GetCurrentTimeline()
    if not timeline:
        log("No current timeline.")
        return

    srt_path = ask_file_path(resolve_app)
    if not srt_path:
        log("Canceled or no file picker appeared.")
        log("Set DEFAULT_SRT_PATH at the top of ImportSRT_TextPlus_v6.py and run again.")
        return

    if not os.path.exists(srt_path):
        log("SRT file does not exist: {0}".format(srt_path))
        return

    log("SRT file: {0}".format(srt_path))

    subtitles = parse_srt(read_text_file(srt_path))
    log("Subtitle count: {0}".format(len(subtitles)))
    if not subtitles:
        return

    fps = get_timeline_fps(timeline)
    timeline_start = int(timeline.GetStartFrame() or 0)
    log("Timeline FPS: {0}".format(fps))
    log("Timeline start frame: {0}".format(timeline_start))

    created = 0
    for subtitle in subtitles:
        rel_start = seconds_to_frame(subtitle["start"], fps)
        rel_end = seconds_to_frame(subtitle["end"], fps)
        log("Subtitle relative frames: {0}-{1}".format(rel_start, rel_end))
        if insert_text_plus_title(timeline, timeline_start, rel_start, rel_end, fps, subtitle["text"]):
            created += 1

    clear_mark_range(timeline)
    log("Created clips: {0}".format(created))
    log("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log("Unexpected error:")
        log(traceback.format_exc())

# resolve-srt-to-textplus

This is a DaVinci Resolve script that creates Text+ clips on the current timeline from an SRT subtitle file.

It is designed to run from DaVinci Resolve's internal `Workspace > Scripts` menu, instead of being launched from an external terminal. This makes it easier to use with the free version of DaVinci Resolve.

## Tested Environment

- Windows
- DaVinci Resolve 20 Free
- Python script executed from Resolve's internal Scripts menu

## Features

- Reads an SRT subtitle file
- Creates Text+ clips according to the SRT start and end times
- Sets Japanese-capable fonts such as `Yu Gothic`
- Handles timelines that start at `01:00:00:00`

## Installation

Copy `ImportSRT_TextPlus.py` to the following folder.

Windows:

`%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`

Example:

`C:\Users\YourName\AppData\Roaming\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Edit\`

Create the `Edit` folder if it does not already exist.

## Usage

1. Open a project in DaVinci Resolve
2. Create an empty timeline
3. Run `Workspace > Scripts > Edit > ImportSRT_TextPlus`
4. Select an SRT file
5. Text+ subtitle clips will be created
6. Add background video, images, and audio afterward
7. Adjust track order if needed

## Recommended Workflow

Depending on your Resolve environment, the scripting API may not fully control which video track receives the inserted Text+ clips.

For that reason, this workflow is recommended:

1. Start with an empty timeline
2. Run the script to create Text+ subtitle clips from the SRT file
3. Add background media afterward
4. Adjust track order so the background is below the subtitles

## Notes

- Tested on DaVinci Resolve 20 Free for Windows.
- macOS and other Resolve versions are not tested.
- If Japanese text appears as square boxes, change the Text+ font to `Yu Gothic`, `Meiryo`, or another Japanese-capable font.
- If you run the script on a timeline that already contains media, Text+ clips may be inserted into an unexpected track.

## License

MIT License


# MP4 and SRT Mixer Script

This Python script allows you to mix subtitles (SRT) with MP4 video files using FFmpeg. The script can process both single MP4 and SRT files or an entire folder of episodes (TV series). It supports custom output file names, manual SRT encoding specification, and automatic overwriting of existing output files.

## Features

- **Mix MP4 video with SRT subtitles** using FFmpeg.
- **Process single files** or **batch process** a folder of TV episodes.
- Customizable output file name.
- Manually specify SRT file encoding (e.g., `UTF-8`, `ISO-8859-1`).
- Automatically overwrite existing output files with `--overwrite`.
- Verbose and silent modes for debugging or quiet operation.

## Requirements

### Operating Systems

- macOS
- Windows

### Python

Ensure that Python 3.x is installed on your system. You can download it from [here](https://www.python.org/downloads/).

### Dependencies

The script uses the following Python libraries:
- `ffmpeg-python`
- `chardet`
- `colorama`

A `requirements.txt` file is provided for easy installation of these dependencies.

## Installation

### macOS

1. **Install Python 3.x**:
   Open your terminal and run:
   ```bash
   brew install python
   ```

2. **Install FFmpeg**:
   Install FFmpeg using Homebrew:
   ```bash
   brew install ffmpeg
   ```

3. **Clone or download the script**.

4. **Install Python dependencies**:
   Inside the project directory, run:
   ```bash
   pip install -r requirements.txt
   ```

### Windows

1. **Install Python 3.x**:
   Download and install Python from [here](https://www.python.org/downloads/).

2. **Install FFmpeg**:
   - Download FFmpeg from the [official website](https://ffmpeg.org/download.html).
   - Add FFmpeg to the system PATH (see instructions [here](https://www.geeksforgeeks.org/how-to-install-ffmpeg-on-windows/)).

3. **Clone or download the script**.

4. **Install Python dependencies**:
   Inside the project directory, run:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Command-line Arguments

```bash
python mix_mp4_srt.py <mp4_file> <srt_file> [options]
```

### Options

- `--output <output_file>`: Specify a custom output file name.
- `--encoding <encoding>`: Specify the encoding of the SRT file (e.g., `UTF-8`, `ISO-8859-1`).
- `--overwrite`: Automatically delete any existing output file without prompting.
- `--verbose`: Display detailed logs for debugging purposes.
- `--silent`: Suppress all output except for errors.

### Examples

1. **Basic Single File Mixing**:
   ```bash
   python mix_mp4_srt.py Meet-Joe-Black.mp4 Meet-Joe-Black.srt
   ```

2. **Custom Output File**:
   ```bash
   python mix_mp4_srt.py Meet-Joe-Black.mp4 Meet-Joe-Black.srt --output Joe-Black-Final.mp4
   ```

3. **Process TV Series Folder**:
   ```bash
   python mix_mp4_srt.py --tv /path/to/tv/series/folder
   ```

4. **Verbose Mode**:
   ```bash
   python mix_mp4_srt.py Meet-Joe-Black.mp4 Meet-Joe-Black.srt --verbose
   ```

5. **Custom Encoding**:
   ```bash
   python mix_mp4_srt.py Meet-Joe-Black.mp4 Meet-Joe-Black.srt --encoding ISO-8859-1
   ```

6. **Overwrite Existing Files**:
   ```bash
   python mix_mp4_srt.py Meet-Joe-Black.mp4 Meet-Joe-Black.srt --overwrite
   ```
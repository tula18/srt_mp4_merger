import chardet
import ffmpeg
import os
import re
import time
import sys
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

# Global flags for verbosity and silent mode
VERBOSE = False
SILENT = False

def log(message, level="info", end="\n"):
    """Log messages based on verbosity and silent mode."""
    if SILENT:
        return

    color = {
        "info": Fore.CYAN,
        "warn": Fore.YELLOW,
        "error": Fore.RED,
        "success": Fore.GREEN
    }.get(level, Fore.CYAN)
    
    if VERBOSE or level in ["error", "success"]:
        print(color + message + Style.RESET_ALL, end=end)
        
def ensure_folder_exists(folder_path):
    """Ensure that the output folder exists, creating it if necessary."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        log(f"Created output folder: {folder_path}", level="success")
    else:
        log(f"Output folder already exists: {folder_path}", level="info")

def detect_encoding(file_path, manual_encoding=None):
    """Detect the encoding of the SRT file using chardet or a manually specified encoding."""
    try:
        if manual_encoding:
            return manual_encoding
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            return result['encoding']
    except Exception as e:
        log(f"Error detecting encoding for {file_path}: {e}", level="error")
        raise

def get_video_metadata(video_file):
    """Retrieve video metadata such as duration, resolution, frame rate, codec, and bitrate."""
    try:
        probe = ffmpeg.probe(video_file)
        format_info = probe['format']
        video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
        audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

        # Duration, resolution, frame rate
        duration = float(format_info['duration'])
        resolution = f"{video_stream['width']}x{video_stream['height']}"
        frame_rate = eval(video_stream['r_frame_rate'])  # Convert frame rate from a string to a float

        # Codec and bitrate
        video_codec = video_stream['codec_name']
        video_bitrate = int(video_stream.get('bit_rate', 0)) / 1000  # Convert to kbps if available

        audio_codec = audio_stream['codec_name'] if audio_stream else 'Unknown'
        audio_bitrate = int(audio_stream.get('bit_rate', 0)) / 1000 if audio_stream else 0
        audio_channels = audio_stream['channels'] if audio_stream else 'Unknown'

        return {
            "duration": duration,
            "resolution": resolution,
            "frame_rate": frame_rate,
            "video_codec": video_codec,
            "video_bitrate": video_bitrate,
            "audio_codec": audio_codec,
            "audio_bitrate": audio_bitrate,
            "audio_channels": audio_channels
        }
    except Exception as e:
        log(f"Error getting video metadata for {video_file}: {e}", level="error")
        raise

def count_subtitles(srt_file):
    """Count the number of subtitles in the SRT file."""
    try:
        with open(srt_file, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for line in f if line.strip() and line.strip().isdigit())
    except Exception as e:
        log(f"Error counting subtitles in {srt_file}: {e}", level="error")
        raise

def convert_to_utf8_if_needed(input_file, manual_encoding=None):
    """Convert the SRT file to UTF-8 only if it's not already in UTF-8."""
    try:
        utf8_srt_file = "utf8_" + os.path.basename(input_file)

        # Check if the UTF-8 SRT file already exists
        if os.path.exists(utf8_srt_file):
            log(f"UTF-8 version of the SRT file already exists: {utf8_srt_file}")
            return utf8_srt_file

        encoding = detect_encoding(input_file, manual_encoding)
        
        if encoding.lower() == 'utf-8':
            log(f"No conversion needed. SRT is already in UTF-8 encoding.")
            return input_file  # Return the same file if it's already UTF-8

        with open(input_file, 'r', encoding=encoding, errors='ignore') as f:
            text = f.read()

        with open(utf8_srt_file, 'w', encoding='UTF-8') as f:
            f.write(text)

        log(f"File converted to UTF-8 and saved as {utf8_srt_file}", level="success")
        return utf8_srt_file
    except Exception as e:
        log(f"Error converting {input_file} to UTF-8: {e}", level="error")
        raise

def format_seconds(seconds):
    """Convert seconds into HH:MM:SS format."""
    hours, remainder = divmod(int(seconds), 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def parse_ffmpeg_progress(line, total_duration, start_time):
    """Parse FFmpeg progress and calculate both video time remaining and estimated runtime remaining."""
    time_match = re.search(r'time=(\d+:\d+:\d+)', line)
    if time_match:
        # Convert the current video processing time to seconds
        current_time = time.strptime(time_match.group(1), '%H:%M:%S')
        seconds_elapsed = current_time.tm_hour * 3600 + current_time.tm_min * 60 + current_time.tm_sec
        
        # Calculate video time remaining
        video_time_remaining = total_duration - seconds_elapsed
        
        # Calculate total runtime remaining
        elapsed_real_time = time.time() - start_time
        if seconds_elapsed > 0:
            runtime_remaining = (elapsed_real_time / seconds_elapsed) * (total_duration - seconds_elapsed)
        else:
            runtime_remaining = 0  # Avoid division by zero if the process just started

        formatted_video_time_remaining = format_seconds(video_time_remaining)
        formatted_runtime_remaining = format_seconds(runtime_remaining)

        log(f"Video Progress: {time_match.group(1)} | Video Time Remaining: {formatted_video_time_remaining} | Estimated Runtime Remaining: {formatted_runtime_remaining}", end="\r", level="success")

def display_file_info(mp4_file, srt_file, video_metadata, subtitle_count, srt_encoding):
    """Display information about the video and subtitle files."""
    log(f"\n--- MP4 File Information ---\n"
        f"File: {mp4_file}\n"
        f"Duration: {format_seconds(video_metadata['duration'])}\n"
        f"Resolution: {video_metadata['resolution']}\n"
        f"Frame Rate: {video_metadata['frame_rate']:.2f} fps\n"
        f"Video Codec: {video_metadata['video_codec']}\n"
        f"Video Bitrate: {video_metadata['video_bitrate']:.2f} kbps\n"
        f"Audio Codec: {video_metadata['audio_codec']}\n"
        f"Audio Bitrate: {video_metadata['audio_bitrate']:.2f} kbps\n"
        f"Audio Channels: {video_metadata['audio_channels']}", level="info")
    
    log(f"\n--- SRT File Information ---\n"
        f"File: {srt_file}\n"
        f"Encoding: {srt_encoding}\n"
        f"Number of Subtitles: {subtitle_count}", level="info")

def handle_interrupt(output_file, auto_delete=False):
    """Handle KeyboardInterrupt and ask if the user wants to delete the output file."""
    log(f"\n\nProcess interrupted!", level="error")
    if os.path.exists(output_file):
        if auto_delete:
            os.remove(output_file)
            log(f"Deleted partial output file: {output_file}", level="success")
        else:
            try:
                user_choice = input(f"The output file {output_file} exists. Do you want to delete it? (y/n): ")
                if user_choice.lower() == 'y':
                    os.remove(output_file)
                    log(f"Deleted partial output file: {output_file}", level="success")
                else:
                    log(f"Partial output file kept: {output_file}", level="warn")
            except KeyboardInterrupt:
                log(f"\n\nProcess interrupted!", level="error")
                os.remove(output_file)
                log(f"Deleted partial output file: {output_file}", level="success")

def mix_mp4_srt(mp4_file, srt_file, folder_path, output_folder="output", output_file=None, auto_delete=False, manual_encoding=None):
    """Mix the MP4 video with SRT subtitles using FFmpeg with options for custom output, manual encoding, and file overwrite."""
    try:
        # Convert the SRT file to UTF-8 if it's not already
        utf8_srt_file = convert_to_utf8_if_needed(srt_file, manual_encoding)
        
        # Validate file extension
        filename, file_extension = os.path.splitext(mp4_file)
        
        if file_extension.lower() != ".mp4":
            log(f"File format: {file_extension} not supported", level="error")
            raise TypeError(f"File format: {file_extension} not supported")

        output_folder_final = os.path.join(folder_path, output_folder)
        print(output_folder_final)
        # Create output folder if it doesn't exist
        ensure_folder_exists(output_folder_final)

        # Prepare output file path
        if not output_file:
            output_file = f"{filename}-with_subtitles{file_extension}"
        output_file = os.path.join(output_folder_final, os.path.basename(output_file))  # Correct the output file path
            
        log(f"Output file: {output_file}", level="info")

        # Check if output MP4 file exists and prompt for deletion if not in auto-delete mode
        if os.path.exists(output_file):
            if auto_delete:
                os.remove(output_file)
                log(f"Deleted existing output file: {output_file}", level="success")
            else:
                try:
                    user_choice = input(f"The output file {output_file} exists. Do you want to delete it? (y/n): ")
                    if user_choice.lower() == 'y':
                        os.remove(output_file)
                        log(f"Deleted partial output file: {output_file}", level="success")
                    else:
                        log(f"Partial output file kept: {output_file}", level="warn")
                except KeyboardInterrupt:
                    log(f"\n\nProcess interrupted!", level="error")
                    os.remove(output_file)
                    log(f"Deleted partial output file: {output_file}", level="success")

        # Get the video metadata
        video_metadata = get_video_metadata(mp4_file)

        # Get encoding of SRT file and count subtitles
        srt_encoding = detect_encoding(srt_file, manual_encoding)
        subtitle_count = count_subtitles(utf8_srt_file)

        # Display file info before starting the progress
        display_file_info(mp4_file, srt_file, video_metadata, subtitle_count, srt_encoding)

        # Start time for runtime estimation
        start_time = time.time()

        # Prepare FFmpeg command with progress reporting
        ffmpeg_cmd = (
            ffmpeg
            .input(mp4_file)
            .output(output_file, vf=f"subtitles={utf8_srt_file}")
            .global_args('-progress', 'pipe:1')  # Output progress to stdout
            .global_args('-loglevel', 'error')   # Suppress extra logs
        )

        # Run FFmpeg and capture progress
        process = ffmpeg_cmd.run_async(pipe_stdout=True, pipe_stderr=True)

        # Parse FFmpeg's progress
        while True:
            output = process.stdout.readline().decode('utf-8')
            if output == '' and process.poll() is not None:
                break
            if output:
                parse_ffmpeg_progress(output, video_metadata['duration'], start_time)
        
        log(f"MP4 and SRT have been mixed and saved to {output_file}", level="success")
    except KeyboardInterrupt:
        handle_interrupt(output_file, auto_delete)
    except FileNotFoundError as fnf_error:
        log(f"File not found: {fnf_error}", level="error")
    except TypeError as te:
        log(f"File type error: {te}", level="error")
    except Exception as e:
        log(f"An unexpected error occurred: {e}", level="error")

def process_tv_series(folder_path, output_folder, auto_delete=False, manual_encoding=None):
    """Process multiple MP4 and SRT files in a folder."""
    try:
        # Get a list of MP4 and SRT files in the folder
        mp4_files = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
        srt_files = [f for f in os.listdir(folder_path) if f.endswith('.srt')]

        if not mp4_files or not srt_files:
            log(f"No MP4 or SRT files found in {folder_path}.", level="error")
            return

        for mp4_file in mp4_files:
            # Try to find a matching SRT file based on episode/filename
            base_name = os.path.splitext(mp4_file)[0]
            matching_srt = next((srt for srt in srt_files if base_name in srt), None)

            if matching_srt:
                log(f"\nProcessing {mp4_file} with {matching_srt}...\n", level="info")
                mp4_path = os.path.join(folder_path, mp4_file)
                srt_path = os.path.join(folder_path, matching_srt)
                mix_mp4_srt(mp4_path, srt_path, folder_path=folder_path, output_folder=output_folder, auto_delete=auto_delete, manual_encoding=manual_encoding)
            else:
                log(f"No matching SRT file found for {mp4_file}", level="warn")

    except Exception as e:
        log(f"Error processing TV series: {e} {os.getcwd()}", level="error")

# Example usage with sys.argv
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"{Fore.RED}Usage: python mix_mp4_srt.py <mp4_file> <srt_file> [--output <output_file>] [--encoding <encoding>] [--overwrite] [--verbose] [--silent] [--tv <folder_path>]")
        sys.exit(1)

    mp4_file = sys.argv[1]
    srt_file = sys.argv[2]

    # Parsing optional arguments
    output_folder = "output"
    output_file = None
    auto_delete = False
    manual_encoding = None
    folder_path = None
    
    if "--output-folder" in sys.argv:
        output_folder = sys.argv[sys.argv.index("--output-folder") + 1]

    if "--output" in sys.argv:
        output_file = sys.argv[sys.argv.index("--output") + 1]

    if "--overwrite" in sys.argv:
        auto_delete = True

    if "--encoding" in sys.argv:
        manual_encoding = sys.argv[sys.argv.index("--encoding") + 1]

    if "--verbose" in sys.argv:
        VERBOSE = True

    if "--silent" in sys.argv:
        SILENT = True

    try:
        # If --tv is passed, process a folder
        if "--tv" in sys.argv:
            folder_path = sys.argv[sys.argv.index("--tv") + 1]
            process_tv_series(folder_path, output_folder=output_folder, auto_delete=auto_delete, manual_encoding=manual_encoding)
        else:
            # Process a single MP4 and SRT file
            mp4_file = sys.argv[1]
            srt_file = sys.argv[2]
            mix_mp4_srt(mp4_file, srt_file, output_folder=output_folder, output_file=output_file, auto_delete=auto_delete, manual_encoding=manual_encoding)
    except Exception as e:
        log(f"Failed to process files: {e}", level="error")

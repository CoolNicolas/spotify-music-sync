"""Search and save audio from videos you have permission to download."""
from pathlib import Path
import re
import yt_dlp


def clean_filename(value: str) -> str:
    """Produce a portable, safe file stem without private filesystem paths."""
    cleaned = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', value).strip().rstrip('. ')
    return cleaned[:180] or 'untitled'


def search_youtube(query: str) -> str | None:
    """Return the first YouTube search result URL, or None."""
    with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True,
                           'extract_flat': True, 'noplaylist': True}) as ydl:
        results = ydl.extract_info(f'ytsearch1:{query}', download=False)
    entries = (results or {}).get('entries') or []
    if not entries:
        return None
    item = entries[0]
    link = item.get('webpage_url') or item.get('url')
    if link and not link.startswith('http'):
        return f'https://www.youtube.com/watch?v={link}'
    return link


def download_mp3(youtube_url: str, song_name: str, output_folder: Path,
                 ffmpeg_location: str | None = None) -> Path:
    """Create an MP3 and return its path only if it exists."""
    output_folder = Path(output_folder)
    output_folder.mkdir(parents=True, exist_ok=True)
    stem = clean_filename(song_name)
    target = output_folder / f'{stem}.mp3'
    if target.is_file() and target.stat().st_size > 0:
        print(f'⏭️ Already present: {target.name}')
        return target

    options = {
        'format': 'bestaudio/best',
        'outtmpl': str(output_folder / f'{stem}.%(ext)s'),
        'noplaylist': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3', 'preferredquality': '192'}],
    }
    if ffmpeg_location:
        options['ffmpeg_location'] = ffmpeg_location
    with yt_dlp.YoutubeDL(options) as ydl:
        ydl.download([youtube_url])
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError(f'Expected output file was not created: {target}')
    return target

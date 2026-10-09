"""Check Spotify Liked Songs and save only missing, permitted audio locally."""
import json
import os
import re
from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotify_downloader import search_youtube, download_mp3

BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_FOLDER = BASE_DIR / 'downloads'
HISTORY_FILE = BASE_DIR / 'downloaded_songs.json'
CACHE_FILE = BASE_DIR / '.spotify_cache'
AUDIO_EXTENSIONS = {'.mp3', '.m4a', '.flac', '.wav'}


def normalize(value: str) -> str:
    return re.sub(r'[^\w]', '', value.casefold(), flags=re.UNICODE)


def already_present(title: str, artist: str) -> bool:
    """Heuristic filename match; cannot guarantee an exact song/version match."""
    title_key, artist_key = normalize(title), normalize(artist)
    for file in DOWNLOAD_FOLDER.iterdir():
        if file.is_file() and file.suffix.lower() in AUDIO_EXTENSIONS and file.stat().st_size > 0:
            candidate = normalize(file.stem)
            if title_key and artist_key and title_key in candidate and artist_key in candidate:
                return True
    return False


def save_history(ids: set[str]) -> None:
    temp_file = HISTORY_FILE.with_suffix('.json.tmp')
    temp_file.write_text(json.dumps(sorted(ids), ensure_ascii=False, indent=2), encoding='utf-8')
    temp_file.replace(HISTORY_FILE)


def main() -> None:
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise SystemExit('Set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET first. See README.md.')

    DOWNLOAD_FOLDER.mkdir(exist_ok=True)
    if HISTORY_FILE.exists():
        history = set(json.loads(HISTORY_FILE.read_text(encoding='utf-8')))
    else:
        history = set()

    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI', 'http://127.0.0.1:8888/callback'),
        scope='user-library-read',
        cache_path=str(CACHE_FILE),
    ))

    tracks = []
    page = spotify.current_user_saved_tracks(limit=50)
    while True:
        tracks.extend(page['items'])
        if not page['next']:
            break
        page = spotify.next(page)

    print(f'🎵 Found {len(tracks)} Spotify Liked Songs')
    counts = {'downloaded': 0, 'skipped': 0, 'failed': 0}
    failed = []
    for item in tracks:
        track = item.get('track')
        if not track or not track.get('id') or not track.get('artists'):
            continue
        song_id = track['id']
        title, artist = track['name'], track['artists'][0]['name']
        label = f'{title} - {artist}'

        if song_id in history:
            counts['skipped'] += 1
            print(f'⏭️ Skipping tracked song: {label}')
            continue
        if already_present(title, artist):
            history.add(song_id)
            save_history(history)
            counts['skipped'] += 1
            print(f'✅ Already on computer: {label}')
            continue

        try:
            print(f'🔍 Searching: {label}')
            url = search_youtube(label)
            if not url:
                raise RuntimeError('No YouTube search result')
            output = download_mp3(
                url, label, DOWNLOAD_FOLDER,
                ffmpeg_location=os.getenv('FFMPEG_LOCATION') or None,
            )
            history.add(song_id)
            save_history(history)
            counts['downloaded'] += 1
            print(f'✅ Saved: {output.name}')
        except Exception as exc:
            counts['failed'] += 1
            failed.append(f'{label}: {exc}')
            print(f'❌ Failed: {label}: {exc}')

    print('\n========== SYNC COMPLETE ==========')
    print(f"New downloads: {counts['downloaded']}")
    print(f"Skipped: {counts['skipped']}")
    print(f"Failed: {counts['failed']}")
    if failed:
        print('Failed songs (not recorded as downloaded):')
        for failure in failed:
            print(f'  - {failure}')


if __name__ == '__main__':
    main()

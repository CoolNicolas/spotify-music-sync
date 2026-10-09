# Spotify Liked Songs → Local Audio (Python)

A personal Python project that reads your **Spotify Liked Songs**, searches YouTube for a matching video, and uses `yt-dlp` and FFmpeg to save an MP3 **only when you have permission to download that audio**. It attempts to avoid duplicate files using a local filename check and a persistent record of Spotify track IDs.

> **Important:** Spotify Premium does not grant a license to download copyrighted recordings from YouTube. Only use this software with your own recordings, appropriately licensed material, or content for which you have explicit permission. Follow applicable laws and platform terms. This tool is not affiliated with Spotify, YouTube, or Apple.

## Features

- Spotify OAuth authorization (`user-library-read`)
- Reads every page of Liked Songs (50 tracks per Spotify API request)
- Searches YouTube using `yt-dlp` (no `youtube-search-python` dependency)
- Converts permitted audio to MP3 using FFmpeg
- Stores Spotify IDs in `downloaded_songs.json` so completed tracks are skipped
- Checks existing local `.mp3`, `.m4a`, `.flac`, and `.wav` filenames
- Prints failures so they can be retried later

## Requirements

- Python **3.10 or newer**
- Spotify account and an app registered at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard); current Spotify developer API eligibility rules may require Premium for the app owner
- `spotipy` and `yt-dlp` (from `requirements.txt`)
- A working **FFmpeg + FFprobe** installation
- Internet access; optional Deno or another supported JavaScript runtime may be needed by recent `yt-dlp` versions for some YouTube formats

## Installation (Windows PowerShell)

1. Clone or download this repository. Put it in a normal project folder, **not inside `.venv`**.
2. Open PowerShell in the repository directory.
3. Set up dependencies:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

4. Install a working FFmpeg build and confirm:

   ```powershell
   ffmpeg -version
   ffprobe -version
   ```

   If the commands fail or return no output, fix the FFmpeg installation first. With multiple installations, you can point `FFMPEG_LOCATION` to the directory holding **working** `ffmpeg.exe` and `ffprobe.exe`.

5. In Spotify Developer Dashboard, configure an application and add this **redirect URI** exactly:

   `http://127.0.0.1:8888/callback`

6. Set environment variables in the **same PowerShell session**:

   ```powershell
   $env:SPOTIFY_CLIENT_ID = Read-Host 'Spotify client ID'
   $env:SPOTIFY_CLIENT_SECRET = Read-Host 'Spotify client secret'
   # Optional if ffmpeg in PATH is broken or a different build should be used:
   # $env:FFMPEG_LOCATION = 'C:\path\to\working-ffmpeg\bin'
   ```

   `Read-Host` prompts you interactively. These values are only set for the current terminal session; repeat them when opening a new one. **Never paste secrets into Python source or Git commits.** `.env.example` shows the variable names but the scripts do not automatically load `.env` files.

7. Run:

   ```powershell
   python spotify_auth.py
   ```

   Authorize the app through your browser if prompted.

## Where files go

- `downloads/`: output audio files (auto-created, Git-ignored)
- `downloaded_songs.json`: Spotify IDs processed successfully or matched as existing audio (auto-created, Git-ignored)
- `.spotify_cache`: private Spotify OAuth token cache (auto-created, Git-ignored)

**The script never imports songs into Apple Music automatically.** You may import your properly licensed local audio into your chosen media player separately.

## Preventing duplicates: important limitations

On the first run, place existing files in `downloads/` before starting. If their names contain the song title and primary artist, the script usually recognizes them. Otherwise it may make a duplicate. The filename match is approximate and **cannot guarantee correct recordings, editions, or perfect duplicate detection**. The first YouTube search result is not necessarily the correct track; review results and audio before use.

The JSON history records Spotify track IDs and is saved after each successful operation. The script does not re-check whether a history-marked file was later deleted. Remove an individual ID from the JSON if you need to reprocess it. Do not share the history or Spotify cache publicly.

## Troubleshooting

- **`KeyError` for a secret / missing credentials:** Set both environment variables, then rerun the script.
- **`invalid_grant` / expired refresh token:** Delete `.spotify_cache` and authorize again. Do not delete music files.
- **Spotify `403 Premium required`:** Check eligibility and allow time for any subscription changes to propagate.
- **`ffmpeg and ffprobe not found`:** Install FFmpeg and set `FFMPEG_LOCATION` to its executable folder if needed.
- **FFmpeg prints nothing and exits with `-1073741515`:** The installed FFmpeg cannot load a Windows DLL; test a working standalone build instead.
- **YouTube JavaScript-runtime warning:** Update `yt-dlp` and consult its current runtime instructions; some formats may still be available.
- **YouTube `403` / no search results:** Some videos are unavailable or restricted. A search hit does not guarantee access or permission.
- **No songs detected:** Confirm tracks are in *Liked Songs* (not merely in a playlist) and the account used for OAuth is the correct one.

## Security before publishing

- Never commit real client secrets, `.spotify_cache`, `.cache`, `.env`, downloaded files, or personal track history.
- If a secret has ever been shared or committed, **rotate it** in Spotify Developer Dashboard. `.gitignore` does not remove leaked information from Git history.
- Review `git diff --cached` and `git status` before pushing.
- No personal Windows usernames, credentials, tokens, or local audio are included in the source files of this template.

## License

No open-source license is included by default. Add an appropriate license if you intend to grant others permission to reuse and redistribute your code.

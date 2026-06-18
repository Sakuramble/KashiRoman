# KashiRoman

KashiRoman is a local Windows tool for converting Japanese lyrics into readable romaji.

It accepts `.txt`, `.lrc`, and `.flac` files. For FLAC files, it reads embedded lyrics tags and can export a new FLAC with updated lyrics tags. It does not perform speech recognition from audio.

## Example

```text
Tell Me Tell Me
Tell Me Tell Me

鏡よ鏡
ka ga mi yo ka ga mi

一番好きな私になるの
i chi ba n su ki na wa ta shi ni na ru no
```

## Features

- Runs fully locally on Windows.
- Converts Japanese kanji and kana lyrics into romaji.
- Keeps English lyric lines as lyrics and preserves them in the romaji line.
- Can optionally keep original lyrics and translations.
- Handles common mixed lines such as `Tell Me Tell Me 告诉我 告诉我`.
- Preserves line timing when exporting updated FLAC lyrics.
- Supports drag and drop in the desktop window.

## Download

Download the Windows executable from the `v1.0` release:

`KashiRoman-1.0-Windows.exe`

## Output Modes

For TXT/LRC input, KashiRoman exports a UTF-8 TXT file.

For FLAC input, KashiRoman can either export a TXT file or export a new FLAC file with updated `LYRICS` and `UNSYNCEDLYRICS` tags. When exporting FLAC, it only writes the new FLAC and does not create a TXT file.

## Build From Source

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Run from source:

```powershell
python .\src\kashiroman.py
```

Build the Windows executable:

```powershell
python -m PyInstaller --onefile --windowed --collect-all tkinterdnd2 --name "KashiRoman" .\src\kashiroman.py
```

## Notes

Japanese kanji readings are inferred using a local Japanese dictionary. Common lyrics work well, but names, places, ateji, and intentionally unusual readings may still need manual review.

## License

GPL-3.0-or-later.

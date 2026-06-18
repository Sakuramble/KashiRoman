# KashiRoman

<p align="center">
  <a href="#中文"><kbd>🇨🇳 中文</kbd></a>
  <a href="#english"><kbd>🇬🇧 English</kbd></a>
</p>

<a id="中文"></a>

## 中文

**KashiRoman** 是一款面向 Windows 的本地日语歌词罗马音转换工具。它可以将日语歌词中的假名与常见汉字读音转换为更易跟唱、校对和整理的罗马音，并尽量保留原歌词的分行结构。

它支持 `.txt`、`.lrc` 和 `.flac` 文件。对于 FLAC 文件，KashiRoman 可以读取内嵌歌词标签，并导出写入新歌词标签的 FLAC 文件。KashiRoman 不会从音频中识别歌词，也不会进行语音识别。

## 示例

```text
Tell Me Tell Me
Tell Me Tell Me

鏡よ鏡
ka ga mi yo ka ga mi

一番好きな私になるの
i chi ba n su ki na wa ta shi ni na ru no
```

## 功能特点

- 完全在 Windows 本地运行。
- 将日语汉字、平假名和片假名歌词转换为罗马音。
- 英文歌词行会作为原歌词保留，并同步保留在罗马音行中。
- 可选择保留原歌词与翻译文本。
- 能处理 `Tell Me Tell Me 告诉我 告诉我` 等常见混合行。
- 导出 FLAC 歌词时保留原有歌词时间轴。
- 桌面窗口支持拖放文件。

## 下载

请在 `v1.0` Release 中下载 Windows 可执行文件：

```text
KashiRoman-1.0-Windows.exe
```

## 输出模式

- TXT/LRC 输入：导出 UTF-8 编码的 TXT 文件。
- FLAC 输入：可导出 TXT 文件，或导出写入 `LYRICS` 与 `UNSYNCEDLYRICS` 标签的新 FLAC 文件。选择导出 FLAC 时，只生成新的 FLAC 文件，不额外生成 TXT 文件。

## 从源码运行与构建

安装依赖：

```powershell
python -m pip install -r requirements.txt
```

从源码运行：

```powershell
python .\src\kashiroman.py
```

构建 Windows 可执行文件：

```powershell
python -m PyInstaller --onefile --windowed --collect-all tkinterdnd2 --name "KashiRoman" .\src\kashiroman.py
```

## 说明

日语汉字读音由本地日语词典推断。常见歌词通常效果较好，但人名、地名、当字以及刻意使用的特殊读法仍建议人工复核。

## 许可证

GPL-3.0-or-later.

---

<a id="english"></a>

## English

**KashiRoman** is a local Windows tool for converting Japanese lyrics into readable romaji. It helps you follow, review, and organize Japanese lyrics while preserving the original line structure as much as possible.

It supports `.txt`, `.lrc`, and `.flac` files. For FLAC files, KashiRoman can read embedded lyrics tags and export a new FLAC with updated lyrics tags. It does not perform speech recognition or extract lyrics from audio.

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
- Converts Japanese kanji, hiragana, and katakana lyrics into romaji.
- Keeps English lyric lines as lyrics and preserves them in the romaji line.
- Can optionally keep original lyrics and translations.
- Handles common mixed lines such as `Tell Me Tell Me 告诉我 告诉我`.
- Preserves line timing when exporting updated FLAC lyrics.
- Supports drag and drop in the desktop window.

## Download

Download the Windows executable from the `v1.0` release:

```text
KashiRoman-1.0-Windows.exe
```

## Output Modes

- TXT/LRC input: exports a UTF-8 TXT file.
- FLAC input: exports either a TXT file or a new FLAC file with updated `LYRICS` and `UNSYNCEDLYRICS` tags. When exporting FLAC, KashiRoman writes only the new FLAC file and does not create an additional TXT file.

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

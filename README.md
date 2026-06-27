<div align="center">

# 🎤 KashiRoman

### 面向 Windows 的本地日语歌词罗马音转换工具

**Japanese Lyrics · Romaji Conversion · TXT / LRC / FLAC · Windows Desktop · Local Processing**

<p>
  <strong>语言</strong><br/>
  <strong>简体中文</strong> ·
  <a href="#english">English</a>
</p>

<p>
  <strong>导航</strong><br/>
  <a href="#项目简介">项目简介</a> ·
  <a href="#示例">示例</a> ·
  <a href="#主要功能">主要功能</a> ·
  <a href="#下载">下载</a> ·
  <a href="#从源码运行与构建">构建</a> ·
  <a href="#许可证">许可证</a>
</p>

![Platform](https://img.shields.io/badge/Platform-Windows%20Desktop-111827)
![Language](https://img.shields.io/badge/Language-Python-0F766E)
![Input](https://img.shields.io/badge/Input-TXT%20%2F%20LRC%20%2F%20FLAC-1D4ED8)
![Output](https://img.shields.io/badge/Output-Romaji%20Lyrics-FF5722)
![License](https://img.shields.io/badge/License-GPL--3.0--or--later-7C3AED)
![Release](https://img.shields.io/github/v/release/V0idream/KashiRoman?include_prereleases)

<p>
  <a href="https://github.com/V0idream/KashiRoman/releases">
    <img src="https://img.shields.io/github/downloads/V0idream/KashiRoman/total?label=Release%20Downloads&style=for-the-badge" alt="Release Downloads" />
  </a>
</p>

</div>

---

<a id="中文"></a>

<a id="项目简介"></a>

## 📌 项目简介

**KashiRoman** 是一款面向 Windows 的本地日语歌词罗马音转换工具。它可以将日语歌词中的假名与常见汉字读音转换为更易跟唱、校对和整理的罗马音，并尽量保留原歌词的分行结构。

它支持 `.txt`、`.lrc` 和 `.flac` 文件。对于 FLAC 文件，KashiRoman 可以读取内嵌歌词标签，并导出写入新歌词标签的 FLAC 文件。KashiRoman 不会从音频中识别歌词，也不会进行语音识别。

<a id="示例"></a>

## 🧪 示例

```text
Tell Me Tell Me
Tell Me Tell Me

鏡よ鏡
ka ga mi yo ka ga mi

一番好きな私になるの
i chi ba n su ki na wa ta shi ni na ru no
```

<a id="主要功能"></a>

## ✨ 主要功能

* 完全在 Windows 本地运行。
* 将日语汉字、平假名和片假名歌词转换为罗马音。
* 英文歌词行会作为原歌词保留，并同步保留在罗马音行中。
* 可选择保留原歌词与翻译文本。
* 能处理 `Tell Me Tell Me 告诉我 告诉我` 等常见混合行。
* 导出 FLAC 歌词时保留原有歌词时间轴。
* 桌面窗口支持拖放文件。

<a id="下载"></a>

## 📦 下载

请在 GitHub Releases 中下载 Windows 可执行文件：

```text
KashiRoman-1.0-Windows.exe
```

> 仓库链接和 Release 徽章已统一使用当前用户名 `V0idream`。

## 📤 输出模式

* TXT / LRC 输入：导出 UTF-8 编码的 TXT 文件。
* FLAC 输入：可导出 TXT 文件，或导出写入 `LYRICS` 与 `UNSYNCEDLYRICS` 标签的新 FLAC 文件。选择导出 FLAC 时，只生成新的 FLAC 文件，不额外生成 TXT 文件。

<a id="从源码运行与构建"></a>

## 🛠️ 从源码运行与构建

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

## 📝 说明

日语汉字读音由本地日语词典推断。常见歌词通常效果较好，但人名、地名、当字以及刻意使用的特殊读法仍建议人工复核。

<a id="许可证"></a>

## 📜 许可证

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

* Runs fully locally on Windows.
* Converts Japanese kanji, hiragana, and katakana lyrics into romaji.
* Keeps English lyric lines as lyrics and preserves them in the romaji line.
* Can optionally keep original lyrics and translations.
* Handles common mixed lines such as `Tell Me Tell Me 告诉我 告诉我`.
* Preserves line timing when exporting updated FLAC lyrics.
* Supports drag and drop in the desktop window.

## Download

Download the Windows executable from GitHub Releases:

```text
KashiRoman-1.0-Windows.exe
```

## Output Modes

* TXT / LRC input: exports a UTF-8 TXT file.
* FLAC input: exports either a TXT file or a new FLAC file with updated `LYRICS` and `UNSYNCEDLYRICS` tags. When exporting FLAC, KashiRoman writes only the new FLAC file and does not create an additional TXT file.

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

---

## ☕ 支持项目 / Support

如果这个项目对你有帮助，欢迎点一个 Star。  
若愿意进一步支持，也可以通过赞赏码请作者续一口 AI 订阅。

众所周知，风水宝地土耳其并非久居之所；账号颠沛流离，订阅价格又日渐高昂，维护开源项目实属不易。

你的赞赏将带来：作者诚挚的感谢、更快更稳定的更新动力，以及对合理功能建议的优先考虑。

不赞赏也完全不影响项目使用、Issue 交流和功能建议。只是如果这个项目真的帮到了你——你真的忍心看作者独自面对订阅账单吗 😢

👉 [查看赞赏方式](./docs/support.md)

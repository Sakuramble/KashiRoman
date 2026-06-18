import argparse
import os
import re
import shutil
import sys
import traceback
from dataclasses import dataclass
from pathlib import Path

try:
    from mutagen.flac import FLAC
    from sudachipy import dictionary, tokenizer
except Exception:
    FLAC = None
    dictionary = None
    tokenizer = None

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:
    DND_FILES = None
    TkinterDnD = None


APP_TITLE = "日文歌词罗马音转换工具"

KANA_RE = re.compile(r"[\u3040-\u309f\u30a0-\u30ff]")
JAPANESE_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\u3005\u3006\u30f5\u30f6]")
LATIN_RE = re.compile(r"[A-Za-z0-9]")
TIMESTAMP_RE = re.compile(r"\[(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?\]")
INLINE_TS_RE = re.compile(r"<(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?>")
LEADING_TIMESTAMPS_RE = re.compile(r"^((?:\[(?:\d{1,2}:)?\d{1,2}:\d{2}(?:[.:]\d{1,3})?\])+)")
LRC_META_RE = re.compile(r"^\s*\[(?:ar|ti|al|by|offset|length|re|ve|tool|kana|language|la):.*\]\s*$", re.I)
META_LABEL_RE = re.compile(
    r"^\s*(?:"
    r"作詞|作词|作曲|編曲|编曲|作編曲|制作|歌手|歌|曲|詞|词|"
    r"翻訳|翻译|中文|日文|罗马音|羅馬音|"
    r"lyrics?|lyricist|composer|arranger|music|vocal|artist|album|title|"
    r"produced\s+by|performed\s+by"
    r")\s*[:：／/].*$",
    re.I,
)
BRACKET_NOTE_RE = re.compile(r"^\s*[\[(【（(].*?[\])】）)]\s*$")
MIXED_LINE_SPLIT_RE = re.compile(r"(?:\s*[|｜/／]\s*|\s*[-–—―=＝:：]\s*)")


ROMAJI_BASE = {
    "ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o",
    "カ": "ka", "キ": "ki", "ク": "ku", "ケ": "ke", "コ": "ko",
    "サ": "sa", "シ": "shi", "ス": "su", "セ": "se", "ソ": "so",
    "タ": "ta", "チ": "chi", "ツ": "tsu", "テ": "te", "ト": "to",
    "ナ": "na", "ニ": "ni", "ヌ": "nu", "ネ": "ne", "ノ": "no",
    "ハ": "ha", "ヒ": "hi", "フ": "fu", "ヘ": "he", "ホ": "ho",
    "マ": "ma", "ミ": "mi", "ム": "mu", "メ": "me", "モ": "mo",
    "ヤ": "ya", "ユ": "yu", "ヨ": "yo",
    "ラ": "ra", "リ": "ri", "ル": "ru", "レ": "re", "ロ": "ro",
    "ワ": "wa", "ヰ": "wi", "ヱ": "we", "ヲ": "wo", "ン": "n",
    "ガ": "ga", "ギ": "gi", "グ": "gu", "ゲ": "ge", "ゴ": "go",
    "ザ": "za", "ジ": "ji", "ズ": "zu", "ゼ": "ze", "ゾ": "zo",
    "ダ": "da", "ヂ": "ji", "ヅ": "zu", "デ": "de", "ド": "do",
    "バ": "ba", "ビ": "bi", "ブ": "bu", "ベ": "be", "ボ": "bo",
    "パ": "pa", "ピ": "pi", "プ": "pu", "ペ": "pe", "ポ": "po",
    "ァ": "a", "ィ": "i", "ゥ": "u", "ェ": "e", "ォ": "o",
    "ャ": "ya", "ュ": "yu", "ョ": "yo", "ヮ": "wa",
    "ヴ": "vu",
}

ROMAJI_DIGRAPHS = {
    "キャ": "kya", "キュ": "kyu", "キョ": "kyo",
    "シャ": "sha", "シュ": "shu", "ショ": "sho",
    "チャ": "cha", "チュ": "chu", "チョ": "cho",
    "ニャ": "nya", "ニュ": "nyu", "ニョ": "nyo",
    "ヒャ": "hya", "ヒュ": "hyu", "ヒョ": "hyo",
    "ミャ": "mya", "ミュ": "myu", "ミョ": "myo",
    "リャ": "rya", "リュ": "ryu", "リョ": "ryo",
    "ギャ": "gya", "ギュ": "gyu", "ギョ": "gyo",
    "ジャ": "ja", "ジュ": "ju", "ジョ": "jo",
    "ヂャ": "ja", "ヂュ": "ju", "ヂョ": "jo",
    "ビャ": "bya", "ビュ": "byu", "ビョ": "byo",
    "ピャ": "pya", "ピュ": "pyu", "ピョ": "pyo",
    "ファ": "fa", "フィ": "fi", "フェ": "fe", "フォ": "fo",
    "ウィ": "wi", "ウェ": "we", "ウォ": "wo",
    "ヴァ": "va", "ヴィ": "vi", "ヴェ": "ve", "ヴォ": "vo",
    "ティ": "ti", "ディ": "di", "トゥ": "tu", "ドゥ": "du",
    "チェ": "che", "シェ": "she", "ジェ": "je",
}

PUNCT_TRANSLATION = str.maketrans({
    "，": ",", "。": ".", "？": "?", "！": "!", "：": ":", "；": ";",
    "（": "(", "）": ")", "「": "\"", "」": "\"", "『": "\"", "』": "\"",
    "“": "\"", "”": "\"", "‘": "'", "’": "'", "　": " ",
})

_tokenizer = None
_split_mode = None


@dataclass
class LyricEntry:
    original: str
    translation: str = ""


@dataclass
class ConvertOptions:
    keep_original: bool = True
    keep_translation: bool = False
    export_flac: bool = False


def app_base_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def ensure_tokenizer():
    global _tokenizer, _split_mode
    if _tokenizer is None:
        if dictionary is None or tokenizer is None:
            raise RuntimeError("缺少日文词典库，程序无法转换汉字读音。")
        _tokenizer = dictionary.Dictionary().create()
        _split_mode = tokenizer.Tokenizer.SplitMode.C
    return _tokenizer, _split_mode


def read_text_file(path: Path) -> str:
    data = path.read_bytes()
    encodings = ["utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "cp932", "gb18030"]
    for encoding in encodings:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def extract_flac_lyrics(path: Path) -> str:
    if FLAC is None:
        raise RuntimeError("缺少 FLAC 读取库，程序无法读取音频标签。")
    audio = FLAC(path)
    preferred = [
        "lyrics", "unsyncedlyrics", "syncedlyrics", "lyric", "description",
        "unsynchronised lyrics", "unsynchronized lyrics",
    ]
    keys = {key.lower(): key for key in audio.keys()}
    values = []
    for name in preferred:
        if name in keys:
            values.extend(audio.get(keys[name], []))
    if not values:
        for key, val in audio.items():
            if "lyric" in key.lower():
                values.extend(val)
    text = "\n".join(str(item) for item in values).strip()
    if not text:
        raise RuntimeError("这个 FLAC 文件没有找到内嵌歌词标签。工具不会从音频做人声识别。")
    return text


def load_input(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".flac":
        return extract_flac_lyrics(path)
    if suffix in {".txt", ".lrc"}:
        return read_text_file(path)
    raise RuntimeError("只支持 .txt、.lrc 或 .flac 文件。")


def strip_timestamps(line: str) -> str:
    line = TIMESTAMP_RE.sub("", line)
    line = INLINE_TS_RE.sub("", line)
    return line.strip()


def split_leading_timestamps(line: str) -> tuple[str, str]:
    match = LEADING_TIMESTAMPS_RE.match(line.strip())
    if not match:
        return "", line.strip()
    prefix = match.group(1)
    return prefix, line.strip()[len(prefix):].strip()


def normalize_content_line(line: str) -> str | None:
    line = line.replace("\ufeff", "").strip()
    if not line:
        return None
    if LRC_META_RE.match(line):
        return None
    line = strip_timestamps(line)
    if not line:
        return None
    if META_LABEL_RE.match(line):
        return None
    if BRACKET_NOTE_RE.match(line) and not KANA_RE.search(line):
        return None
    line = re.sub(r"\s+", " ", line).strip()
    if not line:
        return None
    return line


def split_original_translation(line: str) -> LyricEntry | None:
    # Most Japanese lyric lines contain kana. CJK-only chunks separated from a
    # kana lyric are usually Chinese translations, while Latin words can be part
    # of the sung lyric and should be preserved.
    if not KANA_RE.search(line):
        return None

    original_parts = []
    translation_parts = []
    parts = [part.strip() for part in MIXED_LINE_SPLIT_RE.split(line) if part.strip()]
    for part in parts:
        original_words = []
        translation_words = []
        for word in re.split(r"(\s+)", part):
            if not word:
                continue
            if word.isspace():
                if original_words and original_words[-1] != " ":
                    original_words.append(" ")
                if translation_words and translation_words[-1] != " ":
                    translation_words.append(" ")
                continue
            if KANA_RE.search(word) or LATIN_RE.search(word):
                original_words.append(word)
            elif not JAPANESE_RE.search(word):
                original_words.append(word)
            else:
                translation_words.append(word)
        original = "".join(original_words).strip()
        translation = "".join(translation_words).strip()
        if original:
            original_parts.append(original)
        if translation:
            translation_parts.append(translation)
    if not original_parts:
        return None
    return LyricEntry(
        original=" ".join(original_parts).strip(),
        translation=" ".join(translation_parts).strip(),
    )


def split_latin_translation(line: str) -> LyricEntry | None:
    if not LATIN_RE.search(line) or KANA_RE.search(line):
        return None
    original_words = []
    translation_words = []
    for word in re.split(r"(\s+)", line):
        if not word:
            continue
        if word.isspace():
            if original_words and original_words[-1] != " ":
                original_words.append(" ")
            if translation_words and translation_words[-1] != " ":
                translation_words.append(" ")
            continue
        if LATIN_RE.search(word):
            original_words.append(word)
        elif re.search(r"[\u3400-\u9fff]", word):
            translation_words.append(word)
        elif not JAPANESE_RE.search(word):
            original_words.append(word)
    original = "".join(original_words).strip()
    translation = "".join(translation_words).strip()
    if not original:
        return None
    return LyricEntry(original=original, translation=translation)


def is_translation_only_line(line: str) -> bool:
    if KANA_RE.search(line):
        return False
    if LATIN_RE.search(line):
        return False
    return bool(re.search(r"[\u3400-\u9fff]", line))


def is_latin_lyric_line(line: str) -> bool:
    if not LATIN_RE.search(line):
        return False
    if KANA_RE.search(line):
        return False
    if re.search(r"[\u3400-\u9fff]", line):
        return False
    return True


def extract_translation_text(line: str) -> str:
    return line.translate(PUNCT_TRANSLATION).strip()


def parse_lyrics(raw_text: str) -> list[LyricEntry]:
    entries = []
    for raw_line in raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = normalize_content_line(raw_line)
        if line is None:
            continue
        entry = split_original_translation(line)
        if entry is not None:
            entries.append(entry)
            continue
        entry = split_latin_translation(line)
        if entry is not None:
            entries.append(entry)
            continue
        if is_latin_lyric_line(line):
            entries.append(LyricEntry(original=line))
            continue
        if entries and is_translation_only_line(line) and not entries[-1].translation:
            entries[-1].translation = extract_translation_text(line)
    return entries


def hira_to_kata(text: str) -> str:
    chars = []
    for ch in text:
        code = ord(ch)
        if 0x3041 <= code <= 0x3096:
            chars.append(chr(code + 0x60))
        else:
            chars.append(ch)
    return "".join(chars)


def last_vowel(text: str) -> str:
    for ch in reversed(text):
        if ch in "aeiou":
            return ch
    return ""


def next_romaji_starts_with_vowel(kata: str, index: int) -> bool:
    part = kata[index:index + 2]
    if part in ROMAJI_DIGRAPHS:
        rom = ROMAJI_DIGRAPHS[part]
    else:
        rom = ROMAJI_BASE.get(kata[index], "")
    return bool(rom and rom[0] in "aeiou")


def kana_to_romaji_units(kana: str) -> list[str]:
    kata = hira_to_kata(kana)
    units = []
    double_next = False
    i = 0
    while i < len(kata):
        ch = kata[i]
        if ch in {"ッ", "っ"}:
            double_next = True
            i += 1
            continue
        if ch == "ー":
            vowel = last_vowel("".join(units))
            if vowel:
                units.append(vowel)
            i += 1
            continue
        pair = kata[i:i + 2]
        if pair in ROMAJI_DIGRAPHS:
            rom = ROMAJI_DIGRAPHS[pair]
            i += 2
        else:
            rom = ROMAJI_BASE.get(ch)
            i += 1
        if rom is None:
            raw = ch.translate(PUNCT_TRANSLATION).strip()
            if raw:
                units.append(raw)
            double_next = False
            continue
        if double_next and rom and rom[0] not in "aeioun":
            rom = rom[0] + rom
        double_next = False
        units.append(rom)

    for index, unit in enumerate(units[:-1]):
        if unit == "n" and units[index + 1][:1] in {"b", "m", "p"}:
            units[index] = "m"
    return units


def kana_to_romaji(kana: str) -> str:
    return "".join(kana_to_romaji_units(kana))


def token_reading(morpheme) -> str:
    surface = morpheme.surface()
    pos = morpheme.part_of_speech()
    reading = morpheme.reading_form()
    if pos and pos[0] == "助詞":
        if surface == "は":
            return "ワ"
        if surface == "へ":
            return "エ"
        if surface == "を":
            return "オ"
    if surface == "私" and reading == "ワタクシ":
        return "ワタシ"
    if not reading or reading == "*":
        return surface
    return reading


def split_romaji_parts(line: str) -> list[str]:
    sudachi, mode = ensure_tokenizer()
    parts = []
    buffer = []
    prior_readings = {}

    def flush_buffer():
        if buffer:
            raw = "".join(buffer).translate(PUNCT_TRANSLATION).strip()
            if raw:
                parts.append(raw)
            buffer.clear()

    for morpheme in sudachi.tokenize(line, mode):
        surface = morpheme.surface()
        if JAPANESE_RE.search(surface):
            flush_buffer()
            reading = token_reading(morpheme)
            pos = morpheme.part_of_speech()
            if (
                surface in prior_readings
                and pos
                and pos[0] == "接尾辞"
                and re.search(r"[\u3400-\u9fff]", surface)
            ):
                reading = prior_readings[surface]
            elif re.search(r"[\u3400-\u9fff]", surface) and KANA_RE.search(reading):
                prior_readings.setdefault(surface, reading)
            parts.extend(kana_to_romaji_units(reading))
        else:
            buffer.append(surface)
    flush_buffer()
    return parts


def romanize_line(line: str) -> str:
    text = " ".join(part for part in split_romaji_parts(line) if part)
    text = re.sub(r"\s+([,.?!:;])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    text = re.sub(r"\s+([)])", r"\1", text)
    return text.strip()


def convert_text(raw_text: str, options: ConvertOptions | None = None) -> tuple[list[LyricEntry], str]:
    options = options or ConvertOptions()
    entries = parse_lyrics(raw_text)
    output = []
    for entry in entries:
        if options.keep_original:
            output.append(entry.original)
        if options.keep_translation and entry.translation:
            output.append(entry.translation)
        output.append(romanize_line(entry.original))
        output.append("")
    return entries, "\n".join(output).rstrip() + ("\n" if output else "")


def convert_text_preserve_structure(raw_text: str, options: ConvertOptions | None = None) -> tuple[int, str]:
    options = options or ConvertOptions()
    converted_count = 0
    output = []
    pending_entry_index = None

    for raw_line in raw_text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        stripped = raw_line.replace("\ufeff", "").strip()
        if not stripped:
            output.append("")
            pending_entry_index = None
            continue

        if LRC_META_RE.match(stripped):
            output.append(stripped)
            pending_entry_index = None
            continue

        prefix, content = split_leading_timestamps(stripped)
        content = INLINE_TS_RE.sub("", content).strip()
        if not content:
            output.append(stripped)
            pending_entry_index = None
            continue

        if META_LABEL_RE.match(content) or (BRACKET_NOTE_RE.match(content) and not KANA_RE.search(content)):
            output.append(stripped)
            pending_entry_index = None
            continue

        entry = split_original_translation(re.sub(r"\s+", " ", content).strip())
        if entry is None:
            entry = split_latin_translation(re.sub(r"\s+", " ", content).strip())
        if entry is not None:
            added = []
            if options.keep_original:
                added.append(f"{prefix}{entry.original}")
            if options.keep_translation and entry.translation:
                added.append(f"{prefix}{entry.translation}")
            added.append(f"{prefix}{romanize_line(entry.original)}")
            output.extend(added)
            converted_count += 1
            pending_entry_index = len(output) - 1
            continue

        if is_latin_lyric_line(content):
            if options.keep_original:
                output.append(f"{prefix}{content}")
            output.append(f"{prefix}{romanize_line(content)}")
            converted_count += 1
            pending_entry_index = len(output) - 1
            continue

        if pending_entry_index is not None and is_translation_only_line(content):
            if options.keep_translation:
                output.insert(pending_entry_index, f"{prefix}{extract_translation_text(content)}")
                pending_entry_index += 1
            continue

        if is_translation_only_line(content):
            if options.keep_translation:
                output.append(stripped)
            continue

        output.append(stripped)
        pending_entry_index = None

    return converted_count, "\n".join(output).rstrip() + ("\n" if output else "")


def default_output_path(input_path: Path) -> Path:
    return input_path.with_name(input_path.stem + "_romaji.txt")


def default_flac_output_path(input_path: Path) -> Path:
    return input_path.with_name(input_path.stem + "_romaji.flac")


def export_flac_with_lyrics(input_path: Path, lyrics_text: str, output_path: Path | None = None) -> Path:
    if FLAC is None:
        raise RuntimeError("缺少 FLAC 读取库，程序无法写入音频标签。")
    input_path = input_path.resolve()
    if input_path.suffix.lower() != ".flac":
        raise RuntimeError("只有 FLAC 输入文件可以导出带歌词的 FLAC。")
    output_path = (output_path or default_flac_output_path(input_path)).resolve()
    if output_path == input_path:
        raise RuntimeError("为避免覆盖原音频，FLAC 导出路径不能和原文件相同。")
    shutil.copy2(input_path, output_path)
    audio = FLAC(output_path)
    audio["LYRICS"] = [lyrics_text]
    audio["UNSYNCEDLYRICS"] = [lyrics_text]
    audio.save()
    return output_path


def convert_file(
    input_path: Path,
    output_path: Path | None = None,
    options: ConvertOptions | None = None,
    flac_output_path: Path | None = None,
) -> list[Path]:
    options = options or ConvertOptions()
    input_path = input_path.resolve()
    raw_text = load_input(input_path)

    if options.export_flac:
        target_flac = flac_output_path or output_path or default_flac_output_path(input_path)
        converted_count, converted = convert_text_preserve_structure(raw_text, options)
        if not converted_count:
            raise RuntimeError("没有找到可转换的日文歌词行。请确认 FLAC 歌词标签里包含日文假名歌词。")
        return [export_flac_with_lyrics(input_path, converted, Path(target_flac))]

    if output_path is None:
        output_path = default_output_path(input_path)
    else:
        output_path = output_path.resolve()
    entries, converted = convert_text(raw_text, options)
    if not entries:
        raise RuntimeError("没有找到可转换的日文歌词行。请确认文件里包含日文假名歌词，而不只是翻译或信息。")
    output_path.write_text(converted, encoding="utf-8-sig", newline="\n")
    return [output_path]


def run_gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    root = TkinterDnD.Tk() if TkinterDnD is not None else tk.Tk()
    root.title(APP_TITLE)
    root.geometry("620x360")
    root.resizable(False, False)

    selected_path = tk.StringVar()
    output_path = tk.StringVar()
    keep_original = tk.BooleanVar(value=True)
    keep_translation = tk.BooleanVar(value=False)
    export_flac = tk.BooleanVar(value=False)
    status = tk.StringVar(value="选择 TXT/LRC 或带内嵌歌词的 FLAC 文件。")
    flac_check = None

    def desired_output_path(path: Path) -> Path:
        return default_flac_output_path(path) if export_flac.get() else default_output_path(path)

    def sync_output_path():
        if selected_path.get():
            output_path.set(str(desired_output_path(Path(selected_path.get()))))

    def choose_input():
        path = filedialog.askopenfilename(
            title="选择歌词或 FLAC 文件",
            filetypes=[
                ("支持的文件", "*.txt *.lrc *.flac"),
                ("歌词文本", "*.txt *.lrc"),
                ("FLAC 音频", "*.flac"),
                ("所有文件", "*.*"),
            ],
        )
        if path:
            set_input_file(path)

    def update_flac_option_state():
        if flac_check is None:
            return
        path = Path(selected_path.get()) if selected_path.get() else None
        is_flac = bool(path and path.suffix.lower() == ".flac")
        flac_check.state(["!disabled"] if is_flac else ["disabled"])
        if not is_flac:
            export_flac.set(False)

    def on_export_flac_change(*_args):
        sync_output_path()
        if export_flac.get():
            status.set("FLAC 导出模式：只生成新 FLAC，不生成 TXT。")
        elif selected_path.get():
            status.set("TXT 输出模式：会生成转换后的 TXT 文件。")

    def set_input_file(path_text: str):
        path = Path(path_text.strip()).expanduser()
        if not path.exists():
            messagebox.showwarning(APP_TITLE, "拖入的文件不存在。")
            return
        if path.suffix.lower() not in {".txt", ".lrc", ".flac"}:
            messagebox.showwarning(APP_TITLE, "只支持 .txt、.lrc 或 .flac 文件。")
            return
        selected_path.set(str(path))
        update_flac_option_state()
        sync_output_path()
        if path.suffix.lower() == ".flac":
            status.set("已选择 FLAC。可勾选导出新 FLAC 并写入转换后的歌词。")
        else:
            status.set("已选择文件，点击开始转换。")

    def handle_drop(event):
        try:
            paths = root.tk.splitlist(event.data)
            if paths:
                set_input_file(paths[0])
        except Exception as exc:
            messagebox.showerror(APP_TITLE, f"无法读取拖入文件：{exc}")

    def choose_output():
        initial = output_path.get()
        initial_dir = str(Path(initial).parent) if initial else str(Path.home())
        initial_file = Path(initial).name if initial else ("lyrics_romaji.flac" if export_flac.get() else "lyrics_romaji.txt")
        if export_flac.get():
            title = "选择输出 FLAC 文件"
            defaultextension = ".flac"
            filetypes = [("FLAC 文件", "*.flac"), ("所有文件", "*.*")]
        else:
            title = "选择输出 TXT 文件"
            defaultextension = ".txt"
            filetypes = [("TXT 文件", "*.txt"), ("所有文件", "*.*")]
        path = filedialog.asksaveasfilename(
            title=title,
            defaultextension=defaultextension,
            initialdir=initial_dir,
            initialfile=initial_file,
            filetypes=filetypes,
        )
        if path:
            output_path.set(path)

    def start_convert():
        try:
            if not selected_path.get():
                messagebox.showwarning(APP_TITLE, "请先选择一个 TXT、LRC 或 FLAC 文件。")
                return
            out = output_path.get().strip() or str(desired_output_path(Path(selected_path.get())))
            status.set("正在转换...")
            root.update_idletasks()
            options = ConvertOptions(
                keep_original=keep_original.get(),
                keep_translation=keep_translation.get(),
                export_flac=export_flac.get(),
            )
            written = convert_file(Path(selected_path.get()), Path(out), options)
            written_text = "\n".join(str(path) for path in written)
            status.set(f"完成：{written[0]}")
            messagebox.showinfo(APP_TITLE, f"已输出：\n{written_text}")
        except Exception as exc:
            log_path = app_base_dir() / "lyrics_romaji_error.log"
            log_path.write_text(traceback.format_exc(), encoding="utf-8")
            status.set("转换失败。")
            messagebox.showerror(APP_TITLE, f"{exc}\n\n错误详情已保存到：\n{log_path}")

    padding = {"padx": 16, "pady": 8}
    ttk.Label(root, text="输入文件").grid(row=0, column=0, sticky="w", **padding)
    ttk.Entry(root, textvariable=selected_path, width=58).grid(row=1, column=0, sticky="we", padx=16)
    ttk.Button(root, text="选择文件", command=choose_input).grid(row=1, column=1, padx=12)

    ttk.Label(root, text="输出文件").grid(row=2, column=0, sticky="w", **padding)
    ttk.Entry(root, textvariable=output_path, width=58).grid(row=3, column=0, sticky="we", padx=16)
    ttk.Button(root, text="另存为", command=choose_output).grid(row=3, column=1, padx=12)

    options_frame = ttk.LabelFrame(root, text="输出选项")
    options_frame.grid(row=4, column=0, columnspan=2, sticky="we", padx=16, pady=12)
    ttk.Checkbutton(options_frame, text="保留日文原文", variable=keep_original).grid(row=0, column=0, sticky="w", padx=12, pady=8)
    ttk.Checkbutton(options_frame, text="保留译文", variable=keep_translation).grid(row=0, column=1, sticky="w", padx=12, pady=8)
    flac_check = ttk.Checkbutton(options_frame, text="输入为 FLAC 时另存新 FLAC 并写入歌词", variable=export_flac)
    flac_check.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=8)
    export_flac.trace_add("write", on_export_flac_change)
    update_flac_option_state()

    ttk.Button(root, text="开始转换", command=start_convert).grid(row=5, column=0, sticky="w", padx=16, pady=16)
    ttk.Label(root, textvariable=status, wraplength=580).grid(row=6, column=0, columnspan=2, sticky="w", padx=16)

    if DND_FILES is not None and hasattr(root, "drop_target_register"):
        root.drop_target_register(DND_FILES)
        root.dnd_bind("<<Drop>>", handle_drop)
        status.set("选择文件，或把 TXT/LRC/FLAC 直接拖进这个窗口。")
    else:
        status.set("选择文件；也可以把文件拖到 exe 图标上直接转换。")

    root.mainloop()


def parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("input", nargs="?", help="输入 .txt/.lrc/.flac 文件")
    parser.add_argument("output", nargs="?", help="输出文件；普通模式为 .txt，--export-flac 模式为 .flac")
    parser.add_argument("--no-original", action="store_false", dest="keep_original", help="输出中不保留日文原文")
    parser.add_argument("--translation", action="store_true", dest="keep_translation", help="输出中保留译文")
    parser.add_argument("--export-flac", action="store_true", help="输入为 FLAC 时，另存新 FLAC 并写入转换后的歌词")
    parser.add_argument("--flac-output", help="导出的 FLAC 路径；省略时自动生成 *_romaji.flac")
    parser.set_defaults(keep_original=True, keep_translation=False)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    if not args.input:
        run_gui()
        return 0
    try:
        options = ConvertOptions(
            keep_original=args.keep_original,
            keep_translation=args.keep_translation,
            export_flac=args.export_flac,
        )
        written = convert_file(
            Path(args.input),
            Path(args.output) if args.output else None,
            options,
            Path(args.flac_output) if args.flac_output else None,
        )
        print("已输出：")
        for path in written:
            print(path)
        return 0
    except Exception as exc:
        print(f"转换失败：{exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

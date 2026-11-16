"""Build index.html from briefings/*.md (same idea as the A350 Atlas offline build:
one self-contained HTML file with all data inlined).

Usage:  python3 build.py
"""
import html, json, pathlib, re

ROOT = pathlib.Path(__file__).parent
BRIEF_DIR = ROOT / "briefings"


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
               lambda m: '<a href="%s" target="_blank" rel="noopener">%s</a>'
               % (html.escape(m.group(2)), m.group(1)), s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return s


def md_to_html(md):
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + "<br>".join(inline(x) for x in para) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join("<li>%s</li>" % inline(x) for x in items) + "</ul>")
            items.clear()

    md = re.sub(r"\\([\[\]\\*_#()`>\-.!])", r"\1", md)  # undo markdown escapes
    md = re.sub(r"\s+(\*\*(?:Why it matters|Sources):\*\*)", r"\n\1", md)  # one field per line
    md = re.sub(r"(?m)^\*\*Today in one line:\*\*.*$", "", md)  # shown in its own banner
    for raw in md.splitlines():
        line = raw.rstrip()
        if not line.strip():
            flush()
            continue
        m = re.match(r"^(#{1,4})\s+(.*)", line)
        if m:
            flush()
            lvl = len(m.group(1))
            text = m.group(2)
            if lvl == 1:
                continue  # page shows its own date title
            n = re.match(r"^(\d+)\.\s+(.*)", text)
            if lvl == 2 and n:
                body = n.group(2)
                cat = ""
                c = re.search(r"\s*\[([^\]]+)\]\s*$", body)
                if c:
                    cat = c.group(1)
                    body = body[:c.start()]
                out.append('<h2 class="story"><span class="num">%s</span><span class="ht">%s</span>%s</h2>'
                           % (n.group(1), inline(body),
                              '<span class="cat">%s</span>' % html.escape(cat) if cat else ""))
            else:
                out.append("<h%d>%s</h%d>" % (min(lvl, 3), inline(text), min(lvl, 3)))
            continue
        b = re.match(r"^\s*[-*]\s+(.*)", line)
        if b:
            if para:
                flush()
            items.append(b.group(1))
            continue
        if items:
            flush()
        para.append(line.strip())
    flush()
    return "\n".join(out)


# Editions: World lives in briefings/DATE.md, the others in briefings/<key>/DATE.md
EDITIONS = [("world", BRIEF_DIR), ("us", BRIEF_DIR / "us"), ("asia", BRIEF_DIR / "asia"), ("hk", BRIEF_DIR / "hk")]


def edition(path):
    md = path.read_text(encoding="utf-8-sig")
    one = re.search(r"\*\*Today in one line:\*\*\s*(.+)", md)
    return {
        "line": re.sub(r"\*\*|\[|\]\([^)]*\)", "", one.group(1)).strip() if one else "",
        "html": md_to_html(md),
    }


def main():
    dates = set()
    for _, d in EDITIONS:
        dates |= {f.stem for f in d.glob("*.md") if re.match(r"^\d{4}-\d{2}-\d{2}$", f.stem)}
    entries = []
    for date in sorted(dates, reverse=True):
        eds = {key: edition(d / (date + ".md")) for key, d in EDITIONS if (d / (date + ".md")).exists()}
        entries.append({"date": date, "ed": eds})
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    tpl = (ROOT / "template.html").read_text(encoding="utf-8")
    assert "/*DATA*/" in tpl
    out = tpl.replace("/*DATA*/[]", data)
    (ROOT / "index.html").write_text(out, encoding="utf-8")
    print("index.html: %d briefings, %d bytes" % (len(entries), len(out)))


if __name__ == "__main__":
    main()

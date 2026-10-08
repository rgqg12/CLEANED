"""Build the Word version of the water-footprint methodology with native Word equations.

The methodology is written in a Claude Doc whose formulas are LaTeX code blocks. The doc's own
Word export prints those blocks as raw LaTeX, so this script converts the doc's Markdown export with
pandoc instead:
  - every ```latex block becomes a display equation ($$ ... $$ -> Office Math);
  - symbols written in the text (GWU_c, AF_c,R, ET0,m, Kc,ini, ...) become inline equations.

Usage: python build_docx.py methodology.md output.docx
"""
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
WORD_SUB = {"ini", "dev", "mid", "late", "end", "eff", "herd", "excl", "milk", "meat", "wool",
            "draught", "conc", "true", "annual", "irr", "drink", "service"}


def sub(s):
    """Subscript/superscript text: words upright, single letters italic."""
    parts = s.split(",")
    return ",".join(r"\mathrm{%s}" % p if p in WORD_SUB or len(p) > 3 else p for p in parts)


# Ordered: specific patterns first. Each maps a plain-text symbol to inline LaTeX.
FIXED = [
    (r"CWU\^g\\_c,r", r"CWU^{g}_{c,r}"),
    (r"CWU\^b,irr", r"CWU^{b,\mathrm{irr}}_{c,r}"),
    (r"W\^0\.75", r"W^{0.75}"),
    (r"WG\^1\.097", r"WG^{1.097}"),
    (r"\^0\.75", r"^{0.75}"),
    (r"Σ\\_([kji])", r"\sum_{\1}"),
    (r"K̄c", r"\bar{K}_c"),
    (r"\bET0,annual\b", r"ET_{0,\mathrm{annual}}"),
    (r"\bPeff,annual\b", r"P_{\mathrm{eff},\mathrm{annual}}"),
    (r"\bET0,m\b", r"ET_{0,m}"),
    (r"\bET([cgb]),m\b", r"ET_{\1,m}"),
    (r"\bPeff,m\b", r"P_{\mathrm{eff},m}"),
    (r"\bKc,(ini|mid|end)\b", r"K_{c,\mathrm{\1}}"),
    (r"\bKc,m\b", r"K_{c,m}"),
    (r"\bET0\b", r"ET_0"),
    (r"\bET([cgb])\b", r"ET_\1"),
    (r"\bPeff\b", r"P_{\mathrm{eff}}"),
    (r"\bKc\b", r"K_c"),
]
# Generic X\_y or X\_y,z (e.g. GWU\_c, AF\_c,R, L\_ini, WF\_milk); excludes names like Study\_1.
GENERIC = re.compile(r"(?<![\w\\$])([A-Za-z]{1,4})\\_([A-Za-z0-9]{1,8}(?:,[A-Za-z]{1,3}(?![A-Za-z]))?)(?![\w])")
KEEP = ["Study\\_1", "main\\_product\\_me"]


def inline_math(text):
    protected = {}

    def protect(m):
        key = f"\x00{len(protected)}\x00"
        protected[key] = m.group(0)
        return key

    text = re.sub(r"\[[^\]]*\]\([^)]*\)|`[^`]*`|https?://\S+", protect, text)   # links, code
    for k in KEEP:
        text = text.replace(k, protect(re.match(re.escape(k), k)))
    for pat, rep in FIXED:
        text = re.sub(pat, lambda m, r=rep: "$" + (r.replace("\\1", m.group(1)) if m.groups() else r) + "$", text)

    def gen(m):
        base, s = m.group(1), m.group(2)
        if base.isdigit():
            return m.group(0)
        return "$%s_{%s}$" % (base, sub(s))

    text = GENERIC.sub(gen, text)
    text = text.replace("$$", "")            # two adjacent inline symbols -> merge into one
    text = re.sub(r"\$(\\sum_\{\w\})\$ \$", r"$\1 ", text)   # sum sign joins the symbol after it
    for k, v in protected.items():
        text = text.replace(k, v)
    return text.replace("Study\\_1", "Study_1").replace("main\\_product\\_me", "main_product_me")


def convert(md):
    out, blocks = [], re.split(r"(```latex\n.*?\n```)", md, flags=re.S)
    for b in blocks:
        if b.startswith("```latex"):
            body = b[len("```latex\n"):-len("\n```")].strip()
            # word subscripts upright: K_{c,ini} -> K_{c,\mathrm{ini}}
            body = re.sub(r"(?<=[_,{])(" + "|".join(sorted(WORD_SUB | {"maint", "act", "growth", "lact", "preg", "work", "excluded"})) + r")(?=[},])",
                          r"\\mathrm{\1}", body)
            out.append("\n$$\n" + body + "\n$$\n")
        else:
            out.append("\n".join(inline_math(line) for line in b.split("\n")))
    return "".join(out)


if __name__ == "__main__":
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    tmp = dst.with_suffix(".pandoc.md")
    tmp.write_text(convert(src.read_text()))
    subprocess.run(["pandoc", str(tmp), "-f", "markdown+tex_math_dollars+pipe_tables", "-t", "docx",
                    "--reference-doc", str(HERE / "reference.docx"), "-o", str(dst)], check=True)
    print("written", dst)

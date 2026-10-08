"""Parse Feedipedia datasheets: one record per nutritive-value table (title, DM, ME ruminants)."""
import html as H
import io
import re
import pandas as pd


def parse(path, node):
    h = open(path, encoding="utf-8").read()
    title_page = H.unescape(re.search(r"<title>(.*?)</title>", h, re.S).group(1)).split("|")[0].strip()
    upd = re.findall(r"Last updated on ([0-9/]+)", h)
    out = []
    for m in re.finditer(r"<table", h):
        end = h.find("</table>", m.start())
        seg = h[m.start():end + 8]
        if "Main analysis" not in seg:
            continue
        pre = re.sub(r"<[^>]+>", "\n", h[max(0, m.start() - 800):m.start()])
        lines = [H.unescape(x).strip() for x in pre.split("\n") if x.strip()]
        title = re.sub(r"^.*\d\d:\d\d:\d\d\s*", "", lines[-1]) if lines else ""
        t = pd.read_html(io.StringIO(seg))[0]
        t.columns = ["param", "unit", "avg", "sd", "min", "max", "nb", "x"][: t.shape[1]]
        rec = {"node": node, "page": title_page, "table": title}
        dm = t[t.param.astype(str).str.strip() == "Dry matter"]
        rec["dm_pct"] = pd.to_numeric(dm.avg, errors="coerce").iloc[0] if len(dm) else None
        me = t[t.param.astype(str).str.strip() == "ME ruminants"]
        me = me[me.unit.astype(str).str.contains("MJ/kg DM")]
        if len(me):
            r = me.iloc[0]
            for k in ("avg", "sd", "min", "max", "nb"):
                rec[f"me_{k}"] = pd.to_numeric(r[k], errors="coerce")
        out.append(rec)
    return out

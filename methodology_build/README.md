# Word build of the methodology

The methodology is edited as a Claude Doc. Its built-in Word export prints formulas as raw LaTeX, so the Word file is built here with pandoc, which writes native Word (Office Math) equations.

```
# methodology.md = Markdown export of the doc
python build_docx.py methodology.md ../Green_water_footprint_i-CLEANED_revised_methodology.docx
```

- Display formulas (LaTeX blocks) become numbered Word equations.
- Symbols in the text (GWU_c, AF_c,R, ET0,m, Kc,ini, ...) become inline Word equations.
- `reference.docx` sets the table style (borders, shaded header row).

Requires pandoc ≥ 3.1.

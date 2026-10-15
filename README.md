# Main-figure data and code

Plot-ready data and scripts that redraw the main figures (Figs. 1–5) of the manuscript *Land- and vegetation-conserving deployment of AI data centers enabled by regional renewable planning in China*.

## Run

```bash
pip install -r requirements.txt
python scripts/fig1_cooling.py   # likewise fig2_hourly.py … fig5_layouts.py
```

Figures are written to `outputs/`. Administrative boundary data are not included because of licensing restrictions, so the maps are drawn without boundary lines.

## Contents

- `data/main_figures/`: plot-ready data, one folder per figure (units in its README).
- `scripts/fig1_cooling.py` … `fig5_layouts.py`: one script per figure; `src/plotstyle.py`: shared style and map.

Code: MIT. Data: CC BY 4.0.

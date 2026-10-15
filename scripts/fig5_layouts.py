"""Figure 5: least-land and no-loss layouts and their pathways."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plotstyle import AEA, C, DATA, DOUBLE, china_map, load_npz, save, uplt

COLS = (("free", "Free deployment"), ("region", "Regional quotas"), ("province", "Provincial quotas"))
ROWS = (("least_land", "Least land"), ("no_loss", "Least land, ΔNPP ≥ 0"))
NPP_LEVELS = [0, 25, 50, 100, 200, 300, 400, 600, 800, 1200]
MIX_GROUP_COL = {"PV only": C["pv"], "Wind–PV mix": "#7f7f7f", "Wind only": C["wind"]}

SCEN = {"free": ("Free deployment", "#56B4E9"), "region": ("Regional quotas", "#0072B2"), "province": ("Provincial quotas", "#D55E00")}
BW, BOFF = 0.25, 0.27
KINDS = (("least_land", "Least\nland"), ("no_loss", "ΔNPP\n≥ 0"))
STEPS = ("Least\nland", "Hard\nfootprint", "Barren\nPV", "Grassland\nPV", "ΔNPP\n≥ 0")
LAND = (("data_centre", "Data center", "#8c8c8c"), ("wind", "Wind (permanent)", "#0072B2"),
        ("barren", "PV on barren", "#E69F00"), ("grassland", "PV on grassland", "#009E73"))


def load_layouts() -> dict:
    out = {}
    with open(DATA / "fig5_layouts" / "layouts_60.csv", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out.setdefault((r["scenario"], r["layout"]), []).append((float(r["lon"]), float(r["lat"]), r["supply"]))
    return out


def draw_layout(ax, pts, npp, lat, lon):
    m = china_map(ax, npp, lat, lon, cmap="Greens", levels=NPP_LEVELS, alpha=0.55)
    lo, la, grp = (np.array(v) for v in zip(*pts))
    for g, col in MIX_GROUP_COL.items():
        sel = grp == g
        if sel.any():
            ax.scatter(lo[sel], la[sel], markersize=3.0, color=col, edgecolor="white", linewidth=0.15,
                       label=f"{g} ({sel.sum()})")
    ax.legend(loc="lower left", bbox_to_anchor=(0.19, 0.0), ncols=1, fontsize=4.6, markerscale=2.0, handletextpad=0.1)
    return m


def bar1(ax, x: float, h: float, bottom: float = 0.0, **kw) -> None:
    ax.bar(np.array([x]), np.array([h]), bottom=np.array([bottom]), **kw)


def waterfall(ax, res: dict) -> None:
    for j, (sc, (lab, col)) in enumerate(SCEN.items()):
        a, b, ch = res[f"{sc}_least_land"], res[f"{sc}_no_loss"], res[f"{sc}_change"]
        steps = [ch["hard_loss"], ch["pv"]["barren"], ch["pv"]["grassland"] + ch["pv"].get("shrubland", 0.0)]
        x0 = np.arange(len(STEPS)) + (j - (len(SCEN) - 1) / 2) * BOFF
        bar1(ax, x0[0], a["dnpp"], width=BW, color=col, label=lab)
        level = a["dnpp"]
        for k, s in enumerate(steps, start=1):
            bar1(ax, x0[k], s, bottom=level, width=BW, color=col, alpha=0.45, edgecolor=col, linewidth=0.4)
            if abs(s) >= 0.1:
                ax.text(x0[k], max(level, level + s) + 0.2, f"{s:+.1f}", ha="center", va="bottom", fontsize=4.3, color=col, rotation=90)
            level += s
        ax.scatter(np.array([x0[-1]]), np.array([b["dnpp"]]), marker="_", markersize=40, color=col, linewidth=1.2)
        ax.text(x0[0], a["dnpp"] - 0.3, f"{a['dnpp']:.1f}", ha="center", va="top", fontsize=4.3, color=col)
    ax.axhline(0, color="gray8", linewidth=0.5)
    ax.format(xticks=np.arange(len(STEPS)), xticklabels=STEPS, xticklen=0,
              xrotation=0, ylabel="ΔNPP (10$^4$ tC yr$^{-1}$)", ylim=(-16.5, 3.5), xlim=(-0.6, len(STEPS) - 0.4))
    ax.legend(loc="lr", ncols=1, fontsize=5.2, frame=False)


def group_labels(ax) -> None:
    for j, (lab, col) in enumerate(SCEN.values()):
        ax.text(2 * j + 0.5, -0.2, lab.replace(" ", "\n", 1), transform=ax.get_xaxis_transform(), ha="center",
                va="top", fontsize=5.5, color=col)


def npp_boxes(ax, res: dict, cells: dict) -> None:
    pos, ticks = 0, []
    for sc, (lab, col) in SCEN.items():
        for kind, kname in KINDS:
            v = cells[f"{sc}_{kind}"]
            ax.boxplot([pos], v[:, None], widths=0.55, fillcolor=col, fillalpha=0.25 if kind == "least_land" else 0.7,
                       edgecolor=col, mediancolor="black", whis=(5, 95), marker="none", linewidth=0.5)
            ax.scatter(np.array([pos]), np.array([res[f"{sc}_{kind}"]["hard_npp_weighted"]]), marker="D", markersize=12, color="white",
                       edgecolor="black", linewidth=0.5, zorder=4)
            ticks.append(kname)
            pos += 1
    ax.format(xticks=np.arange(pos), xticklabels=ticks, xticklen=0, xrotation=0, xlim=(-0.6, pos - 0.4),
              ylabel="NPP 2022 of selected cells (gC m$^{-2}$ yr$^{-1}$)", ylim=(0, 1000))
    group_labels(ax)


def land_bars(ax, res: dict) -> None:
    pos, ticks = 0, []
    for sc, (lab, _) in SCEN.items():
        for kind, kname in KINDS:
            r, bottom = res[f"{sc}_{kind}"], 0.0
            for key, name, col in LAND:
                v = r["land_1e4ha"][key] if key in r["land_1e4ha"] else r["pv_area_1e4ha"][key]
                bar1(ax, pos, v, bottom=bottom, width=0.6, color=col, label=name if pos == 0 else None)
                bottom += v
            ax.text(pos, bottom + 0.08, f"{bottom:.2f}", ha="center", va="bottom", fontsize=5)
            ticks.append(kname)
            pos += 1
    ax.format(xticks=np.arange(pos), xticklabels=ticks, xticklen=0, xrotation=0, xlim=(-0.6, pos - 0.4),
              ylabel="Land (10$^4$ ha)", ylim=(0, 1.15 * max(sum(res[f"{sc}_{k}"]["land_1e4ha"].values())
                                                           for sc in SCEN for k, _ in KINDS)))
    group_labels(ax)
    ax.legend(loc="ul", ncols=1, fontsize=5.2, frame=False)


def main() -> None:
    g = load_npz("fig5_layouts")
    lat, lon, npp = g["lat"], g["lon"], g["npp2022"]
    lay = load_layouts()
    res = json.loads((DATA / "fig5_layouts" / "mechanisms.json").read_text(encoding="utf-8"))
    with np.load(DATA / "fig5_layouts" / "mechanisms_cells.npz") as z:
        cells = {k: z[k] for k in z.files}

    fig, axs = uplt.subplots([[1, 2, 3], [4, 5, 6], [7, 8, 9]], proj={i: AEA for i in range(1, 7)}, figwidth=DOUBLE,
                             hratios=(1, 1, 0.78), share=False)
    for r, (kind, _) in enumerate(ROWS):
        for c, (sc, _) in enumerate(COLS):
            m = draw_layout(axs[3 * r + c], lay[(sc, kind)], npp, lat, lon)
    fig.colorbar(m, loc="r", rows=(1, 2), label="NPP 2022 of buildable cells (gC m$^{-2}$ yr$^{-1}$)",
                 length=0.7, ticklabelsize=5.5, labelsize=6)
    axs[:6].format(abcloc="ul", abcborder=True)
    fig.format(toplabels=[n for _, n in COLS], leftlabels=[n for _, n in ROWS] + [""],
               toplabelsize=6.5, leftlabelsize=6.5)
    waterfall(axs[6], res)
    npp_boxes(axs[7], res, cells)
    land_bars(axs[8], res)
    axs[6:].format(abcloc="l")
    print(save(fig, "fig5_layouts"))


if __name__ == "__main__":
    main()

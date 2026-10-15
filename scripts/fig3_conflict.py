"""Figure 3: land saving and vegetation protection at each site."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plotstyle import AEA, DOUBLE, MM, china_map, load_json, load_npz, save, uplt

CLASS_COL = ["#4D9A6A", "#E3B448", "#B5523B"]
CLASS_ONE_LINE = ("Least-land mix avoids loss", "More land avoids loss", "No mix avoids loss")
NPP_EDGES = np.geomspace(5, 1500, 36)
REGION_NAME = {"North": "North China", "Northeast": "Northeast", "East": "East China", "Central": "Central China",
               "Northwest": "Northwest", "Southwest": "Southwest", "South": "South (CSG)"}


class Data:
    def __init__(self):
        g = load_npz("fig3_conflict")
        self.lat, self.lon, self.ok, self.cls, self.npp = g["lat"], g["lon"], g["ok"], g["cls"].astype(int), g["npp"]
        self.regions = load_json("fig3_conflict", "region_counts.json")


def class_shares(d, key: np.ndarray, edges: np.ndarray, min_cells: int = 30) -> tuple[np.ndarray, np.ndarray]:
    k, c = key[d.ok], d.cls[d.ok]
    idx = np.digitize(k, edges) - 1
    share = np.full((3, len(edges) - 1), np.nan)
    for b in range(len(edges) - 1):
        m = idx == b
        if m.sum() >= min_cells:
            share[:, b] = [(c[m] == j).mean() for j in (1, 2, 3)]
    return 0.5 * (edges[1:] + edges[:-1]), share


def stacked(ax, x, share) -> None:
    ok = np.isfinite(share[0])
    lo = np.zeros(ok.sum())
    for j, col in enumerate(CLASS_COL):
        hi = lo + share[j, ok]
        ax.fill_between(x[ok], lo, hi, color=col, linewidth=0)
        lo = hi


def class_map(ax, d) -> None:
    field = np.where(d.ok, d.cls.astype(float), np.nan)
    china_map(ax, field, d.lat, d.lon, cmap=CLASS_COL, levels=[0.5, 1.5, 2.5, 3.5])
    ax.format(title="Site-level conflict")


def region_bars(ax, d) -> None:
    rc = d.regions
    order = sorted(rc, key=lambda r: rc[r]["cells"])
    y = np.arange(len(order))
    left = np.zeros(len(order))
    for c, col in zip(("1", "2", "3"), CLASS_COL):
        v = np.array([rc[r][c] for r in order]) / 1e3
        ax.barh(y, v, left=left, color=col, height=0.68, linewidth=0)
        left += v
    for yi, r in zip(y, order):
        ax.text(left[yi] + 0.2, yi, f"{rc[r]['avoidable_share']:.0%}", va="center", fontsize=5.4)
    ax.format(yticks=y, yticklabels=[REGION_NAME[r] for r in order], ytickminor=False, yticklen=0,
              xlabel="Cells with a feasible mix (thousand); label: avoidable share", xlim=(0, left.max() * 1.15),
              grid=False)


def npp_shares(ax, d) -> None:
    x, s = class_shares(d, d.npp, NPP_EDGES, min_cells=100)
    stacked(ax, x, s)
    ax.format(xscale="log", xlim=(6, 1400), ylim=(0, 1), grid=False,
              xlabel="Baseline NPP of the cell (gC m$^{-2}$ yr$^{-1}$)", ylabel="Share of cells with a feasible mix")


def main() -> None:
    d = Data()
    fig, axs = uplt.subplots(ncols=3, proj={1: AEA}, figwidth=DOUBLE, figheight=62 * MM, wratios=(1.15, 1, 1),
                             share=False)
    class_map(axs[0], d)
    region_bars(axs[1], d)
    npp_shares(axs[2], d)
    share = [(d.cls[d.ok] == c).mean() for c in (1, 2, 3)]
    handles = [axs[2].scatter([], [], marker="s", markersize=24, color=c) for c in CLASS_COL]
    fig.legend(handles, [f"{n} ({p:.0%})" for n, p in zip(CLASS_ONE_LINE, share)], loc="b",
               ncols=3, fontsize=5.8, frame=False, handletextpad=0.3)
    axs.format(abcloc="l")
    axs[0].format(titleloc="ul", titleborder=True, lonlabels="b", latlabels="l")
    print(save(fig, "fig3_conflict"))


if __name__ == "__main__":
    main()

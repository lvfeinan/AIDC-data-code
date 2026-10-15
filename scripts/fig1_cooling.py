"""Figure 1: electricity and water use of the cooling configurations."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plotstyle import AEA, CASE_COLOR, CASE_NAME, DATA, DOUBLE, china_map, load_npz, map_colorbar, save, uplt

CASES = (12, 13, 16, 1, 2, 11, 15)
LIQUID = (12, 13)
MARK = {1: "X", 2: "s", 11: "D", 12: "o", 13: "^", 15: "v", 16: "P"}
LABEL_AT = {12: ("Cold plate +\ndry cooler", (0, 13), "center"), 13: ("Cold plate +\ncooling tower", (0, 8), "center"),
            16: ("Humidified airside", (4, -12), "left"), 2: ("Cooling tower", (0, -11), "center"),
            1: ("Direct evaporative + tower", (8, -4), "left"),
            11: ("Indirect evaporative", (7, 0), "left"), 15: ("Air-cooled chiller", (0, -12), "center")}


class Data:
    def __init__(self):
        g = load_npz("fig1_cooling")
        self.lat, self.lon, self.ok = g["lat"], g["lon"], g["ok"]
        self.pue = {int(c): g["pue"][k] for k, c in enumerate(g["cases"])}
        self.water = g["water_withdrawal_tower_1e4m3"]
        self.city = {}
        with open(DATA / "fig1_cooling" / "city_pue_wue.csv", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                self.city.setdefault(int(r["case"]), []).append((float(r["pue"]), float(r["wue_l_per_kwh_it"])))

    def site(self, case: int, field: str) -> np.ndarray:
        return np.array([p if field == "pue" else w for p, w in self.city[case]])


def maps(axs, d) -> None:
    pue = dict(cmap="YlGnBu", levels=np.arange(1.10, 1.301, 0.02), extend="both")
    for ax, case in zip(axs, (12, 2)):
        m = china_map(ax, d.pue[case], d.lat, d.lon, **pue)
        ax.format(title=f"PUE, {CASE_NAME[case].lower()}")
        map_colorbar(ax, m, "Annual PUE", locator=0.05)
    m = china_map(axs[2], d.water, d.lat, d.lon, cmap="PuBu", levels=np.arange(140, 171, 3), extend="both")
    axs[2].format(title="Water withdrawal, cooling tower")
    map_colorbar(axs[2], m, "10$^4$ m$^3$ yr$^{-1}$ per 100 MW", locator=10)


def plane(ax, d) -> None:
    handles = {}
    for case in CASES:
        p, w = d.site(case, "pue"), d.site(case, "wue")
        col = CASE_COLOR[case]
        ax.scatter(p, w, marker=MARK[case], markersize=9, color="white", edgecolor=col, linewidth=0.6, zorder=2)
        handles[case] = ax.scatter(np.median(p), np.median(w), marker=MARK[case], markersize=34, color=col,
                                   edgecolor="black", linewidth=0.4, zorder=3)
        txt, off, ha = LABEL_AT[case]
        ax.annotate(txt, (np.median(p), np.median(w)), xytext=off, textcoords="offset points", ha=ha, va="center",
                    fontsize=5.2, color=col, fontweight="bold" if case in LIQUID else "normal", linespacing=0.95)
    blank = ax.plot([], [], ls="")[0]
    order = [blank, *(handles[c] for c in LIQUID), blank, *(handles[c] for c in CASES if c not in LIQUID)]
    labels = ["$\\bf{Liquid\\ (cold\\ plate)}$", *(CASE_NAME[c] for c in LIQUID), "$\\bf{Conventional}$",
              *(CASE_NAME[c] for c in CASES if c not in LIQUID)]
    ax.legend(order, labels, loc="ur", ncols=1, fontsize=5.2, handletextpad=0.3)
    ax.text(0.03, 0.62, "Open: 12 Chinese cities (TMYx)\nFilled: median of the 12", transform="axes",
            fontsize=5.5, color="gray7")
    ax.format(xlabel="Annual PUE", ylabel="On-site WUE (L kWh$^{-1}$ IT)", xlim=(1.08, 1.40), ylim=(-0.32, 2.15))


def distributions(ax, d) -> None:
    data = np.column_stack([d.pue[c][d.ok] for c in CASES])
    y = np.arange(1, len(CASES) + 1)
    bodies = ax.violinh(y, data, medians=True, boxpctiles=(25, 75), barpctiles=(5, 95), linewidth=0,
                        boxlinewidth=2.2, barlinewidth=0.6, boxcolor="gray8", barcolor="gray8",
                        boxmarkersize=3, boxmarkerfacecolor="white", boxmarkeredgecolor="black")[0]
    for b, c, yi in zip(bodies, CASES, y):
        b.set_facecolor(CASE_COLOR[c]), b.set_alpha(0.55)
        ax.text(1.085, yi + 0.42, CASE_NAME[c], fontsize=5.8, va="center", color="gray9",
                fontweight="bold" if c in LIQUID else "normal")
    ax.format(yticks=[], ylim=(0.5, len(CASES) + 0.75), xlim=(1.08, 1.40),
              xlabel="Annual PUE across buildable cells (median, IQR, 5–95%)", grid=False)


def main() -> None:
    d = Data()
    fig, axs = uplt.subplots([[1, 1, 2, 2, 3, 3], [4, 4, 4, 5, 5, 5]], proj={1: AEA, 2: AEA, 3: AEA},
                             figwidth=DOUBLE, hratios=(1, 0.95), share=False)
    maps(axs[:3], d)
    plane(axs[3], d)
    distributions(axs[4], d)
    axs[:3].format(abcloc="ul", titleloc="ul", titleborder=True, abcborder=True)
    axs[3:].format(abcloc="l")
    print(save(fig, "fig1_cooling"))


if __name__ == "__main__":
    main()

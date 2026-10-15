"""Figure 2: hourly matching between wind and PV supply and the computing load."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plotstyle import AEA, C, DOUBLE, MIX_COLORS, MIX_NAME, china_map, load_json, load_npz, map_colorbar, save, uplt


class Data:
    def __init__(self):
        g = load_npz("fig2_hourly")
        s = load_json("fig2_hourly", "series.json")
        self.lat, self.lon, self.ok = g["lat"], g["lon"], g["ok"]
        self.m_pv, self.m_ad, self.idx = g["match_pv"], g["match_adaptive"], g["adaptive_mix"].astype(int)
        self.mixes, self.wind_min_cf, self.site, self.load = s["mixes"], s["wind_min_cf"], s["site"], s["load_mw"]
        self.gen = {k: np.array(v) for k, v in s["week_supply_mw"].items()}
        self.phi = np.array(s["phi"])
        self.carbon = s["carbon"]
        self.storage = s["storage"]


def maps(axs, d) -> None:
    green = dict(cmap="Greens", levels=np.arange(0.30, 0.751, 0.05), extend="both")
    for ax, f, t in ((axs[0], d.m_pv, "Hourly green match, PV only"), (axs[1], d.m_ad, "Hourly green match, adaptive mix")):
        m = china_map(ax, f, d.lat, d.lon, **green)
        ax.format(title=t)
        map_colorbar(ax, m, "Same-hour wind and PV share of load", locator=0.1)
    china_map(axs[2], np.where(d.ok, d.idx.astype(float), np.nan), d.lat, d.lon, cmap=MIX_COLORS,
              levels=np.arange(-0.5, 5))
    axs[2].format(title="Adaptive mix chosen per cell")
    handles = [axs[2].scatter([], [], marker="s", markersize=22, color=c) for c in MIX_COLORS]
    axs[2].legend(handles, [MIX_NAME[m] for m in d.mixes], loc="b", ncols=3, handletextpad=0.2, columnspacing=0.8,
                  title=f"Wind allowed where net capacity factor ≥ {d.wind_min_cf:.3f}", titlefontsize=5.5)


def week(ax, d) -> None:
    hrs = np.arange(len(next(iter(d.gen.values()))))
    ax.axhline(d.load, color="black", linewidth=0.8, label=f"Data-center load, annual mean {d.load:.0f} MW")
    for (name, g), c in zip(d.gen.items(), (C["pv"], C["wind"])):
        ax.plot(hrs, g, color=c, linewidth=0.9, label=f"Supply, {name}")
        ax.fill_between(hrs, np.minimum(g, d.load), d.load, color=c, alpha=0.13, linewidth=0)
    top = max(max(g.max() for g in d.gen.values()), d.load) * 1.45
    ax.legend(loc="ur", ncols=3, handlelength=1.5)
    ax.format(xlim=(0, len(hrs) - 1), ylim=(0, top), xticks=np.arange(0, len(hrs) + 1, 24), xtickminor=False,
              xticklabels=[f"Day {k + 1}" for k in range(len(hrs) // 24 + 1)],
              ylabel="MW (one 100 MW IT data center)",
              title=f"{d.site[0]} hub, April 2023; shading marks hours drawn from the grid", titleloc="ul",
              titlesize=5.8, titlecolor="gray7")


def carbon(ax, d) -> None:
    for lab, cv in d.carbon.items():
        c = cv["color"]
        ax.plot(d.phi, cv["q50"], color=c, linewidth=1.0, linestyle=cv["ls"], label=lab)
        ax.fill_between(d.phi, cv["q25"], cv["q75"], color=c, alpha=0.12, linewidth=0)
        ax.scatter(cv["util"], cv["at_util"], markersize=14, color=c, edgecolor="white", linewidth=0.5, zorder=4)
    ax.axhline(1, color="black", linewidth=0.5, linestyle=":")
    h, l = ax.get_legend_handles_labels()
    h.append(ax.scatter([], [], markersize=14, color="gray6", edgecolor="white"))
    l.append("At 2023 provincial utilization\n(reference point)")
    ax.legend(h, l, loc="ur", ncols=1, bbox_to_anchor=(1.0, 0.9))
    ax.format(xlim=(0, 1.02), xticks=np.linspace(0, 1, 6), xtickminor=False,
              xticklabels=["0\n(hourly gap)", "0.2", "0.4", "0.6", "0.8", "1\n(annual)"],
              xlabel="Share of surplus wind/PV absorbed by the grid",
              ylabel="Grid CO$_2$ ÷ annual-basis CO$_2$")


def storage(ax, d) -> None:
    st = d.storage
    for (m, y), c in zip(st["mix"].items(), MIX_COLORS):
        ax.plot(st["hours"], y, marker="o", markersize=2.5, linewidth=1.0, color=c, label=MIX_NAME[m])
    ax.axhline(0.8, color="black", linewidth=0.6, linestyle="--")
    ax.text(0.2, 0.805, "annual target 80%", fontsize=5.3, va="bottom")
    ax.legend(loc="lr", ncols=1)
    ax.format(xticks=st["hours"], xtickminor=False, ylim=(0.3, 0.85), yloc="right", ylabelloc="right",
              xlabel="On-site battery (hours of mean load)", ylabel="Hourly green match (median of cells)")


def main() -> None:
    d = Data()
    fig, axs = uplt.subplots([[1, 1, 2, 2, 3, 3], [4, 4, 4, 4, 4, 4], [5, 5, 5, 6, 6, 6]],
                             proj={1: AEA, 2: AEA, 3: AEA}, figwidth=DOUBLE, hratios=(1, 0.55, 0.8), share=False)
    maps(axs[:3], d)
    week(axs[3], d)
    carbon(axs[4], d)
    storage(axs[5], d)
    axs[:3].format(abcloc="ul", titleloc="ul", titleborder=True, abcborder=True)
    axs[3:].format(abcloc="l")
    print(save(fig, "fig2_hourly"))


if __name__ == "__main__":
    main()

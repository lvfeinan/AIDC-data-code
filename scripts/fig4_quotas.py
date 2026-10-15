"""Figure 4: deployment quotas, hub-node shares, land and vegetation."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Rectangle

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from plotstyle import C, DOUBLE, MM, load_json, save, uplt

STYLE = {"free": ("Free deployment", "#56B4E9", "--", "s"),
         "region": ("Regional quotas", "#0072B2", "-", "o"),
         "province": ("Provincial quotas", "#D55E00", "-", "D")}
BARS = ("free", "region", "province")
TICK = {"free": "F", "region": "R", "province": "P"}
SHARES = (0, 60, 80, 100)
LAND = (("data_centre", "Data center", "#8c8c8c"), ("wind", "Wind (permanent)", C["wind"]),
        ("pv_barren", "PV on barren land", C["pv"]), ("pv_grassland", "PV on grassland", "#009E73"))
REGIONS = (("Northwest", "#8c510a"), ("North", "#d8b365"), ("Northeast", "#f6e8c3"), ("East", "#c7eae5"),
           ("Central", "#5ab4ac"), ("Southwest", "#01665e"), ("South", "#bdbdbd"))
WIDTH, GAP = 0.25, 0.28


def frontier(ax, fr) -> None:
    for sc, (lab, col, ls, mk) in STYLE.items():
        f = fr[sc]
        x, y = np.array(f["land"]), np.array(f["dnpp"])
        ax.plot(x, y, color=col, linestyle=ls, linewidth=1.1 if sc != "free" else 0.8, label=lab, zorder=2)
        ax.scatter(x, y, marker="o", markersize=4, color=col, linewidth=0, zorder=3)
        ll, nl = f["least_land"], f["no_loss"]
        ax.scatter(np.array([ll["land"]]), np.array([ll["dnpp"]]), marker=mk, markersize=16, color="white",
                   edgecolor=col, linewidth=0.9, zorder=4)
        ax.scatter(np.array([nl["land"]]), np.array([nl["dnpp"]]), marker="*", markersize=50, color=col,
                   edgecolor="white", linewidth=0.4, zorder=5)
        if sc != "free":
            ax.annotate(f"+{(nl['land'] / ll['land'] - 1) * 100:.0f}% land", (nl["land"], nl["dnpp"]),
                        xytext=((-3, 5) if sc == "region" else (4, -9)), ha=("right" if sc == "region" else "left"),
                        textcoords="offset points", fontsize=5.4, color=col)
    ax.axhline(0, color="gray6", linewidth=0.5, linestyle=":", zorder=1)
    ax.format(xlabel="Land occupied (10$^4$ ha)", ylabel="ΔNPP (10$^4$ tC yr$^{-1}$)", xlim=(3, 14), ylim=(-17, 8),
              grid=False)
    ax.text(0.03, 0.97, "≥ 60% in hub-node provinces", transform="axes", va="top", fontsize=5.6)
    ax.legend(loc="lr", ncols=1, fontsize=5.2, frame=False)


def positions():
    return {(s, sc): k + (j - (len(BARS) - 1) / 2) * GAP for k, s in enumerate(SHARES) for j, sc in enumerate(BARS)}


def share_axis(ax, ylabel: str, ylim) -> None:
    pos = positions()
    ax.format(xticks=list(pos.values()), xticklabels=[TICK[sc] for _, sc in pos],
              xtickminor=False, xticklen=0, xlabel="Minimum share in hub-node provinces", ylabel=ylabel,
              xlim=(-0.6, len(SHARES) - 0.4), ylim=ylim, grid=False, xlabelpad=13)
    for lab, (_, sc) in zip(ax.get_xticklabels(), pos):
        lab.set_color(STYLE[sc][1]), lab.set_fontweight("bold"), lab.set_fontsize(4.8)
    for k, s in enumerate(SHARES):
        ax.text(k, -0.085, f"{s}%", transform=ax.get_xaxis_transform(), ha="center", va="top", fontsize=6)


def land_bars(ax, L) -> None:
    for (s, sc), x in positions().items():
        nl, ll = L[f"{sc}|{s}|no_loss"], L[f"{sc}|{s}|least_land"]
        if nl is None:
            ax.scatter(np.array([x]), np.array([1.0]), marker="x", markersize=16, color=STYLE[sc][1])
            continue
        bottom = 0.0
        for key, _, col in LAND:
            h = nl["land"][key]
            ax.add_patch(Rectangle((x - WIDTH / 2, bottom), WIDTH, h, facecolor=col, edgecolor="white", linewidth=0.3))
            bottom += h
        ax.plot([x - WIDTH / 2 - 0.02, x + WIDTH / 2 + 0.02], [ll["land_total"]] * 2, color="black", linewidth=0.8)
    handles = [Rectangle((0, 0), 1, 1, facecolor=col) for _, _, col in LAND]
    handles.append(ax.plot([], [], color="black", linewidth=0.9)[0])
    ax.legend(handles, [lab for _, lab, _ in LAND] + ["Least land, no ΔNPP limit"], loc="ul", ncols=1, fontsize=5.0,
              frame=False)
    share_axis(ax, "Land of the ΔNPP ≥ 0 layout (10$^4$ ha)", (0, 15))


def region_bars(ax, L) -> None:
    for (s, sc), x in positions().items():
        nl = L[f"{sc}|{s}|no_loss"]
        if nl is None:
            ax.scatter(np.array([x]), np.array([5.0]), marker="x", markersize=16, color=STYLE[sc][1])
            continue
        n = sum(nl["regions"].values())
        bottom = 0.0
        for r, col in REGIONS:
            h = nl["regions"].get(r, 0) / n * 100
            ax.add_patch(Rectangle((x - WIDTH / 2, bottom), WIDTH, h, facecolor=col, edgecolor="white", linewidth=0.3))
            bottom += h
        ax.text(x, 101.5, f"{nl['access']:.0f}", ha="center", va="bottom", fontsize=4.4, color="gray8")
    handles = [Rectangle((0, 0), 1, 1, facecolor=col) for _, col in REGIONS]
    ax.legend(handles, [r for r, _ in REGIONS], loc="r", ncols=1, fontsize=5.0, frame=False)
    share_axis(ax, "AIDCs of the ΔNPP ≥ 0 layout (%)", (0, 108))
    ax.format(yticks=[0, 25, 50, 75, 100])


def main() -> None:
    fr = load_json("fig4_quotas", "frontiers_60.json")
    L = load_json("fig4_quotas", "layouts.json")
    fig, axs = uplt.subplots(ncols=3, figwidth=DOUBLE, figheight=57.9 * MM, wratios=(1, 1, 1.12), share=False)
    frontier(axs[0], fr)
    land_bars(axs[1], L)
    region_bars(axs[2], L)
    axs.format(abcloc="l")
    print(save(fig, "fig4_quotas"))


if __name__ == "__main__":
    main()

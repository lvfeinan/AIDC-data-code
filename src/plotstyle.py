"""Shared figure style, constants and the China map used by every main-figure script.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import cartopy.crs as ccrs
import numpy as np
import ultraplot as uplt
from shapely.geometry import shape
from shapely.ops import unary_union

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "main_figures"
OUT = ROOT / "outputs"
BOUNDARY = ROOT / "data" / "boundaries" / "china_provinces_100000_full.json"

MM = 1 / 25.4
DOUBLE = 183 * MM

C = dict(liquid="#0072B2", tower="#D55E00", air="#E69F00", iec="#009E73", hum="#CC79A7", cpt="#56B4E9", dec="#882255",
         pv="#E69F00", wind="#0072B2")
CASE_COLOR = {1: C["dec"], 2: C["tower"], 11: C["iec"], 12: C["liquid"], 13: C["cpt"], 15: C["air"], 16: C["hum"]}
CASE_NAME = {1: "Direct evaporative + tower", 2: "Cooling tower", 11: "Indirect evaporative", 12: "Cold plate + dry cooler",
             13: "Cold plate + tower", 15: "Air-cooled chiller", 16: "Humidified airside + air chiller"}
MIX_NAME = {"pv": "PV only", "w30": "30% wind", "hybrid": "50% wind", "w70": "70% wind", "wind": "Wind only"}
MIX_COLORS = ["#E69F00", "#F0C987", "#BDBDBD", "#7FB3D9", "#0072B2"]

AEA = ccrs.AlbersEqualArea(central_longitude=105, standard_parallels=(25, 47))      # metres
PC = ccrs.PlateCarree()
MAIN_EXTENT = (-2700, 2350, 1600, 6000)      # km in Albers: x0, x1, y0, y1
SCS_EXTENT = (100, 2000, 300, 2700)          # South China Sea inset (Albers km)
SCS_H = 0.27                                 # inset height as a fraction of the main map

uplt.rc.update({
    "font.name": "Arial", "font.size": 7, "font.smallsize": 6, "font.largesize": 7,
    "abc": "a", "abc.size": 8, "abc.weight": "bold", "title.size": 6.5, "label.size": 6.5,
    "meta.width": 0.5, "tick.len": 2.5, "tick.labelsize": 6, "grid": False, "gridminor": False,
    "legend.fontsize": 5.5, "legend.frameon": False, "colorbar.width": "1.6mm",
    "pdf.fonttype": 42, "ps.fonttype": 42, "axes.unicode_minus": False, "savefig.facecolor": "white",
    "mathtext.fontset": "custom", "mathtext.rm": "Arial", "mathtext.it": "Arial:italic", "mathtext.bf": "Arial:bold",
    "mathtext.sf": "Arial", "mathtext.default": "regular",
})

GRAT = dict(lonlines=10, latlines=10, lonlabels="t", latlabels="l", labelsize=5, labelpad=1.5,
            gridcolor="#BBBBBB", gridalpha=1, gridlinewidth=0.3, rc_kw={"grid": True, "gridminor": False})
NATION_MIN_DEG2 = 0.5
BORDER = {"province": ("gray7", 0.2), "nation": ("gray9", 0.6), "dash": ("gray9", 0.5)}


def load_npz(fig: str) -> dict:
    with np.load(DATA / fig / "grid.npz") as z:
        return {k: z[k] for k in z.files}


def load_json(fig: str, name: str) -> dict:
    return json.loads((DATA / fig / name).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def borders() -> tuple[list, list, list]:
    if not BOUNDARY.exists():                      # boundaries are not redistributed; maps are drawn without them
        return [], [], []
    d = json.loads(BOUNDARY.read_text(encoding="utf-8"))
    prov, dash = [], []
    for f in d["features"]:
        (dash if f["properties"].get("adcode") == "100000_JD" else prov).append(shape(f["geometry"]))
    union = unary_union([g.buffer(0) for g in prov])
    return prov, dash, [g for g in getattr(union, "geoms", [union]) if g.area >= NATION_MIN_DEG2]


def _metres(extent: tuple) -> list:
    return [v * 1e3 for v in extent]


def _draw(ax, field, lat, lon, dash: bool, **kw):
    prov, dash_geoms, nation = borders()
    m = ax.pcolormesh(lon, lat, field, rasterized=True, **kw) if field is not None else None
    layers = [("province", prov), ("nation", nation)] + ([("dash", dash_geoms)] if dash else [])
    for kind, geoms in layers:
        if not geoms:
            continue
        color, lw = BORDER[kind]
        ax.add_geometries(geoms, crs=PC, facecolor="none", edgecolor=color, linewidth=lw)
    return m


def china_map(ax, field: np.ndarray | None, lat, lon, inset: bool = True, **kw):
    m = _draw(ax, field, lat, lon, dash=False, **kw)
    ax.set_extent(_metres(MAIN_EXTENT), crs=AEA)
    ax.format(**GRAT)
    if inset:
        (x0, x1, y0, y1), (s0, s1, t0, t1) = MAIN_EXTENT, SCS_EXTENT
        w = SCS_H * (y1 - y0) * (s1 - s0) / (t1 - t0) / (x1 - x0)
        ia = ax.inset_axes([0, 0, w, SCS_H], proj=AEA, zoom=False)
        _draw(ia, field, lat, lon, dash=True, **kw)
        ia.set_extent(_metres(SCS_EXTENT), crs=AEA)
        ia.format(lonlines=[], latlines=[], labels=False)
    return m


def map_colorbar(ax, m, label: str, **kw):
    return ax.colorbar(m, loc="b", label=label, length=0.8, ticklabelsize=5.5, labelsize=6, **kw)


def save(fig, name: str) -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    paths = [OUT / f"{name}.pdf", OUT / f"{name}.png"]
    fig.save(paths[0])
    fig.save(paths[1], dpi=600)
    uplt.close(fig)
    return paths

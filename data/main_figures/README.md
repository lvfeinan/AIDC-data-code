# Plot-ready data for the main figures

One folder per figure. Gridded data are `.npz` files on the 0.1° grid over China (`lat`, `lon` at cell centers, NaN outside the cells shown); the other files are `.csv` or `.json`.

| Folder | Figure |
|---|---|
| `fig1_cooling/` | Fig. 1, electricity and water use of the cooling configurations |
| `fig2_hourly/` | Fig. 2, hourly matching of wind and PV supply with the load |
| `fig3_conflict/` | Fig. 3, land and vegetation trade-off in each cell |
| `fig4_quotas/` | Fig. 4, land cost under the quota scenarios |
| `fig5_layouts/` | Fig. 5, layouts and their vegetation change |

Units: land in $10^4\ \mathrm{ha}$, NPP in $\mathrm{gC\ m^{-2}\ yr^{-1}}$, NPP change in $10^4\ \mathrm{tC\ yr^{-1}}$.

License: CC BY 4.0.

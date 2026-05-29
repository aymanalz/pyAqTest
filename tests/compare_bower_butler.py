"""
Build a one-page PDF comparing Bouwer–Rice vs Butler slug-test outputs.

``estimated_conductivity.csv`` has a ``test_name`` column listing every run.
For each ``test_name``, the fit plot is ``fit_plots/{test_name}.png`` (same
basename). The wide batch CSV has a ``test_id`` column matching ``test_name``.

Layout: top row — two stacked tables on the left (Project Information; then
Aquifer and Well data), company logo on the right; fit plots below; bottom
row has two Solution tables. Default logo: ``assets/gsi.png`` under the repo
root.

Output PDFs go under ``PdfPages/`` (or ``OUTPUT`` below). Edit ``RUN_CONFIG`` in this file.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")  # PDF-only; avoids Qt/qtagg when running from IDE

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.axes import Axes
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.gridspec import GridSpec
from matplotlib import image as mpimg


DEFAULT_BUTLER_DIR = r"C:\workspace\projects\pump_tests\WRD_Slug_Data\output_butler"
DEFAULT_BOUWER_DIR = r"C:\workspace\projects\pump_tests\WRD_Slug_Data\output_Bouwer_Rice"
DEFAULT_BATCH_BOUWER = (
    r"C:\workspace\projects\pump_tests\WRD_Slug_Data\wrd_batch_data_clean_Bouwer_Rice.csv"
)
DEFAULT_BATCH_BUTLER = (
    r"C:\workspace\projects\pump_tests\WRD_Slug_Data\wrd_batch_data_clean_butler.csv"
)

FT_PER_SEC_TO_FT_PER_DAY = 86400.0

PDF_DIR_NAME = "PdfPages"

# US Letter landscape (inches): width × height
FIG_SIZE_LANDSCAPE_IN = (11.0, 8.5)

_REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOGO_PATH = str(_REPO_ROOT / "assets" / "gsi.png")

# Project information (defaults; override in RUN_CONFIG); typical WRD report header.
DEFAULT_COMPANY = "GSI"
DEFAULT_CLIENT = "WRD"
DEFAULT_PROJECT = "10557"
DEFAULT_LOCATION = "Water Replenishment District"

# --- Edit these before running (no command-line arguments) ---
RUN_CONFIG = {
    "test_name": "Car1_2_T1",  # ignored when run_all is True
    "run_all": False,  # True -> one PdfPages/compare_<test_name>.pdf per common test
    "output": "",  # bare name -> PdfPages/<name>; empty -> compare_<test_name>.pdf
    "butler_dir": DEFAULT_BUTLER_DIR,
    "bouwer_dir": DEFAULT_BOUWER_DIR,
    "batch_butler": DEFAULT_BATCH_BUTLER,
    "batch_bouwer": DEFAULT_BATCH_BOUWER,
    "company": DEFAULT_COMPANY,
    "client": DEFAULT_CLIENT,
    "project": DEFAULT_PROJECT,
    "location": DEFAULT_LOCATION,
    "logo": DEFAULT_LOGO_PATH,
}

# --- Report palette (professional PDF: slate neutrals + restrained teal accent) ---
# Slug test title row (project table)
TITLE_ROW_BG = "#f4f6fa"
TITLE_ROW_TEXT = "#1c2833"

# Section header bands (full row)
SECTION_BG_NEUTRAL = "#e8ecf2"  # project / aquifer
SECTION_BG_WELL = "#e9edf4"  # well block (subtle shift from neutral)
SECTION_BG_SOLUTION = "#c5e8e4"  # results: muted teal (print-friendly)
SECTION_HEADER_TEXT = "#2c3e50"  # slate for section labels

# Data cells: label columns vs value columns
FIELD_NAME_COLOR = "#455a64"  # blue-grey
VALUE_TEXT_COLOR = "#37474f"  # charcoal body

# Table bottom rule (softer than pure black)
REPORT_RULE_COLOR = "#455a64"

# Top strip of each fit cell: base fraction for method label band (see also extra mm below).
FIT_PLOT_METHOD_BAND_FRAC = 0.06

# Add this much to the white method band height (each Bouwer / Butler header) [mm].
FIT_METHOD_BAND_EXTRA_MM = 0.2

# Method name in the method band (pt).
FIT_METHOD_LABEL_FONTSIZE = 9

# Bouwer–Rice / Butler label strip fill (no outline).
FIT_METHOD_BAND_BG = "#fff0e0"

# Nudge the Bouwer / Butler fit column (title band + image) upward on the page [mm].
FIT_ROW_SHIFT_MM = 3.0

# Vertical gap between the method band and the plot below it [mm].
FIT_METHOD_BAND_PLOT_GAP_MM = 2.0

# Must match ``GridSpec`` in ``plot_comparison_page`` (fit plots = row index 1).
_FIT_GRID_TOP = 0.96
_FIT_GRID_BOTTOM = 0.04
PAGE_GRID_HEIGHT_RATIOS = (0.98, 1.08, 0.42)
_FIT_ROW_INDEX = 1

# Inner subgrid (fit plots + solution tables): small gap between those two rows only.
FIT_SOLUTION_ROW_HSPACE = 0.06


def _method_band_fracs_with_extra_mm(
    fig: plt.Figure, base_band_frac: float, extra_mm: float
) -> tuple[float, float]:
    """
    Return ``(title_band_frac, image_frac)`` for the nested subgrid inside each fit cell,
    with ``extra_mm`` added to the physical height of the title band.
    """
    gh_mm = fig.get_figheight() * 25.4
    s = sum(PAGE_GRID_HEIGHT_RATIOS)
    row_frac = PAGE_GRID_HEIGHT_RATIOS[_FIT_ROW_INDEX] / s
    cell_h_mm = gh_mm * (_FIT_GRID_TOP - _FIT_GRID_BOTTOM) * row_frac
    new_band_mm = base_band_frac * cell_h_mm + extra_mm
    band_frac = new_band_mm / cell_h_mm
    band_frac = min(band_frac, 0.48)
    h_img = 1.0 - band_frac
    if h_img < 0.30:
        h_img = 0.30
        band_frac = 1.0 - h_img
    return band_frac, h_img


def _shift_axes_up_mm(fig: plt.Figure, axes: list, mm: float) -> None:
    """Move axes upward by ``mm`` millimeters (normalized to figure height)."""
    if mm <= 0 or not axes:
        return
    dy = (mm / 25.4) / fig.get_figheight()
    for ax in axes:
        pos = ax.get_position()
        ax.set_position([pos.x0, pos.y0 + dy, pos.width, pos.height])


def _style_method_band_axes(ax: Axes) -> None:
    """Light fill for the method name strip; no border.

    Do not use ``axis('off')``: it hides ``ax.patch``, so the face color never paints.
    """
    ax.set_facecolor(FIT_METHOD_BAND_BG)
    ax.patch.set_facecolor(FIT_METHOD_BAND_BG)
    ax.patch.set_alpha(1.0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.tick_params(left=False, bottom=False, length=0)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    for spine in ax.spines.values():
        spine.set_visible(False)


def _gap_method_band_and_plot_mm(fig: plt.Figure, ax_img, mm: float) -> None:
    """
    After layout, shrink the image axes from the top by ``mm`` (figure bottom fixed)
    so a gap opens between the method band and the plot.
    """
    if mm <= 0 or ax_img is None:
        return
    dy = (mm / 25.4) / fig.get_figheight()
    pi = ax_img.get_position()
    ax_img.set_position([pi.x0, pi.y0, pi.width, max(pi.height - dy, 1e-3)])


def draw_fit_plot_pair(
    fig: plt.Figure,
    gs_row_col,
    path_img: str,
    method: str,
) -> None:
    """
    Highlighted top band with method name; lower panel shows the PNG as stored on disk.
    """
    if not os.path.isfile(path_img):
        ax = fig.add_subplot(gs_row_col)
        _style_method_band_axes(ax)
        ax.text(
            0.5,
            0.5,
            f"Missing:\n{path_img}",
            ha="center",
            va="center",
            fontsize=8,
            color=SECTION_HEADER_TEXT,
            transform=ax.transAxes,
        )
        _shift_axes_up_mm(fig, [ax], FIT_ROW_SHIFT_MM)
        return

    band_frac, h_img = _method_band_fracs_with_extra_mm(
        fig, FIT_PLOT_METHOD_BAND_FRAC, FIT_METHOD_BAND_EXTRA_MM
    )
    gs_pair = gs_row_col.subgridspec(
        2,
        1,
        height_ratios=[band_frac, h_img],
        hspace=0.0,
    )
    ax_title = fig.add_subplot(gs_pair[0, 0])
    _style_method_band_axes(ax_title)
    ax_title.text(
        0.04,
        0.5,
        method.strip(),
        ha="left",
        va="center",
        fontsize=FIT_METHOD_LABEL_FONTSIZE,
        fontweight="bold",
        color=SECTION_HEADER_TEXT,
        transform=ax_title.transAxes,
    )

    ax_img = fig.add_subplot(gs_pair[1, 0])
    ax_img.set_facecolor("white")
    ax_img.axis("off")
    ax_img.set_frame_on(False)
    im = np.asarray(mpimg.imread(path_img))
    ax_img.imshow(im)
    _shift_axes_up_mm(fig, [ax_title, ax_img], FIT_ROW_SHIFT_MM)
    _gap_method_band_and_plot_mm(fig, ax_img, FIT_METHOD_BAND_PLOT_GAP_MM)


def load_batch_table(path: str) -> pd.DataFrame:
    """Wide batch CSV -> one row per test (columns = field names)."""
    df = pd.read_csv(path)
    if "field" not in df.columns:
        raise ValueError(f"Expected a 'field' column in {path}")
    df = df.set_index("field").transpose()
    # Row index is 0,1,...; ``test_id`` is already a column from the ``field`` row.
    return df.reset_index(drop=True)


def load_estimated(path: str) -> pd.DataFrame:
    return pd.read_csv(path, index_col=0)


def list_test_names_intersection(butler_dir: str, bouwer_dir: str) -> list[str]:
    """``test_name`` values present in both ``estimated_conductivity.csv`` files."""
    p_bt = os.path.join(butler_dir, "estimated_conductivity.csv")
    p_br = os.path.join(bouwer_dir, "estimated_conductivity.csv")
    bt = set(load_estimated(p_bt)["test_name"].astype(str).str.strip())
    br = set(load_estimated(p_br)["test_name"].astype(str).str.strip())
    common = sorted(bt & br, key=str.lower)
    return common


def resolve_pdf_output_path(test_name: str, output_arg: str) -> Path:
    """
    Default: ``PdfPages/compare_{test_name}.pdf`` under cwd.
    If ``output_arg`` is a bare filename, place it under ``PdfPages/``.
    If it is a relative path with a parent or an absolute path, use as-is
    (parent dirs are created).
    """
    o = output_arg.strip()
    if not o:
        root = Path.cwd() / PDF_DIR_NAME
        root.mkdir(parents=True, exist_ok=True)
        return root / f"compare_{test_name}.pdf"

    p = Path(o)
    if p.is_absolute() or p.parent != Path("."):
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    root = Path.cwd() / PDF_DIR_NAME
    root.mkdir(parents=True, exist_ok=True)
    return root / p.name


def fmt_cell(v: Any) -> str:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return ""
    if isinstance(v, (float, np.floating)):
        if abs(v) >= 1e4 or (abs(v) > 0 and abs(v) < 1e-3):
            return f"{v:.6g}"
        return f"{v:.6f}".rstrip("0").rstrip(".")
    s = str(v).strip()
    return s if s else ""


def fmt_ft(v: Any) -> str:
    if v is None or v == "":
        return ""
    try:
        x = float(v)
        if np.isnan(x):
            return ""
        return f"{x:.4g} ft"
    except (TypeError, ValueError):
        s = str(v).strip()
        return s if s else ""


def fmt_test_date(raw: Any) -> str:
    if raw is None or (isinstance(raw, float) and np.isnan(raw)):
        return ""
    try:
        dt = pd.to_datetime(raw)
        return dt.strftime("%m/%d/%y")
    except Exception:
        s = str(raw).strip()
        if " " in s:
            return s.split()[0]
        return s


def slug_test_number(test_name: str) -> int | None:
    m = re.search(r"_T(\d+)$", str(test_name).strip(), flags=re.I)
    if m:
        return int(m.group(1))
    return None


def report_header_title(well_name: str, test_name: str) -> str:
    wn = fmt_cell(well_name).replace(" ", "")
    head = wn.upper() if wn else str(test_name).split("_T")[0].upper()
    n = slug_test_number(test_name)
    if n is not None:
        return f"{head} SLUG TEST NO. {n}"
    return f"{head} SLUG TEST — {test_name}"


def batch_get(row: pd.Series | None, key: str) -> Any:
    if row is None or key not in row.index:
        return None
    return row[key]


def k_ft_day_from_series(s: pd.Series) -> float | None:
    hc = s.get("hydraulic_conductivity")
    if hc is None:
        return None
    try:
        v = float(hc)
        if np.isnan(v):
            return None
        return v * FT_PER_SEC_TO_FT_PER_DAY
    except (TypeError, ValueError):
        return None


def build_project_information_rows(
    test_name: str,
    batch_row: pd.Series | None,
    *,
    company: str,
    client: str,
    project: str,
    location: str,
) -> list[list[str]]:
    """Table 1: title + Project Information only."""
    well = fmt_cell(batch_get(batch_row, "well_name"))
    tdate = fmt_test_date(batch_get(batch_row, "Test Date"))
    top = report_header_title(well or "", test_name)
    return [
        [top, ""],
        ["PROJECT INFORMATION", ""],
        ["Company", company],
        ["Client", client],
        ["Project", project],
        ["Location", location],
        ["Test Well", well],
        ["Test Date", tdate],
    ]


def build_aquifer_well_rows(batch_row: pd.Series | None) -> list[list[str]]:
    """Table 2: Aquifer Data and Well Data (no project title row). Four columns: label, value, label, value."""
    well = fmt_cell(batch_get(batch_row, "well_name"))
    wtd = fmt_ft(batch_get(batch_row, "water_table_depth"))
    thick = fmt_ft(batch_get(batch_row, "aquifer_thickness"))
    aniso = fmt_cell(batch_get(batch_row, "anisotropy"))
    wr = fmt_ft(batch_get(batch_row, "well_radius"))
    cr = fmt_ft(batch_get(batch_row, "casing_radius"))
    sl = fmt_ft(batch_get(batch_row, "screen_length"))
    std = fmt_ft(batch_get(batch_row, "screen_top_depth"))
    well_block = f"WELL DATA ({well})" if well else "WELL DATA"

    def nz(x: str) -> str:
        return x if x else "—"

    return [
        ["AQUIFER DATA", "", "", ""],
        [
            "Water Table Depth",
            nz(wtd),
            "Anisotropy Ratio (Kz/Kr)",
            nz(aniso),
        ],
        ["Saturated Thickness", nz(thick), "", ""],
        [well_block, "", "", ""],
        ["Well Radius", nz(wr), "Casing Radius", nz(cr)],
        ["Screen Length", nz(sl), "Screen Top Depth", nz(std)],
    ]


def build_solution_rows(est_series: pd.Series, method_label: str) -> list[list[str]]:
    """Solution block only (per method)."""
    k_day = k_ft_day_from_series(est_series)
    k_str = f"{k_day:.4g} ft/day" if k_day is not None else ""

    r2 = est_series.get("R_squared")
    try:
        r2f = float(r2)
        r2_str = f"{r2f:.4f}" if r2 is not None and not (isinstance(r2f, float) and np.isnan(r2f)) else ""
    except (TypeError, ValueError):
        r2_str = fmt_cell(r2)

    rmse = est_series.get("RMSE")
    try:
        rmsef = float(rmse)
        rmse_str = f"{rmsef:.6g}" if rmse is not None and not (isinstance(rmsef, float) and np.isnan(rmsef)) else ""
    except (TypeError, ValueError):
        rmse_str = fmt_cell(rmse)

    def nz(x: str) -> str:
        return x if x else "—"

    return [
        ["SOLUTION", ""],
        ["Estimated K", nz(k_str)],
        ["Solution Method", method_label],
        ["R²", nz(r2_str)],
        ["RMSE", nz(rmse_str)],
    ]


def _strip_table_cell_edges(tbl) -> None:
    """Remove matplotlib table grid lines (vertical/horizontal cell borders)."""
    for cell in tbl.get_celld().values():
        cell.set_linewidth(0)
        cell.set_edgecolor("none")


def _add_table_bottom_border(tbl, nrows: int, ncols: int) -> None:
    """Single line along the bottom edge of the table (last row)."""
    last = nrows - 1
    for col in range(ncols):
        cell = tbl.get_celld().get((last, col))
        if cell is None:
            continue
        cell.set_linewidth(0.85)
        cell.set_edgecolor(REPORT_RULE_COLOR)
        if hasattr(cell, "set_visible_edges"):
            cell.set_visible_edges("B")
        else:
            cell.visible_edges = "B"


def draw_two_column_report_table(
    ax,
    rows: list[list[str]],
    *,
    fontsize: float = 6.5,
    title_first_row: bool = True,
) -> None:
    ax.axis("off")
    ax.set_frame_on(False)
    if not rows:
        ax.text(0.5, 0.5, "No data", ha="center", va="center", transform=ax.transAxes)
        return

    ncols = len(rows[0])
    for r, row in enumerate(rows):
        if len(row) != ncols:
            raise ValueError(f"Row {r} has {len(row)} columns; expected {ncols}")

    col_widths = [1.0 / ncols] * ncols
    tbl = ax.table(
        cellText=rows,
        loc="upper center",
        cellLoc="left",
        colWidths=col_widths,
    )
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(fontsize)
    tbl.scale(1.0, 1.12)

    section_markers = (
        "PROJECT INFORMATION",
        "AQUIFER DATA",
        "SOLUTION",
    )

    def _section_row_bg(r: int, bg: str) -> None:
        for cc in range(ncols):
            ccell = tbl.get_celld().get((r, cc))
            if ccell is not None:
                ccell.set_facecolor(bg)

    for (r, c), cell in tbl.get_celld().items():
        text = cell.get_text().get_text()
        if r == 0 and title_first_row:
            cell.set_text_props(
                weight="bold",
                size=fontsize + 0.5,
                color=TITLE_ROW_TEXT,
            )
            cell.set_facecolor(TITLE_ROW_BG)
            continue
        if c == 0 and text in section_markers:
            cell.set_text_props(weight="bold", color=SECTION_HEADER_TEXT)
            bg = SECTION_BG_SOLUTION if text == "SOLUTION" else SECTION_BG_NEUTRAL
            cell.set_facecolor(bg)
            _section_row_bg(r, bg)
        elif c == 0 and text.startswith("WELL DATA"):
            cell.set_text_props(weight="bold", color=SECTION_HEADER_TEXT)
            _section_row_bg(r, SECTION_BG_WELL)

    for r in range(len(rows)):
        if r == 0 and title_first_row:
            continue
        row0 = rows[r][0] if rows[r] else ""
        if row0 in section_markers or (row0 or "").startswith("WELL DATA"):
            continue
        for c in range(ncols):
            cell = tbl.get_celld().get((r, c))
            if cell is None:
                continue
            t = cell.get_text().get_text().strip()
            if not t:
                continue
            if c % 2 == 0:
                cell.set_text_props(weight="bold", color=FIELD_NAME_COLOR)
            else:
                cell.set_text_props(weight="normal", color=VALUE_TEXT_COLOR)

    _strip_table_cell_edges(tbl)
    _add_table_bottom_border(tbl, len(rows), ncols)


def draw_logo(ax: Axes, path: str) -> None:
    """Show company logo in an axes (centered, aspect preserved)."""
    ax.axis("off")
    ax.set_frame_on(False)
    if not (path or "").strip():
        return
    if not os.path.isfile(path):
        msg = f"Logo not found:\n{path}"
        ax.text(
            0.5,
            0.5,
            msg,
            ha="center",
            va="center",
            transform=ax.transAxes,
            fontsize=7,
        )
        return
    im = mpimg.imread(path)
    ax.imshow(im, aspect="equal")
    ax.set_axis_off()


def plot_comparison_page(
    test_name: str,
    butler_dir: str,
    bouwer_dir: str,
    batch_butler: str,
    batch_bouwer: str,
    *,
    company: str = DEFAULT_COMPANY,
    client: str = DEFAULT_CLIENT,
    project: str = DEFAULT_PROJECT,
    location: str = DEFAULT_LOCATION,
    logo_path: str | None = None,
) -> plt.Figure:
    est_bt = load_estimated(os.path.join(butler_dir, "estimated_conductivity.csv"))
    est_br = load_estimated(os.path.join(bouwer_dir, "estimated_conductivity.csv"))

    row_bt = est_bt[est_bt["test_name"].astype(str).str.strip() == test_name]
    row_br = est_br[est_br["test_name"].astype(str).str.strip() == test_name]
    if row_bt.empty:
        raise FileNotFoundError(f"No Butler results for test_name={test_name!r}")
    if row_br.empty:
        raise FileNotFoundError(f"No Bouwer–Rice results for test_name={test_name!r}")

    s_bt = row_bt.iloc[0].drop(labels=["test_name"], errors="ignore")
    s_br = row_br.iloc[0].drop(labels=["test_name"], errors="ignore")

    df_batch_bt = load_batch_table(batch_butler)
    df_batch_br = load_batch_table(batch_bouwer)
    tid = str(test_name).strip()
    b_bt = df_batch_bt[df_batch_bt["test_id"].astype(str).str.strip() == tid]
    b_br = df_batch_br[df_batch_br["test_id"].astype(str).str.strip() == tid]
    row_batch_bt = b_bt.iloc[0] if not b_bt.empty else None
    row_batch_br = b_br.iloc[0] if not b_br.empty else None
    batch_row = row_batch_br if row_batch_br is not None else row_batch_bt

    img_br = os.path.join(bouwer_dir, "fit_plots", f"{test_name}.png")
    img_bt = os.path.join(butler_dir, "fit_plots", f"{test_name}.png")

    fig = plt.figure(figsize=FIG_SIZE_LANDSCAPE_IN)

    # Two outer rows: header block | (fit + solution). A single 3-row grid used
    # hspace between *every* row, which left a large gap between plots and tables.
    _h_top, _h_fit, _h_sol = PAGE_GRID_HEIGHT_RATIOS
    _outer_bottom = _h_fit + _h_sol
    gs = GridSpec(
        2,
        2,
        figure=fig,
        height_ratios=[_h_top, _outer_bottom],
        hspace=0.34,
        wspace=0.14,
        left=0.04,
        right=0.99,
        top=0.96,
        bottom=0.04,
    )

    project_rows = build_project_information_rows(
        test_name,
        batch_row,
        company=company,
        client=client,
        project=project,
        location=location,
    )
    aquifer_well_rows = build_aquifer_well_rows(batch_row)
    sol_br = build_solution_rows(s_br, "Bouwer-Rice")
    sol_bt = build_solution_rows(s_bt, "Butler")

    # Row 0: two stacked tables (left); company logo (right)
    gs_top_left = gs[0, 0].subgridspec(
        2,
        1,
        height_ratios=[1.0, 1.05],
        hspace=0.78,
    )
    ax_project = fig.add_subplot(gs_top_left[0, 0])
    draw_two_column_report_table(ax_project, project_rows, fontsize=6.8, title_first_row=True)
    ax_aq_well = fig.add_subplot(gs_top_left[1, 0])
    draw_two_column_report_table(ax_aq_well, aquifer_well_rows, fontsize=6.8, title_first_row=False)

    ax_logo = fig.add_subplot(gs[0, 1])
    lp = logo_path if logo_path is not None else DEFAULT_LOGO_PATH
    draw_logo(ax_logo, lp)

    # Fit plots + solution tables share one outer row; tight vertical spacing between them.
    gs_fit_sol = gs[1, :].subgridspec(
        2,
        2,
        height_ratios=[_h_fit, _h_sol],
        hspace=FIT_SOLUTION_ROW_HSPACE,
        wspace=0.14,
    )
    for col, (path_img, method) in enumerate(
        [(img_br, "Bouwer–Rice"), (img_bt, "Butler")]
    ):
        draw_fit_plot_pair(fig, gs_fit_sol[0, col], path_img, method)

    # First row is "SOLUTION" section header (not slug title) so green shading applies.
    ax_sol_br = fig.add_subplot(gs_fit_sol[1, 0])
    draw_two_column_report_table(ax_sol_br, sol_br, fontsize=7.0, title_first_row=False)
    ax_sol_bt = fig.add_subplot(gs_fit_sol[1, 1])
    draw_two_column_report_table(ax_sol_bt, sol_bt, fontsize=7.0, title_first_row=False)

    return fig


def main() -> None:
    cfg = RUN_CONFIG
    butler_dir = cfg["butler_dir"]
    bouwer_dir = cfg["bouwer_dir"]
    batch_butler = cfg["batch_butler"]
    batch_bouwer = cfg["batch_bouwer"]
    plot_kw = dict(
        company=cfg["company"],
        client=cfg["client"],
        project=cfg["project"],
        location=cfg["location"],
        logo_path=cfg["logo"],
    )

    if cfg["run_all"]:
        names = list_test_names_intersection(butler_dir, bouwer_dir)
        if not names:
            raise SystemExit(
                "No common test_name entries in both estimated_conductivity.csv files."
            )
        if str(cfg.get("output", "")).strip():
            print(
                "Note: output is ignored when run_all is True; "
                "files go to PdfPages/compare_<test_name>.pdf"
            )
        for tn in names:
            out = resolve_pdf_output_path(tn, "")
            fig = plot_comparison_page(
                tn,
                butler_dir,
                bouwer_dir,
                batch_butler,
                batch_bouwer,
                **plot_kw,
            )
            with PdfPages(out) as pdf:
                pdf.savefig(fig, orientation="landscape")
            plt.close(fig)
            print(f"Wrote {out}")
        return

    test_name = str(cfg["test_name"]).strip()
    if not test_name:
        raise SystemExit("RUN_CONFIG['test_name'] is required when run_all is False.")

    out = resolve_pdf_output_path(test_name, str(cfg.get("output", "")))
    fig = plot_comparison_page(
        test_name,
        butler_dir,
        bouwer_dir,
        batch_butler,
        batch_bouwer,
        **plot_kw,
    )
    with PdfPages(out) as pdf:
        pdf.savefig(fig, orientation="landscape")
    plt.close(fig)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

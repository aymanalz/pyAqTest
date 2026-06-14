"""
Backward-compatible entry point for Bouwer–Rice vs Butler comparison PDFs.

Prefer ``tests/run_compare_bower_butler.py`` for batch runs discovered from
``estimated_conductivity.csv``. This script still supports a single ``test_name``
via ``RUN_CONFIG``.
"""

from __future__ import annotations

from pyAqTest.bouwer_butler_compare import (
    DEFAULT_BATCH_BOUWER,
    DEFAULT_BATCH_BUTLER,
    DEFAULT_BOUWER_DIR,
    DEFAULT_BUTLER_DIR,
    DEFAULT_COMPANY,
    DEFAULT_CLIENT,
    DEFAULT_LOCATION,
    DEFAULT_LOGO_PATH,
    DEFAULT_PROJECT,
    resolve_pdf_output_path,
    write_all_comparison_pdfs,
    write_comparison_pdf,
)

RUN_CONFIG = {
    "test_name": "LB6_1_T1",  # ignored when run_all is True
    "run_all": False,
    "output": "",
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


def main() -> None:
    cfg = RUN_CONFIG
    plot_kw = dict(
        company=cfg["company"],
        client=cfg["client"],
        project=cfg["project"],
        location=cfg["location"],
        logo_path=cfg["logo"],
    )

    if cfg["run_all"]:
        if str(cfg.get("output", "")).strip():
            print(
                "Note: output is ignored when run_all is True; "
                "files go to PdfPages/compare_<test_name>.pdf"
            )
        written = write_all_comparison_pdfs(
            cfg["butler_dir"],
            cfg["bouwer_dir"],
            cfg["batch_butler"],
            cfg["batch_bouwer"],
            **plot_kw,
        )
        for path in written:
            print(f"Wrote {path}")
        return

    test_name = str(cfg["test_name"]).strip()
    if not test_name:
        raise SystemExit("RUN_CONFIG['test_name'] is required when run_all is False.")

    out = write_comparison_pdf(
        test_name,
        cfg["butler_dir"],
        cfg["bouwer_dir"],
        cfg["batch_butler"],
        cfg["batch_bouwer"],
        resolve_pdf_output_path(test_name, str(cfg.get("output", ""))),
        **plot_kw,
    )
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()

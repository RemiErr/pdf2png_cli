from __future__ import annotations

from pathlib import Path

import pytest
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from pdf_to_png import convert_pdf_to_png


def _make_sample_pdf(pdf_path: Path, pages: int = 2) -> None:
    c = canvas.Canvas(str(pdf_path), pagesize=A4)
    for i in range(1, pages + 1):
        c.setFont("Helvetica", 24)
        c.drawString(72, 800, f"Hello Page {i}")
        c.showPage()
    c.save()


def test_convert_pdf_to_png_creates_expected_files(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    out_dir = tmp_path / "out"
    _make_sample_pdf(pdf_path, pages=2)

    result = convert_pdf_to_png(
        pdf_path=pdf_path,
        output_dir=out_dir,
        dpi=120,
        prefix="page_",
        zero_pad=3,
    )

    assert result.page_count == 2
    assert result.rendered_pages == 2
    assert len(result.output_paths) == 2

    expected = [out_dir / "page_001.png", out_dir / "page_002.png"]
    assert result.output_paths == expected
    for p in expected:
        assert p.exists()
        assert p.stat().st_size > 0

        # validate it's a readable PNG
        with Image.open(p) as im:
            assert im.format == "PNG"
            w, h = im.size
            assert w > 0 and h > 0


def test_convert_pdf_to_png_page_range(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    out_dir = tmp_path / "out"
    _make_sample_pdf(pdf_path, pages=3)

    result = convert_pdf_to_png(
        pdf_path=pdf_path,
        output_dir=out_dir,
        dpi=72,
        start_page=2,
        end_page=3,
        prefix="p_",
        zero_pad=2,
    )

    assert result.page_count == 3
    assert result.rendered_pages == 2
    assert result.output_paths == [out_dir / "p_02.png", out_dir / "p_03.png"]


def test_invalid_page_range_raises(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    out_dir = tmp_path / "out"
    _make_sample_pdf(pdf_path, pages=2)

    with pytest.raises(ValueError):
        convert_pdf_to_png(pdf_path=pdf_path,
                           output_dir=out_dir, start_page=3, end_page=3)

    with pytest.raises(ValueError):
        convert_pdf_to_png(pdf_path=pdf_path,
                           output_dir=out_dir, start_page=2, end_page=1)

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import pymupdf as fitz


@dataclass(frozen=True)
class ConvertResult:
    output_paths: List[Path]
    page_count: int
    rendered_pages: int


def _validate_pdf_path(pdf_path: Path) -> None:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if not pdf_path.is_file():
        raise ValueError(f"Not a file: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(f"Not a .pdf file: {pdf_path}")


def _ensure_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    if not output_dir.is_dir():
        raise ValueError(f"Output path is not a directory: {output_dir}")


def _dpi_to_zoom(dpi: int) -> float:
    # PyMuPDF uses 72 DPI as 1.0 zoom baseline
    if dpi <= 0:
        raise ValueError("dpi must be > 0")
    return dpi / 72.0


def convert_pdf_to_png(
    pdf_path: os.PathLike | str,
    output_dir: os.PathLike | str,
    dpi: int = 200,
    prefix: str = "page_",
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    zero_pad: int = 3,
    password: Optional[str] = None,
) -> ConvertResult:
    """
    將 PDF 的每一頁轉換為 PNG 檔案。

    參數:
        pdf_path: 輸入 PDF 的路徑。
        output_dir: 儲存 PNG 的目錄。
        dpi: 渲染解析度。
        prefix: 輸出檔案名稱的前綴。
        start_page: 以 1 為基底的起始頁 (None 表示第 1 頁)。
        end_page: 以 1 為基底的結束頁 (None 表示最後一頁)。
        zero_pad: 檔名中頁碼的零補齊寬度。

    回傳:
        ConvertResult，包含輸出路徑和頁數統計。
    """
    pdf_path = Path(pdf_path)
    output_dir = Path(output_dir)

    _validate_pdf_path(pdf_path)
    _ensure_output_dir(output_dir)

    zoom = _dpi_to_zoom(dpi)
    mat = fitz.Matrix(zoom, zoom)

    try:
        doc = fitz.open(pdf_path)

        if doc.is_encrypted:
            if not password:
                raise ValueError("PDF 已加密，請提供密碼")

            ok = doc.authenticate(password)
            if ok <= 0:
                raise ValueError("PDF 密碼錯誤，無法解密")

    except Exception as e:
        raise ValueError(f"Failed to open PDF: {pdf_path}. Error: {e}") from e

    try:
        page_count = doc.page_count
        if page_count <= 0:
            return ConvertResult(output_paths=[], page_count=0, rendered_pages=0)

        s = 1 if start_page is None else start_page
        e = page_count if end_page is None else end_page

        if not (1 <= s <= page_count):
            raise ValueError(f"start_page out of range: {s} (1..{page_count})")
        if not (1 <= e <= page_count):
            raise ValueError(f"end_page out of range: {e} (1..{page_count})")
        if s > e:
            raise ValueError(
                f"start_page ({s}) cannot be greater than end_page ({e})")

        output_paths: List[Path] = []
        rendered = 0

        # PyMuPDF pages are 0-based internally
        for page_no in range(s, e + 1):
            page = doc.load_page(page_no - 1)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            pdf_name = pdf_path.stem
            filename = f"{prefix}{page_no:0{zero_pad}d}.png"
            pdf_output_dir = output_dir / pdf_name
            pdf_output_dir.mkdir(parents=True, exist_ok=True)
            out_path = pdf_output_dir / filename
            pix.save(out_path.as_posix())

            output_paths.append(out_path)
            rendered += 1

        return ConvertResult(output_paths=output_paths, page_count=page_count, rendered_pages=rendered)
    finally:
        doc.close()


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="將 PDF 頁面轉換為 PNG 圖檔 (使用 PyMuPDF)。")
    p.add_argument("pdf", help="輸入 PDF 檔案的路徑")
    p.add_argument("-o", "--output-dir", default="output_png",
                   help="輸出目錄 (default: output_png)")
    p.add_argument("--dpi", type=int, default=200,
                   help="渲染解析度 DPI (default: 200)")
    p.add_argument("--prefix", default="page_",
                   help="輸出檔案名稱的前綴 (default: page_)")
    p.add_argument("--start-page", type=int, default=None,
                   help="以 1 為基底的起始頁 (包含)")
    p.add_argument("--end-page", type=int, default=None,
                   help="以 1 為基底的結束頁 (包含)")
    p.add_argument("--zero-pad", type=int, default=3,
                   help="頁碼的零補齊寬度 (default: 3)")
    p.add_argument("--pwd", type=str, default=None,
                   help="若 PDF 已加密，請提供密碼")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    result = convert_pdf_to_png(
        pdf_path=args.pdf,
        output_dir=args.output_dir,
        dpi=args.dpi,
        prefix=args.prefix,
        start_page=args.start_page,
        end_page=args.end_page,
        zero_pad=args.zero_pad,
        password=args.pwd,
    )
    print(f"PDF pages: {result.page_count}")
    print(f"Rendered pages: {result.rendered_pages}")
    for p in result.output_paths:
        print(p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

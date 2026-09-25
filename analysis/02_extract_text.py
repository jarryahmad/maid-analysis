"""
Dump the readable text of every source document to a .txt alongside it.

Two consumers: 03_build_datasets.py reads a few narrative figures out of the
Health Canada text, and 07_verify.py checks that every sentence quoted on the
page appears verbatim in the document it is attributed to.

Quebec's PDFs before 2022 are AES-encrypted (owner password only, no user
password), which is why `cryptography` is a dependency.
"""
import glob, os, re
from bs4 import BeautifulSoup
from pypdf import PdfReader

HTML_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]


def from_html(path):
    soup = BeautifulSoup(open(path, encoding="utf-8").read(), "lxml")
    main = soup.find("main") or soup
    for t in main.find_all(["table", "script", "style", "nav"]):
        t.decompose()
    return re.sub(r"\n{2,}", "\n", main.get_text("\n", strip=True))


def from_pdf(path):
    return "\n".join((p.extract_text() or "") for p in PdfReader(path).pages)


def main():
    for y in HTML_YEARS:
        src = f"data/raw/hc-annual-{y}.html"
        out = f"data/raw/hc-annual-{y}.txt"
        open(out, "w", encoding="utf-8").write(from_html(src))
        print(f"  {os.path.basename(out)}  {os.path.getsize(out):,} bytes")

    for src in sorted(glob.glob("data/raw/lit/*.pdf")):
        out = src[:-4] + ".txt"
        try:
            open(out, "w", encoding="utf-8").write(from_pdf(src))
            print(f"  {os.path.basename(out)}  {os.path.getsize(out):,} bytes")
        except Exception as e:                      # noqa: BLE001 - report and continue
            print(f"  !! {os.path.basename(src)}: {e}")


if __name__ == "__main__":
    print("extracting document text:")
    main()

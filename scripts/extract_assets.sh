#!/usr/bin/env bash

set -euo pipefail

pdf_file='Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf'

mkdir -p extracted figures/raw

pdfinfo "$pdf_file" > extracted/pdfinfo.txt
pdftotext -layout "$pdf_file" extracted/systematic_trading_layout.txt
pdfimages -list "$pdf_file" > extracted/pdfimages_list.txt
pdfimages -all "$pdf_file" figures/raw/img
awk 'NR > 2 { ext = ($9 == "jpeg" ? "jpg" : "png"); printf("img-%03d.%s\tpage %s\n", $2, ext, $1) }' \
  extracted/pdfimages_list.txt > extracted/image_manifest.tsv

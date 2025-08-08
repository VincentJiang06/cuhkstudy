#!/usr/bin/env bash
set -euo pipefail

# 目标：压缩 static/ 与 content/ 里的 PNG/JPG/JPEG，并生成 WebP；限制宽度最大 1920；剥离元数据。
# 依赖：imagemagick、webp（已在服务器安装）

shopt -s globstar nullglob

opt_one() {
  local f="$1"
  local dir ext base out
  dir="$(dirname "$f")"
  base="$(basename "$f")"
  ext="${base##*.}"
  out="$dir/${base%.*}.webp"

  # 仅当输出不存在或源文件较新时才处理
  if [[ ! -f "$out" || "$f" -nt "$out" ]]; then
    convert "$f" -strip -resize '1920x>' -quality 85 "PNG24:$dir/__tmp_$$.png"
    cwebp -quiet -q 82 "$dir/__tmp_$$.png" -o "$out"
    rm -f "$dir/__tmp_$$.png"
    # 若原图大于新图且为 PNG/JPG，可保留原图以兼容；由 HTML/模板优先引用 webp
    echo "optimized: $f -> $out"
  fi
}

main() {
  local changed=0
  for f in static/**/*.{png,jpg,jpeg,JPG,JPEG,PNG} content/**/*.{png,jpg,jpeg,JPG,JPEG,PNG}; do
    [[ -e "$f" ]] || continue
    opt_one "$f" && changed=1 || true
  done
  exit 0
}

main "$@"



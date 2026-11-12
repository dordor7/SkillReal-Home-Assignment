#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C

dataset_dir=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
python_script=${2:-"$dataset_dir/create_kfold.py"}
case "${OVERSAMPLE:-1}" in
  1) sampling_args=(--oversample) ;;
  0) sampling_args=() ;;
  *) printf 'OVERSAMPLE must be 0 or 1\n' >&2; exit 2 ;;
esac

case "${1:-both}" in
  both) resolutions=(high low) ;;
  low|high) resolutions=("$1") ;;
  *) printf 'Usage: bash %s [both|low|high] [path/to/create_kfold.py]\n' "$0" >&2; exit 2 ;;
esac

if [[ ! -f "$python_script" ]]; then
  printf 'Python script not found: %s\n' "$python_script" >&2
  exit 1
fi
printf 'Dataset folder: %s\nPython script: %s\n' "$dataset_dir" "$python_script"

# Build all requested splits before moving any existing folders.
stage_dir=$(mktemp -d "$dataset_dir/.kfold-stage.XXXXXX")
trap 'rm -rf -- "$stage_dir"' EXIT
shopt -s nullglob

for resolution in "${resolutions[@]}"; do
  source_dir="$dataset_dir/${resolution}_resolution_welds"
  output_name="kfold_${resolution}"
  output_dir="$stage_dir/$output_name"
  images=("$source_dir"/*.jpg)
  if (( ${#images[@]} == 0 )); then
    printf 'No JPG images found in %s\n' "$source_dir" >&2
    exit 1
  fi

  image_ids="$stage_dir/${resolution}_image_ids.txt"
  for image in "${images[@]}"; do
    filename=${image##*/}
    printf '%s\n' "${filename%.jpg}"
  done > "$image_ids"

  printf '\nBuilding %s\n' "$output_name"
  python "$python_script" "$image_ids" "$source_dir" "$output_dir" "${sampling_args[@]}"
  cp -- "$image_ids" "$output_dir/dataset.txt"

  # YOLOv7 resolves ./ entries relative to the list file's directory.
  for fold in fold0 fold1 fold2 fold3 fold4; do
    for split in train val; do
      sed "s|^\./images/|./$split/images/|" \
        "$output_dir/$fold/$split/images.txt" > "$output_dir/$fold/$split.txt"
    done
  done
  sed 's|^\./images/|./test/images/|' \
    "$output_dir/test/images.txt" > "$output_dir/test.txt"
done

backup_dir=""
for resolution in "${resolutions[@]}"; do
  output_name="kfold_${resolution}"
  destination="$dataset_dir/$output_name"
  if [[ -e "$destination" || -L "$destination" ]]; then
    if [[ -z "$backup_dir" ]]; then
      backup_dir=$(mktemp -d "$dataset_dir/kfold_backup.XXXXXX")
    fi
    mv -- "$destination" "$backup_dir/"
    printf 'Previous %s saved to %s\n' "$output_name" "$backup_dir/$output_name"
  fi
  mv -- "$stage_dir/$output_name" "$destination"
  printf 'Wrote splits to %s\n' "$destination"
done

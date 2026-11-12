"""Export a two-class YOLO dataset with one holdout and five folds."""

import argparse
import random
from pathlib import Path
from shutil import copy2

from sklearn.model_selection import StratifiedKFold, train_test_split


def read_sample(source, image_id):
    image = source / f"{image_id}.jpg"
    if not image.is_file():
        raise FileNotFoundError(image)

    annotation = image.with_suffix(".yolo")
    if not annotation.is_file():
        raise FileNotFoundError(
            f"Missing annotation for {image.name}: {annotation}. "
            "Restore the source annotation before building the splits."
        )

    labels = []
    classes = set()
    for line in annotation.read_text().splitlines():
        fields = line.split()
        if fields and fields[0] in {"0", "1"}:
            labels.append(line.strip())
            classes.add(fields[0])
    return image, labels, classes


def strata(samples):
    # "", "0", "1", and "01" represent the four class-presence combinations.
    return ["".join(sorted(classes)) for _, _, classes in samples]


def training_duplicates(samples, seed):
    totals = {c: sum(c in classes for _, _, classes in samples) for c in ("0", "1")}
    if totals["0"] == totals["1"]:
        return []

    minority = min(totals, key=totals.get)
    candidates = [sample for sample in samples if sample[2] == {minority}]
    if not candidates:
        print("  Oversampling skipped: no images contain only the minority class.")
        return []

    gap = abs(totals["0"] - totals["1"])
    return random.Random(seed).choices(candidates, k=gap)


def export_split(folder, samples, duplicates=()):
    (folder / "images").mkdir(parents=True)
    (folder / "labels").mkdir()

    image_paths = []
    negative_count = sum(not labels for _, labels, _ in samples)
    box_counts = {"0": 0, "1": 0}
    image_counts = {"0": 0, "1": 0}
    for index, (image, labels, classes) in enumerate([*samples, *duplicates]):
        stem = image.stem
        if index >= len(samples):
            stem += f"__oversample_{index - len(samples)}"
        name = f"{stem}.jpg"
        copy2(image, folder / "images" / name)
        (folder / "labels" / f"{stem}.txt").write_text(
            "".join(line + "\n" for line in labels)
        )
        image_paths.append(f"./images/{name}")
        for class_id in classes:
            image_counts[class_id] += 1
        for line in labels:
            box_counts[line.split()[0]] += 1

    (folder / "images.txt").write_text("\n".join(image_paths) + "\n")
    print(
        f"{folder.relative_to(folder.parents[1])}: {len(image_paths)} images "
        f"({len(duplicates)} repeats), {negative_count} without pores or deposits, "
        f"pores: {image_counts['0']} images / {box_counts['0']} boxes, "
        f"deposits: {image_counts['1']} images / {box_counts['1']} boxes"
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image_ids", type=Path, help="One image basename per line")
    parser.add_argument("source", type=Path, help="Folder with .jpg and .yolo files")
    parser.add_argument("destination", type=Path, help="New or empty output folder")
    parser.add_argument("--oversample", action="store_true", help="Balance training image counts")
    args = parser.parse_args()

    ids = [Path(line.strip()).stem for line in args.image_ids.read_text().splitlines()
           if line.strip()]
    if len(ids) != len(set(ids)):
        raise ValueError("The input list contains duplicate image IDs.")
    samples = [read_sample(args.source, image_id) for image_id in ids]
    negative_count = sum(not labels for _, labels, _ in samples)
    print(f"Source: {len(samples)} JPGs, {negative_count} without pores or deposits")

    try:
        development, test = train_test_split(
            samples, test_size=0.2, random_state=1, stratify=strata(samples)
        )
        splitter = StratifiedKFold(n_splits=5, shuffle=True, random_state=100)
        folds = list(splitter.split(development, strata(development)))
    except ValueError as exc:
        raise ValueError(f"The class-presence groups are too small for this split: {exc}") from exc

    if args.destination.exists() and any(args.destination.iterdir()):
        raise ValueError(f"Choose a new or empty output folder: {args.destination}")

    export_split(args.destination / "test", test)
    for fold, (train_indices, val_indices) in enumerate(folds):
        train = [development[i] for i in train_indices]
        val = [development[i] for i in val_indices]
        duplicates = training_duplicates(train, seed=100 + fold) if args.oversample else []
        fold_dir = args.destination / f"fold{fold}"
        export_split(fold_dir / "train", train, duplicates)
        export_split(fold_dir / "val", val)


if __name__ == "__main__":
    main()

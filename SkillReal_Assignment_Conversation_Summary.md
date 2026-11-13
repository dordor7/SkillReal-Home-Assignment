# SkillReal ML Engineer Home Assignment

## Weld defect detection

*Condensed dialogue, paraphrased from the working conversation.*

### Choosing the scope

**Dor:** My plan is to focus the detector on pores and deposits. Those are the two classes I need to answer the customer’s three questions for each weld: how large the biggest pore is, how many pores fall within a section of the bead, and whether deposits are near the centerline.

**Assistant:** That scope maps directly to the inspection criteria. The detector provides bounding boxes, and the weld report turns them into the measurements the operator needs.

### Designing the dataset

**Dor:** I want to keep the authors’ five-fold evaluation setup and prepare separate high- and low-resolution datasets. I’d like to test oversampling for the minority class and see whether it improves detection.

**Assistant:** The split scripts stratify images by whether they contain pores, deposits, both, or neither. Each resolution has five train–validation folds and a shared holdout. Oversampling is applied only to the training images.

**Dor:** I’m concerned that oversampling repeats the same welds. I also want to keep images that have no pore or deposit labels after filtering. Welds with only stains or discontinuities are still useful negative examples. My revised plan is to restore those images and train without oversampling.

**Assistant:** The revised build does that. Restoring the images also changes the split, so the run provides a new baseline. An oversampling comparison on identical splits would isolate the effect of the repeated images.

### Designing the weld report

**Dor:** I considered clustering and connecting nearby pores in a graph. My concern with fixed sections is that a dense group could straddle a boundary. I’d use a sliding window along the sorted horizontal positions of pore centers and report the largest count within a section. I’d set the window length as a fraction of the bead span and use bounding-box area as a proxy for pore size.

**Assistant:** That gives each weld a maximum pore count for the specified section length. The window can start wherever it captures the most pores, so the count does not depend on preset boundaries.

**Dor:** For deposits, I want the report to capture both proximity and size. I’d measure distance from the box to the centerline, count a box that touches or crosses the line as zero distance, and include the area of the closest box.

**Assistant:** The report uses that definition. It measures distances in pixels and areas in square pixels. When a bead box is unavailable, it uses the crop midpoint as the centerline.

### Interpreting the results

**Dor:** The authors’ fold 4 mAP@0.5 is 0.630 and mine is 0.421. Their average includes stains and discontinuities, so I want to compare the AP of pores and deposits directly. I also looked at the confusion matrices to see what kinds of errors were most common.

**Assistant:** Your pore and deposit AP@0.5 scores were 0.470 and 0.373. The authors averaged 0.505 over those two classes, putting the gap at about 8.4 percentage points. Unmatched annotations were the largest difference for deposits. The evaluation splits differed, so several factors could contribute to the gap.

**Dor:** I noticed a sharp precision drop across my folds while recall and mAP kept rising. I wanted to see whether the confidence threshold used for reporting explained that pattern. I also flagged my batch size of 128 as a difference from the authors’ batch size of 8.

**Assistant:** YOLOv7 reports precision at the threshold that maximizes mean F1 for each epoch. A change in that threshold is one plausible explanation. Comparing checkpoints before and after the dip on the same validation images at fixed confidence and IoU thresholds would test it. A separate run on the same fold could isolate the effect of batch size.

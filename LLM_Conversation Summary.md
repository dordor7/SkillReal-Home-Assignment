# SkillReal ML Engineer Home Assignment

## Weld defect detection

*Condensed dialogue, paraphrased from the working conversation.*

### Choosing the scope

**Dor:** The customer cares about the largest pore, the number of pores within a section of the bead, and deposits near the centerline. The paper detects four classes. Does it make sense to focus on pores and deposits for this assignment?

**Assistant:** Yes. Those two classes supply the detections needed for all three measurements. The report can turn the boxes into information an operator can use for each weld.

### Building the dataset

**Dor:** How did the authors handle class representation? I’d like to keep their five-fold setup and check whether oversampling helps. Also, what happens to an image when filtering leaves it with no pore or deposit labels?

**Assistant:** Stratifying by whether an image contains pores, deposits, both, or neither helps represent those groups in each split. The updated scripts keep separate high- and low-resolution datasets, each with five train–validation folds and a shared holdout. Oversampling can be applied within training only.

**Dor:** I’m concerned that oversampling mostly repeats the same welds. The cleanup step also removed images with empty labels, including welds with only stains or discontinuities. I want to keep those images as negatives.

**Assistant:** The revised build restores those examples and disables oversampling. The rebuilt splits give you a new baseline. A comparison on identical splits would isolate the effect of oversampling.

### Measuring defects per weld

**Dor:** For pore density, I considered clustering and graph-based grouping, but fixed sections could split a dense group across a boundary. Could I slide a window over the sorted horizontal coordinates of the pore centers and count the most pores it contains?

**Assistant:** Yes. A sliding window finds the highest count over a fixed-length bead section without depending on where section boundaries happen to fall. The implementation uses a configurable fraction of the bead span for the window and bounding-box area as a proxy for pore size.

**Dor:** For deposits, I also want the size of the one closest to the centerline. If a deposit box touches the line, should its distance be zero?

**Assistant:** Yes. The report measures the shortest distance from each box to the line and includes the area of the nearest deposit box. The measurements are in pixels. If a bead box is unavailable, the crop midpoint serves as the centerline.

### Interpreting the results

**Dor:** The authors’ fold 4 mAP@0.5 is 0.630 and mine is 0.421, but their average includes stains and discontinuities. How big is the gap on the two classes I actually trained for?

**Assistant:** Your pore and deposit AP@0.5 scores were 0.470 and 0.373. The authors averaged 0.505 on those same two classes, bringing the gap from 20.9 to about 8.4 percentage points. The confusion matrices showed that the largest difference for deposits was in unmatched annotations. The different evaluation splits limit what we can infer about the cause.

**Dor:** I also noticed a sharp precision drop across my folds even though recall and mAP kept rising. Could the way YOLOv7 chooses its confidence threshold explain that? I also used batch 128, while the authors used batch 8.

**Assistant:** YOLOv7 reports precision at the confidence threshold that maximizes mean F1 for each epoch. A change in that threshold could explain the drop. To test it, compare checkpoints from before and after the dip on the same validation images, using fixed confidence and IoU thresholds. Batch size is another training variable that could be tested on the same fold.

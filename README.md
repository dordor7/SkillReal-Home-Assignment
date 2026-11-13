# SkillReal ML Engineer Home Assignment

**Weld defect detection with YOLOv7-tiny on the LoHi-Weld dataset**

This submission covers the workflow from preparing the dataset and evaluating the detector to turning predictions into per-weld measurements for customer inspection.

[**Read the final report →**](./final_report.pdf) · [**Open the notebook in Colab →**](https://colab.research.google.com/github/dordor7/SkillReal-Home-Assignment/blob/main/SkillReal_ML_Engineer_Home_Assignment.ipynb)

## 📄 Final report

Start with [`final_report.pdf`](./final_report.pdf). It is the main submission document and contains the answers to the assignment questions, the work I carried out, and my analysis of the results.

## 🧪 Code and reproducibility

| File | Purpose |
| --- | --- |
| [`SkillReal_ML_Engineer_Home_Assignment.ipynb`](./SkillReal_ML_Engineer_Home_Assignment.ipynb) | Google Colab notebook for dataset setup, model training, evaluation, and weld report generation. |
| [`create_kfold.py`](./create_kfold.py) | Prepares pore and deposit labels and creates stratified training, validation, and holdout splits. |
| [`create_kfold.sh`](./create_kfold.sh) | Runs the split builder for the low- and high-resolution datasets. |

To reproduce the workflow, open the notebook in Colab, select a GPU runtime, and follow the cells from setup through evaluation and report generation.

## 📊 Customer weld reports

The JSON exports contain per-weld measurements from the fold checkpoints. They correspond to each of teh folds, and include the maximum pore bounding-box area, the highest pore count within a configurable bead section, and the distance and bounding-box area of the deposit closest to the centerline. Distances are reported in pixels and areas in square pixels.

[Report export](./weld_report.json) · [Export (1)](./weld_report%20%281%29.json) · [Export (2)](./weld_report%20%282%29.json) · [Export (3)](./weld_report%20%283%29.json) · [Export (4)](./weld_report%20%284%29.json)

## 💬 LLM Conversation summary

[`SkillReal_Assignment_Conversation_Summary.md`](./SkillReal_Assignment_Conversation_Summary.md) is a condensed, paraphrased dialogue with ChatGPT. It documents the ideas I proposed, the alternatives I explored, and how I interpreted the model’s results.

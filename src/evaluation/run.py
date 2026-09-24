# import json
# import torch
# import torch.nn as nn
# from pathlib import Path
# import os

# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import (
#     accuracy_score,
#     precision_recall_fscore_support,
#     classification_report,
#     confusion_matrix
# )

# import matplotlib.pyplot as plt
# import seaborn as sns

# from src.model.transformer import BehavioralTransformer
# from src.encoding.event_vocab import EventVocab
# from src.preprocessing.prefix import generate_prefixes

# # ================= CONFIG =================
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("Using device:", DEVICE)

# PREFIXES = [64, 128, 256]
# MAX_LEN = 256
# BATCH_SIZE = 4
# TEST_SPLIT = 0.30
# RANDOM_STATE = 42

# # ================= FEATURES =================
# SELECTED_FEATURES = [
#     "pslist.nproc",
#     "pslist.avg_threads",
#     "handles.nhandles",
#     "handles.nfile",
#     "handles.nkey",
#     "dlllist.ndlls",
#     "ldrmodules.not_in_load",
#     "psxview.not_in_pslist",
#     "psxview.not_in_session",
#     "malfind.ninjections",
#     "malfind.uniqueInjections",
#     "svcscan.nservices",
# ]

# NUM_FEATURES = len(SELECTED_FEATURES)

# # ================= LOAD VOCAB =================
# vocab = EventVocab()
# VOCAB_SIZE = len(vocab.token2id)

# # ================= COLLECT FILES =================
# files = []
# labels = []

# for label, y_val in [("ransomware", 1), ("benign", 0)]:
#     for f in Path(f"data/processed/sequences/{label}").glob("*.json"):
#         files.append(f)
#         labels.append(y_val)

# _, test_files, _, test_labels = train_test_split(
#     files,
#     labels,
#     test_size=TEST_SPLIT,
#     stratify=labels,
#     random_state=RANDOM_STATE
# )

# print(f"Test files: {len(test_files)}")

# # ================= BUILD TEST DATA =================
# X_seq, X_feat, y = [], [], []

# for f, y_val in zip(test_files, test_labels):
#     data = json.load(open(f))

#     encoded_seq = vocab.encode(data["sequence"])

#     features = torch.tensor(
#         [data["features"].get(k, 0.0) for k in SELECTED_FEATURES],
#         dtype=torch.float
#     )

#     prefixes = generate_prefixes(encoded_seq, PREFIXES, MAX_LEN)

#     for p in prefixes:
#         X_seq.append(p)
#         X_feat.append(features)
#         y.append(y_val)

# # ================= NORMALIZE FEATURES =================
# scaler = StandardScaler()
# X_feat = scaler.fit_transform(torch.stack(X_feat).numpy())

# X_seq = torch.tensor(X_seq, dtype=torch.long)
# X_feat = torch.tensor(X_feat, dtype=torch.float)
# y = torch.tensor(y, dtype=torch.long)

# print(f"Evaluation samples: {len(y)}")

# # ================= LOAD MODEL =================
# model = BehavioralTransformer(
#     vocab_size=VOCAB_SIZE,
#     num_features=NUM_FEATURES,
#     max_len=MAX_LEN
# ).to(DEVICE)

# model.load_state_dict(
#     torch.load("models/transformer.pt", map_location=DEVICE)
# )

# model.eval()

# # ================= INFERENCE =================
# preds, labels_all = [], []

# with torch.no_grad():
#     for i in range(0, len(y), BATCH_SIZE):
#         xb_seq = X_seq[i:i+BATCH_SIZE].to(DEVICE)
#         xb_feat = X_feat[i:i+BATCH_SIZE].to(DEVICE)
#         yb = y[i:i+BATCH_SIZE].to(DEVICE)

#         out = model(xb_seq, xb_feat)
#         pred = torch.argmax(out, dim=1)

#         preds.extend(pred.cpu().numpy())
#         labels_all.extend(yb.cpu().numpy())

# # ================= METRICS =================
# acc = accuracy_score(labels_all, preds)
# p, r, f1, _ = precision_recall_fscore_support(
#     labels_all, preds, average="binary"
# )

# print("\n===== TEST SET PERFORMANCE =====")
# print(f"Accuracy : {acc:.4f}")
# print(f"Precision: {p:.4f}")
# print(f"Recall   : {r:.4f}")
# print(f"F1 Score : {f1:.4f}")

# # ================= CLASSIFICATION REPORT =================
# print("\n===== CLASSIFICATION REPORT =====")
# print(
#     classification_report(
#         labels_all,
#         preds,
#         target_names=["Benign", "Ransomware"],
#         digits=4
#     )
# )

# # ================= CONFUSION MATRIX =================
# cm = confusion_matrix(labels_all, preds)

# print("\n===== CONFUSION MATRIX =====")
# print(cm)

# os.makedirs("results", exist_ok=True)

# # ================= PLOT 1: CONFUSION MATRIX =================
# plt.figure(figsize=(6, 5))
# sns.heatmap(
#     cm,
#     annot=True,
#     fmt="d",
#     cmap="Blues",
#     cbar=False,
#     linewidths=1,
#     linecolor="black",
#     xticklabels=["Benign", "Ransomware"],
#     yticklabels=["Benign", "Ransomware"],
#     annot_kws={"size": 14, "weight": "bold"}
# )
# plt.xlabel("Predicted Class")
# plt.ylabel("True Class")
# plt.title("Confusion Matrix – Ransomware Detection")
# plt.tight_layout()
# plt.savefig("results/confusion_matrix.png", dpi=300)
# plt.show()

# # ================= PLOT 2: NORMALIZED CONFUSION MATRIX =================
# cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)

# plt.figure(figsize=(6, 5))
# sns.heatmap(
#     cm_norm,
#     annot=True,
#     fmt=".2f",
#     cmap="Greens",
#     cbar=False,
#     linewidths=1,
#     linecolor="black",
#     xticklabels=["Benign", "Ransomware"],
#     yticklabels=["Benign", "Ransomware"],
#     annot_kws={"size": 14}
# )
# plt.xlabel("Predicted Class")
# plt.ylabel("True Class")
# plt.title("Normalized Confusion Matrix")
# plt.tight_layout()
# plt.savefig("results/confusion_matrix_normalized.png", dpi=300)
# plt.show()

# # ================= PLOT 3: METRIC BAR CHART =================
# metrics = {
#     "Accuracy": acc,
#     "Precision": p,
#     "Recall": r,
#     "F1 Score": f1
# }

# plt.figure(figsize=(6, 4))
# plt.bar(metrics.keys(), metrics.values())
# plt.ylim(0.9, 1.01)
# plt.ylabel("Score")
# plt.title("Performance Metrics on Test Set")

# for i, v in enumerate(metrics.values()):
#     plt.text(i, v + 0.002, f"{v:.3f}", ha="center", fontsize=10)

# plt.tight_layout()
# plt.savefig("results/performance_metrics.png", dpi=300)
# plt.show()



import json
import torch
import torch.nn as nn
from pathlib import Path
import os
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    classification_report,
    confusion_matrix,
    roc_curve,
    auc,
    precision_recall_curve
)

import matplotlib.pyplot as plt
import seaborn as sns

from src.model.transformer import BehavioralTransformer
from src.encoding.event_vocab import EventVocab
from src.preprocessing.prefix import generate_prefixes

# ================= CONFIG =================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
PREFIXES = [64, 128, 256]
MAX_LEN = 256
BATCH_SIZE = 4
TEST_SPLIT = 0.30
RANDOM_STATE = 42

SELECTED_FEATURES = [
    "pslist.nproc","pslist.avg_threads","handles.nhandles","handles.nfile",
    "handles.nkey","dlllist.ndlls","ldrmodules.not_in_load",
    "psxview.not_in_pslist","psxview.not_in_session",
    "malfind.ninjections","malfind.uniqueInjections","svcscan.nservices",
]

# ================= LOAD VOCAB =================
vocab = EventVocab()
VOCAB_SIZE = len(vocab.token2id)

# ================= COLLECT FILES =================
files, labels = [], []

for label, y_val in [("ransomware", 1), ("benign", 0)]:
    for f in Path(f"data/processed/sequences/{label}").glob("*.json"):
        files.append(f)
        labels.append(y_val)

_, test_files, _, test_labels = train_test_split(
    files, labels, test_size=TEST_SPLIT,
    stratify=labels, random_state=RANDOM_STATE
)

# ================= BUILD TEST DATA =================
X_seq, X_feat, y = [], [], []

for f, y_val in zip(test_files, test_labels):
    data = json.load(open(f))
    encoded_seq = vocab.encode(data["sequence"])
    features = torch.tensor(
        [data["features"].get(k, 0.0) for k in SELECTED_FEATURES],
        dtype=torch.float
    )
    prefixes = generate_prefixes(encoded_seq, PREFIXES, MAX_LEN)
    for p in prefixes:
        X_seq.append(p)
        X_feat.append(features)
        y.append(y_val)

scaler = StandardScaler()
X_feat = scaler.fit_transform(torch.stack(X_feat).numpy())

X_seq = torch.tensor(X_seq, dtype=torch.long)
X_feat = torch.tensor(X_feat, dtype=torch.float)
y = torch.tensor(y, dtype=torch.long)

# ================= LOAD MODEL =================
model = BehavioralTransformer(
    vocab_size=VOCAB_SIZE,
    num_features=len(SELECTED_FEATURES),
    max_len=MAX_LEN
).to(DEVICE)

model.load_state_dict(torch.load("models/transformer.pt", map_location=DEVICE))
model.eval()

# ================= INFERENCE =================
preds, labels_all, probs_all = [], [], []

with torch.no_grad():
    for i in range(0, len(y), BATCH_SIZE):
        xb_seq = X_seq[i:i+BATCH_SIZE].to(DEVICE)
        xb_feat = X_feat[i:i+BATCH_SIZE].to(DEVICE)
        yb = y[i:i+BATCH_SIZE].to(DEVICE)

        out = model(xb_seq, xb_feat)
        prob = torch.softmax(out, dim=1)[:, 1]

        preds.extend(torch.argmax(out, dim=1).cpu().numpy())
        labels_all.extend(yb.cpu().numpy())
        probs_all.extend(prob.cpu().numpy())

labels_all = np.array(labels_all)
preds = np.array(preds)
probs_all = np.array(probs_all)

# ================= METRICS =================
acc = accuracy_score(labels_all, preds)
precision, recall, f1, support = precision_recall_fscore_support(
    labels_all,
    preds,
    average="binary"
)
precision = float(precision)
recall = float(recall)
f1 = float(f1)
acc = float(acc)

print("Accuracy:", acc)
print("Precision:", precision)
print("Recall:", recall)
print("F1:", f1)

os.makedirs("results", exist_ok=True)

# ================= CONFUSION MATRIX =================
cm = confusion_matrix(labels_all, preds)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues")
plt.title("Confusion Matrix")
plt.savefig("results/confusion_matrix.png", dpi=300)
plt.clf()

# ================= ROC CURVE =================
fpr, tpr, _ = roc_curve(labels_all, probs_all)
roc_auc = auc(fpr, tpr)

plt.plot(fpr, tpr)
plt.plot([0, 1], [0, 1])
plt.title(f"ROC Curve (AUC={roc_auc:.3f})")
plt.savefig("results/roc_curve.png", dpi=300)
plt.clf()

# ================= PRECISION-RECALL CURVE =================
precision_vals, recall_vals, _ = precision_recall_curve(labels_all, probs_all)
plt.plot(recall_vals, precision_vals)
plt.title("Precision–Recall Curve")
plt.savefig("results/pr_curve.png", dpi=300)
plt.clf()

# ================= PREFIX ACCURACY =================
prefix_acc = {}
for prefix in PREFIXES:
    correct, total = 0, 0
    for f, y_val in zip(test_files, test_labels):
        data = json.load(open(f))
        encoded_seq = vocab.encode(data["sequence"])
        features = torch.tensor(
            [data["features"].get(k, 0.0) for k in SELECTED_FEATURES],
            dtype=torch.float
        )
        prefixes = generate_prefixes(encoded_seq, [prefix], MAX_LEN)
        for p in prefixes:
            x_seq = torch.tensor([p], dtype=torch.long).to(DEVICE)
            x_feat = scaler.transform([features.numpy()])
            x_feat = torch.tensor(x_feat, dtype=torch.float).to(DEVICE)
            with torch.no_grad():
                out = model(x_seq, x_feat)
                pred = torch.argmax(out).item()
            correct += int(pred == y_val)
            total += 1
    prefix_acc[prefix] = correct / total

plt.plot(list(prefix_acc.keys()), list(prefix_acc.values()))
plt.title("Prefix Accuracy")
plt.savefig("results/prefix_accuracy.png", dpi=300)
plt.clf()

# ================= SAVE SUMMARY =================
summary = {
    "accuracy": acc,
    "precision": precision,
    "recall": recall,
    "f1": f1,
    "roc_auc": float(roc_auc),
    "prefix_accuracy": prefix_acc
}

with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=4)

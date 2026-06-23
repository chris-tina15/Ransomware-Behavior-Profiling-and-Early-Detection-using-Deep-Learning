# import json
# import os
# import torch
# import torch.nn as nn
# import torch.optim as optim
# from pathlib import Path

# from sklearn.model_selection import train_test_split
# from sklearn.preprocessing import StandardScaler
# from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# from src.model.transformer import BehavioralTransformer
# from src.encoding.event_vocab import EventVocab
# from src.preprocessing.prefix import generate_prefixes

# # ================= CONFIG =================
# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("Using device:", DEVICE)

# PREFIXES = [64, 128, 256]
# MAX_LEN = 256
# BATCH_SIZE = 4
# EPOCHS = 10
# LR = 3e-5
# TEST_SPLIT = 0.30
# RANDOM_STATE = 42

# # ================= MEMORY FEATURES =================
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
# print("Vocab size:", VOCAB_SIZE)

# # ================= COLLECT FILES =================
# files = []
# labels = []

# for label, y_val in [("ransomware", 1), ("benign", 0)]:
#     seq_dir = Path(f"data/processed/sequences/{label}")
#     for f in seq_dir.glob("*.json"):
#         files.append(f)
#         labels.append(y_val)

# train_files, test_files, train_labels, test_labels = train_test_split(
#     files,
#     labels,
#     test_size=TEST_SPLIT,
#     stratify=labels,
#     random_state=RANDOM_STATE
# )

# print(f"Train files: {len(train_files)} | Test files: {len(test_files)}")

# # ================= BUILD DATASETS =================
# def build_dataset(file_list, label_list):
#     X_seq, X_feat, y = [], [], []

#     for f, y_val in zip(file_list, label_list):
#         data = json.load(open(f))

#         # Encode sequence
#         encoded_seq = vocab.encode(data["sequence"])

#         # Extract features
#         features = torch.tensor(
#             [data["features"].get(k, 0.0) for k in SELECTED_FEATURES],
#             dtype=torch.float
#         )

#         prefixes = generate_prefixes(encoded_seq, PREFIXES, MAX_LEN)

#         for p in prefixes:
#             X_seq.append(p)
#             X_feat.append(features)
#             y.append(y_val)

#     return X_seq, X_feat, y

# # Build train and test sets
# X_seq_train, X_feat_train, y_train = build_dataset(train_files, train_labels)
# X_seq_test,  X_feat_test,  y_test  = build_dataset(test_files,  test_labels)

# print(f"Train samples: {len(y_train)} | Test samples: {len(y_test)}")

# # ================= NORMALIZE FEATURES (TRAIN ONLY) =================
# scaler = StandardScaler()
# X_feat_train = scaler.fit_transform(torch.stack(X_feat_train).numpy())
# X_feat_test  = scaler.transform(torch.stack(X_feat_test).numpy())

# # Convert to tensors
# X_seq_train = torch.tensor(X_seq_train, dtype=torch.long)
# X_feat_train = torch.tensor(X_feat_train, dtype=torch.float)
# y_train = torch.tensor(y_train, dtype=torch.long)

# X_seq_test = torch.tensor(X_seq_test, dtype=torch.long)
# X_feat_test = torch.tensor(X_feat_test, dtype=torch.float)
# y_test = torch.tensor(y_test, dtype=torch.long)

# # ================= MODEL =================
# model = BehavioralTransformer(
#     vocab_size=VOCAB_SIZE,
#     num_features=NUM_FEATURES,
#     max_len=MAX_LEN
# ).to(DEVICE)

# criterion = nn.CrossEntropyLoss()
# optimizer = optim.Adam(model.parameters(), lr=LR)

# # ================= TRAINING =================
# model.train()

# for epoch in range(EPOCHS):
#     total_loss = 0.0

#     for i in range(0, len(y_train), BATCH_SIZE):
#         xb_seq = X_seq_train[i:i+BATCH_SIZE].to(DEVICE)
#         xb_feat = X_feat_train[i:i+BATCH_SIZE].to(DEVICE)
#         yb = y_train[i:i+BATCH_SIZE].to(DEVICE)

#         optimizer.zero_grad()
#         outputs = model(xb_seq, xb_feat)
#         loss = criterion(outputs, yb)

#         loss.backward()
#         torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
#         optimizer.step()

#         total_loss += loss.item()

#     avg_loss = total_loss / (len(y_train) // BATCH_SIZE + 1)
#     print(f"Epoch {epoch+1}/{EPOCHS} | Avg Loss: {avg_loss:.4f}")

# # ================= EVALUATION (UNSEEN FILES) =================
# model.eval()
# preds, labels = [], []

# with torch.no_grad():
#     for i in range(0, len(y_test), BATCH_SIZE):
#         xb_seq = X_seq_test[i:i+BATCH_SIZE].to(DEVICE)
#         xb_feat = X_feat_test[i:i+BATCH_SIZE].to(DEVICE)
#         yb = y_test[i:i+BATCH_SIZE].to(DEVICE)

#         out = model(xb_seq, xb_feat)
#         pred = torch.argmax(out, dim=1)

#         preds.extend(pred.cpu().numpy())
#         labels.extend(yb.cpu().numpy())

# acc = accuracy_score(labels, preds)
# p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")

# print("\n===== TEST SET PERFORMANCE =====")
# print(f"Accuracy : {acc:.4f}")
# print(f"Precision: {p:.4f}")
# print(f"Recall   : {r:.4f}")
# print(f"F1 Score : {f1:.4f}")

# # ================= SAVE MODEL =================
# os.makedirs("models", exist_ok=True)
# torch.save(model.state_dict(), "models/transformer.pt")
# print("\n✅ Model saved → models/transformer.pt")


import json
import os
import torch
import torch.nn as nn
import torch.optim as optim
import joblib
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

from src.model.transformer import BehavioralTransformer
from src.encoding.event_vocab import EventVocab
from src.preprocessing.prefix import generate_prefixes

# ================= CONFIG =================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", DEVICE)

PREFIXES = [64, 128, 256]
MAX_LEN = 256
BATCH_SIZE = 4
EPOCHS = 10
LR = 3e-5
TEST_SPLIT = 0.30
RANDOM_STATE = 42

# ================= MEMORY FEATURES =================
SELECTED_FEATURES = [
    "pslist.nproc","pslist.avg_threads","handles.nhandles","handles.nfile",
    "handles.nkey","dlllist.ndlls","ldrmodules.not_in_load",
    "psxview.not_in_pslist","psxview.not_in_session",
    "malfind.ninjections","malfind.uniqueInjections","svcscan.nservices",
]

NUM_FEATURES = len(SELECTED_FEATURES)

# ================= LOAD VOCAB =================
vocab = EventVocab()
VOCAB_SIZE = len(vocab.token2id)
print("Vocab size:", VOCAB_SIZE)

# ================= COLLECT FILES =================
files, labels = [], []

for label, y_val in [("ransomware", 1), ("benign", 0)]:
    for f in Path(f"data/processed/sequences/{label}").glob("*.json"):
        files.append(f)
        labels.append(y_val)

train_files, test_files, train_labels, test_labels = train_test_split(
    files,
    labels,
    test_size=TEST_SPLIT,
    stratify=labels,
    random_state=RANDOM_STATE
)

print(f"Train files: {len(train_files)} | Test files: {len(test_files)}")

# ================= BUILD DATASET =================
def build_dataset(file_list, label_list):
    X_seq, X_feat, y = [], [], []

    for f, y_val in zip(file_list, label_list):
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

    return X_seq, X_feat, y

X_seq_train, X_feat_train, y_train = build_dataset(train_files, train_labels)
X_seq_test,  X_feat_test,  y_test  = build_dataset(test_files,  test_labels)

print(f"Train samples: {len(y_train)} | Test samples: {len(y_test)}")

# ================= NORMALIZE FEATURES =================
scaler = StandardScaler()
X_feat_train = scaler.fit_transform(torch.stack(X_feat_train).numpy())
X_feat_test  = scaler.transform(torch.stack(X_feat_test).numpy())

# SAVE SCALER FOR DASHBOARD
os.makedirs("models", exist_ok=True)
joblib.dump(scaler, "models/scaler.pkl")
print("Scaler saved → models/scaler.pkl")

# Convert to tensors
X_seq_train = torch.tensor(X_seq_train, dtype=torch.long)
X_feat_train = torch.tensor(X_feat_train, dtype=torch.float)
y_train = torch.tensor(y_train, dtype=torch.long)

X_seq_test = torch.tensor(X_seq_test, dtype=torch.long)
X_feat_test = torch.tensor(X_feat_test, dtype=torch.float)
y_test = torch.tensor(y_test, dtype=torch.long)

# ================= MODEL =================
model = BehavioralTransformer(
    vocab_size=VOCAB_SIZE,
    num_features=NUM_FEATURES,
    max_len=MAX_LEN
).to(DEVICE)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LR)

# ================= TRAINING =================
model.train()

for epoch in range(EPOCHS):
    total_loss = 0.0

    for i in range(0, len(y_train), BATCH_SIZE):
        xb_seq = X_seq_train[i:i+BATCH_SIZE].to(DEVICE)
        xb_feat = X_feat_train[i:i+BATCH_SIZE].to(DEVICE)
        yb = y_train[i:i+BATCH_SIZE].to(DEVICE)

        optimizer.zero_grad()
        outputs = model(xb_seq, xb_feat)
        loss = criterion(outputs, yb)

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()

        total_loss += loss.item()

    avg_loss = total_loss / (len(y_train) // BATCH_SIZE + 1)
    print(f"Epoch {epoch+1}/{EPOCHS} | Avg Loss: {avg_loss:.4f}")

# ================= EVALUATION =================
model.eval()
preds, labels = [], []

with torch.no_grad():
    for i in range(0, len(y_test), BATCH_SIZE):
        xb_seq = X_seq_test[i:i+BATCH_SIZE].to(DEVICE)
        xb_feat = X_feat_test[i:i+BATCH_SIZE].to(DEVICE)
        yb = y_test[i:i+BATCH_SIZE].to(DEVICE)

        out = model(xb_seq, xb_feat)
        pred = torch.argmax(out, dim=1)

        preds.extend(pred.cpu().numpy())
        labels.extend(yb.cpu().numpy())

acc = accuracy_score(labels, preds)
p, r, f1, _ = precision_recall_fscore_support(labels, preds, average="binary")

print("\n===== TEST SET PERFORMANCE =====")
print(f"Accuracy : {acc:.4f}")
print(f"Precision: {p:.4f}")
print(f"Recall   : {r:.4f}")
print(f"F1 Score : {f1:.4f}")

# ================= SAVE MODEL =================
torch.save(model.state_dict(), "models/transformer.pt")
print("Model saved → models/transformer.pt")

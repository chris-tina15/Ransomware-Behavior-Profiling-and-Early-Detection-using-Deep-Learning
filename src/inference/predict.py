import torch
from src.model.transformer import BehavioralTransformer

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
WINDOW_SIZE = 256
STRIDE = 256


def create_windows(sequence, window_size, stride):
    windows = []
    for i in range(0, len(sequence), stride):
        window = sequence[i:i + window_size]
        if len(window) < window_size:
            window = window + [0] * (window_size - len(window))
        windows.append(window)
    return windows


def predict(events, vocab, threshold=0.6):
    """
    Returns detailed prediction results for dashboard visualization.
    """

    # -------- Encode events --------
    encoded = vocab.encode(events)

    # -------- Windowing --------
    windows = create_windows(encoded, WINDOW_SIZE, STRIDE)
    X = torch.tensor(windows, dtype=torch.long).to(DEVICE)

    # -------- Load model --------
    model = BehavioralTransformer(
        vocab_size=len(vocab.token2id),
        max_len=WINDOW_SIZE
    ).to(DEVICE)

    model.load_state_dict(
        torch.load("models/transformer.pt", map_location=DEVICE)
    )
    model.eval()

    # -------- Inference --------
    with torch.no_grad():
        logits = model(X)
        probs = torch.softmax(logits, dim=1)[:, 1]  # ransomware probability

    # -------- Aggregate decision --------
    avg_risk = probs.mean().item()
    malicious_windows = (probs > threshold).sum().item()
    total_windows = len(probs)

    verdict = 1 if malicious_windows / total_windows >= 0.5 else 0

    return {
        "verdict": verdict,
        "avg_risk": avg_risk,
        "malicious_windows": malicious_windows,
        "total_windows": total_windows,
        "window_probs": probs.cpu().tolist()
    }

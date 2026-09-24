import torch
import torch.nn as nn

class BehavioralTransformer(nn.Module):
    def __init__(
        self,
        vocab_size,
        num_features,
        d_model=128,
        n_heads=4,
        n_layers=3,
        max_len=256
    ):
        super().__init__()

        # ===== Token embedding =====
        self.embedding = nn.Embedding(
            vocab_size, d_model, padding_idx=0
        )

        # ===== Positional encoding =====
        self.positional_encoding = nn.Parameter(
            torch.zeros(1, max_len, d_model)
        )

        # ===== Transformer encoder =====
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=n_heads,
            batch_first=True
        )

        self.encoder = nn.TransformerEncoder(
            encoder_layer, n_layers
        )

        # ===== Feature projection (TABULAR → EMBEDDING) =====
        self.feature_proj = nn.Linear(num_features, d_model)

        # ===== Classifier =====
        self.classifier = nn.Linear(d_model, 2)

    def forward(self, x_seq, x_feat):
        """
        x_seq  : (B, T)
        x_feat : (B, F)
        """

        seq_len = x_seq.size(1)

        # Token + position embedding
        x = self.embedding(x_seq)
        x = x + self.positional_encoding[:, :seq_len]

        # Transformer encoding
        x = self.encoder(x)

        # Temporal pooling
        seq_repr = x.mean(dim=1)

        # Feature embedding
        feat_repr = self.feature_proj(x_feat)

        # Fusion (additive works best here)
        fused = seq_repr + feat_repr

        return self.classifier(fused)

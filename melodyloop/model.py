"""
PyTorch LSTM Architecture for MelodyLoop.
Multi-task next-event prediction (pitch, duration, step).
"""

from typing import Tuple, Dict, Any
import torch
import torch.nn as nn
from config import Config


class MelodyLSTM(nn.Module):
    """
    Small, educational LSTM model for sequential music generation.
    Takes sequences of (pitch, duration_bin, step_bin) tokens and
    predicts the categorical distributions of the next event.
    """

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg

        # Embedding layers for each discrete attribute
        self.pitch_embed = nn.Embedding(cfg.pitch_vocab_size, cfg.pitch_embed_dim)
        self.duration_embed = nn.Embedding(cfg.duration_bins, cfg.duration_embed_dim)
        self.step_embed = nn.Embedding(cfg.step_bins, cfg.step_embed_dim)

        self.input_dim = cfg.pitch_embed_dim + cfg.duration_embed_dim + cfg.step_embed_dim

        # Core recurrent layer
        self.lstm = nn.LSTM(
            input_size=self.input_dim,
            hidden_size=cfg.hidden_dim,
            num_layers=cfg.num_layers,
            batch_first=True,
            dropout=cfg.dropout if cfg.num_layers > 1 else 0.0,
        )

        # Normalization and dropout for stability
        self.dropout = nn.Dropout(cfg.dropout)

        # Multi-task categorical prediction heads
        self.head_pitch = nn.Linear(cfg.hidden_dim, cfg.pitch_vocab_size)
        self.head_duration = nn.Linear(cfg.hidden_dim, cfg.duration_bins)
        self.head_step = nn.Linear(cfg.hidden_dim, cfg.step_bins)

    def forward(
        self,
        x: torch.Tensor,
        hidden: Tuple[torch.Tensor, torch.Tensor] | None = None,
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        """
        Forward pass.
        Args:
            x: Tensor of shape (batch_size, seq_len, 3) where columns are (pitch, dur, step)
            hidden: Optional (h_0, c_0) state
        Returns:
            logits_pitch: (batch_size, pitch_vocab_size)
            logits_dur:   (batch_size, duration_bins)
            logits_step:  (batch_size, step_bins)
            hidden:       (h_n, c_n)
        """
        p_emb = self.pitch_embed(x[:, :, 0])
        d_emb = self.duration_embed(x[:, :, 1])
        s_emb = self.step_embed(x[:, :, 2])

        # Concatenate along feature dimension -> (batch_size, seq_len, input_dim)
        combined = torch.cat([p_emb, d_emb, s_emb], dim=-1)

        # LSTM pass
        out, next_hidden = self.lstm(combined, hidden)

        # Take output of last timestep for next-event prediction
        last_out = self.dropout(out[:, -1, :])

        logits_pitch = self.head_pitch(last_out)
        logits_duration = self.head_duration(last_out)
        logits_step = self.head_step(last_out)

        return logits_pitch, logits_duration, logits_step, next_hidden

    def compute_loss(
        self,
        logits_p: torch.Tensor,
        logits_d: torch.Tensor,
        logits_s: torch.Tensor,
        target_p: torch.Tensor,
        target_d: torch.Tensor,
        target_s: torch.Tensor,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Compute multi-task categorical cross-entropy loss."""
        loss_fn = nn.CrossEntropyLoss()
        l_pitch = loss_fn(logits_p, target_p)
        l_dur = loss_fn(logits_d, target_d)
        l_step = loss_fn(logits_s, target_s)

        total_loss = l_pitch + l_dur + l_step
        metrics = {
            "loss_total": float(total_loss.item()),
            "loss_pitch": float(l_pitch.item()),
            "loss_dur": float(l_dur.item()),
            "loss_step": float(l_step.item()),
        }
        return total_loss, metrics

    def count_parameters(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)

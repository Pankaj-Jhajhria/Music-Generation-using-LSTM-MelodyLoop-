"""
Conditional PyTorch LSTM Architecture for MelodyLoop 2.0.
Condition-aware multi-task next-event prediction (pitch, duration, step, velocity)
conditioned on structured musical attributes (mood, tempo, pitch register, dynamics).
"""

from typing import Tuple, Dict, Any, Optional
import torch
import torch.nn as nn
from config import Config


class ConditionalMelodyLSTM(nn.Module):
    """
    Condition-Aware LSTM for educational musical sequence generation.
    Takes sequences of 4-token events (pitch, duration, step, velocity) and
    a condition vector (mood, tempo, register, dynamics), projecting them into a shared
    recurrent state space to predict the next event's multi-attribute distribution.
    """

    def __init__(
        self,
        cfg: Config,
        velocity_bins: int = 16,
        mood_vocab_size: int = 7,
        tempo_vocab_size: int = 4,
        register_vocab_size: int = 4,
        dynamics_vocab_size: int = 4,
        velocity_embed_dim: int = 16,
        mood_embed_dim: int = 16,
        tempo_embed_dim: int = 8,
        register_embed_dim: int = 8,
        dynamics_embed_dim: int = 8,
    ):
        super().__init__()
        self.cfg = cfg
        self.velocity_bins = velocity_bins

        # Note event embeddings
        self.pitch_embed = nn.Embedding(cfg.pitch_vocab_size, cfg.pitch_embed_dim)
        self.duration_embed = nn.Embedding(cfg.duration_bins, cfg.duration_embed_dim)
        self.step_embed = nn.Embedding(cfg.step_bins, cfg.step_embed_dim)
        self.velocity_embed = nn.Embedding(velocity_bins, velocity_embed_dim)

        self.event_dim = (
            cfg.pitch_embed_dim
            + cfg.duration_embed_dim
            + cfg.step_embed_dim
            + velocity_embed_dim
        )

        # Condition attribute embeddings
        self.mood_embed = nn.Embedding(mood_vocab_size, mood_embed_dim)
        self.tempo_embed = nn.Embedding(tempo_vocab_size, tempo_embed_dim)
        self.register_embed = nn.Embedding(register_vocab_size, register_embed_dim)
        self.dynamics_embed = nn.Embedding(dynamics_vocab_size, dynamics_embed_dim)

        self.cond_dim = (
            mood_embed_dim
            + tempo_embed_dim
            + register_embed_dim
            + dynamics_embed_dim
        )

        # Total input dimension per timestep
        self.input_dim = self.event_dim + self.cond_dim

        # Recurrent LSTM
        self.lstm = nn.LSTM(
            input_size=self.input_dim,
            hidden_size=cfg.hidden_dim,
            num_layers=cfg.num_layers,
            batch_first=True,
            dropout=cfg.dropout if cfg.num_layers > 1 else 0.0,
        )

        self.dropout = nn.Dropout(cfg.dropout)

        # Multi-task prediction heads
        self.head_pitch = nn.Linear(cfg.hidden_dim, cfg.pitch_vocab_size)
        self.head_duration = nn.Linear(cfg.hidden_dim, cfg.duration_bins)
        self.head_step = nn.Linear(cfg.hidden_dim, cfg.step_bins)
        self.head_velocity = nn.Linear(cfg.hidden_dim, velocity_bins)

    def forward(
        self,
        x: torch.Tensor,
        cond: torch.Tensor,
        hidden: Optional[Tuple[torch.Tensor, torch.Tensor]] = None,
    ) -> Tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        Tuple[torch.Tensor, torch.Tensor],
    ]:
        """
        Forward pass.
        Args:
            x: Tensor of shape (batch_size, seq_len, 4) -> [pitch, dur, step, vel]
            cond: Tensor of shape (batch_size, 4) -> [mood, tempo, reg, dyn]
            hidden: Optional recurrent state tuple (h_0, c_0)
        Returns:
            logits_pitch:    (batch_size, pitch_vocab_size)
            logits_duration: (batch_size, duration_bins)
            logits_step:     (batch_size, step_bins)
            logits_velocity: (batch_size, velocity_bins)
            hidden:          (h_n, c_n)
        """
        batch_size, seq_len, _ = x.shape

        # Event embeddings -> (batch_size, seq_len, dim)
        p_emb = self.pitch_embed(x[:, :, 0])
        d_emb = self.duration_embed(x[:, :, 1])
        s_emb = self.step_embed(x[:, :, 2])
        v_emb = self.velocity_embed(x[:, :, 3])
        event_emb = torch.cat([p_emb, d_emb, s_emb, v_emb], dim=-1)

        # Condition embeddings -> (batch_size, cond_dim)
        m_emb = self.mood_embed(cond[:, 0])
        t_emb = self.tempo_embed(cond[:, 1])
        r_emb = self.register_embed(cond[:, 2])
        dyn_emb = self.dynamics_embed(cond[:, 3])
        cond_emb = torch.cat([m_emb, t_emb, r_emb, dyn_emb], dim=-1)

        # Broadcast condition vector across all time steps -> (batch_size, seq_len, cond_dim)
        cond_broadcast = cond_emb.unsqueeze(1).expand(-1, seq_len, -1)

        # Combined recurrent input -> (batch_size, seq_len, input_dim)
        lstm_input = torch.cat([event_emb, cond_broadcast], dim=-1)

        out, next_hidden = self.lstm(lstm_input, hidden)

        # Last timestep hidden output for next-event prediction
        last_out = self.dropout(out[:, -1, :])

        logits_pitch = self.head_pitch(last_out)
        logits_duration = self.head_duration(last_out)
        logits_step = self.head_step(last_out)
        logits_velocity = self.head_velocity(last_out)

        return (
            logits_pitch,
            logits_duration,
            logits_step,
            logits_velocity,
            next_hidden,
        )

    def compute_loss(
        self,
        logits_p: torch.Tensor,
        logits_d: torch.Tensor,
        logits_s: torch.Tensor,
        logits_v: torch.Tensor,
        target_p: torch.Tensor,
        target_d: torch.Tensor,
        target_s: torch.Tensor,
        target_v: torch.Tensor,
    ) -> Tuple[torch.Tensor, Dict[str, float]]:
        """Compute multi-task categorical cross-entropy loss."""
        loss_fn = nn.CrossEntropyLoss()
        l_pitch = loss_fn(logits_p, target_p)
        l_dur = loss_fn(logits_d, target_d)
        l_step = loss_fn(logits_s, target_s)
        l_vel = loss_fn(logits_v, target_v)

        total_loss = l_pitch + l_dur + l_step + l_vel
        metrics = {
            "loss_total": float(total_loss.item()),
            "loss_pitch": float(l_pitch.item()),
            "loss_dur": float(l_dur.item()),
            "loss_step": float(l_step.item()),
            "loss_vel": float(l_vel.item()),
        }
        return total_loss, metrics

    def get_parameter_count(self) -> int:
        """Return total trainable parameter count."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


"""
Unit tests for MelodyLSTM model architecture.
"""

import torch
from config import Config
from melodyloop.model import MelodyLSTM


def test_model_forward_and_loss():
    cfg = Config(hidden_dim=64, num_layers=1)
    model = MelodyLSTM(cfg)
    
    batch_size = 4
    seq_len = 16
    
    # Random token indices
    x = torch.randint(0, 16, (batch_size, seq_len, 3))
    
    logits_p, logits_d, logits_s, hidden = model(x)
    
    assert logits_p.shape == (batch_size, cfg.pitch_vocab_size)
    assert logits_d.shape == (batch_size, cfg.duration_bins)
    assert logits_s.shape == (batch_size, cfg.step_bins)
    assert hidden is not None
    assert hidden[0].shape == (1, batch_size, cfg.hidden_dim)
    
    # Test loss computation and backprop
    target_p = torch.randint(0, cfg.pitch_vocab_size, (batch_size,))
    target_d = torch.randint(0, cfg.duration_bins, (batch_size,))
    target_s = torch.randint(0, cfg.step_bins, (batch_size,))
    
    loss, metrics = model.compute_loss(logits_p, logits_d, logits_s, target_p, target_d, target_s)
    
    assert torch.isfinite(loss)
    assert loss.item() > 0.0
    assert "loss_pitch" in metrics and "loss_dur" in metrics and "loss_step" in metrics
    
    loss.backward()
    
    # Verify gradients computed
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"Gradient missing for {name}"
            assert torch.isfinite(param.grad).all(), f"Gradient non-finite for {name}"


def test_model_parameter_count():
    cfg = Config(hidden_dim=128, num_layers=1)
    model = MelodyLSTM(cfg)
    num_params = model.count_parameters()
    assert 50000 < num_params < 300000, f"Unexpected parameter count: {num_params}"

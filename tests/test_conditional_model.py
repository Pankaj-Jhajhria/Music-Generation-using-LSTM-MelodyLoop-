"""
Unit tests for ConditionalMelodyLSTM model architecture, forward pass,
loss computation, backpropagation, and checkpoint saving/loading.
"""

import tempfile
from pathlib import Path
import torch
import pytest

from config import Config
from melodyloop.conditional_model import ConditionalMelodyLSTM


def test_model_parameter_count_and_init():
    cfg = Config()
    model = ConditionalMelodyLSTM(cfg)
    param_count = model.get_parameter_count()
    assert param_count == 198304
    assert model.input_dim == 184


def test_forward_pass_output_shapes():
    cfg = Config()
    model = ConditionalMelodyLSTM(cfg)
    model.eval()

    batch_size = 8
    seq_len = 32
    x = torch.randint(0, 16, (batch_size, seq_len, 4))
    cond = torch.randint(0, 4, (batch_size, 4))

    with torch.no_grad():
        lp, ld, ls, lv, hidden = model(x, cond)

    assert lp.shape == (batch_size, cfg.pitch_vocab_size)
    assert ld.shape == (batch_size, cfg.duration_bins)
    assert ls.shape == (batch_size, cfg.step_bins)
    assert lv.shape == (batch_size, 16)
    assert hidden[0].shape == (cfg.num_layers, batch_size, cfg.hidden_dim)
    assert hidden[1].shape == (cfg.num_layers, batch_size, cfg.hidden_dim)


def test_loss_computation_and_backward():
    cfg = Config()
    model = ConditionalMelodyLSTM(cfg)
    model.train()

    batch_size = 4
    x = torch.randint(0, 16, (batch_size, 16, 4))
    cond = torch.randint(0, 4, (batch_size, 4))

    lp, ld, ls, lv, _ = model(x, cond)

    target_p = torch.randint(0, cfg.pitch_vocab_size, (batch_size,))
    target_d = torch.randint(0, cfg.duration_bins, (batch_size,))
    target_s = torch.randint(0, cfg.step_bins, (batch_size,))
    target_v = torch.randint(0, 16, (batch_size,))

    loss, metrics = model.compute_loss(lp, ld, ls, lv, target_p, target_d, target_s, target_v)
    assert torch.isfinite(loss)
    assert loss.item() > 0.0
    assert "loss_pitch" in metrics
    assert "loss_vel" in metrics

    loss.backward()
    for name, param in model.named_parameters():
        if param.requires_grad:
            assert param.grad is not None, f"Parameter {name} has no gradient"


def test_checkpoint_save_and_load():
    cfg = Config()
    model = ConditionalMelodyLSTM(cfg)

    with tempfile.TemporaryDirectory() as tmpdir:
        ckpt_path = Path(tmpdir) / "test_conditional.pt"
        torch.save(
            {
                "epoch": 3,
                "model_state_dict": model.state_dict(),
                "val_loss": 8.52,
                "cfg": cfg,
            },
            str(ckpt_path),
        )

        loaded_ckpt = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
        assert loaded_ckpt["epoch"] == 3
        assert loaded_ckpt["val_loss"] == 8.52

        model.eval()
        model_loaded = ConditionalMelodyLSTM(cfg)
        model_loaded.load_state_dict(loaded_ckpt["model_state_dict"])
        model_loaded.eval()

        x = torch.randint(0, 16, (2, 16, 4))
        cond = torch.randint(0, 4, (2, 4))
        lp1, _, _, _, _ = model(x, cond)
        lp2, _, _, _, _ = model_loaded(x, cond)
        assert torch.allclose(lp1, lp2)

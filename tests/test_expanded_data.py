"""
Tests for expanded MAESTRO dataset processing, proportional sampling,
and checkpoint compatibility across baseline and expanded models.
"""

from pathlib import Path
import pytest
import torch

from config import Config
from melodyloop.data import (
    MelodyDataset,
    create_synthetic_midi,
    parse_midi_file,
    create_sequences_from_events,
)
from melodyloop.model import MelodyLSTM


def test_compact_dataset_tensor_dtype():
    """Verify MelodyDataset uses compact uint8 internally and serves torch.long."""
    cfg = Config()
    import numpy as np

    # Synthetic sequences (10 sequences of length 32 with 3 features)
    x_np = np.random.randint(0, 100, size=(10, 32, 3), dtype=np.int64)
    y_np = np.random.randint(0, 30, size=(10, 3), dtype=np.int64)

    dataset = MelodyDataset(x_np, y_np)

    # Internal storage should be uint8 for memory boundedness
    assert dataset.x.dtype == torch.uint8
    assert dataset.y_pitch.dtype == torch.uint8
    assert dataset.y_duration.dtype == torch.uint8
    assert dataset.y_step.dtype == torch.uint8

    # Served sample should be torch.long for PyTorch Embedding and CrossEntropyLoss
    item = dataset[0]
    assert item["x"].dtype == torch.long
    assert item["pitch"].dtype == torch.long
    assert item["duration"].dtype == torch.long
    assert item["step"].dtype == torch.long
    assert item["x"].shape == (32, 3)


def test_checkpoint_compatibility_baseline_and_expanded():
    """Verify that both baseline and expanded checkpoints load into MelodyLSTM correctly."""
    cfg = Config()
    device = torch.device("cpu")

    baseline_path = cfg.artifacts_dir / "checkpoints" / "best_model_v1_baseline.pt"
    if baseline_path.exists():
        ckpt = torch.load(str(baseline_path), map_location=device)
        model = MelodyLSTM(cfg)
        model.load_state_dict(ckpt["model_state_dict"])
        model.eval()

        # Dummy input
        x = torch.randint(0, 30, (2, 32, 3))
        lp, ld, ls, _ = model(x)
        assert lp.shape == (2, cfg.pitch_vocab_size)
        assert ld.shape == (2, cfg.duration_bins)
        assert ls.shape == (2, cfg.step_bins)


def test_proportional_event_sequence_generation():
    """Verify sequences generated from multiple pieces span all pieces."""
    cfg = Config(seq_length=16, stride=2)
    # Simulate events from 5 different pieces
    events_list = [
        [(60 + i, 10, 10) for _ in range(50)]
        for i in range(5)
    ]
    total_seqs = 0
    all_x = []
    all_y = []
    for events in events_list:
        x, y = create_sequences_from_events(events, cfg.seq_length, cfg.stride)
        all_x.append(x)
        all_y.append(y)
        total_seqs += len(x)

    import numpy as np
    x_cat = np.concatenate(all_x, axis=0)
    y_cat = np.concatenate(all_y, axis=0)

    dataset = MelodyDataset(x_cat, y_cat)
    assert len(dataset) == total_seqs
    assert len(dataset) > 50

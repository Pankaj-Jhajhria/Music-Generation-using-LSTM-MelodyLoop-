"""
MelodyLoop Configuration
Educational LSTM-based Music Generation from MIDI
"""

import os
import torch
from dataclasses import dataclass, field
from pathlib import Path


def get_base_dir() -> Path:
    return Path(__file__).resolve().parent


def find_maestro_dir() -> Path:
    """Auto-locate MAESTRO dataset directory within the workspace."""
    base = get_base_dir()
    candidates = [
        base / "data_maestrov3.0.0-midi" / "maestro-v3.0.0",
        base / "data_maestrov3.0.0-midi",
        base / "maestro-v3.0.0",
    ]
    for c in candidates:
        if (c / "maestro-v3.0.0.csv").exists():
            return c
    
    # Recursive search if not in expected candidates
    for p in base.glob("**/maestro-v3.0.0.csv"):
        return p.parent
        
    return base / "data_maestrov3.0.0-midi" / "maestro-v3.0.0"


def detect_device() -> str:
    """Detect best available device (CUDA if torch has CUDA support, else CPU)."""
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


@dataclass
class Config:
    # Paths
    base_dir: Path = field(default_factory=get_base_dir)
    data_dir: Path = field(default_factory=find_maestro_dir)
    csv_filename: str = "maestro-v3.0.0.csv"
    
    artifacts_dir: Path = field(default_factory=lambda: get_base_dir() / "artifacts")
    checkpoints_dir: Path = field(default_factory=lambda: get_base_dir() / "artifacts" / "checkpoints")
    generated_dir: Path = field(default_factory=lambda: get_base_dir() / "artifacts" / "generated")
    logs_dir: Path = field(default_factory=lambda: get_base_dir() / "artifacts" / "logs")
    
    # Quantization / Representation
    pitch_vocab_size: int = 128       # Standard MIDI pitches 0-127
    duration_bins: int = 32           # Quantized note duration bins
    step_bins: int = 32               # Quantized time-gap (step) to next note bins
    min_duration: float = 0.05        # Seconds (shortest note)
    max_duration: float = 4.0         # Seconds (longest note)
    min_step: float = 0.0             # Seconds (chord / simultaneous notes)
    max_step: float = 2.0             # Seconds (maximum pause between note onsets)
    
    # Model architecture
    pitch_embed_dim: int = 64
    duration_embed_dim: int = 32
    step_embed_dim: int = 32
    hidden_dim: int = 128
    num_layers: int = 1
    dropout: float = 0.1
    
    # Data & Sequences
    seq_length: int = 32              # Number of note events per input sequence
    stride: int = 4                   # Stride when sliding window over notes
    max_train_files: int = 25         # Bounded sample of MAESTRO train performances
    max_val_files: int = 5            # Bounded sample of MAESTRO val performances
    max_train_sequences: int = 40000  # Cap total sequences to respect RAM (bounds memory)
    max_val_sequences: int = 5000
    
    # Training
    device: str = field(default_factory=detect_device)
    batch_size: int = 32 if torch.cuda.is_available() else 16
    epochs: int = 6 if torch.cuda.is_available() else 3
    learning_rate: float = 1e-3
    weight_decay: float = 1e-5
    seed: int = 42
    save_every_epoch: bool = True
    
    # Generation defaults
    default_gen_length: int = 100
    default_temperature: float = 0.9
    tempo_bpm: int = 120
    
    def __post_init__(self):
        # Create output directories safely
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoints_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
    @property
    def csv_path(self) -> Path:
        return self.data_dir / self.csv_filename

    @property
    def best_model_path(self) -> Path:
        return self.checkpoints_dir / "best_model.pt"

    @property
    def latest_model_path(self) -> Path:
        return self.checkpoints_dir / "latest_model.pt"

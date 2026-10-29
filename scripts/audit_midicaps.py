"""
Streaming audit script for MidiCaps dataset.
Reads data_midicaps/train.json line by line with minimal memory usage.
"""

import json
import os
import sys
from collections import Counter
from pathlib import Path


def run_audit(json_path: str, midi_root: str):
    print(f"Starting MidiCaps dataset audit on: {json_path}")
    print(f"MIDI root: {midi_root}")

    total_rows = 0
    unique_locations = set()
    test_set_counts = Counter()
    missing_fields = Counter()
    all_moods = Counter()
    all_genres = Counter()
    tempo_words = Counter()
    duration_words = Counter()
    tempos = []
    durations = []
    caption_word_lens = []

    solo_piano_count = 0
    any_piano_count = 0
    no_piano_count = 0

    files_checked = 0
    files_exist = 0
    files_missing = 0

    PIANO_PROGRAMS = set(range(8))  # General MIDI 0-7

    with open(json_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f):
            total_rows += 1
            if total_rows % 20000 == 0:
                print(f"Processed {total_rows} records...")

            record = json.loads(line)

            loc = record.get("location")
            if not loc:
                missing_fields["location"] += 1
            else:
                unique_locations.add(loc)

            # Check file existence for a sample or all
            # Since checking 168k files on disk with os.path.exists takes 1-2s in Python:
            midi_path = os.path.join(midi_root, loc) if loc else None
            if midi_path and os.path.exists(midi_path):
                files_exist += 1
            else:
                files_missing += 1

            test_val = record.get("test_set", None)
            test_set_counts[test_val] += 1

            # Moods
            moods = record.get("mood", [])
            if not moods:
                missing_fields["mood"] += 1
            else:
                for m in moods:
                    all_moods[m.strip().lower()] += 1

            # Genres
            genres = record.get("genre", [])
            if not genres:
                missing_fields["genre"] += 1
            else:
                for g in genres:
                    all_genres[g.strip().lower()] += 1

            # Tempo
            tw = record.get("tempo_word")
            if tw:
                tempo_words[tw] += 1
            else:
                missing_fields["tempo_word"] += 1

            t_val = record.get("tempo")
            if t_val is not None:
                tempos.append(float(t_val))
            else:
                missing_fields["tempo"] += 1

            # Duration
            dw = record.get("duration_word")
            if dw:
                duration_words[dw] += 1
            else:
                missing_fields["duration_word"] += 1

            d_val = record.get("duration")
            if d_val is not None:
                durations.append(float(d_val))
            else:
                missing_fields["duration"] += 1

            # Captions
            caption = record.get("caption", "")
            if caption:
                caption_word_lens.append(len(caption.split()))
            else:
                missing_fields["caption"] += 1

            # Instruments
            inst_nums = record.get("instrument_numbers_sorted", [])
            inst_summary = record.get("instrument_summary", [])

            # Check piano
            has_piano_num = any(p in PIANO_PROGRAMS for p in inst_nums)
            has_piano_summary = any("piano" in str(s).lower() for s in inst_summary)
            is_piano = has_piano_num or has_piano_summary

            is_solo_piano_num = inst_nums and all(p in PIANO_PROGRAMS for p in inst_nums)
            is_solo_piano_summary = inst_summary and all("piano" in str(s).lower() for s in inst_summary)
            is_solo = is_solo_piano_num or (is_solo_piano_summary and not [x for x in inst_nums if x not in PIANO_PROGRAMS])

            if is_solo:
                solo_piano_count += 1
            elif is_piano:
                any_piano_count += 1
            else:
                no_piano_count += 1

    print("\n" + "=" * 60)
    print("AUDIT RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total metadata records: {total_rows}")
    print(f"Unique location paths: {len(unique_locations)}")
    print(f"Files existing on disk: {files_exist}")
    print(f"Files missing on disk: {files_missing}")
    print(f"test_set distribution: {dict(test_set_counts)}")
    print(f"Solo Piano records: {solo_piano_count} ({solo_piano_count/total_rows*100:.2f}%)")
    print(f"Ensemble with Piano records: {any_piano_count} ({any_piano_count/total_rows*100:.2f}%)")
    print(f"Total with Piano: {solo_piano_count + any_piano_count} ({(solo_piano_count + any_piano_count)/total_rows*100:.2f}%)")
    print(f"No Piano records: {no_piano_count} ({no_piano_count/total_rows*100:.2f}%)")
    print(f"Missing fields: {dict(missing_fields)}")

    import numpy as np
    tempos_arr = np.array(tempos)
    durations_arr = np.array(durations)
    caps_arr = np.array(caption_word_lens)

    print(f"\nTempo (BPM): min={tempos_arr.min():.1f}, 25%={np.percentile(tempos_arr, 25):.1f}, "
          f"median={np.median(tempos_arr):.1f}, 75%={np.percentile(tempos_arr, 75):.1f}, max={tempos_arr.max():.1f}")
    print(f"Top 10 Tempo words: {tempo_words.most_common(10)}")

    print(f"\nDuration (sec): min={durations_arr.min():.1f}, median={np.median(durations_arr):.1f}, max={durations_arr.max():.1f}")
    print(f"Top Duration words: {duration_words.most_common(10)}")

    print(f"\nCaption length (words): min={caps_arr.min()}, median={np.median(caps_arr):.1f}, max={caps_arr.max()}")

    print(f"\nTop 25 Moods: {all_moods.most_common(25)}")
    print(f"Total unique moods: {len(all_moods)}")

    print(f"\nTop 15 Genres: {all_genres.most_common(15)}")
    print(f"Total unique genres: {len(all_genres)}")

    # Save summary dictionary as JSON for generating the markdown report
    summary = {
        "total_records": total_rows,
        "unique_locations": len(unique_locations),
        "files_existing": files_exist,
        "files_missing": files_missing,
        "test_set_counts": dict(test_set_counts),
        "solo_piano_count": solo_piano_count,
        "ensemble_with_piano_count": any_piano_count,
        "total_piano_count": solo_piano_count + any_piano_count,
        "no_piano_count": no_piano_count,
        "missing_fields": dict(missing_fields),
        "tempo_stats": {
            "min": float(tempos_arr.min()),
            "p25": float(np.percentile(tempos_arr, 25)),
            "median": float(np.median(tempos_arr)),
            "p75": float(np.percentile(tempos_arr, 75)),
            "max": float(tempos_arr.max()),
        },
        "top_tempo_words": tempo_words.most_common(15),
        "top_duration_words": duration_words.most_common(10),
        "top_moods": all_moods.most_common(35),
        "total_unique_moods": len(all_moods),
        "top_genres": all_genres.most_common(20),
        "total_unique_genres": len(all_genres),
    }

    out_file = Path("artifacts") / "midicaps_audit_summary.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as out_f:
        json.dump(summary, out_f, indent=2)
    print(f"\nAudit summary saved to {out_file}")


if __name__ == "__main__":
    json_path = os.path.join("data_midicaps", "train.json")
    midi_root = os.path.join("data_midicaps", "midicaps")
    run_audit(json_path, midi_root)

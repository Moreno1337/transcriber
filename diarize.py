import argparse
import json
import os
import time
import subprocess

from pathlib import Path

import torch
from pyannote.audio import Pipeline

# Compatibilidade com checkpoints do pyannote.
# Aplicar somente a modelos de origem confiável.
_original_torch_load = torch.load

def trusted_torch_load(*args, **kwargs):
    kwargs["weights_only"] = False
    return _original_torch_load(*args, **kwargs)

torch.load = trusted_torch_load

def load_audio(path):
    print("Extraindo áudio com FFmpeg...", flush=True)

    command = [
        "ffmpeg",
        "-nostdin",
        "-v", "error",
        "-i", str(path),
        "-map", "0:a:0",
        "-f", "f32le",
        "-acodec", "pcm_f32le",
        "-ac", "1",
        "-ar", "16000",
        "pipe:1",
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )

    import numpy as np

    audio = np.frombuffer(
        result.stdout,
        dtype=np.float32,
    ).copy()

    if audio.size == 0:
        raise RuntimeError("Nenhum áudio foi extraído.")

    waveform = torch.from_numpy(audio).unsqueeze(0)

    return {
        "waveform": waveform,
        "sample_rate": 16000,
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    input_path = Path("/app/input") / args.filename

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {input_path}"
        )

    output_dir = Path("/app/output") / input_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Carregando modelo de diarização...", flush=True)

    pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization-community-1",
        token=os.environ["HF_TOKEN"],
    )

    device = torch.device(
        "cuda" if torch.cuda.is_available() else "cpu"
    )

    print(f"Dispositivo: {device}", flush=True)

    pipeline.to(device)

    print("Iniciando identificação dos falantes...", flush=True)

    start_time = time.time()

    audio = load_audio(input_path)

    result = pipeline(audio)

    segments = []

    for turn, speaker in result.speaker_diarization:
        segments.append({
            "start": round(turn.start, 3),
            "end": round(turn.end, 3),
            "speaker": speaker,
        })

    output_path = output_dir / "speakers.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            segments,
            f,
            ensure_ascii=False,
            indent=2,
        )

    elapsed = time.time() - start_time

    print("\nDiarização concluída!")
    print(f"Intervalos identificados: {len(segments)}")
    print(f"Falantes identificados: {len(set(s['speaker'] for s in segments))}")
    print(f"Tempo de processamento: {elapsed:.1f}s")
    print(f"Resultado: {output_path}")


if __name__ == "__main__":
    main()

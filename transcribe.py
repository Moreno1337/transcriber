import argparse
import json
import time
from pathlib import Path

from faster_whisper import WhisperModel


def timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    input_path = Path("/app/input") / args.filename

    if not input_path.is_file():
        raise FileNotFoundError(f"Arquivo não encontrado: {input_path}")

    output_dir = Path("/app/output") / input_path.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Carregando Whisper large-v3 na GPU...", flush=True)

    model = WhisperModel(
        "large-v3",
        device="cuda",
        compute_type="float16",
        download_root="/app/models",
    )

    print("Iniciando transcrição...", flush=True)
    start_time = time.time()

    segments, info = model.transcribe(
        str(input_path),
        language="pt",
        beam_size=5,
        vad_filter=True,
        condition_on_previous_text=False,
    )

    txt_path = output_dir / "transcript.txt"
    jsonl_path = output_dir / "transcript.jsonl"

    count = 0

    with (
        txt_path.open("w", encoding="utf-8") as txt,
        jsonl_path.open("w", encoding="utf-8") as jsonl,
    ):
        for segment in segments:
            text = segment.text.strip()

            if not text:
                continue

            start = timestamp(segment.start)
            end = timestamp(segment.end)

            txt.write(f"[{start} - {end}] {text}\n")

            record = {
                "start": segment.start,
                "end": segment.end,
                "text": text,
                "language": "pt",
            }

            jsonl.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )

            count += 1
            print(f"[{start}] {text}", flush=True)

    elapsed = time.time() - start_time

    print("\nTranscrição concluída!")
    print(f"Segmentos: {count}")
    print(f"Tempo de processamento: {elapsed:.1f}s")
    print(f"Arquivos gerados em: {output_dir}")


if __name__ == "__main__":
    main()

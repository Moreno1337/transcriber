
import argparse
import json
from pathlib import Path


def timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{secs:02}"


def identify_speaker(start, end, speakers):
    # Escolhe o falante com maior sobreposição temporal.
    overlaps = {}

    for segment in speakers:
        overlap = max(
            0,
            min(end, segment["end"]) -
            max(start, segment["start"])
        )

        if overlap > 0:
            speaker = segment["speaker"]
            overlaps[speaker] = overlaps.get(speaker, 0) + overlap

    if not overlaps:
        return "UNKNOWN"

    return max(overlaps, key=overlaps.get)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    folder = Path("/app/output") / Path(args.filename).stem

    transcript_path = folder / "transcript.jsonl"
    speakers_path = folder / "speakers.json"

    with speakers_path.open(encoding="utf-8") as f:
        speakers = json.load(f)

    output = []

    with transcript_path.open(encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            segment = json.loads(line)

            segment["speaker"] = identify_speaker(
                segment["start"],
                segment["end"],
                speakers
            )

            output.append(segment)

    txt_path = folder / "transcript_diarized.txt"
    jsonl_path = folder / "transcript_diarized.jsonl"

    with (
        txt_path.open("w", encoding="utf-8") as txt,
        jsonl_path.open("w", encoding="utf-8") as jsonl
    ):
        for segment in output:
            start = timestamp(segment["start"])
            end = timestamp(segment["end"])

            txt.write(
                f"[{start} - {end}] "
                f"{segment['speaker']}: "
                f"{segment['text']}\n"
            )

            jsonl.write(
                json.dumps(segment, ensure_ascii=False) + "\n"
            )

    print("Integração concluída!")
    print(f"Segmentos processados: {len(output)}")
    print(f"Resultado: {txt_path}")


if __name__ == "__main__":
    main()

import csv
from pathlib import Path
import argparse
from faker import Faker


# List of biomedical terms to inject
BIOMEDICAL_TERMS = [
    "cocaine",
    "treatment",
    "doctor",
    "nurse",
    "patient",
    "hospital",
    "medicine",
]


def main():
    parser = argparse.ArgumentParser(
        description="Generate a fake CSV with biomedical notes and IDs."
    )
    parser.add_argument(
        "--num-rows",
        type=int,
        default=100,
        help="Number of rows to generate (default: 100)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Path to the output file",
        default="data/fake_biomedical_notes.csv",
    )
    args = parser.parse_args()
    num_rows = int(args.num_rows)
    # output must be valid csv file
    if not args.output.endswith(".csv"):
        raise ValueError("Output file must be a CSV file")
    output_fpath = Path(args.output)

    fake = Faker()
    words = fake.get_words_list()
    words.extend(BIOMEDICAL_TERMS)

    data = []
    for i in range(num_rows):
        # Generate a random biomedical note
        note = fake.paragraph(
            nb_sentences=6,
            variable_nb_sentences=True,
            ext_word_list=words,
        )
        data.append({"note_id": i + 1, "note": note})

    with open(output_fpath, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["note_id", "note"])
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Generated {num_rows} rows of fake data in {output_fpath}")


if __name__ == "__main__":
    main()

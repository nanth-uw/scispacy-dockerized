default:
    @just --list

generate-data:
    @uv run scripts/generate_fake_csv.py

run-client: 
    @uv run examples/client.py

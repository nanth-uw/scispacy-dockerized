import httpx
import pandas as pd
from rich import print

# This is a simple client to test the API
# runs with the defaults from the scripts/generate_fake_csv.py
# expects docker API to be running

def main():
    df = pd.read_csv("data/fake_biomedical_notes.csv", low_memory=False)
    # the API expects us to rename the fields to 'id' and 'note_text'
    df.rename(columns={"note_id": "text_id", "note": "text"}, inplace=True)
    # make a list of dicts
    data: list[dict[str, int | str]] = df.to_dict(orient="records")
    # the API expects us to have an initial field called "entries"
    request_data = {"entries": data}
    # use post method, localhost, port 8000, and the /ner endpoint, passing the data as json
    resp = httpx.post(
        "http://localhost:8000/ner",
        json=request_data,
    )
    # check if the response is ok
    assert resp.status_code == 200, f"Error: {resp.status_code} \n {resp.json()}"
    results = resp.json()
    # results has a top level field called "results"
    assert "results" in results, f"Error: {results}"
    # results["results"] is a list of dicts
    for result in results["results"]:
        print(result)

    # put the list of dicts into a pandas dataframe
    result_df = pd.DataFrame(results["results"])
    # save the result to a csv file
    result_df.to_csv("data/fake_biomedical_notes_results.csv", index=False)


if __name__ == '__main__':
    main()

from datetime import datetime
from typing import Annotated

import spacy
from fastapi import FastAPI
from pydantic import AfterValidator, BaseModel, Field
from scispacy.linking import EntityLinker
from spacy.language import Language

# these two have to stay for "scope" via spacy
# NOTE: do NOT let ruff remove these imports
from negspacy.negation import Negex # scope
from scispacy.abbreviation import AbbreviationDetector # scope


def build_models() -> tuple[Language, EntityLinker]:
    nlp = spacy.load(
        "en_core_sci_lg",
        # remove things not needed for NER, increases perf
        exclude=["tagger", "lemmatizer", "textcat"],
    )
    print("Loaded base model")
    nlp.add_pipe("negex")
    print("Added negex")
    nlp.add_pipe("abbreviation_detector", config={"make_serializable": True})
    print("Added abbreviation_detector")
    nlp.add_pipe(
        "scispacy_linker",
        config={
            # use abbreviations
            "resolve_abbreviations": True,
            # only give us the best corresponding entity
            "max_entities_per_mention": 1,
            # default is 30
            "k": 30,
            # default is 0.7
            "threshold": 0.9,
            # this is the big one! limits to only entities with definitions in knowledge base
            "filter_for_definitions": True,
            # use UMLS knowledge base
            "linker_name": "umls",
        },
    )
    print("Added umls linker")
    linker: EntityLinker = nlp.get_pipe("scispacy_linker")
    return nlp, linker


class TextData(BaseModel):
    text: str
    id: str | int


def _is_unique_ids(entries: list[TextData]) -> list[TextData]:
    entries_length = len(entries)
    unique_ids = len(list(set((x.id for x in entries))))
    if entries_length != unique_ids:
        raise ValueError(
            f"note ids were not unique, found: {unique_ids} unique_ids among {entries_length} notes"
        )
    return entries


class TextDataList(BaseModel):
    entries: Annotated[
        list[TextData], AfterValidator(_is_unique_ids), Field(max_length=100)
    ]


class NEROutput(BaseModel):
    id: str | int
    umls_cui: str
    umls_name: str
    matched_entity: str
    score: float
    negated: bool
    processed_at: datetime


class NEROutputList(BaseModel):
    results: list[NEROutput]


NER, LINKER = build_models()

app = FastAPI(
    responses={404: {"description": "Not found"}},
)


@app.post("/ner")
async def extract_ner(items: TextDataList) -> NEROutputList:
    output: list[NEROutput] = []
    timestamp = datetime.now()
    for entry in items.entries:
        doc = NER(entry.text)
        for ent in doc.ents:
            for kb_ent, score in ent._.kb_ents:
                concept = LINKER.kb.cui_to_entity[kb_ent]
                out = NEROutput(
                    id=entry.id,
                    umls_cui=concept.concept_id.strip(),
                    umls_name=concept.canonical_name.strip(),
                    matched_entity=ent.text.strip(),
                    score=score,
                    negated=ent._.negex,
                    processed_at=timestamp,
                )
                output.append(out)
    results = NEROutputList(results=output)
    return results

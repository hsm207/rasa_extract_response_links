import re
from typing import Any, Dict, ItemsView, List, Text, Tuple

import click
import pandas as pd
from rasa.core.nlg.response import TemplatedNaturalLanguageGenerator
from rasa.shared.core.domain import Domain

HAS_MARKDOWN_URL = "\[[\w\s]+\]\([^)]+\)"
MARKDOWN_URL = "\[([\w\s]+)\]\(([^)]+)\)"


BotResponseDetails = List[Dict[Text, Any]]


def has_text_field(response: BotResponseDetails) -> bool:
    return any("text" in d for d in response)


def has_hyperlink_in_text(response: BotResponseDetails) -> bool:
    text_field = next(d["text"] for d in response if "text" in d)
    return True if re.search(HAS_MARKDOWN_URL, text_field) else False


def extract_url(text: str) -> List[Tuple[str, str]]:
    return re.findall(MARKDOWN_URL, text)


def parse_bot_response(bot_response: Dict[Text, Any]) -> List[str]:
    results = []

    for response_name, response_details in bot_response.items():
        text_field = text_field = next(
            d["text"] for d in response_details if "text" in d
        )
        urls = extract_url(text_field)
        results.append(response_name)
        results.append(urls)

    return results


def make_report(results) -> pd.DataFrame:
    df1 = (
        pd.DataFrame(results, columns=["response_name", "details"])
        .explode("details")
        .reset_index(drop=True)
    )

    df2 = pd.DataFrame(df1["details"].tolist(), columns=["title", "link"]).reset_index(
        drop=True
    )

    return pd.concat([df1, df2], axis=1).drop("details", axis=1)


@click.command()
@click.option(
    "--domain",
    default=".",
    help="Path to a domain file or folder containing domain files",
)
@click.option(
    "--sep",
    default=",",
    help="Separator character for CSV files. Defaults to comma, but can be set to "";"" for German Excel",
)
@click.option(
    "--out", default="./extraction_results.csv", help="Path to save extraction results"
)
def main(domain: str, sep:str, out: str):
    """A script to extract hyperlinks from the responses in a domain file."""
    bot_responses = Domain.load(domain).responses

    bot_responses = [
        {response_name: response_details}
        for response_name, response_details in bot_responses.items()
        if has_text_field(response_details) and has_hyperlink_in_text(response_details)
    ]

    results = [parse_bot_response(br) for br in bot_responses]
    report = make_report(results)

    report.to_csv(out, index=False, sep=sep)


if __name__ == "__main__":
    main()

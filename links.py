from rasa.core.nlg.response import TemplatedNaturalLanguageGenerator
from rasa.shared.core.domain import Domain
import re
import pandas as pd
from typing import ItemsView, Text, List, Dict, Any, Tuple
import click


HAS_MARKDOWN_URL = "\[[\w\s]+\]\([^)]+\)"
MARKDOWN_URL = "\[([\w\s]+)\]\(([^)]+)\)"


def extract_links_from_item(item: Text) -> List[str]:
    print(item)
    # we want to regex match all instances of [title](link), e.g.
    # - text: "You can find more info on the [Domains](rasa.com/docs/rasa/domains) page."

    links = re.findall(r"some regex here", item)
    if links:
        print(links)
    print()
    return links


def extract_links(response: Dict[Text, Any]):
    """Recursively process response and interpolate any text keys.

    Args:
        response: The response that should be interpolated.
        values: A dictionary of keys and the values that those
            keys should be replaced with.

    Returns:
        The response with any replacements made.
    """
    links = []
    # from https://github.com/RasaHQ/rasa/blob/main/rasa/core/nlg/interpolator.py#L49
    # should probably be edited to return a list of links, instead of updating the responses in place
    if isinstance(response, str):
        return extract_links_from_item(response)
    elif isinstance(response, dict):
        for k, v in response.items():
            if isinstance(v, dict):
                extract_links(v)
            elif isinstance(v, list):
                response[k] = [extract_links(i) for i in v]
            elif isinstance(v, str):
                response[k] = extract_links_from_item(v)
        return response
    elif isinstance(response, list):
        return [extract_links(i) for i in response]
    return response


# domain = Domain.load("domain.yml")  # This should probably handle multi domain
# for response_name, response_content in domain.responses.items():
#     extract_links(response_content)

#  Output: a csv of links, their titles, and the response name they came from
#  (response_name, link_title, link)
#  pandas.to_csv

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
    df = pd.DataFrame(results, columns=["response_name", "details"]).explode("details")

    title, link = df["details"].str

    df["title"] = title
    df["link"] = link

    return df.drop("details", axis=1)


@click.command()
@click.option(
    "--domain",
    default=".",
    help="Path to a domain file or folder containing domain files",
)
@click.option(
    "--out", default="./extraction_results.csv", help="Path to save extraction results"
)
def main(domain: str, out: str):
    """A script to extract hyperlinks from the responses in a domain file."""
    bot_responses = Domain.load(domain).responses

    bot_responses = [
        {response_name: response_details}
        for response_name, response_details in bot_responses.items()
        if has_text_field(response_details) and has_hyperlink_in_text(response_details)
    ]

    results = [parse_bot_response(br) for br in bot_responses]
    report = make_report(results)

    report.to_csv(out, index=False)


if __name__ == "__main__":
    main()

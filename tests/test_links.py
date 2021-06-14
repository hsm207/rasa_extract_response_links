import pytest
import links


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        (
            [
                {
                    "text": "Use the [command line interface](https://rasa.com/docs/rasa/command-line-interface#rasa-train)"
                }
            ],
            True,
        ),
        ([{"image": "https://i.imgur.com/nGF1K8f.jpg"}], False),
    ],
)
def test_has_text_field(test_input, expected_output):
    actual_output = links.has_text_field(test_input)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        (
            [
                {
                    "text": "Use the [command line interface](https://rasa.com/docs/rasa/command-line-interface#rasa-train)"
                }
            ],
            True,
        ),
        (
            [
                {
                    "text": "Hey! How are you?",
                    "buttons": [
                        {"title": "great", "payload": "/mood_great"},
                        {"title": "super sad", "payload": "/mood_unhappy"},
                    ],
                }
            ],
            False,
        ),
        (
            [
                {
                    "text": "The intents key in your domain file lists all intents used in your [NLU data](https://rasa.com/docs/rasa/nlu-training-data) and [conversation training data](https://rasa.com/docs/rasa/training-data-format#conversation-training-data)."
                }
            ],
            True,
        ),
    ],
)
def test_has_hyperlink_in_text(test_input, expected_output):
    actual_output = links.has_hyperlink_in_text(test_input)
    assert actual_output == expected_output


@pytest.mark.parametrize(
    "test_input, expected_output",
    [
        (
            "Use the [command line interface](https://rasa.com/docs/rasa/command-line-interface#rasa-train)",
            [
                (
                    "command line interface",
                    "https://rasa.com/docs/rasa/command-line-interface#rasa-train",
                )
            ],
        ),
        (
            "The intents key in your domain file lists all intents used in your [NLU data](https://rasa.com/docs/rasa/nlu-training-data) and [conversation training data](https://rasa.com/docs/rasa/training-data-format#conversation-training-data).",
            [
                ("NLU data", "https://rasa.com/docs/rasa/nlu-training-data"),
                (
                    "conversation training data",
                    "https://rasa.com/docs/rasa/training-data-format#conversation-training-data",
                ),
            ],
        ),
    ],
)
def test_extract_url(test_input, expected_output):
    actual_output = links.extract_url(test_input)
    assert actual_output == expected_output

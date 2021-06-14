import pytest
import links


@pytest.mark.parametrize("test_input, expected_output", [
    ([{'text': 'Use the [command line interface](https://rasa.com/docs/rasa/command-line-interface#rasa-train)'}], True),
    ([{'image': 'https://i.imgur.com/nGF1K8f.jpg'}], False)
])
def test_has_text_field(test_input, expected_output):
    actual_output = links._has_text_field(test_input)
    assert actual_output == expected_output
    
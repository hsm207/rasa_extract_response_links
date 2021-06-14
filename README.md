# Introduction

`links.py` is a script to extract markdown links from a bot's utterance defined in the domain files.

# Usage

Read `python links.py --help`.

# Examples

## Single domain file

If you want to extract the links from the bot utterances of a specific domain file:

```bash
python links.py --domain ./tests/domain.yml --out extraction_results.csv
```

## Multiple domain files

If you want to extract the links from the bot utterances by recursively going through all the domain files in a specific folder:

```bash
python links.py --domain ./tests --out extraction_results.csv
```
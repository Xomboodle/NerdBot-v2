"""functions.py"""


def format_update(text: str) -> str:
    # Need to get the title of the update and set as a heading
    heading: str = text.split('\n')[0]
    subheading: str = text.split('\n-')[0].replace(heading + "\n", "")

    changelog: str = text.replace(heading, f"## {heading}")
    changelog = changelog.replace(subheading, f"_{subheading}_\n")

    return changelog

# google-location-history-tools

See [here](https://www.technowizardry.net/2024/01/migrating-from-google-location-history-to-owntracks/) for the background of this script.

# Installation

1. `git clone https://github.com/ajacques/google-location-history-tools.git`
2. `uv sync`

# Usage

For Google Takeout:

```shell
uv run main.py Records.json --takeout --tracker-id [two digit owntracks tracker id]
```

For Google Maps Mobile Export:

```shell
uv run main.py Timeline.json --gmaps --tracker-id [two digit owntracks tracker id]

``
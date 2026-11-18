import re

from version import __version__


def test_la_version_es_semver():
    # MAJOR.MINOR.PATCH con sufijo opcional de pre-release (-rc.1, -beta.2): el workflow de release
    # marca como pre-release las versiones con guion.
    assert re.fullmatch(r"\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?", __version__)

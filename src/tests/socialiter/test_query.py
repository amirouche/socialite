from pathlib import Path

from socialiter import query


def test_bing_parse():
    # prepare
    filepath = Path(__file__).parent / 'query-bing.html'
    with filepath.open('r') as f:
        string = f.read()
    # exec
    out = query._bing_parse(string)
    # check
    expected = [
        {
            'description': 'foobar2000 is an advanced freeware audio player for the Windows platform. Latest news',  # noqa
            'title': 'foobar2000',
            'url': 'http://www.foobar2000.org/'
        },
        {
            'description': 'Orthographe alternative : Foobar2000, ',
            'title': 'Télécharger Foobar2000 (gratuit)',
            'url': 'https://www.commentcamarche.net/download/telecharger-195-foobar2000'
        }
    ]
    assert out[:2] == expected

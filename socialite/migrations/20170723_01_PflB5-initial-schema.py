"""
Initial schema
"""
from pathlib import Path

from yoyo import step

# absolute import is required here since yoyo does load the file magically see
# https://bitbucket.org/ollyc/yoyo/issues/33/how-to-include-a-relative-file-as-a-step
from socialite import migrations


directory = (Path(migrations.__file__) / '..').resolve()


__depends__ = {}

steps = [
    step((directory / 'initial.sql').read_text())
]

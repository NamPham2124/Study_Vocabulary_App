"""VocabMaster CLI package entrypoint."""

import sys
from vocabmaster.cli.main import cli_entrypoint

if __name__ == "__main__":
    sys.exit(cli_entrypoint())

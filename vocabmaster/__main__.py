"""Top-level package execution for VocabMaster."""

import sys
import uvicorn
from vocabmaster.config import settings

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "cli":
        from vocabmaster.cli.main import cli_entrypoint
        sys.argv.pop(1)
        return cli_entrypoint()
    
    print(f"Starting VocabMaster web server on {settings.api_host}:{settings.api_port}...")
    uvicorn.run("vocabmaster.api.app:app", host=settings.api_host, port=settings.api_port, reload=False)

if __name__ == "__main__":
    main()

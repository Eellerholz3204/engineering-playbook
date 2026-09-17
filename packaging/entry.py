"""PyInstaller entry point, kept outside the package for absolute import resolution."""
from repository_builder.startup import run

if __name__ == "__main__":
    run()

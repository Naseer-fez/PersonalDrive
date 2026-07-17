import subprocess as CMD
import os
from pathlib import Path

try:
    from pckconfig import config
    from installdepen import PYTHON
    from packages import packages
except ImportError:
    from package.pckconfig import config
    from package.installdepen import PYTHON
    from package.packages import packages


DIR = config.get("workspace_path") or config.get("dir") or os.getcwd()
VENV_DIR = "env"


def pipcreation():
    try:
        _, path = PYTHON()

        CMD.run(
            [path, "-m", "venv", VENV_DIR],
            check=True
        )

        venv_python = os.path.join(VENV_DIR, "Scripts", "python.exe")

        # Ensure pip is up to date in the venv
        CMD.run(
            [venv_python, "-m", "ensurepip", "--upgrade"],
            check=True
        )

        requirements_path = Path(os.getcwd()) / "requirements.txt"
        if requirements_path.exists():
            CMD.run(
                [venv_python, "-m", "pip", "install", "-r", str(requirements_path)],
                check=True
            )
        else:
            CMD.run(
                [venv_python, "-m", "pip", "install", *packages],
                check=True
            )

        config.set("venv_python", venv_python)
        return True, venv_python

    except CMD.CalledProcessError:
        return False, None


def PIP():
    venv_python = config.get("venv_python")

    if venv_python and Path(venv_python).exists():
        return venv_python

    success, venv_python = pipcreation()

    if success:
        return venv_python

    return None
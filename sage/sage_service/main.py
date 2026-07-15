import os
import random
from pathlib import Path

from fastapi import FastAPI

from .patch_status import get_patch_status

FORTUNES = [
    "Geeko sent un grand changement arriver.",
    "Aujourd'hui, Geeko se sent d'humeur zen.",
    "Attention, Geeko a mangé une mouche suspecte.",
    "Le vert te va si bien, Geeko.",
    "Geeko recommande une pause café.",
]

_UNPATCHED_SEED = 42  # deliberately fixed: the "vulnerability" is a predictable RNG


def create_app(flag_path: Path) -> FastAPI:
    app = FastAPI(title="geeko-sage")

    @app.get("/healthz")
    def healthz():
        return get_patch_status(flag_path)

    @app.get("/fortune")
    def fortune():
        status = get_patch_status(flag_path)
        rng = random.Random() if status["patched"] else random.Random(_UNPATCHED_SEED)
        return {"message": rng.choice(FORTUNES), **status}

    return app


app = create_app(flag_path=Path(os.environ.get("GEEKO_SAGE_FLAG_PATH", "/etc/geeko-sage/patched")))

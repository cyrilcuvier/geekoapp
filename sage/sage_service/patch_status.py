from pathlib import Path


def get_patch_status(flag_path: Path) -> dict:
    return {"patched": flag_path.exists()}

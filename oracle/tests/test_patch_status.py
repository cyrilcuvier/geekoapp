from oracle_service.patch_status import get_patch_status


def test_reports_unpatched_when_flag_file_absent(tmp_path):
    flag_path = tmp_path / "patched"
    assert get_patch_status(flag_path) == {"patched": False}


def test_reports_patched_when_flag_file_present(tmp_path):
    flag_path = tmp_path / "patched"
    flag_path.write_text("patched by MLM\n")
    assert get_patch_status(flag_path) == {"patched": True}

"""
Unit test for create_perturbed_xml 
"""

import sys
import types
import pytest
from pathlib import Path


class MockIncidentNeutron:
    def __init__(self, called_paths):
        self.called_paths = called_paths
        self.exported_hdf5 = []

    @staticmethod
    def from_ace(path):
        raise NotImplementedError  # replaced dynamically

    def export_to_hdf5(self, filename):
        self.exported_hdf5.append(filename)


class MockLibrary:
    def __init__(self):
        self.registered = []
        self.exported_xml = []

    def register_file(self, filename):
        self.registered.append(filename)

    def export_to_xml(self, filename):
        self.exported_xml.append(filename)


@pytest.fixture
def mock_environment(monkeypatch):

    # -----------------------------
    # Create a fake openmc module
    # -----------------------------
    called_paths = []
    incident = MockIncidentNeutron(called_paths)

    def fake_from_ace(path):
        called_paths.append(Path(path))
        return incident

    # Replace the staticmethod
    incident.from_ace = staticmethod(fake_from_ace)

    fake_openmc = types.ModuleType("openmc")
    fake_openmc.data = types.SimpleNamespace(
        IncidentNeutron=incident
    )

    # Insert fake module into sys.modules
    sys.modules["openmc"] = fake_openmc

    # -----------------------------
    # Fake filesystem
    # -----------------------------
    cwd_log = ["/starting"]

    monkeypatch.setattr("os.getcwd", lambda: cwd_log[0])
    monkeypatch.setattr("os.chdir", lambda p: cwd_log.append(p))
    monkeypatch.setattr("os.listdir", lambda p: ["xsdir", "perturbed.ace"])
    monkeypatch.setattr("os.path.exists", lambda p: False)
    monkeypatch.setattr("os.remove", lambda p: None)

    # -----------------------------
    # Fake deepcopy
    # -----------------------------
    libs = []

    def fake_deepcopy(obj):
        lib = MockLibrary()
        libs.append(lib)
        return lib

    monkeypatch.setattr("copy.deepcopy", fake_deepcopy)

    return {
        "cwd_log": cwd_log,
        "libs": libs,
        "incident": incident,
        "called_paths": called_paths,
    }


def test_create_perturbed_xml_basic(mock_environment):
    # Import AFTER fake openmc is injected
    from src.WINDIGO.openmc_internal_functions import create_perturbed_xml

    env = mock_environment

    unperturbed_library = MockLibrary()
    perturbed_ACE_folder_path = "/ace"
    four_digit_numbers = ["0001", "0002"]
    perturbed_model_folder_list = ["/model1", "/model2"]

    create_perturbed_xml(
        unperturbed_library,
        perturbed_ACE_folder_path,
        four_digit_numbers,
        perturbed_model_folder_list,
    )

    # Correct ACE paths
    assert env["called_paths"] == [
        Path("/ace/0001/perturbed.ace"),
        Path("/ace/0002/perturbed.ace"),
    ]

    # Two deep-copied libraries
    libs = env["libs"]
    assert len(libs) == 2

    # Each library registers its own .h5 file
    assert libs[0].registered == ["/ace/0001/perturbed.ace.h5"]
    assert libs[1].registered == ["/ace/0002/perturbed.ace.h5"]

    # Each library exports cross_sections.xml
    assert libs[0].exported_xml == ["cross_sections.xml"]
    assert libs[1].exported_xml == ["cross_sections.xml"]

    # Directory navigation
    assert env["cwd_log"] == [
        "/starting",
        "/model1",
        "/starting",
        "/model2",
        "/starting",
    ]

def test_create_perturbed_xml_picks_last_valid_file(monkeypatch):
    """
    The function should select the LAST file in the directory that does not
    contain 'xsdir' or 'h5', even if the file is not a real ACE file.
    """

    # --- Fake openmc module ---
    import sys, types
    called_paths = []
    incident = MockIncidentNeutron(called_paths)

    def fake_from_ace(path):
        called_paths.append(Path(path))
        return incident

    incident.from_ace = staticmethod(fake_from_ace)

    fake_openmc = types.ModuleType("openmc")
    fake_openmc.data = types.SimpleNamespace(IncidentNeutron=incident)
    sys.modules["openmc"] = fake_openmc

    # --- Fake filesystem ---
    cwd_log = ["/start"]
    monkeypatch.setattr("os.getcwd", lambda: cwd_log[0])
    monkeypatch.setattr("os.chdir", lambda p: cwd_log.append(p))

    # Multiple files, only last one should be chosen
    monkeypatch.setattr(
        "os.listdir",
        lambda p: ["xsdir", "junk.tmp", "not_really_ace", "perturbed.ace"]
    )

    monkeypatch.setattr("os.path.exists", lambda p: False)
    monkeypatch.setattr("os.remove", lambda p: None)

    # Fake deepcopy
    libs = []
    def fake_deepcopy(obj):
        lib = MockLibrary()
        libs.append(lib)
        return lib

    monkeypatch.setattr("copy.deepcopy", fake_deepcopy)

    # --- Run function ---
    from src.WINDIGO.openmc_internal_functions import create_perturbed_xml

    unperturbed_library = MockLibrary()
    create_perturbed_xml(
        unperturbed_library,
        perturbed_ACE_folder_path="/ace",
        four_digit_numbers=["0001"],
        perturbed_model_folder_list=["/model1"],
    )

    # Should pick the LAST valid file: "perturbed.ace"
    assert called_paths == [Path("/ace/0001/perturbed.ace")]

    # Library created and used
    assert len(libs) == 1
    assert libs[0].registered == ["/ace/0001/perturbed.ace.h5"]
    assert libs[0].exported_xml == ["cross_sections.xml"]

    # Directory navigation correct
    assert cwd_log == ["/start", "/model1", "/start"]

def test_create_perturbed_xml_overwrite_h5(monkeypatch):
    """
    If an .h5 file already exists, it should be removed before writing a new one.
    """

    # --- Fake openmc module ---
    import sys, types
    called_paths = []
    incident = MockIncidentNeutron(called_paths)

    def fake_from_ace(path):
        called_paths.append(Path(path))
        return incident

    incident.from_ace = staticmethod(fake_from_ace)

    fake_openmc = types.ModuleType("openmc")
    fake_openmc.data = types.SimpleNamespace(IncidentNeutron=incident)
    sys.modules["openmc"] = fake_openmc

    # --- Fake filesystem ---
    cwd_log = ["/start"]
    monkeypatch.setattr("os.getcwd", lambda: cwd_log[0])
    monkeypatch.setattr("os.chdir", lambda p: cwd_log.append(p))

    monkeypatch.setattr("os.listdir", lambda p: ["perturbed.ace"])

    # Pretend .h5 already exists
    monkeypatch.setattr("os.path.exists", lambda p: True)

    removed_files = []
    monkeypatch.setattr("os.remove", lambda p: removed_files.append(p))

    # Fake deepcopy
    libs = []
    def fake_deepcopy(obj):
        lib = MockLibrary()
        libs.append(lib)
        return lib

    monkeypatch.setattr("copy.deepcopy", fake_deepcopy)

    # --- Run function ---
    from src.WINDIGO.openmc_internal_functions import create_perturbed_xml

    unperturbed_library = MockLibrary()
    create_perturbed_xml(
        unperturbed_library,
        perturbed_ACE_folder_path="/ace",
        four_digit_numbers=["0001"],
        perturbed_model_folder_list=["/model1"],
    )

    # Correct ACE path
    assert called_paths == [Path("/ace/0001/perturbed.ace")]

    # Existing .h5 file was removed
    assert removed_files == ["/ace/0001/perturbed.ace.h5"]

    # New library created
    assert len(libs) == 1

    # New .h5 file registered
    assert libs[0].registered == ["/ace/0001/perturbed.ace.h5"]

    # XML exported
    assert libs[0].exported_xml == ["cross_sections.xml"]

def test_create_perturbed_xml_multiple_models(monkeypatch):
    """
    Ensure the function correctly loops over multiple model folders.
    """

    # --- Fake openmc module ---
    import sys, types
    called_paths = []
    incident = MockIncidentNeutron(called_paths)

    def fake_from_ace(path):
        called_paths.append(Path(path))
        return incident

    incident.from_ace = staticmethod(fake_from_ace)

    fake_openmc = types.ModuleType("openmc")
    fake_openmc.data = types.SimpleNamespace(IncidentNeutron=incident)
    sys.modules["openmc"] = fake_openmc

    # --- Fake filesystem ---
    cwd_log = ["/start"]
    monkeypatch.setattr("os.getcwd", lambda: cwd_log[0])
    monkeypatch.setattr("os.chdir", lambda p: cwd_log.append(p))

    monkeypatch.setattr("os.listdir", lambda p: ["perturbed.ace"])
    monkeypatch.setattr("os.path.exists", lambda p: False)
    monkeypatch.setattr("os.remove", lambda p: None)

    # Fake deepcopy
    libs = []
    def fake_deepcopy(obj):
        lib = MockLibrary()
        libs.append(lib)
        return lib

    monkeypatch.setattr("copy.deepcopy", fake_deepcopy)

    # --- Run function ---
    from src.WINDIGO.openmc_internal_functions import create_perturbed_xml

    unperturbed_library = MockLibrary()
    create_perturbed_xml(
        unperturbed_library,
        perturbed_ACE_folder_path="/ace",
        four_digit_numbers=["0001", "0002", "0003"],
        perturbed_model_folder_list=["/m1", "/m2", "/m3"],
    )

    # Correct ACE paths for each model
    assert called_paths == [
        Path("/ace/0001/perturbed.ace"),
        Path("/ace/0002/perturbed.ace"),
        Path("/ace/0003/perturbed.ace"),
    ]

    # Three deep-copied libraries
    assert len(libs) == 3

    # Each library registers its own .h5 file
    assert libs[0].registered == ["/ace/0001/perturbed.ace.h5"]
    assert libs[1].registered == ["/ace/0002/perturbed.ace.h5"]
    assert libs[2].registered == ["/ace/0003/perturbed.ace.h5"]

    # Each library exports XML
    assert libs[0].exported_xml == ["cross_sections.xml"]
    assert libs[1].exported_xml == ["cross_sections.xml"]
    assert libs[2].exported_xml == ["cross_sections.xml"]

    # Directory navigation: start → m1 → start → m2 → start → m3 → start
    assert cwd_log == [
        "/start",
        "/m1",
        "/start",
        "/m2",
        "/start",
        "/m3",
        "/start",
    ]
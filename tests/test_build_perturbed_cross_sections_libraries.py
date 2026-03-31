"""
Unit tests for build_perturbed_cross_sections_libraries.
All helper functions are mocked to verify orchestration logic.
"""

import pytest


def test_build_perturbed_cross_sections_libraries_happy_path(monkeypatch):
    'Test that all helper functions are called with correct arguments'
    module = "src.WENDIGO.openmc_internal_functions"

    calls = {}

    def fake_count_directories(perturbed_ACE_folder_path):
        calls["count"] = perturbed_ACE_folder_path
        return 3

    def fake_create_numbers(directory_number):
        calls["numbers"] = directory_number
        return ["0001", "0002", "0003"]

    def fake_create_unperturbed_library(**kwargs):
        calls["unperturbed"] = kwargs
        return "LIB"

    def fake_create_model_folders(**kwargs):
        calls["folders"] = kwargs
        return ("TOP_DIR", ["m1", "m2", "m3"])

    def fake_create_perturbed_xml(**kwargs):
        calls["xml"] = kwargs

    monkeypatch.setattr(f"{module}.count_directories", fake_count_directories)
    monkeypatch.setattr(f"{module}.create_numbers", fake_create_numbers)
    monkeypatch.setattr(f"{module}.create_unperturbed_library", fake_create_unperturbed_library)
    monkeypatch.setattr(f"{module}.create_model_folders", fake_create_model_folders)
    monkeypatch.setattr(f"{module}.create_perturbed_xml", fake_create_perturbed_xml)

    from src.WENDIGO.openmc_main_functions import build_perturbed_cross_sections_libraries

    result = build_perturbed_cross_sections_libraries(
        unperturbed_nuclide_list=["U235"],
        neutron_sublibrary_path="/neut",
        unperturbed_TSL_list=["c_H_in_H2O"],
        thermal_scatter_sublibrary_path="/tsl",
        perturbed_ACE_folder_path="/ace",
        perturbed_nuclide="U235",
        model_name="TestModel",
        perturbation_type="random"
    )

    assert result == "TOP_DIR"

    assert calls["count"] == "/ace"
    assert calls["numbers"] == 3

    assert calls["unperturbed"] == {
        "neutron_sublibrary_path": "/neut",
        "unperturbed_nuclide_list": ["U235"],
        "unperturbed_TSL_list": ["c_H_in_H2O"],
        "thermal_scatter_sublibrary_path": "/tsl",
    }

    assert calls["folders"] == {
        "directory_number": 3,
        "perturbed_nuclide": "U235",
        "model_name": "TestModel",
        "perturbation_type": "random",
    }

    assert calls["xml"] == {
        "unperturbed_library": "LIB",
        "perturbed_ACE_folder_path": "/ace",
        "four_digit_numbers": ["0001", "0002", "0003"],
        "perturbed_model_folder_list": ["m1", "m2", "m3"],
    }


def test_build_perturbed_cross_sections_libraries_defaults(monkeypatch):
    'Test behavior when optional parameters are omitted'
    module = "src.WENDIGO.openmc_internal_functions"

    monkeypatch.setattr(f"{module}.count_directories", lambda perturbed_ACE_folder_path: 1)
    monkeypatch.setattr(f"{module}.create_numbers", lambda directory_number: ["0001"])
    monkeypatch.setattr(f"{module}.create_unperturbed_library", lambda **kwargs: "LIB")
    monkeypatch.setattr(f"{module}.create_model_folders",
                        lambda **kwargs: ("TOP", ["m1"]))

    xml_args = {}
    monkeypatch.setattr(f"{module}.create_perturbed_xml",
                        lambda **kwargs: xml_args.update(kwargs))

    from src.WENDIGO.openmc_main_functions import build_perturbed_cross_sections_libraries

    result = build_perturbed_cross_sections_libraries(
        unperturbed_nuclide_list=["U238"],
        neutron_sublibrary_path="/neut",
        unperturbed_TSL_list=[],
        thermal_scatter_sublibrary_path="/tsl",
        perturbed_ACE_folder_path="/ace"
    )

    assert result == "TOP"
    assert xml_args["four_digit_numbers"] == ["0001"]
    assert xml_args["perturbed_ACE_folder_path"] == "/ace"


def test_build_perturbed_cross_sections_libraries_call_order(monkeypatch):
    'Test that helper functions are called in the correct order'
    module = "src.WENDIGO.openmc_internal_functions"

    call_order = []

    def wrap(name):
        def inner(*args, **kwargs):
            call_order.append(name)
            if name == "count":
                return 2
            if name == "numbers":
                return ["0001", "0002"]
            if name == "unperturbed":
                return "LIB"
            if name == "folders":
                return ("TOP", ["m1", "m2"])
        return inner

    monkeypatch.setattr(f"{module}.count_directories", wrap("count"))
    monkeypatch.setattr(f"{module}.create_numbers", wrap("numbers"))
    monkeypatch.setattr(f"{module}.create_unperturbed_library", wrap("unperturbed"))
    monkeypatch.setattr(f"{module}.create_model_folders", wrap("folders"))
    monkeypatch.setattr(f"{module}.create_perturbed_xml", wrap("xml"))

    from src.WENDIGO.openmc_main_functions import build_perturbed_cross_sections_libraries

    build_perturbed_cross_sections_libraries(
        ["U235"], "/neut", [], "/tsl", "/ace"
    )

    assert call_order == [
        "count",
        "numbers",
        "unperturbed",
        "folders",
        "xml",
    ]
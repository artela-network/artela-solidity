#!/usr/bin/env python3

# ------------------------------------------------------------------------------
# This file is part of solidity.
#
# solidity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# solidity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with solidity.  If not, see <http://www.gnu.org/licenses/>
#
# (c) 2023 solidity contributors.
# ------------------------------------------------------------------------------

import os
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

import subprocess
from shutil import which, copyfile, copytree, rmtree
from argparse import ArgumentParser

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import re
from abc import ABCMeta, abstractmethod

# Our scripts/ is not a proper Python package so we need to modify PYTHONPATH to import from it
# pragma pylint: disable=import-error,wrong-import-position
SCRIPTS_DIR = Path(__file__).parents[3] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from common.git_helpers import git, git_commit_hash
from common.shell_command import run_cmd

SOLC_FULL_VERSION_REGEX = re.compile(r"^[a-zA-Z: ]*(.*)$")
SOLC_SHORT_VERSION_REGEX = re.compile(r"^([0-9.]+).*\+|\-$")

CURRENT_EVM_VERSION: str = "london"
AVAILABLE_PRESETS: Tuple[str] = (
    "legacy-no-optimize",
    "ir-no-optimize",
    "legacy-optimize-evm-only",
    "ir-optimize-evm-only",
    "legacy-optimize-evm+yul",
    "ir-optimize-evm+yul",
)


@dataclass
class SolcConfig:
    binary_type: str
    binary_path: str
    branch: Optional[str] = field(default="master")
    install_dir: Optional[str] = field(default="solc")
    solcjs_src_dir: Optional[str] = field(default="")


@dataclass
class TestConfig:
    repo_url: str
    ref_type: str
    ref: str
    config_file: Optional[str]
    config_var: Optional[str]
    build_dependency: Optional[str] = field(default="nodejs")
    compile_only_presets: Optional[List[str]] = field(default_factory=list)
    settings_presets: Optional[List[str]] = field(default_factory=list)
    evm_version: Optional[str] = field(default=CURRENT_EVM_VERSION)
    solc: Dict[str, SolcConfig] = field(default_factory=lambda: defaultdict(SolcConfig))

    def __post_init__(self):
        if isinstance(self.solc, dict):
            self.solc = SolcConfig(**self.solc)

    def selected_presets(self):
        return self.compile_only_presets + self.settings_presets


class TestRunner(metaclass=ABCMeta):
    @staticmethod
    def on_local_test_dir(fn):
        """Run function inside the test directory"""

        def f(self, *args, **kwargs):
            if self.test_dir:
                os.chdir(self.test_dir)
            else:
                raise RuntimeError("Test directory not defined")
            return fn(self, *args, **kwargs)

        return f

    @abstractmethod
    def setup_environment(self, test_dir: Path):
        pass

    @abstractmethod
    def clean(self):
        pass

    @abstractmethod
    def compiler_settings(
        self, solc_version: str, presets: Tuple[str] = AVAILABLE_PRESETS
    ):
        pass

    @abstractmethod
    def compile(self, solc_version: str, preset: str):
        pass

    @abstractmethod
    def run_test(self, preset: str):
        pass


# Helper functions
def compiler_settings(
    evm_version, via_ir="false", optimizer="false", yul="false"
) -> Dict:
    return {
        "optimizer": {"enabled": optimizer, "details": {"yul": yul}},
        "evmVersion": evm_version,
        "viaIR": via_ir,
    }


def settings_from_preset(preset, evm_version) -> Dict:
    if preset not in AVAILABLE_PRESETS:
        raise RuntimeError(
            f"Preset \"{preset}\" not found. Please select one or more of the available presets:\n{' '.join(map(str, AVAILABLE_PRESETS))}"
        )
    switch = {
        "legacy-no-optimize": compiler_settings(evm_version),
        "ir-no-optimize": compiler_settings(evm_version, via_ir="true"),
        "legacy-optimize-evm-only": compiler_settings(evm_version, optimizer="true"),
        "ir-optimize-evm-only": compiler_settings(
            evm_version, via_ir="true", optimizer="true"
        ),
        "legacy-optimize-evm+yul": compiler_settings(
            evm_version, optimizer="true", yul="true"
        ),
        "ir-optimize-evm+yul": compiler_settings(
            evm_version, via_ir="true", optimizer="true", yul="true"
        ),
    }
    return switch.get(preset)


def parse_command_line(description: str, args: str):
    arg_parser = ArgumentParser(description)
    arg_parser.add_argument(
        "--solc-binary-type",
        required=True,
        type=str,
        help="""Solidity compiler binary type""",
        choices=["native", "solcjs"],
    )
    arg_parser.add_argument(
        "--solc-binary-path",
        required=True,
        type=str,
        help="""Path to solc or soljson.js binary""",
    )
    return arg_parser.parse_args(args)


def download_project(
    test_dir: Path, repo_url: str, ref_type: str = "branch", ref: str = "master"
):
    if ref_type not in ("commit", "branch", "tag"):
        raise RuntimeError(f"Invalid reference type: {ref_type}")

    print(f"Cloning {ref_type} {ref} of {repo_url}...")
    if ref_type == "commit":
        os.mkdir(test_dir)
        os.chdir(test_dir)
        git("init")
        git(f"remote add origin {repo_url}")
        git(f"fetch --depth 1 origin {ref}")
        git("reset --hard FETCH_HEAD")
    else:
        os.chdir(test_dir.parent)
        git(f"clone --depth 1 {repo_url} -b {ref} {test_dir.resolve()}")
        if not test_dir.exists():
            raise RuntimeError("Git clone failed.")
        os.chdir(test_dir)

    if (test_dir / ".gitmodules").exists():
        git("submodule update --init")

    print(f"Current commit hash: {git_commit_hash()}")


def parse_solc_version(solc_version_string):
    solc_version_match = re.search(SOLC_FULL_VERSION_REGEX, solc_version_string)
    if solc_version_match:
        solc_full_version = solc_version_match.group(1)
    else:
        raise RuntimeError(f"Solc version could not be found in: {solc_version_string}")
    return solc_full_version


def get_solc_short_version(solc_full_version):
    solc_short_version_match = re.search(SOLC_SHORT_VERSION_REGEX, solc_full_version)
    if solc_short_version_match:
        solc_short_version = solc_short_version_match.group(1)
    else:
        raise RuntimeError(
            f"Error extracting short version string from: {solc_full_version}"
        )
    return solc_short_version


def setup_solc(config: TestConfig, test_dir: Path) -> (str, str):
    sc_config = config.solc

    if sc_config.binary_type == "solcjs":
        # FIXME: install_dir is assumed to be relative path
        solc_dir = test_dir.parent / sc_config.install_dir
        solc_bin = solc_dir / "dist/solc.js"

        print("Setting up solc-js...")
        if sc_config.solcjs_src_dir == "":
            download_project(
                solc_dir,
                "https://github.com/ethereum/solc-js.git",
                "branch",
                sc_config.branch,
            )
        else:
            print(f"Using local solc-js from {sc_config.solcjs_src_dir}...")
            copytree(sc_config.solcjs_src_dir, solc_dir)
            rmtree(solc_dir / "dist")
            rmtree(solc_dir / "node_modules")
        os.chdir(solc_dir)
        run_cmd("npm install")
        run_cmd("npm run build")
        copyfile(sc_config.binary_path, solc_dir / "dist/soljson.js")
        solc_version_output = subprocess.getoutput(f"node {solc_bin} --version")
    else:
        print("Setting up solc...")
        solc_version_output = subprocess.getoutput(
            f"{sc_config.binary_path} --version"
        ).split(":")[1]

    return parse_solc_version(solc_version_output)


def store_benchmark_report(self):
    # TODO
    raise NotImplementedError()


def prepare_node_env(test_dir: Path):
    if which("node") is None:
        raise RuntimeError("nodejs not found")
    # Remove lock files (if they exist) to prevent them from overriding our changes in package.json
    print("Removing package lock files...")
    rmtree(test_dir / "yarn.lock")
    rmtree(test_dir / "package_lock.json")
    # TODO: neutralize_package_json_hooks
    print("Disabling package.json hooks...")
    if not (test_dir / "package.json").exists():
        raise RuntimeError("package.json not found")
    # TODO: replace prepublish and prepare


def run_test(config, name: str, runner: TestRunner):
    if config.solc.binary_type not in ("native", "solcjs"):
        raise RuntimeError(
            f"Invalid solidity compiler binary type: {config.solc.binary_type}"
        )
    if config.solc.binary_type != "solcjs" and config.solc.solcjs_src_dir != "":
        raise RuntimeError(
            f"""Invalid test configuration: 'native' mode cannot be used with 'solcjs_src_dir'.
            Please use 'binary_type: solcjs' or unset: 'solcjs_src_dir: {config.solc.solcjs_src_dir}'"""
        )
    print(f"Testing {name}...\n===========================")
    with TemporaryDirectory(prefix=f"ext-test-{name}-") as tmp_dir:
        test_dir = Path(tmp_dir) / "ext"
        presets = config.selected_presets()
        print(f"Selected settings presets: {' '.join(map(str, presets))}")

        # Configure solc compiler
        solc_version = setup_solc(config, test_dir)
        print(f"Using compiler version {solc_version}")

        # Download project
        download_project(test_dir, config.repo_url, config.ref_type, config.ref)

        # Configure run environment
        if config.build_dependency == "nodejs":
            prepare_node_env(test_dir)
        runner.setup_environment(test_dir)

        # Configure TestRunner instance
        # TODO: replace_version_pragmas
        runner.compiler_settings(solc_version, presets)
        for preset in config.selected_presets():
            print("Running compile function...")
            runner.compile(solc_version, preset)
            # TODO: skip tests if compile_only_presets
            print("Running test function...")
            runner.run_test(preset)
            # TODO: store_benchmark_report
            # runner.clean()
        print("Done.")

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
import re
import subprocess
from pathlib import Path
from shutil import which
from string import Template
from typing import Tuple
from textwrap import dedent

from exttest.common import AVAILABLE_PRESETS
from exttest.common import settings_from_preset, get_solc_short_version
from exttest.common import TestConfig, TestRunner


def run_forge_command(command: str, env: dict = None):
    subprocess.run(
        command.split(),
        env=env if env is not None else os.environ.copy(),
        check=True
    )


class FoundryRunner(TestRunner):
    """Configure and run Foundry-based projects"""

    profile_tmpl = Template(
        """
        [profile.${name}]
        gas_reports = [\"*\"]
        auto_detect_solc = false
        solc = \"${solc}\"
        evm_version = \"${evm_version}\"
        optimizer = ${optimizer}
        via_ir = ${via_ir}

        [profile.${name}.optimizer_details]
        yul = ${yul}
    """
    )
    foundry_config_file = "foundry.toml"

    def __init__(
        self, config: TestConfig, setup_fn=None, compile_fn=None, test_fn=None
    ):
        self.config = config
        self.setup_fn = setup_fn
        self.compile_fn = compile_fn
        self.test_fn = test_fn
        self.env = os.environ.copy()
        # Note: the test_dir will be set on setup_environment
        self.test_dir: Path = None

    def setup_environment(self, test_dir: Path):
        """Configure the project build environment"""

        print("Configuring Foundry building environment...")
        self.test_dir = test_dir
        if which("forge") is None:
            raise RuntimeError("Forge not found.")
        if self.setup_fn:
            self.setup_fn(self.test_dir, self.env)

    @staticmethod
    def profile_name(preset: str):
        """Returns foundry profile name"""
        # Replace - or + by underscore to avoid invalid toml syntax
        return re.sub(r"(\-|\+)+", "_", preset)

    @TestRunner.on_local_test_dir
    def clean(self):
        """Clean the build artifacts and cache directories"""
        run_forge_command("forge clean")

    @TestRunner.on_local_test_dir
    def compiler_settings(
        self, solc_version: str, presets: Tuple[str] = AVAILABLE_PRESETS
    ):
        """Configure forge tests profiles"""

        binary_type = self.config.solc.binary_type
        binary_path = self.config.solc.binary_path
        print(
            dedent(
                f"""
            Configuring Forge profiles...
            -------------------------------------
            Config file: {self.foundry_config_file}
            Binary type: {binary_type}
            Compiler path: {binary_path}
            -------------------------------------
        """
            )
        )

        # TODO: Add support to solcjs. Currently only native solc is supported. # pylint: disable=fixme
        if binary_type == "solcjs":
            raise NotImplementedError(
                "Solcjs binaries are currently not supported with Foundry. Please use `native` binary_type."
            )

        profiles = []
        for preset in presets:
            name = self.profile_name(preset)
            settings = settings_from_preset(preset, self.config.evm_version)
            profiles.append(
                self.profile_tmpl.substitute(
                    name=name,
                    solc=binary_path,
                    evm_version=self.config.evm_version,
                    optimizer=settings["optimizer"]["enabled"],
                    via_ir=settings["viaIR"],
                    yul=settings["optimizer"]["details"]["yul"],
                )
            )

        with open(
            file=Path(self.test_dir) / self.foundry_config_file,
            mode="a",
            encoding="utf-8",
        ) as f:
            for profile in profiles:
                f.write(profile)

        run_forge_command("forge install", self.env)

    @TestRunner.on_local_test_dir
    def compile(self, solc_version: str, preset: str):
        """Compile project"""

        solc_short_version = get_solc_short_version(solc_version)
        settings = settings_from_preset(preset, self.config.evm_version)
        print(
            dedent(
                f"""
            Using Forge profile...
            -------------------------------------
            Settings preset: {preset}
            Settings: {settings}
            EVM version: {self.config.evm_version}
            Compiler version: {solc_short_version}
            Compiler version (full): {solc_version}
            -------------------------------------
        """
            )
        )
        name = self.profile_name(preset)
        # Set the Foundry profile environment variable
        self.env.update({"FOUNDRY_PROFILE": name})

        if self.compile_fn is not None:
            self.compile_fn(self.test_dir, self.env)
        else:
            run_forge_command("forge build", self.env)

    @TestRunner.on_local_test_dir
    def run_test(self, preset: str):
        """Run project tests"""

        if self.test_fn is not None:
            self.test_fn(self.test_dir, self.env)
        else:
            run_forge_command("forge test --gas-report", self.env)

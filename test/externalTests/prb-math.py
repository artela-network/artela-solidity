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

import sys
import subprocess
import json

from exttest.common import CURRENT_EVM_VERSION
from exttest.common import parse_command_line, run_test
from exttest.common import TestConfig

from runners.foundry import FoundryRunner

if __name__ == "__main__":
    try:
        # Note: We currently accept solc_binary_type and solc_binary_path as parameters
        # to keep compatibility with the current external tests framework.
        args = parse_command_line("PRBMath external tests", sys.argv[1:])

        config_json = json.loads(
            f"""
        {{
            "repo_url": "https://github.com/PaulRBerg/prb-math.git",
            "ref_type": "branch",
            "ref": "main",
            "config_file": "foundry.toml",
            "config_var": "config",
            "build_dependency": "rust",
            "compile_only_presets": [],
            "settings_presets": [
                "ir-optimize-evm+yul",
                "legacy-optimize-evm-only",
                "legacy-optimize-evm+yul",
                "legacy-no-optimize"
            ],
            "evm_version": "{CURRENT_EVM_VERSION}",
            "solc": {{
                "binary_type": "{args.solc_binary_type}",
                "binary_path": "{args.solc_binary_path}",
                "branch": "master",
                "install_dir": "solc/"
            }}
        }}"""
        )

        config = TestConfig(**config_json)
        run_test(
            config,
            "PRBMath",
            FoundryRunner(
                config=config,
                setup_fn=None,
                compile_fn=None,
                test_fn=None,
            ),
        )
    except (
        OSError,
        SystemError,
        RuntimeError,
        subprocess.CalledProcessError,
    ) as exception:
        print(f"Error while processing test: {exception}", file=sys.stderr)
        sys.exit(1)

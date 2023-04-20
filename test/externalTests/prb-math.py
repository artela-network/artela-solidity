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

from exttest.common import CURRENT_EVM_VERSION, InvalidConfigError
from exttest.common import parse_command_line, run_test
from exttest.common import TestConfig

from runners.foundry import FoundryRunner

if __name__ == "__main__":
    try:
        args = parse_command_line("PRBMath external tests", sys.argv[1:])

        runner_config = TestConfig(
            **{
                "repo_url": "https://github.com/PaulRBerg/prb-math.git",
                "ref_type": "branch",
                "ref": "main",
                "build_dependency": "rust",
                "compile_only_presets": [],
                "settings_presets": [
                    "ir-optimize-evm+yul",
                    "legacy-optimize-evm-only",
                    "legacy-optimize-evm+yul",
                    "legacy-no-optimize",
                ],
                "evm_version": f"{CURRENT_EVM_VERSION}",
                "solc": {
                    "binary_type": f"{args.solc_binary_type}",
                    "binary_path": f"{args.solc_binary_path}",
                    "branch": "master",
                    "install_dir": "solc/",
                },
            }
        )

        run_test(
            "PRBMath",
            FoundryRunner(
                config=runner_config,
                setup_fn=None,
                compile_fn=None,
                test_fn=None,
            ),
        )

    except InvalidConfigError as exception:
        print(f"Error while processing test: {exception}", file=sys.stderr)
        sys.exit(1)

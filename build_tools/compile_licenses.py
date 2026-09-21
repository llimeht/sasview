#!/usr/bin/python3

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from mako.template import Template  # type: ignore

# Define Mako template for HTML output
html_template = Template(
    r"""
<html>
<head>
    <meta charset="UTF-8">
    <title>SasView Dependencies</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 1em; }
        h1 { font-size: 1.3em; }
        h2 { margin-top: 2em; font-size: 1.2em; }
        pre { background-color: #f4f4f4; padding: 0.8em; white-space: pre-wrap; }
        ul { line-height: 1.6; }
        a { text-decoration: none; color: #0645ad; }

        /* Dark mode adjustments */
        @media (prefers-color-scheme: dark) {
            body { background-color: #000000; color: #e0e0e0; }
            pre { background-color: #2b2b2b; color: #f4f4f4; }
            a { color: #4da3ff; }
        }
    </style>
</head>
<body>
    <h1>SasView Dependencies</h1>
    SasView is built upon a foundation of free and open-source software packages.
    % if minimal:
        The following modules are part of this release of SasView.
    % else:
        The following modules are used as part of the build process and are bundled
        in the binary distributions that are released.
    % endif
    <ul>
    % for pkg in modules:
        <li><a href="#${pkg['Name']}">${pkg['Name']}</a></li>
    % endfor
    </ul>

    % for pkg in modules:
        <h2 id="${pkg['Name']}">${pkg['Name']}</h2>
        <p><strong>Author(s):</strong> ${pkg.get('Author', 'N/A')}</p>
        <p><strong>License:</strong> ${pkg.get('License', 'N/A')}</p>
        <pre>${pkg.get('LicenseText', 'No license text available.')}</pre>
    % endfor
</body>
</html>
"""
)


# minimal list of modules to include when distributing only in wheel form
minimal_modules = [
    "sasdata",
    "sasmodels",
    "sasview",
]


def get_modules(minimal: bool, python: str | None) -> dict[str, Any]:
    """Load pip-licenses JSON output"""
    cmd: list[str] = [
        "pip-licenses",
        *(["--python", python] if python else []),
        *(["--packages", *minimal_modules] if minimal else []),
        "--format=json",
        "--with-system",
        "--with-authors",
        "--with-license-file",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True,
    )
    modules = json.loads(result.stdout)
    # Sort the data by package name (case-insensitive)
    modules.sort(key=lambda pkg: pkg["Name"].lower())
    return modules


def format_html(filename: str, modules: dict[str, Any], minimal: bool) -> None:
    """Create the HTML output"""
    # Render the template with license data
    html_output = html_template.render(modules=modules, minimal=minimal)

    # Save the HTML to a file
    Path(filename).write_text(html_output, encoding="utf-8")


def main(argv: list[str]) -> bool:
    parser = argparse.ArgumentParser(
        description="Extract license information for modules in the environment",
    )

    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Only include information about a minimal set of modules",
    )
    parser.add_argument(
        "--python",
        metavar="PYTHON_EXEC",
        help="path to python executable to search distributions from",
    )
    parser.add_argument(
        "filename",
        help="output filename",
        metavar="OUTPUT",
    )

    args = parser.parse_args(argv)

    minimal = args.minimal
    filename = args.filename
    python = args.python

    modules = get_modules(minimal, python)

    format_html(filename, modules, minimal)

    return True


if __name__ == "__main__":
    sys.exit(not main(sys.argv[1:]))

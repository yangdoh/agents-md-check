# AGENTS.md Check

A small, offline checker for mechanical problems in `AGENTS.md` files. It helps maintainers spot issues before sharing agent instructions with a team. It does not modify files or send them over the network.

## What it checks

- Unresolved merge markers and invisible bidirectional text controls.
- Empty files, invalid UTF-8 and files above a configurable advisory size.
- Long duplicate lines in the same file, excluding fenced code blocks.
- Symbolic-link instruction files, which are reported but not followed.

The default 32 KiB warning is an arbitrary advisory threshold, not a statement about any specific agent's limits. This tool cannot determine whether instructions are correct, safe, contradictory, applied by an agent, or appropriate for a project. Review all findings yourself.

## Run

Requires Python 3.9 or later. No additional package is required.

```sh
git clone https://github.com/yangdoh/agents-md-check.git
cd agents-md-check
python3 agents_md_check.py /path/to/project
```

For a machine-readable report or a different advisory threshold:

```sh
python3 agents_md_check.py /path/to/project --json --max-bytes 16384
```

The tool recursively scans `AGENTS.md` files beneath the selected directory. It skips `.git`, `.hg`, `.svn`, virtual environments, `node_modules`, `__pycache__`, and symlinked directories. It does not honor `.gitignore`; choose a root whose contents you intend to scan. Files larger than 1 MiB are reported but not analyzed, and the scan is marked incomplete. Paths and line numbers may contain sensitive information, so review reports before sharing them.

Exit codes are `0` for no findings, `1` for findings, and `2` for invalid arguments or an incomplete scan. A directory with no `AGENTS.md` files produces a clean report with zero files; it does not mean the repository has valid instructions.

## Tests

```sh
python3 -m unittest discover -s tests -v
```

## Contributing

Issues and pull requests are welcome. Please do not include private instructions, secrets, or customer information in reports. Include a minimal sanitized reproduction and your Python version.

## License

MIT. See [LICENSE](LICENSE).

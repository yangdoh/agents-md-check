# Contributing

Bug reports, documentation fixes, and pull requests are welcome.

## Report a problem

1. Check whether the problem is already reported.
2. Make a minimal example using invented instructions only.
3. Include your operating system, Python version, command, expected result, and actual result.
4. Review filenames and output before sharing them; they can reveal private paths.

Do not include private instructions, credentials, customer information, or
internal directory names in an issue or pull request.

## Propose a change

1. Describe the problem and include a focused test for behavior changes.
2. Run `python3 -m unittest discover -s tests -v`.
3. Explain any changes to output, exit codes, or privacy behavior.

The checker should work offline and should not modify scanned files. New checks
must describe their limits; a mechanical check cannot establish that an
instruction is correct, safe, or followed by an agent.

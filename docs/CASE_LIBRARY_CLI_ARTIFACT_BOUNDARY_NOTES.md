# Case Library CLI Boundary Notes

The case-library CLI is intentionally separate from the primary `xau-lfx` command group.

Reason:

```text
v9 case-library artifacts are research/validation outputs, not current market-context runtime artifacts.
```

Boundary decisions:

- Use `python -m xau_lfx.validation.case_library_cli`.
- Require explicit `--event-log`.
- Require explicit `--out-dir`.
- Write JSON and Markdown only under the selected output directory.
- Fail with non-zero status when replay/node graph validation fails.
- Keep the existing artifact generator unchanged.

Future promotion to a main `xau-lfx` subcommand requires a separate spec and must preserve monitor-only semantics.

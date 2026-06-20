# Sharing Validation Reports Safely

Share the smallest artifact excerpt that reproduces a validation or dashboard problem. Raw broker exports are usually unnecessary.

## Safe workflow

1. Reproduce the issue with the current release.
2. Record the command name and package version.
3. Copy only the relevant `errors`, `quality_flags`, status, and row-count fields.
4. Replace local paths and account-specific names with placeholders.
5. Review timestamps and prices before deciding whether they may be shared.
6. Use the export-issue template and confirm that no credential is present.

## Never include

- `OANDA_API_TOKEN` or any authorization header;
- account identifiers, email addresses, or broker portal screenshots;
- complete live candle payloads unless redistribution rights are documented;
- absolute local paths that reveal a user name or private folder structure;
- third-party event data whose sharing terms are unknown.

## Minimal validation excerpt

```json
{
  "package_version": "2.4.0",
  "command": "validate-sources",
  "status": "ERROR",
  "source_file_role": "XAUUSD_M15.csv",
  "row_number": 14,
  "error_class": "OHLC_CONSISTENCY",
  "quality_flags": ["M15_CSV_INVALID"]
}
```

The example is a hand-written sanitized shape, not a broker export. Preserve the exact error text only after checking that it contains no private path or proprietary value.

## Live dashboard issue excerpt

For an OANDA refresh problem, share only:

- package version;
- endpoint path;
- `status` from `/api/xau/live/health`;
- redacted error class or HTTP status;
- operating system and Python version;
- whether the PC and phone are on the same private network.

Do not copy request headers or process environment output.

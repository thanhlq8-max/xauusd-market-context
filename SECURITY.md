# Security Policy

Please report security concerns through a private GitHub security advisory when available.

Do not include broker credentials, account identifiers, private API keys, or live trading account exports in issues or pull requests.

The CSV and static-demo paths require no broker credential. The optional OANDA Practice dashboard reads `OANDA_API_TOKEN` from the local process environment only. It must never be committed, placed in an issue, passed as a command argument, returned by an API route, or stored in browser code.

Bind the live dashboard only to loopback or a private LAN address. Do not use public port forwarding. Restrict any host firewall exception to a trusted private network profile.

# LFX Monitor Vocabulary Mapping

This document maps selected LFX monitor vocabulary into the external `xauusd-market-context` documentation layer. It is documentation only. It does not copy Pine thresholds, score weights, route logic, or private runtime assumptions.

Primary boundary reference: [`LFX_EXTERNAL_BASELINE.md`](LFX_EXTERNAL_BASELINE.md).

## Scope

The mapping is allowed only as monitor vocabulary for generated artifacts, reports, issue templates, and user-facing documentation. It must not add execution automation, account-risk logic, or directional trade-call behavior.

## Mapping table

| Vocabulary | External documentation meaning | Required boundary |
|---|---|---|
| Past context | Prior observed source context from user-provided local files. | It is evidence history, not a forecast. |
| Current context | The current generated artifact state after source validation and quality checks. | It is bounded by source freshness and artifact quality. |
| Conditional-next context | A possible future observation path that depends on later confirmed source data. | It must remain conditional and must not be presented as an instruction. |
| Reset | A context label for invalidated or weakened prior assumptions after new evidence. | It is descriptive only and must not imply an action. |
| Barrier | A structural reference zone or condition that may limit confidence or require extra caution. | It is a reference, not a mechanical trigger. |
| Release-reference | A reference label for when prior constraint language may no longer apply after new evidence. | It must not become route logic. |
| Structural-reference | A higher-level reference area or state used for context framing. | It must not become intraday instruction language. |
| Density-reference | A confluence or reference idea related to local profile concentration when separately scoped. | It is not implemented as an engine here and must stay subordinate to source quality. |

## Hypothesis and proxy language

The external repo may use bounded hypothesis/proxy wording only when source limitations are visible:

- inventory-style wording must remain a footprint hypothesis;
- retail-side wording must remain a footprint proxy;
- broker tick activity must remain `tick_volume`, not centralized traded volume;
- density wording must stay confluence/reference only until a separate implementation scope is locked.

## Allowed documentation usage

Allowed:

- explaining DID/NOW/NEXT context rows;
- explaining why a confidence cap was lowered;
- describing why source quality is insufficient;
- documenting user-facing report language;
- linking back to the external baseline contract.

Not allowed:

- copying Pine constants, thresholds, score weights, or route logic;
- converting vocabulary into execution automation;
- claiming actual dealer inventory or actual retail positioning;
- treating broker tick activity as centralized market volume;
- implying predictive, profitability, or financial-advice behavior.

## Release checklist

Before any future change uses this vocabulary in generated artifacts:

1. cite this document and `LFX_EXTERNAL_BASELINE.md`;
2. keep source limitations visible;
3. keep monitor-only wording active;
4. add or update tests for public wording;
5. document the change in the changelog when user-visible.

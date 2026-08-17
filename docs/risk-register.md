# Risk Register

| Risk | Level | Mitigation |
| --- | --- | --- |
| Automatic contest submission | Blocked | App has no submission endpoint; compliance gate blocks auto-submit language. |
| Terms acceptance | Blocked | User must accept terms manually outside PrizePilot. |
| Fake nonprofit or 501(c)(3) claims | Blocked | Compliance scanner blocks nonprofit/credential claims unless documented outside app. |
| Unverified prize facts | Needs Review | Fixture source notes distinguish official and needs-verification fields. |
| AI-use restrictions | Risky | Rules extractor surfaces AI/automation language and unknowns to verify. |
| Security bounty testing | Blocked by default | Sample fixture requires official scope and safe harbor before any action. |
| Firestore credentials unavailable | Needs Review | Local JSON fallback supports demo without paid services. |
| Gemini credentials unavailable | Needs Review | Local deterministic fallback keeps demo runnable while preserving GenAI SDK integration. |
| IP ambiguity | Needs Review | Win Plan includes IP review in sources needed and risks. |
| Sensitive personal data | Blocked/Needs Review | Scanner flags sensitive identifiers and tax/payment language. |


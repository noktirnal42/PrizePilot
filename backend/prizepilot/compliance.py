from __future__ import annotations

import re

from .models import ComplianceFinding, ComplianceReport, RiskLevel

BLOCKED_MESSAGE = "This action requires explicit human approval and must be completed manually outside PrizePilot."

PATTERNS: list[tuple[RiskLevel, str, str, str, bool]] = [
    ("Blocked", "Automatic submission", r"\b(auto(?:matically)? submit|submit on my behalf|click submit|file the entry)\b", "PrizePilot cannot submit entries or press final submission controls.", True),
    ("Blocked", "Terms acceptance", r"\b(accept terms|agree to terms|check the terms box|sign the rules)\b", "Terms and official rules must be accepted manually by the user outside PrizePilot.", True),
    ("Blocked", "Payments and taxes", r"\b(pay the fee|pay entry fee|submit tax|upload w-9|upload ssn|tax document)\b", "Payment, fee, and tax-document steps are blocked for manual completion only.", True),
    ("Blocked", "Fake identity", r"\b(fake account|fake identity|invent credentials|make up credentials|claim phd|claim 501\(c\)\(3\)|claim nonprofit)\b", "Unsupported identities, credentials, and nonprofit claims are prohibited.", True),
    ("Blocked", "Access control", r"\b(bypass captcha|bypass login|scrape behind login|bypass paywall|exfiltrate|private data)\b", "PrizePilot must not bypass access controls or expose private data.", True),
    ("Blocked", "Unauthorized security testing", r"\b(scan their network|exploit|destructive test|ddos|out of scope|unauthorized security)\b", "Security work is blocked unless official scope and safe harbor are verified.", True),
    ("Risky", "AI or automation restriction", r"\b(no ai|ai prohibited|ban ai|automation prohibited|manual submissions only|no generative ai)\b", "Rules may restrict AI or automation. Verify official wording before using AI assistance.", False),
    ("Risky", "Unsupported claims", r"\b(guaranteed impact|proven results|official endorsement|certified by|partnership with)\b", "Impact, endorsement, or certification claims need evidence before use.", False),
    ("Risky", "Citation risk", r"\b(source needed|citation needed|according to studies|research proves|statistics show)\b", "Statistics and research claims need citations from legitimate sources.", False),
    ("Needs Review", "IP ambiguity", r"\b(ip ownership|exclusive rights|work for hire|assign all rights|license ambiguity)\b", "IP terms need manual review before selecting or submitting.", False),
    ("Needs Review", "Sensitive data", r"\b(address|passport|driver'?s license|bank account|ein|ssn|date of birth)\b", "Sensitive personal or business data should not be uploaded through PrizePilot.", False),
]

LEVEL_RANK = {"Safe": 0, "Needs Review": 1, "Risky": 2, "Blocked": 3}


def scan_text(text: str) -> ComplianceReport:
    findings: list[ComplianceFinding] = []
    for level, category, pattern, message, blocked in PATTERNS:
        if re.search(pattern, text or "", flags=re.IGNORECASE):
            findings.append(ComplianceFinding(level=level, category=category, message=message, blocked=blocked))
    if not findings:
        return ComplianceReport(level="Safe", findings=[])
    top = max(findings, key=lambda item: LEVEL_RANK[item.level]).level
    return ComplianceReport(
        level=top,
        findings=findings,
        approval_gate_message=BLOCKED_MESSAGE if top == "Blocked" else None,
    )


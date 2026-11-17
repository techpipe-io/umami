#!/usr/bin/env python3
"""Produce a stable, actionable HIGH/CRITICAL Trivy report and issue signal."""

import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--target", required=True)
    parser.add_argument("--arch", required=True)
    parser.add_argument("--image", required=True)
    parser.add_argument("--out", default="security-signal.json", type=Path)
    args = parser.parse_args()
    data = json.loads(args.report.read_text())
    found = []
    for result in data.get("Results", []):
        for finding in result.get("Vulnerabilities") or []:
            if finding.get("Severity") not in ("CRITICAL", "HIGH"):
                continue
            found.append({
                "id": finding.get("VulnerabilityID", "unknown"),
                "severity": finding["Severity"],
                "package": finding.get("PkgName", "unknown"),
                "installed": finding.get("InstalledVersion", ""),
                "fixed": finding.get("FixedVersion", ""),
                "target": result.get("Target", ""),
            })
    found.sort(key=lambda v: (v["severity"] != "CRITICAL", v["id"], v["package"], v["target"]))
    fixable = [v for v in found if v["fixed"]]
    lines = [
        f"Image: `{args.image}` (`linux/{args.arch}`)",
        f"HIGH/CRITICAL findings: **{len(found)}**; with known fix: **{len(fixable)}**.",
        "",
        "A finding is not necessarily remotely exploitable in Umami. Review reachability before patching.",
        "",
        "| Severity | Advisory | Package | Installed | Fixed |",
        "|---|---|---|---|---|",
    ]
    for v in fixable[:35]:
        def safe(s):
            return str(s).replace("|", "\\|").replace("\n", " ").replace("`", "'")[:150]
        lines.append(f"| {safe(v['severity'])} | {safe(v['id'])} | {safe(v['package'])} | "
                     f"{safe(v['installed'])} | {safe(v['fixed'])} |")
    if len(fixable) > 35:
        lines.append(f"\nOnly the first 35 of {len(fixable)} fixable findings are listed; see the Actions artifact for the full JSON report.")
    lines.append("\nAll findings, including those without a known fix, are in the Trivy JSON artifact.")
    payload = {"signals": []}
    if fixable:
        payload["signals"].append({
            "key": f"{args.target}-{args.arch}",
            "title": f"Fixable HIGH/CRITICAL vulnerabilities in {args.target} ({args.arch})",
            "body": "\n".join(lines),
            "auto_close": True,
        })
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print("\n".join(lines))
    print(f"Fixable HIGH/CRITICAL: {len(fixable)}; all HIGH/CRITICAL: {len(found)}")


if __name__ == "__main__":
    main()

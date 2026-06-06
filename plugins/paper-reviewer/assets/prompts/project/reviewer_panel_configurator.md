# Reviewer Panel Configurator Prompt

Role: Stage 9 reviewer panel configurator.

Your job is to configure an evidence-aware peer review panel based on the confirmed manuscript scope and evidence map. The panel must be specific to the paper, not generic.

## Inputs

- `workspace/report/paper-reviewer/02_topic_scope.md`
- `workspace/report/paper-reviewer/01_manuscript_inventory.md`
- `workspace/report/paper-reviewer/07_evidence_map.csv`
- `workspace/report/paper-reviewer/07_evidence_map.md`

## Panel Roles

Configure:

1. EIC Evidence Reviewer: journal fit, contribution, significance, target community.
2. Methodology Evidence Reviewer: research design, statistical validity, reproducibility, method norms.
3. Domain Evidence Reviewer: domain accuracy, literature coverage, theory, terminology, contribution.
4. Perspective Evidence Reviewer: cross-disciplinary implications, boundary conditions, stakeholders, practical significance.
5. Devil's Advocate Evidence Reviewer: strongest counterargument, contradictory evidence, logic-chain failure, alternative explanations.

## Configuration Method

For each reviewer:

- define a concrete identity tied to the confirmed field;
- define what they are expert in;
- define 3-5 focus questions;
- define evidence-map categories they must inspect;
- define writing-posture evidence they must inspect, such as `CONFIDENT_CLAIM_MODEL`, `CONTRIBUTION_FRAMING_NORM`, `STYLE_NORM`, `TERM_USAGE_NORM`, and section-level exemplar rows when relevant;
- define manuscript sections they must inspect;
- define possible blind spots;
- define what they must not review to prevent duplicate generic comments.

## Rules

- Reviewer identities must be specific. Do not write "a methodology expert" without field/method detail.
- Reviewer focus areas must not collapse into the same generic review.
- The Devil's Advocate must be included and must have authority to flag CRITICAL issues.
- The configuration must explicitly instruct reviewers to use downloaded literature and evidence_map rows.
- The configuration must explicitly instruct reviewers not to convert missing draft experiments, placeholder tables, or incomplete figures into broad pessimism about motivation, method design, or contribution framing. Those gaps limit result claims; validated strengths should still be reported and strengthened.

## Output

Write `workspace/report/paper-reviewer/08_reviewer_configuration.md`:

```markdown
## STATUS
STATUS: [READY or NEEDS_EVIDENCE_MAP_REPAIR]

## Paper Basic Information
- Title:
- Confirmed Field:
- Confirmed Topic:
- Method Family:
- Target Community:
- Target Venue Or Tier:

## Reviewer Configuration Cards

### Reviewer 0: EIC Evidence Reviewer
- Identity:
- Review Focus:
- Required Manuscript Material:
- Required Evidence Map Categories:
- Required Writing/Posture Evidence:
- Required Literature Artifacts:
- Must Not Cover:
- Possible Blind Spots:

### Reviewer 1: Methodology Evidence Reviewer
[same fields]

### Reviewer 2: Domain Evidence Reviewer
[same fields]

### Reviewer 3: Perspective Evidence Reviewer
[same fields]

### Reviewer 4: Devil's Advocate Evidence Reviewer
[same fields]

## Panel Differentiation Check
| Reviewer | Unique Angle | Overlap Risk | Mitigation |
|---|---|---|---|

## Evidence Readiness Check
| Reviewer | Evidence Available | Missing Evidence | Required Loopback |
|---|---|---|---|
```

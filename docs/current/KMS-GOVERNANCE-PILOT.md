# Swift KMS staff review pilot

For subsequent triage and the Finance decision status, see the [26 November completion report](kms-feedback/Swift_G2P_KMS_Feedback_Completion_Response_26Nov2026.pdf).

## Sandbox result on 25 November 2026

Open Knowledge management and select **Staff review register**. A signed-in KMS editor can inspect guide versions, download an exact draft for review, and export filtered evidence as JSON. The existing editorial history retains saves, returns, approvals and publication. Verification officers can record checks. The existing independent-review and publisher permissions still apply.

| Feedback | Available in the staff editor | Outstanding acceptance |
| --- | --- | --- |
| CF-07 | Three candidate instructional rubrics, a 10-guide calibration set, blind first and second assessments, criterion-level comparison, and a reconciliation note. All three rubrics total 100. | Two designated reviewers independently score the ten actual versions, reconcile differences, and Swift KM confirms the convention. The ten pairs exercised in regression tests used synthetic marks. |
| CF-09 | Each of 15 current pilot versions has a Codex AI review, distinct from the Qwen drafting workflow. Each report stores the prompt, numbered article text, source excerpts, claim findings, instructional and technical assessments, and the policy evidence gap. | Swift KM triages 14 reports with findings. Controlled sources and business validation remain outstanding. One guide had sandbox support for all its sampled text. |
| CF-11 | The native editor now owns the review register. It reuses KMS permissions and editorial history. Evidence is bound to article ID and version and records reviewer identity, timestamp, type and finding. | Sudheendra and Swift confirm the ownership arrangement and JSON handover format. |
| CF-16 | Staff can check the current draft. Submitting and publishing record a snapshot of source-gap, boilerplate, identical or overlapping wording, and provisional terminology flags. | Reviewers decide which flags need correction. A clear scan or a supplied reference does not establish policy approval. |
| CF-17 | A recorded mock change to the PBMS Approval comment label identified and re-reviewed a field, three decision screens and the parent workflow. Four guides contain the literal label. The parent needs its related decision links checked. | OORU supplies canonical identifiers and confirms the real control label before any operational change. |

## Working with the pilot

1. In the register, select **10 calibration guides**. Open the draft for the assigned version. Each verifier records marks independently. The second submission makes both sets visible. Record the reason for differences under reconciliation. A new draft version starts a fresh assessment.
2. Score instructional quality on a 0–3 scale. Zero means missing, one means incomplete, two means usable with a gap, and three means clear and supported. **Not Assessable** excludes the criterion and its weight. The result is 100 × the sum of weighted marks divided by three times the assessable weight. An entirely unassessable guide has no numerical score. The weights are a new pilot convention. Historical medians from the earlier assessment use their original method.
3. To inspect the 15 independent reports, select **Guides with a current AI report**. Use the full finding and cited excerpt when deciding a correction. In particular, obtain the controlled refusal procedure for consent and Finance authority for reversal and reopening checks.
4. For a new report, download the current numbered inputs from the guide. Use the fixed review prompt, cite source excerpts for each finding, and retain the separate instructional, technical and policy assessments. The register export contains worked JSON examples. A verifier attaches the JSON to the exact version. The editor checks the digest and text coverage before retention.
5. To review a source revision or control change, record its exact dependency in the register. Editors can maintain additional dependency identifiers on the guide. The change captures the current versions of mapped guides. Its reviewers record a finding against each guide. Coverage depends on registered links.
6. Sandbox change #1 uses `pbms.approval-comment`. The reviewed articles are Finance #387 v4, Audit #388 v4, CEO #389 v4, the parent workflow #395 v2 and the comment field #405 v2.

## Verification

Seventeen automated tests passed across the knowledge lifecycle and the governance controls. Live staff sign-in, report upload and retry, versioned export and the five impact findings were verified. Anonymous access to the register returned HTTP 401. The sandbox still serves 568 public guides. The article and editorial-history table contents matched their pre-installation digests. All review evidence is staff-only.


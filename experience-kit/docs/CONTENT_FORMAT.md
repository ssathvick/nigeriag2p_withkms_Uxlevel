# Knowledge content format

Each entry has `slug`, `module`, `stage`, `audience`, `title`, `purpose`, `steps`, `requirements`, `next_step`, `issues`. Values are plain-text strings; `steps` contains newline-separated instructions. Slugs must be unique. Module IDs must exist in the seed's `modules` list. Audiences: `all`, `citizen`, `officer`, `verifier`, `supervisor`.

```json
{
  "slug": "intake-check-household",
  "module": "intake",
  "stage": "Household details",
  "audience": "officer",
  "title": "Check household details",
  "purpose": "Prepare a complete registration.",
  "steps": "Check the required fields.\nConfirm details with the applicant.\nSubmit using the registration service.",
  "requirements": "An authorized registration account.",
  "next_step": "Follow the service's review status.",
  "issues": "Return incomplete information through the approved workflow.",
  "scope": "local_workflow"
}
```

Optional reference fields: `scope` (`local_workflow` or `upstream_reference`), `sources` (list of `{ "title": "…", "url": "https://…" }`), `sources_checked_on` (`YYYY-MM-DD`). Approved source hosts are configured in `reference_hosts`. The editorial screen edits the nine core content fields; existing reference metadata is retained. New reference metadata is supplied through initial seed content or a deliberate implementation extension.

UI edits enforce nonempty fields, title/stage limits of 160 characters and 6,000 characters for other fields. Stage names must exactly match help mapping values. Preview with an independent reviewer before publishing. Published content is public; do not include beneficiary data, secrets or private staff information.

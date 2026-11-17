# Registry middleware review — 17 November 2026

## Status

Middleware source, tests and this review are included in the repository. They were
built and tested locally and have **not** been deployed to Kubernetes or copied into
live service directories. The F: development copy is unchanged by this work.

The live Registry UI remains on `nsipa/master-registry:mobile-downloads-20261117`.
The separate test image is `nsipa/master-registry:middleware-review-local-20261117`.

## Existing controls reviewed

- Registry Proxy previously handled locale routing only. API handlers read the access
  cookie and send the user's bearer token to IAM/native APIs.
- Native Registry/AWE record-security code remains responsible for ownership, allowed
  workflow states, independent review, revalidation and administrative permissions.
- The main registration Flask service already has session, CSRF and private-cache checks.
- The PBMS workflow adapter already checks its allowed Origin, JSON requests and the Odoo
  session; Odoo remains responsible for programme and approval permissions.
- The separate beneficiary portal uses its own Next.js 15 login/base-path middleware.
  This patch changes the main Registry web layer, not that independent login flow.

## Changes

1. Registry Proxy now covers API paths as well as the existing locale paths. Safe GET,
   HEAD and OPTIONS requests retain their existing behavior, including SSO redirects.
2. Browser writes reject cross-site Fetch Metadata, mismatched/opaque Origin, and
   mismatched Referer. The same check is repeated in `requireAuth` so protected route
   handlers do not rely solely on the Proxy matcher.
3. Existing non-browser JSON clients without Origin/Fetch Metadata remain compatible.
   Browser JSON requests still require the same-origin/CORS boundary. Originless simple
   forms and originless multipart clients must supply a trusted Origin or Referer.
4. API responses and authenticated page responses receive private/no-store caching.
   The native backend proxy removes authenticated fetch revalidation and overrides the
   legacy public cache declaration on register metadata. Schema payloads are unchanged.
5. Proxy generates a fresh request ID, replaces caller-supplied trace IDs and forwards it
   through the authenticated backend headers. No tokens or personal records are logged.
6. API responses receive `nosniff` and a same-origin referrer policy. Existing CSP and
   frame/login behavior are retained; an invalid comment inside the CSP string was removed.
7. Native API 401/403 responses retain their meaning even if an upstream returns HTML.
   Unreadable/unavailable upstream responses become safe 502 responses rather than raw
   exception messages. Native business validation/approval-denial messages remain intact.
8. IAM response parsing and malformed role-claim presentation data fail safely. IAM
   validation remains required before the existing role presentation hint is used.
9. Registry user administration and offline setup accept `NSIPA_REGISTRATION_URL` for
   isolated/destination configuration. The original sandbox fallback URL is unchanged.

No new client-side role authority, automatic approvals, payment actions, token expiry
rules or password changes were introduced. An in-process rate limiter was not added:
gateway limits need a separate capacity policy for offline/bulk uploads and shared users.

## Reverse-proxy configuration

Optionally set `APP_ORIGIN` to the canonical external Registry origin, for example
`https://g2p-register.wverve.in`. If unset, the browser origin is derived from Host and
X-Forwarded-Proto; the trusted edge must overwrite those headers. X-Forwarded-Host is
not treated as another allowed browser origin. Do not configure a list of unrelated
origins or add credentialed cross-origin CORS access without reviewing this boundary.

## Validation

- `npm run test:security`: 10 policy tests passed.
- Standalone production build and TypeScript checks passed.
- Isolated production smoke test: 27 checks passed against a local mock IAM/native
  backend. Container networking was disabled; no real credentials were used.
- Checks cover session 401 and ID-token-only 413 behavior, field-role presentation,
  SSO initiation, locale redirect, successful list requests, cross-site rejection before
  backend access, trace propagation, cache overrides, safe upstream failures, native
  approval denial, administration denial and private Collect setup proxying.
- These checks verify middleware compatibility, not a fresh end-to-end acceptance
  test of the real IAM/database, physical devices or every business workflow.

From `registry-ui-source`, build a separate test image and run:

```sh
docker build -f Dockerfile.native -t nsipa/master-registry:middleware-review-local-20261117 .
docker run --rm --network none -e MIDDLEWARE_ISOLATED_TEST=1 \
  -v "$PWD/tests:/review:ro" \
  nsipa/master-registry:middleware-review-local-20261117 \
  node /review/isolated-middleware-smoke.cjs
```

No live rollout or restart is part of these commands.

## References

- https://nextjs.org/docs/app/api-reference/file-conventions/proxy
- https://nextjs.org/docs/app/guides/backend-for-frontend
- https://nextjs.org/docs/app/guides/authentication

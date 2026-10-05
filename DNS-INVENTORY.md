# DNS inventory for kennethmacmillan.com

Captured 7 September 2026 from the authoritative nameserver (`dns1.p08.nsone.net`) while
the zone was still served by NS1, ahead of moving the nameservers. Rebuild the
zone from this table. Anything not listed here will not survive the move.

## Apex (`kennethmacmillan.com`)

| Type | Priority | Value |
|---|---|---|
| A | — | `198.185.159.145` |
| A | — | `198.49.23.144` |
| A | — | `198.49.23.145` |
| A | — | `198.185.159.144` |
| MX | 5 | `alt2.aspmx.l.google.com.` |
| MX | 10 | `aspmx2.googlemail.com.` |
| MX | 5 | `alt1.aspmx.l.google.com.` |
| MX | 1 | `aspmx.l.google.com.` |
| MX | 10 | `aspmx3.googlemail.com.` |

## Subdomains

| Host | Type | Value |
|---|---|---|
| `www` | CNAME | `ext-sq.squarespace.com.` |
| `mail` | CNAME | `ghs.google.com.` |
| `_domainconnect` | CNAME | `_domainconnect.domains.squarespace.com.` |

## Notes

- The zone carries **no SPF, DKIM or DMARC records**. Pre-existing, not caused by the move.
- The four `ns0*.squarespacedns.com` NS records in the zone are stray; the registry
  delegates only to the NS1 servers. They can be dropped.
- Apex `A` records and the `www` CNAME are Squarespace and are the ones being replaced.
- The five Google MX records and the `mail` CNAME are live email and **must be recreated**.
- `_domainconnect` was not visible to an outside scan and was found by Cloudflare's
  importer on 7 Sep 2026. It is Squarespace's auto-configuration record and can be
  dropped once the site is off Squarespace.

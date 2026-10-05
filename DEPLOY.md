# Moving kennethmacmillan.com off Squarespace

Checked on 7 September 2026. Re-check before you act if time has passed.

## What is actually where

**The domain is managed through Squarespace.** The WHOIS registrar field says
Tucows, which is misleading: Tucows is the wholesale registrar and the reseller
line underneath reads `Reseller: Squarespace`. That is how Squarespace Domains
has always worked, and it is also where domains moved when Google Domains was
sold to Squarespace. So the login you already have for the website is almost
certainly the login for the domain as well.

| Thing | Where it is now | Has to move? |
|---|---|---|
| Domain registration | **Squarespace**, on Tucows' registrar licence. Registered 2008, renews **10 August 2027 for $20** | Your choice |
| DNS hosting (the records) | **NS1** — `dns1–4.p08.nsone.net` | Yes |
| Website hosting | **Squarespace** — the apex A records point at their IPs | Yes, this is what you are leaving |
| Email | **Google Workspace** — MX records point at Google | No, but must be preserved |

WHOIS privacy is switched on, so the registrant shows as Contact Privacy Inc.
rather than a name. That is normal and is not a sign the domain belongs to
somebody else.

Two separate things are tangled together here, and they can be untangled
separately:

- **the website**, which you are moving off Squarespace, and
- **the domain registration**, which you may either leave with Squarespace or
  move elsewhere.

You can do the first without the second. But if the plan is to stop paying
Squarespace altogether, move the registration too, or you will be keeping an
account open purely to hold the domain.

## The one thing that can go wrong

**Your email runs on this domain through Google Workspace.** If the DNS records
are replaced without carrying the MX records across, email to anything
@kennethmacmillan.com stops arriving, silently, and senders get bounces.

These are the live MX records. Copy them exactly into any new DNS provider,
priorities included:

| Priority | Host |
|---|---|
| 1 | `aspmx.l.google.com` |
| 5 | `alt1.aspmx.l.google.com` |
| 5 | `alt2.aspmx.l.google.com` |
| 10 | `aspmx2.googlemail.com` |
| 10 | `aspmx3.googlemail.com` |

There is also `mail.kennethmacmillan.com` → CNAME → `ghs.google.com`, which is
the Google mail redirect. Carry that too.

Worth knowing separately: the domain currently has **no SPF, DKIM or DMARC
records at all**. That is a pre-existing gap, not something the move causes, but
it does mean anyone can forge email from the address. Adding SPF and DMARC while
you are in the DNS anyway is an hour well spent.

## The route

There is no login for the NS1 account that currently holds the DNS, so the zone
cannot be edited or exported where it sits. But the **nameserver setting** lives
with the registrar, and that is Squarespace, which you can get into. Changing it
there points the domain at a DNS provider you control and NS1 drops out of the
picture entirely. No NS1 access needed.

So: **the nameservers move to Cloudflare**, which is free, and puts DNS and
hosting in one account you own.

Because the zone cannot be exported, it has been read off the live nameserver
instead and written down in **[DNS-INVENTORY.md](DNS-INVENTORY.md)**. That file
is the whole zone. Cloudflare will try to import records automatically, but it
can only find records it thinks to ask for — it cannot list a zone it has no
access to. So treat its import as a starting point and check it against the
inventory. The zone is small, which makes this easy: four A records, five MX
records, and two CNAMEs.

Once the nameservers switch, NS1 stops being consulted and anything not carried
across is gone. The inventory is the safety net, so keep it.

The website itself goes to **Cloudflare Pages** (or Netlify — both are free at
this size, both serve static files, and both read the `_redirects` file already
sitting in `dist/`, so every old URL keeps working).

## Order of operations

Do it in this order. The site stays up throughout and Squarespace is cancelled
last, once you are certain.

1. **Log into Squarespace and find the domain.** It sits under Domains,
   separately from the website itself. Confirm you can open its settings and see
   a nameservers section. If you can, everything below is possible; if you
   cannot, stop and tell me, because the plan changes.

   *Confirmed 7 Sep 2026: it is there, under "Domains Managed by Squarespace",
   renewing 10 August 2027 for $20. The domain is billed separately from the
   website, so cancelling the website does not cancel it — but check it is still
   listed and still set to renew once you have cancelled.*

2. **Put the holding page up on a temporary address.** Upload the `holding/`
   folder to Cloudflare Pages. You get a URL like `kmacmillan.pages.dev`. Check
   it on a phone. Nothing about the live site has changed yet.

3. **Deploy the full site too**, from `dist/`, also on a temporary URL. Click
   through it properly. This is your chance to find anything wrong while the
   real site is still serving.

4. **Build the zone at Cloudflare.** Add `kennethmacmillan.com`, let it scan,
   then make the record list match **[What to put in the Cloudflare zone](#what-to-put-in-the-cloudflare-zone)**
   below exactly — including the Squarespace records. The point is that the zone
   is a copy of what is live today, so the switch changes nothing.

   Cloudflare cannot read the NS1 zone, only guess at it, so check every row
   yourself rather than trusting the scan. The five MX records matter most.

5. **Change the nameservers in Squarespace.** Domain settings has an *Update
   Nameservers* button and four custom entries reading `dns1–4.p08.nsone.net`.
   Replace them with the two Cloudflare gives you. This takes DNS out of NS1's
   hands and into yours, and because step 4 copied the zone faithfully, nothing
   visible should change.

6. **Wait for it to settle** — usually under an hour, occasionally 24. Then
   confirm email still works: send a message to your address from an outside
   account, and send one out. Do not skip this.

7. **Point the domain at the site.** In Cloudflare Pages, add
   `kennethmacmillan.com` and `www.kennethmacmillan.com` as custom domains and
   follow the prompt; it creates the records itself. HTTPS certificates issue
   automatically within minutes.

8. **Cancel the Squarespace website subscription** — but not the domain, unless
   you have already done step 9. Confirm the domain is still listed and still
   set to renew after you cancel.

9. **Optional, and best done a week later: move the registration too.** As long
   as the domain stays at Squarespace you need an account there, and it costs
   $20 a year. Cloudflare Registrar charges the wholesale price, about $11, with
   no markup and no upsell. To move it you unlock the domain in Squarespace (it
   currently shows `clientTransferProhibited`), request the authorisation code,
   and paste that into Cloudflare.

   Do this *after* the site is live, not alongside it. One change at a time.

## What to put in the Cloudflare zone

Build the zone to match what is live **now**, including the Squarespace records.
Then switching the nameservers changes nothing for visitors or for email: the
same answers come from a different place. Moving the website becomes a separate,
reversible edit afterwards.

Enter these before you touch the nameservers.

| Type | Name | Value | Priority | Proxy |
|---|---|---|---|---|
| A | `@` | `198.185.159.144` | — | DNS only |
| A | `@` | `198.185.159.145` | — | DNS only |
| A | `@` | `198.49.23.144` | — | DNS only |
| A | `@` | `198.49.23.145` | — | DNS only |
| CNAME | `www` | `ext-sq.squarespace.com` | — | DNS only |
| CNAME | `mail` | `ghs.google.com` | — | DNS only |
| MX | `@` | `aspmx.l.google.com` | 1 | — |
| MX | `@` | `alt1.aspmx.l.google.com` | 5 | — |
| MX | `@` | `alt2.aspmx.l.google.com` | 5 | — |
| MX | `@` | `aspmx2.googlemail.com` | 10 | — |
| MX | `@` | `aspmx3.googlemail.com` | 10 | — |

**Set the Squarespace records to "DNS only" (grey cloud, not orange.)** Proxying
them through Cloudflare would sit Cloudflare in front of Squarespace's own HTTPS
and can break the certificate. Once the site is on Cloudflare Pages the proxy is
fine and desirable, but not while Squarespace is still serving.

Do not add the four `ns0*.squarespacedns.com` NS records. They are stray, they
were never used, and Cloudflare supplies its own.

### Worth adding while you are in there

The domain has no email authentication at all. These two records are safe to add
and cost nothing:

| Type | Name | Value |
|---|---|---|
| TXT | `@` | `v=spf1 include:_spf.google.com ~all` |
| TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:charlottemacmillan@mac.com` |

SPF says Google is allowed to send as you; `~all` is a soft fail, so it will not
bounce anything if some other service also sends on your behalf. DMARC at
`p=none` only reports, it does not block, so it cannot break delivery. DKIM is
the third piece and has to be generated inside Google Workspace admin, so it is
a separate job.

## Records to remove afterwards

Once you are off Squarespace, these can go, and should, because they will
otherwise point at nothing:

- A records `198.185.159.144`, `198.185.159.145`, `198.49.23.144`, `198.49.23.145`
- `www` CNAME → `ext-sq.squarespace.com`
- The stray `ns01–04.squarespacedns.com` NS records sitting in the zone

## If something goes wrong

Switching the nameservers back at the registrar restores the old setup, and the
four to put back are `dns1.p08.nsone.net` through `dns4.p08.nsone.net`. Allow
the same settling time. Keep the Squarespace subscription alive until you have
finished, so the old site is always there to fall back to.

The one thing that is genuinely hard to undo is losing a DNS record nobody wrote
down, which is why [DNS-INVENTORY.md](DNS-INVENTORY.md) exists. If email stops
after the switch, that file is the first place to look: it will almost always be
a missing MX record.

## Publishing updates later

The site is a folder of files, so a later update is: run `./pipeline.sh`, then
upload `dist/` again, or push to a connected Git repository and let the host
rebuild. No CMS, no subscription, no version to keep up to date.

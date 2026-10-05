# Handover: point kennethmacmillan.com at Cloudflare DNS

You are picking this up mid-task with browser control. Everything below is
verified fact as of 7 September 2026, not assumption. Read it all before acting.

## Who and what

Charlotte MacMillan owns kennethmacmillan.com, the archive site for her late
father, the choreographer Kenneth MacMillan. She is moving the website off
Squarespace. A replacement site is already built and waiting; this task is only
the DNS groundwork.

Two accounts are involved, both hers, both already logged in:

- **Squarespace** — holds the domain registration and currently hosts the site.
- **Cloudflare** — new DNS host. Free account, zone already created.

## What is already done

The Cloudflare zone for kennethmacmillan.com has been fully built and checked,
record by record, against the live zone. It contains 14 records:

- 4 × A (apex) → `198.185.159.144`, `198.185.159.145`, `198.49.23.144`, `198.49.23.145`
- 3 × CNAME → `www` → `ext-sq.squarespace.com`, `mail` → `ghs.google.com`,
  `_domainconnect` → `_domainconnect.domains.squarespace.com`
- 5 × MX → Google Workspace, priorities 1 / 5 / 5 / 10 / 10
- 2 × TXT → SPF (`v=spf1 include:_spf.google.com ~all`) and DMARC on `_dmarc`

All A and CNAME records are set to **DNS only** (grey cloud), deliberately. Do
not turn proxying on. Proxying would put Cloudflare in front of Squarespace's
own HTTPS and break the certificate while Squarespace is still serving.

The zone is a deliberate **copy of what is live now**, including the Squarespace
records. The point is that switching nameservers changes nothing visible. The
website move is a separate, later step.

## The remaining task

**Switch the domain's nameservers from NS1 to Cloudflare.** That is all.

### Step 1 — get Cloudflare's nameservers

In the Cloudflare dashboard for kennethmacmillan.com, go to the **Overview**
page (left sidebar). Find the panel naming two Cloudflare nameservers. They are
randomly assigned first names and both end `.ns.cloudflare.com`, for example
`gina.ns.cloudflare.com`. Copy both exactly.

They are **not** on the DNS records page. This is the step she could not find.

### Step 2 — put them into Squarespace

Go to `https://account.squarespace.com/domains/managed/kennethmacmillan.com`
and find the **Domain Nameservers** section. It currently shows four custom
entries:

```
dns1.p08.nsone.net
dns2.p08.nsone.net
dns3.p08.nsone.net
dns4.p08.nsone.net
```

Press **Update Nameservers**. Replace all four with Cloudflare's two, leaving
the remaining fields empty. Squarespace requires a minimum of two, so two is
fine. If the form refuses to save with empty rows, clear rows three and four
rather than deleting them, and if it still refuses, stop and report what it says.

**Confirm with Charlotte before saving.** This is a live domain serving a real
site and live email. Show her the two values you are about to enter and get a
yes.

### Step 3 — verify, do not rush

Propagation is usually under an hour, occasionally up to 24. Once Cloudflare's
dashboard shows the zone as **Active**:

- The site at kennethmacmillan.com must still load normally.
- Email must still work. Have her send a message to her domain address from an
  outside account, and send one out.

If either fails, revert: put the four `dns1–4.p08.nsone.net` values back in
Squarespace. That restores the previous setup.

## Guardrails

- **Do not cancel the Squarespace subscription or delete the Squarespace site.**
  Squarespace is still serving the live website. It gets cancelled much later,
  after the new site is up.
- **Do not delete DNS records** in Cloudflare. Every one of the 14 is there on
  purpose, including the Squarespace ones.
- **Do not enable proxying** (orange cloud) on any record.
- **Do not transfer the domain registration.** That is a separate, optional,
  later job and must not be combined with this one.
- **Do not change anything in the Google Workspace admin.** The MX records are
  live email; treat them as untouchable.

## If something looks different from this brief

Stop and ask. The zone was verified on 7 September 2026; if the records on
screen do not match the list above, something has changed since and it needs
checking before anything is saved.

## Reference

The full zone as it existed before the move, captured from the authoritative
nameserver, is in `DNS-INVENTORY.md`. The wider plan, including the later
website move and the optional registrar transfer, is in `DEPLOY.md`. Both are in
her `kennethmacmillan` project folder on this Mac.

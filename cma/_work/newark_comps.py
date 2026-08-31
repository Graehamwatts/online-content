import statistics as st

# 9 one-bath Newark SFR sold comps, trailing 12mo, 2-4bd, 650-1300sf
comps = [
    dict(addr="7995 Peachtree Ave", sf=1208, beds=3, baths="2(1/1)", yr=1971, sold=1075000, orig=1150000, list_=1150000, dom=3, sold_date="2026-07-11", tier="remodel"),
    dict(addr="6234 Zulmida Ave", sf=942, beds=3, baths=1, yr=1953, sold=980000, orig=699000, list_=699000, dom=10, sold_date="2025-11-03", tier="remodel"),
    dict(addr="7698 Redbud Ct", sf=1087, beds=3, baths=1, yr=1971, sold=941000, orig=889950, list_=889950, dom=11, sold_date="2025-10-26", tier="fixer/dated"),
    dict(addr="36535 Mulberry St", sf=984, beds=3, baths=1, yr=1952, sold=915000, orig=925000, list_=925000, dom=21, sold_date="2025-10-07", tier="partial"),
    dict(addr="37340 Locust St", sf=1187, beds=2, baths=1, yr=1945, sold=880000, orig=899000, list_=880000, dom=47, sold_date="2026-06-22", tier="partial"),
    dict(addr="6278 Dairy Ave", sf=952, beds=2, baths=1, yr=1950, sold=865000, orig=899000, list_=899000, dom=15, sold_date="2025-09-19", tier="dated"),
    dict(addr="37266 Spruce Street", sf=1048, beds=3, baths=1, yr=1947, sold=848000, orig=948000, list_=880000, dom=51, sold_date="2026-05-15", tier="fixer/dated"),
    dict(addr="6364 Noel Ave", sf=942, beds=3, baths=1, yr=1953, sold=845000, orig=899000, list_=899000, dom=26, sold_date="2026-03-09", tier="partial"),
    dict(addr="36593 Leone St", sf=942, beds=3, baths=1, yr=1953, sold=755000, orig=810000, list_=810000, dom=32, sold_date="2025-11-14", tier="partial(discount)"),
]

for c in comps:
    c["ppsf"] = c["sold"]/c["sf"]
    c["lsr_orig"] = c["sold"]/c["orig"]*100

print(f"{'Address':22} {'SF':>5} {'Sold':>10} {'$/SF':>8} {'OrigList':>10} {'LSR%':>6} {'DOM':>4} {'Tier'}")
for c in comps:
    print(f"{c['addr']:22} {c['sf']:5} {c['sold']:10,} {c['ppsf']:8.2f} {c['orig']:10,} {c['lsr_orig']:6.1f} {c['dom']:4} {c['tier']}")

print()
dated_tier = [c for c in comps if c["tier"] in ("fixer/dated","dated")]
partial_tier = [c for c in comps if c["tier"].startswith("partial")]
remodel_tier = [c for c in comps if c["tier"]=="remodel"]

def summarize(name, group):
    ppsf = [c["ppsf"] for c in group]
    sold = [c["sold"] for c in group]
    print(f"{name}: n={len(group)}  $/sf median={st.median(ppsf):.2f} mean={st.mean(ppsf):.2f} min={min(ppsf):.2f} max={max(ppsf):.2f}")
    print(f"   sold median={st.median(sold):,.0f} mean={st.mean(sold):,.0f}")

summarize("DATED/FIXER tier (Redbud, Dairy, Spruce)", dated_tier)
summarize("PARTIAL/cosmetic tier (Mulberry, Locust, Noel, Leone)", partial_tier)
summarize("REMODEL tier (Peachtree, Zulmida)", remodel_tier)

print()
subj_sf = 950
for name, group in [("dated", dated_tier), ("partial", partial_tier), ("remodel", remodel_tier)]:
    ppsf = [c["ppsf"] for c in group]
    lo, med, hi = min(ppsf), st.median(ppsf), max(ppsf)
    print(f"Subject at {subj_sf}sf priced at {name} tier: low={lo*subj_sf:,.0f} median={med*subj_sf:,.0f} high={hi*subj_sf:,.0f}")

print()
all_lsr = [c["lsr_orig"] for c in comps]
print(f"All 9 comps LSR vs orig list: median={st.median(all_lsr):.1f}%  mean={st.mean(all_lsr):.1f}%  min={min(all_lsr):.1f}% max={max(all_lsr):.1f}%")
all_dom = [c["dom"] for c in comps]
print(f"All 9 comps DOM: median={st.median(all_dom)}  mean={st.mean(all_dom):.1f}")

# purchase price appreciation
purchase = 656000
purchase_date = "2017-04-05"
print()
print(f"Subject purchased {purchase_date} for ${purchase:,}")
for name, group in [("dated", dated_tier), ("partial", partial_tier)]:
    ppsf = [c["ppsf"] for c in group]
    med = st.median(ppsf)
    val = med*subj_sf
    gain = val - purchase
    pct = gain/purchase*100
    print(f"  vs {name} tier median value ${val:,.0f}: gross appreciation ${gain:,.0f} ({pct:.0f}%)")

<!-- Markdown twin of https://fapd.info/rules.html · Free Agentic Publication Digester -->
> This is the Markdown form of https://fapd.info/rules.html. Content is licensed CC BY 4.0
> (credit "FAPD — Free Agentic Publication Digester"); quoted official government
> text is public domain. For factual claims, cite the official source each item
> links to. Canonical source: `src/fapd/rules.py` in https://github.com/davidkarnowski/free-agentic-publication-digester.

# Selection rules

Every item in a digest names the rule that put it there, on its “Included because” line. Each rule is mechanical: it tests what a document is (its type, its court, its stage, whether it records a vote, how much floor time it took), never its party, its subject or its importance. When an item matches several rules, the first one listed here is the one recorded. Exclusion rules name what is counted in a section's totals but not listed one by one, so that nothing is left out silently. Changing a rule is a change to the project's governing guide, made in public. The [methods page](methods.html) explains the reasoning.

## Inclusion rules

### CREC-SEL-01

**In the digest:** floor item ≥ threshold floor time.

**Mechanical definition:** House/Senate floor granule with extracted text of at least 15000 characters (floor-time proxy).

### CREC-SEL-02

**In the digest:** recorded vote (all recorded votes are listed).

**Mechanical definition:** House/Senate floor granule containing a recorded-vote marker (Roll No. / Rollcall Vote No. / YEAS–NAYS tally); always included regardless of length.

### BILLS-SEL-01

**In the digest:** reached stage: reported/enrolled/calendar.

**Mechanical definition:** Bill text at a reached stage: Enrolled, Reported, or Placed-on-Calendar (version codes enr/rh/rs/pcs).

### FR-SEL-01

**In the digest:** document type: final rule (all listed).

**Mechanical definition:** Federal Register final rule (doc_type RULE); all are listed.

### FR-SEL-02

**In the digest:** document type: proposed rule (all listed).

**Mechanical definition:** Federal Register proposed rule (doc_type PRORULE); all are listed.

### FR-SEL-03

**In the digest:** presidential document (all listed).

**Mechanical definition:** Federal Register presidential document (doc_type PRESDOCU); all are listed.

### PLAW-SEL-01

**In the digest:** enacted into law (all public and private laws are listed).

**Mechanical definition:** enacted into law (all public and private laws are listed)

### AGENCYPR-SEL-01

**In the digest:** official agency release dated this day by the agency (all such releases from active sources are listed; titles only in the pilot).

### VOTES-SEL-01

**In the digest:** recorded vote of this day in a chamber's own roll-call record (every recorded vote is listed, in vote-number order; selection is by existence, not importance).

### BILLACTIONS-SEL-01

**In the digest:** action the Library of Congress's bill-status record dates on this day (every bill action in the window is listed, in bill-designation order; selection is by existence, not importance).

### USCOURTS-SEL-01

**In the digest:** appellate court opinion (all listed).

**Mechanical definition:** appellate court opinion (doc_type APPELLATE); all listed.

### USCOURTS-SEL-02

**In the digest:** national court opinion (all listed).

**Mechanical definition:** national court opinion (doc_type NATIONAL — e.g. Court of International Trade, Court of Federal Claims); all listed.

### PRESACT-SEL-01

**In the digest:** executive order published by the White House (all listed).

**Mechanical definition:** Executive order published by the White House (doc_type EO); all are listed.

### PRESACT-SEL-02

**In the digest:** presidential proclamation published by the White House (all listed).

**Mechanical definition:** Presidential proclamation published by the White House (doc_type PROCLAMATION); all are listed.

### PRESACT-SEL-03

**In the digest:** presidential memorandum or determination published by the White House (all listed).

**Mechanical definition:** Presidential memorandum or determination published by the White House (doc_type MEMORANDUM); all are listed.

### PRESACT-SEL-04

**In the digest:** other presidential action published by the White House (all listed).

**Mechanical definition:** Other presidential action published by the White House (nominations, and any class the feed does not name); all are listed.

## Exclusion rules (counted, not listed)

### FR-EX-01

**In the digest:** notices counted, not individually summarized.

### CREC-EX-01

**In the digest:** floor granule below floor-time threshold.

### CREC-EX-02

**In the digest:** extensions/daily-digest sections (counted).

### USCOURTS-EX-01

**In the digest:** district court opinions counted, not individually summarized.

### USCOURTS-EX-02

**In the digest:** bankruptcy court opinions counted, not individually summarized.

### AGENCYPR-EX-01

**In the digest:** release dated outside this day by the agency (feed backfill / newly activated source) — counted, not listed.

### VOTES-EX-01

**In the digest:** recorded vote the chamber dates on another day (inside the index lookback window) — counted, not listed.

### PRESACT-EX-01

**In the digest:** presidential action the White House dated outside this day (feed backfill / newly activated source) — counted, not listed.

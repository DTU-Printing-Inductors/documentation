---
name: datasheet-intake
description: Parse material datasheet PDFs from notes/hardware/materials/datasheets/new/ to markdown with Docling, then generate draft material notes from the parsed markdown. Use when the user says they added datasheets, asks to parse/scrape/convert datasheets or PDFs into material notes, or invokes /datasheet-intake. Optional args - company name, grade names, or the Functionality for the batch.
---

# Datasheet intake

Turns datasheet PDFs into material notes in three stages. AI-made files are kept separate from the user's manual ones.

| Stage | Folder (under `notes/hardware/materials/`) | Contents |
| --- | --- | --- |
| 1. Inbox | `datasheets/new/` | PDFs the user drops in |
| 2. Parsed | `datasheets/AI parsed/` (PDF) + `info/raw/` (markdown) | Renamed PDF + Docling markdown with the same name |
| 3. Drafts | `info/validate/` | Draft notes, `Status: To validate` |
| 4. Approved | `info/AI/` | Notes after the user approves, `Status: Identified` |

Never touch `info/manual/` or the manual PDF folder `datasheets/manual parsed/`. Those are the user's own. The extraction rules in `.agents/material-intake/AGENTS.md` also apply; read it if unsure about a field.

## Step 1: Parse
Run from the vault root:
```powershell
powershell -ExecutionPolicy Bypass -File .claude\skills\datasheet-intake\scripts\parse-datasheets.ps1
```
- **Always parse in parallel; never loop over PDFs one at a time yourself.** The script handles it: 2 Docling workers × 4 threads (8 CPU threads), one Docling call per worker so models load once, and **no OCR on the first pass** (datasheets are digital PDFs). Any PDF whose output is suspiciously short (likely a scan) is automatically re-parsed with OCR. Measured: about 18 s per PDF (about 40 s with the old one-by-one + OCR approach). Run long batches in the background.
- It converts each PDF in `datasheets/new/` to `info/raw/<same name>.md` and skips any that are already parsed. `-InputDir <folder>` parses another folder; `-Workers`/`-Threads` tune parallelism; `-Force` re-parses; `-Ocr` forces OCR for scanned batches.
- First run downloads Docling's models (a few minutes). Each PDF takes roughly 10-60 s.
- If Docling is missing: `uv tool install docling --python 3.12`.
- If a PDF fails or its markdown is nearly empty or garbled, read the PDF directly with the Read tool instead, and say so in the report. PDFs that needed the OCR retry often lose their title block (grade name, ISO 1043 designation), so always read those PDFs directly to confirm the grade and composition.
- If the Read tool says a PDF is password-protected, **retry once before telling the user**. This has been a transient error on files that open fine.

## Step 2: Identify and file
For each newly parsed markdown:
1. Read it and find the **manufacturer** and the **exact grade(s)**. One PDF can contain several grades, which means one note per grade.
2. Check for duplicates: look for the same grade in `info/validate/`, `info/AI/` and `info/manual/`. If it already exists, don't create a note. Report it as a duplicate instead.
3. Rename both files to `Manufacturer_Grade` (underscores for spaces, keep the grade's hyphens and dots) and move them:
   - PDF → `datasheets/AI parsed/Manufacturer_Grade.pdf`
   - markdown → `info/raw/Manufacturer_Grade.md`
   - If the name already exists, add `_reprint_YYYY-MM-DD`. Use shell `Move-Item` for these moves, with a short pause (`Start-Sleep -Milliseconds 300`) between files. Rapid back-to-back moves on OneDrive can make Obsidian miss files, so links to them look broken until Obsidian reloads. If the user reports a broken link to a file that exists, rename the file away and back to make Obsidian register it again.
4. If the user named specific grades, only create notes for those. Leave the rest parsed but unscraped, and list them in the report.

## Step 3: Draft notes in `info/validate/`
File name: `<Manufacturer> <Grade>.md` (spaces, matching existing notes, e.g. `MOCOM Alcom PA66 910-1.1 CF15.md`). Create it with the Write tool so the user gets a diff. Use exactly this property set and order:

```yaml
---
Grade:
Manufacturer:            # "[[Company]]" if notes/companies/** has that company note, else plain text
Supplier:                # "[[Company]]" if known (e.g. distributor the user named), else n/a
Type:                    # what the TDS calls it
Functionality:           # the user's classification for this batch; if not given, ask. Never infer.
Matrix:
Filler:
Filler loading:
Size:
Feedstock format:
Permeability:
Surface resistivity (Ω/sq):
Surface resistance (Ω):
Surface resistance standard:
Volume resistivity (Ω·m):
Volume resistivity standard:
Dielectric properties:   # free text: electric strength / breakdown voltage (with unit, AC/DC, thickness), CTI, standards; n/a if none
Thermal conductivity integral (W/m·K):
Thermal conductivity integral standard:
Thermal conductivity in-plane (W/m·K):
Thermal conductivity through-plane (W/m·K):
Thermal conductivity directional standard:
MOQ: n/a
Price: n/a
Lead time: n/a
Status: To validate
Datasheet: "[[Manufacturer_Grade.pdf]]"   # basename link; use the full path only if the basename exists twice
Processing instructions:
---
Parsed source: [[notes/hardware/materials/info/raw/Manufacturer_Grade.md]]

<one short paragraph: TDS date/version, dry vs conditioned basis, anything notable or ambiguous>
```

Value rules:
- Copy values **with their units and test standards** as stated. Note dry/conditioned in the body.
- `n/a` when the datasheet doesn't state it. **Never guess** pellet size, filler chemistry, loading or processing conditions.
- Ω/sq goes in `Surface resistivity`, Ω goes in `Surface resistance`. Don't convert between them.
- For volume resistivity in other units, convert to Ω·m and keep the original value and unit in the body.
- Add extra numeric properties only if they're central to the material (e.g. `Magnetic saturation (T)` for soft magnetic grades).
- Docling tables can misalign columns. If a value looks implausible, check it against the PDF before writing it.
- Known parser glitch: some PDFs (e.g. MOCOM/ALBIS) lose the letter **G** (shown as `�` or `ï¿½`), so "�F20" means "GF20". Rebuild the grade from the filler line and mention it in the note body. If a whole line is garbled (e.g. Special Features), leave that field `n/a` and flag it.

## Step 4: Report
List:
- notes created (with links)
- duplicates skipped
- grades parsed but not scraped
- any `n/a`-heavy notes or values you were unsure about
- which PDFs were read directly because parsing failed

Remind the user to review them in `notes/hardware/Validation.base` and to tick **Scraped** on the company in `Companies.base` when that company is done.

## Step 5: Approve (only when the user says so)
Move the approved notes from `info/validate/` to `info/AI/` (shell `Move-Item`) and set `Status: Identified` with the Edit tool. Don't write a `Last update` property: the material bases show the file's modified time (`file.mtime`) as "Last update", so it updates automatically. Never move notes to `info/AI/` without explicit approval.

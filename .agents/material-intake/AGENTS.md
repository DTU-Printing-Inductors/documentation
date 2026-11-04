# Polymer materials intake workflow

Use this workflow for material investigations in `notes/hardware/materials/`.

## Folder stages

- The user places source PDFs in `datasheets/new/`.
- Parse each PDF and create one draft note per unique material grade in `validate/`. Keep source PDFs in `new/` while notes await review.
- Check exact-grade matches in `validate/` and `AI/` before creating a note. Do not create duplicate material records.
- After the user explicitly approves, move approved notes to `AI/` and their source PDFs to `datasheets/AI/`. Rename PDFs descriptively as `Manufacturer_Grade.pdf`, using underscores for spaces and hyphens for grade punctuation.
- If an approved PDF name already exists for a duplicate grade, preserve both files: add `_reprint_YYYY-MM-DD` to the new copy. Use folder-qualified Obsidian links when the same PDF basename exists in more than one folder.

## Extraction and note fields

- Verify the exact grade on the supplied document. Prefer manufacturer TDS content; do not treat an SDS or family flyer as a grade-specific TDS.
- Use the existing material-note properties, including `Grade`, `Manufacturer`, `Supplier`, `Type`, `Functionality`, `Matrix`, `Filler`, `Filler loading`, `Size`, `Feedstock format`, resistivity and thermal-conductivity fields, `Status`, `Datasheet`, `Last update`, and `Processing instructions`.
- Copy values with their stated units, test standards, and dry/conditioned basis. Use `n/a` when the source does not disclose a value; do not infer pellet format, filler chemistry, loading, or processing conditions.
- Record surface measurements in `Surface resistivity (Ω/sq)` only when the source reports Ω/sq. Measurements reported in Ω belong in `Surface resistance (Ω)`. Do not convert between those properties without specimen geometry. Record volume resistivity in `Volume resistivity (Ω·m)`; when converting another unit, preserve the source value and method in the note body.
- Use separate thermal fields: `Thermal conductivity integral (W/m·K)`, its standard, in-plane value, through-plane value, and directional standard.
- `Functionality` is the user's research classification, not a substitute for the TDS's `Type`. Use the functionality the user specifies for that batch. If none is specified, leave it `n/a` and ask rather than inferring it from the datasheet.
- Use `Status: To validate` for drafts and `Status: Identified` after approval. Format `Last update` as `HH:mm DD/MM/YYYY` in Europe/Copenhagen time.

## Source tracking and review

- Append every investigated website, catalog query, and PDF batch to [[notes/hardware/Material source register]]. Record the date, source URL or PDF, status, resulting grade note, and a reason for any partial or skipped source.
- Use `Processed`, `Partial`, or `Skipped (reason)` consistently. Record exact-grade duplicates as skipped duplicate sources and link them to the existing grade note.
- Before handing off drafts, verify every note-to-PDF link, check the validation Base includes the notes, and report the number of unique grades and any duplicate or skipped sources.
- Never move drafts or PDFs into `AI/` until the user approves them.

---
epoch: 1794472134498
mode: agent
backendId: claude
sessionId: "db6893a2-47ec-4587-b15a-e875eca23e13"
topic: "Alright unfortunetally the Citations plugin is no longer wor…"
tags:
  - copilot-conversation
usage: '{"usedTokens":49077,"contextWindow":1000000,"inputTokens":2,"outputTokens":3,"cacheReadTokens":48777,"cacheWriteTokens":295,"updatedAt":1794472497558}'
---

**user**: Alright unfortunetally the Citations plugin is no longer working so I migrated to Citation Extended, but I want still the same functionality of Citations, where I could Inset this property table when I create literature note, create a template so it could be created again, search the docs for Citation Extended
[Timestamp: 2026/11/12 09:28:54]

**ai**: I've got the current plugin settings and the full list of template variables. Next I'm checking the Citation Extended docs for how the PDF file and the template work.I've set up Citation Extended so new literature notes get the same property table and sections as your old Citations notes. I haven't tested it in Obsidian yet. The GitHub docs page returned 404, so I worked from the plugin's own code, which includes its list of template variables and helpers.

**What I changed**
1. **`citation-content-template.md`** (in the vault root, where the plugin already looks for its template): it now has the same 8 properties as [[aghebModificationEmpiricalCore2013]] (Title, Year, Author, Tags with `#paper`, URL, DOI, Cite Key, Entry). It also adds the Source, Interpretation, Ideas and Connections headings.
   - **Entry:** your bib file stores the full Windows path to each PDF. The template keeps only the filename, so Entry becomes `[[file.pdf]]`, the same link format as your old notes.
2. **Plugin settings** (`.obsidian/plugins/citation-extended/data.json`):
   - New notes now go in `notes/papers` instead of `Reading notes`.
   - Notes are named `aghebModificationEmpiricalCore2013` instead of `@aghebModificationEmpiricalCore2013`.

**To check it works:** reload the plugin (turn it off and on in Community plugins). Then run "Open literature note" on a paper that doesn't have a note yet, and check that all 8 properties are filled in.

The one I'm least sure of is **Entry**. It relies on a `files` variable that the plugin's PDF-link features use, but it isn't in the plugin's documented variable list. If Entry comes out empty, tell me and I'll switch it to `attachments`, the documented variable for PDFs.
[Timestamp: 2026/11/12 09:28:54]

**user**: Can I link the pdf in the entry field or no?
[Timestamp: 2026/11/12 09:32:27]

**ai**: The empty Entry is my mistake: the PDF path is only available as `entry.files`, not `files`. Fixing the template:Yes, Entry can link the PDF. It came out empty because of a mistake in my template: the plugin doesn't offer the PDF path as `files` on its own, only as `entry.files`. I fixed the template to use `{{#each entry.files}}`. It still keeps just the filename, so Entry becomes `[[file.pdf]]` like your old notes.

- **This note:** I filled in Entry by hand as `[[polymers-18-00093.pdf]]`, the PDF your bib file lists for this paper.
- **New notes:** reload the plugin (turn it off and on) and create one more literature note. If Entry is still empty, the plugin may not expose the bib `file` field under that name either. In that case, send me the variable list from the plugin's settings and I'll match it.

This note was created as `Untitled 1.md` instead of `rzepeckiAnisotropicThermalConductivity2025.md`. That suggests it was made from a blank note rather than with "Open literature note", or the plugin hadn't reloaded the new name setting yet. Want me to rename it and move it to `notes/papers`?
[Timestamp: 2026/11/12 09:32:27]

**user**: Great, it works, thanks for fixing that up. Where does the template file live? I want it to be in the documents directory so it is stored with github and it would work on a different machine
[Timestamp: 2026/11/12 09:33:59]

**ai**: The template is already in your `documentation` folder, at `documentation/citation-content-template.md` in the vault root. The plugin's settings point to it with a relative path, so it will work on another machine. I couldn't check what git is tracking because git isn't on this shell's PATH. There's no `.gitignore` in the vault, so nothing is being excluded and the template will go to GitHub with everything else.

One setting will break on a different machine. Your bibliography path is saved as a full Windows path:

`C:\Users\artfi\OneDrive - Danmarks Tekniske Universitet\Research\documentation\pdfs\bibliography.bib`

It only works where the username and OneDrive folder are the same. The PDF paths inside `bibliography.bib` are also full paths, but the template keeps only the filename, so Entry links will still resolve. If the other machine has a different path, change the database path in Citation Extended's settings there. I didn't find anything in the plugin code showing whether it accepts a relative path like `pdfs/bibliography.bib`.

If you'd like the template filed somewhere tidier, I can move it to something like `templates/` and update the setting.
[Timestamp: 2026/11/12 09:33:59]

**user**: i moved to templates, update accordingly
[Timestamp: 2026/11/12 09:34:48]

**ai**: I updated the plugin's template path to `templates/citation-content-template.md` in `.obsidian/plugins/citation-extended/data.json`.

Reload the plugin (turn it off and on in Community plugins) so it picks up the new path. Do it before you change any Citation Extended setting, because changing a setting first could overwrite my edit with the old path. To check, the template field in the plugin's settings should now show the new path.
[Timestamp: 2026/11/12 09:34:48]
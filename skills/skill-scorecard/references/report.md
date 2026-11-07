# The report and the images

Both read the pooled summary (`summary-<tags>.json`) for numbers and
`report/copy.json` for words. Start `copy.json` from `assets/example/copy.json`.

## The verdict

Compare the `always` arm (or `skill`, with no `always` arm) against `noskill`:

| Verdict | When |
|---|---|
| **GOOD** | The pass rate rises beyond the noise, or tasks flip to wins with no flipped losses. |
| **BAD** | The pass rate falls, or flipped losses outnumber wins. |
| **MIXED** | The pass rate holds and the tasks flip both ways, or only efficiency moves. |
| **NO EFFECT** | Nothing moves beyond the noise. |

Efficiency (code, tokens, time) never makes a verdict GOOD on its own: same correctness
with less code is MIXED at best when anything broke, and NO EFFECT plus "cheaper" when
nothing did. The stamp shows the verdict word and a few words of why
("LESS CODE · SAME SCORE").

## Writing the copy

- The headline states the main finding as a plain sentence, like a figure caption.
- Every number in `copy.json` comes from the summary. Re-read each one against it.
- The stories are the flipped tasks: what the prompt asked, what each arm did, and a
  short quote from the agent's own reply when one shows the cause.
- The claims rows put the author's number next to the measured one. Colour with `ok`
  (holds), `meh` (real but much smaller), `no` (not reproduced). When the author
  measured on another model or benchmark, say so in `claims_note` and `claims_foot`.
- Positive wording: say what the skill does, with numbers. No hype, no rhetorical
  questions, no "gotcha".

`copy.json` fields, by where they appear:

| Field | Shown in |
|---|---|
| `title`, `eyebrow`, `copy.headline`, `copy.sub`, `copy.stamp*` | page header |
| `always_label`, `always_short`, `compare_title`, `copy.kpi_notes[4]` | page comparison |
| `copy.activation` | page activation panel (HTML allowed) |
| `matrix_note`, `copy.stories[]` | page grid and story cards |
| `claims[]` (`claim`, `readme`, `measured`, `ok`, `note`, `short`), `claims_title`, `claims_note` | page and slide 4 |
| `method[]`, `footer[]` | page bottom |
| `slides.*` | the 4 images |

## The page

`python3 report/build.py summary-<tags>.json` writes `report/scorecard.html`. Look at
it once (both themes), then publish it with the Artifact tool. Republishing the same
file keeps the URL.

## The images

`python3 report/render_slides.py summary-<tags>.json` writes `report/slides/slide-1..4.png`:
the verdict with the four headline numbers, the activation rate, the flipped tasks, and
the claims table.

They are 6:5 (2160×1800) because X's multi-image carousel crops each image to about
that shape: a 16:9 image loses its left and right edges. The script warns when any
element crosses the side margins or the bottom edge; shorten the copy until all four
print `ok`, then open each PNG and read it like a stranger on a phone.

The draft post's numbers must match the images. A post that says "costs more" next to
an image that shows −3% tokens gets quoted back at its author.

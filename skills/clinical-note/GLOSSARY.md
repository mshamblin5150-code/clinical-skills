# Shorthand glossary

Expansions [clinical-note](SKILL.md) applies at step 2. Anything absent here is an **unknown token** — carried forward verbatim and surfaced in the tier block.

> **Keep this file current.** Every unknown token that comes back from a note belongs here. The skill gets more deterministic with each line you add, and the shift-level roll-up in [batch-shift](../batch-shift/SKILL.md) exists to feed it.

## Personal shorthand

Observed in real notes. Expansions confirmed against the finished versions.

| Shorthand | Expansion |
| --- | --- |
| `hx` | history |
| `cc` | chief complaint |
| `dx` | diagnosis |
| `rtc` | return to clinic |
| `rec 4 days` | recheck in four days |
| `us` | ultrasound |
| `t 97.3` | temperature 97.3 °F |
| `spo2 96` | oxygen saturation 96% |
| `vaccs utd` | vaccinations up to date |
| `OP` | oropharynx |
| `L` / `R` | left / right |
| `36in 33lb` | height 36 inches, weight 33 pounds |
| `2/2j` | **ambiguous** — grade 2/6 murmur, or 2+ pulses. Flag as unknown; do not choose |

### Typos seen in the wild

Corrected silently as transcription noise, per the skill's Given rules.

`triglycerieds` → triglycerides · `oorphectomy` → oophorectomy · `endometroises` → endometriosis · `labido` → libido · `dryiness` → dryness · `sicnce` → since · `draininge` → drainage · `eart tympansotomy` → ear tympanostomy · `prednisolono` → prednisolone · `claritian` → Claritin · `zithromax` → Zithromax (azithromycin) · `brom fed` → Bromfed

## Dose conversions — derived, show the arithmetic

| Shorthand | Conversion |
| --- | --- |
| `1 t`, `1 tsp` | 5 mL |
| `3/4 t` | 3.75 mL |
| `1/2 t` | 2.5 mL |
| `1 T`, `1 tbsp` | 15 mL |
| `200/5ml, 3/4 t` | azithromycin 200 mg/5 mL, 3.75 mL = 150 mg per dose |

## Symbols

| Shorthand | Expansion |
| --- | --- |
| `c/o` | complains of |
| `s/p` | status post |
| `w/`, `w/o` | with, without |
| `2/2` | secondary to |
| `r/o` | rule out |
| `+` / `-` | positive for / negative for |
| `↑` / `↓` | increased / decreased |
| `→` | leading to, progressing to |
| `x` | for (duration) — `x3d` = for three days |
| `q`, `qd`, `bid`, `tid`, `qid` | every, daily, twice daily, three times daily, four times daily |
| `prn` | as needed |
| `NKDA` | no known drug allergies |

## History and exam

| Shorthand | Expansion |
| --- | --- |
| `HPI` | history of present illness |
| `PMH` / `PSH` | past medical history / past surgical history |
| `FH` / `SH` | family history / social history |
| `ROS` | review of systems |
| `NAD` | no acute distress |
| `AAOx3` / `AAOx4` | alert and oriented to person, place, time (and situation) |
| `RRR` | regular rate and rhythm |
| `CTAB` | clear to auscultation bilaterally |
| `S1, S2` | first and second heart sounds normal |
| `S/NT/ND` | soft, non-tender, non-distended |
| `EOMI` | extraocular movements intact |
| `PERRL` | pupils equal, round, reactive to light |
| `CN II-XII` | cranial nerves two through twelve |
| `MAEW` | moves all extremities well |
| `LOC` | loss of consciousness |
| `LAD` | lymphadenopathy |

## Vitals and diagnostics

| Shorthand | Expansion |
| --- | --- |
| `VSS` | vital signs stable |
| `BP` / `HR` / `RR` / `T` | blood pressure / heart rate / respiratory rate / temperature |
| `CBC` / `BMP` / `CMP` | complete blood count / basic metabolic panel / comprehensive metabolic panel |
| `LFTs` | liver function tests |
| `UA` | urinalysis |
| `CXR` / `KUB` | chest x-ray / kidneys-ureters-bladder x-ray |
| `CTA` / `CTH` | CT angiogram / CT head |
| `ECG`, `EKG` | electrocardiogram |
| `POC` | point of care |
| `hCG` | human chorionic gonadotropin |
| `FSH` | follicle-stimulating hormone |
| `TSH` | thyroid-stimulating hormone |

## Treatment and disposition

| Shorthand | Expansion |
| --- | --- |
| `IV` / `IM` / `PO` / `SL` / `SQ` | intravenous / intramuscular / by mouth / sublingual / subcutaneous |
| `NS` / `LR` | normal saline / lactated Ringer's |
| `abx` | antibiotics |
| `f/u` | follow up |
| `d/c` | **ambiguous** — discharge or discontinue. Flag as unknown unless context is unmistakable |
| `DC'd home` | discharged home |
| `AMA` | against medical advice |
| `PCP` | primary care provider |
| `ED` / `ER` | emergency department |
| `OBS` | observation |
| `RTED` | return to emergency department |

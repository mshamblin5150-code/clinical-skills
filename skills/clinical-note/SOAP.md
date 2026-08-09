# Comprehensive SOAP — template

The default branch of [clinical-note](SKILL.md). Tiering rules live in the skill; this file is the shape.

Omit no heading — this rubric wants the full set. A section the shorthand does not reach is **filled** per the skill's rules.

```
S:

CC: <one line, the presenting concern>

HPI: <narrative prose, third person, past tense. Opens with age, sex, and the
pertinent history that frames the visit, then the story. Labs and values quoted
as given. Closes with what was discussed or planned in conversation.>

Allergies: <given, or "No known drug allergies">
Medications: <given; "Not specified today" if none stated>
PMH: <given, comma separated>
Surgical History: <given, comma separated>

ROS:
General: <fragments; semicolon separated>
Skin:
HEENT:
Cardiovascular:
Respiratory:
GI:
GU:
GYN: <include only where relevant to the patient>
Musculoskeletal:
Endocrine:
Psych:
Neuro:

O:

Vital Signs: BP, HR, Temp, RR, SpO2, Height, Weight, BMI
General:
<then only the systems examined or reasonably part of this visit>
Diagnostics Reviewed: <given values only; omit the line entirely if none>

A:

Differential Diagnoses:
<3-5, most likely first, each a noun phrase>

Diagnoses:
<the working problem list, most acute first; include relevant history items
the visit addresses>

P:

<prose paragraph: orders placed, medications, return interval and its purpose,
continued measures, then return precautions — what brings the patient back sooner.>
```

## Section notes

**HPI** carries the narrative weight. Every clinical fact in it is a given; the prose that connects them is yours.

**ROS** is where filling is heaviest. Systems the shorthand addresses get its content; the rest get routine negatives as fragments — `No chest pain; no palpitations`. Include every system relevant to the complaint, and enough others to read as a genuine review.

**Diagnostics Reviewed** is never filled. Values appear only if given. Omit the heading rather than write a placeholder.

**Differential** is generated reasoning, and it is the one filled section that may name abnormal possibilities — a differential is explicitly a list of what has *not* been established. Keep it to entities the givens support.

**Plan** follows the shorthand's stated orders. Return precautions are filled and should be specific to this presentation, not generic.

# case-06

## 1. FILLED and DERIVED, read first

The tier block is present, so nothing here is being treated as filled by default.

**DERIVED**

1. BMI 23.0 = 703 x 160 / 70^2 = 22.955. **Both inputs filled** (height 5'10", weight 160 lb), so
   this derived value is treated as filled here.
2. Patient Time = Pediatric (0 - 17) Hours, from the given age 17. No filled input. Not a code.
3. Visit length 0:35, from estimated start 12:25 and end 13:00. **Both inputs are estimates**, so
   this is treated as filled. It bears only on an E/M level, which is step 5 and was not asked for.
4. Wound length 2.25 cm, under 2.5 cm. **Input given** — the 2.25 cm measurement is in the source.
   Not filled.
5. DOES NOT COMPUTE: days to the Thursday recheck. No visit date. Carried as GAPS 1, not a value.

**FILLED vitals and body measurements** (FILLED·asserted 1-8)

| value | filled |
| --- | --- |
| BP 126/74 | filled |
| HR 88 | filled |
| T 98.4 °F | filled |
| RR 16 | filled |
| SpO2 99% on room air | filled |
| Ht 5'10" (70 in) | filled |
| Wt 160 lb | filled |
| BMI 23.0 | filled, both inputs filled |

**Other filled content that a code could rest on**

- FILLED·asserted 10 — the entire neurovascular and tendon examination of the right thumb.
- FILLED·asserted 11 — wound exploration: full depth, no foreign body visualized, no tendon, joint
  capsule or bone exposure, clean base after irrigation.
- FILLED·asserted 12 — wound description beyond the given 2.25 cm measurement: clean approximable
  edges, no avulsion, no tissue loss, no active bleeding, no surrounding erythema or induration,
  **no nail bed or nail plate involvement**.
- FILLED·asserted 13, 14 — irrigation before closure; sterile dressing and uncomplicated tolerance.
- FILLED·asserted 9 — NKDA, including no known local anesthetic allergy.
- FILLED·proposed 1 — Tdap 0.5 mL IM single dose today, as the product satisfying "update tetanus".
  FLAG 1 records that the source does not say anything was administered.

Every remaining FILLED·asserted item (15-28) and FILLED·proposed item (2-16) is history, social
history, ROS, normal system exams, Medatrax declarations or future plan content, and supports no
code proposed below. Accounted for, and listed once here rather than repeated in step 4.

## 2. Codable elements

**Diagnoses, from the Assessment**

| element | support | mark |
| --- | --- | --- |
| Simple linear laceration of the right thumb, 2.25 cm, favored | "a 2.25 cm linear laceration of the right thumb" — given | codable; the *without foreign body* and *without nail damage* axes are filled-anchored |
| Tetanus immunization not up to date | "tetanus immunization not up to date" — given | codable |
| Immunization given at this encounter | Plan, Tdap 0.5 mL IM today — FILLED·proposed 1 | filled-anchored |
| Sheet-metal edge as the mechanism | "a clean linear cut from a sheet-metal edge" — given | codable |
| BMI 23.0, roughly the 65th percentile for age | VS line — derived from a filled height and a filled weight | filled-anchored |

**Differential entries** (Assessment), each carrying a code in step 3's differential section:
retained metallic foreign body; flexor pollicis longus injury; extensor pollicis longus or brevis
injury; digital nerve injury; digital artery injury; open fracture of the distal phalanx or
traumatic arthrotomy; wound infection present. The tetanus-prone-wound entry is not a competing
diagnosis and is coded above; the favored entry is coded above.

**Procedures, from the Objective and Plan**

| element | support | mark |
| --- | --- | --- |
| Laceration repair, right thumb, 2.25 cm, five 5-0 sutures, single layer | "Five 5-0 sutures placed. Wound approximated." — given; length given | the *simple* designation rests on the filled exploration |
| Tdap 0.5 mL IM administered today | FILLED·proposed 1 | filled-anchored |
| Immunization administration | FILLED·proposed 1 | filled-anchored |

Local infiltration of lidocaine 1% is anesthesia integral to the repair and is not coded separately.
Wound exploration is documented but is filled content and is a component of the repair as
documented; no separate exploration code is proposed.

## 3. Proposed codes

```
ICD-10  S61.011A  Laceration without foreign body of right thumb without damage to nail, initial encounter
  ANCHOR: "Skin/Wound, right thumb: a 2.25 cm linear laceration. Wound edges clean and approximable,
          no avulsion and no tissue loss." / "No nail bed or nail plate involvement."
  SOURCE: filled — the *without foreign body* axis rests on FILLED·asserted 11 (exploration to full
          depth, no foreign body visualized) and the *without damage to nail* axis rests on
          FILLED·asserted 12 (no nail bed or nail plate involvement). The wound itself, its
          2.25 cm length and its right-thumb site are given; confirm before submitting
  SPECIFICITY: complete — laterality documented as right, nail involvement addressed (absent),
          foreign body addressed (absent), episode of care initial for this encounter
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z28.39  Other underimmunization status
  ANCHOR: "Immunizations: tetanus not up to date, as stated."
  SPECIFICITY: complete — Z28.3 has exactly two children, Z28.31 for COVID-19 underimmunization and
          Z28.39 for every other, so lapsed tetanus coverage has no further axis to name. Z28.39's
          own inclusion term, "Lapsed immunization schedule status", is what the source documents
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z23  Encounter for immunization
  ANCHOR: "Tetanus and diphtheria toxoids with acellular pertussis (Tdap) 0.5 mL intramuscular,
          single dose, today."
  SOURCE: filled — the product, dose and the fact of administration are FILLED·proposed 1. The
          source directs only "update tetanus" and FLAG 1 records that nothing documents an
          administration; confirm before submitting
  SPECIFICITY: complete — Z23 has no further axis; its own tabular note puts the identification of
          which immunization onto the procedure code, which is CPT 90715 below
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  W26.8XXA  Contact with other sharp object(s), not elsewhere classified, initial encounter
  ANCHOR: "Character: a clean linear cut from a sheet-metal edge, bleeding controlled on arrival"
  SPECIFICITY: complete — a sheet-metal edge is a sharp object with no named W26 sibling (knife,
          sword, dagger, paper), the placeholder X fills the 5th and 6th characters, and the 7th is
          A for the initial encounter. Place, activity and status are separate codes rather than
          axes of this one, and none is documented — see step 4
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  Z68.52  Body mass index [BMI] pediatric, 5th percentile to less than 85th percentile for age
  ANCHOR: "BMI 23.0" (VS line)
  SOURCE: filled — BMI 23.0 is DERIVED 1 from a filled height (5'10") and a filled weight (160 lb);
          neither was measured, so both inputs are invented and the percentile band rests on them;
          confirm before submitting
  SPECIFICITY: complete — Z68.5- bands by percentile alone, and the tabular restricts pediatric
          codes to ages 2-19, which the given age 17 satisfies; no adult Z68.3- band applies
  CONFIDENCE: verify this number — the code exists and this descriptor is verbatim from
          ICD-10-CM FY2026, but the *choice* of band is recalled: it rests on the CDC growth chart
          placing BMI 23.0 at 17 years near the 65th percentile, and this repo ships the tabular,
          not the charts
```

```
CPT  12001  Simple repair of superficial wounds of scalp, neck, axillae, external genitalia, trunk
            and/or extremities (including hands and feet); 2.5 cm or less
  ANCHOR: length — "a 2.25 cm linear laceration"; repair — "Local anesthesia with lidocaine 1% ...
          Five 5-0 sutures placed. Wound approximated. Sterile dressing applied."; site — right
          thumb, an extremity/hand site
  SOURCE: filled — the *simple* designation requires a superficial wound closed in one layer without
          significant involvement of deeper structures, and that rests on FILLED·asserted 11 (no
          tendon, joint capsule or bone exposure, clean base after irrigation) and FILLED·asserted
          12 (no avulsion, no tissue loss). The 2.25 cm length and the five 5-0 sutures are given;
          confirm before submitting
  SPECIFICITY: complete — the two axes this family turns on are both settled: repair complexity is
          simple on the documentation above, and the length band is 2.5 cm or less at 2.25 cm, which
          is DERIVED 4 off a given measurement
  CONFIDENCE: verify this number — no CPT code set ships in this repo, so this number and its
          descriptor are recalled rather than looked up
```

```
CPT  90715  Tetanus, diphtheria toxoids and acellular pertussis vaccine (Tdap), when administered to
            individuals 7 years or older, for intramuscular use
  ANCHOR: "Tetanus and diphtheria toxoids with acellular pertussis (Tdap) 0.5 mL intramuscular,
          single dose, today." Age 7 or older is satisfied by the given age 17
  SOURCE: filled — FILLED·proposed 1; the source directs "update tetanus" and names no product, no
          dose, no route, no site and no lot, and FLAG 1 records that administration itself is not
          documented; confirm before submitting
  SPECIFICITY: complete — the product (Tdap rather than Td or DT), the route (intramuscular) and the
          age band (7 years or older) are the three axes this code carries, and the note states all
          three. That all three come from filled content is the SOURCE line's business, not this one
  CONFIDENCE: verify this number — no CPT code set ships in this repo; recalled
```

```
CPT  90471  Immunization administration (includes percutaneous, intradermal, subcutaneous, or
            intramuscular injections); 1 vaccine (single or combination vaccine/toxoid)
  ANCHOR: "Tdap 0.5 mL IM today" — one vaccine, injected route
  SOURCE: filled — same anchor as 90715, FILLED·proposed 1, and the administration is exactly what
          FLAG 1 says is undocumented; confirm before submitting
  SPECIFICITY: complete — the count axis is one vaccine and the route axis is injection; 90472 is
          the add-on for each additional vaccine and no second vaccine was given today
  CONFIDENCE: verify this number — no CPT code set ships in this repo; recalled
```

--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

The favored entry and the tetanus-prone-wound entry are proposed for entry above and are not
repeated here. The seven entries the note argues against follow.

```
ICD-10  S61.021A  Laceration with foreign body of right thumb without damage to nail, initial encounter   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  S66.001A  Unspecified injury of long flexor muscle, fascia and tendon of right thumb at wrist and hand level, initial encounter   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  S66.201A  Unspecified injury of extensor muscle, fascia and tendon of right thumb at wrist and hand level, initial encounter   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  S64.31XA  Injury of digital nerve of right thumb, initial encounter   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  S65.401A  Unspecified injury of blood vessel of right thumb, initial encounter   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  S62.521B  Displaced fracture of distal phalanx of right thumb, initial encounter for open fracture   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

```
ICD-10  L08.9  Local infection of the skin and subcutaneous tissue, unspecified   NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026
```

## 4. What documentation is missing

--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---

```
Depth of the wound and the layers closed. "Five 5-0 sutures placed. Wound approximated." does not
state whether the closure was single-layer, which is the line between a simple and an intermediate
repair
  affects: CPT 12001

Whether the Tdap was administered at this visit or only ordered. FLAG 1. Product, dose, route, site
and lot are all absent from the source
  affects: Z23, CPT 90715, CPT 90471

Place of occurrence, activity and employment status at the time of injury. Whether the sheet metal
was being moved at paid work, in a shop class or at home. GAPS 6
  affects: W26.8XXA — the Y92.-, Y93.- and Y99.- companions cannot be proposed at all without it

Volar versus dorsal position of the thumb wound. FLAG 4, GAPS 9
  affects: S66.001A and S66.201A, the two tendon entries in the differential, whose relative weight
  turns on it

A radiograph of the thumb. None was obtained, and exploration alone can miss a small radiodense
fragment
  affects: S61.011A — the foreign-body axis, and its refused alternative below

Nothing at the bedside settles a laterality, episode or site axis left open by a proposed code:
every proposed ICD-10 code above reads "complete" with its reason, so this block carries no
"unspecified" residue
```

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---

```
S61.011A — the wound is given at 2.25 cm on the right thumb; the "without foreign body" axis rests on
a filled wound exploration (FILLED·asserted 11) and the "without damage to nail" axis on a filled
wound description (FILLED·asserted 12)
  needs: a documented exploration and a documented nail bed and nail plate examination. If a
  fragment is found, this becomes S61.021A

Z23 — the immunization encounter rests on FILLED·proposed 1, the Tdap product and dose written in
for the source's bare "update tetanus"
  needs: documentation that a vaccine was actually administered, with product, dose, route, site and
  lot. FLAG 1

Z68.52 — BMI 23.0 derived from a filled height (5'10") and a filled weight (160 lb), placed in the
5th-to-under-85th percentile band from a recalled growth chart
  needs: a measured height and a measured weight, and a plotted BMI-for-age percentile. Both inputs
  are invented, so the band rests on nothing measured; the Assessment already lists BMI-for-age
  percentile as a screening to perform

CPT 12001 — the length and the sutures are given; the "simple" designation rests on the filled
exploration and the filled wound description
  needs: a documented wound depth and the number of layers closed

CPT 90715 — the product, dose and route are FILLED·proposed 1
  needs: the same documentation Z23 needs

CPT 90471 — the administration itself is FILLED·proposed 1
  needs: the same documentation Z23 needs
```

--- NOT CODED, NOTHING ESTABLISHED IT ---

```
Retained metallic foreign body in the thumb wound, suspected on a sheet-metal mechanism, which the
note names as the entry that would change management most; argued against by a filled wound
exploration, and no radiograph obtained
  NOT CODED: S61.021A  Laceration with foreign body of right thumb without damage to nail, initial encounter
  needs: a radiograph of the thumb, or a fragment recovered from the wound. The descriptor asserts a
  foreign body, and exploration alone can miss a small radiodense fragment
  proposed instead: S61.011A  Laceration without foreign body of right thumb without damage to nail,
  initial encounter
```

Every hedged item in the Assessment is accounted for. The seven argued-against differential entries
are coded in the differential block as documentation of reasoning; the one entry the note leaves
explicitly unexcluded is refused above with the code it would have earned named.

## 5. E/M level

No E/M level is selected, because none was asked for. The supporting elements, offered for the
clinician to map:

- **Problems addressed** — one acute injury with a procedure performed, plus a lapsed immunization
  status addressed in its own right, plus an open tetanus immune globulin decision the encounter
  could not close. The differential carries seven entries, one of which (a retained metallic
  fragment) is documented as not excluded with certainty.
- **Data reviewed** — no laboratory study and no imaging obtained today. The radiograph appears only
  as a conditional future order. External records were sought and are absent: the prior tetanus dose
  count is GAPS 2 and is the input the immune globulin decision turns on.
- **Risk** — a procedure with local anesthesia performed at this visit; a prescription-level
  analgesia plan; a documented decision against antibiotic prophylaxis with the conditions that
  would change it named; and an immunization administered.

The mapping of those elements onto an E/M level is recalled and nothing in this repo verifies it —
no coding guidelines ship here. Treat the three columns as the material and let the level be
assigned by the clinician.

# PROPOSED (verify before use)

ICD-10  F17.210  Nicotine dependence, cigarettes, uncomplicated
  ANCHOR: "Tobacco — current daily smoker, 1 pack per day for 24 years, 24 pack-years;"
  SPECIFICITY: complete — cigarettes and current uncomplicated use are documented, with no remission, withdrawal, or induced disorder
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  F12.90  Cannabis use, unspecified, uncomplicated
  ANCHOR: "Drugs — admits marijuana use, frequency and route not documented;"
  SPECIFICITY: needs: pattern and severity sufficient to distinguish use from abuse or dependence, plus remission, intoxication, withdrawal, or induced-disorder status
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R12  Heartburn
  ANCHOR: "PMH — history of elevated troponin, etiology not documented; denies myocardial infarction. Occasional heartburn."
  SPECIFICITY: complete — R12 is the billable symptom code for documented heartburn and has no laterality, episode, or severity axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R79.89  Other specified abnormal findings of blood chemistry
  ANCHOR: "PMH — history of elevated troponin, etiology not documented; denies myocardial infarction. Occasional heartburn."
  SPECIFICITY: complete — the blood-chemistry abnormality is specified as elevated troponin, while its cause is not established as a diagnosis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  L02.612  Cutaneous abscess of left foot
  ANCHOR: "Cutaneous abscess of the left foot, plantar great toe"
  SPECIFICITY: complete — the left foot site selects this billable leaf; an organism would be coded additionally rather than changing it
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.5  Residual foreign body in soft tissue
  ANCHOR: "Residual foreign body of the plantar soft tissue with surrounding inflammatory reaction"
  SPECIFICITY: complete — M79.5 is the billable residual-soft-tissue-foreign-body leaf and carries no laterality or episode axis
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  M79.675  Pain in left toe(s)
  ANCHOR: "left great toe pain and swelling + (1 month, 8/10 today, weight-bearing limited)"
  SPECIFICITY: complete — the documented left toe location selects this billable laterality-specific pain code
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R06.89  Other abnormalities of breathing
  ANCHOR: "Breath sounds diminished in all four fields."
  SPECIFICITY: complete — diminished breath sounds are the documented breathing abnormality, with no separately named respiratory diagnosis established
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  R03.0  Elevated blood-pressure reading, without diagnosis of hypertension
  ANCHOR: "BP 138/86 filled."
  SOURCE: filled — BP 138/86 was filled rather than recorded; confirm before submitting
  SPECIFICITY: complete — the note documents an isolated elevated reading without a hypertension diagnosis, which is the full scope of R03.0
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  E66.3  Overweight
  ANCHOR: "BMI 26.5 = 703 x 185 / 70^2 = 130,055 / 4,900 = 26.54. Overweight band."
  SOURCE: filled — overweight rests on BMI 26.5 derived from filled height 70 in and filled weight 185 lb; confirm before submitting
  SPECIFICITY: complete — E66.3 is the billable overweight diagnosis and the corresponding adult BMI band is coded separately
  CONFIDENCE: verified against ICD-10-CM FY2026

ICD-10  Z68.26  Body mass index [BMI] 26.0-26.9, adult
  ANCHOR: "36-year-old male, 24 pack-years current daily smoker, cannabis use, BMI 26.5:"
  SOURCE: filled — BMI 26.5 was derived from filled height 70 in and filled weight 185 lb; confirm before submitting
  SPECIFICITY: complete — given age 36 establishes the adult family and BMI 26.5 selects the 26.0–26.9 billable band
  CONFIDENCE: verified against ICD-10-CM FY2026

CPT  10060  Incision and drainage of abscess; simple or single
  ANCHOR: "In-clinic procedure documented in the plan: incision and drainage of the plantar left great toe wound."
  SPECIFICITY: needs: a completed procedure note documenting that drainage occurred and whether the abscess was simple or single versus complicated or multiple
  CONFIDENCE: verify this number

--- DIFFERENTIAL, DOCUMENTS MDM, NOT FOR ENTRY ---

Cutaneous abscess of the left foot was favored because the month-long course acutely worsened with focal swelling, a collection appearance, severe tenderness, and inability to bear weight; it repeats the for-entry code above.
ICD-10  L02.612  Cutaneous abscess of left foot  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Residual foreign body in soft tissue was co-favored because symptoms began at work after an unknown mechanism, followed an indolent course, and included an apparent subsurface object; it repeats the hedged for-entry code above.
ICD-10  M79.5  Residual foreign body in soft tissue  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Plantar verruca (plantar wart) was less likely because focal swelling, severe tenderness, and acute escalation were atypical for the observed lesion.
ICD-10  B07.0  Plantar wart  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Cellulitis of the left toe was less likely because spreading erythema, warmth, streaking, and fever were absent.
ICD-10  L03.032  Cellulitis of left toe  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Acute gouty arthritis of the first metatarsophalangeal joint (podagra) was considered because the great toe was exquisitely tender, but the plantar location, month-long course, and discrete collection made it less likely.
ICD-10  M10.9  Gout, unspecified  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Osteomyelitis of the distal phalanx was considered after a month-long focal infection in a smoker, but the intact skin and absence of a sinus or exposed bone left the disease unestablished; the documented left-toe pain code repeats here instead.
ICD-10  M79.675  Pain in left toe(s)  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

Diabetic foot infection was considered, but diabetes was not established and screening was proposed; the screening code documents the decision without asserting the disease.
ICD-10  Z13.1  Encounter for screening for diabetes mellitus  NOT FOR ENTRY
  CONFIDENCE: verified against ICD-10-CM FY2026

--- UNDOCUMENTED, WOULD SUPPORT A MORE SPECIFIC CODE ---

Cannabis pattern and severity sufficient to distinguish use from abuse or dependence, plus remission, intoxication, withdrawal, or induced-disorder status
  affects: F12.90

A completed procedure note documenting that drainage occurred and whether the abscess was simple or single versus complicated or multiple
  affects: 10060

--- CODED, ANCHOR WAS FILLED — CONFIRM BEFORE SUBMITTING ---

R03.0 — BP 138/86 was filled rather than recorded
  needs: a recorded blood-pressure measurement to establish an actual episode

E66.3 — overweight rests on BMI 26.5 derived from filled height 70 in and filled weight 185 lb
  needs: recorded height and weight to establish the overweight state

Z68.26 — BMI 26.5 was derived from filled height 70 in and filled weight 185 lb
  needs: recorded height and weight to establish the adult BMI band

--- NOT CODED, NOTHING ESTABLISHED IT ---

Osteomyelitis of the distal phalanx was considered after the month-long focal infection, but the skin was intact with no sinus or exposed bone and no radiograph result established bone infection
  NOT CODED: M86.9  Osteomyelitis, unspecified
  CONFIDENCE: verified against ICD-10-CM FY2026
  needs: a radiograph or other diagnostic result establishing infection of bone
  proposed instead: M79.675  Pain in left toe(s)

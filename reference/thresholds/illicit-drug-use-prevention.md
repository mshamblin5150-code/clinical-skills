# Illicit drug use prevention — threshold sheet

<!-- schema: threshold-sheet/2 -->

Decision points distilled from the complete source below. **Not a substitute for
the guideline** and not a clinical instruction. Each recommendation record is
preserved as a separate action so no recommendation is silently collapsed into
another.

## Sources

| key | society | document | source class | version | published | url | basis | mode |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| uspstf-2020 | USPSTF | USPSTF/illicit-drug-use-children-final-rec | recommendation-statement | 2020 | 2020 | https://doi.org/10.1001/jama.2020.6774 | stated | exact |

## Scope

**Read:** the complete recommendation statement, including the recommendation,
population limits, intervention descriptions, suggestions for practice, supporting
evidence, response, research needs, recommendations of others, and article material
on pp. 1-6. The read retained the numeric age and use-frequency boundaries that
change whether the prevention recommendation applies. Study sizes,
intervention-session counts, follow-up periods, effect estimates, outcome rates,
dates, and bibliographic numbers describe evidence or administration. Qualitative
patient-action statements are outside this sheet. The reference list on pp. 6-7 is
retired by class because it contains citations rather than clinical prose; it begins
after clinical prose on p. 6, so that page intentionally overlaps the read narrative
and exempt reference spans.

**Not read:** nothing in the source page range.

| span | pages | read |
| --- | --- | --- |
| complete recommendation-statement narrative | 1-6 | yes |
| references | 6-7 | exempt: citation list has no clinical prose |

citations resolved against C:/codeing/guidelines-src on 2026-08-31
extraction identity: producer fbc06d618e3f7c9a7bc9cc17843899dcffa4ff56; tools/guidelines_extract.py sha256 da118785b8872880e4957af279a693f5e943779781a08b7f018c95b5e9b417ac

## Populations

| key | verbatim |
| --- | --- |
| defined-age-population | children (11 years and younger), adolescents (aged 12-17 years), and young adults (aged 18-25 years), including pregnant persons |
| figure-defined-age-population | children (younger than 11 years), adolescents (aged 12 to 17 years), and young adults (aged 18 to 25 years), including pregnant persons |
| regular-users-or-sud | children, adolescents, and young persons who are regular users of illicit drugs (at least once per week) or have been diagnosed with a substance use disorder |
| not-regular-drug-users | children, adolescents, and young adults who are not regular drug users (defined as drug use less than 1 time per week) |

## Quantities

| key | verbatim |
| --- | --- |
| prevention-recommendation-age-scope | numeric age scope of the prevention recommendation |
| regular-use-exclusion | use-frequency boundary outside the prevention recommendation's scope |
| nonregular-use-eligibility | use-frequency boundary inside the prevention recommendation's scope |

## Thresholds

| quantity | population | value | snippet | source | page | rec | class |
| --- | --- | --- | --- | --- | --- | --- | --- |
| prevention-recommendation-age-scope | defined-age-population | children <=11 years; adolescents 12 to 17 years; young adults 18 to 25 years; includes pregnant persons | children (11 years and younger), ado- lescents (aged 12-17 years), and young adults (aged 18-25 years), including pregnant persons | uspstf-2020 | p2 | p2/narrative/recommendation-age-scope | narrative |
| prevention-recommendation-age-scope | figure-defined-age-population | children <11 years; adolescents 12 to 17 years; young adults 18 to 25 years; includes pregnant persons | Children (younger than 11 years), adolescents (aged 12 to 17 years), and young adults (aged 18 to 25 years), including pregnant persons. | uspstf-2020 | p2 | p2/narrative/recommendation-age-scope-figure | narrative |
| regular-use-exclusion | regular-users-or-sud | regular use >=once per week or diagnosed substance use disorder: outside scope | regular users of illicit drugs (at least once per week) or have been diagnosed with a substance use disorder are outside the scope | uspstf-2020 | p2 | p2/narrative/regular-use-exclusion | narrative |
| nonregular-use-eligibility | not-regular-drug-users | drug use <1 time per week: within scope | not regular drug users (defined as drug use less than 1 time per week) | uspstf-2020 | p4 | p4/narrative/nonregular-use-eligibility | narrative |

## Conflicts

CONFLICT: prevention-recommendation-age-scope — the prose defines children as 11
years and younger (`<=11`), while the clinician-summary figure defines children as
younger than 11 years (`<11`). Both source boundaries are retained rather than
silently reconciling the age-11 population.

## Coverage

- `p1/primary-care-based-interventions-to-prevent-illi/1` - I statement is a
  qualitative conclusion about insufficient evidence and states no numeric
  patient-action decision point

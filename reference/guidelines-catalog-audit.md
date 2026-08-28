# Guideline catalog independent audit

This ledger records the blind second read required by issue #106. The reader received the corpus PDFs and file identity only; the committed catalog values stayed hidden until every reading below was recorded. Values are derived metadata, not copied source passages.

`sha256` binds each reading to the exact PDF bytes. `page` is the one-based evidence locator, and `evidence` names the kind of source feature used. A disagreement remains a checker failure until a clinician adds a dated ruling that confirms the catalog value.

## Documents

| society | filename | sha256 | bytes | audited |
| --- | --- | --- | --- | --- |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | 3ee68c13990eb1ba89e3a0d4e74c12ff88bc59f626233e9ea3dde5766d4a645c | 442141 | 2026-08-20 |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | 0f6b6a8db10979bff55eaa9fe333f5dd89542444653cdff6927f9fcba632ee2a | 414298 | 2026-08-20 |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | f585d9f9d825e905cd10dc61787b9c3dca5a02467021058eb39b44ef3eb792e6 | 441139 | 2026-08-20 |
| ADA | standards-of-care-2026.pdf | 7e16169786974cf26e941a097ad60ef390824a8c09af280dea8ae863eda0cde1 | 9620154 | 2026-08-20 |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | 0f41a29f5757a7824a223895546a2757a35b06c12ef88870618dc6889e70e110 | 16885051 | 2026-08-20 |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | 981b98ddb8aa0c298278c5817e0b0718f101b7414a260cfb9e8c3fbd2542db99 | 4590173 | 2026-08-20 |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | 936b6ffcf27890731cdebf5bee45f8301aaf1aceb1654eaf29e52f66433a40bb | 8016526 | 2026-08-20 |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | 6e90423b5f1202732d15ee2cd638009642cfef650ab3346e91d97a23e0bbcdde | 4089250 | 2026-08-20 |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | 91382d1e0850a832fc03bc36e9e5686e080faf14d75b0e9fc07136ab6bd169bc | 1809435 | 2026-08-20 |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | 7cee2d8818175b5c867a5e287202d9a7aaed1a46e9ae9d1d77f07ea698ec9255 | 5205420 | 2026-08-20 |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | a5ceed7e41f05729e7f1eeddc52de9459fc8b9fe0987e29aba39071d6a66c879 | 7912108 | 2026-08-20 |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | fea51b5b72d7ea2f8e5b0c425fa42ac9fe8717221c7242c55ddf353a3f9f61b1 | 10710710 | 2026-08-20 |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | d602f312b8b8a724332be97ef938b2c57eb24b0b7901fc2e9914327f88ce49b8 | 10542421 | 2026-08-20 |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | be11558a6b2f034d13a375ff941104868886076bb4abbb1631afcb4c1ee4b3da | 8191254 | 2026-08-20 |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | d382f19c09c0e70dfedd772ac8e42fea86708fe354f2c626fc9a503040d20364 | 9976210 | 2026-08-20 |
| AHA ACC | kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf | 2fb2082cb8a8ecf00a5babcedb6e67f84770b8f3f92a7e5c249dd035efce336d | 2330798 | 2026-08-20 |
| AHA ACC | kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf | 656b830cb74292e023ad1fe92af8ca8e3eae00dfa712cd3f24cf983970eeb87d | 2936967 | 2026-08-20 |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | 566ec6e096f981952446e21d5d68135540d5f23d0a72460e72e52c32492300fd | 1964620 | 2026-08-20 |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | 4ab7f18ec7981a7b1aa6735b58f56dac0dafabbd17465bb8945c2a7ba38edb61 | 11853857 | 2026-08-20 |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | 6e55808dcb97110da6c5103408ab535f9f0d871ae54131e25cdeb63bb09a9110 | 1452338 | 2026-08-20 |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | a8eaee88aa2085561ff5b26416aaaaaf2b0d2dd6f078dc5af12d4ac3f8b320be | 1190649 | 2026-08-20 |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | 8d8916329f889e97b7e05e5bb2e909b5df04518b8c3a052815b714f1bf117f6d | 1898302 | 2026-08-20 |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | 092f50c311a5838eff7778e4c45010d9e95402becf3c7b488ef479aebce79582 | 6122891 | 2026-08-20 |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | 9762c2a90c95c54ecb4a8def52f86275e22eb6b8cc7f8b5e7e338c35f215d344 | 5431936 | 2026-08-20 |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | 472779ed702642ffbfb94c155d1a86e66d408cbb82014408028714c19790f72b | 13408299 | 2026-08-20 |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | 601089afd2653fd6c84795c06a950be58250eecfde706b517dfa54d8cca15397 | 8497900 | 2026-08-20 |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | 72135540309c16d990599fa49b5ec7d24e848af8bf5b9680d82b3a39e31680b3 | 4876643 | 2026-08-20 |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | bd80a13a30328ec97d096536efa3d3d1fc454f90af4df492629a57e92d15100d | 2176118 | 2026-08-20 |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | b728ba31de6693823b85754b664d09f24f0c3845ca0f2934b547ad4f9891a422 | 1804962 | 2026-08-20 |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | fa12e8e2dbd2090ea84d1a05ba48ab6d967fb1ce9a54d987e54249475714ddac | 20005544 | 2026-08-20 |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | b258b665a021cefdfdc9505a05ac8afe4daafb372f9a3e12300438f6c88f6a8b | 1273065 | 2026-08-20 |
| IDSA | ajrccm_200_7_e45.pdf | ef03f6a627875b4fc953e7c427866a596815cdf06ceb5e1d85bb7b5299ed79cd | 789030 | 2026-08-20 |
| IDSA | amr-guidance-update.pdf | 00c8af8fb551fd1094e6d0f23c9198702f8cf5eb3437b9ef46a395806994df2a | 1205401 | 2026-08-20 |
| IDSA | ciaa1215.pdf | 37c86a089c5b901f45ba83b48936582f41ef7477a66ecfdd7fb3004ae5f71108 | 1274722 | 2026-08-20 |
| IDSA | ciaa241.pdf | eb9b84ad81c9e33dfc5c61c177e898e10423bfb3c72a4ba6914471fac39f2685 | 634363 | 2026-08-20 |
| IDSA | ciab275.pdf | ec94d72672a320b21655d7523c41fa2195a67573707c1ee7b65ddd5ed6332f8b | 144215 | 2026-08-20 |
| IDSA | ciab549.pdf | 0bf8f3483969496aff9ab80d2b94ab3958c68ade8c815416e114d9b9215fd4b1 | 10161997 | 2026-08-20 |
| IDSA | ciab953.pdf | 3a701cd223c58705307d453a73c4b4f08ba5eeb2cf46c48f7100a76ad6f5b908 | 4187691 | 2026-08-20 |
| IDSA | ciac724.pdf | 1da6304a8829b3c8c24345992bb26a0048a3455d13af4d1a87576e68723f549c | 3101274 | 2026-08-20 |
| IDSA | ciad319.pdf | 0a0f0a926485c365c7bb03ee6175a4353c4f27a60020eff46d2d3e07f606f667 | 1065957 | 2026-08-20 |
| IDSA | ciad527.pdf | f76616485fab698c2193b1d092d246f45a1a7c8651e9b75b16bd5319a6df35d5 | 1108663 | 2026-08-20 |
| IDSA | ciae104.pdf | 5b23d7096ebc410c0fbc579db0c14219195fa085522d8ddc4ca978be407dd550 | 3022354 | 2026-08-20 |
| IDSA | ciae121.pdf | 92e88b2ef5bcb1f87fd3d617ea696b10e3b1141f08214c61dedcd4a0e79ae9fd | 1235188 | 2026-08-20 |
| IDSA | ciae479.pdf | 03a66b37d884249cf7e86f419774e11a161c9486c88616a31880f1d8aa7befb7 | 1772981 | 2026-08-20 |
| IDSA | ciu296.pdf | 9927d2f5a0470a0550a63312f03cdafc347be07a5c1b672b038bde02c63d2546 | 1049260 | 2026-08-20 |
| IDSA | ciu617.pdf | d3efb60abf255128ee35e5ae3a4aea1c1532c2ab73ed0d256512d4c674e1a795 | 717829 | 2026-08-20 |
| IDSA | civ482.pdf | 95b8c60ad699f06c80f0c5f6a502df12be5d30f7612334c1b49773a633ff74d1 | 350357 | 2026-08-20 |
| IDSA | ciw118.pdf | 3c078ad9943b8146f010af699eefd0bf38516f5ea97eb0c4402017db75f83d7b | 757705 | 2026-08-20 |
| IDSA | ciw353.pdf | 7e5a538f3b244d8655e624f0391ddfe7765a4ea58dd0074725838028ea5328d5 | 902716 | 2026-08-20 |
| IDSA | ciw360.pdf | 159657ea4ff4ad23300d358977101e0952ccdca930cd883755917c3720108f1a | 805006 | 2026-08-20 |
| IDSA | ciw376.pdf | 5e02dcc70242a78c956687db65dd5635222c8d729aa2032c75844332f9c0656d | 1062013 | 2026-08-20 |
| IDSA | ciw670.pdf | 68295d6fe539f5353d223bfa4d6270de858efcf58ca4301c245516add1f7fd83 | 1742372 | 2026-08-20 |
| IDSA | ciw694.pdf | 0c1e3ec62c5207131393935266ba56d3795e4482474ddeabcb0b24f9fcdf9d62 | 4098586 | 2026-08-20 |
| IDSA | ciw861.pdf | 95b54b49ac82edafff07010749660b578a0deb34beb3588972752ee9b3ff122c | 1891584 | 2026-08-20 |
| IDSA | cix1084.pdf | eb8bd86282c847b11acc59b0da49d3f5c17622ca2f4847b9318e65c87a986005 | 1154582 | 2026-08-20 |
| IDSA | cix1085.pdf | 742fc12877df8561b3aa68dc8b317ade1eccd1ce9f0e12492e6b26abb6556799 | 2935282 | 2026-08-20 |
| IDSA | cix636.pdf | 5be456e384ae34bc3956af4f3e721fe6abac60deb46e5fd8c4c82065275bc0a1 | 1340507 | 2026-08-20 |
| IDSA | cix669.pdf | 15d7bec0fa53581796d9e8058334db93eea58f9af8bab2f2113e3c901dff8fd0 | 1586793 | 2026-08-20 |
| IDSA | ciy745.pdf | e35c67e81d75e60837246a6a4ada4ffca5991e95d09f366a37788f6222a2b1cc | 2636923 | 2026-08-20 |
| IDSA | ciy866.pdf | 6f74151f94a07140b4307c3293db6709ba368ac4441c79cf24190ac54a148c14 | 2094342 | 2026-08-20 |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | 26722fc62de146c970e692b9a1959ead6d610b0d982b9768814cb2faae9dc608 | 320877 | 2026-08-20 |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | 68ee38cb1380ed8b521c41ba97bc2188348b2a72f9e74460751810f7ea7d734b | 396177 | 2026-08-20 |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | 633a440d5bcddd93c071c7546c8ef7eacdde0dbb5438a98a80460d279860df93 | 498795 | 2026-08-20 |
| IDSA | maternal-immunizations.pdf | e6b6c751a1b8418b558b5dfcb7fd042553da6a7d2861d6d00fc64163ab8cc0f9 | 864476 | 2026-08-20 |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | 0397b71f5241e2390556a99d96570a9e1a21f3263487266cd314387ee05ec6a1 | 912081 | 2026-08-20 |
| IDSA | piab027.pdf | 817044ff80e5fe1ecfffb80c4e3d293736303eee47b278644eabd757aba8a01c | 6027068 | 2026-08-20 |
| IDSA | piad089.pdf | bde4a2f75510c01fabc9d48a638f7ab9eccb45eab1997ae1ebcea73ae08abcdb | 8343198 | 2026-08-20 |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | 4560d44b23d6c3ded7b2a917b8fde5fc9518cb3e95f17b6f80c769fb22705e1a | 986368 | 2026-08-20 |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | 55434ffaaa8b662e9739ef34d23e0cf63ed7bb6e7b0509e0bb60206756250aa3 | 4117629 | 2026-08-20 |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | 82109d613573383599e380afc4708b56b4a81169fa76f0a84bd9fff88321b358 | 14069221 | 2026-08-20 |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | c23d7c29b1348111e171f7a4e982f74d3391eea915fd0f22955fc63fed41b623 | 563999 | 2026-08-20 |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | 50030e0eae12981adf2eb61e5cba783e957c1696394c3acf54ce74a74cb41d81 | 1106639 | 2026-08-20 |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | 1310b92cfcf73798af9cafce2dd26cb7360e411583ad92cd443bc1301981b5f6 | 1550036 | 2026-08-20 |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | 9de805834e3d6f009c11af84192e696c5b3b09dc9d1b13d141801f7c421969c9 | 1821890 | 2026-08-20 |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | 8864064d6e902574eb2505402e1ff787c38ee1a82476117e22860757373b568a | 11063116 | 2026-08-20 |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | 58f64dcae76177dbc77544dd1ad84aae69e81861d55c5a5be037c963a1a595f3 | 5010375 | 2026-08-20 |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | 3717244e8a539e710f32180720b442cf0d1dda12810cecbe61e4e8cfb54f7b23 | 4653242 | 2026-08-20 |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | 8ed871ec098c7eba1cfb0ff6bf2355a6c422166b2691aac138f0273307b2acff | 11320223 | 2026-08-20 |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | d2889a8b699ea103129c9f8f8df56c53557993741702e3140e3bd37fb96eb1fb | 8242002 | 2026-08-20 |
| KDIGO | KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf | 7a59501d9f9b60ceca7e15ce5ab0bfda33dc31270abed5b91b46288302d50ecf | 2591897 | 2026-08-20 |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | f1b71336d847a2aab8e44129c099a09d1c383580ea38f31187c45be8f9bfdec8 | 2119291 | 2026-08-20 |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | 0b77a9e32ca6c7bbccbddf902be4427bf8bc0d2dd7e3ffbc18042f602f371b27 | 5838922 | 2026-08-20 |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | a2d993887934c06817f571eec2cd61deddda5c5091e38f110f75caccc9d84889 | 9307417 | 2026-08-20 |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | 5fc2eca6eca313dbb48b3d9787826896fa95f9675701c6dfe79403836b8a0949 | 1489518 | 2026-08-20 |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | 4fe42962842b3f7330ca7bec7551fdb98ae90e56f6a12978c16c5d3a6a1eeb44 | 2018103 | 2026-08-20 |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | a0cf2b6db03a17f3e0c96a746032885b3b14a96786fcc9bb971aeeceff1b8fab | 6127282 | 2026-08-20 |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | 5e72c6f6f5f880e5d842fb8a461585770ba7dac3549da4625745b43f8bc131e1 | 10333458 | 2026-08-20 |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | 679e6d6641e214d497ed4ab6d4c72aaaab88f62faa4a2a249cca526591d71dd3 | 313239 | 2026-08-20 |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | b65b0c624ed315f45189edac2496cb6d5ffe9fb8f64e0b9670ce42ff0d8bab46 | 1737164 | 2026-08-20 |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | a813b94cf2f8f1434886683b6597cce54a9cd2cc0bf2ac7973a68a37f5923ac3 | 487783 | 2026-08-20 |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | b2d97cf1999be3ac98d60de1878e694c27b6a0db0afdea720d179de93c89e162 | 554847 | 2026-08-20 |
| USPSTF | afib-screening-final-recommendation-statement.pdf | 4fd739753e3ac8c0e8bd3ad9d0d2d22135265c8a83924e75822ecfa734824db0 | 536104 | 2026-08-20 |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | 184468d92a8a827d6e22a9afdc5d5c1432973d288a6d6517a79c01dbbd79e839 | 492142 | 2026-08-20 |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | c41425975b9e8b72246eb57540128a1902d50cf70c033b4d9f15a975fd55613c | 459933 | 2026-08-20 |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | 945a7c2c0a22b3cdc587cf47bd6361534f969df3aad437fa01e04c89383a7f93 | 575931 | 2026-08-20 |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | 26cc6a9a68635f69340b9b1e582f02607c9abbc4d5a99e04352a99666a89ad15 | 444064 | 2026-08-20 |
| USPSTF | autismfinalrs.pdf | ff15c972147249d22ba9f013c5bbdc1f070da45f313f5727aa5893fe9d697e5c | 486310 | 2026-08-20 |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | a321e77ed022a2ef74a51c5045978adb689fe047ca2366d5307c4acc391db062 | 412141 | 2026-08-20 |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | b293f7f1356b39c7b937df858cbef3e852f8fb8e0ffcbfe4cfce7a16d5a7115f | 504728 | 2026-08-20 |
| USPSTF | bladcanrs.pdf | d29523cf0ba28fa19987ef6ac190d6693673aab6aeb3bf3a029286dec30c6cd8 | 401108 | 2026-08-20 |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | 49426401d01a95e0b1e79354e02cb9b29369969a5ad4030d364168fe626aeadd | 634587 | 2026-08-20 |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | a48c5c8a6645c64e833d8fa418f6bc2393f1b759e2c2ffb6930b6f2b4ff8658d | 579403 | 2026-08-20 |
| USPSTF | breast-cancer-screening-final-rec.pdf | 0a2adb4feb5e6250f507923107b3a19cf3f67ebe41966e16ee5c4b7fc66c3355 | 591871 | 2026-08-20 |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | 0792b39eecffd5ae4fb01d7b075cb2c588a2adb6e38930da965933e16ff5c85c | 444071 | 2026-08-20 |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | b9d6c5a6ca0d72d4efaeb2a83d88dbdc56ad3a01bc5c00dd5aea1339c400c796 | 505776 | 2026-08-20 |
| USPSTF | celiacscreening-recstatement.pdf | 76a7b5a21e176d606bd73085558f9613349925a51b9f164f157c7f262152142d | 534851 | 2026-08-20 |
| USPSTF | cervical-cancer-final-rec-statement.pdf | 51b97d095e0ca1d300b81bf2f83a2f443a9ae25a3fec0ed990b8b86c9c8bff41 | 580324 | 2026-08-20 |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | 6a1269ad2543c4d9d5665c58ff69f1e6cab03534f9dc9ff8a51c4afbf646e4ce | 501674 | 2026-08-20 |
| USPSTF | child-vision-recstatement.pdf | c7f3f34ed22511d2e24999fedb0bbdcaa46fd3b1cc23a773cedde9e83e6bda89 | 701970 | 2026-08-20 |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | 28aaf31beaa6b1b14b5f4fd929be5c1e64ce05581bed8101426c6b140e2de975 | 862189 | 2026-08-20 |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | 9b7a962b95378c56bee7a25b62744b939c74b1e0b60abea259a3b1ac76d39abb | 446807 | 2026-08-20 |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | 47d559dd91e82c47f427fbe04eb8cd42cdb2dd91ab0f7a6a32dd2c1cc7d8dc45 | 740147 | 2026-08-20 |
| USPSTF | copd-screening-final-recommendation.pdf | 46cb30e7d73fdea4cafc2777b4d980423e15d744d3a6f41c39c6f0b9dd0b13f9 | 430122 | 2026-08-20 |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | 84288026137f008a1d566e6837792d8a8e5dacf173c799a7b7c95d9d27bf74e0 | 503077 | 2026-08-20 |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | 94a11a49dba07dbd18bda5e20ae7ad4271d76bb66ef9d4d2b3bef46453397b0c | 519206 | 2026-08-20 |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | c4d22f4fd48e391f87d8f501122f9a85a4253ca8de93986549c7bb53d2fcab72 | 541959 | 2026-08-20 |
| USPSTF | depression-suicide-risk-adults-rs.pdf | 5d9a544ecb145e50129fff8ac1bf6edc15ab95d966d76783cbe3292468df96b5 | 1279767 | 2026-08-20 |
| USPSTF | diabetes-child-final-recommendation.pdf | b7f968af922ce40d503533c3ea72ca0028997ee85937afe0c9b6c57ecf135676 | 473731 | 2026-08-20 |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | fc9bea488523dbe1ecfa568010b2d2930a38f80a26100cf83df004782bd78bf0 | 487218 | 2026-08-20 |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | 3062dd851d5d0ac794877d3fdaf8efbcdd6421df744ba1cbcde435c58ddc66d1 | 498919 | 2026-08-20 |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | 238e1ec6ab73a99c32db6a4fbcf1a9491f5ffa4d2297ffa4e7c15d7ef11b0bc9 | 476551 | 2026-08-20 |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | 6926dd6a341e1a66ee7f62088138fd8b847679ab3c45a76420bad666a9d3c705 | 469797 | 2026-08-20 |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | f43d217698f6cd90108d547d883341548cd3bab0430e8410dddf5d6fc3c1cad0 | 487554 | 2026-08-20 |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | b2a7d3b56d8ef9170f2054c231b5d76aaffbd01c34e2c7af80cc319434ac47d9 | 484436 | 2026-08-20 |
| USPSTF | glaucoma-screening-final-recommendation.pdf | d2f9ff4e1858d25bd68a02449616265496d7088dfb27105341d629d0adb592c7 | 466513 | 2026-08-20 |
| USPSTF | GON-final-recommendation.pdf | 2b0d60187fde0ac815607154af5dfbfd8c7ba750db7466a3349fb79312890a8e | 377575 | 2026-08-20 |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | 67b08ce62839fe8238150b6b02174d074f73e66952d2822bbcaaae422cd6bcfc | 478749 | 2026-08-20 |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | ba2df9a4a7a20524dd101db38b43df1068dab9f5b7b8e98b6e513941d726e9c8 | 455179 | 2026-08-20 |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | 1836d20598a6c7559cbd0b012a5e45ded25f9f8285d55aee463c2b868d5766cc | 487011 | 2026-08-20 |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | de7ee21c73e077e31a8bb81aa05c03471a8befbcb459b46794a65e46dcab5cef | 484688 | 2026-08-20 |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | 16ff95efc1f0ab01f0ae2720f43e6b348d3504be3c6feeebb5bb233669709cd8 | 646526 | 2026-08-20 |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | dbe00dfcfde93ed7a1eb8f0328e119c6f2cdd1512df781543b42b70e7dcbeeef | 402503 | 2026-08-20 |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | fa6150df426f1149c809f603007eef64402802fbf78a84b4c4c2a5acf10a363f | 489383 | 2026-08-20 |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | ec49218002496575734131698f1be92d6a4a343f830ec90827fc0ca8dd3ae2e3 | 543388 | 2026-08-20 |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | b545ee53f2545d3dbd9095ff7e239960936bc748f985930d0796d3c086ab37bb | 553142 | 2026-08-20 |
| USPSTF | hiv-screening-final-rec-statement.pdf | 8ae50eb66cd9684322831acf3d234d1b72376d0617fb38ebc0e386f096b6c345 | 523647 | 2026-08-20 |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | c006f784209c0dc4d3e81e2f1e7b4777114c7b14cd75147963d98519fba260f3 | 447630 | 2026-08-20 |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | a7083f690b0dc863af82faa8b876bb8893e05a4fb2680b7943edd3d2b0e0b388 | 507749 | 2026-08-20 |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | c3c750a948a49d647a578d4cf3b2111ef62860bca245d6c9010eacd410fc9e2f | 549599 | 2026-08-20 |
| USPSTF | idachildrenfinal.pdf | 230d0037eb6eaf1bea4863e1d848a1793e6b96cd6c0f831c04e6ac45f777f7c8 | 779389 | 2026-08-20 |
| USPSTF | illicit-drug-use-children-final-rec.pdf | 175fb81bcd5b788931131a1dc623074a8b775234c022898ea116b5bbfa8cc7e2 | 407147 | 2026-08-20 |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | 10f08ae48d1284d0433794a469ad71020ca09ab5d83b9e894f51bd3f1b88d16a | 468921 | 2026-08-20 |
| USPSTF | ipv-screening-final-rec-statement.pdf | 3567d287b7ac3f7a43853fd4679e713def939ce5aa3e36e7a9824e45d43917d3 | 513609 | 2026-08-20 |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | 711b8660c9b03ebb3fd873cb8a274f244d79ad1f0dc43f8b640e51a592b8f4d6 | 547740 | 2026-08-20 |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | 00a0f447512114fece67b031f644c6ae76b57d2b0df79e3ec4ad614fd27d5db2 | 503710 | 2026-08-20 |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | cefdbf07eb411d637d4510c072b32fd6fc65f6d9958c958ebe992ce2f1917183 | 496472 | 2026-08-20 |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | bc456e8af10d37d62238e588a544950fe70840d74b477e631c4e8a4e6b71bc83 | 529408 | 2026-08-20 |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | f357e049e3ce8a6f5ca1501cf72d01251974689805f24873d182bad839a39a68 | 499671 | 2026-08-20 |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | cc05af7fe9251c9e7b1ca953e3dfc3b72a464bd044a1145689a31bb924c33946 | 448837 | 2026-08-20 |
| USPSTF | oral-health-children-final-recommendation.pdf | 2c95346817a09d57058f8a63c19c3b4057c0cea04aeb9214115a91c3a6b88d33 | 504543 | 2026-08-20 |
| USPSTF | oralcancerfinalrs.pdf | 2c12508c0b408c35c776d67a4741bad14837a457385ea64ccb464ab8363d130a | 143745 | 2026-08-20 |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | 2bb498bfcfe568a053eee41c075b2d74996e787754c2d4caaf7803ffe3c21383 | 577550 | 2026-08-20 |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | 87ed37f10599e88540d4a9fd426ab2bb9b71ce1d044c1422996986556b23ba7b | 526620 | 2026-08-20 |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | 3b04960385d0abded95ec9a11536eb5292d23e487f25d400777ceb2720dc6fc7 | 491609 | 2026-08-20 |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | dcdb94ace4c07d96ebd97bd8da6a85e3b95a9838de84abe872e8fe7dc8f61754 | 527436 | 2026-08-20 |
| USPSTF | perinatal-depression-final-rec-statement.pdf | 53ccf6648c576754a4b3cde5474d9d58048ce4e88d0ad718fbb618ee0ddb6e94 | 536468 | 2026-08-20 |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | d523e5447fe6592727b1c66a5f7d9f256042011cfb410c93695af1c08f8f451f | 172732 | 2026-08-20 |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | 1f9f6b5bd7abca530089192185e2197d0827e450632080ab115a27e8d1417914 | 740325 | 2026-08-20 |
| USPSTF | rhrs.pdf | deb402efbc27f506cc02aae253476d20ba1e4b115eaf50617272a5a02145aeda | 65752 | 2026-08-20 |
| USPSTF | scoliosis-final-rec-statement.pdf | 3b266fb06dd073a3499a1ebfb0e611cb7c6bdf78e5b256d3ee3de168e21545d3 | 485909 | 2026-08-20 |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | 1f189586bc329fedf9173de9cc4410444dca0fe8fb1d6bc1a54da12274da0baf | 567178 | 2026-08-20 |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | dac99383ada4bd470373a3073a33bcc21967d63632cf2837f24ec5d2f83feadc | 169878 | 2026-08-20 |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | f2f234814fc21ff46ed42fee0487805faec77dada1febb5218e4d03c465c0935 | 459966 | 2026-08-20 |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | 693672d00221c8a6c6689dc1747117513b5b61fb98b82f21adec5172f36a6d02 | 465990 | 2026-08-20 |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | 9924d1b265ed5cd44cc681b63497c4ee0a7a4e19775f3edeec6967bb6095ff24 | 538857 | 2026-08-20 |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | 6ec550f7fe0136b787db464f01520013f9e54e41c16d2d35c5a2198c36da2f36 | 498376 | 2026-08-20 |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | 44b6591fcef864f95c9d9875efe92caebaa6a5bf6068e08fe5b6acef3cd78e7e | 486917 | 2026-08-20 |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | 2ed700a36fcc2f3b9b6c63669e9aadc07957dfc51d8ec2db824e00ca3462ff2f | 534093 | 2026-08-20 |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | 248b51fe0584bf10fa190018b526ce81347bf6bfa6511f493c6d7acf3e090a6a | 509107 | 2026-08-20 |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | 58f17139c8c460ec29020dc811f90070b00b1c75ee516e757f3810859acb7ad8 | 470035 | 2026-08-20 |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | b698225c59cba46b25125abd650542ea9d0599f62e61e1d9b4866805ebc71bcb | 492295 | 2026-08-20 |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | 05dbc55f5f63377746fa30ab72529ea9aeb35cea069188c8f1001841cc789270 | 443648 | 2026-08-20 |
| USPSTF | testicuprs.pdf | 53b5c177b6cfd01501764f489a9f5bb89fd95fa6d10d03ee5e96d645700ae778 | 349483 | 2026-08-20 |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | 758048ad0b979e6bc94947e13e74fb1f3a90e4c437de441d57a8a7bd8d26b84a | 552430 | 2026-08-20 |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | 609c7c5ddba745fe11b61df074a84c308b80bb2a3ee0543e15773c025e64ddfb | 445325 | 2026-08-20 |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | 50ef14ae7327594bde1f30e76b6d6dabc63e8ff993a34996ccc12d3d6d23b755 | 574190 | 2026-08-20 |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | 1ff082bc6ba28a32eff115fbce4f3353a4a19cdbedbb0d932faf1e0db90a83ce | 494828 | 2026-08-20 |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | 0f0b7b594f652a1cb7da5a6dee532b581bbde919fcc77e766f89831546292d37 | 445001 | 2026-08-20 |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | 3c7a5ae4df62a15950408e80f3e182a7eb560083c54a2ea2a9e9231bd780647e | 543090 | 2026-08-20 |

## Independent readings

| society | filename | column | value | page | evidence |
| --- | --- | --- | --- | --- | --- |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | title | Recommended Vaccinations for Adults | 1 | title-page |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | topic | adult immunization schedule | 1 | title-page |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | population | adult | 1 | front-matter |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | year | ? | 1 | front-matter |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | title | Recommended Vaccines for Older Children | 1 | title-page |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | topic | childhood immunization schedule | 1 | title-page |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | population | pediatric, adolescent | 1 | front-matter |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | year | ? | 1 | front-matter |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | title | Recommended Vaccines for Young Children | 1 | title-page |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | topic | childhood immunization schedule | 1 | title-page |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | population | pediatric | 1 | front-matter |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | year | ? | 1 | front-matter |
| ADA | standards-of-care-2026.pdf | title | Standards of Care in Diabetes—2026 | 1 | title-page |
| ADA | standards-of-care-2026.pdf | topic | diabetes standards of care | 1 | title-page |
| ADA | standards-of-care-2026.pdf | population | ? | 1 | front-matter |
| ADA | standards-of-care-2026.pdf | year | 2026 | 1 | title-page |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | title | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 | 1 | title-page |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | topic | opioid prescribing for pain | 1 | title-page |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | population | adult | 1 | front-matter |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | year | 2022 | 1 | title-page |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | title | Summary Guide for Asthma Management and Prevention | 1 | title-page |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | topic | asthma management and prevention | 1 | title-page |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | year | 2026 | 1 | title-page |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | title | Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease | 1 | title-page |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | topic | COPD diagnosis, management, and prevention | 1 | title-page |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | population | ? | 2 | front-matter |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | year | 2026 | 1 | title-page |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | title | 2026 ACC/AHA/AACVPR/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Dyslipidemia | 1 | title-page |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | topic | dyslipidemia management | 1 | title-page |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | population | pediatric, adolescent, adult | 2 | front-matter |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | year | 2026 | 1 | title-page |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | title | 2024 Guideline for the Primary Prevention of Stroke | 1 | title-page |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | topic | primary stroke prevention | 1 | title-page |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | population | general | 1 | front-matter |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | year | 2024 | 1 | title-page |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | title | 2026 AHA/ACC/ACCP/ACEP/CHEST/SCAI/SHM/SIR/SVM/SVN Guideline for the Evaluation and Management of Acute Pulmonary Embolism in Adults | 1 | title-page |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | topic | acute pulmonary embolism evaluation and management | 1 | title-page |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | population | adult | 1 | front-matter |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | year | 2026 | 1 | title-page |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | title | 2024 ACC/AHA/AACVPR/APMA/ABC/SCAI/SVM/SVN/SVS/SIR/VESS Guideline for the Management of Lower Extremity Peripheral Artery Disease | 1 | title-page |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | topic | lower extremity peripheral artery disease management | 1 | title-page |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | population | ? | 1 | front-matter |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | year | 2024 | 1 | title-page |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | title | 2018 AHA/ACC/AACVPR/AAPA/ABC/ACPM/ADA/AGS/APhA/ASPC/NLA/PCNA Guideline on the Management of Blood Cholesterol | 1 | title-page |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | topic | blood cholesterol management | 1 | title-page |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | population | general | 2 | front-matter |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | year | 2018 | 1 | title-page |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | title | 2021 AHA/ACC/ASE/CHEST/SAEM/SCCT/SCMR Guideline for the Evaluation and Diagnosis of Chest Pain | 1 | title-page |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | topic | chest pain evaluation and diagnosis | 1 | title-page |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | population | adult | 1 | front-matter |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | year | 2021 | 1 | title-page |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | title | 2025 ACC/AHA/HRS/ISACHD/SCAI Guideline for the Management of Adults With Congenital Heart Disease | 1 | title-page |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | topic | adult congenital heart disease management | 1 | title-page |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | population | adult | 1 | front-matter |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | year | 2025 | 1 | title-page |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | title | 2022 AHA/ACC/HFSA Guideline for the Management of Heart Failure | 1 | title-page |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | topic | heart failure management | 1 | title-page |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | population | ? | 1 | front-matter |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | year | 2022 | 1 | title-page |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | title | 2022 ACC/AHA Guideline for the Diagnosis and Management of Aortic Disease | 1 | title-page |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | topic | aortic disease diagnosis and management | 1 | title-page |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | population | ? | 1 | front-matter |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | year | 2022 | 1 | title-page |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | title | 2023 ACC/AHA/ACCP/HRS Guideline for the Diagnosis and Management of Atrial Fibrillation | 1 | title-page |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | topic | atrial fibrillation diagnosis and management | 1 | title-page |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | population | ? | 1 | front-matter |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | year | 2023 | 1 | title-page |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | title | 2025 AHA/ACC/AANP/AAPA/ABC/ACCP/ACPM/AGS/AMA/ASPC/NMA/PCNA/SGIM Guideline for the Prevention, Detection, Evaluation and Management of High Blood Pressure in Adults | 1 | title-page |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | topic | high blood pressure prevention, detection, evaluation, and management | 1 | title-page |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | population | adult | 1 | front-matter |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | year | 2025 | 1 | title-page |
| AHA ACC | kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf | title | 2021 Guideline for the Prevention of Stroke in Patients With Stroke and Transient Ischemic Attack | 1 | title-page |
| AHA ACC | kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf | topic | secondary stroke prevention | 1 | title-page |
| AHA ACC | kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf | population | ? | 1 | front-matter |
| AHA ACC | kleindorfer-et-al-2021-2021-guideline-for-the-prevention-of-stroke-in-patients-with-stroke-and-transient-ischemic.pdf | year | 2021 | 1 | title-page |
| AHA ACC | kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf | title | 2018 ACC/AHA/HRS Guideline on the Evaluation and Management of Patients With Bradycardia and Cardiac Conduction Delay | 1 | title-page |
| AHA ACC | kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf | topic | bradycardia and cardiac conduction delay | 1 | title-page |
| AHA ACC | kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf | population | ? | 1 | front-matter |
| AHA ACC | kusumoto-et-al-2018-2018-acc-aha-hrs-guideline-on-the-evaluation-and-management-of-patients-with-bradycardia-and.pdf | year | 2018 | 1 | title-page |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | title | 2023 American Heart Association Focused Update on the Management of Patients With Cardiac Arrest or Life-Threatening Toxicity Due to Poisoning | 1 | title-page |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | topic | cardiac arrest and life-threatening poisoning | 1 | title-page |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | population | general | 1 | front-matter |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | year | 2023 | 1 | title-page |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | title | 2026 AHA/ACC/ADA/ASN Guideline for the Prevention, Detection, Evaluation, and Management of Cardiovascular-Kidney-Metabolic Syndrome | 1 | title-page |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | topic | cardiovascular-kidney-metabolic syndrome | 1 | title-page |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | population | adult | 1 | front-matter |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | year | 2026 | 1 | title-page |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | title | 2020 AHA/ACC Guideline for the Diagnosis and Treatment of Patients With Hypertrophic Cardiomyopathy | 1 | title-page |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | topic | hypertrophic cardiomyopathy diagnosis and treatment | 1 | title-page |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | population | pediatric, adolescent, adult | 2 | front-matter |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | year | 2020 | 1 | title-page |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | title | 2020 AHA/ACC Guideline for the Diagnosis and Treatment of Patients With Hypertrophic Cardiomyopathy: Executive Summary | 1 | title-page |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | topic | hypertrophic cardiomyopathy diagnosis and treatment | 1 | title-page |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | population | pediatric, adolescent, adult | 2 | front-matter |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | year | 2020 | 1 | title-page |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | title | 2024 AHA/ACC/AMSSM/HRS/PACES/SCMR Guideline for the Management of Hypertrophic Cardiomyopathy | 1 | title-page |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | topic | hypertrophic cardiomyopathy management | 1 | title-page |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | population | pediatric, adolescent, adult | 2 | front-matter |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | year | 2024 | 1 | title-page |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | title | 2020 ACC/AHA Guideline for the Management of Patients With Valvular Heart Disease | 1 | title-page |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | topic | valvular heart disease management | 1 | title-page |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | population | ? | 1 | front-matter |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | year | 2020 | 1 | title-page |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | title | Guidelines for the Early Management of Patients With Acute Ischemic Stroke: 2019 Update to the 2018 Guidelines for the Early Management of Acute Ischemic Stroke | 1 | title-page |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | topic | acute ischemic stroke early management | 1 | title-page |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | population | adult | 1 | front-matter |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | year | 2019 | 1 | front-matter |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | title | 2026 Guideline for the Early Management of Patients With Acute Ischemic Stroke | 1 | title-page |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | topic | acute ischemic stroke early management | 1 | title-page |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | population | pediatric, adolescent, adult | 2 | front-matter |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | year | 2026 | 1 | title-page |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | title | 2025 ACC/AHA/ACEP/NAEMSP/SCAI Guideline for the Management of Patients With Acute Coronary Syndromes | 1 | title-page |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | topic | acute coronary syndrome management | 1 | title-page |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | population | ? | 1 | front-matter |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | year | 2025 | 1 | title-page |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | title | 2023 AHA/ACC/ACCP/ASPC/NLA/PCNA Guideline for the Management of Patients With Chronic Coronary Disease | 1 | title-page |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | topic | chronic coronary disease management | 1 | title-page |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | population | ? | 1 | front-matter |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | year | 2023 | 1 | title-page |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | title | AASLD IDSA Practice Guideline on Treatment of Chronic Hepatitis B | 1 | title-page |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | topic | chronic hepatitis B treatment | 1 | title-page |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | population | general | 1 | front-matter |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | year | 2026 | 1 | publication-line |
| IDSA | ajrccm_200_7_e45.pdf | title | Diagnosis and Treatment of Adults With Community-Acquired Pneumonia | 1 | title-page |
| IDSA | ajrccm_200_7_e45.pdf | topic | community-acquired pneumonia diagnosis and treatment | 1 | title-page |
| IDSA | ajrccm_200_7_e45.pdf | population | adult | 1 | front-matter |
| IDSA | ajrccm_200_7_e45.pdf | year | 2019 | 1 | publication-line |
| IDSA | amr-guidance-update.pdf | title | Infectious Diseases Society of America 2026 Guidance on the Treatment of Antimicrobial-Resistant Gram-Negative Infections | 1 | title-page |
| IDSA | amr-guidance-update.pdf | topic | antimicrobial-resistant gram-negative infection treatment | 1 | title-page |
| IDSA | amr-guidance-update.pdf | population | ? | 1 | front-matter |
| IDSA | amr-guidance-update.pdf | year | 2026 | 1 | title-page |
| IDSA | ciaa1215.pdf | title | Clinical Practice Guidelines by the Infectious Diseases Society of America, American Academy of Neurology, and American College of Rheumatology: 2020 Guidelines for the Prevention, Diagnosis and Treatment of Lyme Disease | 1 | title-page |
| IDSA | ciaa1215.pdf | topic | Lyme disease prevention, diagnosis, and treatment | 1 | title-page |
| IDSA | ciaa1215.pdf | population | general | 1 | front-matter |
| IDSA | ciaa1215.pdf | year | 2020 | 1 | title-page |
| IDSA | ciaa241.pdf | title | Treatment of Nontuberculous Mycobacterial Pulmonary Disease: An Official ATS/ERS/ESCMID/IDSA Clinical Practice Guideline | 1 | title-page |
| IDSA | ciaa241.pdf | topic | nontuberculous mycobacterial pulmonary disease treatment | 1 | title-page |
| IDSA | ciaa241.pdf | population | adult | 1 | front-matter |
| IDSA | ciaa241.pdf | year | 2020 | 1 | publication-line |
| IDSA | ciab275.pdf | title | Erratum to: SD1000: High Sustained Viral Response Rate in 1361 Patients With Hepatitis C Genotypes 1, 2, 3, and 4 Using a Low-cost Fixed-dose Combination Tablet of Generic Sofosbuvir and Daclatasvir: A Multicenter Phase III Clinical Trial; Corrigendum to: Clinical Practice Guidelines by the Infectious Diseases Society of America (IDSA): 2020 Guideline on Diagnosis and Management of Babesiosis | 1 | title-page |
| IDSA | ciab275.pdf | topic | hepatitis C trial and babesiosis guideline corrections | 1 | title-page |
| IDSA | ciab275.pdf | population | ? | 1 | front-matter |
| IDSA | ciab275.pdf | year | 2021 | 1 | publication-line |
| IDSA | ciab549.pdf | title | Clinical Practice Guideline by the Infectious Diseases Society of America and Society for Healthcare Epidemiology of America: 2021 Focused Update Guidelines on Management of Clostridioides difficile Infection in Adults | 1 | title-page |
| IDSA | ciab549.pdf | topic | Clostridioides difficile infection management | 1 | title-page |
| IDSA | ciab549.pdf | population | adult | 1 | front-matter |
| IDSA | ciab549.pdf | year | 2021 | 1 | title-page |
| IDSA | ciab953.pdf | title | Infectious Diseases Society of America Guidelines on Infection Prevention for Healthcare Personnel Caring for Patients With Suspected or Known COVID-19 (November 2021) | 1 | title-page |
| IDSA | ciab953.pdf | topic | COVID-19 infection prevention in healthcare settings | 1 | title-page |
| IDSA | ciab953.pdf | population | healthcare personnel | 1 | front-matter |
| IDSA | ciab953.pdf | year | 2021 | 1 | title-page |
| IDSA | ciac724.pdf | title | Infectious Diseases Society of America Guidelines on the Treatment and Management of Patients With COVID-19 (September 2022) | 1 | title-page |
| IDSA | ciac724.pdf | topic | COVID-19 treatment and management | 1 | title-page |
| IDSA | ciac724.pdf | population | general | 1 | front-matter |
| IDSA | ciac724.pdf | year | 2022 | 1 | title-page |
| IDSA | ciad319.pdf | title | Hepatitis C Guidance 2023 Update: American Association for the Study of Liver Diseases–Infectious Diseases Society of America Recommendations for Testing, Managing, and Treating Hepatitis C Virus Infection | 1 | title-page |
| IDSA | ciad319.pdf | topic | hepatitis C testing, management, and treatment | 1 | title-page |
| IDSA | ciad319.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| IDSA | ciad319.pdf | year | 2023 | 1 | title-page |
| IDSA | ciad527.pdf | title | IWGDF/IDSA Guidelines on the Diagnosis and Treatment of Diabetes-Related Foot Infections (IWGDF/IDSA 2023) | 1 | title-page |
| IDSA | ciad527.pdf | topic | diabetes-related foot infection diagnosis and treatment | 1 | title-page |
| IDSA | ciad527.pdf | population | general | 1 | front-matter |
| IDSA | ciad527.pdf | year | 2023 | 1 | title-page |
| IDSA | ciae104.pdf | title | Guide to Utilization of the Microbiology Laboratory for Diagnosis of Infectious Diseases: 2024 Update by the Infectious Diseases Society of America and the American Society for Microbiology | 1 | title-page |
| IDSA | ciae104.pdf | topic | microbiology laboratory use for infectious disease diagnosis | 1 | title-page |
| IDSA | ciae104.pdf | population | general | 1 | front-matter |
| IDSA | ciae104.pdf | year | 2024 | 1 | title-page |
| IDSA | ciae121.pdf | title | Infectious Diseases Society of America Guidelines on the Diagnosis of Coronavirus Disease 2019: Serologic Testing | 1 | title-page |
| IDSA | ciae121.pdf | topic | COVID-19 serologic testing | 1 | title-page |
| IDSA | ciae121.pdf | population | general | 1 | front-matter |
| IDSA | ciae121.pdf | year | 2024 | 1 | publication-line |
| IDSA | ciae479.pdf | title | Primary Care Guidance for Providers Who Care for Persons With Human Immunodeficiency Virus: 2024 Update by the HIV Medicine Association of the Infectious Diseases Society of America | 1 | title-page |
| IDSA | ciae479.pdf | topic | HIV primary care | 1 | title-page |
| IDSA | ciae479.pdf | population | general | 1 | front-matter |
| IDSA | ciae479.pdf | year | 2024 | 1 | title-page |
| IDSA | ciu296.pdf | title | Practice Guidelines for the Diagnosis and Management of Skin and Soft Tissue Infections: 2014 Update by the Infectious Diseases Society of America | 1 | title-page |
| IDSA | ciu296.pdf | topic | skin and soft tissue infection diagnosis and management | 1 | title-page |
| IDSA | ciu296.pdf | population | general | 1 | front-matter |
| IDSA | ciu296.pdf | year | 2014 | 1 | title-page |
| IDSA | ciu617.pdf | title | Clinical Practice Guideline for the Management of Chronic Kidney Disease in Patients Infected With HIV: 2014 Update by the HIV Medicine Association of the Infectious Diseases Society of America | 1 | title-page |
| IDSA | ciu617.pdf | topic | chronic kidney disease in HIV | 1 | title-page |
| IDSA | ciu617.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| IDSA | ciu617.pdf | year | 2014 | 1 | title-page |
| IDSA | civ482.pdf | title | 2015 Infectious Diseases Society of America Clinical Practice Guidelines for the Diagnosis and Treatment of Native Vertebral Osteomyelitis in Adults | 1 | title-page |
| IDSA | civ482.pdf | topic | native vertebral osteomyelitis diagnosis and treatment | 1 | title-page |
| IDSA | civ482.pdf | population | adult | 1 | front-matter |
| IDSA | civ482.pdf | year | 2015 | 1 | title-page |
| IDSA | ciw118.pdf | title | Implementing an Antibiotic Stewardship Program: Guidelines by the Infectious Diseases Society of America and the Society for Healthcare Epidemiology of America | 1 | title-page |
| IDSA | ciw118.pdf | topic | antibiotic stewardship program implementation | 1 | title-page |
| IDSA | ciw118.pdf | population | inpatient | 1 | front-matter |
| IDSA | ciw118.pdf | year | 2016 | 1 | publication-line |
| IDSA | ciw353.pdf | title | Management of Adults With Hospital-Acquired and Ventilator-Associated Pneumonia: 2016 Clinical Practice Guidelines by the Infectious Diseases Society of America and the American Thoracic Society | 1 | title-page |
| IDSA | ciw353.pdf | topic | hospital-acquired and ventilator-associated pneumonia | 1 | title-page |
| IDSA | ciw353.pdf | population | adult | 1 | front-matter |
| IDSA | ciw353.pdf | year | 2016 | 1 | title-page |
| IDSA | ciw360.pdf | title | 2016 Infectious Diseases Society of America Clinical Practice Guideline for the Treatment of Coccidioidomycosis | 1 | title-page |
| IDSA | ciw360.pdf | topic | coccidioidomycosis treatment | 1 | title-page |
| IDSA | ciw360.pdf | population | general | 1 | front-matter |
| IDSA | ciw360.pdf | year | 2016 | 1 | title-page |
| IDSA | ciw376.pdf | title | Official American Thoracic Society, Centers for Disease Control and Prevention, and Infectious Diseases Society of America Clinical Practice Guidelines: Treatment of Drug-Susceptible Tuberculosis | 1 | title-page |
| IDSA | ciw376.pdf | topic | drug-susceptible tuberculosis treatment | 1 | title-page |
| IDSA | ciw376.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| IDSA | ciw376.pdf | year | 2016 | 1 | publication-line |
| IDSA | ciw670.pdf | title | Diagnosis and Treatment of Leishmaniasis: Clinical Practice Guidelines by the Infectious Diseases Society of America and the American Society of Tropical Medicine and Hygiene | 1 | title-page |
| IDSA | ciw670.pdf | topic | leishmaniasis diagnosis and treatment | 1 | title-page |
| IDSA | ciw670.pdf | population | general | 1 | front-matter |
| IDSA | ciw670.pdf | year | 2016 | 1 | publication-line |
| IDSA | ciw694.pdf | title | Official American Thoracic Society, Infectious Diseases Society of America, and Centers for Disease Control and Prevention Clinical Practice Guidelines: Diagnosis of Tuberculosis in Adults and Children | 1 | title-page |
| IDSA | ciw694.pdf | topic | tuberculosis diagnosis | 1 | title-page |
| IDSA | ciw694.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| IDSA | ciw694.pdf | year | 2017 | 1 | publication-line |
| IDSA | ciw861.pdf | title | 2017 Infectious Diseases Society of America Clinical Practice Guidelines for Healthcare-Associated Ventriculitis and Meningitis | 1 | title-page |
| IDSA | ciw861.pdf | topic | healthcare-associated ventriculitis and meningitis | 1 | title-page |
| IDSA | ciw861.pdf | population | general | 1 | front-matter |
| IDSA | ciw861.pdf | year | 2017 | 1 | title-page |
| IDSA | cix1084.pdf | title | Diagnosis and Treatment of Neurocysticercosis: 2017 Clinical Practice Guidelines by the Infectious Diseases Society of America and the American Society of Tropical Medicine and Hygiene | 1 | title-page |
| IDSA | cix1084.pdf | topic | neurocysticercosis diagnosis and treatment | 1 | title-page |
| IDSA | cix1084.pdf | population | general | 1 | front-matter |
| IDSA | cix1084.pdf | year | 2017 | 1 | title-page |
| IDSA | cix1085.pdf | title | Clinical Practice Guidelines for Clostridium difficile Infection in Adults and Children: 2017 Update by the Infectious Diseases Society of America and Society for Healthcare Epidemiology of America | 1 | title-page |
| IDSA | cix1085.pdf | topic | Clostridium difficile infection diagnosis and management | 1 | title-page |
| IDSA | cix1085.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| IDSA | cix1085.pdf | year | 2017 | 1 | title-page |
| IDSA | cix636.pdf | title | 2017 HIVMA of IDSA Clinical Practice Guideline for the Management of Chronic Pain in Patients Living With HIV | 1 | title-page |
| IDSA | cix636.pdf | topic | chronic pain in people with HIV | 1 | title-page |
| IDSA | cix636.pdf | population | ? | 1 | front-matter |
| IDSA | cix636.pdf | year | 2017 | 1 | title-page |
| IDSA | cix669.pdf | title | 2017 Infectious Diseases Society of America Clinical Practice Guidelines for the Diagnosis and Management of Infectious Diarrhea | 1 | title-page |
| IDSA | cix669.pdf | topic | infectious diarrhea diagnosis and management | 1 | title-page |
| IDSA | cix669.pdf | population | general | 1 | front-matter |
| IDSA | cix669.pdf | year | 2017 | 1 | title-page |
| IDSA | ciy745.pdf | title | 2018 Infectious Diseases Society of America Clinical Practice Guideline for the Management of Outpatient Parenteral Antimicrobial Therapy | 1 | title-page |
| IDSA | ciy745.pdf | topic | outpatient parenteral antimicrobial therapy management | 1 | title-page |
| IDSA | ciy745.pdf | population | general | 1 | front-matter |
| IDSA | ciy745.pdf | year | 2018 | 1 | title-page |
| IDSA | ciy866.pdf | title | Clinical Practice Guidelines by the Infectious Diseases Society of America: 2018 Update on Diagnosis, Treatment, Chemoprophylaxis, and Institutional Outbreak Management of Seasonal Influenza | 1 | title-page |
| IDSA | ciy866.pdf | topic | seasonal influenza diagnosis, treatment, and outbreak management | 1 | title-page |
| IDSA | ciy866.pdf | population | general | 1 | front-matter |
| IDSA | ciy866.pdf | year | 2018 | 1 | title-page |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | title | 2025 Clinical Practice Guideline Update by the Infectious Diseases Society of America on Group A Streptococcal Pharyngitis: Risk Assessment Using Clinical Scoring Systems in Children and Adults | 1 | title-page |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | topic | group A streptococcal pharyngitis risk assessment | 1 | title-page |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | population | pediatric, adolescent, adult | 1 | front-matter |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | year | 2025 | 1 | title-page |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | title | Guidance for the Knowledge and Skills Required for Antimicrobial Stewardship Leaders: An Update From the Society for Healthcare Epidemiology of America, Infectious Diseases Society of America, Pediatric Infectious Diseases Society, and the Society of Infectious Diseases Pharmacists | 1 | title-page |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | topic | antimicrobial stewardship leadership competencies | 1 | title-page |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | population | antimicrobial stewardship leaders | 1 | front-matter |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | year | 2026 | 1 | publication-line |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | title | Infection Prevention and Control of Candida auris in Pediatric Settings | 1 | title-page |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | topic | Candida auris infection prevention and control | 1 | title-page |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | population | pediatric | 1 | front-matter |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | year | 2026 | 1 | publication-line |
| IDSA | maternal-immunizations.pdf | title | Maternal Immunizations | 1 | title-page |
| IDSA | maternal-immunizations.pdf | topic | maternal immunization | 1 | title-page |
| IDSA | maternal-immunizations.pdf | population | pregnancy, postpartum | 1 | front-matter |
| IDSA | maternal-immunizations.pdf | year | 2026 | 1 | title-page |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | title | Consensus Guidance for Beta-Lactam Antibiotic Dose Individualization in Acutely Ill Patients | 1 | title-page |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | topic | beta-lactam antibiotic dose individualization | 1 | title-page |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | population | critically ill | 1 | front-matter |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | year | 2026 | 1 | publication-line |
| IDSA | piab027.pdf | title | Clinical Practice Guideline by the Pediatric Infectious Diseases Society and the Infectious Diseases Society of America: 2021 Guideline on Diagnosis and Management of Acute Hematogenous Osteomyelitis in Pediatrics | 1 | title-page |
| IDSA | piab027.pdf | topic | acute hematogenous osteomyelitis diagnosis and management | 1 | title-page |
| IDSA | piab027.pdf | population | pediatric | 1 | front-matter |
| IDSA | piab027.pdf | year | 2021 | 1 | title-page |
| IDSA | piad089.pdf | title | Clinical Practice Guideline by the Pediatric Infectious Diseases Society and the Infectious Diseases Society of America: 2023 Guideline on Diagnosis and Management of Acute Bacterial Arthritis in Pediatrics | 1 | title-page |
| IDSA | piad089.pdf | topic | acute bacterial arthritis diagnosis and management | 1 | title-page |
| IDSA | piad089.pdf | population | pediatric | 1 | front-matter |
| IDSA | piad089.pdf | year | 2023 | 1 | title-page |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | title | Society of Critical Care Medicine and the Infectious Diseases Society of America Guidelines for Evaluating New Fever in Adult Patients in the ICU | 1 | title-page |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | topic | new fever evaluation in intensive care | 1 | title-page |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | population | adult, critically ill | 1 | front-matter |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | year | 2023 | 1 | publication-line |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | title | Surviving Sepsis Campaign International Guidelines for the Management of Sepsis and Septic Shock in Children 2026 | 1 | title-page |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | topic | sepsis and septic shock management | 1 | title-page |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | population | pediatric, adolescent | 1 | front-matter |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | year | 2026 | 1 | title-page |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | title | Surviving Sepsis Campaign: International Guidelines for Management of Sepsis and Septic Shock 2026 | 1 | title-page |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | topic | sepsis and septic shock management | 1 | title-page |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | population | adult | 1 | front-matter |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | year | 2026 | 1 | title-page |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | title | Antimicrobial Prophylaxis for Adult Patients With Cancer-Related Immunosuppression: ASCO and IDSA Clinical Practice Guideline Update Summary | 1 | title-page |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | topic | antimicrobial prophylaxis for cancer-related immunosuppression | 1 | title-page |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | population | adult | 1 | front-matter |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | year | 2018 | 1 | publication-line |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | title | KDIGO 2024 Clinical Practice Guideline for the Management of Lupus Nephritis | 2 | title-page |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | topic | lupus nephritis management | 2 | title-page |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | population | ? | 3 | front-matter |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | year | 2024 | 2 | title-page |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | title | KDIGO Clinical Practice Guideline for the Care of Kidney Transplant Recipients | 14 | front-matter |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | topic | kidney transplant recipient care | 14 | front-matter |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | population | pediatric, adolescent, adult | 14 | front-matter |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | year | 2009 | 14 | publication-line |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | title | KDIGO Clinical Practice Guideline for Lipid Management in Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | topic | lipid management in chronic kidney disease | 1 | title-page |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | population | pediatric, adolescent, adult | 3 | front-matter |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | year | 2013 | 1 | publication-line |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | title | KDIGO 2017 Clinical Practice Guideline Update for the Diagnosis, Evaluation, Prevention, and Treatment of Chronic Kidney Disease–Mineral and Bone Disorder | 1 | title-page |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | topic | chronic kidney disease–mineral and bone disorder | 1 | title-page |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | population | ? | 3 | front-matter |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | year | 2017 | 1 | title-page |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | title | KDIGO Clinical Practice Guideline on the Evaluation and Care of Living Kidney Donors | 1 | title-page |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | topic | living kidney donor evaluation and care | 1 | title-page |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | population | ? | 1 | front-matter |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | year | 2017 | 1 | publication-line |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | title | KDIGO Clinical Practice Guideline on the Evaluation and Management of Candidates for Kidney Transplantation | 1 | title-page |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | topic | kidney transplant candidate evaluation and management | 1 | title-page |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | population | pediatric, adolescent, adult | 2 | front-matter |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | year | 2020 | 1 | publication-line |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | title | KDIGO 2021 Clinical Practice Guideline for the Management of Blood Pressure in Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | topic | blood pressure management in chronic kidney disease | 1 | title-page |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | population | ? | 1 | front-matter |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | year | 2021 | 1 | title-page |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | title | KDIGO 2021 Clinical Practice Guideline for the Management of Glomerular Diseases | 1 | title-page |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | topic | glomerular disease management | 1 | title-page |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | population | ? | 1 | front-matter |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | year | 2021 | 1 | title-page |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | title | KDIGO 2022 Clinical Practice Guideline for Diabetes Management in Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | topic | diabetes management in chronic kidney disease | 1 | title-page |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | population | ? | 3 | front-matter |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | year | 2022 | 1 | title-page |
| KDIGO | KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf | title | KDIGO 2022 Clinical Practice Guideline for the Prevention, Diagnosis, Evaluation, and Treatment of Hepatitis C in Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf | topic | hepatitis C in chronic kidney disease | 1 | title-page |
| KDIGO | KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf | population | ? | 3 | front-matter |
| KDIGO | KDIGO-2022-Hepatitis-C-in-CKD-Guideline.pdf | year | 2022 | 1 | title-page |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | title | KDIGO 2024 Clinical Practice Guideline for the Management of Antineutrophil Cytoplasmic Antibody–Associated Vasculitis | 1 | title-page |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | topic | ANCA-associated vasculitis management | 1 | title-page |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | population | ? | 3 | front-matter |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | year | 2024 | 1 | title-page |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | title | KDIGO 2024 Clinical Practice Guideline for the Evaluation and Management of Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | topic | chronic kidney disease evaluation and management | 1 | title-page |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | population | general | 3 | front-matter |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | year | 2024 | 1 | title-page |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | title | KDIGO 2025 Clinical Practice Guideline for the Evaluation, Management, and Treatment of Autosomal Dominant Polycystic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | topic | autosomal dominant polycystic kidney disease | 1 | title-page |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | population | pediatric, adolescent, adult | 3 | front-matter |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | year | 2025 | 1 | title-page |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | title | KDIGO 2025 Clinical Practice Guideline for the Management of Nephrotic Syndrome in Children | 1 | title-page |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | topic | nephrotic syndrome management | 1 | title-page |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | population | pediatric | 1 | title-page |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | year | 2025 | 1 | title-page |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | title | KDIGO 2025 Clinical Practice Guideline for the Management of Immunoglobulin A Nephropathy and Immunoglobulin A Vasculitis | 1 | title-page |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | topic | immunoglobulin A nephropathy and vasculitis management | 1 | title-page |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | population | ? | 2 | front-matter |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | year | 2025 | 1 | title-page |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | title | KDIGO 2026 Clinical Practice Guideline for Acute Kidney Injury and Acute Kidney Disease: Public Review Draft | 1 | title-page |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | topic | acute kidney injury and acute kidney disease | 1 | title-page |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | population | pediatric, adolescent, adult | 3 | front-matter |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | year | 2026 | 1 | title-page |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | title | KDIGO 2026 Clinical Practice Guideline for the Management of Anemia in Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | topic | anemia management in chronic kidney disease | 1 | title-page |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | population | general | 2 | front-matter |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | year | 2026 | 1 | title-page |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | title | Scope of Work: KDIGO Clinical Practice Guideline for the Management of Heart Failure in Chronic Kidney Disease | 1 | title-page |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | topic | heart failure management in chronic kidney disease | 1 | title-page |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | population | general | 2 | front-matter |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | year | ? | 1 | front-matter |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | title | Screening for Abdominal Aortic Aneurysm | 1 | title-page |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | topic | abdominal aortic aneurysm screening | 1 | title-page |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | population | adult | 1 | population-statement |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | year | 2019 | 1 | publication-line |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | title | Behavioral Weight Loss Interventions to Prevent Obesity-Related Morbidity and Mortality in Adults | 1 | title-page |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | topic | behavioral weight loss interventions for obesity | 1 | title-page |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | afib-screening-final-recommendation-statement.pdf | title | Screening for Atrial Fibrillation | 1 | title-page |
| USPSTF | afib-screening-final-recommendation-statement.pdf | topic | atrial fibrillation screening | 1 | title-page |
| USPSTF | afib-screening-final-recommendation-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | afib-screening-final-recommendation-statement.pdf | year | 2022 | 1 | publication-line |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | title | Screening for Anxiety Disorders in Adults | 1 | title-page |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | topic | anxiety disorder screening | 1 | title-page |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | title | Aspirin Use to Prevent Preeclampsia and Related Morbidity and Mortality | 1 | title-page |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | topic | aspirin for preeclampsia prevention | 1 | title-page |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | year | 2021 | 1 | publication-line |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | title | Aspirin Use to Prevent Cardiovascular Disease | 1 | title-page |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | topic | aspirin for primary cardiovascular disease prevention | 1 | title-page |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | population | adult | 1 | population-statement |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | year | 2022 | 1 | publication-line |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | title | Screening for Asymptomatic Bacteriuria in Adults | 1 | title-page |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | topic | asymptomatic bacteriuria screening | 1 | title-page |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | year | 2019 | 1 | publication-line |
| USPSTF | autismfinalrs.pdf | title | Screening for Autism Spectrum Disorder in Young Children | 1 | title-page |
| USPSTF | autismfinalrs.pdf | topic | autism spectrum disorder screening | 1 | title-page |
| USPSTF | autismfinalrs.pdf | population | pediatric | 1 | recommendation-statement |
| USPSTF | autismfinalrs.pdf | year | 2016 | 1 | publication-line |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | title | Screening for Bacterial Vaginosis in Pregnant Persons to Prevent Preterm Delivery | 1 | title-page |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | topic | bacterial vaginosis screening to prevent preterm delivery | 1 | title-page |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | year | 2020 | 1 | publication-line |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | title | Behavioral Counseling Interventions to Promote a Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults Without Cardiovascular Disease Risk Factors | 1 | title-page |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | topic | healthy diet and physical activity counseling for cardiovascular disease prevention | 1 | title-page |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | population | adult | 1 | population-statement |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | year | 2022 | 1 | publication-line |
| USPSTF | bladcanrs.pdf | title | Screening for Bladder Cancer | 1 | title-page |
| USPSTF | bladcanrs.pdf | topic | bladder cancer screening | 1 | title-page |
| USPSTF | bladcanrs.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | bladcanrs.pdf | year | 2011 | 1 | publication-line |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | title | Risk Assessment, Genetic Counseling, and Genetic Testing for BRCA-Related Cancer | 1 | title-page |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | topic | BRCA-related cancer risk assessment, counseling, and testing | 1 | title-page |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | population | adult | 1 | evidence-review |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | year | 2019 | 1 | publication-line |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | title | Medication Use to Reduce Risk of Breast Cancer | 1 | title-page |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | topic | medication to reduce breast cancer risk | 1 | title-page |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | population | adult | 1 | applicability-statement |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | year | 2019 | 1 | publication-line |
| USPSTF | breast-cancer-screening-final-rec.pdf | title | Screening for Breast Cancer | 1 | title-page |
| USPSTF | breast-cancer-screening-final-rec.pdf | topic | breast cancer screening | 1 | title-page |
| USPSTF | breast-cancer-screening-final-rec.pdf | population | adult | 1 | population-statement |
| USPSTF | breast-cancer-screening-final-rec.pdf | year | 2024 | 1 | publication-line |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | title | Primary Care Behavioral Counseling Interventions to Support Breastfeeding | 1 | title-page |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | topic | behavioral counseling to support breastfeeding | 1 | title-page |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | population | pediatric, adolescent, adult | 1 | population-statement |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | year | 2025 | 1 | publication-line |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | title | Screening for Asymptomatic Carotid Artery Stenosis | 1 | title-page |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | topic | asymptomatic carotid artery stenosis screening | 1 | title-page |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | celiacscreening-recstatement.pdf | title | Screening for Celiac Disease | 1 | title-page |
| USPSTF | celiacscreening-recstatement.pdf | topic | celiac disease screening | 1 | title-page |
| USPSTF | celiacscreening-recstatement.pdf | population | pediatric, adolescent, adult | 1 | recommendation-statement |
| USPSTF | celiacscreening-recstatement.pdf | year | 2017 | 1 | publication-line |
| USPSTF | cervical-cancer-final-rec-statement.pdf | title | Screening for Cervical Cancer | 1 | title-page |
| USPSTF | cervical-cancer-final-rec-statement.pdf | topic | cervical cancer screening | 1 | title-page |
| USPSTF | cervical-cancer-final-rec-statement.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | cervical-cancer-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | title | Primary Care Interventions to Prevent Child Maltreatment | 1 | title-page |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | topic | primary care interventions to prevent child maltreatment | 1 | title-page |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | year | 2024 | 1 | publication-line |
| USPSTF | child-vision-recstatement.pdf | title | Vision Screening in Children Aged 6 Months to 5 Years | 1 | title-page |
| USPSTF | child-vision-recstatement.pdf | topic | vision screening in young children | 1 | title-page |
| USPSTF | child-vision-recstatement.pdf | population | pediatric | 1 | recommendation-statement |
| USPSTF | child-vision-recstatement.pdf | year | 2017 | 1 | publication-line |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | title | Screening for Chlamydia and Gonorrhea | 1 | title-page |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | topic | chlamydia and gonorrhea screening | 1 | title-page |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | title | Screening for Cognitive Impairment in Older Adults | 1 | title-page |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | topic | cognitive impairment screening | 1 | title-page |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | year | 2020 | 1 | publication-line |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | title | Screening for Colorectal Cancer | 1 | title-page |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | topic | colorectal cancer screening | 1 | title-page |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | population | adult | 1 | population-statement |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | year | 2021 | 1 | publication-line |
| USPSTF | copd-screening-final-recommendation.pdf | title | Screening for Chronic Obstructive Pulmonary Disease | 1 | title-page |
| USPSTF | copd-screening-final-recommendation.pdf | topic | chronic obstructive pulmonary disease screening | 1 | title-page |
| USPSTF | copd-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | copd-screening-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | title | Risk Assessment for Cardiovascular Disease With Nontraditional Risk Factors | 1 | title-page |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | topic | cardiovascular disease risk assessment with nontraditional risk factors | 1 | title-page |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | population | adult | 1 | evidence-review |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | title | Screening for Cardiovascular Disease Risk With Electrocardiography | 1 | title-page |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | topic | cardiovascular disease risk screening with electrocardiography | 1 | title-page |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | title | Screening and Interventions to Prevent Dental Caries in Children Younger Than 5 Years | 1 | title-page |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | topic | dental caries screening and prevention | 1 | title-page |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | population | pediatric | 1 | population-statement |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | depression-suicide-risk-adults-rs.pdf | title | Screening for Depression and Suicide Risk in Adults | 1 | title-page |
| USPSTF | depression-suicide-risk-adults-rs.pdf | topic | depression and suicide risk screening | 1 | title-page |
| USPSTF | depression-suicide-risk-adults-rs.pdf | population | adult | 1 | population-statement |
| USPSTF | depression-suicide-risk-adults-rs.pdf | year | 2023 | 1 | publication-line |
| USPSTF | diabetes-child-final-recommendation.pdf | title | Screening for Prediabetes and Type 2 Diabetes in Children and Adolescents | 1 | title-page |
| USPSTF | diabetes-child-final-recommendation.pdf | topic | prediabetes and type 2 diabetes screening | 1 | title-page |
| USPSTF | diabetes-child-final-recommendation.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | diabetes-child-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | title | Screening for Eating Disorders in Adolescents and Adults | 1 | title-page |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | topic | eating disorder screening | 1 | title-page |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | title | Interventions to Prevent Falls in Community-Dwelling Older Adults | 1 | title-page |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | topic | fall prevention interventions | 1 | title-page |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | year | 2024 | 1 | publication-line |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | title | Folic Acid Supplementation to Prevent Neural Tube Defects | 1 | title-page |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | topic | folic acid supplementation to prevent neural tube defects | 1 | title-page |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | year | 2023 | 1 | publication-line |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | title | Screening for Food Insecurity | 1 | title-page |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | topic | food insecurity screening | 1 | title-page |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | population | pediatric, adolescent, adult | 1 | population-statement |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | year | 2025 | 1 | publication-line |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | title | Serologic Screening for Genital Herpes Infection | 1 | title-page |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | topic | genital herpes serologic screening | 1 | title-page |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | title | Screening for Gestational Diabetes | 1 | title-page |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | topic | gestational diabetes screening | 1 | title-page |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | year | 2021 | 1 | publication-line |
| USPSTF | glaucoma-screening-final-recommendation.pdf | title | Screening for Primary Open-Angle Glaucoma | 1 | title-page |
| USPSTF | glaucoma-screening-final-recommendation.pdf | topic | primary open-angle glaucoma screening | 1 | title-page |
| USPSTF | glaucoma-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | glaucoma-screening-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | GON-final-recommendation.pdf | title | Ocular Prophylaxis for Gonococcal Ophthalmia Neonatorum | 1 | title-page |
| USPSTF | GON-final-recommendation.pdf | topic | gonococcal ophthalmia neonatorum prophylaxis | 1 | title-page |
| USPSTF | GON-final-recommendation.pdf | population | pediatric | 1 | recommendation-statement |
| USPSTF | GON-final-recommendation.pdf | year | 2019 | 1 | publication-line |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | title | Behavioral Counseling Interventions to Promote a Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults With Cardiovascular Risk Factors | 1 | title-page |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | topic | healthy diet and physical activity counseling for cardiovascular disease prevention | 1 | title-page |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | population | adult | 1 | population-statement |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | year | 2020 | 1 | publication-line |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | title | Behavioral Counseling Interventions for Healthy Weight and Weight Gain in Pregnancy | 1 | title-page |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | topic | healthy weight and weight gain counseling in pregnancy | 1 | title-page |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | title | Screening for Hearing Loss in Older Adults | 1 | title-page |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | topic | hearing loss screening | 1 | title-page |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | title | Screening for Hepatitis B Virus Infection in Pregnant Women | 1 | title-page |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | topic | hepatitis B screening in pregnancy | 1 | title-page |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | population | adult, pregnant | 1 | recommendation-statement |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | year | 2019 | 1 | publication-line |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | title | Screening for Hepatitis B Virus Infection in Adolescents and Adults | 1 | title-page |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | topic | hepatitis B screening | 1 | title-page |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | year | 2020 | 1 | publication-line |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | title | Screening for Hepatitis C Virus Infection in Adolescents and Adults | 1 | title-page |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | topic | hepatitis C screening | 1 | title-page |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | year | 2020 | 1 | publication-line |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | title | Screening for High Blood Pressure in Children and Adolescents | 1 | title-page |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | topic | high blood pressure screening | 1 | title-page |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | year | 2020 | 1 | publication-line |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | title | Interventions for High Body Mass Index in Children and Adolescents | 1 | title-page |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | topic | high body mass index interventions | 1 | title-page |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | year | 2024 | 1 | publication-line |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | title | Preexposure Prophylaxis to Prevent Acquisition of HIV | 1 | title-page |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | topic | HIV preexposure prophylaxis | 1 | title-page |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | hiv-screening-final-rec-statement.pdf | title | Screening for HIV Infection | 1 | title-page |
| USPSTF | hiv-screening-final-rec-statement.pdf | topic | HIV screening | 1 | title-page |
| USPSTF | hiv-screening-final-rec-statement.pdf | population | adolescent, adult, pregnant | 1 | recommendation-statement |
| USPSTF | hiv-screening-final-rec-statement.pdf | year | 2019 | 1 | publication-line |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | title | Hormone Therapy for the Primary Prevention of Chronic Conditions in Postmenopausal Persons | 1 | title-page |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | topic | hormone therapy for primary prevention in postmenopausal persons | 1 | title-page |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | title | Screening for Hypertension in Adults | 1 | title-page |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | topic | hypertension screening | 1 | title-page |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | title | Screening for Hypertensive Disorders of Pregnancy | 1 | title-page |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | topic | hypertensive disorder screening in pregnancy | 1 | title-page |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | idachildrenfinal.pdf | title | Screening for Iron Deficiency Anemia in Young Children | 1 | title-page |
| USPSTF | idachildrenfinal.pdf | topic | iron deficiency anemia screening in young children | 1 | title-page |
| USPSTF | idachildrenfinal.pdf | population | pediatric | 1 | recommendation-statement |
| USPSTF | idachildrenfinal.pdf | year | 2015 | 1 | publication-line |
| USPSTF | illicit-drug-use-children-final-rec.pdf | title | Primary Care–Based Interventions to Prevent Illicit Drug Use in Children, Adolescents, and Young Adults | 1 | title-page |
| USPSTF | illicit-drug-use-children-final-rec.pdf | topic | primary care interventions to prevent illicit drug use | 1 | title-page |
| USPSTF | illicit-drug-use-children-final-rec.pdf | population | pediatric, adolescent, adult | 1 | population-statement |
| USPSTF | illicit-drug-use-children-final-rec.pdf | year | 2020 | 1 | publication-line |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | title | Screening for Impaired Visual Acuity in Older Adults | 1 | title-page |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | topic | impaired visual acuity screening | 1 | title-page |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | ipv-screening-final-rec-statement.pdf | title | Screening for Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults | 1 | title-page |
| USPSTF | ipv-screening-final-rec-statement.pdf | topic | intimate partner violence and caregiver abuse screening | 1 | title-page |
| USPSTF | ipv-screening-final-rec-statement.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | ipv-screening-final-rec-statement.pdf | year | 2025 | 1 | publication-line |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | title | Screening and Supplementation for Iron Deficiency and Iron Deficiency Anemia During Pregnancy | 1 | title-page |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | topic | iron deficiency and iron deficiency anemia in pregnancy | 1 | title-page |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | population | adolescent, adult, pregnant | 1 | population-statement |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | year | 2024 | 1 | publication-line |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | title | Screening for Latent Tuberculosis Infection in Adults | 1 | title-page |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | topic | latent tuberculosis infection screening | 1 | title-page |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | year | 2023 | 1 | publication-line |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | title | Screening for Lipid Disorders in Children and Adolescents | 1 | title-page |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | topic | lipid disorder screening | 1 | title-page |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | year | 2023 | 1 | publication-line |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | title | Screening for Lung Cancer | 1 | title-page |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | topic | lung cancer screening | 1 | title-page |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | year | 2021 | 1 | publication-line |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | title | Vitamin, Mineral, and Multivitamin Supplementation to Prevent Cardiovascular Disease and Cancer | 1 | title-page |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | topic | vitamin and mineral supplementation for cardiovascular disease and cancer prevention | 1 | title-page |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | title | Screening and Preventive Interventions for Oral Health in Adults | 1 | title-page |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | topic | oral health screening and preventive interventions | 1 | title-page |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | oral-health-children-final-recommendation.pdf | title | Screening and Preventive Interventions for Oral Health in Children and Adolescents Aged 5 to 17 Years | 1 | title-page |
| USPSTF | oral-health-children-final-recommendation.pdf | topic | oral health screening and preventive interventions | 1 | title-page |
| USPSTF | oral-health-children-final-recommendation.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | oral-health-children-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | oralcancerfinalrs.pdf | title | Screening for Oral Cancer | 1 | title-page |
| USPSTF | oralcancerfinalrs.pdf | topic | oral cancer screening | 1 | title-page |
| USPSTF | oralcancerfinalrs.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | oralcancerfinalrs.pdf | year | 2014 | 1 | publication-line |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | title | Screening for Osteoporosis to Prevent Fractures | 1 | title-page |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | topic | osteoporosis screening to prevent fractures | 1 | title-page |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | year | 2025 | 1 | publication-line |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | title | Screening for Ovarian Cancer | 1 | title-page |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | topic | ovarian cancer screening | 1 | title-page |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | title | Screening for Peripheral Artery Disease and Cardiovascular Disease Risk Assessment With the Ankle-Brachial Index | 1 | title-page |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | topic | peripheral artery disease and cardiovascular disease risk screening with ankle-brachial index | 1 | title-page |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | title | Screening for Pancreatic Cancer | 1 | title-page |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | topic | pancreatic cancer screening | 1 | title-page |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | year | 2019 | 1 | publication-line |
| USPSTF | perinatal-depression-final-rec-statement.pdf | title | Interventions to Prevent Perinatal Depression | 1 | title-page |
| USPSTF | perinatal-depression-final-rec-statement.pdf | topic | perinatal depression prevention interventions | 1 | title-page |
| USPSTF | perinatal-depression-final-rec-statement.pdf | population | adult, pregnant, postpartum | 1 | recommendation-statement |
| USPSTF | perinatal-depression-final-rec-statement.pdf | year | 2019 | 1 | publication-line |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | title | Screening for Prediabetes and Type 2 Diabetes | 1 | title-page |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | topic | prediabetes and type 2 diabetes screening | 1 | title-page |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | year | 2021 | 1 | publication-line |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | title | Screening for Prostate Cancer | 1 | title-page |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | topic | prostate cancer screening | 1 | title-page |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | year | 2018 | 1 | publication-line |
| USPSTF | rhrs.pdf | title | Screening for Rh (D) Incompatibility | 3 | section-heading |
| USPSTF | rhrs.pdf | topic | Rh (D) incompatibility screening | 3 | section-heading |
| USPSTF | rhrs.pdf | population | adult, pregnant | 1 | recommendation-statement |
| USPSTF | rhrs.pdf | year | 2004 | 3 | publication-line |
| USPSTF | scoliosis-final-rec-statement.pdf | title | Screening for Adolescent Idiopathic Scoliosis | 1 | title-page |
| USPSTF | scoliosis-final-rec-statement.pdf | topic | adolescent idiopathic scoliosis screening | 1 | title-page |
| USPSTF | scoliosis-final-rec-statement.pdf | population | pediatric, adolescent | 1 | recommendation-statement |
| USPSTF | scoliosis-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | title | Screening for Thyroid Cancer | 1 | title-page |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | topic | thyroid cancer screening | 1 | title-page |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | year | 2017 | 1 | publication-line |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | title | Screening for Thyroid Dysfunction | 1 | title-page |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | topic | thyroid dysfunction screening | 1 | title-page |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | population | adult | 1 | recommendation-statement |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | year | 2015 | 1 | publication-line |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | title | Screening for Anxiety in Children and Adolescents | 1 | title-page |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | topic | anxiety screening | 1 | title-page |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | title | Screening for Depression and Suicide Risk in Children and Adolescents | 1 | title-page |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | topic | depression and suicide risk screening | 1 | title-page |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | title | Behavioral Counseling to Prevent Skin Cancer | 1 | title-page |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | topic | behavioral counseling to prevent skin cancer | 1 | title-page |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | population | pediatric, adolescent, adult | 1 | recommendation-statement |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | year | 2018 | 1 | publication-line |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | title | Screening for Skin Cancer | 1 | title-page |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | topic | skin cancer screening | 1 | title-page |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | year | 2023 | 1 | publication-line |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | title | Screening for Obstructive Sleep Apnea in Adults | 1 | title-page |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | topic | obstructive sleep apnea screening | 1 | title-page |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | year | 2022 | 1 | publication-line |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | title | Screening for Speech and Language Delay and Disorders in Children | 1 | title-page |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | topic | speech and language delay and disorder screening | 1 | title-page |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | population | pediatric | 1 | population-statement |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | year | 2024 | 1 | publication-line |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | title | Statin Use for the Primary Prevention of Cardiovascular Disease in Adults | 1 | title-page |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | topic | statin use for primary cardiovascular disease prevention | 1 | title-page |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | population | adult | 1 | population-statement |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | year | 2022 | 1 | publication-line |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | title | Behavioral Counseling Interventions to Prevent Sexually Transmitted Infections | 1 | title-page |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | topic | behavioral counseling to prevent sexually transmitted infections | 1 | title-page |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | year | 2020 | 1 | publication-line |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | title | Screening for Syphilis Infection in Nonpregnant Adolescents and Adults | 1 | title-page |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | topic | syphilis screening in nonpregnant persons | 1 | title-page |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | year | 2022 | 1 | publication-line |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | title | Screening for Syphilis Infection During Pregnancy | 1 | title-page |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | topic | syphilis screening during pregnancy | 1 | title-page |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | population | adolescent, adult, pregnant | 1 | population-statement |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | year | 2025 | 1 | publication-line |
| USPSTF | testicuprs.pdf | title | Screening for Testicular Cancer | 1 | title-page |
| USPSTF | testicuprs.pdf | topic | testicular cancer screening | 1 | title-page |
| USPSTF | testicuprs.pdf | population | adolescent, adult | 1 | recommendation-statement |
| USPSTF | testicuprs.pdf | year | 2011 | 1 | publication-line |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | title | Interventions for Tobacco Smoking Cessation in Adults, Including Pregnant Persons | 1 | title-page |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | topic | tobacco smoking cessation interventions | 1 | title-page |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | population | adult, pregnant | 1 | population-statement |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | year | 2021 | 1 | publication-line |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | title | Primary Care Interventions for Prevention and Cessation of Tobacco Use in Children and Adolescents | 1 | title-page |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | topic | tobacco use prevention and cessation interventions | 1 | title-page |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | population | pediatric, adolescent | 1 | population-statement |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | year | 2020 | 1 | publication-line |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | title | Screening and Behavioral Counseling Interventions to Reduce Unhealthy Alcohol Use in Adolescents and Adults | 1 | title-page |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | topic | unhealthy alcohol use screening and behavioral counseling | 1 | title-page |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | population | adolescent, adult | 1 | recommendation-statement |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | year | 2018 | 1 | publication-line |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | title | Screening for Unhealthy Drug Use | 1 | title-page |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | topic | unhealthy drug use screening | 1 | title-page |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | population | adolescent, adult | 1 | population-statement |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | year | 2020 | 1 | publication-line |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | title | Screening for Vitamin D Deficiency in Adults | 1 | title-page |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | topic | vitamin D deficiency screening | 1 | title-page |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | population | adult | 1 | population-statement |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | year | 2021 | 1 | publication-line |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | title | Vitamin D, Calcium, or Combined Supplementation for the Primary Prevention of Fractures in Community-Dwelling Adults | 1 | title-page |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | topic | vitamin D and calcium supplementation for fracture prevention | 1 | title-page |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | population | adult | 1 | evidence-review |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | year | 2018 | 1 | publication-line |

## Clinician rulings

| society | filename | column | confirmed_value | confirmed_date | rationale |
| --- | --- | --- | --- | --- | --- |
| ACIP | Recommended Vaccinations for Adults  Vaccines  Immunizations  CDC.pdf | title | Recommended Vaccinations for Adults, Vaccines & Immunizations, CDC | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | title | Recommended Vaccines for Older Children, Vaccines & Immunizations, CDC | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| ACIP | Recommended Vaccines for Older Children  Vaccines  Immunizations  CDC.pdf | topic | childhood and adolescent immunization schedule | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| ACIP | Recommended Vaccines for Young Children  Vaccines  Immunizations  CDC.pdf | title | Recommended Vaccines for Young Children, Vaccines & Immunizations, CDC | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| ADA | standards-of-care-2026.pdf | title | Standards of Care in Diabetes-2026 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| ADA | standards-of-care-2026.pdf | topic | diabetes mellitus | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| CDC | CDC Clinical Practice Guideline for Prescribing Opioids for Pain — United States, 2022 MMWR.pdf | title | CDC Clinical Practice Guideline for Prescribing Opioids for Pain - United States, 2022 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | title | Summary Guide for Asthma Management and Prevention: For Adults, Adolescents and Children 6-11 Years | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| GINA | GINA-Summary-Guide-2026-WEB-WMS.pdf | topic | asthma | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | title | Global Strategy for the Diagnosis, Management, and Prevention of Chronic Obstructive Pulmonary Disease: 2026 Report | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| GOLD | GOLD-REPORT-2026-v1.3-8Dec2025_WMV2.pdf | topic | chronic obstructive pulmonary disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | topic | dyslipidemia | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | blumenthal-et-al-2026-2026-acc-aha-aacvpr-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | topic | stroke primary prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | bushnell-et-al-2024-2024-guideline-for-the-primary-prevention-of-stroke-a-guideline-from-the-american-heart-association.pdf | population | adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | creager-et-al-2026-2026-aha-acc-accp-acep-chest-scai-shm-sir-svm-svn-guideline-for-the-evaluation-and-management-of.pdf | topic | acute pulmonary embolism | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | gornik-et-al-2024-2024-acc-aha-aacvpr-apma-abc-scai-svm-svn-svs-sir-vess-guideline-for-the-management-of-lower.pdf | topic | lower extremity peripheral artery disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | topic | blood cholesterol | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | grundy-et-al-2018-2018-aha-acc-aacvpr-aapa-abc-acpm-ada-ags-apha-aspc-nla-pcna-guideline-on-the-management-of-blood.pdf | population | adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | gulati-et-al-2021-2021-aha-acc-ase-chest-saem-scct-scmr-guideline-for-the-evaluation-and-diagnosis-of-chest-pain-a.pdf | topic | chest pain evaluation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | gurvitz-et-al-2025-2025-acc-aha-hrs-isachd-scai-guideline-for-the-management-of-adults-with-congenital-heart-disease-a.pdf | topic | congenital heart disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | heidenreich-et-al-2022-2022-aha-acc-hfsa-guideline-for-the-management-of-heart-failure-a-report-of-the-american-college.pdf | topic | heart failure | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | isselbacher-et-al-2022-2022-acc-aha-guideline-for-the-diagnosis-and-management-of-aortic-disease-a-report-of-the.pdf | topic | aortic disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | joglar-et-al-2023-2023-acc-aha-accp-hrs-guideline-for-the-diagnosis-and-management-of-atrial-fibrillation-a-report-of.pdf | topic | atrial fibrillation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | jones-et-al-2025-2025-aha-acc-aanp-aapa-abc-accp-acpm-ags-ama-aspc-nma-pcna-sgim-guideline-for-the-prevention-detection.pdf | topic | high blood pressure | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | topic | cardiac arrest and life-threatening toxicity due to poisoning | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | lavonas-et-al-2023-2023-american-heart-association-focused-update-on-the-management-of-patients-with-cardiac-arrest-or.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | ndumele-et-al-2026-2026-aha-acc-ada-asn-guideline-for-the-prevention-detection-evaluation-and-management-of.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | topic | hypertrophic cardiomyopathy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy (1).pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | topic | hypertrophic cardiomyopathy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | ommen-et-al-2020-2020-aha-acc-guideline-for-the-diagnosis-and-treatment-of-patients-with-hypertrophic-cardiomyopathy.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | ommen-et-al-2024-2024-aha-acc-amssm-hrs-paces-scmr-guideline-for-the-management-of-hypertrophic-cardiomyopathy-a-report.pdf | topic | hypertrophic cardiomyopathy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | otto-et-al-2020-2020-acc-aha-guideline-for-the-management-of-patients-with-valvular-heart-disease-a-report-of-the.pdf | topic | valvular heart disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | powers-et-al-2019-guidelines-for-the-early-management-of-patients-with-acute-ischemic-stroke-2019-update-to-the-2018.pdf | topic | acute ischemic stroke, early management | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | topic | acute ischemic stroke, early management | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | prabhakaran-et-al-2026-2026-guideline-for-the-early-management-of-patients-with-acute-ischemic-stroke-a-guideline-from.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | rao-et-al-2025-2025-acc-aha-acep-naemsp-scai-guideline-for-the-management-of-patients-with-acute-coronary-syndromes-a.pdf | topic | acute coronary syndromes | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| AHA ACC | virani-et-al-2023-2023-aha-acc-accp-aspc-nla-pcna-guideline-for-the-management-of-patients-with-chronic-coronary.pdf | topic | chronic coronary disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | title | AASLD IDSA Practice Guideline on treatment of chronic hepatitis B | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | topic | chronic hepatitis B | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | aasld-idsa-practice-guideline-on-treatment-of-chronic.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ajrccm_200_7_e45.pdf | title | Diagnosis and Treatment of Adults with Community-acquired Pneumonia: An Official Clinical Practice Guideline of the American Thoracic Society and Infectious Diseases Society of America | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ajrccm_200_7_e45.pdf | topic | community-acquired pneumonia | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | amr-guidance-update.pdf | topic | antimicrobial-resistant gram-negative infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | amr-guidance-update.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciaa1215.pdf | title | Clinical Practice Guidelines by the Infectious Diseases Society of America, American Academy of Neurology, and American College of Rheumatology: Guidelines for the Prevention, Diagnosis and Treatment of Lyme Disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciaa1215.pdf | topic | Lyme disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciaa1215.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciaa1215.pdf | year | 2021 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciaa241.pdf | topic | nontuberculous mycobacterial pulmonary disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab275.pdf | title | Errata | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab275.pdf | topic | hepatitis C treatment trial, babesiosis treatment tables (corrections) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab549.pdf | title | Clinical Practice Guideline by the Infectious Diseases Society of America (IDSA) and Society for Healthcare Epidemiology of America (SHEA): 2021 Focused Update Guidelines on Management of Clostridioides difficile Infection in Adults | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab549.pdf | topic | Clostridioides difficile infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab953.pdf | title | Infectious Diseases Society of America Guidelines on Infection Prevention for Healthcare Personnel Caring for Patients With Suspected or Known COVID-19 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab953.pdf | topic | COVID-19 infection prevention for healthcare personnel | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciab953.pdf | population | general | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciac724.pdf | topic | COVID-19 treatment | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciac724.pdf | population | adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciad319.pdf | title | Hepatitis C Guidance 2023 Update: American Association for the Study of Liver Diseases-Infectious Diseases Society of America Recommendations for Testing, Managing, and Treating Hepatitis C Virus Infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciad319.pdf | topic | hepatitis C virus infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciad319.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciad527.pdf | title | IWGDF/IDSA Guidelines on the Diagnosis and Treatment of Diabetes-related Foot Infections (IWGDF/IDSA 2023) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciad527.pdf | topic | diabetes-related foot infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciad527.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciae104.pdf | title | Guide to Utilization of the Microbiology Laboratory for Diagnosis of Infectious Diseases: 2024 Update by the Infectious Diseases Society of America (IDSA) and the American Society for Microbiology (ASM) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciae104.pdf | topic | microbiology laboratory utilization for infectious disease diagnosis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciae104.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciae121.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciae479.pdf | population | pediatric, adolescent, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciu296.pdf | topic | skin and soft tissue infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciu296.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciu617.pdf | topic | chronic kidney disease in HIV infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciu617.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | civ482.pdf | title | 2015 Infectious Diseases Society of America (IDSA) Clinical Practice Guidelines for the Diagnosis and Treatment of Native Vertebral Osteomyelitis in Adults | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | civ482.pdf | topic | native vertebral osteomyelitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw118.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw353.pdf | title | Management of Adults With Hospital-acquired and Ventilator-associated Pneumonia: 2016 Clinical Practice Guidelines by the Infectious Diseases Society of America and the American Thoracic Society | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw360.pdf | title | 2016 Infectious Diseases Society of America (IDSA) Clinical Practice Guideline for the Treatment of Coccidioidomycosis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw360.pdf | topic | coccidioidomycosis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw360.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw376.pdf | title | Official American Thoracic Society/Centers for Disease Control and Prevention/Infectious Diseases Society of America Clinical Practice Guidelines: Treatment of Drug-Susceptible Tuberculosis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw376.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw670.pdf | title | Diagnosis and Treatment of Leishmaniasis: Clinical Practice Guidelines by the Infectious Diseases Society of America (IDSA) and the American Society of Tropical Medicine and Hygiene (ASTMH) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw670.pdf | topic | leishmaniasis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw670.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw694.pdf | title | Official American Thoracic Society/Infectious Diseases Society of America/Centers for Disease Control and Prevention Clinical Practice Guidelines: Diagnosis of Tuberculosis in Adults and Children | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw694.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw861.pdf | title | 2017 Infectious Diseases Society of America's Clinical Practice Guidelines for Healthcare-Associated Ventriculitis and Meningitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciw861.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1084.pdf | title | Diagnosis and Treatment of Neurocysticercosis: 2017 Clinical Practice Guidelines by the Infectious Diseases Society of America (IDSA) and the American Society of Tropical Medicine and Hygiene (ASTMH) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1084.pdf | topic | neurocysticercosis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1084.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1084.pdf | year | 2018 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1085.pdf | title | Clinical Practice Guidelines for Clostridium difficile Infection in Adults and Children: 2017 Update by the Infectious Diseases Society of America (IDSA) and Society for Healthcare Epidemiology of America (SHEA) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1085.pdf | topic | Clostridium difficile infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1085.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix1085.pdf | year | 2018 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix636.pdf | topic | chronic pain in HIV infection | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix669.pdf | topic | infectious diarrhea | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | cix669.pdf | population | pediatric, adolescent, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciy745.pdf | topic | outpatient parenteral antimicrobial therapy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciy745.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciy745.pdf | year | 2019 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciy866.pdf | topic | seasonal influenza | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciy866.pdf | population | pediatric, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | ciy866.pdf | year | 2019 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | title | 2025 Clinical Practice Guideline Update by the Infectious Diseases Society of America on Group A Streptococcal (GAS) Pharyngitis: Risk assessment using clinical scoring systems in children and adults | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | topic | group A streptococcal pharyngitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | gas-pharyngitis-pico-a-b-guideline.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | title | Guidance for the Knowledge and Skills required for Antimicrobial Stewardship Leaders: an update from the Society for Healthcare Epidemiology of America, Infectious Diseases Society of America, Pediatric Infectious Diseases Society, and the Society of Infectious Diseases Pharmacists | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | topic | antimicrobial stewardship leadership | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | guidance-for-the-knowledge-and-skills-required-for-antimicrobial-stewardship-leaders-an-update-from-the-society-for-healthcare-epidemiology-of-america-infectious-diseases-society-of-america.pdf | population | general | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | infection-prevention-and-control-of-candida-auris-in-pediatric-settings.pdf | title | Infection prevention and control of Candida auris in pediatric settings | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | maternal-immunizations.pdf | title | Maternal Immunizations: ACOG Committee Statement Number 26 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | maternal-immunizations.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | topic | beta-lactam antibiotic dosing | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | Pharmacotherapy - 2026 - Barreto - Consensus Guidance for Beta‐Lactam Antibiotic Dose Individualization in Acutely Ill.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | piab027.pdf | topic | acute hematogenous osteomyelitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | piad089.pdf | topic | acute bacterial arthritis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | piad089.pdf | year | 2024 | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | topic | new fever in the intensive care unit | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | society-of-critical-care-medicine-and-the-infectious.pdf | population | adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | topic | sepsis and septic shock | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | surviving-sepsis-campaign-international-guidelines-for-the.pdf | population | pediatric | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | surviving-sepsis-campaign-international-guidelines-for.pdf | topic | sepsis and septic shock | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | title | Antimicrobial Prophylaxis for Adult Patients With Cancer-Related Immunosuppression: ASCO and IDSA Clinical Practice Guideline Update | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| IDSA | taplitz-et-al-2018-antimicrobial-prophylaxis-for-adult-patients-with-cancer-related-immunosuppression-asco-and-idsa.pdf | topic | antimicrobial prophylaxis in cancer-related immunosuppression | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO_2024_Lupus_Nephritis_Guideline.pdf | topic | lupus nephritis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | title | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2009-Transplant-Recipient-Guideline-English.pdf | population | transplant | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2013-Lipids-Guideline.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | title | KDIGO 2017 Clinical Practice Guideline Update for the Diagnosis, Evaluation, Prevention, and Treatment of Chronic Kidney Disease-Mineral and Bone Disorder (CKD-MBD) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2017-CKD-MBD-Guideline.pdf | topic | chronic kidney disease-mineral and bone disorder | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2017-Living-Kidney-Donors-Guideline.pdf | population | transplant | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | topic | kidney transplantation candidate evaluation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2020-Transplant-Candidate-Guideline.pdf | population | transplant | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2021-Blood-Pressure-in-CKD-Guideline.pdf | topic | blood pressure in chronic kidney disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2021-Glomerular-Diseases-Guideline_English_2024-Chapter-Updates.pdf | topic | glomerular disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2022-Clinical-Practice-Guideline-for-Diabetes-Management-in-CKD.pdf | topic | diabetes in chronic kidney disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | title | KDIGO 2024 Clinical Practice Guideline for the Management of Antineutrophil Cytoplasmic Antibody (ANCA)-Associated Vasculitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2024-ANCA-Vasculitis-Guideline-Update.pdf | topic | ANCA-associated vasculitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | topic | chronic kidney disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2024-CKD-Guideline.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | title | KDIGO 2025 Clinical Practice Guideline for the Evaluation, Management, and Treatment of Autosomal Dominant Polycystic Kidney Disease (ADPKD) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2025-ADPKD-Guideline.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2025-Guideline-for-Nephrotic-Syndrome-in-Children.pdf | topic | nephrotic syndrome | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | title | KDIGO 2025 Clinical Practice Guideline for the Management of Immunoglobulin A Nephropathy (IgAN) and Immunoglobulin A Vasculitis (IgAV) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | topic | IgA nephropathy and IgA vasculitis | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2025-IgAN-IgAV-Guideline.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | title | KDIGO 2026 Clinical Practice Guideline for Acute Kidney Injury (AKI) and Acute Kidney Disease (AKD): Public Review Draft | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2026-AKI-AKD-Guideline-Public-Review-Draft-March-2026.pdf | population | pediatric, adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | title | KDIGO 2026 Clinical Practice Guideline for the Management of Anemia in Chronic Kidney Disease (CKD) | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | topic | anemia in chronic kidney disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-2026-Anemia-in-CKD-Guideline.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | title | KDIGO Clinical Practice Guideline for the Management of Heart Failure in Chronic Kidney Disease: Scope of Work | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | topic | heart failure in chronic kidney disease | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| KDIGO | KDIGO-Heart-Failure-in-CKD-Guideline-Scope-of-Work.pdf | population | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | abdom-aortic-aneurysm-screening-final-rs.pdf | title | Screening for Abdominal Aortic Aneurysm: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | title | Behavioral Weight Loss Interventions to Prevent Obesity-Related Morbidity and Mortality in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | adult-obesity-intervention-final-rec-statement.pdf | topic | obesity, behavioral weight loss intervention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | afib-screening-final-recommendation-statement.pdf | title | Screening for Atrial Fibrillation: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | title | Screening for Anxiety Disorders in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | anxiety-adults-screening-final-recommendation.pdf | population | adult, pregnancy, postpartum | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | title | Aspirin Use to Prevent Preeclampsia and Related Morbidity and Mortality: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | topic | preeclampsia prevention, low-dose aspirin | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | aspirin-preeclampsia-prevention-final-rec.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | title | Aspirin Use to Prevent Cardiovascular Disease: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | aspirin-use-cvd-prevention-final-rec.pdf | topic | cardiovascular disease prevention, aspirin | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | title | Screening for Asymptomatic Bacteriuria in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | asymptomatic-bacteriuria-final-rec-statement.pdf | population | adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | autismfinalrs.pdf | title | Screening for Autism Spectrum Disorder in Young Children: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | title | Screening for Bacterial Vaginosis in Pregnant Persons to Prevent Preterm Delivery: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | topic | bacterial vaginosis screening, preterm delivery prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | bacterial-vaginosis-final-rec-statement.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | title | Behavioral Counseling Interventions to Promote a Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults Without Cardiovascular Disease Risk Factors: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | behav-counsel-healthy-lifestyle-low-cvd-risk-final-rs.pdf | topic | cardiovascular disease prevention, diet and physical activity counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | bladcanrs.pdf | title | Screening for Bladder Cancer: U.S. Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | title | Risk Assessment, Genetic Counseling, and Genetic Testing for BRCA-Related Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | brca-related-cancer-final-RS_v2.pdf | topic | BRCA-related cancer risk assessment and genetic testing | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | title | Medication Use to Reduce Risk of Breast Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | breast-cancer-meds-final-recommendation.pdf | topic | breast cancer risk-reducing medication | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | breast-cancer-screening-final-rec.pdf | title | Screening for Breast Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | title | Primary Care Behavioral Counseling Interventions to Support Breastfeeding: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | topic | breastfeeding support counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | breastfeeding-interventions-final-recommendation.pdf | population | pregnancy, postpartum | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | title | Screening for Asymptomatic Carotid Artery Stenosis: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | carotid-artery-stenosis-final-rec-statement.pdf | topic | carotid artery stenosis screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | celiacscreening-recstatement.pdf | title | Screening for Celiac Disease: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cervical-cancer-final-rec-statement.pdf | title | Screening for Cervical Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | title | Primary Care Interventions to Prevent Child Maltreatment: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | child-maltreatment-interventions-final-rec-statement.pdf | topic | child maltreatment prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | child-vision-recstatement.pdf | title | Vision Screening in Children Aged 6 Months to 5 Years: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | child-vision-recstatement.pdf | topic | vision screening, amblyopia | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | title | Screening for Chlamydia and Gonorrhea: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | chlamydia-gonorrhea-recstatement.pdf | population | adolescent, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | title | Screening for Cognitive Impairment in Older Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cognitive-impairment-screening-final-rec-statement.pdf | population | older adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | colorectal-cancer-screening-final-recommendation-updated.pdf | title | Screening for Colorectal Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | copd-screening-final-recommendation.pdf | title | Screening for Chronic Obstructive Pulmonary Disease: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | copd-screening-final-recommendation.pdf | topic | COPD screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | title | Risk Assessment for Cardiovascular Disease With Nontraditional Risk Factors: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cvd-nontraditional-risk-factors-final-rec-statement.pdf | topic | cardiovascular disease risk assessment, nontraditional risk factors | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | title | Screening for Cardiovascular Disease Risk With Electrocardiography: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | cvd-screening-with-ecg-final-rec-statement.pdf | topic | cardiovascular disease risk screening, electrocardiography | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | title | Screening and Interventions to Prevent Dental Caries in Children Younger Than 5 Years: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | dental-caries-young children-final-rec-statement.pdf | topic | dental caries prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | depression-suicide-risk-adults-rs.pdf | title | Screening for Depression and Suicide Risk in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | depression-suicide-risk-adults-rs.pdf | population | adult, pregnancy, postpartum | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | diabetes-child-final-recommendation.pdf | title | Screening for Prediabetes and Type 2 Diabetes in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | eating-disorders-screening-adults-adolescents-final-recommendation.pdf | title | Screening for Eating Disorders in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | title | Interventions to Prevent Falls in Community-Dwelling Older Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | topic | falls prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | falls-prevention-older-adults-final-rec-statement.pdf | population | older adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | title | Folic Acid Supplementation to Prevent Neural Tube Defects: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | topic | neural tube defect prevention, folic acid | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | folic-acid-supplementation-final-rec-statement.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | food-insecurity-screening-final-recommendation.pdf | title | Screening for Food Insecurity: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | title | Serologic Screening for Genital Herpes Infection: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | genital-herpes-screening-final-recommendation.pdf | population | adolescent, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | title | Screening for Gestational Diabetes: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | gestational-diabetes-screening-final-recommendation.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | glaucoma-screening-final-recommendation.pdf | title | Screening for Primary Open-Angle Glaucoma: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | GON-final-recommendation.pdf | title | Ocular Prophylaxis for Gonococcal Ophthalmia Neonatorum: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | GON-final-recommendation.pdf | population | newborn | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | title | Behavioral Counseling Interventions to Promote a Healthy Diet and Physical Activity for Cardiovascular Disease Prevention in Adults With Cardiovascular Risk Factors: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | healthy-diet-phys-activity-high-risk-final-rec.pdf | topic | cardiovascular disease prevention, diet and physical activity counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | title | Behavioral Counseling Interventions for Healthy Weight and Weight Gain in Pregnancy: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | topic | gestational weight gain counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | healthy-weight-gain-pregnancy-final-rec-statement.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | title | Screening for Hearing Loss in Older Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hearing-loss-older-adults-final-rec-statement.pdf | population | older adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | title | Screening for Hepatitis B Virus Infection in Pregnant Women: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | topic | hepatitis B screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hepatitis-b-pregnant-women-final-rec-statement.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hepatitis-b-screening-adults-adolescents-final-rec-statement.pdf | title | Screening for Hepatitis B Virus Infection in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | title | Screening for Hepatitis C Virus Infection in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hepatitis-c-screening-final-recommendation.pdf | population | adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | high-blood-pressure-children-screening-final-rec-statement.pdf | title | Screening for High Blood Pressure in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | title | Interventions for High Body Mass Index in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | high-bmi-children-adolescents-final-recommendation.pdf | topic | high body mass index intervention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hiv-prep-prevention-final-recommendation.pdf | title | Preexposure Prophylaxis to Prevent Acquisition of HIV: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hiv-screening-final-rec-statement.pdf | title | Screening for HIV Infection: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hiv-screening-final-rec-statement.pdf | population | adolescent, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | title | Hormone Therapy for the Primary Prevention of Chronic Conditions in Postmenopausal Persons: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hormone-therapy-postmenopausal-final-recommendation.pdf | topic | postmenopausal hormone therapy for chronic disease prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hypertension-screening-adults-final-rec-statement.pdf | title | Screening for Hypertension in Adults: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | title | Screening for Hypertensive Disorders of Pregnancy: US Preventive Services Task Force Final Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | topic | hypertensive disorders of pregnancy screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | hypertensive-disorders-pregnancy-final-recommendation.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | idachildrenfinal.pdf | title | Screening for Iron Deficiency Anemia in Young Children: USPSTF Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | idachildrenfinal.pdf | topic | iron deficiency anemia screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | illicit-drug-use-children-final-rec.pdf | title | Primary Care-Based Interventions to Prevent Illicit Drug Use in Children, Adolescents, and Young Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | illicit-drug-use-children-final-rec.pdf | topic | illicit drug use prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | illicit-drug-use-children-final-rec.pdf | population | pediatric, adolescent, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | title | Screening for Impaired Visual Acuity in Older Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | impaired-visual-acuity-screening-final-recommendation.pdf | population | older adult | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | ipv-screening-final-rec-statement.pdf | title | Screening for Intimate Partner Violence and Caregiver Abuse of Older or Vulnerable Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | ipv-screening-final-rec-statement.pdf | topic | intimate partner violence and elder abuse screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | ipv-screening-final-rec-statement.pdf | population | adolescent, adult, older adult, pregnancy, postpartum | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | title | Screening and Supplementation for Iron Deficiency and Iron Deficiency Anemia During Pregnancy: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | topic | iron deficiency anemia screening and supplementation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | iron-deficiency-anemia-pregnancy-final-recommendation.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | latent-tuberulosis-screening-final-rec-statement.pdf | title | Screening for Latent Tuberculosis Infection in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | lipid-screening-children-adolescents-final-rec.pdf | title | Screening for Lipid Disorders in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | lung-cancer-screening-final-recommendation.pdf | title | Screening for Lung Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | multivitamin-mineral-suppl-cvd-cancer-prev-final-recommendation.pdf | title | Vitamin, Mineral, and Multivitamin Supplementation to Prevent Cardiovascular Disease and Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | title | Screening and Preventive Interventions for Oral Health in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | oral-health-adults-screening-interventions-final-recommendation.pdf | topic | oral health screening and prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | oral-health-children-final-recommendation.pdf | title | Screening and Preventive Interventions for Oral Health in Children and Adolescents Aged 5 to 17 Years: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | oral-health-children-final-recommendation.pdf | topic | oral health screening and prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | oralcancerfinalrs.pdf | title | Screening for Oral Cancer: U.S. Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | title | Screening for Osteoporosis to Prevent Fractures: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | osteoporosis-screening-final-recommendation.pdf | topic | osteoporosis screening, fracture prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | ovarian-cancer-final-rec-statement.pdf | title | Screening for Ovarian Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | title | Screening for Peripheral Artery Disease and Cardiovascular Disease Risk Assessment With the Ankle-Brachial Index: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | pad-ankle-brachial-screening-final-rec-statement.pdf | topic | peripheral artery disease screening, ankle-brachial index | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | pancreatic-cancer-final-rec-statement.pdf | title | Screening for Pancreatic Cancer: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | perinatal-depression-final-rec-statement.pdf | title | Interventions to Prevent Perinatal Depression: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | perinatal-depression-final-rec-statement.pdf | topic | perinatal depression prevention | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | perinatal-depression-final-rec-statement.pdf | population | pregnancy, postpartum | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | prediabetes-type2-diabetes-adult-final-recommendation.pdf | title | Screening for Prediabetes and Type 2 Diabetes: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | prostate-cancer-final-rec-statement-051418.pdf | title | Screening for Prostate Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | rhrs.pdf | title | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | rhrs.pdf | topic | Rh(D) incompatibility screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | rhrs.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | rhrs.pdf | year | ? | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | scoliosis-final-rec-statement.pdf | title | Screening for Adolescent Idiopathic Scoliosis: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | Screening for Thyroid Cancer US Preventive Services Task Force Recommendation Statement Cancer Screening, Prevention, Control JAMA JAMA Network.pdf | title | Screening for Thyroid Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | Screening for Thyroid Dysfunction Final RS_Print_5.5.15.pdf | title | Screening for Thyroid Dysfunction: U.S. Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | screening-anxiety-children-final-recommendation.pdf | title | Screening for Anxiety in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | screening-depression-suicide-risk-children-final-recommendation.pdf | title | Screening for Depression and Suicide Risk in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | title | Behavioral Counseling to Prevent Skin Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | skin-cancer-counseling-final-recommendation.pdf | topic | skin cancer prevention counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | skin-cancer-screening-final-recommendation.pdf | title | Screening for Skin Cancer: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | sleep-apnea-screening-final-rec-statement.pdf | title | Screening for Obstructive Sleep Apnea in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | title | Screening for Speech and Language Delay and Disorders in Children: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | speech-language-delay-screening-children-final-recommendation.pdf | topic | speech and language delay screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | title | Statin Use for the Primary Prevention of Cardiovascular Disease in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | statin-use-cvd-prevention-final-rec-statement.pdf | topic | cardiovascular disease prevention, statins | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | title | Behavioral Counseling Interventions to Prevent Sexually Transmitted Infections: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | sti-counseling-final-recommendation-statement.pdf | topic | sexually transmitted infection prevention counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | title | Screening for Syphilis Infection in Nonpregnant Adolescents and Adults: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | syphilis-nonpregnant-adults-screening-final-recommendation.pdf | topic | syphilis screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | title | Screening for Syphilis Infection During Pregnancy: US Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | topic | syphilis screening | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | syphilis-pregnancy-screening-final-rec-statement.pdf | population | pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | testicuprs.pdf | title | Screening for Testicular Cancer: U.S. Preventive Services Task Force Reaffirmation Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | title | Interventions for Tobacco Smoking Cessation in Adults, Including Pregnant Persons: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | topic | tobacco smoking cessation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | tobacco-cessation-adults-final-rec-statement.pdf | population | adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | title | Primary Care Interventions for Prevention and Cessation of Tobacco Use in Children and Adolescents: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | tobacco-use-children-final-rec-statement.pdf | topic | tobacco use prevention and cessation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | title | Screening and Behavioral Counseling Interventions to Reduce Unhealthy Alcohol Use in Adolescents and Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | topic | unhealthy alcohol use screening and counseling | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | unhealthy-alcohol-use-adults-final-rec-statement.pdf | population | adolescent, adult, pregnancy | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | title | Screening for Unhealthy Drug Use: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | unhealthy-drug-use-screening-interventions-final-rec.pdf | population | adolescent, adult, pregnancy, postpartum | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | vitamin-d-deficiency-screening-final-recommendation.pdf | title | Screening for Vitamin D Deficiency in Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | title | Vitamin D, Calcium, or Combined Supplementation for the Primary Prevention of Fractures in Community-Dwelling Adults: US Preventive Services Task Force Recommendation Statement | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |
| USPSTF | vitamind-calcium-fracture-prevention-final-rec-statement.pdf | topic | fracture prevention, vitamin D and calcium supplementation | 2026-08-20 | Clinician confirmed the catalog value after reviewing the blind audit disagreement. |

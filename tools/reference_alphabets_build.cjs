// Rebuild with Node ICU 78.3 / CLDR 48.0; no collation library is needed by readers.
// Run: node tools/reference_alphabets_build.cjs <private output path>
const fs = require('node:fs');
if (process.versions.icu !== '78.3' || process.versions.cldr !== '48.0')
  throw new Error('Reviewed ICU/CLDR versions changed; re-check ADR 0356 controls');
const fold = { 'ø':'o', 'œ':'oe', 'æ':'ae', 'ł':'l', 'ð':'d', 'đ':'d', 'þ':'th', 'ı':'i' };
const plain = s => [...s.toLowerCase().normalize('NFKD')].filter(c => !/\p{M}/u.test(c)).map(c => fold[c] || c).join('').replaceAll('ß', 'ss');
const characters = [...new Set([...Array.from({length: 0x250 - 0xc0}, (_,i) => String.fromCodePoint(0xc0+i)), ...Array.from({length: 0x1f00 - 0x1e00}, (_,i) => String.fromCodePoint(0x1e00+i))].filter(c => /\p{L}/u.test(c)).flatMap(c => [...c.toLowerCase()]))];
const languages = {};
for (const locale of ['en', 'da', 'nb', 'sv', 'fi', 'is', 'pl', 'cs', 'tr', 'es', 'de']) {
  const collator = new Intl.Collator(locale, {sensitivity:'base', usage:'sort'});
  const contractions = locale === 'da' || locale === 'nb' ? ['aa'] : locale === 'cs' ? ['ch'] : [];
  const units = [...'abcdefghijklmnopqrstuvwxyz', ...characters, ...contractions];
  const expansions = {};
  const representatives = [...'abcdefghijklmnopqrstuvwxyz'];
  for (const token of units) {
    const candidate = plain(token);
    if (locale === 'en') { expansions[token] = candidate; continue; }
    if (candidate !== token && /^[a-z]+$/.test(candidate) && collator.compare(token, candidate) === 0) {
      expansions[token] = candidate;
    } else if (!representatives.some(r => collator.compare(r, token) === 0)) {
      representatives.push(token);
    }
  }
  representatives.sort(collator.compare);
  const weights = {};
  if (locale !== 'en') {
    for (const token of units) {
      if (expansions[token] !== undefined) continue;
      const index = representatives.findIndex(r => collator.compare(r, token) === 0);
      weights[token] = String.fromCodePoint(0x100 + index);
    }
    for (const [token, expanded] of Object.entries(expansions))
      weights[token] = [...expanded].map(c => weights[c]).join('');
  }
  const base = ['Zhang', 'Øvretveit', 'Olsen', 'Aasen', 'Åsen', 'Äberg', 'Æsop', 'Öberg', 'Œuvre', 'Þórsson', 'Thomas', 'Łukasz', 'Luka', 'Ðor', 'Đor', 'Dora', 'Chata', 'Husa', 'Ivan', 'Ábel', 'Abel', 'Çelik', 'Celik', 'Ipek', 'İpek', 'ıpek', 'ipek', 'Ğul', 'Gul', 'Ñunez', 'Nunez', 'Ąbel', 'Ćala', 'Ęla', 'Ńova', 'Óla', 'Śara', 'Źara', 'Żara', 'Řada', 'Šara', 'Žara', 'Ŋara', 'Ǥara', 'Ŧara', 'Ʒara', 'Yara', 'Üara', 'Ôara', 'Ǫara'];
  // ADR 0399: German umlauts file as plain vowels; a sharp-s or umlaut tie stays unbroken.
  const input = locale === 'de' ? [...base, 'Göbel', 'Gobel', 'Goebel', 'Goethe', 'Müller', 'Mueller', 'Muller', 'Mullner', 'Straße', 'Strasse', 'Straub'] : base;
  languages[locale] = {
    cldr: process.versions.cldr,
    icu: process.versions.icu,
    source: `https://raw.githubusercontent.com/unicode-org/cldr/release-48/common/collation/${locale === 'nb' ? 'no' : locale}.xml`,
    inherited_source: 'https://raw.githubusercontent.com/unicode-org/cldr/release-48/common/collation/root.xml',
    note: locale === 'en' ? 'ADR 0356 ruling 2; thorn follows Yale/Library of Congress TH filing rather than CLDR.' : locale === 'de' ? 'ADR 0399; CLDR standard German is root: umlauts file as plain vowels and sharp s as ss. Göttingen (DGPs 2016), FAU art education (DGPs 2019) and FernUniversität Hagen ZitFit state plain-vowel filing; DGPs 2019 section 9.1 was not read.' : 'CLDR standard primary order; not confirmed by national APA guides. Bokmål inherits no.xml.',
    contractions,
    weights,
    controls: {input, ordered: [...input].sort(locale === 'en' ? (a,b) => plain(a) < plain(b) ? -1 : plain(a) > plain(b) ? 1 : 0 : collator.compare)}
  };
}
fs.writeFileSync(process.argv[2], JSON.stringify({english_fold: fold, languages}, null, 2) + '\n');

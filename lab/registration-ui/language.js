(() => {
  'use strict';
  const storageKey = 'iqs-display-language';
  const labels = {
    en: { language: 'Language', home: 'Registration & enrollment', services: 'All services', signin: 'Staff sign in', signout: 'Sign out', notice: '' },
    ha: { language: 'Harshe', home: 'Rajista', services: 'Dukkan ayyuka', signin: 'Shiga na ma’aikata', signout: 'Fita', notice: 'Preview: some labels and headings are translated. Much of the form, guidance and decisions remain in English. Translations require review.' },
    yo: { language: 'Èdè', home: 'Ìforúkọsílẹ̀', services: 'Gbogbo iṣẹ́', signin: 'Ìwọlé oṣiṣẹ́', signout: 'Jade', notice: 'Preview: some labels and headings are translated. Much of the form, guidance and decisions remain in English. Translations require review.' },
    ig: { language: 'Asụsụ', home: 'Ndebanye aha', services: 'Ọrụ niile', signin: 'Nbanye ndị ọrụ', signout: 'Pụọ', notice: 'Preview: some labels and headings are translated. Much of the form, guidance and decisions remain in English. Translations require review.' }
  };
  // Preview labels are deliberately limited to explicit, non-transactional headings.
  const extra = {
    en: { household: 'Household details', members: 'Household members', library: 'Knowledge library', what: 'What to do', need: 'What you need', next: 'Next step', references: 'References' },
    ha: { household: 'Bayanan iyali', members: 'Membobin iyali', library: 'Ɗakin karatu na ilimi', what: 'Abin da za a yi', need: 'Abin da kuke bukata', next: 'Mataki na gaba', references: 'Manazarta' },
    yo: { household: 'Àlàyé agbo ilé', members: 'Àwọn ọmọ agbo ilé', library: 'Ilé ìkàwé ìmọ̀', what: 'Ohun tí a ó ṣe', need: 'Ohun tí o nílò', next: 'Ìgbésẹ̀ tó tẹ̀ lé', references: 'Àwọn ìtọ́kasí' },
    ig: { household: 'Nkọwa ezinụlọ', members: 'Ndị òtù ezinụlọ', library: 'Ọbá akwụkwọ ihe ọmụma', what: 'Ihe a ga-eme', need: 'Ihe ị chọrọ', next: 'Nzọụkwụ ọzọ', references: 'Ntụaka' }
  };
  Object.keys(labels).forEach(code => Object.assign(labels[code], extra[code]));
  const forms = {
    en: { register: 'Register your household', household_name: 'Household name', state: 'State / FCT', community: 'Community / area', member_name: 'Given name', family_name: 'Family name', birth: 'Date of birth', gender: 'Gender' },
    ha: { register: 'Yi rijistar iyalinka', household_name: 'Sunan iyali', state: 'Jiha / FCT', community: 'Al’umma / yanki', member_name: 'Sunan farko', family_name: 'Sunan iyali', birth: 'Ranar haihuwa', gender: 'Jinsi' },
    yo: { register: 'Forúkọ agbo ilé rẹ sílẹ̀', household_name: 'Orúkọ agbo ilé', state: 'Ìpínlẹ̀ / FCT', community: 'Agbègbè', member_name: 'Orúkọ ẹni', family_name: 'Orúkọ ìdílé', birth: 'Ọjọ́ ìbí', gender: 'Ìbálòpọ̀' },
    ig: { register: 'Debanye ezinụlọ gị aha', household_name: 'Aha ezinụlọ', state: 'Steeti / FCT', community: 'Obodo / mpaghara', member_name: 'Aha mbụ', family_name: 'Aha ezinụlọ', birth: 'Ụbọchị ọmụmụ', gender: 'Okike' }
  };
  Object.keys(labels).forEach(code => Object.assign(labels[code], forms[code]));

  const selector = document.getElementById('display-language');
  if (!selector) return;
  const change = (language) => {
    const selected = Object.hasOwn(labels, language) ? language : 'en';
    const translations = labels[selected];
    selector.value = selected;
    document.querySelectorAll('[data-i18n]').forEach(node => {
      const value = translations[node.dataset.i18n];
      if (value !== undefined) { node.textContent = value; node.lang = selected; }
    });
    const notice = document.getElementById('language-preview-notice');
    notice.textContent = translations.notice;
    notice.hidden = !translations.notice;
    // Only navigation is translated; keep the document language English for assistive technology.
    try { localStorage.setItem(storageKey, selected); } catch (_) { /* storage may be unavailable */ }
  };
  let saved = 'en';
  try { saved = localStorage.getItem(storageKey) || 'en'; } catch (_) { /* use English */ }
  selector.addEventListener('change', () => change(selector.value));
  change(saved);
})();


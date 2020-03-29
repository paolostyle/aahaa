const axios = require('axios');
const fs = require('fs-extra');
const { JSDOM } = require('jsdom');

async function downloadImage(url, filename) {
  const response = await axios({ url, responseType: 'stream' });
  return new Promise((resolve, reject) => {
    response.data
      .pipe(fs.createWriteStream(filename))
      .on('finish', resolve)
      .on('error', reject);
  });
}

async function fetchHeroData() {
  const { window } = await JSDOM.fromURL('https://afk-arena.fandom.com/wiki/Heroes');
  const heroRows = Array.from(window.document.querySelectorAll('tr')).filter(
    i => i.querySelectorAll('img').length > 0
  );
  return heroRows.map(tr => {
    const heroNameAndTitleCell = tr.querySelector('td:nth-child(3)');
    const [name, title] = heroNameAndTitleCell.textContent.trim().split(' - ');
    return {
      icon: tr.querySelector('td:nth-child(2) img').getAttribute('data-src'),
      faction: tr.parentNode.parentNode.previousElementSibling
        .querySelector('span')
        .getAttribute('id'),
      rarity: tr.querySelector('td:nth-child(1)').innerText,
      name,
      title,
      class: tr.querySelector('td:nth-child(4) img').getAttribute('alt')
    };
  });
}

async function saveHeroDataToFile() {
  try {
    const heroData = await fetchHeroData();
    await fs.writeJSON('./heroData.json', heroData);
  } catch (err) {
    console.log(err);
  }
}

async function saveHeroIconsToFiles() {
  try {
    const heroData = await fs.readJSON('./heroData.json');
    await Promise.all(heroData.map(i => downloadImage(i.heroIcon, `./images/${i.heroName}.jpg`)));
  } catch (err) {
    console.log(err);
  }
}

if (require.main === module) {
  (async () => {
    await saveHeroDataToFile();
    // await saveHeroIconsToFiles();
  })();
}

module.exports = {
  fetchHeroData,
  downloadImage,
  saveHeroDataToFile,
  saveHeroIconsToFiles
};

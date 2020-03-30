const axios = require("axios");
const fs = require("fs-extra");
const { JSDOM } = require("jsdom");
const path = require("path");

const getPath = filePath => path.join(__dirname, filePath);

async function downloadImage(url, filename) {
  const response = await axios({ url, responseType: "stream" });
  return new Promise((resolve, reject) => {
    response.data
      .pipe(fs.createWriteStream(filename))
      .on("finish", resolve)
      .on("error", reject);
  });
}

async function fetchHeroData() {
  const { window } = await JSDOM.fromURL(
    "https://afk-arena.fandom.com/wiki/Heroes"
  );
  const heroRows = Array.from(window.document.querySelectorAll("tr")).filter(
    i => i.querySelectorAll("img").length > 0
  );
  return heroRows.map(tr => {
    const heroNameAndTitleCell = tr.querySelector("td:nth-child(3)");
    const [name, title] = heroNameAndTitleCell.textContent.trim().split(" - ");
    return {
      icon: tr.querySelector("td:nth-child(2) img").getAttribute("data-src"),
      faction: tr.parentNode.parentNode.previousElementSibling
        .querySelector("span")
        .getAttribute("id"),
      rarity: tr.querySelector("td:nth-child(1)").innerText,
      name,
      title,
      class: tr.querySelector("td:nth-child(4) img").getAttribute("alt"),
      skins: name === "Brutus" ? 1 : 0
    };
  });
}

async function saveHeroDataToFile() {
  try {
    console.log("Starting fetching data...");
    const heroData = await fetchHeroData();
    await fs.writeJSON(getPath("../resources/heroData.json"), heroData);
    console.log("Hero data saved to heroData.json!");
  } catch (err) {
    console.log(err);
  }
}

async function saveHeroIconsToFiles() {
  try {
    console.log("Downloading hero icons...");
    const heroData = await fs.readJSON(getPath("../resources/heroData.json"));
    await Promise.all(
      heroData.map(i =>
        downloadImage(i.icon, getPath(`../resources/${i.name}.jpg`))
      )
    );
    console.log("Hero icons downloaded!");
  } catch (err) {
    console.log(err);
  }
}

async function replaceOverrides() {
  try {
    console.log("Replacing images with overrides");
    await fs.copy(getPath("../resources/overrides"), getPath("../resources"));
  } catch (err) {
    console.log(err);
  }
}

(async () => {
  await saveHeroDataToFile();
  await saveHeroIconsToFiles();
  await replaceOverrides();
})();
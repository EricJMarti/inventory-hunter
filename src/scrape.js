const fs = require('fs')
const puppeteer = require('puppeteer');

const url = process.argv[2];
if (!url) {
    throw 'missing url argument';
}

const htmlfile = process.argv[3];
const pngfile = process.argv[4];

(async () => {
    const browser = await puppeteer.launch({
        args: [
            '--no-sandbox',
            '--user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4427.0 Safari/537.36"'
        ],
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 1920, height: 1080 });
    await page.goto(url, {waitUntil: 'domcontentloaded'});
    const content = await page.content();
    if (htmlfile) {
        fs.writeFile(htmlfile, content, err => {
            if (err) {
                console.error(err)
                return
            }
        });
    } else {
        console.log(content);
    }
    if (pngfile) {
        await page.screenshot({path: pngfile});
    }
    await page.close();
    await browser.close();
})();

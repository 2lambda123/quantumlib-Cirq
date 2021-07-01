// Copyright 2021 The Cirq Developers
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      https://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import puppeteer from 'puppeteer';
import {expect} from 'chai';
import {readFileSync} from 'fs';
import pixelmatch from 'pixelmatch';
import * as PNG from 'pngjs';
import * as temp from 'temp';
import * as path from 'path';

/**
 * Generates an HTML script with the current repository bundle
 * that we will use to compare.
 */

// Due to the path, reading the file will only work by running this file in the same directory
// as the package.json file.
const bundle_string = readFileSync('dist/bloch_sphere.bundle.js');
const browserStrings = [
  `
  <!doctype html>
  <meta charset="UTF-8">
  <html lang="en">
    <head>
    <title>Cirq Web Development page</title>
    </head>
    <body>
    <div id="container"></div>
    <script>${bundle_string}</script>
    <script>
  `,
  ` renderBlochSphere('container')`,
  `
    </script>
    </body>
  </html>
  `,
];

/**
 * Testing to see if they look the same.
 */

// Automatically track and cleanup files on exit
temp.track();

describe('Bloch sphere', () => {
  // Create the temporary directory first, then run everything.
  temp.mkdir('tmp', (err, dirPath) => {
    const output_path = path.join(dirPath, 'bloch_sphere.png');
    const new_vector_output_path = path.join(dirPath, 'bloch_sphere_vec.png');

    before(async () => {
      // Opens a headless browser with the generated HTML file and takes a screenshot.
      // The '--app' flag ensures that chromium does capture any 
      // excess browser input
      const browser = await puppeteer.launch({args: ['--app']});
      const page = await browser.newPage();

      // Take a screenshot of the first image
      await page.setContent(browserStrings.join(''));
      await page.screenshot({path: output_path});
      await browser.close();
    });

    it('with no vector matches the gold PNG', () => {
      const expected = PNG.PNG.sync.read(
        readFileSync('e2e/bloch_sphere/bloch_sphere_expected.png')
      );
      const actual = PNG.PNG.sync.read(readFileSync(output_path));
      const {width, height} = expected;
      const diff = new PNG.PNG({width, height});

      const pixels = pixelmatch(
        expected.data,
        actual.data,
        diff.data,
        width,
        height,
        {threshold: 0.1}
      );

      expect(pixels).to.equal(0);
    });

    before(async () => {
      //Opens a headless browser with the generated HTML file and takes a screenshot.
      const browser = await puppeteer.launch({args: ['--app']});
      const page = await browser.newPage();

      // Take a screenshot of the second image, adding the vector
      browserStrings[1] += `.addVector(1, 1, 2);`;
      await page.setContent(browserStrings.join(''));
      await page.screenshot({path: new_vector_output_path});
      await browser.close();
    });

    it('with custom statevector matches the gold PNG', () => {
      const expected = PNG.PNG.sync.read(
        readFileSync('e2e/bloch_sphere/bloch_sphere_expected_custom.png')
      );
      const actual = PNG.PNG.sync.read(readFileSync(new_vector_output_path));
      const {width, height} = expected;
      const diff = new PNG.PNG({width, height});

      const pixels = pixelmatch(
        expected.data,
        actual.data,
        diff.data,
        width,
        height,
        {threshold: 0.1}
      );

      expect(pixels).to.equal(0);
    });
  });
});

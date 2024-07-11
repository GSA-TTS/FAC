import { readFile, writeFile } from 'fs';
import { sync } from 'glob';
import process from 'node:process';
import { join } from 'path';
import postcss from 'postcss';

import autoprefixer from 'autoprefixer';
import { context } from 'esbuild';
import { sassPlugin } from 'esbuild-sass-plugin';


(async () => {
  const watch = process.argv.includes('--watch');
  const jsPath = sync(join('.', 'static', 'js', '*.js'));

  const runPostcss = (cssIn, cssOut) => {
    console.info('Running postcss');

    readFile(cssIn, (err, css) => {
      postcss([autoprefixer])
        .process(css, { from: cssIn, to: cssOut })
        .then((result) => {
          writeFile(cssOut, result.css, () => true);
          if (result.map) {
            writeFile(cssOut + '.map', result.map.toString(), () => true);
          }
        });
    });
  };

  const plugins = [
    {
      name: 'rebuild',
      setup(build) {
        let count = 0;
        build.onEnd((result) => {
          runPostcss(
            'static/compiled/scss/main.css',
            'static/compiled/scss/main-post.css'
          );

          if (count++ === 0) console.log('First build:', result);
          else console.log('Subsequent build:', result);
        });
      },
    },
    sassPlugin({
      loadPaths: [
        './node_modules/@uswds',
        './node_modules/@uswds/uswds/packages',
        './static/compiled/js',
      ],
    }),
  ];

  const buildOptions = {
    entryPoints: [...jsPath, 'static/scss/main.scss'],
    outdir: 'static/compiled',
    minify: process.env.NODE_ENV === 'production',
    sourcemap: process.env.NODE_ENV !== 'production',
    target: ['chrome58', 'firefox57', 'safari11', 'edge18'],
    bundle: true,
    format: 'iife',
    loader: {
      '.jpg': 'file',
      '.png': 'file',
      '.svg': 'file',
      '.ttf': 'file',
      '.woff': 'file',
      '.woff2': 'file',
    },
    plugins: plugins,
  };

  let ctx = await context({ ...buildOptions, plugins });
  if (watch) {
    console.info('Watching assets...');
    await ctx.watch();
  } else {
    console.info('Building assets...');
    await ctx.rebuild();
    await ctx.dispose();
  }
})();

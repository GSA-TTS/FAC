const esbuild = require('esbuild');
const postcss = require('postcss');
const autoprefixer = require('autoprefixer');
const fs = require('fs');
const glob = require('glob');
const path = require('path');
const { sassPlugin } = require('esbuild-sass-plugin');

(async () => {
  const watch = process.argv.includes('--watch');
  const jsPath = glob.sync(path.join('.', 'static', 'js', '*.js'));

  const runPostcss = (cssIn, cssOut) => {
    console.info('Running postcss');

    fs.readFile(cssIn, (err, css) => {
      postcss([autoprefixer])
        .process(css, { from: cssIn, to: cssOut })
        .then((result) => {
          fs.writeFile(cssOut, result.css, () => true);
          if (result.map) {
            fs.writeFile(cssOut + '.map', result.map.toString(), () => true);
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

  let ctx = await esbuild.context({ ...buildOptions, plugins });
  if (watch) {
    console.info('Watching assets...');
    await ctx.watch();
  } else {
    console.info('Building assets...');
    await ctx.rebuild();
    await ctx.dispose();
  }
})();

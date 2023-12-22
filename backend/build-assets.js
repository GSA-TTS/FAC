const esbuild = require('esbuild');
const postcss = require('postcss');
const autoprefixer = require('autoprefixer');
const fs = require('fs');
const glob = require('glob');
const path = require('path');
const { sassPlugin } = require('esbuild-sass-plugin');

const watch = process.argv.includes('--watch');
const jsPath = glob.sync(path.join('.','static','js','*.js'));

// Basic plugin to watch for build end, then run PostCSS
const postCssPlugin = {
  name: 'Trigger PostCSS',
  setup(build) {
    build.onEnd(() => {
      runPostcss('static/compiled/scss/main.css', 'static/compiled/scss/main-post.css');
    })
  },
}

const buildProps = {
  entryPoints: [...jsPath, 'static/scss/main.scss'],
  outdir: 'static/compiled',
  minify: process.env.NODE_ENV === "production",
  sourcemap: process.env.NODE_ENV !== "production",
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
  plugins: [
    sassPlugin({
      loadPaths: [
        "./node_modules/@uswds",
        "./node_modules/@uswds/uswds/packages",
        "./static/compiled/js",
      ],
    }),
    postCssPlugin
  ]
}

const runPostcss = (cssIn, cssOut) => {
  console.info('Running PostCSS...');
  fs.readFile(cssIn, (err, css) => {
    postcss([autoprefixer])
      .process(css, { from: cssIn, to: cssOut })
      .then(result => {
        fs.writeFile(cssOut, result.css, () => true)
        if ( result.map ) {
          fs.writeFile(cssOut + '.map', result.map.toString(), () => true)
          console.info('✅ PostCSS complete!')
        }
      })
  })
}

const run = async () => {
  if (watch) {
    const ctx = await esbuild.context(buildProps);
    console.info('Watching assets…')
    await ctx.watch();
  } else {
    esbuild.build(buildProps)
  }
}

run();

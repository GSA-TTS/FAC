const esbuild = require('esbuild');
const postcss = require('postcss');
const autoprefixer = require('autoprefixer');
const fs = require('fs');
const { sassPlugin } = require('esbuild-sass-plugin');

const runPostcss = (cssIn, cssOut) => {
  console.info('Running postcss');

  fs.readFile(cssIn, (err, css) => {
    postcss([autoprefixer])
      .process(css, { from: cssIn, to: cssOut })
      .then(result => {
        fs.writeFile(cssOut, result.css, () => true)
        if ( result.map ) {
          fs.writeFile(cssOut + '.map', result.map.toString(), () => true)
        }
      })
  })
}

require('esbuild').build({
  entryPoints: ['static/js/app.js', 'static/scss/main.scss'],
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
  watch: {
    onRebuild(error, result) {
      runPostcss('static/compiled/scss/main.css', 'static/compiled/scss/main-post.css');

      if (error) console.error('watch build failed:', error)
      else console.info('watch build succeeded:', result)
    },
  },
  plugins: [
    sassPlugin({
      loadPaths: [
        "./node_modules/@uswds",
        "./node_modules/@uswds/uswds/packages",
      ],
    }),
  ]
})
  .then(() => { 
    runPostcss('static/compiled/scss/main.css', 'static/compiled/scss/main-post.css');
    console.info('Watching assets…') 
  })
  .catch(() => process.exit(1))

const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');

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
  .then(() => console.info('Watching assets…'))
  .catch(() => process.exit(1))

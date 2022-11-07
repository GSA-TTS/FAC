const esbuild = require('esbuild');
const { sassPlugin } = require('esbuild-sass-plugin');

require('esbuild').build({
  entryPoints: ['static/scss/main.scss'],
  outdir: 'static/compiled',
  // TODO: django env vars for environment
  // minify: process.env.ELEVENTY_ENV === "production",
  // sourcemap: process.env.ELEVENTY_ENV !== "production",
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
      ],
    }),
  ]
}).catch(() => process.exit(1))

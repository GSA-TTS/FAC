import pluginJs from '@eslint/js';
import pluginCypress from 'eslint-plugin-cypress/flat';
import eslintConfigPrettier from 'eslint-config-prettier';

// Exported rules included later will override rules included earlier.
// As in, the Cypress ruleset will override those from Prettier, which overrides those from the eslint recommended.
export default [
  pluginJs.configs.recommended,
  eslintConfigPrettier,
  pluginCypress.configs.recommended,
  {
    rules: {
      // Cypress plugin rule options defined at https://github.com/cypress-io/eslint-plugin-cypress/tree/master/docs/rules
      'cypress/unsafe-to-chain-command': 'error',
    },
  },
  {
    ignores:
      [
        "static/compiled/*",
        "staticfiles/*",
        "node_modules/*"
      ]
  }
];
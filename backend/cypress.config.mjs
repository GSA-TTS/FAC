import { defineConfig } from 'cypress';
import { downloadFile } from 'cypress-downloadfile/lib/addPlugin.js';
import indexTasks from './cypress/plugins/index.mjs';

export default defineConfig({
  e2e: {
    // We've imported your old cypress plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {
      on('task', {downloadFile});
      return indexTasks(on, config);
    },
    baseUrl: 'http://localhost:8000/',
    excludeSpecPattern: ['*/*/**/sf-sac-general-info.cy.js', '*/*/**/display-submissions.cy.js'],
    video: false,
    screenshotOnRunFailure: true,
  }
});

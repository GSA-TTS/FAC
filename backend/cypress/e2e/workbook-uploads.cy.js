import 'cypress-file-upload';
//require("@4tw/cypress-drag-drop");

import {
  testWorkbookFederalAwards,
  testWorkbookFindingsUniformGuidance,
  testWorkbookFindingsText,
  testWorkbookCorrectiveActionPlan,
  testWorkbookAdditionalUEIs,
} from '../support/workbook-uploads.js';

const reportTestId = '2023AUG0001000016';

describe('Workbook upload successful', () => {
  before(() => {
    cy.session('login-session', () => {
      cy.visit('/');
      cy.login();
    });
  });

  it('Successfully uploads Federal Awards', () => {
    cy.visit(`/report_submission/federal-awards/${reportTestId}`);
    testWorkbookFederalAwards();
  });

  it('Successfully uploads audit findings', () => {
    cy.visit(`report_submission/audit-findings/${reportTestId}`);
    testWorkbookFindingsUniformGuidance();
  });

  it('Successfully uploads audit findings text', () => {
    cy.visit(`report_submission/audit-findings-text/${reportTestId}`);
    testWorkbookFindingsText();
  });

  it('Successfully uploads CAP', () => {
    cy.visit(`/report_submission/CAP/${reportTestId}`);
    testWorkbookCorrectiveActionPlan();
  });

  it('Successfully uploads Additional UEIs', () => {
    cy.visit(`/report_submission/additional-ueis/${reportTestId}`);
    testWorkbookAdditionalUEIs();
  });

  describe('Workbook upload fail', () => {
    it('unsuccessful upload Federal Awards', () => {
      cy.intercept('POST', '/audit/excel/federal-awards-expended/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail');
      cy.visit(`report_submission/federal-awards/${reportTestId}`);
      cy.get('#file-input-federal-awards-xlsx').attachFile(
        'fed-awards-invalid.xlsx'
      );
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400);
      cy.wait(2000).get('#info_box').should('contain', 'A field is missing');
    });

    it('unsuccessful upload audit findings', () => {
      cy.intercept('POST', '/audit/excel/findings-uniform-guidance/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail');
      cy.visit(`report_submission/audit-findings/${reportTestId}`);
      cy.get('#file-input-audit-findings-xlsx').attachFile(
        'find-uni-invalid.xlsx'
      );
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400);
      cy.wait(2000).get('#info_box').should('contain', 'A field is missing');
    });

    it('unsuccessful upload audit findings text', () => {
      cy.intercept('POST', '/audit/excel/findings-text/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail');
      cy.visit(`/report_submission/audit-findings-text/${reportTestId}`);
      cy.get('#file-input-audit-findings-text-xlsx').attachFile(
        'find-text-invalid.xlsx'
      );
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400);
      cy.wait(2000).get('#info_box').should('contain', 'A field is missing');
    });

    it('unsuccessful upload CAP', () => {
      cy.intercept('POST', '/audit/excel/corrective-action-plan/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail');
      cy.visit(`/report_submission/CAP/${reportTestId}`);
      cy.get('#file-input-CAP-xlsx').attachFile('cap-invalid.xlsx');
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400);
      cy.wait(2000)
        .get('#info_box')
        .should('have.text', 'Field Error: undefined');
    });

    it('unsuccessful upload Additional UEIs', () => {
      cy.intercept('POST', '/audit/excel/additional-ueis/*', {
        statusCode: 400,
        fixture: 'fail-res.json',
      }).as('uploadFail');
      cy.visit(`/report_submission/additional-ueis/${reportTestId}`);
      cy.get('#file-input-additional-ueis-xlsx').attachFile('cap-invalid.xlsx');
      cy.wait('@uploadFail').its('response.statusCode').should('eq', 400);
      cy.wait(2000).get('#info_box').should('contain', 'A field is missing');
    });
  });
});

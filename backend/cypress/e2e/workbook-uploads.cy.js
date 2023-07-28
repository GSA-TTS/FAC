import 'cypress-file-upload';
//require("@4tw/cypress-drag-drop");

const reportTestId = '2023MAY0001000001'

describe('Workbook upload successful', () => {

    it('Successfully uploads Federal Awards', () => {
        cy.intercept('/audit/excel/federal-awards-expended/*', {
            fixture: 'success-res.json',
        }).as('uploadSuccess')
        cy.visit(`report_submission/federal-awards/${reportTestId}`);
        cy.get('#file-input-federal-awards-xlsx').attachFile('federal-awards-expended-UPDATE.xlsx');
        cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
        cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
        cy.get('#continue').click();
        cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    });

    it('Successfully uploads audit findings', () => {
        cy.intercept('/audit/excel/findings-uniform-guidance/*', {
            fixture: 'success-res.json',
        }).as('uploadSuccess')
        cy.visit(`report_submission/audit-findings/${reportTestId}`);
        cy.get('#file-input-audit-findings-xlsx').attachFile('findings-uniform-guidance-UPDATE.xlsx');
        cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
        cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
        cy.get('#continue').click();
        cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    });

    it('Successfully uploads audit findings text', () => {
        cy.intercept('/audit/excel/findings-text/*', {
            fixture: 'success-res.json',
        }).as('uploadSuccess')
        cy.visit(`report_submission/audit-findings-text/${reportTestId}`);
        cy.get('#file-input-audit-findings-text-xlsx').attachFile('findings-text-UPDATE.xlsx');
        cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
        cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
        cy.get('#continue').click();
        cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    });

    it('Successfully uploads CAP', () => {
        cy.intercept('/audit/excel/corrective-action-plan/*', {
            fixture: 'success-res.json',
        }).as('uploadSuccess')
        cy.visit(`/report_submission/CAP/${reportTestId}`);
        cy.get('#file-input-CAP-xlsx').attachFile('corrective-action-plan-UPDATE.xlsx');
        cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
        cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
        cy.get('#continue').click();
        cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    });

    it('Successfully uploads Additional UEIs', () => {  
        cy.intercept('/audit/excel/additional-ueis/*', {
            fixture: 'success-res.json',
        }).as('uploadSuccess')
        cy.visit(`/report_submission/additional-ueis/${reportTestId}`);
        cy.get('#file-input-additional-ueis-xlsx').attachFile('additional-uei-UPDATE.xlsx');
        cy.wait('@uploadSuccess').its('response.statusCode').should('eq', 200)
        cy.wait(2000).get('#info_box').should('have.text', 'File successfully validated! Your work has been saved.');
        cy.get('#continue').click();
        cy.url().should('contain', `/audit/submission-progress/${reportTestId}`);
    })

    describe('Workbook upload fail', () => {
        it('unsuccessful upload Federal Awards', () => {
            cy.intercept('POST', '/audit/excel/federal-awards-expended/*', {
                statusCode: 400,
                fixture: 'fail-res.json',
            }).as('uploadFail')
            cy.visit(`report_submission/federal-awards/${reportTestId}`);
            cy.get('#file-input-federal-awards-xlsx').attachFile('fed-awards-invalid.xlsx');
            cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
            cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
        })

        it('unsuccessful upload audit findings', () => {
            cy.intercept('POST', '/audit/excel/findings-uniform-guidance/*', {
                statusCode: 400,
                fixture: 'fail-res.json',
            }).as('uploadFail')
            cy.visit(`report_submission/audit-findings/${reportTestId}`);
            cy.get('#file-input-audit-findings-xlsx').attachFile('find-uni-invalid.xlsx');
            cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
            cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
        })

        it('unsuccessful upload audit findings text', () => {
            cy.intercept('POST', '/audit/excel/findings-text/*', {
                statusCode: 400,
                fixture: 'fail-res.json',
            }).as('uploadFail')
            cy.visit(`/report_submission/audit-findings-text/${reportTestId}`);
            cy.get('#file-input-audit-findings-text-xlsx').attachFile('find-text-invalid.xlsx');
            cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
            cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
        })

        it('unsuccessful upload CAP', () => {
            cy.intercept('POST', '/audit/excel/corrective-action-plan/*', {
                statusCode: 400,
                fixture: 'fail-res.json',
            }).as('uploadFail')
            cy.visit(`/report_submission/CAP/${reportTestId}`);
            cy.get('#file-input-CAP-xlsx').attachFile('cap-invalid.xlsx');
            cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
            cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
        })

        it('unsuccessful upload Additional UEIs', () => {
            cy.intercept('POST', '/audit/excel/additional-ueis/*', {
                statusCode: 400,
                fixture: 'fail-res.json',
            }).as('uploadFail')
            cy.visit(`/report_submission/additional-ueis/${reportTestId}`);
            cy.get('#file-input-additional-ueis-xlsx').attachFile('cap-invalid.xlsx');
            cy.wait('@uploadFail').its('response.statusCode').should('eq', 400)
            cy.wait(2000).get('#info_box').should('have.text', 'Field Error: undefined');
           })
    })

})

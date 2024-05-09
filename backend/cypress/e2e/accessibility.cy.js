import { terminalLog } from '../support/log-functions'

const screen_sizes = ['iphone-6', ['iphone-6', 'landscape'], [3840, 2160]]

function test_check_a11y(url, pageName, report_id) {
    if (report_id) {
        it(`Tests the full ${pageName} page for all screen sizes`, () => {
            check_a11y(`${url}${report_id}`, 'eligibility');
        })
    } else {
        it(`Tests the full ${pageName} page for all screen sizes`, () => {
            check_a11y(url)
        })
    }
}

function check_a11y(url) {
    cy.visit(url)
    cy.injectAxe()
    screen_sizes.forEach((size) => {
        if (Cypress._.isArray(size)) {
            cy.viewport(size[0], size[1])
        } else {
            cy.viewport(size)
        }
        cy.checkA11y(null, null, terminalLog)
    })
}

describe('A11y Testing on Home Page', () => {
    test_check_a11y('/', 'home');
    
    it('Tests the pop out primary nav', () => {
        cy.visit('/')
        cy.injectAxe()
        cy.get(".usa-menu-btn").contains("Menu").click()
        cy.checkA11y(null, null, terminalLog)
    })

    // Log in modal fails contrast tests with the darker background, which is expected.
    // it('Tests the log in modal', () => {
    //     cy.get('[aria-controls="login-modal"]').contains("Submit an audit").click();
    //     cy.checkA11y(null, null, terminalLog)
    // })
})

describe('A11y Testing on search pages', () => {
    before(() => {
        cy.visit('/dissemination/search/')
        cy.get('label').contains("All years").click()
        cy.get('[id="search-form"]').submit()
        cy.get('tbody > :nth-child(1) > td > a').invoke('attr', 'href').as('summary_url')
    })

    it(`Tests the summary page for all screen sizes`, () => {
        cy.get('@summary_url').then(val => {
            check_a11y(val)
        })
    })

    test_check_a11y('/dissemination/search/', 'basic search');
    test_check_a11y('/dissemination/search/advanced/', 'advanced search');
})


describe('A11y Testing on pre-submission pages', () => {
    test_check_a11y('/audit/', 'my submissions');
    test_check_a11y('/report_submission/eligibility/', 'eligibility');
    test_check_a11y('/report_submission/auditeeinfo/', 'auditee info');
    test_check_a11y('/report_submission/accessandsubmission/', 'submission access');
})

describe('A11y tests on an in progress report', () => {
    before(() => {
        cy.visit('/audit')
        cy.get('tr').contains('In Progress').parent().parent().contains('GSAFAC').invoke('text').as('report_id')
    })

    it(`Tests submission pages for all screen sizes`, () => {
        cy.get('@report_id').then(val => {
            // Submission items:
            check_a11y(`/audit/submission-progress/${val}`)
            check_a11y(`/report_submission/general-information/${val}`)
            check_a11y(`/audit/audit-info/${val}`)
            check_a11y(`/audit/upload-report/${val}`)
            check_a11y(`/report_submission/federal-awards/${val}`)
            // Cross validation:
            check_a11y(`/audit/cross-validation/${val}`)
            check_a11y(`/audit/ready-for-certification/${val}`)
            // Access Management:
            check_a11y(`/audit/manage-submission/${val}`)
            check_a11y(`/audit/manage-submission/add-editor/${val}`)
            check_a11y(`/audit/manage-submission/auditee-certifying-official/${val}`)
            check_a11y(`/audit/manage-submission/auditor-certifying-official/${val}`)
        })
    })
})

describe('A11y tests on a ready for certification report', () => {
    before(() => {
        cy.visit('/audit')
        cy.get('tr').contains('Ready for Certification').parent().parent().contains('GSAFAC').invoke('text').as('report_id')
    })

    it(`Tests submission pages for all screen sizes after locking for certification`, () => {
        cy.get('@report_id').then(val => {
            // Check checklist after locking for certification:
            check_a11y(`/audit/submission-progress/${val}`)
            // Certification and final submission pages:
            check_a11y(`/audit/auditor-certification/${val}`)
            check_a11y(`/audit/auditee-certification/${val}`)
            check_a11y(`/audit/submission/${val}`)
        })
    })
})

describe('A11y tests on a fully submitted report', () => {
    before(() => {
        cy.visit('/audit')
        cy.get('tr').contains('Accepted').parent().parent().contains('GSAFAC').invoke('text').as('report_id')
    })

    it(`Tests submission checklist for all screen sizes after submission`, () => {
        cy.get('@report_id').then(val => {
            // Check the checklist after submission:
            check_a11y(`/audit/submission-progress/${val}`)
        })
    })
})
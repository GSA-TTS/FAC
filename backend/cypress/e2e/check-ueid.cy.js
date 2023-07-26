describe('Create New Audit', () => {
  beforeEach(() => {
    cy.visit('/report_submission/auditeeinfo/');
  });

  describe('A Blank Form', () => {
    it('marks empty responses as invalid', () => {
      cy.get('.auditee-information input:invalid').should('have.length', 3);
    });

    it('will not submit', () => {
      cy.get('.usa-form--large').invoke('submit', (e) => {
        e.preventDefault();
        throw new Error('Form was submitted'); // The test will fail if this error is thrown
      });

      cy.get('.usa-button').contains('Continue').click();
    });
  });

  describe('Validation', () => {
    it('does not show any errors initially', () => {
      cy.get('[class*=--error]').should('have.length', 0);
    });

    describe('Auditee UEID', () => {
      function leaveUeiBlank() {
        cy.get('#auditee_uei').click().blur();
      }

      it('should display an error message when left blank', () => {
        leaveUeiBlank();
        cy.get('#auditee_uei-not-null').should('be.visible');
      });

      it('should disable the submit button when fields are invalid', () => {
        leaveUeiBlank();
        cy.get('#continue').should('be.disabled');
      });

      it('should remove the error message when input is supplied', () => {
        cy.get('#auditee_uei').type('ASDF').blur();
        cy.get('#auditee_uei-not-null').should('not.be.visible');
      });

      it('should indicate when the supplied input is too short', () => {
        cy.get('#auditee_uei').type('ASDF').blur();
        cy.get('#auditee_uei-length').should('be.visible');
      });

      it('should indicate when the supplied input is too long', () => {
        cy.get('#auditee_uei').clear().type('ASDFASDFASDFA').blur();
        cy.get('#auditee_uei-length').should('be.visible');
      });

      it('should remove the error message when the input is correct', () => {
        cy.get('#auditee_uei').clear().type('ASDFASDFASDF').blur();
        cy.get('#auditee_uei-length').should('not.be.visible');
      });

      it('should enable the "Continue" button when entities are fixed', () => {
        cy.get('button').contains('Continue').should('not.be.disabled');
      });
    });

    describe('Fiscal Year Start Validation', () => {
      function leaveFyStartBlank() {
        cy.get('#auditee_fiscal_period_end').click().blur();
      }

      it('should display an error message when left blank', () => {
        leaveFyStartBlank();
        cy.get('#auditee_fiscal_period_start').click().blur();
        cy.get('#auditee_fiscal_period_start-not-null').should('be.visible');
      });

      it('should disable the submit button when fields are invalid', () => {
        leaveFyStartBlank();
        cy.get('button').contains('Continue').should('be.disabled');
      });

      it('should remove the error message when input is supplied', () => {
        // arrange
        leaveFyStartBlank();

        // act
        cy.get('#auditee_fiscal_period_start').type('01/01/2022').blur();

        // assert
        cy.get('#auditee_fiscal_period_start-not-null').should(
          'not.be.visible'
        );
      });

      it('should show an error if the user enters a date before 1/1/2020', () => {
        cy.get('#auditee_fiscal_period_start').type('12/31/2019');
        cy.get('#fy-error-message li').should('have.length', 1);
      });

      it('should not show an error if the user enters a date after 12/31/2019', () => {
        cy.get('#auditee_fiscal_period_start').clear().type('12/31/2020');
        cy.get('#fy-error-message li').should('have.length', 0);
      });
    });

    describe('Fiscal Year End Validation', () => {
      function leaveFyEndBlank() {
        cy.get('#auditee_fiscal_period_end').click().blur();
      }

      it('should display an error message when left blank', () => {
        leaveFyEndBlank();
        cy.get('#auditee_fiscal_period_end-not-null').should('be.visible');
      });

      it('should disable the submit button when fields are invalid', () => {
        leaveFyEndBlank();
        cy.get('button').contains('Continue').should('be.disabled');
      });

      it('should remove the error message when input is supplied', () => {
        cy.get('#auditee_fiscal_period_end').type('01/31/2022').blur();
        cy.get('#auditee_fiscal_period_end-not-null').should('not.be.visible');
      });
    });

    describe('UEI Validation via API', () => {
      beforeEach(() => {
        cy.get('#auditee_uei').clear().type('ASDFASDFASDF').blur();
        cy.get('#auditee_uei-btn').as('searchButton');
        cy.get('.usa-modal__footer button.primary').as('primaryButton');
        cy.get('.usa-modal__footer button.secondary').as('secondaryButton');
      });

      afterEach(() => {
        cy.reload();
      });

      describe('Connection Errors', () => {
        beforeEach(() => {
          cy.intercept(
            {
              method: 'POST', // Route all GET requests
              url: '/api/sac/ueivalidation', // that have a URL that matches '/users/*'
            },
            {
              statusCode: 500,
            }
          ).as('apiError');
        });

        it('handles API errors', () => {
          cy.get('@searchButton').click();

          cy.wait('@apiError').then((interception) => {
            assert.isNotNull(
              interception.response.body,
              '1st API call has data'
            );
          });

          cy.contains(`We can't connect to SAM.gov to confirm your UEI.`);
        });
      });

      describe('An invalid UEI', () => {
        beforeEach(() => {
          cy.intercept(
            {
              method: 'POST',
              url: '/api/sac/ueivalidation',
            },
            {
              valid: false,
              errors: {
                auditee_uei: [
                  'The letters “O” and “I” are not used to avoid confusion with zero and one.',
                  'Ensure this field has at least 12 characters.',
                ],
              },
            }
          ).as('invalidUeiRequest');
        });

        it('Lets users know when their UEI is not recognized', () => {
          cy.get('@searchButton').click();

          cy.wait('@invalidUeiRequest').then((interception) => {
            assert.isNotNull(
              interception.response.body,
              '1st API call has data'
            );
          });

          cy.contains('Your UEI is not recognized');
        });
      });

      describe('A successful lookup', () => {
        beforeEach(() => {
          cy.intercept(
            {
              method: 'POST', // Route all GET requests
              url: '/api/sac/ueivalidation', // that have a URL that matches '/users/*'
            },
            {
              valid: true,
              response: {
                uei: 'ZQGGHJH74DW7',
                auditee_name: 'INTERNATIONAL BUSINESS MACHINES CORPORATION',
              },
            }
          ).as('validUeiRequest');
        });

        it('shows entity name after valid UEI request', () => {
          cy.get('@searchButton').click();

          cy.wait('@validUeiRequest').then((interception) => {
            assert.isNotNull(
              interception.response.body,
              '1st API call has data'
            );
          });

          cy.get('#uei-error-message li').should('have.length', 0);
          cy.get('#auditee_name').should(
            'have.value',
            'INTERNATIONAL BUSINESS MACHINES CORPORATION'
          );
        });

        it('Shows UEI and name in the page and hides the search field', () => {
          cy.get('@searchButton').click();

          cy.wait('@validUeiRequest').then((interception) => {
            assert.isNotNull(
              interception.response.body,
              '1st API call has data'
            );
          });

          cy.get('@primaryButton').click();
          cy.get('#auditee_uei').should('not.be.visible');
          cy.get('[data-testid=uei-info]').should('be.visible');
        });
      });
    });
  });

  describe('Prepopulate the form', () => {
    it('does not show any errors initially', () => {
      cy.get('[class*=--error]').should('have.length', 0);
    });

    describe('Add Auditee UEID', () => {
      it('should add auditee UEI', () => {
        cy.get('#auditee_uei').clear().type('ZQGGHJH74DW7').blur();
      });
    });

    describe('ADD Auditee Name as part of UEI Validation via API', () => {
      it('shows entity name after valid UEI request', () => {
        cy.intercept(
          {
            method: 'POST', // Route all GET requests
            url: '/api/sac/ueivalidation', // that have a URL that matches '/users/*'
          },
          {
            valid: true,
            response: {
              uei: 'ZQGGHJH74DW7',
              auditee_name: 'INTERNATIONAL BUSINESS MACHINES CORPORATION',
            },
          }
        ).as('validUeiRequest');

        cy.get('#auditee_uei-btn').click();

        cy.wait('@validUeiRequest').then((interception) => {
          assert.isNotNull(interception.response.body, '1st API call has data');
        });

        cy.get('.usa-modal__footer button.primary').as('primaryButton').click();

        cy.get('#uei-error-message li').should('have.length', 0);
        cy.get('#auditee_name').should(
          'have.value',
          'INTERNATIONAL BUSINESS MACHINES CORPORATION'
        );
      });
    });

    describe('ADD Fiscal start/end dates', () => {
      it('Enter expected start date', () => {
        cy.get('#auditee_fiscal_period_start').clear().type('01/01/2021');
        cy.get('#fy-error-message li').should('have.length', 0);
      });
      it('Enter expected end date', () => {
        cy.get('#auditee_fiscal_period_end').clear().type('01/01/2022');
        cy.get('#fy-error-message li').should('have.length', 0);
      });
    });
  });

  describe('Auditee info validation via API', () => {
    function completeFormWithValidInfo() {
      cy.get('#auditee_uei').clear().type('ASDFASDFASDF').blur();
      cy.get('#auditee_uei-btn').as('searchButton');
      cy.get('.usa-modal__footer button.primary').as('primaryButton');
      cy.get('.usa-modal__footer button.secondary').as('secondaryButton');
      cy.get('#auditee_fiscal_period_start').clear().type('01/01/2021');
      cy.get('#auditee_fiscal_period_end').clear().type('01/01/2022');
    }

    xit('should return auditee info errors from the remote server', () => {
      completeFormWithValidInfo();

      cy.intercept('POST', '/sac/auditee', {
        validueid: false,
        errors: 'Not valid.',
      }).as('invalidResponse');

      cy.get('.usa-button').contains('Continue').click();

      cy.wait('@invalidResponse').then((interception) => {
        assert.isFalse(
          interception.response.body.validueid,
          'Failure API Response'
        );
        // console.log('Response:' + interception.response.body.validueid);
      });
    });

    xit('should return success response and move to the next page', () => {
      completeFormWithValidInfo();

      cy.intercept('POST', '/sac/auditee', {
        validueid: true,
        next: '/sac/accessandsubmission',
      }).as('validResponse');

      cy.get('.usa-button').contains('Continue').click();

      cy.wait('@validResponse').then((interception) => {
        assert.isTrue(
          interception.response.body.validueid,
          'Succcessful API Response'
        );
        // console.log('Response:' + interception.response.body.validueid);
      });
      cy.url().should('include', '/report_submission/accessandsubmission');
    });

    it('should proceed to the next step after successful submission', () => {
      completeFormWithValidInfo();
      cy.get('.usa-button').contains('Continue').click();
      cy.url().should('include', '/report_submission/accessandsubmission');
    });
  });

  it('Canceling an audit submission returns to the home page', () => {
    cy.get('.usa-button').contains('Cancel').click();
    cy.get('.usa-button').contains('OK').click();
    cy.url().should('include', '/audit/');
  });
});

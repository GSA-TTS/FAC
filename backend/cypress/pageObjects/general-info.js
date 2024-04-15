import genInfoData from '../fixtures/genInfoData/genInfoData.json';


class GeneralInfoForm {
    constructor() {
        this.auditTypeSingle = 'label[for=single-audit]';
        this.auditPeriodAnnual = 'label[for=audit-period-annual]';
        this.auditeeNameField = '#auditee_name';
        this.einField = '#ein';
        this.einNotSSNAttestationLabel = 'label[for=ein_not_an_ssn_attestation]';
        this.multipleEINsYesLabel = 'label[for=multiple-eins-yes]';
        this.auditeeAddressLine1Field = '#auditee_address_line_1';
        this.auditeeCityField = '#auditee_city';
        this.auditeeStateField = '#auditee_state';
        this.auditeeZipField = '#auditee_zip';
        this.auditeeContactNameField = '#auditee_contact_name';
        this.auditeeContactTitleField = '#auditee_contact_title';
        this.auditeePhoneField = '#auditee_phone';
        this.auditeeEmailField = '#auditee_email';
        this.auditorEINField = '#auditor_ein';
        this.auditorEINNotSSNAttestationLabel = 'label[for=auditor_ein_not_an_ssn_attestation]';
        this.auditorFirmNameField = '#auditor_firm_name';
        this.auditorAddressLine1Field = '#auditor_address_line_1';
        this.auditorCityField = '#auditor_city';
        this.auditorStateField = '#auditor_state';
        this.auditorZipField = '#auditor_zip';
        this.auditorContactNameField = '#auditor_contact_name';
        this.auditorContactTitleField = '#auditor_contact_title';
        this.auditorPhoneField = '#auditor_phone';
        this.auditorEmailField = '#auditor_email';
        this.continueButton = '#continue';
        this.auditeeUEI = '#auditee_uei';
        this.multipleUEIsYesLabel = 'label[for=multiple-ueis-yes]';
        this.secondaryAuditorsField = 'label[for=secondary_auditors-yes]';
    }


    selectAuditTypeAndPeriod() {
        cy.get(this.auditTypeSingle).click();

        cy.get(this.auditPeriodAnnual).click();
    }

    fillAuditeeInformation() {
        cy.get(this.auditeeNameField).type(genInfoData.auditeeNameField);
        cy.get(this.einField).type(genInfoData.einField);
        cy.get(this.einNotSSNAttestationLabel).click();
        cy.get(this.multipleEINsYesLabel).click();
        cy.get(this.auditeeAddressLine1Field).type(genInfoData.auditeeAddressLine1Field);
        cy.get(this.auditeeCityField).type(genInfoData.auditeeCityField);
        cy.get(this.auditeeStateField).type(genInfoData.auditeeStateField + '{enter}');
        cy.get(this.auditeeZipField).type(genInfoData.auditeeZipField);
        cy.get(this.auditeeContactNameField).type(genInfoData.auditeeContactNameField);
        cy.get(this.auditeeContactTitleField).type(genInfoData.auditeeContactTitleField);
        cy.get(this.auditeePhoneField).type(genInfoData.auditeePhoneField);
        cy.get(this.auditeeEmailField).type(genInfoData.auditeeEmailField);
        cy.get(this.multipleUEIsYesLabel).click();
    }

    fillAuditorInformation() {
        cy.get(this.auditorEINField).type(genInfoData.auditorEINField);
        cy.get(this.auditorEINNotSSNAttestationLabel).click();
        cy.get(this.auditorFirmNameField).type(genInfoData.auditorFirmNameField);
        cy.get(this.auditorAddressLine1Field).type(genInfoData.auditorAddressLine1Field);
        cy.get(this.auditorCityField).type(genInfoData.auditorCityField);
        cy.get(this.auditorStateField).type(genInfoData.auditorStateField + '{enter}');
        cy.get(this.auditorZipField).type(genInfoData.auditorZipField);
        cy.get(this.auditorContactNameField).type(genInfoData.auditorContactNameField);
        cy.get(this.auditorContactTitleField).type(genInfoData.auditorContactTitleField);
        cy.get(this.auditorPhoneField).type(genInfoData.auditorPhoneField);
        cy.get(this.auditorEmailField).type(genInfoData.auditorEmailField);
        cy.get(this.secondaryAuditorsField).click();
    }

    clickContinueButton() {
        cy.get(this.continueButton).click();
        cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
    }


}


export default GeneralInfoForm;

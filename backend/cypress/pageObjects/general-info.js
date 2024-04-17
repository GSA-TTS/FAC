import auditeeNameField from '../fixtures/genInfoData/auditeeNameField.json';
import einField from '../fixtures/genInfoData/einField.json';
import auditeeAddressLine1Field from '../fixtures/genInfoData/auditeeAddressLine1Field.json';
import auditeeCityField from '../fixtures/genInfoData/auditeeCityField.json';
import auditeeStateField from '../fixtures/genInfoData/auditeeStateField.json';
import auditeeZipField from '../fixtures/genInfoData/auditeeZipField.json';
import auditeeContactNameField from '../fixtures/genInfoData/auditeeContactNameField.json';
import auditeeContactTitleField from '../fixtures/genInfoData/auditeeContactTitleField.json';
import auditeePhoneField from '../fixtures/genInfoData/auditeePhoneField.json';
import auditeeEmailField from '../fixtures/genInfoData/auditeeEmailField.json';
import auditorEINField from '../fixtures/genInfoData/auditorEINField.json';
import auditorFirmNameField from '../fixtures/genInfoData/auditorFirmNameField.json';
import auditorAddressLine1Field from '../fixtures/genInfoData/auditorAddressLine1Field.json';
import auditorCityField from '../fixtures/genInfoData/auditorCityField.json';
import auditorStateField from '../fixtures/genInfoData/auditorStateField.json';
import auditorZipField from '../fixtures/genInfoData/auditorZipField.json';
import auditorContactNameField from '../fixtures/genInfoData/auditorContactNameField.json';
import auditorContactTitleField from '../fixtures/genInfoData/auditorContactTitleField.json';
import auditorPhoneField from '../fixtures/genInfoData/auditorPhoneField.json';
import auditorEmailField from '../fixtures/genInfoData/auditorEmailField.json';

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
        cy.get(this.auditeeNameField).type(auditeeNameField.auditeeNameField);
        cy.get(this.einField).type(einField.einField);
        cy.get(this.einNotSSNAttestationLabel).click();
        cy.get(this.multipleEINsYesLabel).click();
        cy.get(this.auditeeAddressLine1Field).type(auditeeAddressLine1Field.auditeeAddressLine1Field);
        cy.get(this.auditeeCityField).type(auditeeCityField.auditeeCityField);
        cy.get(this.auditeeStateField).type(auditeeStateField.auditeeStateField + '{enter}');
        cy.get(this.auditeeZipField).type(auditeeZipField.auditeeZipField);
        cy.get(this.auditeeContactNameField).type(auditeeContactNameField.auditeeContactNameField);
        cy.get(this.auditeeContactTitleField).type(auditeeContactTitleField.auditeeContactTitleField);
        cy.get(this.auditeePhoneField).type(auditeePhoneField.auditeePhoneField);
        cy.get(this.auditeeEmailField).type(auditeeEmailField.auditeeEmailField);
        cy.get(this.multipleUEIsYesLabel).click();
    }

    fillAuditorInformation() {
        cy.get(this.auditorEINField).type(auditorEINField.auditorEINField);
        cy.get(this.auditorEINNotSSNAttestationLabel).click();
        cy.get(this.auditorFirmNameField).type(auditorFirmNameField.auditorFirmNameField);
        cy.get(this.auditorAddressLine1Field).type(auditorAddressLine1Field.auditorAddressLine1Field);
        cy.get(this.auditorCityField).type(auditorCityField.auditorCityField);
        cy.get(this.auditorStateField).type(auditorStateField.auditorStateField + '{enter}');
        cy.get(this.auditorZipField).type(auditorZipField.auditorZipField);
        cy.get(this.auditorContactNameField).type(auditorContactNameField.auditorContactNameField);
        cy.get(this.auditorContactTitleField).type(auditorContactTitleField.auditorContactTitleField);
        cy.get(this.auditorPhoneField).type(auditorPhoneField.auditorPhoneField);
        cy.get(this.auditorEmailField).type(auditorEmailField.auditorEmailField);
        cy.get(this.secondaryAuditorsField).click();
    }

    clickContinueButton() {
        cy.get(this.continueButton).click();
        cy.url().should('match', /\/audit\/submission-progress\/[0-9]{4}-[0-9]{2}-GSAFAC-[0-9]{10}/);
    }
}

export default GeneralInfoForm;

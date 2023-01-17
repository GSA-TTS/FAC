from django.db import models

class Agencies(models.Model):
    auditid = models.ForeignKey('DataDistroAudits', models.DO_NOTHING, db_column='auditid')
    agency_cfda = models.TextField(blank=True, null=True)
    prior_agency = models.TextField(blank=True, null=True)
    prior_finding = models.BooleanField(blank=True, null=True)
    current_finding = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_distro_agencies'

# GRMLegalEntity
class Auditees(models.Model):
    name = models.TextField(blank=True, null=True)
    street1 = models.TextField(blank=True, null=True)
    street2 = models.TextField(blank=True, null=True)
    city = models.TextField(blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    zipcode = models.TextField(blank=True, null=True)
    contact = models.TextField(blank=True, null=True)
    title = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    fax = models.TextField(blank=True, null=True)
    email = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'data_distro_auditees'


class Audits(models.Model):
    auditid = models.AutoField(primary_key=True)
    auditeeid = models.ForeignKey(DataDistroAuditees, models.DO_NOTHING, db_column='auditeeid')
    audit_year = models.SmallIntegerField()
    reportid = models.IntegerField()
    version = models.SmallIntegerField()
    entity_type = models.ForeignKey('DataDistroEntityTypes', models.DO_NOTHING, blank=True, null=True)
    fyenddate = models.DateField(blank=True, null=True)
    audittype = models.TextField()
    periodcovered = models.TextField(blank=True, null=True)
    numberofmonths = models.SmallIntegerField(blank=True, null=True)
    auditee_date_signed = models.DateField(blank=True, null=True)
    cpa_date_signed = models.DateField(blank=True, null=True)
    cog_agency = models.TextField(blank=True, null=True)
    # oversight_agency not linked to agency?
    oversight_agency = models.TextField(blank=True, null=True)
    completed_on = models.DateField(blank=True, null=True)
    previously_completed_on = models.DateField(blank=True, null=True)
    fac_accepted_date = models.DateField(blank=True, null=True)
    dollar_threshhold = models.TextField(blank=True, null=True)  # This field type is a guess.
    total_federal_expenditure = models.TextField(blank=True, null=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'data_distro_audits'


class EntityTypes(models.Model):
    identifier = models.SmallIntegerField()
    name = models.TextField()

    class Meta:
        managed = False
        db_table = 'data_distro_entity_types'





from django.test import TestCase

from model_bakery import baker

from .wb_generator import load_historic_data
from .models import ELECAUDITHEADER, ELECAUDITS


class WbGegeratorTestCase(TestCase):
    def test_submission_with_gen_and_awards(self):
        audit_year = "2021"
        dbkey = "10001"
        self.fake_gen(audit_year, dbkey).save()
        self.fake_cfda(audit_year, dbkey).save()
        self.fake_cfda(audit_year, dbkey, variant=2).save()
        result = load_historic_data(audit_year, dbkey)
        success_log = result.get("success")
        self.assertIsNotNone(success_log)
        print(success_log)

    def fake_gen(self, audit_year, dbkey):
        gen = baker.make(
            ELECAUDITHEADER,
            AUDITYEAR=audit_year,
            DBKEY=dbkey,
            FYENDDATE="12/31/2022 00:00:00",
            AUDITTYPE="S",
            PERIODCOVERED="A",
            MULTIPLEEINS="N",
            EIN="134278617",
            MULTIPLEDUNS="N",
            AUDITEENAME="DELTA PARTNERS MANOR II",
            STREET1="288 S. FIRST STREET",
            CITY="DREW",
            STATE="MS",
            ZIPCODE="38737",
            AUDITEECONTACT="SCOTT RUSSELL",
            AUDITEETITLE="MANAGING AGENT",
            AUDITEEPHONE="6018562362",
            AUDITEEEMAIL="ALPHA4ONE@COMCAST.NET",
            AUDITEEDATESIGNED="03/31/2023 16:13:05",
            AUDITEENAMETITLE="SCOTT RUSSELL-MANAGING AGENT",
            CPAFIRMNAME="HARPER, RAINS, KNIGHT & COMPANY",
            CPASTREET1="1052 HIGHLAND COLONY PARKWAY SUITE 100",
            CPACITY="RIDGELAND",
            CPASTATE="MS",
            CPAZIPCODE="39157",
            CPACONTACT="JOEY FLETCHER",
            CPATITLE="LEAD AUDITOR",
            CPAPHONE="6016050722",
            CPAEMAIL="JFLETCHER@HRKCPA.COM",
            CPADATESIGNED="03/31/2023 16:17:06",
            COG_OVER="O",
            TYPEREPORT_FS="U",
            REPORTABLECONDITION="N",
            MATERIALWEAKNESS="N",
            MATERIALNONCOMPLIANCE="N",
            GOINGCONCERN="N",
            TYPEREPORT_MP="U",
            DOLLARTHRESHOLD="750000",
            LOWRISK="Y",
            TOTFEDEXPEND="2157610",
            REPORTABLECONDITION_MP="N",
            MATERIALWEAKNESS_MP="N",
            QCOSTS="N",
            CYFINDINGS="N",
            PYSCHEDULE="N",
            DUP_REPORTS="N",
            OVERSIGHTAGENCY="14",
            DATERECEIVED="03/31/2023 00:00:00",
            DATEFIREWALL="04/04/2023 01:30:04",
            FINDINGREFNUM="N",
            TYPEOFENTITY="903",
            IMAGE="1",
            AGENCYCFDA="x00",
            INITIALDATE="03/31/2023 00:00:00",
            MULTIPLE_CPAS="N",
            AUDITEECERTIFYNAME="SCOTT RUSSELL",
            AUDITEECERTIFYTITLE="MANAGING AGENT",
            FACACCEPTEDDATE="03/31/2023 00:00:00",
            AUDITOR_EIN="640809101",
            SD_MATERIALWEAKNESS="N",
            SIGNIFICANTDEFICIENCY="N",
            SIGNIFICANTDEFICIENCY_MP="N",
            ENTITY_TYPE="Non-profit",
            TYPEAUDIT_CODE="UG",
            FYSTARTDATE="01/01/2022 00:00:00",
            UEI="NW6ZDZNA9VY7",
            MULTIPLEUEIS="N",
            CPACOUNTRY="US",
        )
        return gen

    def fake_cfda(self, audit_year, dbkey, variant=1):
        # TODO Use realistic values
        cfda = baker.make(
            ELECAUDITS,
            AUDITYEAR=audit_year,
            DBKEY=dbkey,
            CFDA="93.667",
            FEDERALPROGRAMNAME="SOCIAL SERVICES BLOCK GRANT",
            AMOUNT="95248",
            MAJORPROGRAM="N",
            DIRECT="Y",
            LOANS="N",
            CLUSTERTOTAL="190496",
            FINDINGSCOUNT="0",
        )
        return cfda

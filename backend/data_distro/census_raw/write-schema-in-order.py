# We can't count on the CSVs ever coming in the right order.
# So, we'll write the schema out every time, based
# on the order in the CSVs we're working with.

NUMERIC = "NUMERIC"
TEXT = "TEXT"
DATE = "DATE"

mappings = {
    "CFDA_AGENCIES": { ##
        "AGENCYNUM": TEXT,
        "AGENCYNAME": TEXT,
        "I_9": TEXT,
        "III_9": TEXT,
        "III_10A": TEXT,
    },
    "CFDALOOKUP": { ##
        "ID": NUMERIC,
        "FEDERALPROGRAMNAME": TEXT,
        "CFDAPREFIX": TEXT,
        "CFDAEXT": TEXT,
    },
    "CLUSTERNAMELOOKUP": { ##
        "ID": NUMERIC,
        "NAME": TEXT,
        "SORT_NUM": NUMERIC

    },
    "ELECAUDITFINDINGS": { ##
        "ELECAUDITFINDINGSID": NUMERIC,
        "QCOSTS": TEXT,
        "OTHERFINDINGS": TEXT,
        "SIGNIFICANTDEFICIENCY": TEXT,
        "MATERIALWEAKNESS": TEXT,
        "OTHERNONCOMPLIANCE": TEXT,
        "TYPEREQUIREMENT": TEXT,
        "FINDINGREFNUMS": TEXT,
        "REPORTID": NUMERIC,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "VERSION": NUMERIC,
        "ELECAUDITSID": NUMERIC,
        "MODIFIEDOPINION": TEXT,
        "REPEATFINDING": TEXT,
        "PRIORFINDINGREFNUMS": TEXT
    },
    "ELECAUDITHEADER_IMS": { ##
        "ID": TEXT,
        "ID2": TEXT,
        "DBKEY": NUMERIC,
        "AUDITYEAR": TEXT,
        "TYPEAUDIT_CODE": TEXT,
        "SUPPRESSION_CODE": TEXT,
        "REPORTID": NUMERIC,
        "VERSION": NUMERIC,
        "IMAGE_EXISTS": TEXT
    },
    "ELECAUDITHEADER": { ##
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "FYENDDATE": DATE,
        "AUDITTYPE": TEXT,
        "PERIODCOVERED": TEXT,
        "NUMBERMONTHS": NUMERIC,
        "MULTIPLEEINS": TEXT,
        "EIN": TEXT,
        "EINSUBCODE": TEXT,
        "MULTIPLEDUNS": TEXT,
        "DUNS": TEXT,
        "AUDITEENAME": TEXT,
        "STREET1": TEXT,
        "STREET2": TEXT,
        "CITY": TEXT,
        "STATE": TEXT,
        "ZIPCODE": TEXT,
        "AUDITEECONTACT": TEXT,
        "AUDITEETITLE": TEXT,
        "AUDITEEPHONE": TEXT,
        "AUDITEEFAX": TEXT,
        "AUDITEEEMAIL": TEXT,
        "AUDITEEDATESIGNED": DATE,
        "AUDITEENAMETITLE": TEXT,
        "CPAFIRMNAME": TEXT,
        "CPASTREET1": TEXT,
        "CPASTREET2": TEXT,
        "CPACITY": TEXT,
        "CPASTATE": TEXT,
        "CPAZIPCODE": TEXT,
        "CPACONTACT": TEXT,
        "CPATITLE": TEXT,
        "CPAPHONE": TEXT,
        "CPAFAX": TEXT,
        "CPAEMAIL": TEXT,
        "CPADATESIGNED": DATE,
        "CPANAMETITLE": TEXT,
        "COG_OVER": TEXT,
        "COGAGENCY": TEXT,
        "TYPEREPORT_FS": TEXT,
        "REPORTABLECONDITION": TEXT,
        "MATERIALWEAKNESS": TEXT,
        "MATERIALNONCOMPLIANCE": TEXT,
        "GOINGCONCERN": TEXT,
        "TYPEREPORT_MP": TEXT,
        "DOLLARTHRESHOLD": NUMERIC,
        "LOWRISK": TEXT,
        "REPORTREQUIRED": TEXT,
        "TOTFEDEXPEND": NUMERIC,
        "COPIES": TEXT,
        "REPORTABLECONDITION_MP": TEXT,
        "MATERIALWEAKNESS_MP": TEXT,
        "QCOSTS": TEXT,
        "CYFINDINGS": TEXT,
        "PYSCHEDULE": TEXT,
        "DUP_REPORTS": TEXT,
        "COG_AGENCY": TEXT,
        "OVERSIGHTAGENCY": TEXT,
        "DATERECEIVED": DATE,
        "DATEFIREWALL": DATE,
        "PREVIOUSDATEFIREWALL": TEXT,
        "FINDINGREFNUM": TEXT,
        "TYPEOFENTITY": TEXT,
        "IMAGE": NUMERIC,
        "AGENCYCFDA": TEXT,
        "INITIALDATE": DATE,
        "DATERECEIVEDOTHER": DATE,
        "MULTIPLE_CPAS": TEXT,
        "AUDITEECERTIFYNAME": TEXT,
        "AUDITEECERTIFYTITLE": TEXT,
        "FACACCEPTEDDATE": DATE,
        "AUDITOR_EIN": TEXT,
        "ELECAUDITHEADERID": TEXT,
        "SD_MATERIALWEAKNESS": TEXT,
        "SD_MATERIALWEAKNESS_MP": TEXT,
        "SIGNIFICANTDEFICIENCY": TEXT,
        "SIGNIFICANTDEFICIENCY_MP": TEXT,
        "SP_FRAMEWORK": TEXT,
        "SP_FRAMEWORK_REQUIRED": TEXT,
        "TYPEREPORT_SP_FRAMEWORK": TEXT,
        "SUPPRESSION_CODE": TEXT,
        "ENTITY_TYPE": TEXT,
        "TYPEAUDIT_CODE": TEXT,
        "FYSTARTDATE": DATE,
        "CPAFOREIGN": TEXT,
        "CPACOUNTRY": TEXT,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT,
        "OPEID": TEXT,
        "DATETOED": DATE,
        "DATEFINISHED": DATE,
        "TYPEFINDING": TEXT,
        "TYPEFUNDING": TEXT

    },
    "ELECAUDITHEADER3049": { ## 
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "FYENDDATE": DATE,
        "AUDITTYPE": TEXT,
        "PERIODCOVERED": TEXT,
        "NUMBERMONTHS": NUMERIC,
        "MULTIPLEEINS": TEXT,
        "EIN": TEXT,
        "EINSUBCODE": TEXT,
        "AUDITEENAME": TEXT,
        "STREET1": TEXT,
        "STREET2": TEXT,
        "CITY": TEXT,
        "STATE": TEXT,
        "ZIPCODE": TEXT,
        "AUDITEECONTACT": TEXT,
        "AUDITEETITLE": TEXT,
        "AUDITEEPHONE": TEXT,
        "AUDITEEFAX": TEXT,
        "AUDITEEEMAIL": TEXT,
        "AUDITEEDATESIGNED": DATE,
        "AUDITEENAMETITLE": TEXT,
        "CPAFIRMNAME": TEXT,
        "CPASTREET1": TEXT,
        "CPASTREET2": TEXT,
        "CPACITY": TEXT,
        "CPASTATE": TEXT,
        "CPAZIPCODE": TEXT,
        "CPACONTACT": TEXT,
        "CPATITLE": TEXT,
        "CPAPHONE": TEXT,
        "CPAFAX": TEXT,
        "CPAEMAIL": TEXT,
        "CPADATESIGNED": DATE,
        "CPANAMETITLE": TEXT,
        "COG_OVER": TEXT,
        "COGAGENCY": TEXT,
        "TYPEREPORT_FS": TEXT,
        "REPORTABLECONDITION": TEXT,
        "MATERIALWEAKNESS": TEXT,
        "MATERIALNONCOMPLIANCE": TEXT,
        "GOINGCONCERN": TEXT,
        "TYPEREPORT_MP": TEXT,
        "DOLLARTHRESHOLD": NUMERIC,
        "LOWRISK": TEXT,
        "REPORTREQUIRED": TEXT,
        "TOTFEDEXPEND": NUMERIC,
        "COPIES": TEXT,
        "REPORTABLECONDITION_MP": TEXT,
        "MATERIALWEAKNESS_MP": TEXT,
        "QCOSTS": TEXT,
        "CYFINDINGS": TEXT,
        "PYSCHEDULE": TEXT,
        "DUP_REPORTS": TEXT,
        "COG_AGENCY": TEXT,
        "OVERSIGHTAGENCY": TEXT,
        "DATERECEIVED": DATE,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT

    },
    "ELECAUDITS": { ##
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "CFDASEQNUM": TEXT,
        "CFDA": TEXT,
        "FEDERALPROGRAMNAME": TEXT,
        "AMOUNT": NUMERIC,
        "MAJORPROGRAM": TEXT,
        "TYPEREQUIREMENT": TEXT,
        "QCOSTS2": TEXT,
        "FINDINGS": TEXT,
        "FINDINGREFNUMS": TEXT,
        "RD": TEXT,
        "DIRECT": TEXT,
        "CFDA_PREFIX": TEXT,
        "CFDA_EXT": TEXT,
        "EIN": TEXT,
        "CFDA2": TEXT,
        "TYPEREPORT_MP": TEXT,
        "TYPEREPORT_MP_OVERRIDE": TEXT,
        "ARRA": TEXT,
        "LOANS": TEXT,
        "ELECAUDITSID": TEXT,
        "FINDINGSCOUNT": NUMERIC,
        "LOANBALANCE": NUMERIC,
        "PASSTHROUGHAMOUNT": NUMERIC,
        "AWARDIDENTIFICATION": TEXT,
        "CLUSTERNAME": TEXT,
        "PASSTHROUGHAWARD": TEXT,
        "STATECLUSTERNAME": TEXT,
        "PROGRAMTOTAL": NUMERIC,
        "CLUSTERTOTAL": NUMERIC,
        "OTHERCLUSTERNAME": TEXT,
        "CFDAPROGRAMNAME": TEXT,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT

    },
    "ELECCAPTEXT": { ##
        "SEQ_NUMBER": NUMERIC,
        "REPORTID": NUMERIC,
        "VERSION": NUMERIC,
        "DBKEY": NUMERIC,
        "AUDITYEAR": TEXT,
        "FINDINGREFNUMS": TEXT,
        "TEXT": TEXT,
        "CHARTSTABLES": TEXT,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT

    },
    "ELECCPAS": { ##
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "SEQNUM": NUMERIC,
        "VERSION": NUMERIC,
        "CPAFIRMNAME": TEXT,
        "CPASTREET1": TEXT,
        "CPACITY": TEXT,
        "CPASTATE": TEXT,
        "CPAZIPCODE": TEXT,
        "CPACONTACT": TEXT,
        "CPATITLE": TEXT,
        "CPAPHONE": TEXT,
        "CPAFAX": TEXT,
        "CPAEMAIL": TEXT,
        "CPAEIN": TEXT
    },
    "ELECEINS": { ##
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "EIN": TEXT,
        "EINSEQNUM": NUMERIC,
        "DUNS": TEXT,
        "DUNSEQNUM": NUMERIC
    },
    "ELECFINDINGSTEXT": { ##
        "SEQ_NUMBER": NUMERIC,
        "REPORTID": NUMERIC,
        "VERSION": NUMERIC,
        "DBKEY": NUMERIC,
        "AUDITYEAR": TEXT,
        "FINDINGREFNUMS": TEXT,
        "TEXT": TEXT,
        "CHARTSTABLES": TEXT,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT

    },
    "ELECNOTES": { ##
        "ID": NUMERIC,
        "REPORTID": NUMERIC,
        "VERSION": NUMERIC,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "SEQ_NUMBER": NUMERIC,
        "TYPE_ID": NUMERIC,
        "NOTE_INDEX": NUMERIC,
        "TITLE": TEXT,
        "CONTENT": TEXT,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT

    },
    "ELECPASSTHROUGH": { ##
        "ID": NUMERIC,
        "DBKEY": NUMERIC,
        "AUDITYEAR": TEXT,
        "ELECAUDITSID": NUMERIC,
        "PASSTHROUGHNAME": TEXT,
        "PASSTHROUGHID": TEXT

    },
    "ELECREPORTSAGENCY": {
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "DBKEY": NUMERIC,
        "AGENCYCFDA": TEXT,
        "EIN": TEXT,
        "PYAGENCY": TEXT,
        "PRIORFINDING": TEXT,
        "CURRENTFINDING": TEXT,
        "UEI": TEXT,
        "MULTIPLEUEIS": TEXT

    },
    "ELECRPT_REVISIONS": { ##
        "ELECRPTREVISIONID": NUMERIC,
        "REPORTID": NUMERIC,
        "VERSION": NUMERIC,
        "DBKEY": NUMERIC,
        "AUDITYEAR": TEXT,
        "GENINFO": TEXT,
        "GENINFO_EXPLAIN": TEXT,
        "FEDERALAWARDS": TEXT,
        "FEDERALAWARDS_EXPLAIN": TEXT,
        "NOTESTOSEFA": TEXT,
        "NOTESTOSEFA_EXPLAIN": TEXT,
        "AUDITINFO": TEXT,
        "AUDITINFO_EXPLAIN": TEXT,
        "FINDINGS": TEXT,
        "FINDINGS_EXPLAIN": TEXT,
        "FINDINGSTEXT": TEXT,
        "FINDINGSTEXT_EXPLAIN": TEXT,
        "CAP": TEXT,
        "CAP_EXPLAIN": TEXT,
        "OTHER": TEXT,
        "OTHER_EXPLAIN": TEXT

    },
    "ELECUEIS": { ##
        "UEISID": NUMERIC,
        "REPORTID": NUMERIC,
        "AUDITYEAR": TEXT,
        "VERSION": NUMERIC,
        "UEI": TEXT,
        "SEQNUM": TEXT,
        "DBKEY": NUMERIC

    },
    "FEDERAGENCYLOOKKUP": { ##
        "ID": NUMERIC,
        "CFDAPREFIX": TEXT,
        "NAME": TEXT,
        "ACRONYM": TEXT,
        "STARTEXT": TEXT,
        "ENDEXT": TEXT

    },
    "IDES_SHISTORY":
    { ##
        "ID": TEXT,
        "AUDITYEAR": TEXT,
        "REPORTID": NUMERIC,
        "DBKEY": NUMERIC,
        "VERSION": NUMERIC,
        "FINAL": TEXT,
        "AUDIT_UPLOAD": TEXT,
        "AUDITEE_SUBMIT": TEXT,
        "AUDITEE_SUBMIT_DATE": DATE,
        "AUDITOR_SUBMIT": TEXT,
        "AUDITOR_SUBMIT_DATE": DATE,
        "FAC_SUBMIT": TEXT,
        "FAC_SUBMIT_DATE": DATE,
        "CREATED": DATE,
        "DATEMODIFIED": DATE,
        "SH_MODDATE": DATE,
        "AUDIT_UPLOAD_DATE": TEXT,
        "EMAIL_SENT": TEXT,
        "EMAIL_SENT_DATE": DATE,
        "AUDITEE_REJECT_DATE": DATE,
        "AUDITOR_REJECT_DATE": DATE,
        "AUDITEE_IDES_EMAIL": TEXT,
        "CPA_IDES_EMAIL": TEXT,
        "NEW_AUDIT_UPLOAD": TEXT,
        "AUDITEE_RESENT_DATE": DATE,
        "AUDITOR_RESENT_DATE": DATE,
        "AUDITEE_SIG_CODE": TEXT,
        "AUDITOR_SIG_CODE": TEXT,
        "SUBMITTED": TEXT
    }
}

import sys
import os

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"GIVEN: {sys.argv}")
        print("Need an infile and destination directory.")
        exit()
    
    infile = sys.argv[1]
    mapped_tables = "mapped_schema.sql"
    outfile = os.path.join(sys.argv[2], mapped_tables)

    with open(infile, newline="", encoding="cp1252") as inp:
        headers = next(inp, None)
        for table in mappings.keys():
            if f"-{table}-" in infile:
                print(f"Writing {table}")
                print(f"Headers: {headers}")
                with open(outfile, "a") as outp:
                    outp.write(f'DROP TABLE IF EXISTS "{table}";\n')
                    outp.write(f'CREATE TABLE "{table}" (\n')
                    headers = headers.replace("\"", "")
                    headers = headers.replace("\r", "")
                    headers = headers.replace("\n", "")
                    headers = headers.split(",")
                    for ndx, header in enumerate(headers):
                        ending = ","
                        if ndx == len(headers) - 1:
                            ending = ""
                        outp.write(f"\t{header} {mappings[table][header]}{ending}\n")
                    outp.write(");\n\n")



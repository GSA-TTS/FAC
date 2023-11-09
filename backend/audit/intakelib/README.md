# intakelib

This code transforms how workbooks are brought into the FAC.

## The transformation to an intermediate representation

A workbook is an Excel (OpenOffice, etc.) document in XLSX format.

The workbook is loaded by OpenPyxl. At this point, it is a Python object.

We then convert that object into a JSON object. We will call this initial transformation the *intermediate representation*, or IR. 

The IR looks like this:

```
{'name': 'Form',
 'ranges': [{'end_cell': {'column': 'A', 'row': '2'},
             'name': 'award_reference',
             'start_cell': {'column': 'A', 'row': '2'},
             'values': ['AWARD-0001']},
            {'end_cell': {'column': 'C', 'row': '2'},
             'name': 'compliance_requirement',
             'start_cell': {'column': 'C', 'row': '2'},
             'values': ['A']},
            {'end_cell': {'column': 'L', 'row': '2'},
             'name': 'is_valid',
             'start_cell': {'column': 'L', 'row': '2'},
             'values': ['Y']},
             ...
```

In BNF, roughly:

`...` means 0-or-more
`..+` means 1-or-more
`{}` is an object
`[]` is an array
`int` and `string` are primitive types

```
IR      := [ Form... ]
Form    := { 
              name: string,
              ranges: [ Range... ]
            }
Range   := { 
              start_cell: Cell, 
              end_cell: Cell, 
              name: string, 
              values: [ Value... ]
            }
Cell    := { 
              column: string, 
              row: string 
            }
Value: string or int
```

Every workbook is transformed into this IR. The IR is independent of the workbook we are taking in. It is a direct representation of a spreadsheet that is composed of multiple sheets, where all the values we are interested are contained within named ranges.

Put another way, the IR is largely semantics-free. Or, the semantics are 1:1 to the workbook itself. The IR represents **sheets** and **named ranges**. It layers no additional semantics on the workbook beyond that.


## Why the IR?

The IR provides us with a simple way to interact with the named ranges independent of which workbook we are using. 

Presented above was a snippet of the Federal Awards workbook in the IR representation. This is very different from our internal representation in the application. For example, here is part of the same workbook:

```
{'FederalAwards': {'auditee_uei': 'ABC123ABC123',
                   'federal_awards': [{'award_reference': 'AWARD-0001',
                                       'cluster': {'cluster_name': 'N/A',
                                                   'cluster_total': 0},
                                       'direct_or_indirect_award': {'is_direct': 'Y'},
                                       'loan_or_loan_guarantee': {'is_guaranteed': 'N'},
                                       'program': {'amount_expended': 69038,
                                                   'federal_agency_prefix': '10',
                                                   'federal_program_total': 69038,
                                                   'is_major': 'N',
                                                   'number_of_audit_findings': 0,
                                                   'program_name': 'COMMUNITY '
                                                                   'FACILITIES '
                                                                   'LOANS AND '
                                                                   'GRANTS',
                                                   'three_digit_extension': '766'},
```

This is very *semantics-heavy* and has *internal topology*. It is semantically heavy because it is essentially representing the logical structures inherent in the workbook. (This is, in a way, good: it reflects the Uniform Guidance and conceptual structure of the object.) It has internal topology because it is bumpy; it is highly structured. Instead of being a list of sheets containing a list of ranges, it is deeply nested around the semantic structure of the audit. For shorthand, we'll refer to this as the **semantically-heavy** reprsentation, or **SH**.

The SH representation above is part of a Federal Awards workbook. That object includes an array of awards called `federal_awards`. An individual award might have an object called a `cluster`, and that cluster has a `cluster_name` and `cluster_total`. 

We then apply *JSON Schemas* to the SH representation. The schemas do an excellent job of making sure the overall shape of the object is correct. The schemas do a poor job of providing errors that are human-readable.

TO BE CLEAR: It is possible that the JSON Schemas would perform better if the SH representation had less internal topology. Many of the problems we are encountering are *not* because the structure is SH. Instead, it is because of all of the IT. The deeply nested nature (the IT) of the semantically-heavy representation (SH) is very possibly the root of the problem. The IT was introduced in an attempt to compartmentalize or otherwise group validations around *parts* of a workbook, as opposed to applying them to a flat structure as a whole. This design choice---to add topology to the workbook structure before validation---is quite possibly the design decision that set JSON Schems up for "failure," so-to-speak. Had the workbooks been left flat, as opposed to nested, we might not have this problem today.

For these reasons, **we have introduced the IR so that we can handle some user errors using a simpler workbook format**. We're doing this *instead* of rewriting the workbook format because too much of our application depends on the nested structure at this point.

## The transformation, in full

1. Take in an XLSX document
2. Convert it to the IR
3. Perform transformations and checks on the IR
4. Convert the IR to the semantically-laden format
5. Apply schema checks to the SH representation

## The new checks

The new checks are in the subdirectory `checks`. 

Each check: 

* takes in a workbook represented in the IR
* applies a check against one or more named ranges
* either quietly passes (effectively returning `None`) or throws an `CheckIRError`

This mirrors the cross-validations. Each check does one, and only one, check. This allows us to isolate questions about how our checks are operating, and makes it easy to add more checks.



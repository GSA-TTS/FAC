---
name: Cross-validation template
about: Starting point for writing individual cross-validation functions.
title: 'Cross-validation: short summary'
labels: ''
assignees: ''
---

## Validation Description

[//]: # (A description of the validalidation in plain language.)

## Section(s):
- [ ] This validation touches ALL sections

[//]: # (Spacing)

&nbsp;

[//]: # (Spacing)

- [ ] Pre-SAC
- [ ] General Information
- [ ] Audit Information
- [ ] Federal Awards
- [ ] Audit Findings
- [ ] Audit findings text
- [ ] CAP Text
- [ ] Additional UEIs
- [ ] Additional Auditors
- [ ] Audit package (PDF)
- [ ] Tribal data consent
- [ ] Auditee certification
- [ ] Auditor certification

## Error(s)

- [ ] This generates one error
- [ ] This possibly generates multiple errors


### Error text

[//]: # (Use Python format string syntax. E.g. f"The section {general-information} is missing everything.")

```python
f"Sad Mac"
```

### Error number

[//]: # (Short identifier followed by timestamp. E.g. UEI_202307050927)

```
SADMAC_202307071352
```

## Notes

[//]: # (Any additional notes for implementation.)


```[tasklist]
### Tasks
- [ ] Error text is edited and approved by @lauraherring 
- [ ] Validation is implemented
- [ ] When data is correct, validation produces no errors
- [ ] When data is incorrect, validation produces expected errors.
```



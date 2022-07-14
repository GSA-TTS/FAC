# 5. Determine certify audit submission path

Introduced: 20220714.

## Status

Approved

## Context

We need to decide on a path forward for how we will cerfify audits for the MVP in order to unblock design. We considered two options: 

Option 1: Special roles/UX in the app to sign digitally - current, user-preferred solution defined more fully in https://github.com/GSA-TTS/FAC/issues/319

Option 2: Copy solve to ask people to sign the PDF (lightweight solution)

## Decision

We decided on Option 1 (Special roles/UX in the app to sign digitally) as we believe the engineering cost is justified to overcome the risks introdcued by option 2: 

* Risk: Could lead to more audit churn if they are uploaded without signatures
* Risk: Could lead to more scanned PDFs being uploaded rather than searchable ones, slowing down auditors

We are moving forward with the caveat that we may consider some lighter-weight email notification system like a mailto link if we think sending emails directly from the app will be too challenging and not useful elsewhere in the app. 
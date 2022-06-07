# Compliance

A compliance documentation workflow using [OSCAL](https://pages.nist.gov/OSCAL/) with [Trestle](https://github.com/IBM/compliance-trestle) to generate a System Security Plan (SSP) using Markdown. Based on [Compliance Template](https://github.com/GSA-TTS/compliance-template).

## Usage

### Installation

Follow the steps to [install Trestle in a Python virtual environment](https://ibm.github.io/compliance-trestle/python_trestle_setup/).

### To start

Add an OSCAL Profile to [profiles](./profiles/lato/) that adheres to selected controls in the NIST 800-53 and CIS Docker Benchmark catalogs.

### Make

- `make generate` to have `trestle` generate the corresponding control statement in Markdown.
- `make generate-with-header` to have `trestle` generate the corresponding control statement in Markdown with the status headers.
- `make assemble` will generate the resulting OSCAL System Security Plan (SSP).
- `make status` will print out some basic metrics about control status bits.

### Suggested workflow

Here is a suggested compliance documentation workflow that uses [compliance-trestle](https://github.com/IBM/compliance-trestle):

- Add a control to the [profile](./profiles/lato/) that will be satisfied.
- Run `make generate` to have `trestle` generate the corresponding control statement in Markdown.
  - This Markdown file will live in `dist/system-security-plans/`.
- Flesh out implementation detail stubs for that control.
  - It is OK to leave a control implementation description blank initially.
  - Backfill missing implementation descriptions as needed.
  - If links to existing code are needed, consider linking to high level artifacts with a general description.
    - Avoid linking directly to lines of code as these will change over time.
- (Optionally) Run `make assemble` to generate the resulting OSCAL System Security Plan (SSP).
  - This is an optional step because nothing uses the OSCAL SSP yet.

### Illustrative example

- Add `ac-2` to the NIST import in the [example profile](./profiles/lato/example-profile.json).
- `make generate` produces [ac-2.md](./dist/system-security-plans/ac-2.md)
- Fill out the controls except for subsection `g`.
- Commit and push to the repository and go through the usual code review procedures.
- At some time in the future, add support for `ac-2:g` and link to the commit introducing that support.
- Rinse and repeat for each control to document/expand upon.

### Status

To track compliance status, there's a header yaml file with a status list. The options are:

- `c-not-implemented`: this control has not been met.
- `c-not-documented`: this control has not been documented. 
- `c-implemented`: this control has been met.
- `c-documented`: this control has been documented.
- `c-organization-defined`: this control should be organization defined.
- `c-inherited`: this control is inherited from AWS.
- `c-org-help-needed`: this control needs to be implemented at a higher level.

`make status` will print out some basic metrics about control status bits.

### Effort

Some controls are tagged with an `effort` that estimates its level of difficulty. If absent, the `effort` is by default `low`. (Options are `low`, `medium`, and `high`.)

## Controls

Below are details about the controls, including additional parameters, notes, and control families.

### Parameters

A few controls require us to supply parameters to the control. These parameter choices are given in the official NIST catalog description. For instance, `sc-12.2` requires us to choose between `NIST FIPS-compliant` or `NSA-approved` symmetric keys.

To provide a parameter, edit the [example profile](./profiles/lato/example-profile.json) and add the relevant parameter id to the `set-parameters` section, along with the value(s) that best fits the control. (Note that some controls allow more than one parameter.)

It is also possible to override the default parameters for a control, if needed.

Once new parameters are set in the profile, please run `make generate` to re-generate the control Markdown with the new parameters.

### Control Families Guide

There are families of controls defined by their prefix (i.e. `ul-`), which groups the controls. Here is a guide for helping which of our *17 control families* you might want to write to. [`control_freak`](https://controlfreak.risk-redux.io/families/) is another great resource for learning more about these families, but note that it is specific to rev. 5, lacks the rev. 4 appendix J, and doesn't include GSA container-related controls. 

[Detailed control family descriptions here.](./control-families.md)

## Notes

- We are using JSON primarily because `trestle` YAML support is spotty. This may change in the future.
- We do not need a lot of features that `trestle` offers and are currently using a small subset of these features.
  - This workflow is intentionally primitive: for instance, we generate only the control documentation and fill out the implementation details.
  - We do not support profile authoring or editing or adding items in the control statement.
  - This also means that we do not (currently) have plans to actually use the SSP OSCAL file but the SSP is nonetheless is intended to be a final compliance artifact.
- The use of "System Security Plan" here is somewhat of a misnomer but is a byproduct of `compliance-trestle` and its [opinionated directory structure](https://ibm.github.io/compliance-trestle/cli/#opinionated-directory-structure).
- Link checking and general compliance documentation validation via CI pipelines is a possible future improvement.

## Demos

Some [asciinema](https://asciinema.org/) demos are provided under [demos/](./demos/). To play back these terminal sessions, please `brew install asciinema` if you have not already. You can run these demos locally by doing, for instance, `asciinema play demos/trestle-add-control.cast`. (If you wish to record a demo, `asciinema rec <file>`; control-d exits the recording.)

## TODO

1. Detailed usage
2. git submodule support
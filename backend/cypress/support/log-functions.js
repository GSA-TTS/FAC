export function terminalLog(violations) {
    cy.task(
        'log',
        `${violations.length} accessibility violation${violations.length === 1 ? '' : 's'
        } ${violations.length === 1 ? 'was' : 'were'} detected`
    )

    console.log(violations)

    // Pluck specific keys for readability. Add helpUrl if messages are not as clear as needed.
    const violationData = violations.map(
        ({ id, impact, description, nodes, helpUrl }) => ({
            id,
            impact,
            description,
            nodes: nodes.length,
            helpUrl: helpUrl
        })
    )

    cy.task('table', violationData)
}
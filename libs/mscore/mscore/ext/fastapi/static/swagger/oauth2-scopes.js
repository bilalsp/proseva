const OAuth2ScopesPlugin = (system) => {
    const React = system.React;

    function toArray(value) {
        if (!value) {
            return [];
        }

        if (typeof value.toArray === "function") {
            return value.toArray();
        }

        return Array.isArray(value) ? value : [];
    }

    function getSecurityAlternatives(security) {
        return toArray(security).map((requirement) => {
            if (!requirement || typeof requirement.entrySeq !== "function") {
                return [];
            }

            return requirement.entrySeq().toArray().map(([scheme, scopes]) => ({
                scheme,
                scopes: toArray(scopes),
            }));
        });
    }

    function ScopeRequirements({ security }) {
        const alternatives = getSecurityAlternatives(security);

        if (!alternatives.length) {
            return null;
        }

        const hasRequirements = alternatives.some(
            (alternative) => alternative.length > 0
        );

        if (!hasRequirements) {
            return null;
        }

        return React.createElement(
            "span",
            {
                className: "mscore-security-requirements",
                "aria-label": "Operation security requirements",
            },
            alternatives.map((alternative, alternativeIndex) =>
                React.createElement(
                    React.Fragment,
                    { key: alternativeIndex },

                    alternativeIndex > 0
                        ? React.createElement(
                              "span",
                              {
                                  className: "mscore-security-operator",
                                  key: `or-${alternativeIndex}`,
                              },
                              "OR"
                          )
                        : null,

                    React.createElement(
                        "span",
                        {
                            className: "mscore-security-alternative",
                            key: `alternative-${alternativeIndex}`,
                        },
                        alternative.map((requirement, requirementIndex) =>
                            React.createElement(
                                React.Fragment,
                                { key: requirementIndex },

                                requirementIndex > 0
                                    ? React.createElement(
                                          "span",
                                          {
                                              className: "mscore-security-operator",
                                              key: `and-${requirementIndex}`,
                                          },
                                          "AND"
                                      )
                                    : null,

                                React.createElement(
                                    "span",
                                    {
                                        className: "mscore-security-scheme",
                                        key: `scheme-${requirementIndex}`,
                                    },
                                    requirement.scheme
                                ),

                                requirement.scopes.map((scope, scopeIndex) =>
                                    React.createElement(
                                        "span",
                                        {
                                            className: "mscore-security-scope",
                                            key: `scope-${scopeIndex}`,
                                        },
                                        scope
                                    )
                                )
                            )
                        )
                    )
                )
            )
        );
    }

    return {
        wrapComponents: {
            OperationSummary: (Original, system) => (props) => {
                const security = props.operationProps.get("security");

                const originalGetComponent = props.getComponent;

                const getComponent = (name, withSystem) => {
                    const Component = originalGetComponent(name, withSystem);

                    if (name !== "authorizeOperationBtn") {
                        return Component;
                    }

                    return (buttonProps) =>
                        React.createElement(
                            React.Fragment,
                            null,
                            React.createElement(ScopeRequirements, {
                                security,
                            }),
                            React.createElement(Component, buttonProps)
                        );
                };

                return React.createElement(Original, {
                    ...props,
                    getComponent,
                });
            },
        },
    };
};

export default OAuth2ScopesPlugin;

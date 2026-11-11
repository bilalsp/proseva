const OAuth2ScopesPlugin = (system) => {
    const React = system.React;

    const toArray = (value) => {
        if (!value) {
            return [];
        }

        if (typeof value.toArray === "function") {
            return value.toArray();
        }

        return Array.isArray(value) ? value : [];
    };

    const getSecurityAlternatives = (security) =>
        toArray(security).map((requirement) => {
            if (typeof requirement?.entrySeq !== "function") {
                return [];
            }

            return requirement.entrySeq().toArray().map(([scheme, scopes]) => ({
                scheme,
                scopes: toArray(scopes),
            }));
        });

    const ScopeRequirements = ({ security }) => {
        const alternatives = getSecurityAlternatives(security);

        if (!alternatives.some((alternative) => alternative.length > 0)) {
            return null;
        }

        return React.createElement(
            "span",
            {
                className: "swagger-security-requirements",
                "aria-label": "Operation security requirements",
            },
            alternatives.map((alternative, alternativeIndex) =>
                React.createElement(
                    React.Fragment,
                    { key: `alternative-${alternativeIndex}` },

                    alternativeIndex > 0 &&
                        React.createElement(
                            "span",
                            {
                                className: "swagger-security-operator",
                            },
                            "OR"
                        ),

                    React.createElement(
                        "span",
                        {
                            className: "swagger-security-alternative",
                        },
                        alternative.map((requirement, requirementIndex) =>
                            React.createElement(
                                React.Fragment,
                                { key: `requirement-${requirementIndex}` },

                                requirementIndex > 0 &&
                                    React.createElement(
                                        "span",
                                        {
                                            className: "swagger-security-operator",
                                        },
                                        "AND"
                                    ),

                                React.createElement(
                                    "span",
                                    {
                                        className: "swagger-security-scheme",
                                    },
                                    requirement.scheme
                                ),

                                requirement.scopes.map((scope, scopeIndex) =>
                                    React.createElement(
                                        "span",
                                        {
                                            className: "swagger-security-scope",
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
    };

    return {
        wrapComponents: {
            OperationSummary: (Original) => (props) => {
                const security = props.operationProps.get("security");
                const originalGetComponent = props.getComponent;

                const getComponent = (name, withSystem) => {
                    const Component = originalGetComponent(
                        name,
                        withSystem
                    );

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

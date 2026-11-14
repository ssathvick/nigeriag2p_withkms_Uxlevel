"""Helper for resolving data policies from middleware response.

This helper provides methods to filter and merge data policies
that come from the IAM middleware, replacing the need to query
the local data policy service.
"""

from ..models.enum import DataPolicyTypeEnum, PolicyTargetEnum


class DataPolicyHelper:
    """Helper for resolving data policies from middleware response."""

    @staticmethod
    def resolve_register_record_policy(
        data_policies: list[dict] | None,
        register_id: str | None = None,
    ) -> dict | None:
        """Resolve and merge REGISTER_RECORD policies from middleware response.

        Filters by policy_target and optionally by register_id.
        ALLOW policies are unioned (OR); DISALLOW policies are negated and
        intersected (AND NOT). Returns ``None`` when no policy applies (no
        restriction).

        Args:
            data_policies: List of policy data from middleware (already filtered by mnemonics)
            register_id: Optional register ID to further filter policies by

        Returns:
            Merged expression dict or None if no policies apply
        """
        if not data_policies:
            return None

        # Filter by policy_target and optionally register_id
        policies_data = [
            p
            for p in data_policies
            if p.get("policy_target") == PolicyTargetEnum.REGISTER_RECORD.value
            and (register_id is None or p.get("register_id") == register_id)
        ]

        if not policies_data:
            return None

        allow_expressions: list[dict] = []
        disallow_expressions: list[dict] = []
        for policy in policies_data:
            expression = policy.get("policy_filter_expression")
            if not isinstance(expression, dict):
                continue
            if policy.get("policy_type") == DataPolicyTypeEnum.DISALLOW.value:
                disallow_expressions.append(expression)
            else:
                allow_expressions.append(expression)

        return DataPolicyHelper._merge_expressions(allow_expressions, disallow_expressions)

    @staticmethod
    def resolve_attribute_policy(
        data_policies: list[dict] | None,
    ) -> dict | None:
        """Resolve and merge global ATTRIBUTE policies from middleware response.

        ATTRIBUTE policies are register-agnostic (``register_id`` is null).
        ALLOW policies are unioned (OR); DISALLOW policies are negated and
        intersected (AND NOT). Returns ``None`` when no policy applies (no
        restriction).

        Args:
            data_policies: List of policy data from middleware (already filtered by mnemonics)

        Returns:
            Merged expression dict or None if no policies apply
        """
        if not data_policies:
            return None

        # Filter by policy_target only (register-agnostic)
        policies_data = [
            p for p in data_policies if p.get("policy_target") == PolicyTargetEnum.ATTRIBUTE.value
        ]

        if not policies_data:
            return None

        allow_expressions: list[dict] = []
        disallow_expressions: list[dict] = []
        for policy in policies_data:
            expression = policy.get("policy_filter_expression")
            if not isinstance(expression, dict):
                continue
            if policy.get("policy_type") == DataPolicyTypeEnum.DISALLOW.value:
                disallow_expressions.append(expression)
            else:
                allow_expressions.append(expression)

        return DataPolicyHelper._merge_expressions(allow_expressions, disallow_expressions)

    @staticmethod
    def _merge_expressions(
        allow_expressions: list[dict],
        disallow_expressions: list[dict],
    ) -> dict | None:
        """Merge ALLOW and DISALLOW expressions into a single expression.

        ALLOW policies are unioned (OR); DISALLOW policies are negated and
        intersected (AND NOT). Returns ``None`` when no expressions to merge.
        """
        nodes: list[dict] = []

        if len(allow_expressions) == 1:
            nodes.append(allow_expressions[0])
        elif len(allow_expressions) > 1:
            nodes.append({"type": "GROUP", "operator": "OR", "children": allow_expressions})

        if len(disallow_expressions) == 1:
            nodes.append(
                {
                    "type": "GROUP",
                    "operator": "NOT",
                    "children": [disallow_expressions[0]],
                }
            )
        elif len(disallow_expressions) > 1:
            nodes.append(
                {
                    "type": "GROUP",
                    "operator": "NOT",
                    "children": [
                        {
                            "type": "GROUP",
                            "operator": "OR",
                            "children": disallow_expressions,
                        }
                    ],
                }
            )

        if not nodes:
            return None

        if len(nodes) == 1:
            return nodes[0]

        return {"type": "GROUP", "operator": "AND", "children": nodes}

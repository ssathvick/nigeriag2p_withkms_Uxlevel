import type { RegisterRecordField } from '@/features/configuration/shared/hooks/useRegisterRecordFields';

export type GroupOperator = 'AND' | 'OR';

export type ConditionOperator =
    | 'eq'
    | 'neq'
    | 'gt'
    | 'gte'
    | 'lt'
    | 'lte'
    | 'contains'
    | 'not_contains'
    | 'in'
    | 'not_in'
    | 'is_null'
    | 'is_not_null';

export const MULTI_VALUE_OPERATORS: ConditionOperator[] = ['in', 'not_in'];
export const NULL_OPERATORS: ConditionOperator[] = ['is_null', 'is_not_null'];

export type PolicyFilterExpression = {
    type: 'GROUP' | 'CONDITION';
    operator?: GroupOperator | ConditionOperator;
    field_id?: string;
    value?: string | number | boolean;
    values?: (string | number | boolean)[];
    children?: PolicyFilterExpression[];
};

export type FilterConditionState = {
    id: string;
    type: 'CONDITION';
    field_id: string;
    operator: ConditionOperator;
    valueInput: string;
};

export type FilterGroupState = {
    id: string;
    type: 'GROUP';
    operator: GroupOperator;
    children: FilterNodeState[];
    /** false when filter was started via Condition — hides + Group at this root */
    allowNestedGroups?: boolean;
};

export type FilterNodeState = FilterGroupState | FilterConditionState;

export type FilterRootState = FilterGroupState;

export function createId() {
    return `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`;
}

export function createEmptyGroup(allowNestedGroups = true): FilterGroupState {
    return {
        id: createId(),
        type: 'GROUP',
        operator: 'AND',
        children: [],
        allowNestedGroups,
    };
}

export function createDefaultFilterRoot(): FilterRootState {
    return createEmptyGroup();
}

export function createEmptyCondition(): FilterConditionState {
    return {
        id: createId(),
        type: 'CONDITION',
        field_id: '',
        operator: 'eq',
        valueInput: '',
    };
}

export function getOperatorsForFieldType(dataType: string): ConditionOperator[] {
    const normalized = dataType?.toLowerCase() ?? 'string';

    if (normalized === 'boolean' || normalized === 'bool') {
        return ['eq', 'is_null', 'is_not_null'];
    }

    if (
        normalized === 'int' ||
        normalized === 'integer' ||
        normalized === 'float' ||
        normalized === 'double' ||
        normalized === 'decimal' ||
        normalized === 'number'
    ) {
        return ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'in', 'not_in', 'is_null', 'is_not_null'];
    }

    if (
        normalized === 'datetime' ||
        normalized === 'date' ||
        normalized === 'time' ||
        normalized === 'timestamp'
    ) {
        return ['eq', 'neq', 'gt', 'gte', 'lt', 'lte', 'is_null', 'is_not_null'];
    }

    if (normalized === 'json') {
        return ['eq', 'contains','is_null', 'is_not_null'];
    }

    return [
        'eq',
        'neq',
        'contains',
        'not_contains',
        'in',
        'not_in',
        'is_null',
        'is_not_null',
    ];
}

export function usesMultiValue(operator: ConditionOperator) {
    return MULTI_VALUE_OPERATORS.includes(operator);
}

export function usesNoValue(operator: ConditionOperator) {
    return NULL_OPERATORS.includes(operator);
}

function parseScalarValue(raw: string, dataType: string): string | number | boolean {
    const normalized = dataType?.toLowerCase() ?? 'string';
    const trimmed = raw.trim();

    if (normalized === 'boolean' || normalized === 'bool') {
        if (trimmed === 'true') return true;
        if (trimmed === 'false') return false;
        return trimmed;
    }

    if (
        normalized === 'int' ||
        normalized === 'integer' ||
        normalized === 'float' ||
        normalized === 'double' ||
        normalized === 'decimal' ||
        normalized === 'number'
    ) {
        const num = Number(trimmed);
        return Number.isNaN(num) ? trimmed : num;
    }

    return trimmed;
}

function parseMultiValues(raw: string, dataType: string): (string | number | boolean)[] {
    if (!raw.trim()) return [];
    return raw.split(',').map((part) => parseScalarValue(part, dataType));
}

function serializeCondition(
    node: FilterConditionState,
    fields: RegisterRecordField[],
): PolicyFilterExpression {
    const field = fields.find((f) => f.field_name === node.field_id);
    const dataType = field?.data_type ?? 'string';

    const base: PolicyFilterExpression = {
        type: 'CONDITION',
        field_id: node.field_id,
        operator: node.operator,
    };

    if (usesNoValue(node.operator)) {
        return base;
    }

    if (usesMultiValue(node.operator)) {
        return {
            ...base,
            values: parseMultiValues(node.valueInput, dataType),
        };
    }

    return {
        ...base,
        value: parseScalarValue(node.valueInput, dataType),
    };
}

function serializeGroup(
    node: FilterGroupState,
    fields: RegisterRecordField[],
): PolicyFilterExpression {
    return {
        type: 'GROUP',
        operator: node.operator,
        children: node.children.map((child) =>
            child.type === 'GROUP'
                ? serializeGroup(child, fields)
                : serializeCondition(child, fields),
        ),
    };
}

export function serializeFilterExpression(
    root: FilterRootState,
    fields: RegisterRecordField[],
): PolicyFilterExpression {
    return serializeGroup(root, fields);
}

export function parseFilterExpressionToState(
    expr: PolicyFilterExpression | Record<string, unknown> | null | undefined,
): FilterRootState {
    if (!expr || expr.type !== 'GROUP') {
        return createDefaultFilterRoot();
    }

    const group = expr as PolicyFilterExpression;

    return {
        id: createId(),
        type: 'GROUP',
        operator: (group.operator === 'OR' ? 'OR' : 'AND') as GroupOperator,
        children: (group.children || []).map(parseNodeToState),
        allowNestedGroups: true,
    };
}

function parseNodeToState(node: PolicyFilterExpression): FilterNodeState {
    if (node.type === 'GROUP') {
        return {
            id: createId(),
            type: 'GROUP',
            operator: (node.operator === 'OR' ? 'OR' : 'AND') as GroupOperator,
            children: (node.children || []).map(parseNodeToState),
            allowNestedGroups: true,
        };
    }

    const operator = (node.operator as ConditionOperator) || 'eq';
    let valueInput = '';

    if (usesMultiValue(operator) && Array.isArray(node.values)) {
        valueInput = node.values.map(String).join(', ');
    } else if (node.value !== undefined && node.value !== null) {
        valueInput = String(node.value);
    }

    return {
        id: createId(),
        type: 'CONDITION',
        field_id: node.field_id || '',
        operator,
        valueInput,
    };
}

export type FilterPreviewLine =
    | { kind: 'group'; operator: GroupOperator; depth: number }
    | {
          kind: 'condition';
          depth: number;
          field_id: string;
          operator: ConditionOperator;
          valueInput: string;
          incomplete: boolean;
      };

export function buildFilterPreviewLines(root: FilterRootState): FilterPreviewLine[] {
    const lines: FilterPreviewLine[] = [];

    const walkGroup = (group: FilterGroupState, depth: number) => {
        if (depth > 0) {
            lines.push({ kind: 'group', operator: group.operator, depth });
        }

        for (const child of group.children) {
            if (child.type === 'GROUP') {
                walkGroup(child, depth + 1);
            } else {
                const incomplete =
                    !child.field_id ||
                    (!usesNoValue(child.operator) && !child.valueInput.trim());
                lines.push({
                    kind: 'condition',
                    depth: depth + 1,
                    field_id: child.field_id,
                    operator: child.operator,
                    valueInput: child.valueInput,
                    incomplete,
                });
            }
        }
    };

    walkGroup(root, 0);
    return lines;
}

export function countConditions(root: FilterRootState): number {
    let count = 0;
    const walk = (nodes: FilterNodeState[]) => {
        for (const node of nodes) {
            if (node.type === 'GROUP') {
                walk(node.children);
            } else {
                count += 1;
            }
        }
    };
    walk(root.children);
    return count;
}

export function validateFilterExpression(root: FilterRootState): boolean {
    const hasValidCondition = (nodes: FilterNodeState[]): boolean => {
        for (const node of nodes) {
            if (node.type === 'GROUP') {
                if (hasValidCondition(node.children)) return true;
                continue;
            }
            if (!node.field_id || !node.operator) continue;
            if (usesNoValue(node.operator)) return true;
            if (node.valueInput.trim()) return true;
        }
        return false;
    };

    return hasValidCondition(root.children);
}

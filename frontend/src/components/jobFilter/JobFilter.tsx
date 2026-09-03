
const FILTER_OPTIONS = [
    { value: "frontend", label: "Frontend" },
    { value: "backend", label: "Backend" },
    { value: "full_stack", label: "Full Stack" },
    { value: "non_software", label: "Non Software" },
    { value: "unknown", label: "Unknown" },
];

type JobFilterProps = {
    value: string;
    onChange: (value: string) => void;
};


export function JobFilter({ value, onChange }: JobFilterProps) {


    return (
        <select
            style={styles.select}
            value={value}
            onChange={(e) => onChange(e.target.value)}
        >
            <option value="all">All Roles</option>
            {FILTER_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>{option.label}</option>
            ))}
        </select>
    )
}

const styles = {
    select: {
        padding: "10px 14px",
        borderRadius: 8,
        border: "1.5px solid #e2e8f0",
        fontSize: 14,
        background: "#fff",
        cursor: "pointer",
        outline: "none",
        minWidth: 160,
        color: "#000000",

    }
}
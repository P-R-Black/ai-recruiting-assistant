import { RELEVANCE_OPTIONS } from "../../constants/constants";

type RelevanceFilterProps = {
    value: string;
    onChange: (value: string) => void;
    ariaLabel: string;
};

export function JobRelevanceFilter({
    value,
    onChange,
    ariaLabel
}: RelevanceFilterProps) {


    return (
        <select
            style={styles.select}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            aria-label={ariaLabel}
        >
            <option value="all">All Jobs</option>
            {RELEVANCE_OPTIONS.map((option) => (
                <option key={option.value} value={option.value} >{option.label}</option>
            ))}

        </select>
    );
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
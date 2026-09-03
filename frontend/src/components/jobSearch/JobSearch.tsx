
import type { CSSProperties } from "react";

type JobSearchInputProps = {
    value: string;
    onChange: (value: string) => void;
};

type JobStatusFilterProps = {
    value: string;
    onChange: (value: string) => void;
};


export function JobSearch({ value, onChange }: JobSearchInputProps) {
    return (
        <div style={styles.inputWrap}>
            <span style={styles.inputIcon}>🔍</span>
            <input
                style={styles.input}
                type="text"
                placeholder="Search jobs by title..."
                value={value}
                onChange={(e) => onChange(e.target.value)}
            />
            {value && (
                <button style={styles.clearButton} onClick={() => onChange("")}> x</button>)}

        </div>
    )
}

const styles = {
    inputWrap: {
        position: "relative" as const,
        flex: "1 1 260px" as const,
        display: "flex" as const,
        alignItems: "center" as const,

        // border: "2px solid yellow",


    },
    inputIcon: {
        position: "relative" as const,
        left: 10,
        fontSize: 15,
        pointerEvents: "none" as const,
        lineHeight: 1,
        zIndex: 1,

    },
    input: {
        position: "relative" as const,
        right: 17,
        width: "100%" as const,
        padding: "10px 36px 10px 36px" as const,
        borderRadius: 8,
        border: "1.5px solid #e2e8f0" as const,
        fontSize: 14,
        background: "#fff" as const,
        outline: "none" as const,
        boxSizing: "border-box" as const,
        transition: "border-color .15s" as const,
        color: "#000000"


    },



    clearButton: {
        position: "absolute" as const,
        right: 30,
        fontSize: 13,
        color: "#94a3b8",
        background: "none" as const,
        border: "none" as const,
        cursor: "pointer" as const,
        lineHeight: 1,
        padding: 2,
    },
}
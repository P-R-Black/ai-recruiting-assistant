
export function SummaryCard({ label, value, accent }: { label: string; value: string; accent: string }) {

    console.log('label:', label, 'value:', value, 'accent:', accent)
    return (
        <div style={{ ...styles.summaryCard, borderTop: `3px solid #${accent.replace("#", "")}` }}>
            <span style={{ ...styles.summaryCardValue, color: `#${accent.replace("#", "")}` }}>{value}</span>
            <span style={styles.cardLabel}>{label}</span>
        </div>
    )
}

const styles = {
    summaryCard: {
        backgroundColor: "var(--inverse-primary)",
        borderRadius: 10,
        padding: "14px 16px",
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.2)",
        display: "flex",
        flexDirection: "column" as const,
    },
    summaryCardValue: {
        fontSize: 22,
        fontWeight: 800,
        letterSpacing: "-0.02em",
        lineHeight: 1,
    },
    cardLabel: {
        fontSize: 11,
        fontWeight: 600,
        color: "#94a3b8",
        textTransform: "uppercase" as const,
        letterSpacing: "0.07em",
    }
}                   
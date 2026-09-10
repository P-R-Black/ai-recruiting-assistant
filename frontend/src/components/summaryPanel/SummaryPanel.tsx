import { SummaryCard } from "../summaryCard/SummaryCard";
import { ROLE_COLORS, roleTypes } from "../../constants/constants"
import { useMemo } from "react";

export function SummaryPanel({ jobs }: { jobs: { id: string; role_type: string; count: number, recommended_resume: string }[] }) {

    const roleCounts = useMemo(() => {
        return jobs.reduce<Record<string, number>>((acc, job) => {
            const role = job.role_type;
            acc[role] = (acc[role] ?? 0) + 1; //(acc[role] || 0) + job.count;
            return acc;
        }, {});
    }, [jobs]);


    return (
        <div style={styles.summaryPanel}>
            <SummaryCard label="Total Jobs" value={jobs.length ? jobs.length.toString() : "0"} accent="6366f1" />

            {Object.entries(roleCounts).map(([role, count]) => (

                <SummaryCard
                    key={role}
                    label={roleTypes[role] ?? "Unknown"}
                    value={count.toString()}
                    accent={ROLE_COLORS[role]}
                />
            ))}


        </div>
    )

}

const styles = {
    summaryPanel: {
        display: "flex",
        gap: "1rem",
        padding: "10px",
        borderRadius: 8,
        border: "1.5px solid #e2e8f0",
        width: "100%",

    },
    summaryPanelH2: {
        fontSize: 18,
        fontWeight: 600,
        marginBottom: 10,
    },
    summaryPanelP: {
        fontSize: 14,
        lineHeight: 1.5,
    }
}                   
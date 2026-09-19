import { useParams } from "react-router";
import { useJob } from "../../hooks/useJobs";

import { JobCardDetail } from "../../components/jobCardDetail/JobCardDetail";

export function JobDetailPage() {
    const { jobId } = useParams()

    const { data: job, isLoading, isError, error } = useJob(jobId)

    if (isLoading) {
        return <p>Loading job...</p>;
    }

    if (isError) {
        return (
            <p>
                Error loading job: {error.message}
            </p>
        );
    }

    if (!job) {
        return (
            <p>Job not found.</p>
        )
    }

    return (

        <main style={styles.jobsPageStyle}>
            <h1 style={styles.pageH1Styles}>Job Details Page</h1>
            <div style={styles.summaryContainer} aria-label="Job summary" role="region">

            </div>
            <div style={styles.controls}>

            </div>
            <JobCardDetail job={job} />
        </main>

    )
}
const styles = {
    jobsPageStyle: {
        alignItems: "center" as const,
        justifyContent: "left" as const,
        display: "flex" as const,
        flexDirection: "column" as const,
    },

    summaryContainer: {
        display: "flex",
        justifyContent: "space-between",
        width: "100%",
        marginBottom: 20,

    },

    pageH1Styles: {
        textAlign: "left",
        width: "100%",
        padding: "1rem 0rem",
        marginBottom: "1rem",
    },

    controls: {
        display: "flex",
        marginBottom: 16,
        width: "100%",

    }
} as const;
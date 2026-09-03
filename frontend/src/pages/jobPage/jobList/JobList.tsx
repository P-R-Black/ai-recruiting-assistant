import type { Job } from "../../../types";
import { JobCard } from "../../../components/jobCard/JobCard";

type JobListProps = {
    jobs: Job[];
};

export function JobList({ jobs }: JobListProps) {
    return (
        <section style={styles.JobListLayout}>
            {jobs.map((job) => (
                <JobCard
                    job={job}
                    key={job.id}
                />
            ))}
        </section>
    );
}

const styles = {
    JobListLayout: {
        display: "flex",
        justifyContent: "space-between",
        flexWrap: "wrap" as const,
        maxWidth: "100vw",
    },
}
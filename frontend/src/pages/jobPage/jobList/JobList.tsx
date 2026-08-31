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
                    key={job.id}
                    job={job}
                />
            ))}
        </section>
    );
}

const styles = {
    JobListLayout: {

        display: "flex",
        gap: "1rem",
        flexWrap: "wrap",
        maxWidth: "100vw",

    },
}
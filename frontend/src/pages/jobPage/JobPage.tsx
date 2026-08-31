import { JobList } from "./jobList/JobList";
import { useJobs } from "../../hooks/useJobs";

export function JobsPage() {
    const {
        data: jobs,
        isLoading,
        isError,
        error
    } = useJobs()

    if (isLoading) {
        return <p>Loading jobs...</p>;
    }

    if (isError) {
        return (
            <p>
                Error loading jobs: {error.message}
            </p>
        );
    }

    if (!jobs || jobs.length === 0) {
        return <p>No jobs found.</p>;
    }




    return (
        <main>
            <h1>Jobs</h1>
            <JobList jobs={jobs} />

        </main>
    );
}

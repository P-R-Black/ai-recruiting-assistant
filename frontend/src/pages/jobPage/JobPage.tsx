import { JobList } from "./jobList/JobList";
import { useJobs } from "../../hooks/useJobs";
import { JobSearch } from "../../components/jobSearch/JobSearch";
import { JobFilter } from "../../components/jobFilter/JobFilter";
import { useState, useMemo } from "react";

export function JobsPage() {
    const [search, setSearch] = useState<string>("");
    const [jobFilter, setJobFilter] = useState<string>("all");

    const {
        data: jobs,
        isLoading,
        isError,
        error
    } = useJobs()

    const filteredJobs = useMemo(() => {
        const q = search.trim().toLowerCase();
        console.log('q:', q)
        return (jobs ?? []).filter((job) => {

            const matchesSearch =
                !q ||
                job.title.toLowerCase().includes(q)

            const matchesFilter = jobFilter === "all" || job.role_type === jobFilter;
            return matchesSearch && matchesFilter;

        });
    }, [search, jobFilter, jobs]);


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
        <main style={styles.jobsPageStyle}>
            <h1 style={styles.pageH1Styles}>Jobs</h1>
            <div style={styles.controls}>
                <JobSearch value={search} onChange={setSearch} />
                <JobFilter value={jobFilter} onChange={setJobFilter} />
            </div>
            <JobList jobs={filteredJobs} />
        </main>
    );
}


const styles = {
    jobsPageStyle: {
        alignItems: "center" as const,
        justifyContent: "center" as const,
        display: "flex" as const,
        flexDirection: "column" as const,

        // border: "2px solid blue",
    },

    pageH1Styles: {
        textAlign: "left",
        width: "100%",
        padding: "1rem 0rem",
        marginBottom: "1rem",
    },

    controls: {
        display: "flex",
        // gap: 12,
        marginBottom: 16,
        // flexWrap: "wrap",
        width: "100%",
        // justifyContent: "space-between",

        // border: "2px solid red",

    }
} as const;
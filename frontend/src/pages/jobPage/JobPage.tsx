import { JobList } from "./jobList/JobList";
import { useJobs } from "../../hooks/useJobs";
import { JobSearch } from "../../components/jobSearch/JobSearch";
import { JobFilter } from "../../components/jobFilter/JobFilter";
import { JobRelevanceFilter } from "../../components/jobRelevanceFilter/JobRelevanceFilter";
import { JobResumeFilter } from "../../components/jobResumeFilter/JobResumeFilter";
import { SummaryPanel } from "../../components/summaryPanel/SummaryPanel";
import { useState, useMemo } from "react";


export function JobsPage() {
    const [search, setSearch] = useState<string>("");
    const [roleType, setRoleType] = useState<string>("all");
    const [relevance, setRelevance] = useState<string>("all");
    const [recommendedResume, setRecommendedResume] = useState<string>("all");

    const filters = {
        ...(roleType !== "all" && {
            role_type: roleType,
        }),

        ...(relevance !== "all" && {
            is_relevant: relevance == "relevant",
        }),

        ...(recommendedResume !== "all" && {
            recommended_resume: recommendedResume
        })
    };


    const {
        data: jobs,
        isLoading,
        isError,
        error
    } = useJobs(filters)

    const filteredJobs = useMemo(() => {
        const q = search.trim().toLowerCase();

        return (jobs ?? []).filter((job) => {

            const matchesSearch =
                !q ||
                job.title.toLowerCase().includes(q)

            return matchesSearch;

        });
    }, [search, jobs]);


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
        return (
            <main style={styles.jobsPageStyle} >
                <h1 style={styles.pageH1Styles}>No jobs found</h1>
                <div style={styles.summaryContainer} aria-label="Job summary" role="region">
                    <SummaryPanel jobs={filteredJobs} />
                </div>
                <div style={styles.controls}>
                    <JobSearch value={search} onChange={setSearch} />
                    <JobFilter value={roleType} onChange={setRoleType} ariaLabel={"Role"} />
                    <JobRelevanceFilter value={relevance} onChange={setRelevance} ariaLabel={"Relevance"} />
                    <JobResumeFilter value={recommendedResume} onChange={setRecommendedResume} ariaLabel={"Resume"} />
                </div>
            </main >
        );
    }


    return (
        <main style={styles.jobsPageStyle}>
            <h1 style={styles.pageH1Styles}>Jobs</h1>
            <div style={styles.summaryContainer} aria-label="Job summary" role="region">
                <SummaryPanel jobs={filteredJobs} />
            </div>
            <div style={styles.controls}>
                <JobSearch value={search} onChange={setSearch} />
                <JobFilter value={roleType} onChange={setRoleType} ariaLabel={"Role"} />
                <JobRelevanceFilter value={relevance} onChange={setRelevance} ariaLabel={"Relevance"} />
                <JobResumeFilter value={recommendedResume} onChange={setRecommendedResume} ariaLabel={"Resume"} />
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
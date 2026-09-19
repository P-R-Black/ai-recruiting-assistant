import type { Job, JobFilters } from "../types";

const API_URL = "http://127.0.0.1:8000/jobs/"

export async function getJobs(filters: JobFilters = {}): Promise<Job[]> {
    const params = new URLSearchParams();

    if (filters.is_relevant !== undefined) {
        params.set(
            "is_relevant",
            String(filters.is_relevant)
        )
    }

    if (filters.role_type !== undefined) {
        params.set("role_type", filters.role_type);
    }

    if (filters.recommended_resume !== undefined) {
        params.set('recommended_resume', filters.recommended_resume)
    }

    const queryString = params.toString();
    const url = queryString ? `${API_URL}?${queryString}` : API_URL;

    const response = await fetch(url);
    if (!response.ok) {
        throw new Error("Failed to fetch jobs");
    }

    const jobs: Job[] = await response.json();
    return jobs;
}


export async function getJob(jobId: string): Promise<Job> {
    const response = await fetch(`${API_URL}${jobId}`);

    if (!response.ok) {
        throw new Error("Failed to fetch job");
    }

    const job: Job = await response.json();

    return job;
}

export async function deleteJob(jobId: string): Promise<void> {

    const response = await fetch(`${API_URL}${jobId}`, {
        method: "DELETE",
    });

    if (!response.ok) {
        throw new Error("Failed to delete job");
    }
}


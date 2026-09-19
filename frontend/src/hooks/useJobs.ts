import { useQuery } from "@tanstack/react-query";
import { getJobs, getJob } from "../api/jobs";
import type { JobFilters } from "../types";


export function useJobs(filters: JobFilters = {}) {
    return useQuery({
        queryKey: ["jobs", filters],
        queryFn: () => getJobs(filters),
    })
}

export function useJob(jobId: string | undefined) {
    return useQuery({
        queryKey: ["job", jobId],
        queryFn: () => getJob(jobId!),
        enabled: !!jobId,
    })
}
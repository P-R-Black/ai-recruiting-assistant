import { useQuery } from "@tanstack/react-query";
import { getJobs } from "../api/jobs";
import type { JobFilters } from "../types";


export function useJobs(filters: JobFilters = {}) {
    return useQuery({
        queryKey: ["jobs", filters],
        queryFn: () => getJobs(filters),
    })
}
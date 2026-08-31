import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { renderHook, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";

import { describe, expect, it, vi, beforeEach } from "vitest";

import { useJobs } from "./useJobs";
import { getJobs } from "../api/jobs";


vi.mock("../api/jobs", () => ({
    getJobs: vi.fn(),
}));

const mockJobs = [
    {
        id: "1",
        title: "Frontend Developer",
        company: "OpenAI",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        salary_min: 100000,
        salary_max: 150000,
        salary_currency: "USD",
        description: "Build frontend applications",
        job_url: "https://example.com/job/1",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "abc123",
        role_type: "frontend",
        recommended_resume: "frontend",
        is_relevant: true,
    },
];

describe("useJobs", () => {
    function createWrapper() {
        const queryClient = new QueryClient({
            defaultOptions: {
                queries: {
                    retry: false,
                },
            },
        });

        return function Wrapper({
            children,
        }: {
            children: ReactNode;
        }) {
            return (
                <QueryClientProvider client={queryClient}>
                    {children}
                </QueryClientProvider>
            );
        };
    }

    it("returns jobs from getJobs", async () => {
        vi.mocked(getJobs).mockResolvedValue(mockJobs);

        const { result } = renderHook(() => useJobs(), {
            wrapper: createWrapper(),
        });

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true);
        });

        expect(result.current.data).toEqual(mockJobs);

        expect(getJobs).toHaveBeenCalledTimes(1);
    });

    it("returns an error when getJobs fails", async () => {
        vi.mocked(getJobs).mockRejectedValue(
            new Error("Failed to fetch jobs")
        );

        const { result } = renderHook(() => useJobs(), {
            wrapper: createWrapper(),
        });

        await waitFor(() => {
            expect(result.current.isError).toBe(true);
        });

        expect(result.current.error).toBeInstanceOf(Error);

        expect(result.current.error?.message).toBe(
            "Failed to fetch jobs"
        );
    });

    it("returns an error when getJobs fails", async () => {
        vi.mocked(getJobs).mockRejectedValue(
            new Error("Failed to fetch jobs")
        );

        const { result } = renderHook(() => useJobs(), {
            wrapper: createWrapper(),
        });

        await waitFor(() => {
            expect(result.current.isError).toBe(true);
        });

        expect(result.current.error).toBeInstanceOf(Error);

        expect(result.current.error?.message).toBe(
            "Failed to fetch jobs"
        );
    });
});
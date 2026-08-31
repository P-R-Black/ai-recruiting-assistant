import { describe, expect, it, vi, beforeEach } from "vitest";


import { getJobs } from "./jobs";

describe("getJobs", () => {
    beforeEach(() => {
        vi.restoreAllMocks();
    });

    it("returns jobs when the request is successful", async () => {
        const mockJobs = [
            {
                id: "123",
                title: "Frontend Developer",
                company: "OpenAI",
                location: "Orlando, FL",
                employment_type: null,
                work_location: "remote",
                recruiter_name: null,
                salary_min: 100000,
                salary_max: 150000,
                salary_currency: "USD",
                description: "Frontend developer position",
                job_url: "https://example.com/job",
                source: "mail",
                status: "new",
                email_id: "456",
                fingerprint: "abc123",
                role_type: "frontend",
                recommended_resume: "frontend",
                is_relevant: true,
                created_at: "2026-08-28T12:00:00Z",
                updated_at: "2026-08-28T12:00:00Z",
            }
        ];

        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(JSON.stringify(mockJobs), {
                status: 200,
                headers: {
                    "Content-Type": "application/json",

                },
            }),
        );

        const jobs = await getJobs();

        expect(jobs).toEqual(mockJobs);

        expect(fetch).toHaveBeenCalledWith(
            "http://127.0.0.1:8000/jobs/"
        )
    })

    it("throws an error when the request fails", async () => {
        vi.spyOn(globalThis, "fetch").mockResolvedValue(
            new Response(null, {
                status: 500,
            }),
        );

        await expect(getJobs()).rejects.toThrow(
            "Failed to fetch jobs",
        );
    });
})
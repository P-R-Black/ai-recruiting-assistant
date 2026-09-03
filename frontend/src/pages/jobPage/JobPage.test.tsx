import { render, screen } from "@testing-library/react";
import { vi, describe, it, expect } from "vitest";

import { JobsPage } from "./JobPage";
import { useJobs } from "../../hooks/useJobs";

vi.mock("../../hooks/useJobs", () => ({
    useJobs: vi.fn(),
}));

const jobs = [
    {
        id: "1",
        title: "Frontend Developer",
        company: "Acme Inc.",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: 80,
        salary_max: 120,
        salary_currency: "USD",
        description: "Frontend development role",
        job_url: "https://example.com/job/1",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "a".repeat(64),
        role_type: "frontend",
        recommended_resume: "frontend",
        is_relevant: true,
        created_at: "",
        updated_at: ""
    }
];

const mockedUseJobs = vi.mocked(useJobs);

describe("JobsPage", () => {
    it("shows loading text while jobs are loading", () => {
        mockedUseJobs.mockReturnValue({
            data: undefined,
            isLoading: true,
            isError: false,
            error: null,
        } as unknown as ReturnType<typeof useJobs>);

        render(<JobsPage />);

        expect(
            screen.getByText("Loading jobs...")
        ).toBeInTheDocument();
    });

    it("shows a message when no jobs are found", () => {
        mockedUseJobs.mockReturnValue({
            data: [],
            isLoading: false,
            isError: false,
            error: null,
        } as unknown as ReturnType<typeof useJobs>);

        render(<JobsPage />);

        expect(
            screen.getByText("No jobs found.")
        ).toBeInTheDocument();
    });

    it("shows an error message when loading jobs fails", () => {
        mockedUseJobs.mockReturnValue({
            data: undefined,
            isLoading: false,
            isError: true,
            error: new Error("Failed to fetch"),
        } as ReturnType<typeof useJobs>);

        render(<JobsPage />);

        expect(
            screen.getByText(/Error loading jobs: Failed to fetch/)
        ).toBeInTheDocument();
    });

    it("renders jobs when jobs are successfully loaded", () => {
        mockedUseJobs.mockReturnValue({
            data: jobs,
            isLoading: false,
            isError: false,
            error: null,
        } as ReturnType<typeof useJobs>);

        render(<JobsPage />);

        expect(
            screen.getByRole("heading", {
                name: "Jobs",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByText("Frontend Developer")
        ).toBeInTheDocument();
    });
});

// npx vitest
import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
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
    },
    {
        id: "2",
        title: "Backend Developer",
        company: "Acme Inc.",
        location: "Kissimmee, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: 80,
        salary_max: 120,
        salary_currency: "USD",
        description: "Backend development role",
        job_url: "https://example.com/job/1",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "a".repeat(64),
        role_type: "backend",
        recommended_resume: "backend",
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
            screen.getByText("No jobs found")
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

    it("shows a summary of the displayed jobs", async () => {
        // mock useJobs with several jobs

        render(<JobsPage />);

        const summary = screen.getByRole("region", { name: "Job summary", });
        expect(within(summary).getByText("Total Jobs")).toBeInTheDocument();
        expect(within(summary).getByText("Frontend")).toBeInTheDocument();
        expect(within(summary).getByText("Backend")).toBeInTheDocument();
    });

    it("passes the selected role type to useJobs", async () => {
        const user = userEvent.setup();

        render(<JobsPage />);

        await user.selectOptions(
            screen.getByRole("combobox", { name: "Role" }),
            "frontend"
        );

        await user.selectOptions(
            screen.getByRole("combobox", { name: "Relevance" }),
            "relevant"
        );

        await user.selectOptions(
            screen.getByRole("combobox", { name: "Resume" }),
            "backend"
        );

        expect(useJobs).toHaveBeenLastCalledWith({
            role_type: "frontend",
            is_relevant: true,
            recommended_resume: "backend"

        });
    });

    it("passes the selected relevance filter to useJobs", async () => {
        const user = userEvent.setup();

        render(<JobsPage />);

        await user.selectOptions(
            screen.getByRole("combobox", { name: /relevance/i }),
            "Relevant"
        );

        expect(useJobs).toHaveBeenLastCalledWith({
            is_relevant: true,
        });
    });

});

// npx vitest
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SummaryPanel } from "./SummaryPanel";
import type { Job } from "../../types";

const mockJobs: Job[] = [
    {
        id: "1",
        title: "Frontend Developer",
        company: "Company A",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: null,
        salary_max: null,
        salary_currency: null,
        description: "Frontend job",
        job_url: "https://example.com/1",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "abc",
        role_type: "frontend",
        recommended_resume: "frontend",
        is_relevant: true,
        created_at: "",
        updated_at: "",
    },
    {
        id: "2",
        title: "React Developer",
        company: "Company B",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: null,
        salary_max: null,
        salary_currency: null,
        description: "Frontend job",
        job_url: "https://example.com/2",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "def",
        role_type: "frontend",
        recommended_resume: "frontend",
        is_relevant: true,
        created_at: "",
        updated_at: "",
    },
    {
        id: "3",
        title: "Software Engineer",
        company: "Company C",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: null,
        salary_max: null,
        salary_currency: null,
        description: "Backend job",
        job_url: "https://example.com/3",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "ghi",
        role_type: "backend",
        recommended_resume: "backend",
        is_relevant: true,
        created_at: "",
        updated_at: "",
    },
    {
        id: "4",
        title: "Some Other Job",
        company: "Company D",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: null,
        salary_max: null,
        salary_currency: null,
        description: "Unknown role",
        job_url: "https://example.com/4",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "jkl",
        role_type: "unknown",
        recommended_resume: "unknown",
        is_relevant: false,
        created_at: "",
        updated_at: "",
    },
    {
        id: "5",
        title: "Another Job",
        company: "Company E",
        location: "Orlando, FL",
        employment_type: null,
        work_location: null,
        recruiter_name: null,
        salary_min: null,
        salary_max: null,
        salary_currency: null,
        description: "Unknown role",
        job_url: "https://example.com/5",
        source: "mail",
        status: "new",
        email_id: null,
        fingerprint: "mno",
        role_type: "unknown",
        recommended_resume: "unknown",
        is_relevant: false,
        created_at: "",
        updated_at: "",
    },
];

describe("SummaryCard", () => {
    it("displays the total number of jobs", () => {
        render(<SummaryPanel jobs={mockJobs} />);

        expect(screen.getByText("Total Jobs")).toBeInTheDocument();
        expect(screen.getByText("5")).toBeInTheDocument();
    });

    it("groups jobs with the same role into a single summary card", () => {
        render(<SummaryPanel jobs={mockJobs} />);

        const frontendLabel = screen.getByText("Frontend");
        const backendLabel = screen.getByText("Backend");
        const unknownLabel = screen.getByText("Unknown");

        expect(frontendLabel.parentElement).toHaveTextContent("Frontend");
        expect(frontendLabel.parentElement).toHaveTextContent("2");

        expect(backendLabel.parentElement).toHaveTextContent("Backend");
        expect(backendLabel.parentElement).toHaveTextContent("1");

        expect(unknownLabel.parentElement).toHaveTextContent("Unknown");
        expect(unknownLabel.parentElement).toHaveTextContent("2");
    });

    it("counts jobs with no role as Unknown", () => {
        const jobs = [
            ...mockJobs,
            {
                ...mockJobs[0],
                id: "6",
                role_type: null,
            },
        ];



        render(
            <SummaryPanel
                jobs={jobs.map((job) => ({
                    ...job,
                    role_type: job.role_type ?? "unknown",
                    count: 1,
                    recommended_resume: job.recommended_resume ?? "unknown",
                }))}
            />,
        );

        const unknownLabel = screen.getByText("Unknown");
        expect(unknownLabel.parentElement).toHaveTextContent("3");
    });

});
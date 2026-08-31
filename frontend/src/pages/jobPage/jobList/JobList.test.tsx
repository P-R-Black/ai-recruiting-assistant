import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";

import { JobList } from "./JobList";
import type { Job } from "../../../types";



describe("JobList", () => {
    const jobs: Job[] = [
        {
            id: "1",
            title: "Frontend Developer",
            company: "Acme",
            location: "Orlando, FL",
            employment_type: null,
            work_location: null,
            recruiter_name: null,
            salary_min: 80,
            salary_max: 110,
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
            company: "Example Corp",
            location: "Remote",
            employment_type: null,
            work_location: null,
            recruiter_name: null,
            salary_min: 90,
            salary_max: 130,
            salary_currency: "USD",
            description: "Backend development role",
            job_url: "https://example.com/job/2",
            source: "mail",
            status: "new",
            email_id: null,
            fingerprint: "b".repeat(64),
            role_type: "backend",
            recommended_resume: "backend",
            is_relevant: true,
            created_at: "",
            updated_at: ""
        },
    ];

    it("renders a JobCard for each job", () => {
        render(<JobList jobs={jobs} />);

        expect(
            screen.getByText("Frontend Developer")
        ).toBeInTheDocument();

        expect(
            screen.getByText("Backend Developer")
        ).toBeInTheDocument();
    });
});
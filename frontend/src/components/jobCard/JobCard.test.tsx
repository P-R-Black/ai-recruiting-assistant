import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { JobCard } from "./JobCard";
import type { Job } from "../../types";


const job: Job = {
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
};

describe("JobCard", () => {
    it("renders job information", () => {
        render(<JobCard job={job} />);

        expect(
            screen.getByText("Acme Inc.")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                name: "Frontend Developer",
            })
        ).toBeInTheDocument();

        const role = screen.getByText("Role:").closest("p")
        expect(
            role
        ).toHaveTextContent("Role: Frontend");

        const recommendedResume = screen
            .getByText("Recommended Resume:")
            .closest("p");

        expect(recommendedResume).toHaveTextContent(
            "Recommended Resume: Frontend"
        );

        const relevant = screen.getByText("Relevant:").closest("p")
        expect(
            relevant
        ).toHaveTextContent("Relevant: Yes");

        expect(
            screen.getByText(/Orlando, FL/)
        ).toBeInTheDocument();
    });

    it("formats a USD salary range", () => {
        render(<JobCard job={job} />);

        const salary = screen.getByText((_, element) => {
            return (
                element?.tagName.toLowerCase() === "p" &&
                element.textContent?.includes("$80K - $120K") === true
            );
        });

        expect(salary).toBeInTheDocument();
    });

    it("shows Not listed when salary is missing", () => {
        const jobWithoutSalary: Job = {
            ...job,
            salary_min: null,
            salary_max: null,
            salary_currency: null,
        };

        render(<JobCard job={jobWithoutSalary} />);

        expect(
            screen.getByText(/Not listed/)
        ).toBeInTheDocument();
    });

    it("formats EUR salaries with the euro symbol", () => {
        const euroJob: Job = {
            ...job,
            salary_min: 70,
            salary_max: 90,
            salary_currency: "EUR",
        };

        render(<JobCard job={euroJob} />);

        expect(
            screen.getByText(/€70K - €90K/)
        ).toBeInTheDocument();
    });

    it("formats GBP salaries with the pound symbol", () => {
        const poundJob: Job = {
            ...job,
            salary_min: 70,
            salary_max: 90,
            salary_currency: "GBP",
        };

        render(<JobCard job={poundJob} />);

        expect(
            screen.getByText(/£70K - £90K/)
        ).toBeInTheDocument();
    });

    it("truncates a long company name", () => {
        const longCompany =
            "This Is An Extremely Long Company Name That Should Be Truncated";

        const longCompanyJob: Job = {
            ...job,
            company: longCompany,
        };

        render(<JobCard job={longCompanyJob} />);

        expect(
            screen.getByText("This Is An Extremely Long Compa...")
        ).toBeInTheDocument();

        expect(
            screen.queryByText(longCompany)
        ).not.toBeInTheDocument();
    });


    it("truncates a long company name", () => {
        const longCompany =
            "This Is An Extremely Long Company Name That Should Be Truncated";

        const longCompanyJob: Job = {
            ...job,
            company: longCompany,
        };

        render(<JobCard job={longCompanyJob} />);

        expect(
            screen.getByText("This Is An Extremely Long Compa...")
        ).toBeInTheDocument();

        expect(
            screen.queryByText(longCompany)
        ).not.toBeInTheDocument();
    });

    it("renders a link to the job", () => {
        render(<JobCard job={job} />);

        const link = screen.getByRole("link", {
            name: "View Job",
        });

        expect(link).toHaveAttribute(
            "href",
            job.job_url
        );

        expect(link).toHaveAttribute(
            "target",
            "_blank"
        );

        expect(link).toHaveAttribute(
            "rel",
            "noopener noreferrer"
        );
    });
});
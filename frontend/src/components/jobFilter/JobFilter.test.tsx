import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { JobFilter } from "./JobFilter";

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

describe("JobFilter", () => {
    it("renders the filter options", () => {
        render(
            <JobFilter
                value="all"
                onChange={vi.fn()}
            />
        );

        expect(screen.getByRole("combobox")).toBeInTheDocument();

        expect(screen.getByRole("option", {
            name: "All Roles",
        })).toBeInTheDocument();

        expect(screen.getByRole("option", {
            name: "Frontend",
        })).toBeInTheDocument();

        expect(screen.getByRole("option", {
            name: "Backend",
        })).toBeInTheDocument();

        expect(screen.getByRole("option", {
            name: "Full Stack",
        })).toBeInTheDocument();

        expect(screen.getByRole("option", {
            name: "Non Software",
        })).toBeInTheDocument();

        expect(screen.getByRole("option", {
            name: "Unknown",
        })).toBeInTheDocument();
    });

    it("shows the current selected value", () => {
        render(
            <JobFilter
                value="frontend"
                onChange={vi.fn()}
            />
        );

        expect(screen.getByRole("combobox")).toHaveValue("frontend");
    });

    it("calls onChange when the selected filter changes", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();

        render(
            <JobFilter
                value="all"
                onChange={onChange}
            />
        );

        await user.selectOptions(
            screen.getByRole("combobox"),
            "frontend"
        );

        expect(onChange).toHaveBeenCalledWith("frontend");
    });

    it("can select non_software", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();

        render(
            <JobFilter
                value="all"
                onChange={onChange}
            />
        );

        await user.selectOptions(
            screen.getByRole("combobox"),
            "non_software"
        );

        expect(onChange).toHaveBeenCalledWith("non_software");
    });
});
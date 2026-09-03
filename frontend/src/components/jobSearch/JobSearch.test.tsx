import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";
import { JobSearch } from "./JobSearch";


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

describe("JobSearch", () => {
    it("renders the search input", () => {
        render(
            <JobSearch
                value=""
                onChange={vi.fn()}
            />
        );

        expect(
            screen.getByPlaceholderText("Search jobs by title...")
        ).toBeInTheDocument();
    });

    it("shows the current search value", () => {
        render(
            <JobSearch
                value="frontend developer"
                onChange={vi.fn()}
            />
        );

        expect(
            screen.getByRole("textbox")
        ).toHaveValue("frontend developer");
    });

    it("calls onChange when the user types", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();

        let value = "";

        const handleChange = (newValue: string) => {
            value = newValue;
            onChange(newValue);
        };

        const { rerender } = render(
            <JobSearch
                value={value}
                onChange={handleChange}
            />
        );

        const input = screen.getByRole("textbox");

        for (const character of "frontend") {
            await user.type(input, character);

            rerender(
                <JobSearch
                    value={value}
                    onChange={handleChange}
                />
            );
        }

        expect(onChange).toHaveBeenLastCalledWith("frontend");
    });

    it("shows the clear button when there is a search value", () => {
        render(
            <JobSearch
                value="frontend"
                onChange={vi.fn()}
            />
        );

        expect(
            screen.getByRole("button")
        ).toBeInTheDocument();
    });

    it("clears the search when the clear button is clicked", async () => {
        const user = userEvent.setup();
        const onChange = vi.fn();

        render(
            <JobSearch
                value="frontend"
                onChange={onChange}
            />
        );

        await user.click(screen.getByRole("button"));

        expect(onChange).toHaveBeenCalledWith("");
    });

    it("does not show the clear button when the search is empty", () => {
        render(
            <JobSearch
                value=""
                onChange={vi.fn()}
            />
        );

        expect(
            screen.queryByRole("button")
        ).not.toBeInTheDocument();
    });
});
import { render, screen } from "@testing-library/react";
import { vi, describe, it, expect } from "vitest";

import { JobsPage } from "./JobPage";
import { useJobs } from "../../hooks/useJobs";

vi.mock("../../hooks/useJobs", () => ({
    useJobs: vi.fn(),
}));

const mockedUseJobs = vi.mocked(useJobs);

describe("JobsPage", () => {
    it("shows loading text while jobs are loading", () => {
        mockedUseJobs.mockReturnValue({
            data: undefined,
            isLoading: true,
            isError: false,
            error: null,
        } as ReturnType<typeof useJobs>);

        render(<JobsPage />);

        expect(
            screen.getByText("Loading jobs...")
        ).toBeInTheDocument();
    });
});
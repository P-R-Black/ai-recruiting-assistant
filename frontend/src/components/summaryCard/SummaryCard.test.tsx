import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { SummaryCard } from "./SummaryCard";

describe("SummaryCard", () => {
    it("renders the label", () => {
        render(
            <SummaryCard
                label="Total Jobs"
                value="10"
                accent="6366f1"
            />
        );

        expect(screen.getByText("Total Jobs")).toBeInTheDocument();
    });

    it("renders the value", () => {
        render(
            <SummaryCard
                label="Total Jobs"
                value="10"
                accent="6366f1"
            />
        );

        expect(screen.getByText("10")).toBeInTheDocument();
    });

    it("applies the accent color to the top border", () => {
        render(
            <SummaryCard
                label="Total Jobs"
                value="10"
                accent="6366f1"
            />
        );

        const card = screen.getByText("Total Jobs").parentElement;

        expect(card).toHaveStyle({
            borderTop: "4px solid 6366f1",
        });
    });


});
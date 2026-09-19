import type { JobCardProps, Job } from "../../types"
import { JobDeleteButton } from "../jobDeleteButton/JobDeleteButton"

import { ROLE_COLORS, roleTypes, resumeRecommendations } from "../../constants/constants"


export function JobCardDetail({ job, }: JobCardProps) {


    const formatCurrency = (currency: string) => {
        if (!currency) {
            return "Not listed"
        }

        if (currency === "USD") {
            return "$"
        }

        if (currency === "EUR") {
            return "€"
        }

        if (currency === "GBP") {
            return "£"
        }

        return currency
    }



    const formatSalary = (job: Job) => {
        if (
            job.salary_min === null && job.salary_max === null
        ) {
            return "Not listed"
        }

        const currency = job.salary_currency ?? "";
        const currency_symbol = formatCurrency(currency)

        if (
            job.salary_min !== null && job.salary_max !== null
        ) {
            return `${currency_symbol}${job.salary_min.toLocaleString()} - ${currency_symbol}${job.salary_max.toLocaleString()}`;
        }

        if (job.salary_min !== null) {
            return `${currency_symbol}${job.salary_min.toLocaleString()}`
        }

        return `${currency_symbol}${job.salary_max?.toLocaleString()}`
    }



    return (
        <article style={{
            ...styles.cardBorder, borderLeft: `7px solid ${job.role_type ?
                ROLE_COLORS[job.role_type] : "Unknown"}`
        }}>
            <header style={styles.cardSectionDivider}>
                <p style={styles.companyName}><span>🏢</span> {job.company}</p>
            </header>
            <section>
                <h2 style={styles.cardJobTitle}>{job.title}</h2>
            </section>
            <section style={{ ...styles.badgeSpacing }}>
                <span style={styles.badge}>{job.employment_type ? job.employment_type : "Unknown"}</span>
                <span style={styles.badge}>{job.work_location ? job.work_location : "Unknown"}</span>
            </section>
            <div style={styles.cardSectionDivider}></div>
            <section style={styles.roleResumeBlock}>
                <p style={styles.cardParagraphMarginReduction}><strong>Role:</strong>{" "}
                    {job.role_type ? roleTypes[job.role_type] : "Unknown"}
                </p>
                <p style={styles.cardParagraphMarginReduction}><strong>Recommended Resume:</strong>{" "}
                    {job.recommended_resume ?
                        resumeRecommendations[job.recommended_resume] : "Unknown"}
                </p>
                <p style={styles.cardParagraphMarginReduction}>
                    <strong>Relevant:</strong>{" "}
                    {job.is_relevant ? "Yes" : "No"}
                </p>
            </section>
            <div style={styles.cardSectionDivider}></div>
            <footer style={styles.cardFooter}>
                <div style={styles.salaryLocationBlock}>
                    <p style={styles.cardJobSalary}><span>💰</span> {formatSalary(job)}</p>
                    <p style={styles.cardLocation}><span>📍</span> {job.location ?? "Not Listed"}</p>
                </div>
                <div style={styles.cardButtonContainer}>

                    <div className="innerCardButtonContainer">
                        <a style={styles.cardButton}
                            className="cardButton"
                            href={job.job_url}
                            target="_blank"
                            rel="noopener noreferrer">
                            View Job
                        </a>
                    </div>
                    <div className="innerCardButtonContainer">
                        <JobDeleteButton jobId={job.id} />
                    </div>
                </div>

            </footer>
        </article>
    )

}


const styles = {
    cardBorder: {
        alignItems: "flex-start",
        background: "var(--off-primary)",
        borderRadius: "10px",
        display: "flex",
        flexDirection: "column" as const,
        padding: "1rem 2rem",
        marginBottom: "2.2rem",
        // minWidth: "10rem",
        // maxWidth: "18rem",

        width: "93%"
    },

    companyName: {
        color: "var(--primary-text)",
        fontSize: ".80rem",
        fontWeight: "600",
        textAlign: "left" as "left",
        // marginBottom: ".5rem",
    },

    cardJobTitle: {
        textAlign: "left" as "left",
        marginBottom: ".25rem",

    },

    badge: {
        backgroundColor: "var(--highlight-text)",
        borderRadius: "3px",
        color: "var(--inverse-secondary)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: ".70rem",
        height: "1rem",
        padding: "0.05rem 0.50rem",

    },

    badgeSpacing: {
        display: "flex",
        justifyContent: "flex-start",
        gap: "2rem",
        marginBottom: ".5rem",
    },

    roleResumeBlock: {
        color: "var(--primary-text)",
        display: "flex",
        flexDirection: "column" as const,
        fontSize: ".90rem",
        marginBottom: ".5rem",
        textAlign: "left" as 'left',
    },

    salaryLocationBlock: {
        display: "flex",
        flexDirection: "column" as const,

    },
    cardFooter: {
        alignItems: "flex-start",
        display: "flex",
        gap: "1rem",
        flexDirection: "column",
        width: "100%",
    },

    cardLocation: {
        color: "var(--primary-text)",
        fontSize: ".75rem",
        fontWeight: "400",
        textAlign: "left" as const

    },

    cardJobSalary: {
        color: "var(--primary-text)",
        fontSize: ".85rem",
        fontWeight: "600",
        textAlign: "left" as "left",
        marginBottom: "-.25rem"

    },



    cardParagraphMarginReduction: {
        marginBottom: "-.25rem",
    },

    cardSectionDivider: {
        borderBottom: "1px solid var(--highlight-text)",
        marginBottom: ".5rem",
        width: "100%",


    },

    cardButton: {
        alignItems: "center",
        backgroundColor: "var(--primary-text)",
        border: "none",
        borderRadius: "5px",
        color: "var(--secondary-text)",
        cursor: "pointer",
        display: "flex",
        fontSize: ".75rem",
        height: ".90rem",
        justifyContent: "center",
        padding: "0.05rem 0.50rem",
        textDecoration: "none",
        width: "auto",
        zIndex: "1",

    },


    cardButtonContainer: {
        alignItems: "center",
        // border: "2px solid yellow",
        width: "100%",
        display: "flex",
        gap: "1rem",

    }


}
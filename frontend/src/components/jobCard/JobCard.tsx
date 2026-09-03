import type { JobCardProps, Job } from "../../types"

const COMPANY_NAME_TEXT_LENGTH = 31
const JOB_TITLE_TEXT_LENGTH = 24

export function JobCard({ job, }: JobCardProps) {


    const roleTypes: Record<string, string> = {
        "backend": "Backend",
        "frontend": "Frontend",
        "full_stack": "Full Stack",
        "non_software": "Non Software",
        "unknown": "Unknown",
        "software": "Software Engineer",
        "software_engineer": "Software Engineer",
    }

    const resumeRecommendations: Record<string, string> = {
        "backend": "Backend",
        "frontend": "Frontend",
        "full_stack": "Full Stack",
        "non_software": "Non Software",
        "unknown": "Unknown",
    }

    const ROLE_COLORS: Record<string, string> = {
        "backend": "#10b981",
        "frontend": "#f2ab1c",
        "full_stack": "#f31515",
        "non_software": "#090162",
        "unknown": "#7f7d7d",
    };





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

    const truncateCompanyName = (text: string) => {
        if (!text) {
            return " "
        }

        if (text.length > COMPANY_NAME_TEXT_LENGTH) {
            return text.slice(0, COMPANY_NAME_TEXT_LENGTH) + "..."
        }

        return text;

    }

    const truncateJobTitle = (text: string) => {
        if (!text) {
            return " "
        }

        if (text.length > JOB_TITLE_TEXT_LENGTH) {
            return text.slice(0, JOB_TITLE_TEXT_LENGTH) + "..."
        }

        return text

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
            return `${currency_symbol}${job.salary_min.toLocaleString()}K - ${currency_symbol}${job.salary_max.toLocaleString()}K`;
        }

        if (job.salary_min !== null) {
            return `${currency_symbol}${job.salary_min.toLocaleString()}K`
        }

        return `${currency_symbol}${job.salary_max?.toLocaleString()}K`
    }





    return (
        <article style={{
            ...styles.cardBorder, borderLeft: `7px solid ${job.recommended_resume ?
                ROLE_COLORS[job.recommended_resume] : "Unknown"}`
        }}>
            <header style={styles.cardSectionDivider}>
                <p style={styles.companyName}><span>🏢</span> {truncateCompanyName(job.company)}</p>
            </header>
            <section>
                <h2 style={styles.cardJobTitle}>{truncateJobTitle(job.title)}</h2>
            </section>
            <section style={{ ...styles.badgeSpacing }}>
                <span style={styles.badge}>Full Time</span>
                <span style={styles.badge}>Hybrid/Remote</span>
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
                <div className="cardButtonContainer">
                    <a style={styles.cardButton}
                        className="cardButton"
                        href={job.job_url}
                        target="_blank"
                        rel="noopener noreferrer">
                        View Job
                    </a>
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
        color: "var(--inverse-primary)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: ".70rem",
        height: "1rem",
        padding: "0.05rem 0.50rem",

    },

    badgeSpacing: {
        display: "flex",
        justifyContent: "space-between",
        width: "70%",
        marginRight: "2rem",
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
        alignItems: "center",
        display: "flex",
        justifyContent: "space-between",
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

    cardButton: {
        alignItems: "center",
        backgroundColor: "var(--primary-text)",
        borderRadius: "5px",
        color: "var(--secondary-text)",
        display: "flex",
        fontSize: ".75rem",
        height: ".90rem",
        justifyContent: "center",
        padding: "0.05rem 0.50rem",
        textDecoration: "none",
        width: "3.75rem",
        zIndex: "1",

    },



    cardParagraphMarginReduction: {
        marginBottom: "-.25rem",
    },

    cardSectionDivider: {
        borderBottom: "1px solid var(--highlight-text)",
        marginBottom: ".5rem",
        width: "100%"
    }


}
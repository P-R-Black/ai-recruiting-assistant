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

        return text

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
        <article style={styles.cardBorder}>
            <header>
                <p style={styles.companyName}><span>🏢</span> {truncateCompanyName(job.company)}</p>
            </header>
            <section>
                <h2 style={styles.cardJobTitle}>{truncateJobTitle(job.title)}</h2>
            </section>
            <section style={styles.badgeSpacing}>
                <span style={styles.badge}>Full Time</span>
                <span style={styles.badge}>Hybrid/Remote</span>
            </section>

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
            <footer style={styles.cardFooter}>
                <div style={styles.salaryLocationBlock}>
                    <p style={styles.cardJobSalary}><span>💰</span> {formatSalary(job)}</p>
                    <p style={styles.cardLocation}><span>📍</span> {job.location ?? "Not Listed"}</p>
                </div>
                <a style={styles.cardButton}
                    href={job.job_url}
                    target="_blank"
                    rel="noopener noreferrer">
                    View Job
                </a>

            </footer>
        </article>
    )

}


const styles = {
    cardBorder: {

        alignItems: "flex-start",
        border: "1px solid black",
        borderRadius: "10px",
        display: "flex",
        flexDirection: "column" as "column",
        padding: "1rem 2rem",
        width: "25%",

    },
    companyName: {
        color: "black",
        fontSize: ".85rem",
        fontWeight: "600",
        textAlign: "left" as "left",
        marginBottom: ".5rem",

    },

    cardJobTitle: {
        color: "black",
        fontSize: "1.20rem",
        fontWeight: "600",
        textAlign: "left" as "left",
        marginBottom: ".25rem",

    },

    badge: {
        backgroundColor: "#E0E0E0",
        display: "inline-block",
        padding: "0.05rem 0.50rem",
        borderRadius: "5px",
        color: "#000000",
        fontSize: ".75rem",
    },

    badgeSpacing: {
        display: "flex",
        justifyContent: "space-between",
        width: "70%",
        marginRight: "2rem",
        marginBottom: ".5rem",
    },

    roleResumeBlock: {
        color: "#000000",
        display: "flex",
        flexDirection: "column" as "column",
        fontSize: ".90rem",
        // border: "2px solid green",
        textAlign: "left" as 'left',
        marginBottom: ".5rem",
    },

    salaryLocationBlock: {
        display: "flex",
        flexDirection: "column" as "column",

    },
    cardFooter: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        width: "100%",
    },

    cardLocation: {
        fontSize: ".80rem",
        fontWeight: "400",
        textAlign: "left" as "left"

    },

    cardJobSalary: {
        color: "black",
        fontSize: ".85rem",
        fontWeight: "600",
        textAlign: "left" as "left",
        marginBottom: "-.25rem"

    },

    cardButton: {
        backgroundColor: "#000000",
        color: "#ffffff",
        padding: "0.05rem 0.50rem",
        borderRadius: "5px",
        fontSize: ".75rem",
        textDecoration: "None"
    },

    cardParagraphMarginReduction: {
        marginBottom: "-.25rem",
    }


}
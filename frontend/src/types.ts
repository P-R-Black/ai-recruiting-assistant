

export type Job = {
    id: string;
    title: string;
    company: string;

    location: string | null;
    employment_type: string | null;
    work_location: string | null;

    recruiter_name: string | null;

    salary_min: number | null;
    salary_max: number | null;
    salary_currency: string | null;

    description: string;
    job_url: string;

    source: string;
    status: string;

    email_id: string | null;
    fingerprint: string;

    role_type: string | null;
    recommended_resume: string | null;
    is_relevant: boolean | null;

    created_at: string;
    updated_at: string;
};

export type JobCardProps = {
    job: Job;
}

export type JobFilters = {
    is_relevant?: boolean;
    role_type?: string;
    recommended_resume?: string;
}
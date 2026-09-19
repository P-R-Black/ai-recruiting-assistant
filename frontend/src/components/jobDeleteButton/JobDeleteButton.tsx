import { useDeleteJob } from "../../hooks/useDeleteJob";


type JobDeleteButtonProps = {
    jobId: string;
}

export function JobDeleteButton({ jobId }: JobDeleteButtonProps) {

    const deleteJob = useDeleteJob();
    console.log('deleteJob:', deleteJob)

    function handleDelete() {
        if (!window.confirm("Are you sure you want to delete this job?")) {
            return;
        }
        deleteJob.mutate(jobId)
    }

    return (
        <button
            style={styles.cardButton}
            type="button"
            onClick={handleDelete}
            disabled={deleteJob.isPending}
        >
            {deleteJob.isPending ? "Deletin..." : "Delete Job"}

        </button>

    )

}

const styles = {
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


}
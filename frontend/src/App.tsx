// import { reactRouter } from "@react-router/dev/vite"
import { JobsPage } from "./pages/jobPage/JobPage";
import { JobDetailPage } from "./pages/jobDetail/JobDetailPage";
import { Route, Routes } from "react-router";


function App() {
    return (
        <Routes>
            <Route path="/jobs" element={<JobsPage />} />
            <Route path="/jobs/:jobId" element={<JobDetailPage />} />
        </Routes>
    );

    return (<JobsPage />);
}

export default App;
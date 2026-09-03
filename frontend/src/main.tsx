import './style.css'
// import typescriptLogo from './assets/typescript.svg'
// import viteLogo from './assets/vite.svg'
// import heroImg from './assets/hero.png'
// import { setupCounter } from './counter.ts'

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";


const queryClient = new QueryClient();

ReactDOM.createRoot(document.getElementById("app")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);

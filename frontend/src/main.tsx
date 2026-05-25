import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { Toaster } from "@/components/ui/sonner";
import { GlobalErrorBoundary } from "@/components/shared/global-error-boundary";
import { AppRoutes } from "@/routes";
import { applyTheme, useThemeStore } from "@/stores/theme-store";

import "./index.css";

applyTheme(useThemeStore.getState().theme);

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000,
      retry: 1,
    },
  },
});
import { initRealtime } from "@/lib/realtime";
import { useAuthStore } from "@/stores/auth-store";

// Manage a single realtime connection tied to the current auth token.
let _ws: WebSocket | null = null;
useAuthStore.subscribe((s) => s.accessToken, (token) => {
  try {
    if (token) {
      // open connection when token becomes available
      _ws = initRealtime(queryClient);
    } else {
      // close existing connection on logout
      if (_ws) {
        try { _ws.close(); } catch (e) { /* ignore */ }
        _ws = null;
      }
    }
  } catch (e) {
    // noop
  }
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <GlobalErrorBoundary>
        <AppRoutes />
      </GlobalErrorBoundary>
      <Toaster position="top-right" richColors closeButton />
    </QueryClientProvider>
  </StrictMode>,
);

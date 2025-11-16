import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import Details from "./pages/Details";
import Plan from "./pages/Plan";
import Mindmap from "./pages/Mindmap";
import Progress from "./pages/Progress";
import AITutor from "./pages/AITutor";
import History from "./pages/History";
import Game from "./pages/Game";
import Auth from "./pages/Auth";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/details" element={<Details />} />
          <Route path="/plan" element={<Plan />} />
          <Route path="/mindmap" element={<Mindmap />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/ai-tutor" element={<AITutor />} />
          <Route path="/history" element={<History />} />
          <Route path="/game" element={<Game />} />
          <Route path="/auth" element={<Auth />} />
          {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;

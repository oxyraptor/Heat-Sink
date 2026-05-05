import { useState } from "react";
import { motion } from "framer-motion";
import { Sparkles, Shapes, BarChart3 } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { CFDOptimization } from "./components/CFDOptimization";
import { DesignSuggestion } from "./components/DesignSuggestion";

const normalizeBaseUrl = (url: string): string => url.replace(/\/+$/, "");

const configuredBaseUrl = import.meta.env.VITE_API_BASE_URL as
  | string
  | undefined;
const API_BASE_URLS = configuredBaseUrl
  ? [normalizeBaseUrl(configuredBaseUrl)]
  : [
      "http://localhost:8001",
      "http://127.0.0.1:8001",
      "https://oxyraptor-heat-sink-backend.hf.space",
    ];

function App() {
  const [activeTab, setActiveTab] = useState("design");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 px-3 py-4 sm:px-6 lg:px-8 sm:py-8 overflow-x-hidden">
      <div className="max-w-7xl mx-auto w-full">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-6 sm:mb-8"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="bg-blue-500 p-2 rounded-lg">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-3xl sm:text-4xl font-bold text-white leading-tight">
              Fins Design Studio
            </h1>
          </div>
          <p className="text-slate-400 max-w-2xl">
            Design Synthesizer is the primary workflow for choosing fin shape
            and dimensions.
          </p>
        </motion.div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-8">
          <TabsList className="bg-slate-800 border border-slate-700 w-full flex flex-col sm:flex-row h-auto sm:h-10 p-1 gap-1">
            <TabsTrigger value="design" className="gap-2 w-full sm:w-auto">
              <Shapes className="w-4 h-4" />
              Design Synthesizer
            </TabsTrigger>
            <TabsTrigger value="cfd" className="gap-2 w-full sm:w-auto">
              <BarChart3 className="w-4 h-4" />
              CFD Optimization
            </TabsTrigger>
          </TabsList>

          <TabsContent value="design">
            <DesignSuggestion apiBaseUrls={API_BASE_URLS} />
          </TabsContent>

          <TabsContent value="cfd">
            <CFDOptimization apiBaseUrls={API_BASE_URLS} />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

export default App;

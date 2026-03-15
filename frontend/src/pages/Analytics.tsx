import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { AnalyticsCharts } from "@/components/AnalyticsCharts";
import { ChatBot } from "@/components/ChatBot";
import { Menu, Download } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Analytics() {
  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        <main className="flex-1 overflow-auto">
          {/* Header */}
          <header className="sticky top-0 z-10 bg-card/80 backdrop-blur-sm border-b border-border px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <SidebarTrigger className="lg:hidden">
                  <Menu className="w-5 h-5" />
                </SidebarTrigger>
                <div>
                  <h1 className="text-xl font-semibold text-foreground">Analytics</h1>
                  <p className="text-sm text-muted-foreground">
                    Detailed fraud detection insights
                  </p>
                </div>
              </div>
              <Button variant="outline" className="gap-2">
                <Download className="w-4 h-4" />
                Export Data
              </Button>
            </div>
          </header>

          {/* Content */}
          <div className="p-6">
            <AnalyticsCharts />
          </div>
        </main>
        <ChatBot />
      </div>
    </SidebarProvider>
  );
}

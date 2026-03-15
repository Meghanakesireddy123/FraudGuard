import { useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";

const generateTimeData = (period: string) => {
  const now = new Date();
  const data = [];

  if (period === "1H") {
    for (let i = 59; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 1000);
      data.push({
        time: time.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }),
        transactions: Math.floor(Math.random() * 50) + 10,
        fraud: Math.floor(Math.random() * 5),
      });
    }
  } else if (period === "24H") {
    for (let i = 23; i >= 0; i--) {
      const time = new Date(now.getTime() - i * 60 * 60 * 1000);
      data.push({
        time: time.toLocaleTimeString("en-US", { hour: "2-digit" }) + ":00",
        transactions: Math.floor(Math.random() * 500) + 100,
        fraud: Math.floor(Math.random() * 30) + 5,
      });
    }
  } else if (period === "7D") {
    for (let i = 6; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      data.push({
        time: date.toLocaleDateString("en-US", { weekday: "short" }),
        transactions: Math.floor(Math.random() * 5000) + 2000,
        fraud: Math.floor(Math.random() * 200) + 50,
      });
    }
  } else {
    for (let i = 29; i >= 0; i--) {
      const date = new Date(now.getTime() - i * 24 * 60 * 60 * 1000);
      data.push({
        time: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        transactions: Math.floor(Math.random() * 8000) + 3000,
        fraud: Math.floor(Math.random() * 300) + 100,
      });
    }
  }

  return data;
};

const pieData = [
  { name: "Genuine", value: 89, color: "hsl(160, 84%, 39%)" },
  { name: "Fraud", value: 11, color: "hsl(347, 77%, 50%)" },
];

const hourlyFraudData = [
  { hour: "00:00", fraud: 45 },
  { hour: "02:00", fraud: 52 },
  { hour: "04:00", fraud: 38 },
  { hour: "06:00", fraud: 22 },
  { hour: "08:00", fraud: 15 },
  { hour: "10:00", fraud: 18 },
  { hour: "12:00", fraud: 25 },
  { hour: "14:00", fraud: 20 },
  { hour: "16:00", fraud: 28 },
  { hour: "18:00", fraud: 35 },
  { hour: "20:00", fraud: 42 },
  { hour: "22:00", fraud: 58 },
];

export function AnalyticsCharts() {
  const [period, setPeriod] = useState("30D");
  const timeData = generateTimeData(period);

  return (
    <div className="space-y-6">
      {/* Time Filter */}
      <div className="flex justify-end">
        <Tabs value={period} onValueChange={setPeriod}>
          <TabsList className="bg-secondary">
            <TabsTrigger value="1H" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">1H</TabsTrigger>
            <TabsTrigger value="24H" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">24H</TabsTrigger>
            <TabsTrigger value="7D" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">7D</TabsTrigger>
            <TabsTrigger value="30D" className="data-[state=active]:bg-primary data-[state=active]:text-primary-foreground">30D</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* Main Line Chart */}
      <div className="bg-card rounded-xl border border-border p-6 shadow-card">
        <h3 className="text-lg font-semibold text-foreground mb-6">Transaction Volume</h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={timeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                tickLine={{ stroke: "hsl(var(--border))" }}
                interval="preserveStartEnd"
              />
              <YAxis
                tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                tickLine={{ stroke: "hsl(var(--border))" }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "hsl(var(--card))",
                  border: "1px solid hsl(var(--border))",
                  borderRadius: "8px",
                }}
              />
              <Line
                type="monotone"
                dataKey="transactions"
                stroke="hsl(var(--primary))"
                strokeWidth={2}
                dot={false}
                name="Total Transactions"
              />
              <Line
                type="monotone"
                dataKey="fraud"
                stroke="hsl(var(--fraud))"
                strokeWidth={2}
                dot={false}
                name="Fraud Detected"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        <div className="flex items-center gap-6 mt-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-primary" />
            <span className="text-sm text-muted-foreground">Total Transactions</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-fraud" />
            <span className="text-sm text-muted-foreground">Fraud Detected</span>
          </div>
        </div>
      </div>

      {/* Bottom Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Donut Chart */}
        <div className="bg-card rounded-xl border border-border p-6 shadow-card">
          <h3 className="text-lg font-semibold text-foreground mb-6">Fraud vs Genuine</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                  formatter={(value: number) => [`${value}%`, ""]}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex items-center justify-center gap-6 mt-4">
            {pieData.map((entry) => (
              <div key={entry.name} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: entry.color }}
                />
                <span className="text-sm text-muted-foreground">
                  {entry.name}: {entry.value}%
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Bar Chart - Fraud by Hour */}
        <div className="bg-card rounded-xl border border-border p-6 shadow-card">
          <h3 className="text-lg font-semibold text-foreground mb-6">Fraud by Hour (Peak Risk Times)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyFraudData}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                <XAxis
                  dataKey="hour"
                  tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                  tickLine={{ stroke: "hsl(var(--border))" }}
                />
                <YAxis
                  tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                  tickLine={{ stroke: "hsl(var(--border))" }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Bar
                  dataKey="fraud"
                  fill="hsl(var(--fraud))"
                  radius={[4, 4, 0, 0]}
                  name="Fraud Count"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}

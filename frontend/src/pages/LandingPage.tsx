import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Shield, TrendingUp, Brain, Bell, BarChart3, Lock } from "lucide-react";

export default function LandingPage() {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
            {/* Navigation */}
            <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <Shield className="w-8 h-8 text-primary" />
                            <span className="text-2xl font-bold text-gray-900">FraudGuard</span>
                        </div>
                        <div className="flex gap-3">
                            <Button
                                variant="outline"
                                onClick={() => navigate("/login")}
                                className="font-medium"
                            >
                                Sign In
                            </Button>
                            <Button
                                onClick={() => navigate("/register")}
                                className="font-medium"
                            >
                                Sign Up
                            </Button>
                        </div>
                    </div>
                </div>
            </nav>

            {/* Hero Section */}
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <div className="text-center">
                    <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-primary mb-6">
                        <Shield className="w-10 h-10 text-white" />
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
                        Real-Time Fraud Detection
                        <span className="block text-primary mt-2">Powered by AI</span>
                    </h1>
                    <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
                        Protect your financial transactions with cutting-edge machine learning.
                        FraudGuard analyzes transactions in real-time to detect and prevent fraudulent activities.
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Button
                            size="lg"
                            onClick={() => navigate("/register")}
                            className="text-lg px-8 py-6"
                        >
                            Get Started Free
                        </Button>
                        <Button
                            size="lg"
                            variant="outline"
                            onClick={() => navigate("/login")}
                            className="text-lg px-8 py-6"
                        >
                            View Demo
                        </Button>
                    </div>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-8 mt-24">
                    <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center mb-4">
                            <Brain className="w-6 h-6 text-blue-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">AI-Powered Detection</h3>
                        <p className="text-gray-600">
                            Advanced machine learning models analyze transaction patterns to identify fraudulent behavior with 95%+ accuracy.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="w-12 h-12 rounded-lg bg-green-100 flex items-center justify-center mb-4">
                            <TrendingUp className="w-6 h-6 text-green-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Real-Time Monitoring</h3>
                        <p className="text-gray-600">
                            Monitor transactions as they happen with live updates and instant fraud alerts to prevent losses.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="w-12 h-12 rounded-lg bg-purple-100 flex items-center justify-center mb-4">
                            <Bell className="w-6 h-6 text-purple-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Instant Alerts</h3>
                        <p className="text-gray-600">
                            Get notified immediately when suspicious activity is detected via email and dashboard notifications.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="w-12 h-12 rounded-lg bg-orange-100 flex items-center justify-center mb-4">
                            <BarChart3 className="w-6 h-6 text-orange-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Advanced Analytics</h3>
                        <p className="text-gray-600">
                            Comprehensive dashboards with detailed insights into transaction patterns and fraud trends.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="w-12 h-12 rounded-lg bg-red-100 flex items-center justify-center mb-4">
                            <Lock className="w-6 h-6 text-red-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">Secure & Compliant</h3>
                        <p className="text-gray-600">
                            Bank-level security with encrypted data storage and compliance with financial regulations.
                        </p>
                    </div>

                    <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition">
                        <div className="w-12 h-12 rounded-lg bg-indigo-100 flex items-center justify-center mb-4">
                            <Brain className="w-6 h-6 text-indigo-600" />
                        </div>
                        <h3 className="text-xl font-semibold text-gray-900 mb-2">AI Chatbot Support</h3>
                        <p className="text-gray-600">
                            Get instant help with Gemini AI-powered chatbot that understands your fraud detection queries.
                        </p>
                    </div>
                </div>

                {/* Stats Section */}
                <div className="mt-24 bg-primary rounded-2xl p-12 text-white">
                    <div className="grid md:grid-cols-3 gap-8 text-center">
                        <div>
                            <div className="text-4xl font-bold mb-2">95%+</div>
                            <div className="text-blue-100">Detection Accuracy</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold mb-2">&lt;1s</div>
                            <div className="text-blue-100">Response Time</div>
                        </div>
                        <div>
                            <div className="text-4xl font-bold mb-2">24/7</div>
                            <div className="text-blue-100">Continuous Monitoring</div>
                        </div>
                    </div>
                </div>

                {/* CTA Section */}
                <div className="mt-24 text-center">
                    <h2 className="text-3xl font-bold text-gray-900 mb-4">
                        Ready to Protect Your Transactions?
                    </h2>
                    <p className="text-xl text-gray-600 mb-8">
                        Join thousands of businesses using FraudGuard to prevent fraud
                    </p>
                    <Button
                        size="lg"
                        onClick={() => navigate("/register")}
                        className="text-lg px-8 py-6"
                    >
                        Start Free Trial
                    </Button>
                </div>
            </div>

            {/* Footer */}
            <footer className="bg-gray-900 text-gray-400 py-8 mt-20">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <p>&copy; 2026 FraudGuard. All rights reserved.</p>
                </div>
            </footer>
        </div>
    );
}

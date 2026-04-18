import React from 'react';
import { ArrowRight, ShieldCheck, Layers, TrendingUp } from 'lucide-react';

const LandingPage: React.FC = () => {
  return (
    <div className="py-16 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto text-center">
        <div className="mb-12">
          <p className="text-base font-semibold tracking-wider text-blue-600 uppercase">Sokogate</p>
          <h1 className="mt-4 text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl">
            Build smarter subscription workflows for construction materials
          </h1>
          <p className="mt-6 text-xl text-gray-600 max-w-3xl mx-auto">
            Manage plans, track orders, and unlock analytics with a modern dashboard built for construction teams.
          </p>
          <div className="mt-10 flex flex-col sm:flex-row justify-center gap-4">
            <a
              href="/login"
              className="inline-flex items-center justify-center rounded-md bg-blue-600 px-8 py-3 text-base font-semibold text-white hover:bg-blue-700"
            >
              Get Started
              <ArrowRight className="ml-2 h-5 w-5" />
            </a>
            <a
              href="/plans"
              className="inline-flex items-center justify-center rounded-md bg-white px-8 py-3 text-base font-semibold text-blue-600 border border-blue-200 hover:bg-blue-50"
            >
              View Plans
            </a>
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          <div className="rounded-3xl border border-gray-200 bg-white p-8 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600 mb-5">
              <ShieldCheck className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Secure customer access</h3>
            <p className="mt-3 text-gray-600">
              Protect your subscription data with secure login and centralized account controls.
            </p>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-white p-8 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600 mb-5">
              <Layers className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Plan management made easy</h3>
            <p className="mt-3 text-gray-600">
              Compare subscription tiers, manage usage, and choose the right plan for your construction materials pipeline.
            </p>
          </div>

          <div className="rounded-3xl border border-gray-200 bg-white p-8 shadow-sm">
            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-100 text-blue-600 mb-5">
              <TrendingUp className="h-6 w-6" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900">Actionable analytics</h3>
            <p className="mt-3 text-gray-600">
              Track revenue, subscription growth, and pre-order performance from one intuitive dashboard.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;

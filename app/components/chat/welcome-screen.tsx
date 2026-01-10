"use client";

import { Flower } from "lucide-react";

export function WelcomeScreen() {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 min-h-[calc(100vh-12rem)]">
      {/* Logo/Greeting */}
      <div className="mb-8 text-center">
        <div className="size-16 rounded-2xl bg-primary/10 flex items-center justify-center mx-auto mb-4">
          <Flower className="size-8 text-primary" />
        </div>
        <h1 className="text-2xl font-semibold mb-2">
          What can Lilli help you with?
        </h1>
      </div>
    </div>
  );
}

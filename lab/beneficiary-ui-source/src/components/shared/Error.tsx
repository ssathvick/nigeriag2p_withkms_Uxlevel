"use client";

import React from "react";

interface ErrorProps {
    message?: string;
}

export default function Error({ message = "Something went wrong!" }: ErrorProps) {
    return (
        <div className="flex items-center justify-center min-h-screen bg-red-50 px-4">
            <div className="bg-white shadow-md rounded-lg p-6 flex flex-col items-center max-w-md w-full text-center">
                <p className="text-red-600 font-semibold text-lg">{message}</p>
                <button
                    onClick={() => window.location.reload()}
                    className="mt-4 px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 transition"
                >
                    Retry
                </button>
            </div>
        </div>
    );
}

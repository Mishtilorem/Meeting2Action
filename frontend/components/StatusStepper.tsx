const STEPS = [
    { key: "transcribing", label: "Transcribe" },
    { key: "extracting", label: "Extract" },
    { key: "verifying", label: "Verify" },
    { key: "awaiting_approval", label: "Review" },
    { key: "executing", label: "Create cards" },
    { key: "done", label: "Done" },
];

const CAPTION: Record<string, string> = {
    queued: "Waiting to start...",
    transcribing: "Turning the recording into text...",
    extracting: "Finding action items...",
    verifying: "Checking every item against the transcript...",
    awaiting_approval: "Ready for your review",
    executing: "Creating cards in Trello...",
    done: "All done",
};

function Check() {
    return (
        <svg viewBox="0 0 20 20" className="h-4 w-4" fill="none" stroke="currentColor"
            strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <path d="M5 10.5l3.5 3.5L15 7" />
        </svg>
    );
}

export default function StatusStepper({ status }: { status: string }) {
    const failed = status === "failed";
    const allDone = status === "done";
    const idx = STEPS.findIndex((s) => s.key === status);

    return (
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <ol className="flex">
                {STEPS.map((s, i) => {
                    const state = failed
                        ? "todo"
                        : allDone || i < idx
                            ? "done"
                            : i === idx
                                ? "current"
                                : "todo";
                    const waiting = state === "current" && s.key === "awaiting_approval";
                    const filledLine = !failed && (allDone || i <= idx);
                    const labelColor =
                        state === "done" ? "text-slate-700"
                            : waiting ? "text-amber-700"
                                : state === "current" ? "text-indigo-700"
                                    : "text-slate-400";

                    return (
                        <li key={s.key} className="relative flex flex-1 flex-col items-center">
                            {i > 0 && (
                                <span
                                    className={`absolute right-1/2 top-4 h-0.5 w-full -translate-y-1/2 transition-colors duration-500 ${filledLine ? "bg-indigo-600" : "bg-slate-200"
                                        }`}
                                />
                            )}
                            <span
                                className={`relative z-10 flex h-8 w-8 items-center justify-center rounded-full text-xs font-medium transition-colors duration-300 ${state === "done"
                                    ? "bg-indigo-600 text-white"
                                    : waiting
                                        ? "border-2 border-amber-500 bg-amber-50"
                                        : state === "current"
                                            ? "border-2 border-indigo-600 bg-white"
                                            : "border-2 border-slate-200 bg-white text-slate-400"
                                    }`}
                            >
                                {state === "done" ? (
                                    <Check />
                                ) : waiting ? (
                                    <span className="h-3 w-3 animate-pulse rounded-full bg-amber-500" />
                                ) : state === "current" ? (
                                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
                                ) : (
                                    i + 1
                                )}
                            </span>
                            <span className={`mt-2 text-center text-xs font-medium ${labelColor}`}>{s.label}</span>
                        </li>
                    );
                })}
            </ol>
            <p className={`mt-5 text-center text-sm ${failed ? "text-red-600" : "text-slate-500"}`}>
                {failed ? "Something went wrong" : CAPTION[status] ?? status}
            </p>
        </div>
    );
}